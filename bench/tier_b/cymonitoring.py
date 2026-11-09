"""Tier B: cymonitoring scope/fire helpers vs the raw C-API externs an author writes.

Run: bash bench/tier_b/run.sh cymonitoring
"""
from __future__ import annotations

import sys

from bench.tier_b._tb_util import N, ensure_ext, markdown_table, tier_b_session

# Tool ids 0-5 are caller-owned; 6/7 are reserved for sys.setprofile/settrace.
TOOL_A = 5
TOOL_B = 4


def _arm(tool_id: int, seen: list[tuple[object, ...]]) -> None:
    sys.monitoring.use_tool_id(tool_id, f"picop-tier-b-{tool_id}")
    sys.monitoring.register_callback(
        tool_id, sys.monitoring.events.PY_RETURN, lambda *args: seen.append(args)
    )
    sys.monitoring.set_events(tool_id, sys.monitoring.events.PY_RETURN)


def _disarm(tool_id: int) -> None:
    sys.monitoring.free_tool_id(tool_id)


def main() -> None:
    tb = ensure_ext("cymonitoring")
    code = compile("y = 1", "<tier-b>", "exec")
    session = tier_b_session("cymonitoring — Tier B")
    session.header()
    print(f"inner loop N={N:,}")
    print()

    session.section("scope enter+exit per emulated call (no tool watching)")
    session.compare(
        "monitoring_scope / monitoring_exit_scope (18-event scope)",
        tb.cypy_scope_pair,
        tb.baseline_scope_pair,
        code,
        N,
        param="vs hand-rolled 3-id array",
    )
    session.compare(
        "monitoring_scope / monitoring_exit_scope (18-event scope)",
        tb.cypy_scope_pair,
        tb.baseline_scope_pair_full,
        code,
        N,
        param="vs hand-built 18-id array",
    )

    session.section("fire PY_RETURN with nothing watching")
    session.compare(
        "fire_py_return (inline active gate)",
        tb.cypy_fire_inactive,
        tb.baseline_fire_inactive,
        code,
        N,
        param="scope entered, no tool",
    )

    seen: list[tuple[object, ...]] = []
    _arm(TOOL_A, seen)
    session.section("fire PY_RETURN with one tool watching")
    session.compare(
        "fire_py_return (inline active gate)",
        tb.cypy_fire_active,
        tb.baseline_fire_active,
        code,
        N,
        param="1 tool live",
    )
    _arm(TOOL_B, seen)
    session.section("fire PY_RETURN with two tools watching")
    session.compare(
        "fire_py_return (inline active gate)",
        tb.cypy_fire_active,
        tb.baseline_fire_active,
        code,
        N,
        param="2 tools live",
    )
    _disarm(TOOL_B)
    _disarm(TOOL_A)
    print(f"callbacks observed by the harness: {len(seen):,}")

    session.summary()
    print("Markdown (paste under ### Tier B):")
    print(markdown_table(session._rows))
    print()


if __name__ == "__main__":
    main()
