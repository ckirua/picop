#!/usr/bin/env python3
"""Generate wave-hot Tier B harnesses (idempotent)."""
from __future__ import annotations

from pathlib import Path

HERE = Path(__file__).resolve().parent

MODULES: dict[str, dict[str, str]] = {}

MODULES["cybytes"] = {
    "pyx": r'''# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from cypy.cybytes cimport bytes_contains, bytes_eq, bytes_len, bytes_check, bytes_check_exact
include "_sink.pxi"

cpdef bint baseline_bcontains(bytes haystack, bytes needle, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = needle in <bytes>tb_obj(haystack, k)
        tb_sink_bint(r)
    return r

cpdef bint cypy_bcontains(bytes haystack, bytes needle, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = bytes_contains(<bytes>tb_obj(haystack, k), needle)
        tb_sink_bint(r)
    return r

cpdef bint baseline_beq(bytes a, bytes b, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = <bytes>tb_obj(a, k) == b
        tb_sink_bint(r)
    return r

cpdef bint cypy_beq(bytes a, bytes b, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = bytes_eq(<bytes>tb_obj(a, k), b)
        tb_sink_bint(r)
    return r

cpdef Py_ssize_t baseline_blen(bytes b, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef Py_ssize_t r = 0
    for k in range(n):
        r = len(<bytes>tb_obj(b, k))
        tb_sink_ssize(r)
    return r

cpdef Py_ssize_t cypy_blen(bytes b, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef Py_ssize_t r = 0
    for k in range(n):
        r = bytes_len(<bytes>tb_obj(b, k))
        tb_sink_ssize(r)
    return r

cpdef bint baseline_bcheck(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = isinstance(tb_obj(p, k), bytes)
        tb_sink_bint(r)
    return r

cpdef bint cypy_bcheck(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = bytes_check(tb_obj(p, k))
        tb_sink_bint(r)
    return r

cpdef bint baseline_bcheck_exact(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = type(tb_obj(p, k)) is bytes
        tb_sink_bint(r)
    return r

cpdef bint cypy_bcheck_exact(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = bytes_check_exact(tb_obj(p, k))
        tb_sink_bint(r)
    return r
''',
    "body": r'''
HAY = b"abcabc"
NEEDLE = b"ab"

def main() -> None:
    tb = ensure_ext("cybytes")
    session = tier_b_session("cybytes — Tier B (cypy vs typed Cython cdef loop)")
    session.header()
    print(f"inner loop N={N:,}")
    print()
    session.section("bytes_contains vs `in`  [primary]")
    session.compare("bytes_contains", tb.cypy_bcontains, tb.baseline_bcontains, HAY, NEEDLE, N, param="small multi hit")
    session.section("bytes_eq vs `==`")
    session.compare("bytes_eq", tb.cypy_beq, tb.baseline_beq, HAY, HAY, N, param="equal")
    session.section("bytes_len / bytes_check")
    session.compare("bytes_len", tb.cypy_blen, tb.baseline_blen, HAY, N, param="small")
    session.compare("bytes_check", tb.cypy_bcheck, tb.baseline_bcheck, HAY, N, param="bytes")
    session.compare("bytes_check_exact", tb.cypy_bcheck_exact, tb.baseline_bcheck_exact, HAY, N, param="bytes")
    session.summary()
    print("Markdown (paste under ### Tier B):")
    print(markdown_table(session._rows))
    print()
''',
}

MODULES["cydict"] = {
    "pyx": r'''# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from cypy.cydict cimport dict_get, dict_contains, dict_len, dict_check
include "_sink.pxi"

cpdef object baseline_dget(dict d, str key, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r
    for k in range(n):
        r = (<dict>tb_obj(d, k)).get(key)
        tb_sink_obj(r)
    return r

cpdef object cypy_dget(dict d, str key, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r
    for k in range(n):
        r = dict_get(<dict>tb_obj(d, k), key)
        tb_sink_obj(r)
    return r

cpdef bint baseline_dcontains(dict d, str key, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = key in <dict>tb_obj(d, k)
        tb_sink_bint(r)
    return r

cpdef bint cypy_dcontains(dict d, str key, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = dict_contains(<dict>tb_obj(d, k), key)
        tb_sink_bint(r)
    return r

cpdef Py_ssize_t baseline_dlen(dict d, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef Py_ssize_t r = 0
    for k in range(n):
        r = len(<dict>tb_obj(d, k))
        tb_sink_ssize(r)
    return r

cpdef Py_ssize_t cypy_dlen(dict d, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef Py_ssize_t r = 0
    for k in range(n):
        r = dict_len(<dict>tb_obj(d, k))
        tb_sink_ssize(r)
    return r

cpdef bint baseline_dcheck(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = isinstance(tb_obj(p, k), dict)
        tb_sink_bint(r)
    return r

cpdef bint cypy_dcheck(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = dict_check(tb_obj(p, k))
        tb_sink_bint(r)
    return r
''',
    "body": r'''
PAYLOAD = {"symbol": "BTCUSDT", "price": "1", "qty": "2"}

def main() -> None:
    tb = ensure_ext("cydict")
    session = tier_b_session("cydict — Tier B (cypy vs typed Cython cdef loop)")
    session.header()
    print(f"inner loop N={N:,}")
    print()
    session.section("dict_get vs dict.get  [primary]")
    session.compare("dict_get", tb.cypy_dget, tb.baseline_dget, PAYLOAD, "symbol", N, param="hit symbol")
    session.section("dict_contains / dict_len / dict_check")
    session.compare("dict_contains", tb.cypy_dcontains, tb.baseline_dcontains, PAYLOAD, "symbol", N, param="hit")
    session.compare("dict_len", tb.cypy_dlen, tb.baseline_dlen, PAYLOAD, N, param="n=3")
    session.compare("dict_check", tb.cypy_dcheck, tb.baseline_dcheck, PAYLOAD, N, param="dict")
    session.summary()
    print("Markdown (paste under ### Tier B):")
    print(markdown_table(session._rows))
    print()
''',
}

MODULES["cylist"] = {
    "pyx": r'''# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from cypy.cylist cimport list_get, list_get_checked, list_len, list_check
include "_sink.pxi"

cpdef object baseline_lget(list l, Py_ssize_t i, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r
    for k in range(n):
        r = (<list>tb_obj(l, k))[i]
        tb_sink_obj(r)
    return r

cpdef object cypy_lget(list l, Py_ssize_t i, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r
    for k in range(n):
        r = list_get(<list>tb_obj(l, k), i)
        tb_sink_obj(r)
    return r

cpdef object cypy_lget_checked(list l, Py_ssize_t i, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef object r
    for k in range(n):
        r = list_get_checked(<list>tb_obj(l, k), i)
        tb_sink_obj(r)
    return r

cpdef Py_ssize_t baseline_llen(list l, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef Py_ssize_t r = 0
    for k in range(n):
        r = len(<list>tb_obj(l, k))
        tb_sink_ssize(r)
    return r

cpdef Py_ssize_t cypy_llen(list l, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef Py_ssize_t r = 0
    for k in range(n):
        r = list_len(<list>tb_obj(l, k))
        tb_sink_ssize(r)
    return r

cpdef bint baseline_lcheck(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = isinstance(tb_obj(p, k), list)
        tb_sink_bint(r)
    return r

cpdef bint cypy_lcheck(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = list_check(tb_obj(p, k))
        tb_sink_bint(r)
    return r
''',
    "body": r'''
PAYLOAD = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"]

def main() -> None:
    tb = ensure_ext("cylist")
    session = tier_b_session("cylist — Tier B (cypy vs typed Cython cdef loop)")
    session.header()
    print(f"inner loop N={N:,}")
    print()
    session.section("list_get vs l[i]  [primary]")
    session.compare("list_get", tb.cypy_lget, tb.baseline_lget, PAYLOAD, 0, N, param="index=0")
    session.compare("list_get_checked", tb.cypy_lget_checked, tb.baseline_lget, PAYLOAD, 0, N, param="index=0")
    session.section("list_len / list_check")
    session.compare("list_len", tb.cypy_llen, tb.baseline_llen, PAYLOAD, N, param="n=4")
    session.compare("list_check", tb.cypy_lcheck, tb.baseline_lcheck, PAYLOAD, N, param="list")
    session.summary()
    print("Markdown (paste under ### Tier B):")
    print(markdown_table(session._rows))
    print()
''',
}

MODULES["cyset"] = {
    "pyx": r'''# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from cypy.cyset cimport set_contains, set_len, set_check
include "_sink.pxi"

cpdef bint baseline_scontains(object s, object value, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = value in tb_obj(s, k)
        tb_sink_bint(r)
    return r

cpdef bint cypy_scontains(object s, object value, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = set_contains(tb_obj(s, k), value)
        tb_sink_bint(r)
    return r

cpdef Py_ssize_t baseline_slen(set s, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef Py_ssize_t r = 0
    for k in range(n):
        r = len(<set>tb_obj(s, k))
        tb_sink_ssize(r)
    return r

cpdef Py_ssize_t cypy_slen(set s, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef Py_ssize_t r = 0
    for k in range(n):
        r = set_len(<set>tb_obj(s, k))
        tb_sink_ssize(r)
    return r

cpdef bint baseline_scheck(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = isinstance(tb_obj(p, k), set)
        tb_sink_bint(r)
    return r

cpdef bint cypy_scheck(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = set_check(tb_obj(p, k))
        tb_sink_bint(r)
    return r
''',
    "body": r'''
PAYLOAD = {"BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"}

def main() -> None:
    tb = ensure_ext("cyset")
    session = tier_b_session("cyset — Tier B (cypy vs typed Cython cdef loop)")
    session.header()
    print(f"inner loop N={N:,}")
    print()
    session.section("set_contains vs `in`  [primary]")
    session.compare("set_contains", tb.cypy_scontains, tb.baseline_scontains, PAYLOAD, "BTCUSDT", N, param="hit")
    session.section("set_len / set_check")
    session.compare("set_len", tb.cypy_slen, tb.baseline_slen, PAYLOAD, N, param="n=4")
    session.compare("set_check", tb.cypy_scheck, tb.baseline_scheck, PAYLOAD, N, param="set")
    session.summary()
    print("Markdown (paste under ### Tier B):")
    print(markdown_table(session._rows))
    print()
''',
}

MODULES["cystr"] = {
    "pyx": r'''# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from cypy.cystr cimport str_contains, str_eq, str_len, str_check_exact
include "_sink.pxi"

cpdef bint baseline_contains(str haystack, str needle, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = needle in <str>tb_obj(haystack, k)
        tb_sink_bint(r)
    return r

cpdef bint cypy_contains(str haystack, str needle, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = str_contains(<str>tb_obj(haystack, k), needle)
        tb_sink_bint(r)
    return r

cpdef bint baseline_streq(str a, str b, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = <str>tb_obj(a, k) == b
        tb_sink_bint(r)
    return r

cpdef bint cypy_streq(str a, str b, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = str_eq(<str>tb_obj(a, k), b)
        tb_sink_bint(r)
    return r

cpdef Py_ssize_t baseline_strlen(str s, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef Py_ssize_t r = 0
    for k in range(n):
        r = len(<str>tb_obj(s, k))
        tb_sink_ssize(r)
    return r

cpdef Py_ssize_t cypy_strlen(str s, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef Py_ssize_t r = 0
    for k in range(n):
        r = str_len(<str>tb_obj(s, k))
        tb_sink_ssize(r)
    return r

cpdef bint baseline_is_str(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = type(tb_obj(p, k)) is str
        tb_sink_bint(r)
    return r

cpdef bint cypy_is_str(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = str_check_exact(tb_obj(p, k))
        tb_sink_bint(r)
    return r
''',
    "body": r'''
HAY = "abcabc"
NEEDLE = "ab"

def main() -> None:
    tb = ensure_ext("cystr")
    session = tier_b_session("cystr — Tier B (cypy vs typed Cython cdef loop)")
    session.header()
    print(f"inner loop N={N:,}")
    print()
    session.section("str_contains vs `in`  [primary]")
    session.compare("str_contains", tb.cypy_contains, tb.baseline_contains, HAY, NEEDLE, N, param="short hit")
    session.section("str_eq / str_len / str_check_exact")
    session.compare("str_eq", tb.cypy_streq, tb.baseline_streq, HAY, HAY, N, param="equal")
    session.compare("str_len", tb.cypy_strlen, tb.baseline_strlen, HAY, N, param="short")
    session.compare("str_check_exact", tb.cypy_is_str, tb.baseline_is_str, HAY, N, param="str")
    session.summary()
    print("Markdown (paste under ### Tier B):")
    print(markdown_table(session._rows))
    print()
''',
}

MODULES["cyunicode"] = {
    "pyx": r'''# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from cypy.cyunicode cimport uutf8_bytes, uintern
from cpython.object cimport PyObject
include "_sink.pxi"

cdef extern from "Python.h":
    object PyUnicode_AsUTF8String(object unicode)
    void PyUnicode_InternInPlace(PyObject **)

cpdef bytes baseline_uutf8_bytes(str s, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bytes r
    for k in range(n):
        r = <bytes>PyUnicode_AsUTF8String(<str>tb_obj(s, k))
        tb_sink_obj(r)
    return r

cpdef bytes cypy_uutf8_bytes(str s, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bytes r
    for k in range(n):
        r = uutf8_bytes(<str>tb_obj(s, k))
        tb_sink_obj(r)
    return r

cpdef str baseline_uintern(str s, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef PyObject *p
    cdef str r
    for k in range(n):
        r = <str>tb_obj(s, k)
        p = <PyObject*>r
        PyUnicode_InternInPlace(&p)
        r = <str>p
        tb_sink_obj(r)
    return r

cpdef str cypy_uintern(str s, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef str r
    for k in range(n):
        r = uintern(<str>tb_obj(s, k))
        tb_sink_obj(r)
    return r
''',
    "body": r'''
SHORT = "BTCUSDT"

def main() -> None:
    tb = ensure_ext("cyunicode")
    session = tier_b_session("cyunicode — Tier B (cypy vs typed Cython cdef loop)")
    session.header()
    print(f"inner loop N={N:,}")
    print()
    session.section("uutf8_bytes vs AsUTF8String  [primary]")
    session.compare("uutf8_bytes", tb.cypy_uutf8_bytes, tb.baseline_uutf8_bytes, SHORT, N, param="short")
    session.section("uintern vs InternInPlace")
    session.compare("uintern", tb.cypy_uintern, tb.baseline_uintern, SHORT, N, param="already")
    session.summary()
    print("Markdown (paste under ### Tier B):")
    print(markdown_table(session._rows))
    print()
''',
}

MODULES["cyansi"] = {
    "pyx": r'''# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from cypy.cyansi cimport ansi_fg8, ansi_bg8, ansi_bold
include "_sink.pxi"

cpdef str baseline_fg8(int code, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef str r
    cdef int c
    for k in range(n):
        c = code
        tb_sink_ssize(c ^ (k & 0))
        r = f"\x1b[{c}m"
        tb_sink_obj(r)
    return r

cpdef str cypy_fg8(int code, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef str r
    cdef int c
    for k in range(n):
        c = code
        tb_sink_ssize(c ^ (k & 0))
        r = ansi_fg8(c)
        tb_sink_obj(r)
    return r

cpdef str baseline_bg8(int code, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef str r
    cdef int c
    for k in range(n):
        c = code
        tb_sink_ssize(c ^ (k & 0))
        r = f"\x1b[{c}m"
        tb_sink_obj(r)
    return r

cpdef str cypy_bg8(int code, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef str r
    cdef int c
    for k in range(n):
        c = code
        tb_sink_ssize(c ^ (k & 0))
        r = ansi_bg8(c)
        tb_sink_obj(r)
    return r

cpdef str baseline_bold(bint on, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef str r
    for k in range(n):
        tb_sink_bint(on)
        tb_sink_ssize(k & 0)
        r = "\x1b[1m" if on else "\x1b[0m"
        tb_sink_obj(r)
    return r

cpdef str cypy_bold(bint on, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef str r
    for k in range(n):
        tb_sink_ssize(k & 0)
        r = ansi_bold(on)
        tb_sink_obj(r)
    return r
''',
    "body": r'''
# f-string baseline allocates; keep signal without multi-second runs
N = min(N, 200_000)

def main() -> None:
    tb = ensure_ext("cyansi")
    session = tier_b_session("cyansi — Tier B (cypy vs typed Cython cdef loop)")
    session.header()
    print(f"inner loop N={N:,}")
    print()
    session.section("ansi_fg8 vs f-string  [primary]")
    session.compare("ansi_fg8", tb.cypy_fg8, tb.baseline_fg8, 31, N, param="table hit 31")
    session.compare("ansi_bg8", tb.cypy_bg8, tb.baseline_bg8, 41, N, param="table hit 41")
    session.compare("ansi_bold", tb.cypy_bold, tb.baseline_bold, True, N, param="on")
    session.summary()
    print("Markdown (paste under ### Tier B):")
    print(markdown_table(session._rows))
    print()
''',
}

MODULES["cygc"] = {
    "pyx": r'''# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from cypy.cygc cimport gc_is_enabled
include "_sink.pxi"

cdef extern from "Python.h":
    int PyGC_IsEnabled() except -1

cpdef bint baseline_gc_is_enabled(Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        tb_sink_ssize(k)
        r = PyGC_IsEnabled() != 0
        tb_sink_bint(r)
    return r

cpdef bint cypy_gc_is_enabled(Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        tb_sink_ssize(k)
        r = gc_is_enabled()
        tb_sink_bint(r)
    return r
''',
    "body": r'''
def main() -> None:
    tb = ensure_ext("cygc")
    session = tier_b_session("cygc — Tier B (cypy vs typed Cython cdef loop)")
    session.header()
    print(f"inner loop N={N:,}")
    print()
    session.section("gc_is_enabled vs PyGC_IsEnabled  [primary]")
    session.compare("gc_is_enabled", tb.cypy_gc_is_enabled, tb.baseline_gc_is_enabled, N, param="flag read")
    session.summary()
    print("Markdown (paste under ### Tier B):")
    print(markdown_table(session._rows))
    print()
''',
}

MODULES["cybytearray"] = {
    "pyx": r'''# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from cypy.cybytearray cimport bytearray_len, bytearray_check, bytearray_check_exact
include "_sink.pxi"

cpdef Py_ssize_t baseline_balen(bytearray ba, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef Py_ssize_t r = 0
    for k in range(n):
        r = len(<bytearray>tb_obj(ba, k))
        tb_sink_ssize(r)
    return r

cpdef Py_ssize_t cypy_balen(bytearray ba, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef Py_ssize_t r = 0
    for k in range(n):
        r = bytearray_len(<bytearray>tb_obj(ba, k))
        tb_sink_ssize(r)
    return r

cpdef bint baseline_bacheck(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = isinstance(tb_obj(p, k), bytearray)
        tb_sink_bint(r)
    return r

cpdef bint cypy_bacheck(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = bytearray_check(tb_obj(p, k))
        tb_sink_bint(r)
    return r

cpdef bint baseline_bacheck_exact(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = type(tb_obj(p, k)) is bytearray
        tb_sink_bint(r)
    return r

cpdef bint cypy_bacheck_exact(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = bytearray_check_exact(tb_obj(p, k))
        tb_sink_bint(r)
    return r
''',
    "body": r'''
PAYLOAD = bytearray(b"abcabc")

def main() -> None:
    tb = ensure_ext("cybytearray")
    session = tier_b_session("cybytearray — Tier B (cypy vs typed Cython cdef loop)")
    session.header()
    print(f"inner loop N={N:,}")
    print()
    session.section("bytearray_len vs len  [primary]")
    session.compare("bytearray_len", tb.cypy_balen, tb.baseline_balen, PAYLOAD, N, param="small")
    session.section("bytearray_check / exact")
    session.compare("bytearray_check", tb.cypy_bacheck, tb.baseline_bacheck, PAYLOAD, N, param="bytearray")
    session.compare("bytearray_check_exact", tb.cypy_bacheck_exact, tb.baseline_bacheck_exact, PAYLOAD, N, param="bytearray")
    session.summary()
    print("Markdown (paste under ### Tier B):")
    print(markdown_table(session._rows))
    print()
''',
}

MODULES["cyarray"] = {
    "pyx": r'''# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from cpython.array cimport array
from cypy.cyarray cimport array_len, array_check
include "_sink.pxi"

cpdef Py_ssize_t baseline_aylen(array a, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef Py_ssize_t r = 0
    for k in range(n):
        r = len(<array>tb_obj(a, k))
        tb_sink_ssize(r)
    return r

cpdef Py_ssize_t cypy_aylen(array a, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef Py_ssize_t r = 0
    for k in range(n):
        r = array_len(<array>tb_obj(a, k))
        tb_sink_ssize(r)
    return r

cpdef bint baseline_aycheck(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = isinstance(tb_obj(p, k), array)
        tb_sink_bint(r)
    return r

cpdef bint cypy_aycheck(object p, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    for k in range(n):
        r = array_check(tb_obj(p, k))
        tb_sink_bint(r)
    return r
''',
    "body": r'''
from array import array

PAYLOAD = array("i", range(8))

def main() -> None:
    tb = ensure_ext("cyarray")
    session = tier_b_session("cyarray — Tier B (cypy vs typed Cython cdef loop)")
    session.header()
    print(f"inner loop N={N:,}")
    print()
    session.section("array_len vs len  [primary]")
    session.compare("array_len", tb.cypy_aylen, tb.baseline_aylen, PAYLOAD, N, param="small i")
    session.section("array_check")
    session.compare("array_check", tb.cypy_aycheck, tb.baseline_aycheck, PAYLOAD, N, param="array")
    session.summary()
    print("Markdown (paste under ### Tier B):")
    print(markdown_table(session._rows))
    print()
''',
}

HDR = '''"""Tier B: {name} public helpers vs typed Cython ``cdef`` loops.

Run::

    python -m bench.tier_b.build {name}
    python -m bench.tier_b.{name}
"""

from __future__ import annotations

from bench.tier_b._tb_util import N, ensure_ext, markdown_table, tier_b_session
'''


def main() -> None:
    for name, spec in MODULES.items():
        (HERE / f"{name}_tb.pyx").write_text(spec["pyx"].lstrip() + "\n", encoding="utf-8")
        (HERE / f"{name}.py").write_text(
            HDR.format(name=name)
            + spec["body"].lstrip()
            + "\n\nif __name__ == \"__main__\":\n    main()\n",
            encoding="utf-8",
        )
        print("wrote", name)
    print("done", len(MODULES))


if __name__ == "__main__":
    main()
