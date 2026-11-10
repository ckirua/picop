"""Compare C-API and Python warning calls with ignored warnings (tier A)."""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
from _bench_util import BenchSession  # noqa: E402
from picop import warn_ex  # noqa: E402


def py_warn(category, message):
    warnings.warn(message, category)


def py_warn_stacklevel(category, message):
    warnings.warn(message, category, stacklevel=2)
def main():
    session = BenchSession("cywarnings — ignored warning dispatch (tier A)")
    session.header()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        assert warn_ex(RuntimeWarning, "ignored") == 0
        session.section("ignored warning dispatch")
        session.compare("warn_ex", warn_ex, py_warn, RuntimeWarning, "ignored", param="vs warnings.warn")
        session.compare("warn_ex", warn_ex, py_warn_stacklevel, RuntimeWarning, "ignored", param="vs warnings.warn stacklevel=2")
    session.summary()


if __name__ == "__main__":
    main()
