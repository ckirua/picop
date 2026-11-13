"""Interpreter guards: keep the interpreter alive while foreign threads run.

Order 077 example. On CPython < 3.15 the guard API is unavailable and this
script reports that instead of failing.
"""

from picop import guards_supported, interpreter_guard


def main() -> None:
    if not guards_supported():
        print("interpreter guards require CPython 3.15+; nothing to do here.")
        return
    with interpreter_guard():
        print("interpreter cannot finalize while this guard is open")
    print("guard closed; finalization allowed again")


if __name__ == "__main__":
    main()
