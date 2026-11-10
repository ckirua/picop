import pickle

import pytest
import sys

pytestmark = pytest.mark.skipif(sys.version_info < (3, 15), reason="PickleBuffer C API requires CPython 3.15")

from picop import (
    pickle_buffer_check,
    pickle_buffer_from_object,
    pickle_buffer_release,
    pickle_buffer_type,
)


class BufferHolder:
    def __init__(self, value):
        self.value = value

    def __reduce__(self):
        return (type(self), (pickle_buffer_from_object(self.value),))

def test_pickle_buffer_from_bytearray_and_memoryview():
    for obj in (bytearray(b"hello"), memoryview(bytearray(b"world"))):
        wrapped = pickle_buffer_from_object(obj)
        assert type(wrapped) is pickle_buffer_type()
        assert pickle_buffer_check(wrapped)
        assert bytes(memoryview(wrapped)) == bytes(obj)


def test_pickle_buffer_release_invalidates_export():
    wrapped = pickle_buffer_from_object(bytearray(b"payload"))
    view = memoryview(wrapped)
    assert view.tobytes() == b"payload"
    pickle_buffer_release(wrapped)
    with pytest.raises(ValueError):
        memoryview(wrapped)
    # Existing views own their acquired export and remain valid until released.
    view.release()


def test_pickle_buffer_rejects_non_buffer():
    with pytest.raises(TypeError):
        pickle_buffer_from_object(object())


def test_pickle_buffer_requires_type_for_release():
    with pytest.raises(TypeError):
        pickle_buffer_release(object())


def test_pickling_round_trip_of_pickle_buffer():
    restored = pickle.loads(pickle.dumps(BufferHolder(bytearray(b"round trip")), protocol=5))
    assert bytes(memoryview(restored.value)) == b"round trip"
