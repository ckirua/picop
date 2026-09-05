# cyansi.pxd
# Interned ANSI SGR builders. Public docs: ``cyansi.pyi``.
# Tables init once via ``uintern`` (see ``cyunicode``).

from .cyunicode cimport uintern

include "cyansi.pxi"

cdef str _RESET
cdef str _BOLD_ON
cdef object _FG8_TABLE
cdef object _BG8_TABLE
cdef object _FG256_TABLE
cdef bint _tables_initialized = False


cdef inline void _cyansi_init_tables():
    cdef int i
    cdef str seq
    cdef list fg8
    cdef list bg8
    cdef list fg256

    global _tables_initialized, _RESET, _BOLD_ON, _FG8_TABLE, _BG8_TABLE, _FG256_TABLE
    if _tables_initialized:
        return

    _RESET = uintern(ANSI_RESET)
    _BOLD_ON = uintern(ANSI_BOLD_ON)

    fg8 = [
        uintern(ANSI_FG8_BLACK),
        uintern(ANSI_FG8_RED),
        uintern(ANSI_FG8_GREEN),
        uintern(ANSI_FG8_YELLOW),
        uintern(ANSI_FG8_BLUE),
        uintern(ANSI_FG8_MAGENTA),
        uintern(ANSI_FG8_CYAN),
        uintern(ANSI_FG8_WHITE),
    ]
    bg8 = [
        uintern(ANSI_BG8_BLACK),
        uintern(ANSI_BG8_RED),
        uintern(ANSI_BG8_GREEN),
        uintern(ANSI_BG8_YELLOW),
        uintern(ANSI_BG8_BLUE),
        uintern(ANSI_BG8_MAGENTA),
        uintern(ANSI_BG8_CYAN),
        uintern(ANSI_BG8_WHITE),
    ]
    fg256 = []
    for i in range(256):
        seq = f"\x1b[38;5;{i}m"
        fg256.append(uintern(seq))

    _FG8_TABLE = tuple(fg8)
    _BG8_TABLE = tuple(bg8)
    _FG256_TABLE = tuple(fg256)
    _tables_initialized = True


cdef inline str reset():
    _cyansi_init_tables()
    return _RESET


cdef inline str fg8(int code):
    _cyansi_init_tables()
    if 30 <= code <= 37:
        return <str>(<tuple>_FG8_TABLE)[code - 30]
    return f"\x1b[{code}m"


cdef inline str bg8(int code):
    _cyansi_init_tables()
    if 40 <= code <= 47:
        return <str>(<tuple>_BG8_TABLE)[code - 40]
    return f"\x1b[{code}m"


cdef inline str fg256(int n):
    _cyansi_init_tables()
    if 0 <= n <= 255:
        return <str>(<tuple>_FG256_TABLE)[n]
    return f"\x1b[38;5;{n}m"


cdef inline str bold(bint on = True):
    _cyansi_init_tables()
    if on:
        return _BOLD_ON
    return _RESET


cdef inline str wrap(str prefix, str text, str suffix = *):
    _cyansi_init_tables()
    if suffix is None:
        suffix = _RESET
    return prefix + text + suffix


cdef str strip_ansi(str s)

# Wave 4 N1/N5 preferred names (0.3: soft letter/bare are cdef-only)

cpdef inline str ansi_bg8(int code):
    return bg8(code)

cpdef inline str ansi_bold(bint on = True):
    return bold(on)

cpdef inline str ansi_fg256(int n):
    return fg256(n)

cpdef inline str ansi_fg8(int code):
    return fg8(code)

cpdef inline str ansi_reset():
    return reset()

cpdef inline str ansi_strip(str s):
    return strip_ansi(s)

cpdef inline str ansi_wrap(str prefix, str text, str suffix = *):
    return wrap(prefix, text, suffix)

