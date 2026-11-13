import subprocess
import sys
import textwrap

import pytest

from picop import lazy_import_mode, lazy_imports_supported, set_lazy_import_mode, sys_get_attr


@pytest.mark.skipif(sys.version_info < (3, 15), reason="PySys attribute APIs require CPython 3.15")
def test_required_getter_balances_new_references():
    before = sys.getrefcount(sys.version)
    for _ in range(100):
        assert sys_get_attr("version") is sys.version
    assert sys.getrefcount(sys.version) == before


@pytest.mark.skipif(sys.version_info < (3, 15), reason="PySys attribute APIs require CPython 3.15")
def test_required_getter_raises_on_missing_name():
    with pytest.raises(RuntimeError):
        sys_get_attr("_picop_missing_sys_name")


@pytest.mark.skipif(sys.version_info < (3, 15), reason="Lazy import controls require CPython 3.15")
def test_lazy_import_mode_round_trip():
    original = lazy_import_mode()
    try:
        set_lazy_import_mode("all")
        assert lazy_import_mode() == "all"
        set_lazy_import_mode("normal")
        assert lazy_import_mode() == "normal"
    finally:
        set_lazy_import_mode(original)


@pytest.mark.skipif(sys.version_info < (3, 15), reason="Lazy import controls require CPython 3.15")
def test_lazy_mode_defers_module_registration_in_fresh_interpreter():
    script = textwrap.dedent(
        """
        import sys
        from picop import lazy_import_mode, set_lazy_import_mode
        set_lazy_import_mode("all")
        import wave
        deferred = "wave" not in sys.modules
        wave.open  # first use materializes the module
        materialized = "wave" in sys.modules
        print(deferred, materialized, lazy_import_mode())
        """
    )
    result = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert result.stdout.split() == ["True", "True", "all"]


@pytest.mark.skipif(sys.version_info < (3, 15), reason="Lazy import controls require CPython 3.15")
def test_lazy_import_mode_rejects_unknown_value():
    with pytest.raises(ValueError):
        set_lazy_import_mode("maybe")


@pytest.mark.skipif(sys.version_info >= (3, 15), reason="3.14 shim behavior")
def test_lazy_import_helpers_unavailable_on_314():
    assert lazy_imports_supported() is False
    with pytest.raises(NotImplementedError):
        lazy_import_mode()
    with pytest.raises(NotImplementedError):
        set_lazy_import_mode("all")
