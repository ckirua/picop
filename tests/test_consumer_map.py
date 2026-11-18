"""Isolated contract tests for the consumer-map checker."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts" / "check_consumer_map.py"
HEADER = "| Symbol | Kind | Access | Decision | Expression or use | Contract | Python evidence | Cython evidence |"


def _put(root: Path, relative: str, text: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _row(key: str, *, access: str = "both", symbol: str | None = None,
         kind: str = "function", decision: str = "candidate",
         expression: str = "`dict.get(d, k)` for dicts where missing and stored None are equivalent",
         contract: str = "Concrete dict inputs; preserves only the stated miss contract.",
         python: str = "not-measured: no comparison recorded",
         cython: str = "not-applicable: no Cython baseline") -> str:
    symbol = symbol or key.rsplit(".", 1)[-1]
    return (f"| <a id=\"{symbol.replace('.', '-')}\"></a>`{key}` | {kind} | {access} | {decision} "
            f"| {expression} | {contract} | {python} | {cython} |")
def _fixture(root: Path, *, row: str | None = None) -> None:
    """Build a tiny checkout-shaped source tree; no repository sources are copied."""
    _put(root, "scripts/consumer_map_sources.py",
         (ROOT / "scripts/consumer_map_sources.py").read_text(encoding="utf-8"))
    _put(root, "src/picop/__init__.py",
         "from .cydict import dict_get\nfrom .cybytes import BytesWriter\n")
    _put(root, "src/picop/__init__.pxd",
         "from .cydict cimport dict_get as dget\n"
         "from .cybytes cimport (BytesWriter, bytes_len as blen, FIXTURE_CONSTANT)\n")
    _put(root, "src/picop/cybytes.pxd",
         "ctypedef enum:\n    FIXTURE_CONSTANT\n"
         "cdef class BytesWriter:\n"
         "    cpdef void write(self, object data)\n"
         "    cpdef void write_char(self, int ch)\n"
         "    cpdef Py_ssize_t size(self)\n"
         "    cpdef bytes finish(self)\n"
         "    cpdef void discard(self)\n"
         "    cdef char *data(self) noexcept\n"
         "    cdef char *grow(self, Py_ssize_t extra) except NULL\n"
         "cpdef Py_ssize_t bytes_len(object value)\n"
         "cpdef int direct_example()\n")
    _put(root, "src/picop/cyunicode.pxd", "")
    _put(root, "src/picop/cyunicode.pyi", "")
    _put(root, "src/picop/cydict.pyi", "def dict_get(d: dict, key: object, /) -> object: ...\n")
    _put(root, "src/picop/cybytes.pyi",
         "class BytesWriter:\n"
         "    def __init__(self, max_size: int = 0) -> None: ...\n"
         "    def write(self, data: bytes) -> None: ...\n"
         "    def write_char(self, ch: int) -> None: ...\n"
         "    def size(self) -> int: ...\n"
         "    def finish(self) -> bytes: ...\n"
         "    def discard(self) -> None: ...\n"
         "def bytes_len(value: bytes) -> int: ...\n")
    _put(root, "src/picop/uuid/__init__.py", "from ._uuid import UUID, uuid4, uuid4_bytes\n")
    _put(root, "src/picop/uuid/_uuid.pyi",
         "class UUID:\n    def bytes(self) -> bytes: ...\n"
         "def uuid4(): ...\ndef uuid4_bytes(): ...\n")
    _put(root, "examples/cimport_ext/demo.pyx",
         "from picop.cydict cimport dict_get as lookup\n"
         "from picop.cybytes cimport (BytesWriter as Writer, bytes_len, direct_example)\n")
    table = row if row is not None else _row("picop.cydict.dict_get")
    writer_methods = (
        ("__init__", "specialized", "Construct a `BytesWriter`", "max_size is a capacity hint."),
        ("write", "specialized", "Stream each bytes part into the writer", "Accepts bytes or bytearray; only while open."),
        ("write_char", "specialized", "Append one byte to the writer", "Integer must be in byte range."),
        ("size", "specialized", "Read the number of bytes written", "Writer must be open."),
        ("finish", "specialized", "Finish and obtain the bytes result", "Closes writer; subsequent operations raise RuntimeError."),
        ("discard", "specialized", "Close without producing bytes", "Closes writer; subsequent operations raise RuntimeError."),
    )
    _put(root, ".cursor/skills/use-cypy/maps/cydict.md",
         "# cydict\n\n" + HEADER + "\n|---|---|---|---|---|---|---|---|\n" + table + "\n")
    _put(root, ".cursor/skills/use-cypy/maps/cybytes.md",
         "# cybytes\n\n" + HEADER + "\n|---|---|---|---|---|---|---|---|\n"
         + _row("picop.cybytes.BytesWriter", kind="class", decision="companion",
                expression="Construct or use a typed byte writer",
                contract="Writer lifecycle is specialized; see each member row.",
                symbol="BytesWriter")
         + "\n" + _row("picop.cybytes.bytes_len", access="cimport",
                       expression="`len(value)` for bytes", contract="Exact bytes input.")
         + "\n" + _row("picop.cybytes.FIXTURE_CONSTANT", access="cimport",
                       kind="constant", decision="companion",
                       expression="No direct replacement: Cython constant for the API declaration.",
                       contract="Compile-time fixture constant; not a callable optimization.")
         + "\n" + _row("picop.cybytes.direct_example", access="cimport",
                       expression="No direct replacement: direct-only example Cython API.",
                       contract="Documented direct `cimport`; unavailable as a Python export.")
         + "".join(
             "\n" + _row(f"picop.cybytes.BytesWriter.{member}", kind="method",
                         decision=decision, expression=expression, contract=contract,
                         symbol=f"BytesWriter-{member}")
             for member, decision, expression, contract in writer_methods
         )
         + "\n" + _row("picop.cybytes.BytesWriter.data", access="cimport",
                       kind="method", decision="specialized",
                       expression="Use the raw writer buffer in a Cython direct-fill path.",
                       contract="Returned pointer is writer-owned and valid only while writer remains open.",
                       symbol="BytesWriter-data")
         + "\n" + _row("picop.cybytes.BytesWriter.grow", access="cimport",
                       kind="method", decision="specialized",
                       expression="Grow the writer buffer before filling it directly in Cython.",
                       contract="Native pointer is writer-owned; preserve the writer lifecycle and requested bounds.",
                       symbol="BytesWriter-grow")
         + "\n")
    _put(root, ".cursor/skills/use-cypy/maps/uuid.md",
         "# UUID\n\n" + HEADER + "\n|---|---|---|---|---|---|---|---|\n"
         + "| <a id=\"UUID\"></a>`picop.uuid._uuid.UUID` | class | python | companion | UUID value type | Public UUID class. | not-applicable: separate UUID suite | not-applicable: no Cython baseline |\n"
         + "| <a id=\"UUID-bytes\"></a>`picop.uuid._uuid.UUID.bytes` | method | python | companion | Read UUID bytes | Public UUID member. | not-applicable: separate UUID suite | not-applicable: no Cython baseline |\n"
         + "| <a id=\"uuid4\"></a>`picop.uuid._uuid.uuid4` | function | python | candidate | `uuid.uuid4()` | UUID generation. | not-measured: separate UUID suite; no superiority claim | not-applicable: no Cython baseline |\n"
         + "| <a id=\"uuid4_bytes\"></a>`picop.uuid._uuid.uuid4_bytes` | function | python | candidate | `uuid.uuid4().bytes` | UUID bytes. | not-measured: separate UUID suite; no superiority claim | not-applicable: no Cython baseline |\n")
    _put(root, ".cursor/skills/use-cypy/catalog.md",
         "# Catalog\n\n## Module maps\n\n| Module | Map | Surface |\n|---|---|---|\n"
         "| cydict | [map](maps/cydict.md) | Python and Cython exports |\n"
         "| cybytes | [map](maps/cybytes.md) | Python and Cython exports, writer members |\n"
         "| uuid | [map](maps/uuid.md) | UUID exports and members |\n")
    _put(root, "bench/cydict.py", "# fixture benchmark evidence\n")
    _put(root, "docs/PERF_PARITY.md", "")


def _run(root: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[int, str]:
    monkeypatch.setattr(sys, "argv", [str(CHECKER), "--root", str(root)])
    ns = runpy.run_path(str(CHECKER), run_name="__picop_check_consumer_map__")
    # main() is the stable contract; capture CLI diagnostics through pytest's capsys.
    return ns["main"](), ""

def _diagnostics(capsys: pytest.CaptureFixture[str]) -> str:
    captured = capsys.readouterr()
    return captured.out + captured.err


def test_valid_isolated_catalog_has_separate_coverage_totals(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    _fixture(tmp_path)
    assert _run(tmp_path, monkeypatch)[0] == 0
    output = capsys.readouterr().out
    assert "Additional Cython callables:" in output
    assert "UUID:" in output
    assert "Class members:" in output
    assert "Companion types/constants:" in output


@pytest.mark.parametrize("replacement, expected", [
    ("", "picop.cydict.dict_get"),
    (_row("picop.cydict.unknown"), "picop.cydict.unknown"),
])
def test_missing_or_unknown_row_is_diagnosed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], replacement: str, expected: str) -> None:
    _fixture(tmp_path, row=replacement)
    assert _run(tmp_path, monkeypatch)[0] != 0
    assert expected in capsys.readouterr().out


def test_duplicate_rows_fail_before_key_collapse(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    row = _row("picop.cydict.dict_get")
    _fixture(tmp_path, row=row + "\n" + row)
    assert _run(tmp_path, monkeypatch)[0] != 0
    assert "picop.cydict.dict_get" in capsys.readouterr().out


def test_cimport_only_access_cannot_be_claimed_as_python(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    _fixture(tmp_path)
    _put(tmp_path, "src/picop/__init__.py", "from .cydict import dict_get\n")
    path = tmp_path / ".cursor/skills/use-cypy/maps/cydict.md"
    path.write_text(path.read_text().replace("| function | both |", "| function | cimport |"), encoding="utf-8")
    assert _run(tmp_path, monkeypatch)[0] != 0
    assert "dict_get" in capsys.readouterr().out


def test_broken_catalog_link_is_rejected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    _fixture(tmp_path)
    path = tmp_path / ".cursor/skills/use-cypy/catalog.md"
    path.write_text(path.read_text().replace("maps/cydict.md", "maps/missing.md"), encoding="utf-8")
    assert _run(tmp_path, monkeypatch)[0] != 0
    assert "missing.md" in capsys.readouterr().out


def test_parity_loser_requires_skip_python(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    _fixture(tmp_path, row=_row(
        "picop.cydict.dict_get",
        python="recorded: [case](../../../../bench/cydict.py) measured losing baseline 1.2x",
    ))
    _put(tmp_path, "docs/PERF_PARITY.md",
         "## Always slower from pure Python\n"
         "| `dict_get` | `cydict` | 1.20x | `dict.get` | hit |\n")
    assert _run(tmp_path, monkeypatch)[0] != 0
    assert "skip-python" in _diagnostics(capsys).lower()


def test_not_measured_state_is_accepted_as_unmeasured(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _fixture(tmp_path)
    assert _run(tmp_path, monkeypatch)[0] == 0


@pytest.mark.parametrize(
    "source, expected",
    [
        ("from picop.cydict cimport *\n", "wildcard"),
        ("from .cydict import dict_get\n", None),
    ],
)
def test_invalid_or_supported_source_imports_are_handled(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    source: str,
    expected: str | None,
) -> None:
    _fixture(tmp_path)
    path = tmp_path / "examples/cimport_ext/demo.pyx"
    path.write_text(path.read_text(encoding="utf-8") + source, encoding="utf-8")
    status, _ = _run(tmp_path, monkeypatch)
    if expected is None:
        assert status == 0
    else:
        assert status != 0
        assert expected in _diagnostics(capsys).lower()


def test_missing_required_cell_is_rejected(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _fixture(tmp_path, row=_row("picop.cydict.dict_get").replace(
        "Concrete dict inputs; preserves only the stated miss contract.", ""
    ))
    assert _run(tmp_path, monkeypatch)[0] != 0
    assert "dict_get" in _diagnostics(capsys)


def test_mixed_parity_requires_case_dependent_evidence(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _fixture(tmp_path)
    _put(tmp_path, "docs/PERF_PARITY.md",
         "## Slower only on some inputs\n"
         "| `dict_get` | 1.2x (hit) | 0.9x (miss) |\n")
    assert _run(tmp_path, monkeypatch)[0] != 0
    assert "case-dependent" in _diagnostics(capsys).lower()


@pytest.mark.parametrize(
    "evidence, diagnostic",
    [
        ("not-measured: [missing](../../../../missing.py) no result", "missing.py"),
        ("not-measured: [catalog](../catalog.md#not-a-fragment) no result", "not-a-fragment"),
    ],
)
def test_broken_evidence_target_or_fragment_is_rejected(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    evidence: str,
    diagnostic: str,
) -> None:
    _fixture(tmp_path, row=_row("picop.cydict.dict_get", python=evidence))
    assert _run(tmp_path, monkeypatch)[0] != 0
    assert diagnostic in _diagnostics(capsys)


def test_grouped_symbol_cell_is_rejected(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _fixture(tmp_path, row=_row("picop.cydict.dict_get,dict_len"))
    assert _run(tmp_path, monkeypatch)[0] != 0
    assert "dict_get,dict_len" in _diagnostics(capsys)


def test_broken_catalog_fragment_is_rejected(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _fixture(tmp_path)
    index = tmp_path / ".cursor/skills/use-cypy/catalog.md"
    index.write_text(
        index.read_text(encoding="utf-8")
        + "\n## Navigate\n\n[dict lookup](maps/cydict.md#missing-row)\n",
        encoding="utf-8",
    )
    assert _run(tmp_path, monkeypatch)[0] != 0
    assert "missing-row" in _diagnostics(capsys)
