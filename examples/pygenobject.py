"""Python usage for picop cygenobject.

Run: python examples/pygenobject.py
"""
from picop import gen_check, gen_check_exact, gen_eq


def main() -> None:
    def g():
        yield 1

    gen = g()
    other = g()
    assert gen_check(gen) and gen_check_exact(gen)
    assert not gen_check([1])
    assert gen_eq(gen, gen) and not gen_eq(gen, other)
    assert gen_eq(gen, gen) is (gen is gen)
    print("ok", gen_check(gen), gen_eq(gen, gen))


if __name__ == "__main__":
    main()
