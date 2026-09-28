from __future__ import annotations

import os
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
