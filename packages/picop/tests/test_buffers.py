"""Buffer helpers remain safe when mutable exporters are resized concurrently."""

from __future__ import annotations

import subprocess
import sys
import sysconfig
import textwrap

from picop import memoryview_eq, memoryview_from_object, memoryview_nbytes



def test_bytearray_and_array_comparisons_during_resize() -> None:
    gil_option = ["-Xgil=0"] if sysconfig.get_config_var("Py_GIL_DISABLED") else []
    code = textwrap.dedent(
        """
        from array import array
        from threading import Barrier, Thread

        from picop import array_eq, bytearray_eq, bytes_bytearray_eq

        left = bytearray(b"a" * 64)
        right = bytearray(b"b" * 64)
        left_array = array("B", [1] * 64)
        right_array = array("B", [2] * 64)
        start = Barrier(2)

        def resize() -> None:
            start.wait()
            for i in range(5000):
                size = 64 if i & 1 else 96
                left[:] = b"a" * size
                right[:] = b"b" * size
                left_array[:] = array("B", [1] * size)
                right_array[:] = array("B", [2] * size)

        worker = Thread(target=resize, daemon=True)
        worker.start()
        start.wait()
        for _ in range(5000):
            assert bytearray_eq(left, right) is False
            assert array_eq(left_array, right_array) is False
            assert bytes_bytearray_eq(b"a" * len(left), right) is False
        worker.join(timeout=10)
        assert not worker.is_alive()
        """
    )
    subprocess.run(
        [sys.executable, *gil_option, "-c", code],
        check=True,
        timeout=30,
    )

def test_memoryview_exports_keep_mutable_exporters_stable() -> None:
    source = bytearray(b"payload")
    view = memoryview_from_object(source)
    child = view[1:]
    assert memoryview_nbytes(view) == 7
    assert memoryview_eq(view, memoryview_from_object(bytearray(b"payload")))
    try:
        source.extend(b"!")
    except BufferError:
        pass
    else:
        raise AssertionError("live memoryview did not prevent exporter resize")
    del view
    assert bytes(child) == b"ayload"
    del child
    source.extend(b"!")
    assert source == b"payload!"
