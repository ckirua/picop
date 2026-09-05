#!/usr/bin/env python3
"""Throughput benchmark: threaded SPSC (paired threads)."""

import argparse
import os
import struct
import sys
import threading
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from picoipc import Ring


def slot_bytes(payload_bytes: int) -> int:
    return max(64, payload_bytes + 8)


def percentile(samples: list[int], p: float) -> float:
    if not samples:
        return 0.0
    idx = int(p * (len(samples) - 1))
    return float(samples[idx])


def run_threaded(count: int, payload_bytes: int) -> None:
    name = f"smh_q_py_bench_tp_{os.getpid()}"
    Ring.unlink(name)

    producer = Ring(
        name,
        create=True,
        slot_count=256,
        slot_size=slot_bytes(payload_bytes),
    )
    consumer = Ring(name=name, create=False)

    payload = bytes(payload_bytes)
    latencies: list[int] = [0] * count
    received = 0
    go = threading.Event()

    def reader() -> None:
        nonlocal received
        go.wait()
        while received < count:
            msg = consumer.try_consume()
            if msg is None:
                continue
            pub_ns = struct.unpack_from("<Q", msg, 0)[0]
            latencies[received] = time.time_ns() - pub_ns
            received += 1

    t = threading.Thread(target=reader, daemon=True)
    t.start()

    t0 = time.perf_counter()
    go.set()
    for _ in range(count):
        stamp = struct.pack("<Q", time.time_ns())
        body = stamp + payload[len(stamp):]
        while not producer.try_publish(body):
            pass

    t.join(timeout=30.0)
    t1 = time.perf_counter()
    producer.close(unlink=True)

    elapsed_ms = (t1 - t0) * 1000.0
    samples = sorted(latencies[:received])
    msgs_per_sec = count / (elapsed_ms / 1000.0)
    mb_per_sec = msgs_per_sec * payload_bytes / (1024.0 * 1024.0)
    print(
        f"{'threaded':<12} payload={payload_bytes:4d}B count={count:7d} "
        f"elapsed={elapsed_ms:8.2f} ms  msgs/s={msgs_per_sec:10.0f}  "
        f"MB/s={mb_per_sec:8.2f}  p50={percentile(samples, 0.50):6.0f} ns  "
        f"p99={percentile(samples, 0.99):6.0f} ns"
    )


def run_sequential(count: int, payload_bytes: int) -> None:
    name = f"smh_q_py_bench_seq_{os.getpid()}"
    Ring.unlink(name)

    ring = Ring(
        name,
        create=True,
        slot_count=max(count, 256),
        slot_size=slot_bytes(payload_bytes),
    )
    payload = bytes(payload_bytes)

    t0 = time.perf_counter()
    for _ in range(count):
        while not ring.try_publish(payload):
            pass
    for _ in range(count):
        while ring.try_consume() is None:
            pass
    t1 = time.perf_counter()
    ring.close(unlink=True)

    elapsed_ms = (t1 - t0) * 1000.0
    msgs_per_sec = count / (elapsed_ms / 1000.0)
    mb_per_sec = msgs_per_sec * payload_bytes / (1024.0 * 1024.0)
    print(
        f"{'sequential':<12} payload={payload_bytes:4d}B count={count:7d} "
        f"elapsed={elapsed_ms:8.2f} ms  msgs/s={msgs_per_sec:10.0f}  "
        f"MB/s={mb_per_sec:8.2f}"
    )


def main() -> int:
    p = argparse.ArgumentParser(description="smh_q Python throughput benchmark")
    p.add_argument("count", nargs="?", type=int, default=100_000)
    p.add_argument("payload", nargs="?", type=int, default=0,
                   help="payload bytes (0 = run 64, 256, 1024)")
    args = p.parse_args()

    payloads = [args.payload] if args.payload > 0 else [64, 256, 1024]

    print(f"smh_q bench_throughput (count={args.count})")
    print("mode         payload  count    elapsed_ms    throughput")
    print("----------------------------------------------------------------")

    for pb in payloads:
        run_threaded(args.count, pb)
        run_sequential(args.count, pb)
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
