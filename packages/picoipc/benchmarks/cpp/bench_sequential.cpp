#include "smh_q/ring.hpp"
#include <unistd.h>

#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <string>
#include <vector>

using Clock = std::chrono::high_resolution_clock;

static std::uint32_t bench_slot_bytes(int payload_bytes) {
  return static_cast<std::uint32_t>((payload_bytes + 8) < 64 ? 64 : (payload_bytes + 8));
}

int main(int argc, char** argv) {
  const int count = (argc > 1) ? std::atoi(argv[1]) : 100'000;
  const int payload_bytes = (argc > 2) ? std::atoi(argv[2]) : 64;

  const std::string name = "/smh_q_bench_seq_" + std::to_string(::getpid());
  smh_q::Ring::unlink(name);

  smh_q::Ring::Config cfg;
  cfg.name = name;
  cfg.slot_count = static_cast<std::uint32_t>(count < 256 ? 256 : count);
  cfg.slot_size = bench_slot_bytes(payload_bytes);

  smh_q::Ring ring(cfg, true);
  std::vector<std::byte> payload(static_cast<std::size_t>(payload_bytes));
  std::vector<std::byte> consume_buf(static_cast<std::size_t>(payload_bytes));

  std::printf("smh_q bench_sequential (count=%d payload=%dB)\n", count, payload_bytes);

  const auto t0 = Clock::now();
  for (int i = 0; i < count; ++i) {
    while (!ring.try_publish(payload)) {
    }
  }
  for (int i = 0; i < count; ++i) {
    while (!ring.try_consume(consume_buf).has_value()) {
    }
  }
  const auto t1 = Clock::now();
  smh_q::Ring::unlink(name);

  const double elapsed_ms =
      std::chrono::duration<double, std::milli>(t1 - t0).count();
  const double msgs_per_sec = static_cast<double>(count) / (elapsed_ms / 1000.0);
  const double mb_per_sec =
      msgs_per_sec * static_cast<double>(payload_bytes) / (1024.0 * 1024.0);

  std::printf(
      "%-12s payload=%4dB count=%7d elapsed=%8.2f ms  msgs/s=%10.0f  MB/s=%8.2f\n",
      "sequential", payload_bytes, count, elapsed_ms, msgs_per_sec, mb_per_sec);

  return 0;
}
