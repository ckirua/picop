#!/usr/bin/env python3
"""Unified benchmark harness: correctness smoke + timed benchmarks -> JSON."""

from __future__ import annotations

import argparse
import json
import os
import struct
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]

ROOT = Path(__file__).resolve().parent.parent
CPP_BUILD = ROOT / "build" / "native"
ARTIFACTS = ROOT / "artifacts"
PYTHON_DIR = ROOT / "src"


def _git_sha() -> str:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=ROOT,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        return out.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def _gil_enabled() -> bool | None:
    fn = getattr(sys, "_is_gil_enabled", None)
    return fn() if callable(fn) else None


def _backend_impl() -> str:
    backend = os.environ.get("PICOIPC_BACKEND", "pybind11").lower()
    mapping = {
        "pure": "pure_python",
        "pure_python": "pure_python",
        "ctypes": "ctypes",
        "pybind11": "pybind11",
        "cython": "cython",
    }
    return mapping.get(backend, backend)


def _slot_bytes(payload_bytes: int) -> int:
    return max(64, payload_bytes + 8)


def _ensure_import_path() -> None:
    sys.path.insert(0, str(PYTHON_DIR))


def _run_cmd(name: str, cmd: list[str], cwd: Path | None = None) -> None:
    proc = subprocess.run(
        cmd,
        cwd=cwd or ROOT,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        msg = proc.stderr.strip() or proc.stdout.strip() or f"exit {proc.returncode}"
        raise RuntimeError(f"{name} failed: {msg}")


def correctness_cpp_roundtrip() -> None:
    exe = CPP_BUILD / "roundtrip"
    if not exe.is_file():
        raise FileNotFoundError(f"missing {exe}; run cmake build first")
    _run_cmd("cpp_roundtrip", [str(exe)])


def correctness_cpp_stress() -> None:
    exe = CPP_BUILD / "stress"
    if not exe.is_file():
        raise FileNotFoundError(f"missing {exe}")
    _run_cmd("cpp_stress", [str(exe)])


def correctness_py_roundtrip() -> None:
    script = ROOT / "examples" / "python" / "roundtrip.py"
    _run_cmd("py_roundtrip", [sys.executable, str(script)])


def correctness_py_cpp_xlang() -> None:
    _ensure_import_path()
    from picoipc import Ring

    name = f"smh_q_xlang_{os.getpid()}"
    Ring.unlink(name)

    cpp_producer = CPP_BUILD / "producer"
    if not cpp_producer.is_file():
        raise FileNotFoundError(f"missing {cpp_producer}")

    _run_cmd("py_cpp_xlang_producer", [str(cpp_producer), name, "1", "0"])

    consumer = Ring(name=name, create=False)
    got = None
    for _ in range(5000):
        got = consumer.try_consume()
        if got is not None:
            break
        time.sleep(0.0001)
    consumer.close()

    if got is None:
        Ring.unlink(name)
        raise RuntimeError("py_cpp_xlang: Python consumer got no message from C++ producer")

    if not got.startswith(b"msg-"):
        Ring.unlink(name)
        raise RuntimeError(f"py_cpp_xlang: unexpected payload {got!r}")

    Ring.unlink(name)


CORRECTNESS_FUNCS = {
    "cpp_roundtrip": correctness_cpp_roundtrip,
    "cpp_stress": correctness_cpp_stress,
    "py_roundtrip": correctness_py_roundtrip,
    "py_cpp_xlang": correctness_py_cpp_xlang,
}


def run_correctness(steps: list[str]) -> dict[str, bool]:
    results: dict[str, bool] = {}
    for step in steps:
        fn = CORRECTNESS_FUNCS.get(step)
        if fn is None:
            raise ValueError(f"unknown correctness step: {step}")
        try:
            fn()
            results[step] = True
        except Exception as exc:
            print(f"correctness {step} FAIL: {exc}", file=sys.stderr)
            results[step] = False
    return results


def _make_publish_fn(ring, payload_buf: bytearray, payload_bytes: int, copy_payload: bool):
    if hasattr(ring, "claim") and hasattr(ring, "publish"):
        if copy_payload and payload_bytes:
            def publish_one() -> None:
                while True:
                    slot = ring.claim()
                    if slot is not None:
                        slot[:payload_bytes] = payload_buf[:payload_bytes]
                        ring.publish(payload_bytes)
                        return
        else:
            def publish_one() -> None:
                while not ring.publish(payload_bytes):
                    pass
    else:
        payload = bytes(payload_buf[:payload_bytes])

        def publish_one() -> None:
            while not ring.try_publish(payload):
                pass

    return publish_one


def bench_sequential(count: int, payload_bytes: int, warmup: int) -> float:
    _ensure_import_path()
    from picoipc import Ring

    name = f"smh_q_harness_seq_{os.getpid()}_{threading.get_ident()}"
    Ring.unlink(name)

    ring = Ring(
        name,
        create=True,
        slot_count=max(count, 256),
        slot_size=_slot_bytes(payload_bytes),
    )
    payload_buf = bytearray(payload_bytes)
    publish_one = _make_publish_fn(
        ring, payload_buf, payload_bytes, copy_payload=any(payload_buf)
    )

    for _ in range(warmup):
        publish_one()
        while ring.try_consume() is None:
            pass

    t0 = time.perf_counter()
    for _ in range(count):
        publish_one()
    for _ in range(count):
        while ring.try_consume() is None:
            pass
    elapsed = time.perf_counter() - t0
    ring.close(unlink=True)

    return count / elapsed if elapsed > 0 else 0.0


def bench_threaded(count: int, payload_bytes: int, warmup: int) -> float:
    _ensure_import_path()
    from picoipc import Ring

    name = f"smh_q_harness_thr_{os.getpid()}_{threading.get_ident()}"
    Ring.unlink(name)

    producer = Ring(
        name,
        create=True,
        slot_count=256,
        slot_size=_slot_bytes(payload_bytes),
    )
    consumer = Ring(name=name, create=False)
    payload = bytes(payload_bytes)
    done = 0
    go = threading.Event()

    def reader() -> None:
        nonlocal done
        go.wait()
        while done < count:
            msg = consumer.try_consume()
            if msg is None:
                continue
            done += 1

    t = threading.Thread(target=reader, daemon=True)
    t.start()

    stamp_len = min(8, payload_bytes)
    for _ in range(warmup):
        stamp = struct.pack("<Q", time.time_ns())
        body = stamp + payload[stamp_len:]
        while not producer.try_publish(body):
            pass

    t0 = time.perf_counter()
    go.set()
    for _ in range(count):
        stamp = struct.pack("<Q", time.time_ns())
        body = stamp + payload[stamp_len:]
        while not producer.try_publish(body):
            pass

    t.join(timeout=60.0)
    elapsed = time.perf_counter() - t0
    producer.close(unlink=True)

    if done < count:
        raise RuntimeError(f"threaded bench incomplete: {done}/{count}")
    return count / elapsed if elapsed > 0 else 0.0


def bench_cpp_sequential(count: int, payload_bytes: int) -> float:
    exe = CPP_BUILD / "bench_sequential"
    if not exe.is_file():
        return 0.0
    proc = subprocess.run(
        [str(exe), str(count), str(payload_bytes)],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"cpp bench_sequential failed: {proc.stderr}")
    for line in proc.stdout.splitlines():
        if "msgs/s=" in line:
            part = line.split("msgs/s=")[-1].strip().split()[0]
            return float(part)
    raise RuntimeError("could not parse cpp bench_sequential output")


def load_config(path: Path) -> dict:
    if yaml is None:
        raise RuntimeError("PyYAML required: pip install pyyaml")
    with path.open() as f:
        return yaml.safe_load(f)


def run_harness(config_path: Path, output: Path | None = None) -> dict:
    config_path = config_path.resolve()
    cfg = load_config(config_path)
    t_start = time.perf_counter()

    correctness_steps = list(cfg.get("correctness", []))
    correctness = run_correctness(correctness_steps)
    correctness_ok = all(correctness.values())

    warmup = int(cfg.get("warmup_iters", 500))
    count = int(cfg.get("count", 5000))
    payloads = list(cfg.get("payloads", [64]))
    modes = list(cfg.get("modes", ["sequential"]))
    threaded_count = int(cfg.get("python_threaded_count", 2000))
    cpp_ref = bool(cfg.get("cpp_reference", True))
    max_wall_s = float(cfg.get("max_wall_s", 90))
    throughput_multiplier = float(cfg.get("throughput_multiplier", 1.25))

    result: dict = {
        "impl": _backend_impl(),
        "gil_enabled": _gil_enabled(),
        "python": sys.executable,
        "git_sha": _git_sha(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "config": str(config_path.resolve().relative_to(ROOT)),
        "correctness": correctness,
        "correctness_ok": correctness_ok,
        "correctness_pass": correctness_ok,
        "max_wall_s": max_wall_s,
        "throughput_multiplier": throughput_multiplier,
    }

    primary_payload = payloads[0] if payloads else 64

    if "sequential" in modes:
        rate = bench_sequential(count, primary_payload, warmup)
        result[f"sequential_msgs_per_sec_{primary_payload}b"] = rate
        if primary_payload == 64:
            result["sequential_msgs_per_sec_64b"] = rate

    if "threaded" in modes:
        thr_rate = bench_threaded(threaded_count, primary_payload, min(warmup, 200))
        result[f"threaded_msgs_per_sec_{primary_payload}b"] = thr_rate
        if primary_payload == 64:
            result["threaded_msgs_per_sec_64b"] = thr_rate

    if cpp_ref:
        cpp_rate = bench_cpp_sequential(count, primary_payload)
        result[f"cpp_sequential_msgs_per_sec_{primary_payload}b"] = cpp_rate
        if primary_payload == 64:
            result["cpp_sequential_msgs_per_sec_64b"] = cpp_rate

    result["wall_s"] = round(time.perf_counter() - t_start, 3)

    out_path = output
    if out_path is None:
        ARTIFACTS.mkdir(parents=True, exist_ok=True)
        sha = result["git_sha"]
        out_path = ARTIFACTS / f"bench_{sha}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w") as f:
        json.dump(result, f, indent=2)
        f.write("\n")

    return result


def main() -> int:
    p = argparse.ArgumentParser(description="picoipc unified benchmark harness")
    p.add_argument(
        "--config",
        type=Path,
        default=ROOT / "bench" / "config_smoke.yaml",
        help="YAML config path",
    )
    p.add_argument(
        "--output",
        type=Path,
        default=None,
        help="output JSON path (default: artifacts/bench_<sha>.json)",
    )
    args = p.parse_args()

    _ensure_import_path()
    result = run_harness(args.config, args.output)
    print(json.dumps(result, indent=2))
    return 0 if result.get("correctness_ok", False) else 1


if __name__ == "__main__":
    raise SystemExit(main())
