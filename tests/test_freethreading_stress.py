"""Free-threaded stress for the borrowed-result and unlocked-mutation helpers.

Every assertion below is an integrity invariant that a torn or unlocked read
would break: a borrowed slot promoted without a lock can hand back a dangling
pointer, a lost update, or a half-written object.
"""

from __future__ import annotations

import sysconfig
import threading

import pytest

pytestmark = pytest.mark.skipif(
    not sysconfig.get_config_var("Py_GIL_DISABLED"),
    reason="requires a free-threaded CPython build",
)

THREADS = 12
ITERATIONS = 3000


def _run(work: callable, threads: int = THREADS) -> list[object]:
    """Run ``work(index)`` in ``threads`` threads and return collected results."""
    barrier = threading.Barrier(threads)
    results: list[object] = []
    errors: list[str] = []

    def runner(index: int) -> None:
        try:
            barrier.wait(timeout=10)
            results.extend(work(index) or [])
        except BaseException as error:  # pragma: no cover - surfaced below
            errors.append(f"thread {index}: {error!r}")

    pool = [threading.Thread(target=runner, args=(i,)) for i in range(threads)]
    for thread in pool:
        thread.start()
    for thread in pool:
        thread.join(timeout=30)
    assert not any(thread.is_alive() for thread in pool), "stress workers did not finish"
    assert not errors, "; ".join(errors)
    return results


def test_dict_get_ref_survives_concurrent_replacement() -> None:
    from picop import dict_get_ref

    class Payload:
        __slots__ = ("tag", "pair")

        def __init__(self, tag: int) -> None:
            self.tag = tag
            self.pair = (tag, tag ^ 0x5A5A)

    mapping = {"value": Payload(0)}

    def work(index: int) -> list[object]:
        seen = []
        for iteration in range(ITERATIONS):
            if index % 4 == 0:
                mapping["value"] = Payload(index * ITERATIONS + iteration)
            else:
                retained = dict_get_ref(mapping, "value")
                assert retained is not None, "borrowed lookup returned NULL"
                assert isinstance(retained, Payload), "torn result is not a Payload"
                left, right = retained.pair
                assert right == (left ^ 0x5A5A), "result is half-written"
                seen.append(retained)
        return seen

    seen = _run(work)
    final = dict_get_ref(mapping, "value")
    assert final is mapping["value"]
    assert all(item.tag == item.pair[0] for item in seen)


def test_dict_setdefault_promotes_one_shared_object() -> None:
    from picop import dict_setdefault, dict_setdefault_ref

    mapping: dict[str, object] = {}

    def work(index: int) -> list[object]:
        for _ in range(ITERATIONS):
            borrowed = dict_setdefault(mapping, "shared", [index])
            owned = dict_setdefault_ref(mapping, "shared", [index])
            assert borrowed is owned, "setdefault handed out two different objects"
        return [dict_setdefault(mapping, "shared", None)]

    results = _run(work)
    assert len({id(result) for result in results}) == 1, "setdefault lost the first insert"
    assert isinstance(results[0], list)


def test_hash_buffer_agrees_across_threads() -> None:
    from picop import hash_buffer

    view = memoryview(bytes(range(256)) * 8)
    expected_full = hash(bytes(view))
    expected_range = hash(bytes(view[64:128]))

    def work(index: int) -> list[int]:
        return [hash_buffer(view) for _ in range(ITERATIONS)]

    results = _run(work)
    assert all(value == expected_full for value in results), "buffer hash diverged across threads"
    assert hash_buffer(view, 64, 128) == expected_range, "range hash disagrees with a slice copy"


def test_cell_get_reads_intact_values_under_concurrent_set() -> None:
    from picop import cell_get, cell_set

    def make_cell():
        value = 0

        def reader():
            return value

        return reader.__closure__[0]

    cell = make_cell()

    def work(index: int) -> list[object]:
        observed = []
        for _ in range(ITERATIONS):
            cell_set(cell, ("tag", index))
            got = cell_get(cell)
            assert isinstance(got, tuple) and got[0] == "tag", "borrowed cell read is torn"
            observed.append(got)
        return observed

    observed = _run(work)
    final = cell_get(cell)
    assert isinstance(final, tuple) and final[0] == "tag", "final cell read is torn"
    assert all(item[1] < THREADS for item in observed)


def test_list_get_reads_intact_items_under_concurrent_replacement() -> None:
    from picop import list_get, list_get_checked

    items = [None]

    def work(index: int) -> list[object]:
        observed = []
        for _ in range(ITERATIONS):
            items[0] = (index, index * 2)
            got = list_get(items, 0)
            checked = list_get_checked(items, 0)
            assert isinstance(got, tuple) and got[1] == got[0] * 2, "list slot read is torn"
            assert isinstance(checked, tuple) and checked[1] == checked[0] * 2, "checked read is torn"
            observed.append(got)
        return observed

    _run(work)
    assert list_get_checked(items, 0) is items[0]
