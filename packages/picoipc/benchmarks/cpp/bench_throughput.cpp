#include "smh_q/ring.hpp"
#include <unistd.h>

#include <algorithm>
#include <atomic>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <thread>
#include <vector>

using Clock = std::chrono::high_resolution_clock;

static std::uint64_t bench_now_ns() {
  return static_cast<std::uint64_t>(
      std::chrono::duration_cast<std::chrono::nanoseconds>(Clock::now().time_since_epoch())
          .count());
}

static std::uint32_t bench_slot_bytes(int payload_bytes) {
  return static_cast<std::uint32_t>((payload_bytes + 8) < 64 ? 64 : (payload_bytes + 8));
}

int main(int argc, char** argv) {
  const int count = (argc > 1) ? std::atoi(argv[1]) : 100'000;
  const int payload_bytes = (argc > 2) ? std::atoi(argv[2]) : 64;

  const std::string name = "/smh_q_bench_tp_" + std::to_string(::getpid());
  smh_q::Ring::unlink(name);

  smh_q::Ring::Config cfg;
  cfg.name = name;
  cfg.slot_count = 256;
  cfg.slot_size = bench_slot_bytes(payload_bytes);

  smh_q::Ring producer(cfg, true);
  smh_q::Ring consumer(cfg, false);
  std::vector<std::byte> payload(static_cast<std::size_t>(payload_bytes));
  std::vector<std::uint64_t> latencies;
  latencies.reserve(static_cast<std::size_t>(count));

  std::atomic<bool> go{false};
  std::atomic<int> done{0};

  std::printf("smh_q bench_throughput (count=%d payload=%dB)\n", count, payload_bytes);
  std::printf("mode         payload  count    elapsed_ms    throughput\n");
  std::printf("----------------------------------------------------------------\n");

  const auto t0 = Clock::now();

  std::thread reader([&] {
    while (!go.load(std::memory_order_acquire)) std::this_thread::yield();
    while (done.load(std::memory_order_relaxed) < count) {
      auto msg = consumer.try_consume();
      if (!msg.has_value()) {
        consumer.wait_readable(std::chrono::milliseconds(1));
        continue;
      }
      std::uint64_t pub = 0;
      std::memcpy(&pub, msg->data(), sizeof(pub));
      latencies.push_back(bench_now_ns() - pub);
      done.fetch_add(1, std::memory_order_relaxed);
    }
  });

  go.store(true, std::memory_order_release);

  for (int i = 0; i < count; ++i) {
    const std::uint64_t stamp = bench_now_ns();
    std::memcpy(payload.data(), &stamp, sizeof(stamp));
    while (!producer.try_publish(payload)) std::this_thread::yield();
  }

  reader.join();
  const auto t1 = Clock::now();
  smh_q::Ring::unlink(name);

  const double elapsed_ms =
      std::chrono::duration<double, std::milli>(t1 - t0).count();
  std::sort(latencies.begin(), latencies.end());

  const double msgs_per_sec = static_cast<double>(count) / (elapsed_ms / 1000.0);
  const double mb_per_sec =
      msgs_per_sec * static_cast<double>(payload_bytes) / (1024.0 * 1024.0);
  const double p50 =
      latencies.empty() ? 0.0 : static_cast<double>(latencies[latencies.size() / 2]);
  const double p99 = latencies.empty()
                         ? 0.0
                         : static_cast<double>(latencies[static_cast<std::size_t>(
                               0.99 * static_cast<double>(latencies.size() - 1))]);

  std::printf(
      "%-12s payload=%4dB count=%7d elapsed=%8.2f ms  msgs/s=%10.0f  MB/s=%8.2f  "
      "p50=%6.0f ns  p99=%6.0f ns\n",
      "threaded", payload_bytes, count, elapsed_ms, msgs_per_sec, mb_per_sec, p50, p99);

  return 0;
}
