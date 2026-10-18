"""POSIX SHM SPSC ring — layout matches the bundled smh_q C++ engine."""
from __future__ import annotations
import ctypes
import mmap
import os
import platform
import struct
import threading
import time
from typing import Optional

MAGIC = 0x534D4851
DEFAULT_SCHEMA_ID = 1
DEFAULT_VERSION = 1
CACHE_LINE = 64
SLOT_HDR_SIZE = 8
_HEADER_FMT = "<IHHIII"
_HEADER_SIZE = struct.calcsize(_HEADER_FMT)
_SLOT_HDR_FMT = "<II"
FUTEX_WAIT = 0
FUTEX_WAKE = 1


def _align_up(value: int, alignment: int) -> int:
    return (value + alignment - 1) & ~(alignment - 1)


def _seq_offset() -> int:
    return _align_up(_HEADER_SIZE, CACHE_LINE)


def _slots_offset() -> int:
    return _align_up(_seq_offset() + 2 * CACHE_LINE, CACHE_LINE)


def _posix_name(name: str) -> str:
    return name if name.startswith("/") else f"/{name}"


def _libc() -> ctypes.CDLL:
    libc = ctypes.CDLL("libc.so.6", use_errno=True)
    libc.syscall.restype = ctypes.c_long
    libc.syscall.argtypes = [ctypes.c_long, ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int]
    libc.shm_open.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_uint]
    libc.shm_open.restype = ctypes.c_int
    libc.shm_unlink.argtypes = [ctypes.c_char_p]
    libc.shm_unlink.restype = ctypes.c_int
    return libc


_atomic_lock = threading.Lock()
_atomic: ctypes.CDLL | None = None


def _libatomic() -> ctypes.CDLL:
    global _atomic
    if _atomic is None:
        with _atomic_lock:
            if _atomic is None:
                try:
                    lib = ctypes.CDLL("libatomic.so.1")
                    load = getattr(lib, "__atomic_load_4")
                    load.argtypes = [ctypes.c_void_p, ctypes.c_int]
                    load.restype = ctypes.c_uint32
                    store = getattr(lib, "__atomic_store_4")
                    store.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_int]
                    store.restype = None
                    lock_free = getattr(lib, "__atomic_is_lock_free")
                    lock_free.argtypes = [ctypes.c_size_t, ctypes.c_void_p]
                    lock_free.restype = ctypes.c_bool
                except (OSError, AttributeError) as exc:
                    raise OSError("libatomic.so.1 with 32-bit atomic operations is required") from exc
                _atomic = lib
    return _atomic


class Ring:
    """Single-producer / single-consumer byte ring over POSIX shm + futex."""
    def __init__(self, name: str = "smh_q_demo", *, create: bool = False, slot_count: int = 64,
                 slot_size: int = 256, schema_id: int = DEFAULT_SCHEMA_ID, version: int = DEFAULT_VERSION,
                 magic: int = MAGIC) -> None:
        if platform.system() != "Linux" or platform.machine().lower() not in ("x86_64", "amd64"):
            raise OSError("pure picoipc backend supports futex only on Linux x86_64")
        if struct.pack("=I", 1)[0] != 1:
            raise OSError("picoipc shared ring requires little-endian Linux")
        if slot_count < 2:
            raise ValueError("slot_count must be >= 2")
        if slot_size < 64:
            raise ValueError("slot_size must be >= 64")
        self.name = _posix_name(name)
        self.slot_count, self.slot_size = slot_count, slot_size
        self.schema_id, self.version, self.magic = schema_id, version, magic
        self._create = create
        self._fd: int | None = None
        self._mm: mmap.mmap | None = None
        self._write_seq_off = _seq_offset()
        self._read_seq_off = self._write_seq_off + CACHE_LINE
        self._slots_off = _slots_offset()
        self._lock = threading.Lock()
        self._open()

    @property
    def region_size(self) -> int:
        return self._slots_off + self.slot_count * self.slot_size

    def _open(self) -> None:
        libc = _libc()
        fd = libc.shm_open(self.name.encode(), os.O_RDWR | (os.O_CREAT if self._create else 0), 0o600)
        if fd < 0:
            raise OSError(ctypes.get_errno(), f"shm_open({self.name})")
        mm = None
        try:
            if self._create:
                os.ftruncate(fd, self.region_size)
                mm = mmap.mmap(fd, self.region_size, mmap.MAP_SHARED, mmap.PROT_READ | mmap.PROT_WRITE)
                mm[:] = b"\0" * self.region_size
                mm[:_HEADER_SIZE] = struct.pack(_HEADER_FMT, self.magic, self.schema_id, self.version, self.slot_count, self.slot_size, self._slots_off)
            else:
                size = os.fstat(fd).st_size
                if size < _HEADER_SIZE:
                    raise OSError(f"shm {self.name} too small")
                mm = mmap.mmap(fd, size, mmap.MAP_SHARED, mmap.PROT_READ | mmap.PROT_WRITE)
                magic, schema, version, self.slot_count, self.slot_size, self._slots_off = struct.unpack_from(_HEADER_FMT, mm)
                if magic != self.magic:
                    raise OSError(f"shm {self.name} magic mismatch: {magic:#x}")
                if schema != self.schema_id:
                    raise OSError(f"shm {self.name} schema mismatch: {schema}")
                self.version = version
            atomic = _libatomic()
            is_lock_free = getattr(atomic, "__atomic_is_lock_free")
            for offset in (self._write_seq_off, self._read_seq_off):
                if offset + 4 > len(mm):
                    raise OSError("shared ring sequence counter is outside mapping")
                cell = ctypes.c_uint32.from_buffer(mm, offset)
                address = ctypes.addressof(cell)
                if address % ctypes.alignment(ctypes.c_uint32) or not is_lock_free(4, address):
                    del cell
                    raise OSError("shared ring requires aligned lock-free 32-bit counters")
                del cell
            self._mm, self._fd = mm, fd
        except Exception:
            if mm is not None:
                mm.close()
            os.close(fd)
            raise

    def close(self, *, unlink: bool = False) -> None:
        with self._lock:
            mm, fd = self._mm, self._fd
            self._mm = self._fd = None
            if mm is not None:
                mm.close()
            if fd is not None:
                os.close(fd)
            if unlink and self._create:
                _libc().shm_unlink(self.name.encode())

    @staticmethod
    def unlink(name: str) -> None:
        _libc().shm_unlink(_posix_name(name).encode())

    def _atomic_u32_locked(self, offset: int, value: int | None = None) -> int:
        mm = self._mm
        if mm is None:
            return 0
        cell = ctypes.c_uint32.from_buffer(mm, offset)
        address = ctypes.addressof(cell)
        atomic = _libatomic()
        try:
            if value is None:
                return int(getattr(atomic, "__atomic_load_4")(address, 2))
            getattr(atomic, "__atomic_store_4")(address, value & 0xFFFFFFFF, 3)
            return value & 0xFFFFFFFF
        finally:
            del cell

    def _write_seq_locked(self) -> int:
        return self._atomic_u32_locked(self._write_seq_off)

    def _read_seq_locked(self) -> int:
        return self._atomic_u32_locked(self._read_seq_off)

    def write_seq(self) -> int:
        with self._lock:
            return self._write_seq_locked()

    def read_seq(self) -> int:
        with self._lock:
            return self._read_seq_locked()

    def _slot_offset(self, index: int) -> int:
        return self._slots_off + (index % self.slot_count) * self.slot_size

    def try_publish(self, payload: bytes) -> bool:
        if not isinstance(payload, (bytes, bytearray, memoryview)):
            payload = str(payload).encode()
        capacity = self.slot_size - SLOT_HDR_SIZE
        if len(payload) > capacity:
            raise ValueError(f"payload exceeds slot capacity ({capacity} bytes)")
        with self._lock:
            mm = self._mm
            if mm is None:
                return False
            write, read = self._write_seq_locked(), self._read_seq_locked()
            if write - read >= self.slot_count:
                return False
            offset = self._slot_offset(write)
            mm[offset:offset + SLOT_HDR_SIZE] = struct.pack(_SLOT_HDR_FMT, len(payload), 0)
            mm[offset + SLOT_HDR_SIZE:offset + SLOT_HDR_SIZE + len(payload)] = payload
            self._atomic_u32_locked(self._write_seq_off, write + 1)
            self._wake_locked()
            return True

    def try_consume(self) -> Optional[bytes]:
        with self._lock:
            mm = self._mm
            if mm is None:
                return None
            read, write = self._read_seq_locked(), self._write_seq_locked()
            if read >= write:
                return None
            offset = self._slot_offset(read)
            length, _ = struct.unpack_from(_SLOT_HDR_FMT, mm, offset)
            if not length:
                return None
            length = min(length, self.slot_size - SLOT_HDR_SIZE)
            payload = bytes(mm[offset + SLOT_HDR_SIZE:offset + SLOT_HDR_SIZE + length])
            self._atomic_u32_locked(self._read_seq_off, read + 1)
            return payload

    def _write_seq_pointer_locked(self):
        mm = self._mm
        if mm is None:
            return None
        cell = ctypes.c_uint32.from_buffer(mm, self._write_seq_off)
        return cell, ctypes.c_void_p(ctypes.addressof(cell))

    def _wake_locked(self) -> None:
        holder = self._write_seq_pointer_locked()
        if holder is not None:
            cell, pointer = holder
            try:
                _libc().syscall(202, pointer, FUTEX_WAKE, 0x7FFFFFFF, None, None, 0)
            finally:
                del cell, holder

    def wake(self) -> None:
        with self._lock:
            self._wake_locked()

    def wait_readable(self, timeout_ms: int) -> bool:
        deadline = time.monotonic() + max(timeout_ms, 0) / 1000
        with self._lock:
            if self._mm is None:
                return False
            read = self._read_seq_locked()
        libc = _libc()
        while True:
            # Pin each bounded wait, not the whole deadline: a producer or
            # closer using this same handle must be able to make progress.
            with self._lock:
                if self._mm is None:
                    return False
                write = self._write_seq_locked()
                if write > read:
                    return True
                if time.monotonic() >= deadline:
                    return False
                holder = self._write_seq_pointer_locked()
                assert holder is not None
                cell, pointer = holder
                try:
                    timeout = struct.pack("ll", 0, 1_000_000)
                    libc.syscall(202, pointer, FUTEX_WAIT, write, ctypes.c_char_p(timeout), None, 0)
                finally:
                    del cell, holder
            time.sleep(0)
