import sys

import pytest

from picop import sys_get_attr


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
