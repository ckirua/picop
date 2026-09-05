#include "smh_q/ring.hpp"

#include <cstdio>
#include <cstring>
#include <string>
#include <unistd.h>

#define CHECK(cond)                                                          \
  do {                                                                       \
    if (!(cond)) {                                                           \
      std::fprintf(stderr, "CHECK failed: %s (%s:%d)\n", #cond, __FILE__,   \
                   __LINE__);                                                \
      std::abort();                                                          \
    }                                                                        \
  } while (0)

int main() {
  const std::string name = "smh_q_stress_" + std::to_string(::getpid());
  smh_q::Ring::unlink(name);

  constexpr std::uint32_t kSlots = 4;
  smh_q::Ring::Config cfg;
  cfg.name = name;
  cfg.slot_count = kSlots;
  cfg.slot_size = 128;

  smh_q::Ring ring(cfg, true);

  const char* msg = "x";
  const auto span = std::span<const std::byte>(reinterpret_cast<const std::byte*>(msg), 1);

  int published = 0;
  while (ring.try_publish(span)) {
    ++published;
  }
  std::printf("filled ring: published=%d slot_count=%u (ring full)\n", published, kSlots);
  CHECK(published == static_cast<int>(kSlots));

  CHECK(!ring.try_publish(span));

  auto got = ring.try_consume();
  CHECK(got.has_value());
  CHECK(got->size() == 1);
  CHECK(got->front() == std::byte{'x'});

  CHECK(ring.try_publish(span));

  std::printf("backpressure OK: full at %d slots, unblock after consume\n", kSlots);

  smh_q::Ring::unlink(name);
  return 0;
}
