"""Lifecycle-safe ctypes binding to libsmh_q.so."""
from __future__ import annotations
import ctypes
import os
import threading
from pathlib import Path
from typing import Optional

MAGIC = 0x534D4851
DEFAULT_SCHEMA_ID = 1
DEFAULT_VERSION = 1
_loader_lock = threading.Lock()
_lib: ctypes.CDLL | None = None


def _find_lib() -> Path:
    env = os.environ.get("SMH_Q_LIB", "").strip()
    if env:
        return Path(env)
    here = Path(__file__).resolve()
    for path in (here.parent / "libsmh_q.so", here.parents[2] / "build/native/libsmh_q.so",
                 Path("/usr/local/lib/libsmh_q.so"), Path("/usr/lib/libsmh_q.so"),
                 Path("/usr/lib/x86_64-linux-gnu/libsmh_q.so")):
        if path.is_file():
            return path
    raise OSError("libsmh_q.so not found; set SMH_Q_LIB or install the package shared library")


def _load() -> ctypes.CDLL:
    global _lib
    if _lib is None:
        with _loader_lock:
            if _lib is None:
                lib = ctypes.CDLL(str(_find_lib()))
                lib.smh_q_ring_create.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint16, ctypes.c_uint16, ctypes.c_uint32]
                lib.smh_q_ring_create.restype = ctypes.c_void_p
                lib.smh_q_ring_destroy.argtypes = [ctypes.c_void_p]
                lib.smh_q_ring_destroy.restype = None
                lib.smh_q_ring_try_publish.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32]
                lib.smh_q_ring_try_publish.restype = ctypes.c_int
                lib.smh_q_ring_try_consume.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32)]
                lib.smh_q_ring_try_consume.restype = ctypes.c_int
                lib.smh_q_ring_wake.argtypes = [ctypes.c_void_p]
                lib.smh_q_ring_wake.restype = None
                lib.smh_q_ring_wait_readable.argtypes = [ctypes.c_void_p, ctypes.c_int]
                lib.smh_q_ring_wait_readable.restype = ctypes.c_int
                for seq in ("write_seq", "read_seq"):
                    function = getattr(lib, f"smh_q_ring_{seq}")
                    function.argtypes = [ctypes.c_void_p]
                    function.restype = ctypes.c_uint32
                lib.smh_q_ring_unlink.argtypes = [ctypes.c_char_p]
                lib.smh_q_ring_unlink.restype = None
                lib.smh_q_ring_max_payload.argtypes = [ctypes.c_void_p]
                lib.smh_q_ring_max_payload.restype = ctypes.c_uint32
                _lib = lib
    return _lib


class Ring:
    def __init__(self, name: str = "smh_q_demo", *, create: bool = False, slot_count: int = 64,
                 slot_size: int = 256, schema_id: int = DEFAULT_SCHEMA_ID, version: int = 1, magic: int = MAGIC) -> None:
        self.name = name if name.startswith("/") else f"/{name}"
        self._create = create
        self.slot_count, self.slot_size = slot_count, slot_size
        self._condition = threading.Condition()
        self._handle: ctypes.c_void_p | None = None
        self._active = 0
        self._closing = False
        self._closed = False
        handle = _load().smh_q_ring_create(self.name.encode(), int(create), slot_count, slot_size, schema_id, version, magic)
        if not handle:
            raise OSError(f"smh_q_ring_create failed for {self.name}")
        try:
            self._handle = ctypes.c_void_p(handle)
        except BaseException:
            _load().smh_q_ring_destroy(ctypes.c_void_p(handle))
            raise

    def _pin(self) -> ctypes.c_void_p | None:
        with self._condition:
            if self._closing or self._handle is None:
                return None
            self._active += 1
            return self._handle

    def _unpin(self) -> None:
        with self._condition:
            self._active -= 1
            if self._active == 0:
                self._condition.notify_all()

    @staticmethod
    def unlink(name: str) -> None:
        nm = name if name.startswith("/") else f"/{name}"
        _load().smh_q_ring_unlink(nm.encode())

    def close(self, *, unlink: bool = False) -> None:
        with self._condition:
            if self._closing:
                while not self._closed:
                    self._condition.wait()
                should_unlink = unlink and self._create
                handle = None
            else:
                self._closing = True
                while self._active:
                    self._condition.wait()
                handle, self._handle = self._handle, None
                should_unlink = unlink and self._create
        try:
            if handle is not None:
                _load().smh_q_ring_destroy(handle)
            if should_unlink:
                self.unlink(self.name)
        finally:
            with self._condition:
                self._closed = True
                self._condition.notify_all()

    def try_publish(self, payload: bytes) -> bool:
        if not isinstance(payload, (bytes, bytearray, memoryview)):
            payload = str(payload).encode()
        view = memoryview(payload)
        if view.ndim != 1 or view.itemsize != 1 or not view.contiguous:
            raise TypeError("payload must be a contiguous one-dimensional byte buffer")
        raw = view.cast("B")
        buf = (ctypes.c_ubyte * len(raw)).from_buffer_copy(raw)
        handle = self._pin()
        if handle is None:
            return False
        try:
            rc = _load().smh_q_ring_try_publish(handle, buf, len(raw))
            if rc < 0:
                raise OSError("smh_q_ring_try_publish failed")
            return rc == 1
        finally:
            self._unpin()

    def try_consume(self) -> Optional[bytes]:
        handle = self._pin()
        if handle is None:
            return None
        try:
            lib = _load()
            maximum = lib.smh_q_ring_max_payload(handle)
            out = (ctypes.c_uint8 * max(maximum, 1))()
            length = ctypes.c_uint32()
            rc = lib.smh_q_ring_try_consume(handle, out, len(out), ctypes.byref(length))
            if rc < 0:
                raise OSError("smh_q_ring_try_consume failed")
            return bytes(out[:length.value]) if rc else None
        finally:
            self._unpin()

    def wake(self) -> None:
        handle = self._pin()
        if handle is None:
            return
        try:
            _load().smh_q_ring_wake(handle)
        finally:
            self._unpin()

    def wait_readable(self, timeout_ms: int) -> bool:
        handle = self._pin()
        if handle is None:
            return False
        try:
            return _load().smh_q_ring_wait_readable(handle, timeout_ms) == 1
        finally:
            self._unpin()

    def write_seq(self) -> int:
        handle = self._pin()
        if handle is None:
            return 0
        try:
            return int(_load().smh_q_ring_write_seq(handle))
        finally:
            self._unpin()

    def read_seq(self) -> int:
        handle = self._pin()
        if handle is None:
            return 0
        try:
            return int(_load().smh_q_ring_read_seq(handle))
        finally:
            self._unpin()
