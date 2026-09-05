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

namespace {

using Clock = std::chrono::high_resolution_clock;

std::uint64_t now_ns() {
  return static_cast<std::uint64_t>(
      std::chrono::duration_cast<std::chrono::nanoseconds>(Clock::now().time_since_epoch())
          .count());
}

enum class WaitMode { Spin, Futex };

struct FutexBenchResult {
  WaitMode mode;
  int count = 0;
  double elapsed_ms = 0.0;
  double avg_wakeup_ns = 0.0;
  double p99_wakeup_ns = 0.0;
};

FutexBenchResult run_bench(WaitMode mode, int count, int idle_us) {
  const std::string name = "/smh_q_bench_futex_" + std::to_string(::getpid()) + "_" +
                           (mode == WaitMode::Spin ? "spin" : "futex");
  smh_q::Ring::unlink(name);

  smh_q::Ring::Config cfg;
  cfg.name = name;
  cfg.slot_count = 16;
  cfg.slot_size = 128;

  smh_q::Ring producer(cfg, true);
  smh_q::Ring consumer(cfg, false);

  std::vector<std::uint64_t> wakeups;
  wakeups.reserve(static_cast<std::size_t>(count));

  std::atomic<bool> go{false};
  std::atomic<int> received{0};

  std::thread reader([&] {
    while (!go.load(std::memory_order_acquire)) {
      std::this_thread::yield();
    }
    while (received.load(std::memory_order_relaxed) < count) {
      auto msg = consumer.try_consume();
      if (msg.has_value()) {
        std::uint64_t pub_ns = 0;
        std::memcpy(&pub_ns, msg->data(), sizeof(pub_ns));
        wakeups.push_back(now_ns() - pub_ns);
        received.fetch_add(1, std::memory_order_relaxed);
        continue;
      }

      if (mode == WaitMode::Futex) {
        consumer.wait_readable(std::chrono::milliseconds(100));
      }
    }
  });

  const char payload[64] = {};
  go.store(true, std::memory_order_release);

  const auto t0 = Clock::now();
  for (int i = 0; i < count; ++i) {
    const std::uint64_t stamp = now_ns();
    std::memcpy(const_cast<char*>(payload), &stamp, sizeof(stamp));
    while (!producer.try_publish(
        std::span<const std::byte>(reinterpret_cast<const std::byte*>(payload), sizeof(stamp)))) {
      std::this_thread::yield();
    }
    if (idle_us > 0) {
      std::this_thread::sleep_for(std::chrono::microseconds(idle_us));
    }
  }

  while (received.load(std::memory_order_relaxed) < count) {
    std::this_thread::yield();
  }
  const auto t1 = Clock::now();

  reader.join();
  smh_q::Ring::unlink(name);

  std::sort(wakeups.begin(), wakeups.end());
  double sum = 0.0;
  for (auto w : wakeups) sum += static_cast<double>(w);

  FutexBenchResult r;
  r.mode = mode;
  r.count = count;
  r.elapsed_ms = std::chrono::duration<double, std::milli>(t1 - t0).count();
  r.avg_wakeup_ns = wakeups.empty() ? 0.0 : sum / static_cast<double>(wakeups.size());
  r.p99_wakeup_ns = wakeups.empty()
                        ? 0.0
                        : static_cast<double>(wakeups[static_cast<std::size_t>(
                              0.99 * static_cast<double>(wakeups.size() - 1))]);
  return r;
}

void print_result(const FutexBenchResult& r) {
  const char* label = (r.mode == WaitMode::Spin) ? "spin" : "futex";
  std::printf(
      "%-6s count=%5d elapsed=%8.2f ms  avg_wakeup=%8.0f ns  p99_wakeup=%8.0f ns\n", label,
      r.count, r.elapsed_ms, r.avg_wakeup_ns, r.p99_wakeup_ns);
}

}  // namespace

int main(int argc, char** argv) {
  const int count = (argc > 1) ? std::atoi(argv[1]) : 1000;
  const int idle_us = (argc > 2) ? std::atoi(argv[2]) : 1000;

  std::printf("smh_q bench_futex (count=%d idle_us=%d between publishes)\n", count, idle_us);
  const char* spin_env = std::getenv("SMH_Q_SHM_SPIN_ITERS");
  const char* wait_env = std::getenv("SMH_Q_SHM_WAIT_MS");
  std::printf("Env: SMH_Q_SHM_SPIN_ITERS=%s SMH_Q_SHM_WAIT_MS=%s (defaults 2000, 1)\n",
              spin_env ? spin_env : "(unset)", wait_env ? wait_env : "(unset)");
  std::printf("Compare consumer spin-only vs wait_readable (futex) when producer is idle.\n\n");

  print_result(run_bench(WaitMode::Spin, count, idle_us));
  print_result(run_bench(WaitMode::Futex, count, idle_us));

  return 0;
}
