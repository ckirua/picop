"""Deprecated :mod:`cypy.uuid` alias for :mod:`picop.uuid` (removal in 3.0)."""

from __future__ import annotations

import sys
import warnings

warnings.warn(
    "cypy.uuid is deprecated; use picop.uuid (removal planned in picop 3.0).",
    DeprecationWarning,
    stacklevel=2,
)

import picop.uuid as _uuid
from picop.uuid import *  # noqa: F403

sys.modules.setdefault("cypy.uuid", _uuid)
