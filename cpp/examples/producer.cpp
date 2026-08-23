#include "smh_q/ring.hpp"

#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <thread>

int main(int argc, char** argv) {
  const std::string name = (argc > 1) ? argv[1] : "smh_q_demo";
  const int count = (argc > 2) ? std::atoi(argv[2]) : 10;
  const int delay_ms = (argc > 3) ? std::atoi(argv[3]) : 100;

  smh_q::Ring::Config cfg;
  cfg.name = name;
  cfg.slot_count = 16;
  cfg.slot_size = 128;

  smh_q::Ring ring(cfg, true);
  std::printf("producer: name=%s count=%d delay_ms=%d\n", name.c_str(), count, delay_ms);

  for (int i = 0; i < count; ++i) {
  retry:
    char buf[64];
    const int n = std::snprintf(buf, sizeof(buf), "msg-%04d", i);
    while (!ring.try_publish(std::span<const std::byte>(
        reinterpret_cast<const std::byte*>(buf), static_cast<std::size_t>(n)))) {
      std::this_thread::sleep_for(std::chrono::milliseconds(1));
      goto retry;
    }
    std::printf("published: %s (write_seq=%u)\n", buf, ring.write_seq());
    std::this_thread::sleep_for(std::chrono::milliseconds(delay_ms));
  }

  std::puts("producer done");
  return 0;
}
