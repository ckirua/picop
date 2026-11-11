"""Tier A sysmodule.h getter comparisons."""
import sys

from picop import sys_get_attr
from _bench_util import BenchSession


def main():
    session = BenchSession("cysys — sysmodule.h getters (tier A)")
    session.header()
    session.section("sys attribute and option access")
    system = sys
    if sys.version_info >= (3, 15):
        session.compare("sys_get_attr", sys_get_attr, lambda name: getattr(system, name), "version")
    session.summary()


if __name__ == "__main__":
    main()
