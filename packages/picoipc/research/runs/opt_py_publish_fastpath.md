# opt/py-publish-fastpath — claim/publish sequential harness

## Summary

Branch `opt/py-publish-fastpath` (`ee35a67`) on top of `opt/py-zero-copy` (`f92f1e5`).

Publish: preallocated `bytearray`, `publish(length)` / `try_publish_length`.
Consume: `try_consume_into` via `_drain_ring`.

## Gate vs stored baseline (stale)

| Metric | Baseline | Candidate | Ratio |
|--------|----------|-----------|-------|
| sequential_msgs_per_sec_64b | 2,042,098 | ~1,820,000 | 0.89x |
| VERDICT | | **FAIL** | |

## Re-check vs current main (2026-08-23)

Three harness runs, smoke, pybind11:

| Branch | sequential msgs/s (64B) |
|--------|------------------------|
| main (9188b5b) | 1,960,904 / 2,027,492 / 2,070,942 |
| opt/py-publish-fastpath | 1,750,721 / 1,770,279 / 1,804,682 |

Median main: 2,027,492. Median branch: 1,770,279 (**0.87x**).

**Conclusion:** Real regression, not only stale baseline.

## Verdict

**no merge** — correctness PASS; ~10–15% slower than main at 64B.

## Follow-up

- APIs useful for 1KB payloads; smoke gate should use fastest path at 64B.
- Try publish-only fastpath without `try_consume_into` in timed loop.
