#!/usr/bin/env python3
"""Compare candidate bench JSON against baseline; print table and verdict."""
from __future__ import annotations
import argparse, json
from pathlib import Path

def load_json(path: Path) -> dict:
    with path.open() as f:
        return json.load(f)

def fmt_rate(v):
    return "n/a" if v is None else f"{v:,.0f}"

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("baseline", type=Path)
    p.add_argument("candidate", type=Path)
    p.add_argument("--multiplier", type=float, default=None)
    args = p.parse_args()
    baseline, candidate = load_json(args.baseline), load_json(args.candidate)
    mult = args.multiplier or float(candidate.get("throughput_multiplier", 1.25))
    base_impl = baseline.get("impl", "")
    cand_impl = candidate.get("impl", "")
    if base_impl == cand_impl:
        mult = 1.0
    base_seq = float(baseline.get("sequential_msgs_per_sec_64b", 0))
    cand_seq = float(candidate.get("sequential_msgs_per_sec_64b", 0))
    required = base_seq * mult
    speedup = (cand_seq / base_seq) if base_seq > 0 else 0.0
    print("=== smh_q gate comparison ===")
    print(f"baseline impl:  {base_impl}")
    print(f"candidate impl: {cand_impl}")
    print(f"git sha:        {candidate.get('git_sha', '?')}")
    print()
    for label, key in [
        ("sequential_msgs_per_sec_64b", "sequential_msgs_per_sec_64b"),
        ("threaded_msgs_per_sec_64b", "threaded_msgs_per_sec_64b"),
        ("cpp_sequential_msgs_per_sec_64b", "cpp_sequential_msgs_per_sec_64b"),
    ]:
        b, c = baseline.get(key), candidate.get(key)
        ratio = (float(c)/float(b)) if b and c and float(b)>0 else None
        print(f"{label:<35} {fmt_rate(b):>12} {fmt_rate(c):>12} {(f'{ratio:.2f}x' if ratio else 'n/a'):>8}")
    print()
    print(f"required sequential (>={mult:.2f}x): {required:,.0f} msgs/s")
    print(f"candidate sequential:            {cand_seq:,.0f} msgs/s")
    print(f"speedup:                         {speedup:.2f}x")
    correctness_ok = candidate.get("correctness_pass", candidate.get("correctness_ok", False))
    wall_ok = candidate.get("wall_s", 999) <= candidate.get("max_wall_s", 90)
    throughput_ok = cand_seq >= required if base_seq > 0 else True
    print()
    print(f"correctness: {'PASS' if correctness_ok else 'FAIL'}")
    print(f"wall time:   {'PASS' if wall_ok else 'FAIL'} ({candidate.get('wall_s', '?')}s / {candidate.get('max_wall_s', 90)}s)")
    print(f"throughput:  {'PASS' if throughput_ok else 'FAIL'}")
    passed = correctness_ok and wall_ok and throughput_ok
    print()
    print("VERDICT: " + ("PASS" if passed else "FAIL"))
    return 0 if passed else 1

if __name__ == "__main__":
    raise SystemExit(main())
