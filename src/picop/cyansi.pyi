"""ANSI/SGR escape helpers built on unicode intern (not a CPython C-API wrap).

Prefer :mod:`picop.cyansi` (or starters in :mod:`picop.hot`) for terminal color
wraps and CSI stripping. See :doc:`/user_guide/quickstart` for import patterns.
"""

RESET: str

class FOREGROUND_COLORS_8:
    """Standard 8-color ANSI foreground escape sequences (SGR 30–37)."""

    BLACK: str
    RED: str
    GREEN: str
    YELLOW: str
    BLUE: str
    MAGENTA: str
    CYAN: str
    WHITE: str

class BACKGROUND_COLORS_8:
    """Standard 8-color ANSI background escape sequences (SGR 40–47)."""

    BLACK: str
    RED: str
    GREEN: str
    YELLOW: str
    BLUE: str
    MAGENTA: str
    CYAN: str
    WHITE: str

class FOREGROUND_COLORS_256:
    """Selected 256-color ANSI foreground sequences (SGR 38;5;n)."""

    GREEN_JUNGLE: str
    RED: str
    YELLOW: str
    ORANGE: str
    BLUE_ULTRAMARINE: str
    BLUE_DEFAULT: str
    GREY: str

class BOLD_COLORS_256:
    """Bold foreground color variants."""

    RED: str

# Preferred public names (0.3 hard trim)

def ansi_bg8(code: int) -> str:
    """Return an 8-color background SGR for ``code``.

    Notes
    -----
    Table hit for codes ``40``–``47``.
    """
    ...

def ansi_bold(on: bool = True) -> str:
    """Return bold-on SGR, or reset when ``on`` is false."""
    ...

def ansi_fg256(n: int) -> str:
    """Return a 256-color foreground SGR for palette index ``n``.

    Notes
    -----
    Table lookup for indices ``0``–``255``.
    """
    ...

def ansi_fg8(code: int) -> str:
    """Return an 8-color foreground SGR for ``code``.

    Notes
    -----
    Table hit for codes ``30``–``37``.
    """
    ...

def ansi_reset() -> str:
    """Return the interned ANSI reset SGR sequence."""
    ...

def ansi_strip(s: str) -> str:
    """Remove CSI sequences from ``s`` in a single pass.

    Notes
    -----
    Returns ``s`` unchanged when no CSI sequences are present.
    """
    ...

def ansi_wrap(prefix: str, text: str, suffix: str | None = ...) -> str:
    """Return ``prefix + text + suffix``.

    Notes
    -----
    Default ``suffix`` is the ANSI reset sequence.
    """
    ...
