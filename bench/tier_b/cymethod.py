"""Tier B: cymethod vs typed Cython cdef loops."""
from __future__ import annotations
from bench.tier_b._tb_util import N, ensure_ext, markdown_table, tier_b_session
class _T:
    def m(self):
        return None

PAYLOAD = _T().m

def main() -> None:
    tb = ensure_ext("cymethod")
    session = tier_b_session("cymethod — Tier B")
    session.header(); print(f"inner loop N={N:,}"); print()
    session.section("method_check  [primary]")
    session.compare("method_check", tb.cypy_method_check, tb.baseline_method_check, PAYLOAD, N, param="bound")
    session.section("cfunction_check  [checked vs exact]")
    session.compare(
        "cfunction_check",
        tb.cypy_cfunction_check,
        tb.baseline_cfunction_check,
        len,
        N,
        param="builtin",
    )
    session.compare(
        "cfunction_check_exact",
        tb.cypy_cfunction_check_exact,
        tb.baseline_cfunction_check_exact,
        len,
        N,
        param="builtin",
    )
    session.section("cfunction_get_self  [checked vs macro]")
    session.compare(
        "cfunction_get_self",
        tb.cypy_cfunction_get_self,
        tb.baseline_cfunction_get_self,
        len,
        N,
        param="builtin",
    )
    session.compare(
        "cfunction_get_self_unchecked",
        tb.cypy_cfunction_get_self_unchecked,
        tb.baseline_cfunction_get_self,
        len,
        N,
        param="builtin (macro)",
    )
    session.section("classmethod_new / staticmethod_new")
    session.compare(
        "classmethod_new",
        tb.cypy_classmethod_new,
        tb.baseline_classmethod_new,
        PAYLOAD,
        N,
        param="wrap",
    )
    session.compare(
        "staticmethod_new",
        tb.cypy_staticmethod_new,
        tb.baseline_staticmethod_new,
        PAYLOAD,
        N,
        param="wrap",
    )
    session.summary(); print("Markdown (paste under ### Tier B):"); print(markdown_table(session._rows)); print()

if __name__ == "__main__":
    main()
