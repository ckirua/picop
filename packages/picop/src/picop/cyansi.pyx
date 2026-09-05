# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
"""
ANSI SGR escape sequences for terminals.
"""

from .cyansi cimport _RESET, bg8, bold, fg8, fg256, reset, wrap
from .cyunicode cimport uintern

include "cyansi.pxi"

reset()

RESET = _RESET


class FOREGROUND_COLORS_8:
    """Standard 8-color ANSI foreground escape sequences (SGR 30–37)."""


FOREGROUND_COLORS_8.BLACK = uintern(ANSI_FG8_BLACK)
FOREGROUND_COLORS_8.RED = uintern(ANSI_FG8_RED)
FOREGROUND_COLORS_8.GREEN = uintern(ANSI_FG8_GREEN)
FOREGROUND_COLORS_8.YELLOW = uintern(ANSI_FG8_YELLOW)
FOREGROUND_COLORS_8.BLUE = uintern(ANSI_FG8_BLUE)
FOREGROUND_COLORS_8.MAGENTA = uintern(ANSI_FG8_MAGENTA)
FOREGROUND_COLORS_8.CYAN = uintern(ANSI_FG8_CYAN)
FOREGROUND_COLORS_8.WHITE = uintern(ANSI_FG8_WHITE)


class BACKGROUND_COLORS_8:
    """Standard 8-color ANSI background escape sequences (SGR 40–47)."""


BACKGROUND_COLORS_8.BLACK = uintern(ANSI_BG8_BLACK)
BACKGROUND_COLORS_8.RED = uintern(ANSI_BG8_RED)
BACKGROUND_COLORS_8.GREEN = uintern(ANSI_BG8_GREEN)
BACKGROUND_COLORS_8.YELLOW = uintern(ANSI_BG8_YELLOW)
BACKGROUND_COLORS_8.BLUE = uintern(ANSI_BG8_BLUE)
BACKGROUND_COLORS_8.MAGENTA = uintern(ANSI_BG8_MAGENTA)
BACKGROUND_COLORS_8.CYAN = uintern(ANSI_BG8_CYAN)
BACKGROUND_COLORS_8.WHITE = uintern(ANSI_BG8_WHITE)


class FOREGROUND_COLORS_256:
    """Selected 256-color ANSI foreground sequences (SGR 38;5;n)."""


FOREGROUND_COLORS_256.GREEN_JUNGLE = uintern(ANSI_FG256_GREEN_JUNGLE)
FOREGROUND_COLORS_256.RED = uintern(ANSI_FG256_RED)
FOREGROUND_COLORS_256.YELLOW = uintern(ANSI_FG256_YELLOW)
FOREGROUND_COLORS_256.ORANGE = uintern(ANSI_FG256_ORANGE)
FOREGROUND_COLORS_256.BLUE_ULTRAMARINE = uintern(ANSI_FG256_BLUE_ULTRAMARINE)
FOREGROUND_COLORS_256.BLUE_DEFAULT = uintern(ANSI_FG256_BLUE_DEFAULT)
FOREGROUND_COLORS_256.GREY = uintern(ANSI_FG256_GREY)


class BOLD_COLORS_256:
    """Bold foreground color variants."""


BOLD_COLORS_256.RED = uintern(ANSI_BOLD256_RED)


cdef str strip_ansi(str s):
    cdef Py_ssize_t n = len(s)
    if n == 0:
        return s

    cdef Py_ssize_t i = 0
    cdef Py_ssize_t j
    cdef Py_ssize_t start = 0
    cdef list pieces = []
    cdef int c
    cdef int c2
    cdef bint found = False

    while i < n:
        c = ord(s[i])
        if c == 27 and i + 1 < n:
            c2 = ord(s[i + 1])
            if c2 == 91:  # '['
                found = True
                if i > start:
                    pieces.append(s[start:i])
                j = i + 2
                while j < n:
                    c = ord(s[j])
                    if 0x40 <= c <= 0x7E:
                        j += 1
                        break
                    j += 1
                i = j
                start = i
                continue
        i += 1

    if not found:
        return s
    if start < n:
        pieces.append(s[start:])
    if not pieces:
        return ""
    if len(pieces) == 1:
        return <str>pieces[0]
    return "".join(pieces)


__all__: tuple[str, ...] = (
    "BACKGROUND_COLORS_8",
    "BOLD_COLORS_256",
    "FOREGROUND_COLORS_256",
    "FOREGROUND_COLORS_8",
    "RESET",
    "ansi_bg8",
    "ansi_bold",
    "ansi_fg8",
    "ansi_fg256",
    "ansi_reset",
    "ansi_strip",
    "ansi_wrap",
)
