import warnings

import pytest

from picop.cywarnings import warn_ex, warn_explicit, warnings_module


def test_warning_default_filter():
    with pytest.warns(RuntimeWarning, match="probe"):
        assert warn_ex(RuntimeWarning, "probe") is False

def test_warning_ignore_and_error():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        assert warnings.filters[0][0] == "ignore"
        assert warn_ex(RuntimeWarning, "ignored") is False
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        assert warnings.filters[0][0] == "error"
        with pytest.raises(RuntimeWarning, match="raised"):
            warn_ex(RuntimeWarning, "raised")


def test_custom_category_and_stacklevel():
    class CustomWarning(Warning):
        pass

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        expected = __import__(__name__, fromlist=["x"]).__file__
        line = __import__("inspect").currentframe().f_lineno + 1
        warn_ex(CustomWarning, "location", stacklevel=1)
        assert caught[-1].category is CustomWarning
        assert caught[-1].filename == expected
        assert caught[-1].lineno == line

    def issue_from_helper():
        warn_ex(CustomWarning, "caller", stacklevel=2)

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        line = __import__("inspect").currentframe().f_lineno + 1
        issue_from_helper()
        assert caught[-1].lineno == line

def test_warn_explicit_and_warnings_module():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        assert warn_explicit(RuntimeWarning, "explicit", "source.py", 42) is False
        assert caught[-1].category is RuntimeWarning
        assert str(caught[-1].message) == "explicit"
        assert caught[-1].filename == "source.py"
        assert caught[-1].lineno == 42
    assert warnings_module() is warnings

def test_warn_explicit_registry_and_bad_category():
    registry = {}
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        assert warn_explicit(RuntimeWarning, "registry", "registry.py", 7, registry=registry) is False
    assert caught[-1].lineno == 7
    assert caught[-1].category is RuntimeWarning
    assert str(caught[-1].message) == "registry"
    with pytest.raises(TypeError):
        warn_ex(str, "invalid category")

def test_warn_explicit_registry_suppresses_duplicates():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("default")
        warn_explicit(RuntimeWarning, "duplicate", "registry.py", 5, "registry_probe", None)
        warn_explicit(RuntimeWarning, "duplicate", "registry.py", 5, "registry_probe", None)
        assert len(caught) == 2

    registry = {}
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("default")
        warn_explicit(RuntimeWarning, "duplicate", "registry.py", 5, "registry_probe", registry)
        warn_explicit(RuntimeWarning, "duplicate", "registry.py", 5, "registry_probe", registry)
        assert len(caught) == 1
