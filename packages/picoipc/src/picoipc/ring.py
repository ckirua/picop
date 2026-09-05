"""POSIX SHM SPSC ring — layout matches the bundled smh_q C++ engine."""

from __future__ import annotations

import ctypes
import mmap
import os
import struct
import threading
import time
from typing import Optional

MAGIC = 0x534D4851  # "SMHQ"
DEFAULT_SCHEMA_ID = 1
DEFAULT_VERSION = 1
CACHE_LINE = 64
SLOT_HDR_SIZE = 8

_HEADER_FMT = "<IHHIII"  # magic, schema, version, slot_count, slot_size, header_bytes
_HEADER_SIZE = struct.calcsize(_HEADER_FMT)  # 20
_SLOT_HDR_FMT = "<II"


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
    libc.syscall.argtypes = [
        ctypes.c_long,
        ctypes.c_void_p,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_int,
    ]
    libc.shm_open.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_uint]
    libc.shm_open.restype = ctypes.c_int
    libc.shm_unlink.argtypes = [ctypes.c_char_p]
    libc.shm_unlink.restype = ctypes.c_int
    return libc


FUTEX_WAIT = 0
FUTEX_WAKE = 1
SYS_futex = 202 if struct.calcsize("P") == 8 else 240


class Ring:
    """Single-producer / single-consumer byte ring over POSIX shm + futex."""

    def __init__(
        self,
        name: str = "smh_q_demo",
        *,
        create: bool = False,
        slot_count: int = 64,
        slot_size: int = 256,
        schema_id: int = DEFAULT_SCHEMA_ID,
        version: int = DEFAULT_VERSION,
        magic: int = MAGIC,
    ) -> None:
        if slot_count < 2:
            raise ValueError("slot_count must be >= 2")
        if slot_size < 64:
            raise ValueError("slot_size must be >= 64")

        self.name = _posix_name(name)
        self.slot_count = slot_count
        self.slot_size = slot_size
        self.schema_id = schema_id
        self.version = version
        self.magic = magic
        self._create = create
        self._fd: int | None = None
        self._mm: mmap.mmap | None = None
        self._write_seq_off = 0
        self._read_seq_off = 0
        self._slots_off = 0
        self._lock = threading.Lock()
        self._open()

    @property
    def region_size(self) -> int:
        return self._slots_off + self.slot_count * self.slot_size

    def _open(self) -> None:
        libc = _libc()
        flags = os.O_RDWR
        if self._create:
            flags |= os.O_CREAT

        self._write_seq_off = _seq_offset()
        self._read_seq_off = self._write_seq_off + CACHE_LINE
        self._slots_off = _slots_offset()
        region_size = self.region_size

        fd = libc.shm_open(self.name.encode(), flags, 0o600)
        if fd < 0:
            raise OSError(ctypes.get_errno(), f"shm_open({self.name})")

        try:
            if self._create:
                os.ftruncate(fd, region_size)
                mm = mmap.mmap(fd, region_size, mmap.MAP_SHARED, mmap.PROT_READ | mmap.PROT_WRITE)
            else:
                st = os.fstat(fd)
                if st.st_size < _HEADER_SIZE:
                    raise OSError(f"shm {self.name} too small")
                mm = mmap.mmap(fd, st.st_size, mmap.MAP_SHARED, mmap.PROT_READ | mmap.PROT_WRITE)

            if self._create:
                mm[:region_size] = b"\x00" * region_size
                mm[:_HEADER_SIZE] = struct.pack(
                    _HEADER_FMT,
                    self.magic,
                    self.schema_id,
                    self.version,
                    self.slot_count,
                    self.slot_size,
                    self._slots_off,
                )
            else:
                magic, schema, version, sc, ss, hb = struct.unpack(_HEADER_FMT, mm[:_HEADER_SIZE])
                if magic != self.magic:
                    raise OSError(f"shm {self.name} magic mismatch: {magic:#x}")
                if schema != self.schema_id:
                    raise OSError(f"shm {self.name} schema mismatch: {schema}")
                self.slot_count = int(sc)
                self.slot_size = int(ss)
                self.version = int(version)
                self._slots_off = int(hb)

            self._fd = fd
            self._mm = mm
        except Exception:
            os.close(fd)
            raise

    def close(self, *, unlink: bool = False) -> None:
        with self._lock:
            if self._mm is not None:
                self._mm.close()
                self._mm = None
            if self._fd is not None:
                os.close(self._fd)
                self._fd = None
            if unlink and self._create:
                _libc().shm_unlink(self.name.encode())

    @staticmethod
    def unlink(name: str) -> None:
        _libc().shm_unlink(_posix_name(name).encode())

    def _load_u32(self, offset: int) -> int:
        assert self._mm is not None
        return struct.unpack_from("<I", self._mm, offset)[0]

    def _store_u32(self, offset: int, value: int) -> None:
        assert self._mm is not None
        struct.pack_into("<I", self._mm, offset, value & 0xFFFFFFFF)

    def write_seq(self) -> int:
        return self._load_u32(self._write_seq_off)

    def read_seq(self) -> int:
        return self._load_u32(self._read_seq_off)

    def _slot_offset(self, index: int) -> int:
        return self._slots_off + (index % self.slot_count) * self.slot_size

    def try_publish(self, payload: bytes) -> bool:
        if not isinstance(payload, (bytes, bytearray, memoryview)):
            payload = str(payload).encode()

        max_payload = self.slot_size - SLOT_HDR_SIZE
        if len(payload) > max_payload:
            raise ValueError(f"payload exceeds slot capacity ({max_payload} bytes)")

        with self._lock:
            if self._mm is None:
                return False

            write = self.write_seq()
            read = self.read_seq()
            if (write - read) >= self.slot_count:
                return False

            idx = write % self.slot_count
            off = self._slot_offset(idx)
            self._mm[off : off + SLOT_HDR_SIZE] = struct.pack(_SLOT_HDR_FMT, len(payload), 0)
            self._mm[off + SLOT_HDR_SIZE : off + SLOT_HDR_SIZE + len(payload)] = payload
            self._store_u32(self._write_seq_off, write + 1)
            self.wake()
            return True

    def try_consume(self) -> Optional[bytes]:
        with self._lock:
            if self._mm is None:
                return None

            read = self.read_seq()
            write = self.write_seq()
            if read >= write:
                return None

            idx = read % self.slot_count
            off = self._slot_offset(idx)
            length, _ = struct.unpack(_SLOT_HDR_FMT, self._mm[off : off + SLOT_HDR_SIZE])
            if length == 0:
                return None

            max_payload = self.slot_size - SLOT_HDR_SIZE
            length = min(int(length), max_payload)
            raw = bytes(self._mm[off + SLOT_HDR_SIZE : off + SLOT_HDR_SIZE + length])
            self._store_u32(self._read_seq_off, read + 1)
            return raw

    def _write_seq_addr(self) -> ctypes.c_void_p:
        assert self._mm is not None
        seq = ctypes.c_uint32.from_buffer(self._mm, self._write_seq_off)
        return ctypes.cast(ctypes.byref(seq), ctypes.c_void_p)

    def wake(self) -> None:
        libc = _libc()
        libc.syscall(SYS_futex, self._write_seq_addr(), FUTEX_WAKE, 0x7FFFFFFF, None, None, 0)

    def wait_readable(self, timeout_ms: int) -> bool:
        if self._mm is None:
            return False

        deadline = time.monotonic() + timeout_ms / 1000.0
        read = self.read_seq()

        for i in range(2000):
            write = self.write_seq()
            if write > read:
                return True
            if i > 64:
                time.sleep(0)

        libc = _libc()
        while time.monotonic() < deadline:
            write = self.write_seq()
            if write > read:
                return True

            rem_ms = int((deadline - time.monotonic()) * 1000)
            if rem_ms <= 0:
                break

            slice_ms = min(1, rem_ms)
            ts = struct.pack("ll", slice_ms // 1000, (slice_ms % 1000) * 1_000_000)
            libc.syscall(
                SYS_futex,
                self._write_seq_addr(),
                FUTEX_WAIT,
                write,
                ctypes.c_char_p(ts),
                None,
                0,
            )

        return self.write_seq() > read
