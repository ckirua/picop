"""Python usage for picop cytime.

Run: python examples/pytime.py
"""
from picop import time_wall, time_monotonic, time_perf_counter

def main() -> None:
    t = time_wall()
    assert isinstance(t, float) and t > 0
    m = time_monotonic()
    p = time_perf_counter()
    assert isinstance(m, float) and isinstance(p, float)
    print("ok", round(t, 3))

if __name__ == "__main__":
    main()
