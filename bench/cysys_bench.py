"""Tier A sysmodule.h getter comparisons."""
import sys

from picop import lazy_import_mode, lazy_imports_supported, sys_get_attr
from _bench_util import BenchSession


def main():
    session = BenchSession("cysys — sysmodule.h getters (tier A)")
    session.header()
    session.section("sys attribute and option access")
    system = sys
    if sys.version_info >= (3, 15):
        session.compare("sys_get_attr", sys_get_attr, lambda name: getattr(system, name), "version")
        session.compare("lazy_imports_supported", lazy_imports_supported,
                        lambda: sys.version_info >= (3, 15), param="probe vs version check")
        session.compare("lazy_import_mode", lazy_import_mode,
                        lambda: getattr(system, "lazy_imports", 0), param="mode getter vs sys.flags attribute")
    session.summary()


if __name__ == "__main__":
    main()
