"""Tier A interpreter-guard comparisons (Order 077)."""
import sys

from picop import guards_supported, interpreter_guard
from _bench_util import BenchSession


def main():
    session = BenchSession("cythread — interpreter guards (tier A)")
    session.header()
    session.section("guard support probe")
    session.compare("guards_supported", guards_supported,
                    lambda: sys.version_info >= (3, 15), param="vs version check")
    if guards_supported():
        session.section("guard acquire + close")

        def guard_cm():
            with interpreter_guard():
                pass

        session.compare("interpreter_guard", guard_cm, lambda: None, param="acquire+close vs no-op")
    session.summary()


if __name__ == "__main__":
    main()
