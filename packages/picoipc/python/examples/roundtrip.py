#!/usr/bin/env python3
"""Single-process roundtrip: create ring, publish, consume."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from smh_q import Ring


def main() -> int:
    name = f"smh_q_py_roundtrip_{os.getpid()}"
    Ring.unlink(name)

    cfg = dict(name=name, create=True, slot_count=8, slot_size=128, schema_id=42)
    producer = Ring(**cfg)
    consumer = Ring(name=name, create=False, schema_id=42)

    msg = b"hello-smh_q-py"
    assert producer.try_publish(msg), "publish failed"
    got = consumer.try_consume()
    assert got == msg, f"expected {msg!r}, got {got!r}"

    producer.close(unlink=True)
    print("roundtrip OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
