import pytest

from picop.cydescr import descr_is_data, descr_name, descr_objclass


def test_descriptor_introspection():
    descriptor = str.upper
    assert descr_name(descriptor) == "upper"
    assert descr_objclass(descriptor) is str
    assert descr_is_data(property())


@pytest.mark.parametrize("value", [None, 1, object(), property()])
def test_non_cpython_descriptor_rejected(value):
    with pytest.raises(TypeError):
        descr_name(value)
    with pytest.raises(TypeError):
        descr_objclass(value)
