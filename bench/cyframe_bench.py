"""Compare public :mod:`picop` frame helpers with plain Python calls (tier A)."""

from __future__ import annotations

import sys
import types
from pathlib import Path

_BENCH_ROOT = Path(__file__).resolve().parent
if str(_BENCH_ROOT) not in sys.path:
    sys.path.insert(0, str(_BENCH_ROOT))

from picop import (  # noqa: E402
    frame_back, frame_builtins, frame_check, frame_code, frame_generator,
    frame_globals, frame_lasti, frame_lineno, frame_locals, frame_var,
    frame_var_cstr,
)
from _bench_util import BenchSession  # noqa: E402


def make_frame():
    value = 42
    return sys._getframe()


def py_frame_check(frame):
    return isinstance(frame, types.FrameType)


def py_frame_var(frame, name):
    return frame.f_locals[name]


def py_frame_var_cstr(frame, name):
    return frame.f_locals["value"]


def py_frame_generator(frame):
    return None


def main() -> None:
    frame = make_frame()
    session = BenchSession("cyframe — public helpers vs plain Python (tier A)")
    session.header()
    session.section("frame accessors")
    session.compare("frame_check", frame_check, py_frame_check, frame)
    session.compare("frame_lineno", frame_lineno, lambda f: f.f_lineno, frame)
    session.compare("frame_lasti", frame_lasti, lambda f: f.f_lasti, frame)
    session.compare("frame_code", frame_code, lambda f: f.f_code, frame)
    session.compare("frame_back", frame_back, lambda f: f.f_back, frame)
    session.compare("frame_locals", frame_locals, lambda f: f.f_locals, frame)
    session.compare("frame_globals", frame_globals, lambda f: f.f_globals, frame)
    session.compare("frame_builtins", frame_builtins, lambda f: f.f_builtins, frame)
    session.compare("frame_generator", frame_generator, py_frame_generator, frame)
    session.compare("frame_var", frame_var, py_frame_var, frame, "value")
    session.compare("frame_var_cstr", frame_var_cstr, py_frame_var_cstr, frame, b"value")
    session.summary()


if __name__ == "__main__":
    main()
