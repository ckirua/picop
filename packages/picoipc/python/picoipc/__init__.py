"""picoipc — low-latency local IPC primitives for Linux."""
import os
from picoipc.ring import MAGIC

def _posix(name: str) -> str:
    return name if name.startswith("/") else f"/{name}"

def _backend() -> str:
    return os.environ.get("PICOIPC_BACKEND", "pybind11").strip().lower()

def _load_ring_impl():
    b = _backend()
    if b in ("pure", "pure_python"):
        from picoipc.ring import Ring as R
        return R, "pure_python"
    if b == "ctypes":
        from picoipc._ctypes_ring import Ring as R
        return R, "ctypes"
    if b == "cython":
        from picoipc._cython_ring import Ring as R
        return R, "cython"
    try:
        from picoipc._native import Ring as R
        return R, "pybind11"
    except ImportError:
        from picoipc.ring import Ring as R
        return R, "pure_python"

RingImpl, _IMPL = _load_ring_impl()

class Ring(RingImpl):
    def __init__(self, name: str = "smh_q_demo", *, create: bool = False,
                 slot_count: int = 64, slot_size: int = 256, schema_id: int = 1,
                 version: int = 1, magic: int = MAGIC) -> None:
        name = _posix(name)
        if _IMPL == "pybind11":
            super().__init__(name, create, slot_count, slot_size, schema_id, version, magic)
        else:
            super().__init__(name, create=create, slot_count=slot_count, slot_size=slot_size,
                             schema_id=schema_id, version=version, magic=magic)

    @staticmethod
    def unlink(name: str) -> None:
        name = _posix(name)
        if _IMPL == "pybind11":
            from picoipc._native import unlink
            unlink(name)
        else:
            RingImpl.unlink(name)

    def close(self, unlink: bool = False) -> None:
        if _IMPL == "pybind11":
            super().close(unlink)
        else:
            super().close(unlink=unlink)

def impl_name() -> str:
    return _IMPL

__all__ = ["MAGIC", "Ring", "impl_name"]
__version__ = "0.1.0"
