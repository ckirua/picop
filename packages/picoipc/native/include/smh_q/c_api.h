#pragma once
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
typedef struct SmhQRing SmhQRing;
SmhQRing* smh_q_ring_create(const char* name, int create, uint32_t slot_count,
    uint32_t slot_size, uint16_t schema_id, uint16_t version, uint32_t magic);
void smh_q_ring_destroy(SmhQRing* ring);
int smh_q_ring_try_publish(SmhQRing* ring, const uint8_t* data, uint32_t len);
int smh_q_ring_try_consume(SmhQRing* ring, uint8_t* out_buf, uint32_t out_cap, uint32_t* out_len);
void smh_q_ring_wake(SmhQRing* ring);
int smh_q_ring_wait_readable(SmhQRing* ring, int timeout_ms);
void smh_q_ring_unlink(const char* name);
uint32_t smh_q_ring_max_payload(SmhQRing* ring);
#ifdef __cplusplus
}
#endif
