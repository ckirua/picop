#include "smh_q/c_api.h"
#include "smh_q/ring.hpp"
#include <chrono>
#include <cstring>
#include <new>
#include <string>
#include <vector>

struct SmhQRing { smh_q::Ring ring; };

SmhQRing* smh_q_ring_create(const char* name, int create, uint32_t slot_count,
                            uint32_t slot_size, uint16_t schema_id, uint16_t version,
                            uint32_t magic) {
  if (!name) return nullptr;
  try {
    smh_q::Ring::Config cfg;
    cfg.name = name; cfg.slot_count = slot_count; cfg.slot_size = slot_size;
    cfg.schema_id = schema_id; cfg.version = version; cfg.magic = magic;
    return new SmhQRing{smh_q::Ring(std::move(cfg), create != 0)};
  } catch (...) { return nullptr; }
}
void smh_q_ring_destroy(SmhQRing* ring) { delete ring; }
int smh_q_ring_try_publish(SmhQRing* ring, const uint8_t* data, uint32_t len) {
  if (!ring || !data) return 0;
  try {
    return ring->ring.try_publish(std::span<const std::byte>(reinterpret_cast<const std::byte*>(data), len)) ? 1 : 0;
  } catch (...) { return -1; }
}
int smh_q_ring_try_consume(SmhQRing* ring, uint8_t* out_buf, uint32_t out_cap, uint32_t* out_len) {
  if (!ring || !out_len) return -1;
  *out_len = 0;
  try {
    const uint32_t cap = out_cap;
    auto n = ring->ring.try_consume(
        std::span<std::byte>(reinterpret_cast<std::byte*>(out_buf), cap));
    if (!n) return 0;
    if (!out_buf || *n > cap) return -1;
    *out_len = static_cast<uint32_t>(*n);
    return 1;
  } catch (...) { return -1; }
}
void smh_q_ring_wake(SmhQRing* ring) { if (ring) ring->ring.wake(); }
int smh_q_ring_wait_readable(SmhQRing* ring, int timeout_ms) {
  if (!ring) return 0;
  try { return ring->ring.wait_readable(std::chrono::milliseconds(timeout_ms)) ? 1 : 0; }
  catch (...) { return 0; }
}
void smh_q_ring_unlink(const char* name) { if (name) smh_q::Ring::unlink(name); }
uint32_t smh_q_ring_max_payload(SmhQRing* ring) {
  if (!ring) return 0;
  return ring->ring.slot_size() > 8 ? ring->ring.slot_size() - 8 : 0;
}
