"""Python usage for picop cyfileobject.

Run: python examples/pyfileobject.py
"""
import os
import tempfile

from picop import file_from_fd, file_write_cstr

def main() -> None:
    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, "out.txt")
        fd = os.open(path, os.O_RDWR | os.O_CREAT)
        obj = file_from_fd(fd, b"out.txt", b"w+", closefd=1)
        assert file_write_cstr(b"hello", obj) == 0
        obj.close()
        assert open(path, "rb").read() == b"hello"
    print("ok", b"hello")

if __name__ == "__main__":
    main()
