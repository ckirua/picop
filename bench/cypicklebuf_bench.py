"""Compare PickleBuffer creation with ordinary views and pickle serialization."""
from __future__ import annotations

import pickle
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from picop import pickle_buffer_from_object  # noqa: E402
from _bench_util import BenchSession  # noqa: E402


class BufferRecord:
    def __init__(self, data):
        self.data = data

    def __reduce__(self):
        return (type(self), (pickle_buffer_from_object(self.data),))


def cypy_buffer_for_record(record):
    return pickle_buffer_from_object(record.data)


def main() -> None:
    session = BenchSession("cypicklebuf — creation vs Python baselines (tier A)")
    session.header()
    session.section("buffer wrapper creation")
    for data in (bytearray(b"short!"), bytearray(b"pickle buffer benchmark payload" * 8),
                 bytearray(b"x" * 4096)):
        session.compare("pickle_buffer_from_object", pickle_buffer_from_object, memoryview, data,
                        param=f"bytearray n={len(data)}")
    data = bytearray(b"pickle buffer benchmark payload" * 8)
    record = BufferRecord(data)
    session.section("creation vs serializing a buffer-backed object")
    session.compare("pickle_buffer_from_object", cypy_buffer_for_record,
                    lambda obj: pickle.dumps(obj), record,
                    param=f"pickle.dumps buffer-backed record n={len(data)}")
    session.summary()


if __name__ == "__main__":
    main()
