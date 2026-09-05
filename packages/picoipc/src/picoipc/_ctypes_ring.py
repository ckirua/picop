"""ctypes binding to libsmh_q.so."""
from __future__ import annotations
import ctypes
import os
from pathlib import Path
from typing import Optional

MAGIC = 0x534D4851
DEFAULT_SCHEMA_ID = 1
DEFAULT_VERSION = 1

def _find_lib() -> Path:
    env = os.environ.get("SMH_Q_LIB", "").strip()
    if env:
        return Path(env)
    here = Path(__file__).resolve()
    for path in [here.parents[2] / "cpp" / "build" / "libsmh_q.so", Path("/usr/local/lib/libsmh_q.so")]:
        if path.is_file():
            return path
    raise OSError("libsmh_q.so not found; cmake -S native -B build/native && cmake --build build/native")

_lib: ctypes.CDLL | None = None

def _load() -> ctypes.CDLL:
    global _lib
    if _lib is None:
        _lib = ctypes.CDLL(str(_find_lib()))
        _lib.smh_q_ring_create.argtypes = [
            ctypes.c_char_p, ctypes.c_int, ctypes.c_uint32, ctypes.c_uint32,
            ctypes.c_uint16, ctypes.c_uint16, ctypes.c_uint32,
        ]
        _lib.smh_q_ring_create.restype = ctypes.c_void_p
        _lib.smh_q_ring_destroy.argtypes = [ctypes.c_void_p]
        _lib.smh_q_ring_try_publish.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32]
        _lib.smh_q_ring_try_publish.restype = ctypes.c_int
        _lib.smh_q_ring_try_consume.argtypes = [
            ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32),
        ]
        _lib.smh_q_ring_try_consume.restype = ctypes.c_int
        _lib.smh_q_ring_wake.argtypes = [ctypes.c_void_p]
        _lib.smh_q_ring_wait_readable.argtypes = [ctypes.c_void_p, ctypes.c_int]
        _lib.smh_q_ring_wait_readable.restype = ctypes.c_int
        _lib.smh_q_ring_unlink.argtypes = [ctypes.c_char_p]
        _lib.smh_q_ring_max_payload.argtypes = [ctypes.c_void_p]
        _lib.smh_q_ring_max_payload.restype = ctypes.c_uint32
    return _lib

class Ring:
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
        self.name = name if name.startswith("/") else f"/{name}"
        self._create = create
        self.slot_count = slot_count
        self.slot_size = slot_size
        h = _load().smh_q_ring_create(
            self.name.encode(), 1 if create else 0, slot_count, slot_size,
            schema_id, version, magic,
        )
        if not h:
            raise OSError(f"smh_q_ring_create failed for {self.name}")
        self._handle = ctypes.c_void_p(h)

    def close(self, *, unlink: bool = False) -> None:
        if getattr(self, "_handle", None):
            _load().smh_q_ring_destroy(self._handle)
            self._handle = None
        if unlink and self._create:
            self.unlink(self.name)

    @staticmethod
    def unlink(name: str) -> None:
        nm = name if name.startswith("/") else f"/{name}"
        _load().smh_q_ring_unlink(nm.encode())

    def try_publish(self, payload: bytes) -> bool:
        if not isinstance(payload, (bytes, bytearray, memoryview)):
            payload = str(payload).encode()
        buf = (ctypes.c_char * len(payload)).from_buffer_copy(payload)
        rc = _load().smh_q_ring_try_publish(self._handle, buf, len(payload))
        if rc < 0:
            raise OSError("smh_q_ring_try_publish failed")
        return rc == 1

    def try_consume(self) -> Optional[bytes]:
        mp = _load().smh_q_ring_max_payload(self._handle)
        out = (ctypes.c_uint8 * max(mp, 1))()
        out_len = ctypes.c_uint32(0)
        rc = _load().smh_q_ring_try_consume(self._handle, out, len(out), ctypes.byref(out_len))
        if rc < 0:
            raise OSError("smh_q_ring_try_consume failed")
        if rc == 0:
            return None
        return bytes(out[: out_len.value])

    def wake(self) -> None:
        _load().smh_q_ring_wake(self._handle)

    def wait_readable(self, timeout_ms: int) -> bool:
        return _load().smh_q_ring_wait_readable(self._handle, timeout_ms) == 1
