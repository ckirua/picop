"""Subprocess-isolated ownership and mutable-container regressions."""

from __future__ import annotations

import os
import subprocess
import sys
import sysconfig
import textwrap


def _run_isolated(source: str) -> None:
    gil_disabled = bool(sysconfig.get_config_var("Py_GIL_DISABLED"))
    command = [sys.executable]
    if gil_disabled:
        command.extend(["-X", "gil=0"])
    bootstrap = (
        "import sys\n"
        "import sysconfig\n"
        "if sysconfig.get_config_var('Py_GIL_DISABLED'):\n"
        "    assert sys._is_gil_enabled() is False\n"
        "import picop\n"
        "if sysconfig.get_config_var('Py_GIL_DISABLED'):\n"
        "    assert sys._is_gil_enabled() is False\n"
    )
    script = bootstrap + textwrap.dedent(source)
    command.extend(["-c", script])
    env = os.environ.copy()
    env.pop("PYTHON_GIL", None)
    result = subprocess.run(command, timeout=30, capture_output=True, text=True, env=env)
    assert result.returncode == 0, result.stderr


def test_weakref_owned_results_and_reclamation() -> None:
    _run_isolated(
        """
        import gc
        from picop import weakref_get_object, weakref_new_ref

        class Value: pass
        value = Value()
        ref = weakref_new_ref(value)
        assert weakref_get_object(ref) is value
        del value
        gc.collect()
        assert weakref_get_object(ref) is None
        try:
            weakref_get_object(object())
        except TypeError:
            pass
        else:
            raise AssertionError('wrong weakref type accepted')

        value = Value()
        ref = weakref_new_ref(value)
        retained = weakref_get_object(ref)
        del value
        gc.collect()
        assert ref() is retained
        del retained
        gc.collect()
        assert ref() is None
        """
    )


def test_checked_list_bounds_and_fixed_index_replacement() -> None:
    _run_isolated(
        """
        from concurrent.futures import ThreadPoolExecutor
        from threading import Barrier
        from picop import list_get, list_get_checked, list_get_ref

        values = [object()]
        for index in (-1, 1):
            try:
                list_get_checked(values, index)
            except IndexError:
                pass
            else:
                raise AssertionError('checked getter did not reject OOB index')
        assert list_get_ref(values, 0) is values[0]

        class Payload:
            def __init__(self, value):
                self.value = (value, value ^ 0x5A5A)
        values = [Payload(0)]
        start = Barrier(2)
        def replace():
            start.wait(timeout=10)
            for i in range(20000):
                values[0] = Payload(i)
        def read():
            start.wait(timeout=10)
            for _ in range(20000):
                for get in (list_get_checked, list_get):
                    value = get(values, 0)
                    assert value.value[1] == value.value[0] ^ 0x5A5A
        with ThreadPoolExecutor(max_workers=2) as pool:
            a = pool.submit(replace)
            b = pool.submit(read)
            a.result(timeout=20)
            b.result(timeout=20)
        """
    )


def test_dict_lookup_errors_and_retained_results() -> None:
    _run_isolated(
        """
        from concurrent.futures import ThreadPoolExecutor
        from threading import Barrier
        from picop import dict_get, dict_get_ref, dict_get_with_error

        class BadKey:
            def __hash__(self):
                return hash('bad')
            def __eq__(self, other):
                raise LookupError('comparison failed')
        class BadHash:
            def __hash__(self):
                raise LookupError('hash failed')
        mapping = {'none': None}
        assert dict_get(mapping, 'missing') is None
        assert dict_get(mapping, 'none') is None
        assert dict_get_ref(mapping, 'missing') is None
        assert dict_get_ref(mapping, 'none') is None
        assert dict_get_with_error(mapping, 'missing') is None
        assert dict_get_with_error(mapping, 'none') is None
        broken = {BadKey(): 1}
        assert dict_get(broken, 'bad') is None
        for lookup, key, message in (
            (broken, 'bad', 'comparison failed'),
            (mapping, BadHash(), 'hash failed'),
        ):
            try:
                dict_get_with_error(lookup, key)
            except LookupError as error:
                assert str(error) == message
            else:
                raise AssertionError('propagating lookup suppressed an error')

        class Payload:
            def __init__(self, value):
                self.value = (value, value ^ 0x5A5A)
        marker = Payload(10)
        mapping['value'] = marker
        retained = dict_get_ref(mapping, 'value')
        mapping['value'] = Payload(11)
        assert retained is marker

        mapping['value'] = Payload(0)
        start = Barrier(2)
        def replace():
            start.wait(timeout=10)
            for i in range(20000):
                mapping['value'] = Payload(i)
        def read():
            start.wait(timeout=10)
            for _ in range(20000):
                result = dict_get(mapping, 'value')
                assert result.value[1] == result.value[0] ^ 0x5A5A
        with ThreadPoolExecutor(max_workers=2) as pool:
            a = pool.submit(replace)
            b = pool.submit(read)
            a.result(timeout=20)
            b.result(timeout=20)
        """
    )


def test_cell_and_function_replacement_ownership() -> None:
    _run_isolated(
        """
        import gc
        import weakref
        from concurrent.futures import ThreadPoolExecutor
        from threading import Barrier
        from picop import (
            cell_get, cell_new, cell_set,
            func_get_defaults, func_set_defaults,
        )

        class Payload:
            def __init__(self, value):
                self.value = (value, value ^ 0x5A5A)
        initial = Payload(0)
        cell = cell_new(initial)
        cell_ref = weakref.ref(initial)
        original = cell_get(cell)
        cell_set(cell, Payload(1))
        del initial
        gc.collect()
        assert cell_ref() is original
        del original
        gc.collect()
        assert cell_ref() is None

        def function(value=None):
            return value
        held = function.__defaults__
        marker = Payload(2)
        marker_ref = weakref.ref(marker)
        func_set_defaults(function, (marker,))
        result = func_get_defaults(function)
        func_set_defaults(function, (Payload(3),))
        del marker
        gc.collect()
        assert marker_ref() is result[0]
        del result
        gc.collect()
        assert marker_ref() is None
        assert held == (None,)

        start = Barrier(4)
        def replace_cell():
            start.wait(timeout=10)
            for i in range(20000):
                cell_set(cell, Payload(i))
        def read_cell():
            start.wait(timeout=10)
            for _ in range(20000):
                value = cell_get(cell)
                assert value.value[1] == value.value[0] ^ 0x5A5A
        def replace_defaults():
            start.wait(timeout=10)
            for i in range(20000):
                func_set_defaults(function, (Payload(i),))
        def read_defaults():
            start.wait(timeout=10)
            for _ in range(20000):
                value = func_get_defaults(function)[0]
                assert value.value[1] == value.value[0] ^ 0x5A5A
        with ThreadPoolExecutor(max_workers=4) as pool:
            jobs = [
                pool.submit(replace_cell), pool.submit(read_cell),
                pool.submit(replace_defaults), pool.submit(read_defaults),
            ]
            for job in jobs:
                job.result(timeout=20)
        """
    )
