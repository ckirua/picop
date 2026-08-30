"""DateTime C-API construction, field getters, and equality helpers.

Prefer :mod:`datetime` from Python unless you need unchecked C-API
constructors or field access on known date/time objects. Unchecked ``*_new``
helpers are trusted-caller — see :doc:`/user_guide/safety`.
"""

def dt_date_check(o: object) -> bool:
    """Return True if ``o`` is a ``date`` or subtype (``PyDate_Check``)."""
    ...

def dt_date_check_exact(o: object) -> bool:
    """Return True if ``type(o) is date`` (``PyDate_CheckExact``)."""
    ...

def dt_date_eq(a: object, b: object) -> bool:
    """Return True if ``a == b`` for dates (exact y/m/d; else richcompare)."""
    ...

def dt_datetime_check(o: object) -> bool:
    """Return True if ``o`` is a ``datetime`` or subtype (``PyDateTime_Check``)."""
    ...

def dt_datetime_check_exact(o: object) -> bool:
    """Return True if ``type(o) is datetime`` (``PyDateTime_CheckExact``)."""
    ...

def dt_datetime_eq(a: object, b: object) -> bool:
    """Return True if ``a == b`` for datetimes (exact naive fields; else richcompare)."""
    ...

def dt_time_check(o: object) -> bool:
    """Return True if ``o`` is a ``time`` or subtype (``PyTime_Check``)."""
    ...

def dt_time_check_exact(o: object) -> bool:
    """Return True if ``type(o) is time`` (``PyTime_CheckExact``)."""
    ...

def dt_time_eq(a: object, b: object) -> bool:
    """Return True if ``a == b`` for times (exact naive h/m/s/us; else richcompare)."""
    ...

def dt_timedelta_eq(a: object, b: object) -> bool:
    """Return True if ``a == b`` for timedeltas (exact days/s/us; else richcompare)."""
    ...

def dt_date_new(year: int, month: int, day: int) -> object:
    """Return a ``date`` via DateTime C-API.

    Notes
    -----
    Ranges are unchecked — trusted-caller. See :doc:`/user_guide/safety`.
    """
    ...

def dt_time_new(hour: int, minute: int, second: int, microsecond: int, tz: object = None, fold: int = 0) -> object:
    """Return a ``time`` via DateTime C-API.

    Notes
    -----
    Ranges are unchecked — trusted-caller. See :doc:`/user_guide/safety`.
    """
    ...

def dt_datetime_new(year: int, month: int, day: int, hour: int, minute: int, second: int, microsecond: int, tz: object = None, fold: int = 0) -> object:
    """Return a ``datetime`` via DateTime C-API.

    Notes
    -----
    Ranges are unchecked — trusted-caller. See :doc:`/user_guide/safety`.
    """
    ...

def dt_timedelta_new(days: int, seconds: int, useconds: int) -> object:
    """Return a ``timedelta`` via DateTime C-API."""
    ...

def dt_date_year(o: object) -> int:
    """Return the year field of date ``o``."""
    ...

def dt_date_month(o: object) -> int:
    """Return the month field of date ``o``."""
    ...

def dt_date_day(o: object) -> int:
    """Return the day field of date ``o``."""
    ...

def dt_datetime_year(o: object) -> int:
    """Return the year field of datetime ``o``."""
    ...

def dt_datetime_month(o: object) -> int:
    """Return the month field of datetime ``o``."""
    ...

def dt_datetime_day(o: object) -> int:
    """Return the day field of datetime ``o``."""
    ...

def dt_datetime_hour(o: object) -> int:
    """Return the hour field of datetime ``o``."""
    ...

def dt_datetime_minute(o: object) -> int:
    """Return the minute field of datetime ``o``."""
    ...

def dt_datetime_second(o: object) -> int:
    """Return the second field of datetime ``o``."""
    ...

def dt_datetime_microsecond(o: object) -> int:
    """Return the microsecond field of datetime ``o``."""
    ...

def dt_time_hour(o: object) -> int:
    """Return the hour field of time ``o``."""
    ...

def dt_time_minute(o: object) -> int:
    """Return the minute field of time ``o``."""
    ...

def dt_time_second(o: object) -> int:
    """Return the second field of time ``o``."""
    ...

def dt_time_microsecond(o: object) -> int:
    """Return the microsecond field of time ``o``."""
    ...

def dt_timedelta_check(o: object) -> bool:
    """Return True if ``o`` is a ``timedelta`` or subtype.

    Notes
    -----
    Alias of ``dt_delta_check`` (preferred ``timedelta`` spelling).
    """
    ...

def dt_timedelta_check_exact(o: object) -> bool:
    """Return True if ``type(o) is timedelta``.

    Notes
    -----
    Alias of ``dt_delta_check_exact`` (preferred ``timedelta`` spelling).
    """
    ...

def dt_timedelta_days(o: object) -> int:
    """Return the days component of timedelta ``o``.

    Notes
    -----
    Alias of ``dt_delta_days`` (preferred ``timedelta`` spelling).
    """
    ...

def dt_timedelta_seconds(o: object) -> int:
    """Return the seconds component of timedelta ``o``.

    Notes
    -----
    Alias of ``dt_delta_seconds`` (preferred ``timedelta`` spelling).
    """
    ...

def dt_timedelta_microseconds(o: object) -> int:
    """Return the microseconds component of timedelta ``o``.

    Notes
    -----
    Alias of ``dt_delta_microseconds`` (preferred ``timedelta`` spelling).
    """
    ...
