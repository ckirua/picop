"""Python usage for picop cydatetime.

Run: python examples/pydatetime.py
"""
from datetime import date, datetime, time, timedelta, timezone

from picop import (
    dt_date_check,
    dt_date_eq,
    dt_date_new,
    dt_date_year,
    dt_datetime_eq,
    dt_datetime_new,
    dt_time_eq,
    dt_time_new,
    dt_timedelta_check,
    dt_timedelta_days,
    dt_timedelta_eq,
    dt_timedelta_new,
)

def main() -> None:
    d = dt_date_new(2026, 7, 21)
    assert dt_date_check(d)
    assert dt_date_year(d) == 2026
    assert dt_date_eq(d, date(2026, 7, 21)) and not dt_date_eq(d, date(2026, 7, 22))
    assert dt_date_eq(d, d)
    assert not dt_date_eq(d, datetime(2026, 7, 21))  # date vs datetime

    t = dt_time_new(12, 30, 45, 1000)
    assert dt_time_eq(t, time(12, 30, 45, 1000)) and not dt_time_eq(t, time(12, 30, 45, 1001))
    assert dt_time_eq(t, t)
    assert dt_time_eq(time(1, 2, 3, fold=0), time(1, 2, 3, fold=1))  # fold ignored
    assert not dt_time_eq(time(1), time(1, tzinfo=timezone.utc))  # naive vs aware

    dt = dt_datetime_new(2026, 7, 21, 12, 30, 45, 1000)
    assert dt_datetime_eq(dt, datetime(2026, 7, 21, 12, 30, 45, 1000))
    assert not dt_datetime_eq(dt, datetime(2026, 7, 21, 12, 30, 45, 1001))
    assert dt_datetime_eq(dt, dt)
    assert dt_datetime_eq(
        datetime(2020, 1, 1, fold=0), datetime(2020, 1, 1, fold=1)
    )  # fold ignored
    assert not dt_datetime_eq(dt, datetime(2026, 7, 21, 12, 30, 45, 1000, tzinfo=timezone.utc))
    assert not dt_datetime_eq(dt, date(2026, 7, 21))  # datetime vs date

    td = dt_timedelta_new(1, 2, 3)
    assert dt_timedelta_check(td)
    assert dt_timedelta_days(td) == 1
    assert dt_timedelta_eq(td, timedelta(1, 2, 3)) and not dt_timedelta_eq(td, timedelta(1, 2, 4))
    assert dt_timedelta_eq(td, td)
    assert isinstance(td, timedelta)
    print("ok", d, t, dt, td)

if __name__ == "__main__":
    main()
