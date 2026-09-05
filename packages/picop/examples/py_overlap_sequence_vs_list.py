"""Overlap playbook: known ``list``/``tuple`` → typed; unknown sequence → cysequence.

Run: python examples/py_overlap_sequence_vs_list.py
"""

from __future__ import annotations

from picop import list_get, list_len, seq_check, seq_get, seq_len, tuple_get, tuple_len

def main() -> None:
    xs: list[int] = [10, 20, 30]
    t: tuple[int, ...] = (1, 2, 3)

    # Known list / tuple → Core typed helpers
    assert list_len(xs) == 3
    assert list_get(xs, 1) == 20
    assert tuple_len(t) == 3
    assert tuple_get(t, 0) == 1

    # Unknown sequence-like (str, range, …) → protocol helpers
    assert seq_check("ab")
    assert seq_len("ab") == 2
    assert seq_get("ab", 1) == "b"
    assert seq_len(range(4)) == 4

    # seq_* works on list too, but prefer list_* when typed
    assert seq_len(xs) == 3
    print("ok sequence vs list", list_len(xs), seq_len("ab"))

if __name__ == "__main__":
    main()
