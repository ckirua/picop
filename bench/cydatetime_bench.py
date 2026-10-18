"""Tier A benches for cydatetime."""
from __future__ import annotations
import sys
from datetime import date, datetime, time, timedelta
from pathlib import Path
_BENCH_ROOT = Path(__file__).resolve().parent
if str(_BENCH_ROOT) not in sys.path: sys.path.insert(0, str(_BENCH_ROOT))
from cypy import (
    dt_date_check, dt_datetime_check, dt_date_year, dt_date_new, dt_timedelta_check, dt_timedelta_new,
)
from _bench_util import BenchSession

def main():
    session = BenchSession("cydatetime — tier A")
    session.header()
    d = date(2024, 7, 21)
    dt = datetime(2024, 7, 21, 12, 0, 0)
    session.section("checks / getters")
    session.compare("dt_date_check", dt_date_check, lambda o: isinstance(o, date), d, param="date")
    session.compare("dt_date_check", dt_date_check, lambda o: isinstance(o, date), 1, param="int")
    session.compare("dt_datetime_check", dt_datetime_check, lambda o: isinstance(o, datetime), dt, param="datetime")
    session.compare("dt_date_year", dt_date_year, lambda o: o.year, d, param="year")
    session.compare("dt_date_new", dt_date_new, date, 2024, 7, 21, param="2024-7-21")
    session.compare("dt_timedelta_check", dt_timedelta_check, lambda o: isinstance(o, timedelta), timedelta(1), param="delta")
    session.compare("dt_timedelta_new", dt_timedelta_new, timedelta, 1, 2, 3, param="1d")
    session.summary()
if __name__ == '__main__':
    main()
