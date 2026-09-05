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
  const std::string name = "smh_q_roundtrip_" + std::to_string(::getpid());
  smh_q::Ring::unlink(name);

  smh_q::Ring::Config cfg;
  cfg.name = name;
  cfg.slot_count = 8;
  cfg.slot_size = 128;
  cfg.schema_id = 42;

  {
    smh_q::Ring producer(cfg, true);
    smh_q::Ring consumer(cfg, false);

    const char* msg = "hello-smh_q";
    CHECK(producer.try_publish(std::span<const std::byte>(
        reinterpret_cast<const std::byte*>(msg), std::strlen(msg))));

    auto got = consumer.try_consume();
    CHECK(got.has_value());
    CHECK(got->size() == std::strlen(msg));
    CHECK(std::memcmp(got->data(), msg, got->size()) == 0);

    std::puts("roundtrip OK");
  }

  smh_q::Ring::unlink(name);
  return 0;
}
