"""Tier B: cydict public helpers vs typed Cython ``cdef`` loops.

Run::

    python -m bench.tier_b.build cydict
    python -m bench.tier_b.cydict
"""

from __future__ import annotations

from bench.tier_b._tb_util import N, ensure_ext, markdown_table, tier_b_session
dict_keys = type({}.keys())
dict_values = type({}.values())
dict_items = type({}.items())
PAYLOAD = {"symbol": "BTCUSDT", "price": "1", "qty": "2"}


def main() -> None:
    tb = ensure_ext("cydict")
    session = tier_b_session("cydict — Tier B (cypy vs typed Cython cdef loop)")
    session.header()
    print(f"inner loop N={N:,}")
    print()
    session.section("dict_get vs dict.get  [primary]")
    session.compare("dict_get", tb.cypy_dget, tb.baseline_dget, PAYLOAD, "symbol", N, param="hit symbol")
    session.section("dict_contains / dict_len / dict_check")
    session.compare("dict_contains", tb.cypy_dcontains, tb.baseline_dcontains, PAYLOAD, "symbol", N, param="hit")
    session.compare("dict_len", tb.cypy_dlen, tb.baseline_dlen, PAYLOAD, N, param="n=3")
    session.compare("dict_check", tb.cypy_dcheck, tb.baseline_dcheck, PAYLOAD, N, param="dict")
    session.section("dict view predicates vs isinstance")
    session.compare("dict_keys_check", tb.cypy_dict_keys_check, tb.baseline_view_check, PAYLOAD.keys(), dict_keys, N, param="hit")
    session.compare("dict_values_check", tb.cypy_dict_values_check, tb.baseline_view_check, PAYLOAD.values(), dict_values, N, param="hit")
    session.compare("dict_items_check", tb.cypy_dict_items_check, tb.baseline_view_check, PAYLOAD.items(), dict_items, N, param="hit")
    session.compare("dict_view_check", tb.cypy_dict_view_check, tb.baseline_view_check, PAYLOAD.keys(), (dict_keys, dict_items), N, param="hit")
    session.compare("dict_view_check", tb.cypy_dict_view_check, tb.baseline_view_check, PAYLOAD.items(), (dict_keys, dict_items), N, param="items hit")
    session.compare("dict_view_check", tb.cypy_dict_view_check, tb.baseline_view_check, PAYLOAD.values(), (dict_keys, dict_items), N, param="values miss")
    session.section("dict set — watcher dispatch cost  [informational]")
    WATCHED = {"watch_key": "x"}
    session.compare(
        "dict_set (no-op watcher)",
        tb.cypy_dict_set_noop_cb,
        tb.cypy_dict_set_plain,
        WATCHED,
        N,
        "v",
        param="N sets",
    )
    session.compare(
        "dict_set (counting watcher)",
        tb.cypy_dict_set_count_cb,
        tb.cypy_dict_set_plain,
        WATCHED,
        N,
        "v",
        param="N sets",
    )
    session.summary()
    print("Markdown (paste under ### Tier B):")
    print(markdown_table(session._rows))
    print()


if __name__ == "__main__":
    main()
