#!/usr/bin/env python3
"""Consumer: reads messages, blocking on futex when idle."""

import argparse
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from smh_q import Ring


def main() -> int:
    p = argparse.ArgumentParser(description="smh_q consumer")
    p.add_argument("name", nargs="?", default="smh_q_demo")
    p.add_argument("timeout_ms", nargs="?", type=int, default=5000)
    args = p.parse_args()

    ring = Ring(args.name, create=False)
    print(f"consumer: name={args.name} timeout_ms={args.timeout_ms}")

    deadline = time.monotonic() + args.timeout_ms / 1000.0
    received = 0

    while time.monotonic() < deadline:
        msg = ring.try_consume()
        if msg is not None:
            print(
                f"consumed: {msg.decode()} "
                f"(read_seq={ring.read_seq()} write_seq={ring.write_seq()})"
            )
            received += 1
            continue

        rem_ms = int((deadline - time.monotonic()) * 1000)
        if rem_ms <= 0:
            break
        if not ring.wait_readable(rem_ms):
            break

    print(f"consumer done: received={received}")
    return 0 if received > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
