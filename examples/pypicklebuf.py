"""Create and release a PickleBuffer for a bytearray exporter."""

from picop import pickle_buffer_check, pickle_buffer_from_object, pickle_buffer_release

payload = bytearray(b"serialized payload")
buffer = pickle_buffer_from_object(payload)
assert pickle_buffer_check(buffer)
assert memoryview(buffer).tobytes() == payload
pickle_buffer_release(buffer)
try:
    memoryview(buffer)
except ValueError:
    pass
else:
    raise AssertionError("released PickleBuffer still exposes a new buffer")
