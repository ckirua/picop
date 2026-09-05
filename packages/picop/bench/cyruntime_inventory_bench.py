"""Tier A inventory: datetime / context / codecs / conv / remaining runtime.

Helpers that cannot be fairly looped (registry mutation, GC global, file I/O,
reload, Context enter/exit) are documented as ``n/a`` in ``docs/OPS_INVENTORY.md``.

Run: CPY_BENCH_RUNS=11 python bench/cyruntime_inventory_bench.py
"""

from __future__ import annotations

import codecs
import io
import sys
from contextvars import Context, ContextVar, copy_context
from datetime import date, datetime, time, timedelta
from pathlib import Path

_BENCH_ROOT = Path(__file__).resolve().parent
if str(_BENCH_ROOT) not in sys.path:
    sys.path.insert(0, str(_BENCH_ROOT))

from cypy import (
    codec_backslashreplace_errors,
    codec_decoder,
    codec_encoder,
    codec_ignore_errors,
    codec_incremental_decoder,
    codec_incremental_encoder,
    codec_lookup_error,
    codec_namereplace_errors,
    codec_replace_errors,
    codec_stream_reader,
    codec_stream_writer,
    codec_strict_errors,
    codec_xmlcharrefreplace_errors,
    conv_strnicmp,
    ctx_copy,
    ctx_new,
    ctxtoken_check_exact,
    ctxvar_reset,
    ctxvar_set,
    dt_date_check_exact,
    dt_date_day,
    dt_date_month,
    dt_datetime_check_exact,
    dt_datetime_day,
    dt_datetime_hour,
    dt_datetime_microsecond,
    dt_datetime_minute,
    dt_datetime_month,
    dt_datetime_new,
    dt_datetime_second,
    dt_datetime_year,
    dt_time_check,
    dt_time_check_exact,
    dt_time_hour,
    dt_time_microsecond,
    dt_time_minute,
    dt_time_new,
    dt_time_second,
    dt_timedelta_check_exact,
    dt_timedelta_days,
    dt_timedelta_microseconds,
    dt_timedelta_seconds,
)

from _bench_util import BenchSession


def main() -> None:
    session = BenchSession("cyruntime — datetime / ctx / codecs / conv (tier A)")
    session.header()

    d = date(2024, 7, 21)
    dt = datetime(2024, 7, 21, 12, 30, 45, 123456)
    t = time(12, 30, 45, 123456)
    td = timedelta(days=1, seconds=2, microseconds=3)

    session.section("datetime fields / checks / new")
    session.compare(
        "dt_date_check_exact",
        dt_date_check_exact,
        lambda o: type(o) is date,
        d,
        param="date",
    )
    session.compare("dt_date_month", dt_date_month, lambda o: o.month, d, param="month")
    session.compare("dt_date_day", dt_date_day, lambda o: o.day, d, param="day")
    session.compare(
        "dt_datetime_check_exact",
        dt_datetime_check_exact,
        lambda o: type(o) is datetime,
        dt,
        param="dt",
    )
    session.compare("dt_datetime_year", dt_datetime_year, lambda o: o.year, dt, param="year")
    session.compare("dt_datetime_month", dt_datetime_month, lambda o: o.month, dt, param="month")
    session.compare("dt_datetime_day", dt_datetime_day, lambda o: o.day, dt, param="day")
    session.compare("dt_datetime_hour", dt_datetime_hour, lambda o: o.hour, dt, param="hour")
    session.compare(
        "dt_datetime_minute", dt_datetime_minute, lambda o: o.minute, dt, param="minute"
    )
    session.compare(
        "dt_datetime_second", dt_datetime_second, lambda o: o.second, dt, param="second"
    )
    session.compare(
        "dt_datetime_microsecond",
        dt_datetime_microsecond,
        lambda o: o.microsecond,
        dt,
        param="us",
    )
    session.compare(
        "dt_datetime_new",
        dt_datetime_new,
        datetime,
        2024,
        7,
        21,
        12,
        0,
        0,
        0,
        param="new",
    )
    session.compare("dt_time_check", dt_time_check, lambda o: isinstance(o, time), t, param="time")
    session.compare(
        "dt_time_check_exact", dt_time_check_exact, lambda o: type(o) is time, t, param="exact"
    )
    session.compare("dt_time_hour", dt_time_hour, lambda o: o.hour, t, param="hour")
    session.compare("dt_time_minute", dt_time_minute, lambda o: o.minute, t, param="minute")
    session.compare("dt_time_second", dt_time_second, lambda o: o.second, t, param="second")
    session.compare(
        "dt_time_microsecond", dt_time_microsecond, lambda o: o.microsecond, t, param="us"
    )
    session.compare(
        "dt_time_new", dt_time_new, time, 12, 0, 0, 0, param="new"
    )
    session.compare(
        "dt_timedelta_check_exact",
        dt_timedelta_check_exact,
        lambda o: type(o) is timedelta,
        td,
        param="exact",
    )
    session.compare("dt_timedelta_days", dt_timedelta_days, lambda o: o.days, td, param="days")
    session.compare(
        "dt_timedelta_seconds", dt_timedelta_seconds, lambda o: o.seconds, td, param="sec"
    )
    session.compare(
        "dt_timedelta_microseconds",
        dt_timedelta_microseconds,
        lambda o: o.microseconds,
        td,
        param="us",
    )

    session.section("contextvars")
    session.compare("ctx_new", ctx_new, Context, param="new")
    _ctx = Context()
    session.compare("ctx_copy", ctx_copy, lambda c: c.copy(), _ctx, param="copy")
    var = ContextVar("cypy_rt_var", default=0)
    tok = var.set(1)
    session.compare(
        "ctxtoken_check_exact",
        ctxtoken_check_exact,
        lambda o: type(o).__name__ == "Token",
        tok,
        param="token",
    )

    def _cy_ctxvar_set() -> object:
        v = ContextVar("cypy_rt_set", default=0)
        return ctxvar_set(v, 5)

    def _py_ctxvar_set() -> object:
        v = ContextVar("cypy_rt_set", default=0)
        return v.set(5)

    session.compare("ctxvar_set", _cy_ctxvar_set, _py_ctxvar_set, param="set")

    def _cy_ctxvar_reset() -> None:
        v = ContextVar("cypy_rt_reset", default=0)
        token = v.set(1)
        ctxvar_reset(v, token)

    def _py_ctxvar_reset() -> None:
        v = ContextVar("cypy_rt_reset", default=0)
        token = v.set(1)
        v.reset(token)

    session.compare("ctxvar_reset", _cy_ctxvar_reset, _py_ctxvar_reset, param="set+reset")

    session.section("codecs / conv")

    def _enc(name: bytes) -> object:
        return codecs.getencoder(name.decode())

    def _dec(name: bytes) -> object:
        return codecs.getdecoder(name.decode())

    def _inc_enc(name: bytes) -> object:
        return codecs.getincrementalencoder(name.decode())()

    def _inc_dec(name: bytes) -> object:
        return codecs.getincrementaldecoder(name.decode())()

    def _reader(name: bytes, stream: object) -> object:
        return codecs.getreader(name.decode())(stream)

    def _writer(name: bytes, stream: object) -> object:
        return codecs.getwriter(name.decode())(stream)

    def _lookup_err(name: bytes) -> object:
        return codecs.lookup_error(name.decode())

    session.compare("codec_encoder", codec_encoder, _enc, b"utf-8", param="utf-8")
    session.compare("codec_decoder", codec_decoder, _dec, b"utf-8", param="utf-8")
    session.compare(
        "codec_incremental_encoder",
        codec_incremental_encoder,
        _inc_enc,
        b"utf-8",
        param="utf-8",
    )
    session.compare(
        "codec_incremental_decoder",
        codec_incremental_decoder,
        _inc_dec,
        b"utf-8",
        param="utf-8",
    )
    bio = io.BytesIO()
    session.compare(
        "codec_stream_reader", codec_stream_reader, _reader, b"utf-8", bio, param="reader"
    )
    session.compare(
        "codec_stream_writer", codec_stream_writer, _writer, b"utf-8", bio, param="writer"
    )
    session.compare(
        "codec_lookup_error", codec_lookup_error, _lookup_err, b"strict", param="strict"
    )
    exc = UnicodeEncodeError("ascii", "€", 0, 1, "ordinal not in range(128)")

    def _wrap_err(fn):  # type: ignore[no-untyped-def]
        def _inner(e: object) -> object:
            try:
                return fn(e)
            except UnicodeError:
                return None

        return _inner

    session.compare(
        "codec_strict_errors",
        _wrap_err(codec_strict_errors),
        _wrap_err(codecs.strict_errors),
        exc,
        param="strict",
    )
    session.compare(
        "codec_ignore_errors", codec_ignore_errors, codecs.ignore_errors, exc, param="ignore"
    )
    session.compare(
        "codec_replace_errors",
        codec_replace_errors,
        codecs.replace_errors,
        exc,
        param="replace",
    )
    session.compare(
        "codec_xmlcharrefreplace_errors",
        codec_xmlcharrefreplace_errors,
        codecs.xmlcharrefreplace_errors,
        exc,
        param="xml",
    )
    session.compare(
        "codec_backslashreplace_errors",
        codec_backslashreplace_errors,
        codecs.backslashreplace_errors,
        exc,
        param="bs",
    )
    session.compare(
        "codec_namereplace_errors",
        codec_namereplace_errors,
        codecs.namereplace_errors,
        exc,
        param="name",
    )
    session.compare(
        "conv_strnicmp",
        conv_strnicmp,
        lambda a, b, n: 0 if a[:n].lower() == b[:n].lower() else 1,
        b"AbC",
        b"aBc",
        3,
        param="icmp",
    )

    session.summary()


if __name__ == "__main__":
    main()
