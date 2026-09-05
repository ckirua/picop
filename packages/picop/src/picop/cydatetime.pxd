# cydatetime.pxd
# datetime.h helpers. Public docs in ``cydatetime.pyi``.
# Call ``import_datetime()`` once (done in ``cydatetime.pyx``) before use.

from cpython.datetime cimport (
    PyDate_Check,
    PyDate_CheckExact,
    PyDateTime_Check,
    PyDateTime_CheckExact,
    PyDelta_Check,
    PyDelta_CheckExact,
    PyTime_Check,
    PyTime_CheckExact,
    date_day,
    date_month,
    date_new,
    date_year,
    datetime_day,
    datetime_hour,
    datetime_microsecond,
    datetime_minute,
    datetime_month,
    datetime_new,
    datetime_second,
    datetime_tzinfo,
    datetime_year,
    import_datetime,
    time_hour,
    time_microsecond,
    time_minute,
    time_new,
    time_second,
    time_tzinfo,
    timedelta_days,
    timedelta_microseconds,
    timedelta_new,
    timedelta_seconds,
)
from cpython.object cimport PyObject_RichCompareBool, Py_EQ


cpdef inline bint dt_date_check(object o) noexcept:
    return PyDate_Check(o)


cpdef inline bint dt_date_check_exact(object o) noexcept:
    return PyDate_CheckExact(o)


cdef inline bint dteq_date(object a, object b):
    # Identity short-circuit; exact ``date`` pairs compare y/m/d; else richcompare
    # (subtypes / ``date`` vs ``datetime`` — Python ``==`` parity). Soft ``dteq_date``.
    if a is b:
        return True
    if PyDate_CheckExact(a) and PyDate_CheckExact(b):
        return (
            date_year(a) == date_year(b)
            and date_month(a) == date_month(b)
            and date_day(a) == date_day(b)
        )
    return <bint>PyObject_RichCompareBool(a, b, Py_EQ)


cpdef inline bint dt_date_eq(object a, object b):
    return dteq_date(a, b)


cpdef inline bint dt_datetime_check(object o) noexcept:
    return PyDateTime_Check(o)


cpdef inline bint dt_datetime_check_exact(object o) noexcept:
    return PyDateTime_CheckExact(o)


cdef inline bint dteq_dt(object a, object b):
    # Identity short-circuit; exact naive ``datetime`` pairs compare
    # y/m/d/h/m/s/us; else richcompare (subtypes / aware/naive / offset /
    # date↔datetime — Python ``==`` parity). Soft ``dteq_dt``. Fold ignored.
    if a is b:
        return True
    if PyDateTime_CheckExact(a) and PyDateTime_CheckExact(b):
        if datetime_tzinfo(a) is None and datetime_tzinfo(b) is None:
            return (
                datetime_year(a) == datetime_year(b)
                and datetime_month(a) == datetime_month(b)
                and datetime_day(a) == datetime_day(b)
                and datetime_hour(a) == datetime_hour(b)
                and datetime_minute(a) == datetime_minute(b)
                and datetime_second(a) == datetime_second(b)
                and datetime_microsecond(a) == datetime_microsecond(b)
            )
    return <bint>PyObject_RichCompareBool(a, b, Py_EQ)


cpdef inline bint dt_datetime_eq(object a, object b):
    return dteq_dt(a, b)


cpdef inline bint dt_time_check(object o) noexcept:
    return PyTime_Check(o)


cpdef inline bint dt_time_check_exact(object o) noexcept:
    return PyTime_CheckExact(o)


cdef inline bint dteq_time(object a, object b):
    # Identity short-circuit; exact naive ``time`` pairs compare h/m/s/us;
    # else richcompare (subtypes / aware/naive / offset — Python ``==`` parity).
    # Soft ``dteq_time``. Fold is ignored (matches ``time.__eq__``).
    if a is b:
        return True
    if PyTime_CheckExact(a) and PyTime_CheckExact(b):
        if time_tzinfo(a) is None and time_tzinfo(b) is None:
            return (
                time_hour(a) == time_hour(b)
                and time_minute(a) == time_minute(b)
                and time_second(a) == time_second(b)
                and time_microsecond(a) == time_microsecond(b)
            )
    return <bint>PyObject_RichCompareBool(a, b, Py_EQ)


cpdef inline bint dt_time_eq(object a, object b):
    return dteq_time(a, b)


cdef inline bint dteq_delta(object a, object b):
    # Identity short-circuit; exact ``timedelta`` pairs compare
    # days/seconds/microseconds; else richcompare (subtypes — Python ``==``
    # parity). Soft ``dteq_delta``.
    if a is b:
        return True
    if PyDelta_CheckExact(a) and PyDelta_CheckExact(b):
        return (
            timedelta_days(a) == timedelta_days(b)
            and timedelta_seconds(a) == timedelta_seconds(b)
            and timedelta_microseconds(a) == timedelta_microseconds(b)
        )
    return <bint>PyObject_RichCompareBool(a, b, Py_EQ)


cpdef inline bint dt_timedelta_eq(object a, object b):
    return dteq_delta(a, b)


cdef inline bint dt_delta_check(object o) noexcept:
    return PyDelta_Check(o)


cdef inline bint dt_delta_check_exact(object o) noexcept:
    return PyDelta_CheckExact(o)


cpdef inline object dt_date_new(int year, int month, int day):
    return date_new(year, month, day)


cpdef inline object dt_time_new(int hour, int minute, int second, int microsecond, object tz=None, int fold=0):
    return time_new(hour, minute, second, microsecond, tz, fold)


cpdef inline object dt_datetime_new(
    int year, int month, int day, int hour, int minute, int second, int microsecond, object tz=None, int fold=0
):
    return datetime_new(year, month, day, hour, minute, second, microsecond, tz, fold)


cpdef inline object dt_timedelta_new(int days, int seconds, int useconds):
    return timedelta_new(days, seconds, useconds)


cpdef inline int dt_date_year(object o) noexcept:
    return date_year(o)


cpdef inline int dt_date_month(object o) noexcept:
    return date_month(o)


cpdef inline int dt_date_day(object o) noexcept:
    return date_day(o)


cpdef inline int dt_datetime_year(object o) noexcept:
    return datetime_year(o)


cpdef inline int dt_datetime_month(object o) noexcept:
    return datetime_month(o)


cpdef inline int dt_datetime_day(object o) noexcept:
    return datetime_day(o)


cpdef inline int dt_datetime_hour(object o) noexcept:
    return datetime_hour(o)


cpdef inline int dt_datetime_minute(object o) noexcept:
    return datetime_minute(o)


cpdef inline int dt_datetime_second(object o) noexcept:
    return datetime_second(o)


cpdef inline int dt_datetime_microsecond(object o) noexcept:
    return datetime_microsecond(o)


cpdef inline int dt_time_hour(object o) noexcept:
    return time_hour(o)


cpdef inline int dt_time_minute(object o) noexcept:
    return time_minute(o)


cpdef inline int dt_time_second(object o) noexcept:
    return time_second(o)


cpdef inline int dt_time_microsecond(object o) noexcept:
    return time_microsecond(o)


cdef inline int dt_delta_days(object o) noexcept:
    return timedelta_days(o)


cdef inline int dt_delta_seconds(object o) noexcept:
    return timedelta_seconds(o)


cdef inline int dt_delta_microseconds(object o) noexcept:
    return timedelta_microseconds(o)

# N6 spelling: preferred dt_timedelta_* (0.3: dt_delta_* cdef-only)
cpdef inline bint dt_timedelta_check(object o) noexcept:
    return dt_delta_check(o)

cpdef inline bint dt_timedelta_check_exact(object o) noexcept:
    return dt_delta_check_exact(o)

cpdef inline int dt_timedelta_days(object o) noexcept:
    return dt_delta_days(o)

cpdef inline int dt_timedelta_seconds(object o) noexcept:
    return dt_delta_seconds(o)

cpdef inline int dt_timedelta_microseconds(object o) noexcept:
    return dt_delta_microseconds(o)

