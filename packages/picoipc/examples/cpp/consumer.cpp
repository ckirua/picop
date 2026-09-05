#include "smh_q/ring.hpp"

#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <string>
#include <thread>

int main(int argc, char** argv) {
  const std::string name = (argc > 1) ? argv[1] : "smh_q_demo";
  const int timeout_ms = (argc > 2) ? std::atoi(argv[2]) : 5000;

  smh_q::Ring::Config cfg;
  cfg.name = name;
  cfg.slot_count = 16;
  cfg.slot_size = 128;

  smh_q::Ring ring(cfg, false);
  std::printf("consumer: name=%s timeout_ms=%d\n", name.c_str(), timeout_ms);

  const auto deadline = std::chrono::steady_clock::now() + std::chrono::milliseconds(timeout_ms);
  int received = 0;

  while (std::chrono::steady_clock::now() < deadline) {
    auto msg = ring.try_consume();
    if (msg.has_value()) {
      std::string text(reinterpret_cast<const char*>(msg->data()), msg->size());
      std::printf("consumed: %s (read_seq=%u write_seq=%u)\n", text.c_str(), ring.read_seq(),
                  ring.write_seq());
      ++received;
      continue;
    }

    const auto remaining = std::chrono::duration_cast<std::chrono::milliseconds>(
        deadline - std::chrono::steady_clock::now());
    if (remaining.count() <= 0) break;

    if (!ring.wait_readable(remaining)) {
      break;
    }
  }

  std::printf("consumer done: received=%d\n", received);
  return received > 0 ? 0 : 1;
}
