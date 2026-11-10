"""Tier B: cyfunction vs typed Cython cdef loops."""
from __future__ import annotations
from bench.tier_b._tb_util import N, ensure_ext, markdown_table, tier_b_session
def _f():
    return None
PAYLOAD = _f

def main() -> None:
    tb = ensure_ext("cyfunction")
    session = tier_b_session("cyfunction — Tier B")
    session.header(); print(f"inner loop N={N:,}"); print()
    session.section("func_check  [primary]")
    session.compare("func_check", tb.cypy_func_check, tb.baseline_func_check, PAYLOAD, N, param="def")
    session.section("func_get_code  [checked vs macro]")
    session.compare("func_get_code", tb.cypy_func_get_code, tb.baseline_func_get_code, PAYLOAD, N, param="def")
    session.compare(
        "func_get_code_unchecked",
        tb.cypy_func_get_code_unchecked,
        tb.baseline_func_get_code,
        PAYLOAD,
        N,
        param="def (macro)",
    )
    session.section("func_get_kw_defaults  [checked vs macro]")
    session.compare(
        "func_get_kw_defaults",
        tb.cypy_func_get_kw_defaults,
        tb.baseline_func_get_kw_defaults,
        PAYLOAD,
        N,
        param="def",
    )
    session.compare(
        "func_get_kw_defaults_unchecked",
        tb.cypy_func_get_kw_defaults_unchecked,
        tb.baseline_func_get_kw_defaults,
        PAYLOAD,
        N,
        param="def (macro)",
    )
    session.section("func_get_annotations  [checked vs macro]")
    session.compare(
        "func_get_annotations",
        tb.cypy_func_get_annotations,
        tb.baseline_func_get_annotations,
        PAYLOAD,
        N,
        param="def",
    )
    session.compare(
        "func_get_annotations_unchecked",
        tb.cypy_func_get_annotations_unchecked,
        tb.baseline_func_get_annotations,
        PAYLOAD,
        N,
        param="def (macro)",
    )
    session.section("func_set_kw_defaults")
    session.compare(
        "func_set_kw_defaults",
        tb.cypy_func_set_kw_defaults,
        tb.baseline_func_set_kw_defaults,
        PAYLOAD,
        N,
        {"c": 3},
        param="dict",
    )
    session.section("func_new_with_qualname")
    session.compare(
        "func_new_with_qualname",
        tb.cypy_func_new_with_qualname,
        tb.baseline_func_new_with_qualname,
        PAYLOAD,
        N,
        param="code + globals + qualname",
    )
    session.summary(); print("Markdown (paste under ### Tier B):"); print(markdown_table(session._rows)); print()

if __name__ == "__main__":
    main()
