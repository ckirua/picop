"""Python usage for picop cypycapsule.

Run: python examples/pypycapsule.py
"""
import ctypes

from picop import capsule_check_exact, capsule_eq, capsule_is_valid


def _capsule(ptr: int, name: bytes) -> object:
    PyCapsule_New = ctypes.pythonapi.PyCapsule_New
    PyCapsule_New.restype = ctypes.py_object
    PyCapsule_New.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_void_p]
    return PyCapsule_New(ctypes.c_void_p(ptr), name, None)


def main() -> None:
    assert capsule_check_exact(object()) is False
    assert capsule_is_valid(object(), b"x") is False
    a = _capsule(0x1000, b"picop.test")
    b = _capsule(0x1000, b"picop.test")
    assert capsule_check_exact(a)
    assert capsule_eq(a, a) and not capsule_eq(a, b)
    assert capsule_eq(a, a) is (a is a)
    print("ok", capsule_check_exact(a), capsule_eq(a, a))


if __name__ == "__main__":
    main()
