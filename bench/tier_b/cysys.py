"""Tier B sysmodule.h getter loops."""
import sys

from bench.tier_b._tb_util import N, ensure_ext, markdown_table, tier_b_session


def main():
    tb = ensure_ext("cysys")
    session = tier_b_session("cysys — Tier B getters")
    session.header()
    print(f"inner loop N={N:,}\n")
    session.section("sys attribute getters")
    session.compare("sys_get_object", tb.cypy_get_object, tb.baseline_get_object, "version", N)
    session.compare("sys_get_xoptions", tb.cypy_get_xoptions, tb.baseline_get_xoptions, N)
    if sys.version_info >= (3, 15):
        session.compare("sys_get_attr", tb.cypy_get_attr, tb.baseline_get_attr, "version", N)
        session.compare("sys_get_attr_string", tb.cypy_get_attr_string, tb.baseline_get_attr_string, "version", N)
    session.summary()
    print(markdown_table(session._rows))


if __name__ == "__main__":
    main()
