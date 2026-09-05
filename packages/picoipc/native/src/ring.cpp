#include "smh_q/ring.hpp"

#include <algorithm>
#include <cstdlib>
#include <cstring>
#include <string>
#include <stdexcept>
#include <thread>

#include <errno.h>
#include <fcntl.h>
#include <linux/futex.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <unistd.h>

namespace smh_q {

namespace {

constexpr std::size_t kCacheLine = 64;

std::size_t align_up(std::size_t value, std::size_t alignment) {
  return (value + alignment - 1) & ~(alignment - 1);
}

std::uint32_t load_relaxed(volatile std::uint32_t* addr) {
  return __atomic_load_n(addr, __ATOMIC_RELAXED);
}

std::uint32_t load_acquire(volatile std::uint32_t* addr) {
  return __atomic_load_n(addr, __ATOMIC_ACQUIRE);
}

void store_release(volatile std::uint32_t* addr, std::uint32_t value) {
  __atomic_store_n(addr, value, __ATOMIC_RELEASE);
}

int futex_wait(volatile std::uint32_t* addr, std::uint32_t expected,
               const struct timespec* timeout) {
  return static_cast<int>(
      ::syscall(SYS_futex, reinterpret_cast<int*>(const_cast<std::uint32_t*>(addr)), FUTEX_WAIT,
                static_cast<int>(expected), timeout, nullptr, 0));
}

int futex_wake(volatile std::uint32_t* addr, int n) {
  __atomic_thread_fence(__ATOMIC_SEQ_CST);
  return static_cast<int>(
      ::syscall(SYS_futex, reinterpret_cast<int*>(const_cast<std::uint32_t*>(addr)), FUTEX_WAKE, n,
                nullptr, nullptr, 0));
}

int getenv_int(const char* name, int default_value) {
  const char* raw = std::getenv(name);
  if (raw == nullptr || raw[0] == '\0') {
    return default_value;
  }
  try {
    return std::stoi(raw);
  } catch (...) {
    return default_value;
  }
}

int shm_wait_slice_ms() {
  return std::max(1, getenv_int("SMH_Q_SHM_WAIT_MS", 1));
}

int shm_spin_iters() {
  return std::max(0, getenv_int("SMH_Q_SHM_SPIN_ITERS", 2000));
}

}  // namespace

std::string Ring::posix_name(const std::string& name) {
  return name.starts_with('/') ? name : "/" + name;
}

void Ring::unlink(const std::string& name) {
  ::shm_unlink(posix_name(name).c_str());
}

Ring::Ring(Config cfg, bool create) : cfg_(std::move(cfg)) {
  if (cfg_.slot_count < 2) {
    throw std::invalid_argument("slot_count must be >= 2");
  }
  if (cfg_.slot_size < 64) {
    throw std::invalid_argument("slot_size must be >= 64");
  }
  magic_ = cfg_.magic;

  slot_count_ = cfg_.slot_count;
  slot_size_ = cfg_.slot_size;
  schema_id_ = cfg_.schema_id;
  mapped_size_ = region_size();

  const std::string shm_name = posix_name(cfg_.name);

  if (create) {
    ::shm_unlink(shm_name.c_str());
    fd_ = shm_open(shm_name.c_str(), O_CREAT | O_RDWR, 0600);
    if (fd_ < 0) {
      throw std::runtime_error("shm_open(create) failed");
    }
    if (ftruncate(fd_, static_cast<off_t>(mapped_size_)) != 0) {
      throw std::runtime_error("ftruncate failed");
    }
  } else {
    fd_ = shm_open(shm_name.c_str(), O_RDWR, 0600);
    if (fd_ < 0) {
      throw std::runtime_error("shm_open(open) failed");
    }
  }

  region_ = mmap(nullptr, mapped_size_, PROT_READ | PROT_WRITE, MAP_SHARED, fd_, 0);
  if (region_ == MAP_FAILED) {
    region_ = nullptr;
    throw std::runtime_error("mmap failed");
  }

  header_ = static_cast<RingHeader*>(region_);
  const std::size_t seq_off = align_up(sizeof(RingHeader), kCacheLine);
  const std::size_t slots_off = align_up(seq_off + 2 * kCacheLine, kCacheLine);

  if (create) {
    std::memset(region_, 0, mapped_size_);
    header_->magic = magic_;
    header_->schema_id = cfg_.schema_id;
    header_->version = cfg_.version;
    header_->slot_count = slot_count_;
    header_->slot_size = slot_size_;
    header_->header_bytes = static_cast<std::uint32_t>(slots_off);
  } else {
    if (header_->magic != magic_) {
      throw std::runtime_error("invalid shm ring magic");
    }
    if (header_->schema_id != cfg_.schema_id) {
      throw std::runtime_error("schema_id mismatch");
    }
    slot_count_ = header_->slot_count;
    slot_size_ = header_->slot_size;
    schema_id_ = header_->schema_id;
    const std::size_t actual =
        slots_off + static_cast<std::size_t>(slot_count_) * slot_size_;
    if (actual != mapped_size_) {
      munmap(region_, mapped_size_);
      mapped_size_ = actual;
      region_ = mmap(nullptr, mapped_size_, PROT_READ | PROT_WRITE, MAP_SHARED, fd_, 0);
      if (region_ == MAP_FAILED) {
        region_ = nullptr;
        throw std::runtime_error("mmap remap failed");
      }
      header_ = static_cast<RingHeader*>(region_);
    }
  }

  write_seq_ =
      reinterpret_cast<volatile std::uint32_t*>(static_cast<std::byte*>(region_) + seq_off);
  read_seq_ = reinterpret_cast<volatile std::uint32_t*>(static_cast<std::byte*>(region_) +
                                                        seq_off + kCacheLine);
  slots_base_ = static_cast<std::byte*>(region_) + slots_off;
}

Ring::~Ring() {
  if (region_ != nullptr) {
    munmap(region_, mapped_size_);
  }
  if (fd_ >= 0) {
    close(fd_);
  }
}

std::uint32_t Ring::write_seq() const {
  return write_seq_ ? load_acquire(write_seq_) : 0;
}

std::uint32_t Ring::read_seq() const {
  return read_seq_ ? load_acquire(read_seq_) : 0;
}

std::size_t Ring::region_size() const {
  const std::size_t seq_off = align_up(sizeof(RingHeader), kCacheLine);
  const std::size_t slots_off = align_up(seq_off + 2 * kCacheLine, kCacheLine);
  return slots_off + static_cast<std::size_t>(slot_count_) * slot_size_;
}

Ring::SlotHeader* Ring::slot_at(std::uint32_t index) {
  return reinterpret_cast<SlotHeader*>(slots_base_ + static_cast<std::size_t>(index) * slot_size_);
}

const Ring::SlotHeader* Ring::slot_at(std::uint32_t index) const {
  return reinterpret_cast<const SlotHeader*>(slots_base_ +
                                             static_cast<std::size_t>(index) * slot_size_);
}

std::span<std::byte> Ring::slot_payload(SlotHeader* slot) {
  const std::size_t payload_size = slot_size_ - sizeof(SlotHeader);
  return {reinterpret_cast<std::byte*>(slot) + sizeof(SlotHeader), payload_size};
}

std::span<const std::byte> Ring::slot_payload(const SlotHeader* slot) const {
  const std::size_t payload_size = slot_size_ - sizeof(SlotHeader);
  return {reinterpret_cast<const std::byte*>(slot) + sizeof(SlotHeader), payload_size};
}

void Ring::check_schema() const {
  if (header_->schema_id != schema_id_) {
    throw std::runtime_error("schema_id mismatch in ring header");
  }
}

std::span<std::byte> Ring::claim() {
  if (has_claim_) {
    throw std::runtime_error("slot already claimed");
  }

  check_schema();
  const std::uint32_t write = load_relaxed(write_seq_);
  const std::uint32_t read = load_acquire(read_seq_);
  if (write - read >= slot_count_) {
    return {};
  }

  claimed_index_ = write % slot_count_;
  SlotHeader* slot = slot_at(claimed_index_);
  slot->length = 0;
  slot->reserved = 0;
  has_claim_ = true;
  return slot_payload(slot);
}

void Ring::publish(std::size_t length) {
  if (!has_claim_) {
    throw std::runtime_error("publish without claim");
  }

  SlotHeader* slot = slot_at(claimed_index_);
  if (length > slot_payload(slot).size()) {
    throw std::runtime_error("publish length exceeds slot payload");
  }
  slot->length = static_cast<std::uint32_t>(length);
  store_release(write_seq_, load_relaxed(write_seq_) + 1);
  has_claim_ = false;
  wake();
}

void Ring::publish_payload(std::span<const std::byte> payload) {
  if (!has_claim_) {
    throw std::runtime_error("publish_payload without claim");
  }
  auto slot = slot_payload(slot_at(claimed_index_));
  if (payload.size() > slot.size()) {
    has_claim_ = false;
    throw std::runtime_error("payload exceeds slot size");
  }
  if (!payload.empty()) {
    std::memcpy(slot.data(), payload.data(), payload.size());
  }
  publish(payload.size());
}

bool Ring::try_publish_length(std::size_t length) {
  auto slot = claim();
  if (slot.empty()) {
    return false;
  }
  if (length > slot.size()) {
    has_claim_ = false;
    throw std::runtime_error("publish length exceeds slot payload");
  }
  publish(length);
  return true;
}

bool Ring::try_publish(std::span<const std::byte> payload) {
  auto slot = claim();
  if (slot.empty()) return false;
  if (payload.size() > slot.size()) {
    has_claim_ = false;
    throw std::runtime_error("payload exceeds slot size");
  }
  std::memcpy(slot.data(), payload.data(), payload.size());
  publish(payload.size());
  return true;
}

std::optional<std::size_t> Ring::try_consume(std::span<std::byte> out) {
  check_schema();
  const std::uint32_t read = load_relaxed(read_seq_);
  const std::uint32_t write = load_acquire(write_seq_);
  if (read >= write) {
    return std::nullopt;
  }

  const SlotHeader* slot = slot_at(read % slot_count_);
  const std::uint32_t length = slot->length;
  if (length == 0) {
    return std::nullopt;
  }

  auto payload = slot_payload(slot);
  if (length > payload.size() || length > out.size()) {
    return std::nullopt;
  }

  std::memcpy(out.data(), payload.data(), length);
  store_release(read_seq_, read + 1);
  return static_cast<std::size_t>(length);
}

std::optional<std::vector<std::byte>> Ring::try_consume() {
  check_schema();
  const std::uint32_t read = load_relaxed(read_seq_);
  const std::uint32_t write = load_acquire(write_seq_);
  if (read >= write) {
    return std::nullopt;
  }

  const SlotHeader* slot = slot_at(read % slot_count_);
  const std::uint32_t length = slot->length;
  if (length == 0) {
    return std::nullopt;
  }

  auto payload = slot_payload(slot);
  if (length > payload.size()) {
    return std::nullopt;
  }

  std::vector<std::byte> out(static_cast<std::size_t>(length));
  std::memcpy(out.data(), payload.data(), length);
  store_release(read_seq_, read + 1);
  return out;
}

void Ring::wake() {
  if (write_seq_ == nullptr) return;
  (void)futex_wake(write_seq_, INT_MAX);
}

bool Ring::wait_readable(std::chrono::milliseconds timeout) {
  if (write_seq_ == nullptr || read_seq_ == nullptr) return false;
  check_schema();

  const auto deadline = std::chrono::steady_clock::now() + timeout;
  const std::uint32_t read = load_relaxed(read_seq_);

  const int spin_iters = shm_spin_iters();
  for (int i = 0; i < spin_iters; ++i) {
    const std::uint32_t write = load_acquire(write_seq_);
    if (write > read) return true;
    if (i > 64) std::this_thread::yield();
  }

  while (std::chrono::steady_clock::now() < deadline) {
    const std::uint32_t write = load_acquire(write_seq_);
    if (write > read) return true;

    const auto rem = std::chrono::duration_cast<std::chrono::milliseconds>(
        deadline - std::chrono::steady_clock::now());
    if (rem.count() <= 0) break;

    const int slice = std::min(shm_wait_slice_ms(), static_cast<int>(rem.count()));
    struct timespec ts {};
    ts.tv_sec = static_cast<time_t>(slice / 1000);
    ts.tv_nsec = static_cast<long>((slice % 1000) * 1'000'000L);
    (void)futex_wait(write_seq_, write, &ts);
    (void)errno;
  }

  return load_acquire(write_seq_) > read;
}

}  // namespace smh_q
