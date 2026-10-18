from __future__ import annotations

import os
import time
import threading
import uuid
from collections.abc import Callable

import pytest

from picoipc import Ring, impl_name


def unique_name() -> str:
    return f"picoipc_test_{os.getpid()}_{uuid.uuid4().hex}"


@pytest.fixture
def ring_factory() -> Callable[..., tuple[str, Ring, Callable[[], Ring]]]:
    rings: list[Ring] = []
    names: list[str] = []

    def create(**kwargs: object) -> tuple[str, Ring, Callable[[], Ring]]:
        name = unique_name()
        Ring.unlink(name)
        names.append(name)
        creator = Ring(name, create=True, **kwargs)
        rings.append(creator)

        def attach() -> Ring:
            consumer = Ring(name, create=False, **kwargs)
            rings.append(consumer)
            return consumer

        return name, creator, attach

    try:
        yield create
    finally:
        for ring in reversed(rings):
            ring.close()
        for name in names:
            Ring.unlink(name)


def test_selected_backend() -> None:
    expected = os.environ.get("PICOIPC_EXPECTED_IMPL")
    if expected is None:
        pytest.skip("no backend selected for this test run")
    assert impl_name() == expected


def test_create_attach_readability(ring_factory: Callable[..., tuple[str, Ring, Callable[[], Ring]]]) -> None:
    _, producer, attach = ring_factory(slot_count=2, slot_size=64, schema_id=42)
    consumer = attach()

    assert consumer.try_consume() is None
    assert consumer.wait_readable(0) is False
    assert producer.try_publish(b"hello") is True
    assert consumer.wait_readable(0) is True
    assert consumer.try_consume() == b"hello"
    assert consumer.try_consume() is None
    assert consumer.wait_readable(0) is False


def test_fifo(ring_factory: Callable[..., tuple[str, Ring, Callable[[], Ring]]]) -> None:
    _, producer, attach = ring_factory(slot_count=3, slot_size=64)
    consumer = attach()

    for payload in (b"one", b"two", b"three"):
        assert producer.try_publish(payload) is True

    assert [consumer.try_consume() for _ in range(3)] == [b"one", b"two", b"three"]
    assert consumer.try_consume() is None


def test_backpressure_and_wraparound(ring_factory: Callable[..., tuple[str, Ring, Callable[[], Ring]]]) -> None:
    _, producer, attach = ring_factory(slot_count=2, slot_size=64)
    consumer = attach()

    assert producer.try_publish(b"a") is True
    assert producer.try_publish(b"b") is True
    assert producer.try_publish(b"c") is False
    assert consumer.try_consume() == b"a"
    assert producer.try_publish(b"c") is True
    assert consumer.try_consume() == b"b"
    assert consumer.try_consume() == b"c"
    assert consumer.try_consume() is None


def test_payload_capacity_boundary(ring_factory: Callable[..., tuple[str, Ring, Callable[[], Ring]]]) -> None:
    _, producer, attach = ring_factory(slot_count=2, slot_size=64)
    consumer = attach()

    payload = b"x" * 56
    assert producer.try_publish(payload) is True
    assert consumer.try_consume() == payload
    with pytest.raises(Exception):
        producer.try_publish(b"x" * 57)


@pytest.mark.parametrize("kwargs", [{"slot_count": 1}, {"slot_size": 63}])
def test_invalid_geometry(kwargs: dict[str, int]) -> None:
    with pytest.raises(Exception):
        Ring(unique_name(), create=True, **kwargs)


def test_attach_failures(ring_factory: Callable[..., tuple[str, Ring, Callable[[], Ring]]]) -> None:
    name, _, _ = ring_factory(slot_count=2, slot_size=64, schema_id=42)

    with pytest.raises(Exception):
        Ring(name, create=False, schema_id=43)
    with pytest.raises(Exception):
        Ring(unique_name(), create=False)


def test_creator_unlink_prevents_attach(ring_factory: Callable[..., tuple[str, Ring, Callable[[], Ring]]]) -> None:
    name, creator, _ = ring_factory(slot_count=2, slot_size=64)
    creator.close(unlink=True)

    with pytest.raises(Exception):
        Ring(name, create=False)


def test_closed_sentinels(ring_factory: Callable[..., tuple[str, Ring, Callable[[], Ring]]]) -> None:
    _, producer, _ = ring_factory(slot_count=2, slot_size=64)
    producer.close()
    assert producer.try_publish(b"x") is False
    assert producer.try_consume() is None
    assert producer.wait_readable(0) is False
    assert producer.write_seq() == producer.read_seq() == 0
    producer.wake()
    producer.close()





def _packet(index: int) -> bytes:
    checksum = (index * 2654435761) & 0xFFFFFFFF
    return index.to_bytes(4, "little") + checksum.to_bytes(4, "little")


def test_ten_thousand_threaded_fifo(ring_factory: Callable[..., tuple[str, Ring, Callable[[], Ring]]]) -> None:
    _, producer, attach = ring_factory(slot_count=128, slot_size=64)
    consumer = attach()
    failures: list[BaseException | object] = []

    def run(operation: Callable[[], None]) -> None:
        try:
            operation()
        except BaseException as exc:
            failures.append(exc)

    def produce() -> None:
        for index in range(10_000):
            deadline = time.monotonic() + 10
            while not producer.try_publish(_packet(index)):
                assert time.monotonic() < deadline

    def consume() -> None:
        for index in range(10_000):
            deadline = time.monotonic() + 10
            value = consumer.try_consume()
            while value is None:
                assert time.monotonic() < deadline
                value = consumer.try_consume()
            if value != _packet(index):
                failures.append((index, value))

    threads = [threading.Thread(target=run, args=(produce,), daemon=True),
               threading.Thread(target=run, args=(consume,), daemon=True)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(30)
        assert not thread.is_alive()
    assert failures == []




def _process_consume(name: str, result: object) -> None:
    from picoipc import Ring as ProcessRing
    ring = ProcessRing(name, create=False, slot_count=128, slot_size=64)
    output: list[bytes] = []
    try:
        for index in range(10_000):
            deadline = time.monotonic() + 15
            item = ring.try_consume()
            while item is None:
                if time.monotonic() >= deadline:
                    raise TimeoutError(f"timed out at {index}")
                item = ring.try_consume()
            output.append(item)
    finally:
        ring.close()
    result.put(output)


def test_ten_thousand_process_fifo(ring_factory: Callable[..., tuple[str, Ring, Callable[[], Ring]]]) -> None:
    import multiprocessing
    name, producer, _ = ring_factory(slot_count=128, slot_size=64)
    context = multiprocessing.get_context("spawn")
    result = context.Queue()
    process = context.Process(target=_process_consume, args=(name, result))
    try:
        process.start()
        for index in range(10_000):
            deadline = time.monotonic() + 15
            while not producer.try_publish(_packet(index)):
                assert time.monotonic() < deadline
        received = result.get(timeout=30)
        process.join(30)
        assert not process.is_alive()
        assert process.exitcode == 0
        assert received == [_packet(index) for index in range(10_000)]
    finally:
        if process.pid is not None and process.is_alive():
            process.terminate()
        if process.pid is not None:
            process.join(5)
        result.close()
        result.join_thread()


def test_wait_allows_publication_on_the_same_handle(ring_factory: Callable[..., tuple[str, Ring, Callable[[], Ring]]]) -> None:
    _, ring, _ = ring_factory(slot_count=2, slot_size=64)
    started = threading.Event()
    results: list[object] = []

    def waiter() -> None:
        started.set()
        try:
            results.append(ring.wait_readable(2000))
        except BaseException as error:
            results.append(error)

    worker = threading.Thread(target=waiter, daemon=True)
    worker.start()
    assert started.wait(2)
    assert ring.try_publish(b"wake")
    worker.join(3)
    assert not worker.is_alive()
    assert results == [True]
    assert ring.try_consume() == b"wake"


def test_close_races_with_wait_and_operations(ring_factory: Callable[..., tuple[str, Ring, Callable[[], Ring]]]) -> None:
    _, ring, _ = ring_factory(slot_count=2, slot_size=64)
    started = threading.Event()

    def waiter() -> None:
        started.set()
        ring.wait_readable(50)

    worker = threading.Thread(target=waiter, daemon=True)
    worker.start()
    assert started.wait(2)
    closers = [threading.Thread(target=ring.close, daemon=True) for _ in range(2)]
    for closer in closers:
        closer.start()
    worker.join(2)
    for closer in closers:
        closer.join(2)
        assert not closer.is_alive()
    assert not worker.is_alive()
    assert ring.try_publish(b"x") is False
    assert ring.try_consume() is None


def test_native_buffers_and_claim_view_lifetime_when_pybind11() -> None:
    if impl_name() != "pybind11":
        pytest.skip("native buffer API belongs to the pybind11 backend")
    from array import array
    from ctypes import c_ubyte

    name = unique_name()
    producer = Ring(name, create=True, slot_count=2, slot_size=64)
    consumer = Ring(name, create=False, slot_count=2, slot_size=64)
    view = None
    derived = None
    try:
        assert producer.try_publish(memoryview(bytearray(b"contiguous")))
        assert consumer.try_consume() == b"contiguous"
        assert producer.try_publish(memoryview((c_ubyte * 3)(1, 2, 3)))
        assert consumer.try_consume() == b"\x01\x02\x03"
        with pytest.raises(TypeError):
            producer.try_publish(memoryview(bytearray(b"abcdef"))[::2])
        with pytest.raises(TypeError):
            producer.try_publish(memoryview(array("I", [1, 2])))
        with pytest.raises(TypeError):
            consumer.try_consume_into(memoryview(b"readonly"))
        view = producer.claim()
        assert view is not None
        derived = view[:]
        view[:5] = b"claim"
        assert producer.publish(5)
        producer.close(unlink=True)
        del producer
        assert bytes(derived[:5]) == b"claim"
    finally:
        consumer.close()
        if derived is not None:
            derived.release()
        if view is not None:
            view.release()
        if "producer" in locals():
            producer.close(unlink=True)


def test_pybind_closed_claim_and_publish_sentinels() -> None:
    if impl_name() != "pybind11":
        pytest.skip("native lifecycle API belongs to the pybind11 backend")
    ring = Ring(unique_name(), create=True, slot_count=2, slot_size=64)
    ring.close(unlink=True)
    assert ring.try_claim() is False
    assert ring.claim() is None
    assert ring.publish(1) is False
    with pytest.raises(RuntimeError, match="Ring is closed"):
        ring.publish(b"x", 1)


@pytest.mark.parametrize("failure", ["missing", "not_lock_free"])
def test_pure_backend_requires_lock_free_atomics(monkeypatch: pytest.MonkeyPatch, failure: str) -> None:
    if impl_name() != "pure_python":
        pytest.skip("libatomic requirements belong to the pure backend")
    import picoipc.ring as pure_ring

    name = unique_name()
    if failure == "missing":
        def unavailable() -> object:
            raise OSError("libatomic unavailable")
        monkeypatch.setattr(pure_ring, "_libatomic", unavailable)
    else:
        from types import SimpleNamespace
        monkeypatch.setattr(pure_ring, "_libatomic", lambda: SimpleNamespace(**{"__atomic_is_lock_free": lambda size, address: False}))
    try:
        with pytest.raises(OSError):
            pure_ring.Ring(name, create=True, slot_count=2, slot_size=64)
    finally:
        pure_ring.Ring.unlink(name)




