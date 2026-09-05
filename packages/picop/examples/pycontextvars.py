"""Python usage for picop cycontextvars.

Run: python examples/pycontextvars.py
"""
import contextvars

from picop import (
    context_eq,
    ctx_check_exact,
    ctx_copy_current,
    ctxvar_check_exact,
    ctxvar_new,
)


def main() -> None:
    v = ctxvar_new(b"demo", 1)
    assert ctxvar_check_exact(v)
    cur = ctx_copy_current()
    assert ctx_check_exact(cur)

    a = contextvars.Context()
    b = contextvars.Context()
    assert context_eq(a, b)
    assert context_eq(a, a)
    assert context_eq(a, b) == (a == b)

    def set_one() -> None:
        v.set(42)

    a.run(set_one)
    assert not context_eq(a, b)
    assert context_eq(a, a) == (a == a)
    print("ok", type(v).__name__, type(cur).__name__, "context_eq")


if __name__ == "__main__":
    main()
