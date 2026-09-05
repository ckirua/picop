#!/usr/bin/env python3
"""Producer: writes numbered messages into the ring."""

import argparse
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from picoipc import Ring


def main() -> int:
    p = argparse.ArgumentParser(description="picoipc SPSC producer")
    p.add_argument("name", nargs="?", default="smh_q_demo")
    p.add_argument("count", nargs="?", type=int, default=10)
    p.add_argument("delay_ms", nargs="?", type=int, default=100)
    args = p.parse_args()

    ring = Ring(args.name, create=True, slot_count=16, slot_size=128)
    print(f"producer: name={args.name} count={args.count} delay_ms={args.delay_ms}")

    for i in range(args.count):
        msg = f"msg-{i:04d}".encode()
        while not ring.try_publish(msg):
            time.sleep(0.001)
        print(f"published: {msg.decode()} (write_seq={ring.write_seq()})")
        time.sleep(args.delay_ms / 1000.0)

    print("producer done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
