"""Run example ``main()`` entry points under pytest."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"


def _example_paths() -> list[Path]:
    paths = sorted(EXAMPLES.glob("py*.py"))
    wrap = EXAMPLES / "wrap_ansi.py"
    if wrap.is_file():
        paths.append(wrap)
    return paths


@pytest.mark.parametrize("path", _example_paths(), ids=lambda p: p.name)
def test_example_main(path: Path) -> None:
    spec = importlib.util.spec_from_file_location(f"_picop_example_{path.stem}", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    main = getattr(module, "main", None)
    if main is None:
        pytest.skip(f"{path.name} has no main()")
    main()
