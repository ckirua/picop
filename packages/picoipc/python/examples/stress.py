#!/usr/bin/env python3
"""Fill the ring until full; verify backpressure and unblock after consume."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from smh_q import Ring


def main() -> int:
    name = f"smh_q_py_stress_{os.getpid()}"
    Ring.unlink(name)

    slot_count = 4
    ring = Ring(name, create=True, slot_count=slot_count, slot_size=128)

    msg = b"x"
    published = 0
    while ring.try_publish(msg):
        published += 1

    print(f"filled ring: published={published} slot_count={slot_count} (ring full)")
    assert published == slot_count, f"expected {slot_count} publishes, got {published}"
    assert not ring.try_publish(msg), "try_publish should fail when ring is full"

    got = ring.try_consume()
    assert got == msg, f"expected {msg!r}, got {got!r}"

    assert ring.try_publish(msg), "try_publish should succeed after consume"

    print(f"backpressure OK: full at {slot_count} slots, unblock after consume")

    ring.close(unlink=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
