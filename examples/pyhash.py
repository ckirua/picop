"""Python usage for picop cyhash.

Run: python examples/pyhash.py
"""
import array

from picop import hash_buffer


def main() -> None:
    data = b"picop hashing"

    # bytearray and array.array have no __hash__: the plain-Python route is
    # hash(bytes(...)), which copies the buffer first.
    print("bytearray:", hash_buffer(bytearray(data)))
    print("array.array:", hash_buffer(array.array("B", data)))
    try:
        hash(bytearray(data))
    except TypeError as exc:
        print("plain hash(bytearray) fails:", exc)

    # Same value as the builtin, no copy.
    print("bytes:", hash_buffer(data), "== hash(data):", hash_buffer(data) == hash(data))
    print("range 6:13:", hash_buffer(data, 6, 13), "== hash(data[6:13]):", hash_buffer(data, 6, 13) == hash(data[6:13]))

    # bytes/memoryview cache their hash, so the builtin is cheaper once it is warm.
    warm = memoryview(data)
    print("warm memoryview: hash(mv) is the cheap path, hash_buffer re-hashes")


if __name__ == "__main__":
    main()
