#pragma once

/** POSIX shared-memory SPSC ring with futex wake (Linux only). */

#include <chrono>
#include <cstddef>
#include <cstdint>
#include <optional>
#include <span>
#include <string>
#include <vector>

namespace smh_q {

constexpr std::uint32_t kDefaultMagic = 0x534D4851;  // "SMHQ"

class Ring {
 public:
  struct Config {
    std::string name = "smh_q_demo";
    std::uint32_t slot_count = 64;
    std::uint32_t slot_size = 256;
    std::uint16_t schema_id = 1;
    std::uint16_t version = 1;
    std::uint32_t magic = kDefaultMagic;
  };

  Ring(Config cfg, bool create);
  ~Ring();

  Ring(const Ring&) = delete;
  Ring& operator=(const Ring&) = delete;

  bool try_publish(std::span<const std::byte> payload);
  /** Claim next writable slot payload; empty span if ring full. Valid until publish(). */
  std::span<std::byte> claim();
  void publish(std::size_t length);
  /** Copy into claimed slot and publish; requires prior claim(). */
  void publish_payload(std::span<const std::byte> payload);
  /** claim() + publish(length) without payload copy; false if ring full. */
  bool try_publish_length(std::size_t length);
  bool has_claim() const { return has_claim_; }
  /** Copy next message into out; returns byte count, or nullopt if empty/invalid. */
  std::optional<std::size_t> try_consume(std::span<std::byte> out);
  std::optional<std::vector<std::byte>> try_consume();

  void wake();
  bool wait_readable(std::chrono::milliseconds timeout);

  static void unlink(const std::string& name);

  std::uint16_t schema_id() const { return schema_id_; }
  std::uint32_t slot_count() const { return slot_count_; }
  std::uint32_t slot_size() const { return slot_size_; }
  const std::string& name() const { return cfg_.name; }
  std::uint32_t write_seq() const;
  std::uint32_t read_seq() const;

 private:
  struct RingHeader {
    std::uint32_t magic;
    std::uint16_t schema_id;
    std::uint16_t version;
    std::uint32_t slot_count;
    std::uint32_t slot_size;
    std::uint32_t header_bytes;
  };

  struct SlotHeader {
    std::uint32_t length;
    std::uint32_t reserved;
  };

  std::size_t region_size() const;
  SlotHeader* slot_at(std::uint32_t index);
  const SlotHeader* slot_at(std::uint32_t index) const;
  std::span<std::byte> slot_payload(SlotHeader* slot);
  std::span<const std::byte> slot_payload(const SlotHeader* slot) const;
  void check_schema() const;
  static std::string posix_name(const std::string& name);

  Config cfg_;
  std::uint32_t magic_ = 0;
  int fd_ = -1;
  void* region_ = nullptr;
  std::size_t mapped_size_ = 0;
  RingHeader* header_ = nullptr;
  volatile std::uint32_t* write_seq_ = nullptr;
  volatile std::uint32_t* read_seq_ = nullptr;
  std::byte* slots_base_ = nullptr;
  std::uint32_t slot_count_ = 0;
  std::uint32_t slot_size_ = 0;
  std::uint16_t schema_id_ = 0;
  std::uint32_t claimed_index_ = 0;
  bool has_claim_ = false;
};

}  // namespace smh_q
