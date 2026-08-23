#include "smh_q/ring.hpp"

#include <algorithm>
#include <atomic>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <thread>
#include <vector>

namespace {

using Clock = std::chrono::high_resolution_clock;

std::uint64_t now_ns() {
  return static_cast<std::uint64_t>(
      std::chrono::duration_cast<std::chrono::nanoseconds>(Clock::now().time_since_epoch())
          .count());
}

std::uint32_t slot_bytes(std::size_t payload_bytes) {
  const std::uint32_t min_size = static_cast<std::uint32_t>(payload_bytes + 8);
  return min_size < 64 ? 64 : min_size;
}

double percentile(std::vector<std::uint64_t>& samples, double p) {
  if (samples.empty()) return 0.0;
  const std::size_t idx =
      static_cast<std::size_t>(p * static_cast<double>(samples.size() - 1));
  return static_cast<double>(samples[idx]);
}

struct BenchResult {
  int count = 0;
  int payload_bytes = 0;
  double elapsed_ms = 0.0;
  double msgs_per_sec = 0.0;
  double mb_per_sec = 0.0;
  double p50_ns = 0.0;
  double p99_ns = 0.0;
};

BenchResult run_threaded(int count, int payload_bytes) {
  const std::string name = "/smh_q_bench_tp_" + std::to_string(::getpid());
  smh_q::Ring::unlink(name);

  smh_q::Ring::Config cfg;
  cfg.name = name;
  cfg.slot_count = 256;
  cfg.slot_size = slot_bytes(static_cast<std::size_t>(payload_bytes));

  smh_q::Ring producer(cfg, true);
  smh_q::Ring consumer(cfg, false);

  std::vector<std::byte> payload(static_cast<std::size_t>(payload_bytes), std::byte{0});
  std::vector<std::uint64_t> latencies;
  latencies.reserve(static_cast<std::size_t>(count));

  std::atomic<bool> go{false};
  std::atomic<int> done{0};
  std::atomic<bool> producer_error{false};

  std::thread reader([&] {
    while (!go.load(std::memory_order_acquire)) {
      std::this_thread::yield();
    }
    while (done.load(std::memory_order_relaxed) < count) {
      auto msg = consumer.try_consume();
      if (!msg.has_value()) {
        consumer.wait_readable(std::chrono::milliseconds(1));
        continue;
      }
      (void)msg;
      done.fetch_add(1, std::memory_order_relaxed);
    }
  });

  const auto t0 = Clock::now();
  go.store(true, std::memory_order_release);

  for (int i = 0; i < count; ++i) {
    const std::uint64_t stamp = now_ns();
    std::memcpy(payload.data(), &stamp, sizeof(stamp));
    while (!producer.try_publish(payload)) {
      std::this_thread::yield();
    }
  }

  while (done.load(std::memory_order_relaxed) < count) {
    std::this_thread::yield();
  }
  const auto t1 = Clock::now();

  reader.join();
  smh_q::Ring::unlink(name);

  if (producer_error.load()) {
    std::fprintf(stderr, "benchmark error: short payload\n");
    std::exit(1);
  }

  const double elapsed_ms =
      std::chrono::duration<double, std::milli>(t1 - t0).count();
  std::sort(latencies.begin(), latencies.end());

  BenchResult r;
  r.count = count;
  r.payload_bytes = payload_bytes;
  r.elapsed_ms = elapsed_ms;
  r.msgs_per_sec = static_cast<double>(count) / (elapsed_ms / 1000.0);
  r.mb_per_sec = r.msgs_per_sec * static_cast<double>(payload_bytes) / (1024.0 * 1024.0);
  r.p50_ns = percentile(latencies, 0.50);
  r.p99_ns = percentile(latencies, 0.99);
  return r;
}

BenchResult run_sequential(int count, int payload_bytes) {
  const std::string name = "/smh_q_bench_seq_" + std::to_string(::getpid());
  smh_q::Ring::unlink(name);

  smh_q::Ring::Config cfg;
  cfg.name = name;
  cfg.slot_count = 256;
  cfg.slot_size = slot_bytes(static_cast<std::size_t>(payload_bytes));

  smh_q::Ring ring(cfg, true);

  std::vector<std::byte> payload(static_cast<std::size_t>(payload_bytes), std::byte{0});
  for (int i = 0; i < payload_bytes; ++i) {
    payload[static_cast<std::size_t>(i)] = static_cast<std::byte>(i & 0xff);
  }

  const auto t0 = Clock::now();
  for (int i = 0; i < count; ++i) {
    while (!ring.try_publish(payload)) {
    }
  }
  for (int i = 0; i < count; ++i) {
    while (!ring.try_consume().has_value()) {
    }
  }
  const auto t1 = Clock::now();

  smh_q::Ring::unlink(name);

  const double elapsed_ms =
      std::chrono::duration<double, std::milli>(t1 - t0).count();

  BenchResult r;
  r.count = count;
  r.payload_bytes = payload_bytes;
  r.elapsed_ms = elapsed_ms;
  r.msgs_per_sec = static_cast<double>(count) / (elapsed_ms / 1000.0);
  r.mb_per_sec = r.msgs_per_sec * static_cast<double>(payload_bytes) / (1024.0 * 1024.0);
  r.p50_ns = 0.0;
  r.p99_ns = 0.0;
  return r;
}

void print_result(const char* mode, const BenchResult& r) {
  std::printf(
      "%-12s payload=%4dB count=%7d elapsed=%8.2f ms  msgs/s=%10.0f  MB/s=%8.2f",
      mode, r.payload_bytes, r.count, r.elapsed_ms, r.msgs_per_sec, r.mb_per_sec);
  if (r.p50_ns > 0.0) {
    std::printf("  p50=%6.0f ns  p99=%6.0f ns", r.p50_ns, r.p99_ns);
  }
  std::printf("\n");
}

}  // namespace

int main(int argc, char** argv) {
  const int count = (argc > 1) ? std::atoi(argv[1]) : 100'000;
  const int payload_arg = (argc > 2) ? std::atoi(argv[2]) : 0;

  const int payloads[] = {64, 256, 1024};
  const int n_payloads = (payload_arg > 0) ? 1 : 3;
  const int first_payload = (payload_arg > 0) ? payload_arg : payloads[0];

  std::printf("smh_q bench_throughput (count=%d)\n", count);
  std::printf("mode         payload  count    elapsed_ms    throughput\n");
  std::printf("----------------------------------------------------------------\n");

  for (int pi = 0; pi < n_payloads; ++pi) {
    const int pb = (payload_arg > 0) ? first_payload : payloads[pi];
    print_result("threaded", run_threaded(count, pb));
    print_result("sequential", run_sequential(count, pb));
    std::printf("\n");
  }

  return 0;
}
