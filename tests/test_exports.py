"""Export / COMPAT gates as pytest failures."""

from __future__ import annotations

import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECK_EXPORTS = ROOT / "scripts" / "check_exports.py"


def test_check_exports_exits_zero() -> None:
    ns = runpy.run_path(str(CHECK_EXPORTS), run_name="__picop_check_exports__")
    assert ns["main"]() == 0
