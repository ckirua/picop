"""Behavioral tests for :mod:`picop.uuid`."""

from __future__ import annotations

import concurrent.futures
from collections.abc import Callable
import os
import pickle
import uuid as stdlib_uuid

import pytest

import picop
import picop.uuid as picop_uuid
from picop.uuid import UUID, uuid4, uuid4_bytes

COMPACT = "12345678123456789abcdef012345678"
CANONICAL = "12345678-1234-5678-9abc-def012345678"
VALUE_BYTES = bytes.fromhex(COMPACT)


def test_public_exports_are_exactly_the_canonical_api() -> None:
    assert tuple(picop_uuid.__all__) == ("UUID", "uuid4", "uuid4_bytes")
    assert picop_uuid.UUID is UUID
    assert picop_uuid.uuid4 is uuid4
    assert picop_uuid.uuid4_bytes is uuid4_bytes
    assert not hasattr(picop_uuid, "randstr_16")
    assert picop.UUID is UUID
    assert picop.uuid4 is uuid4
    assert picop.uuid4_bytes is uuid4_bytes
    assert {"UUID", "uuid4", "uuid4_bytes"} <= set(picop.__all__)


def test_uuid_is_final_and_inherits_from_stdlib_uuid() -> None:
    assert issubclass(UUID, stdlib_uuid.UUID)
    assert UUID.__bases__ == (stdlib_uuid.UUID,)
    assert UUID.__mro__ == (UUID, stdlib_uuid.UUID, object)
    with pytest.raises(TypeError):
        type("DerivedUUID", (UUID,), {})


@pytest.mark.parametrize(
    "source",
    [
        VALUE_BYTES,
        COMPACT,
        COMPACT.upper(),
        CANONICAL,
        CANONICAL.upper(),
    ],
    ids=[
        "bytes",
        "compact-lower",
        "compact-upper",
        "canonical-lower",
        "canonical-upper",
    ],
)
def test_uuid_constructs_from_supported_representations(source: bytes | str) -> None:
    value = UUID(source)

    assert type(value) is UUID
    assert isinstance(value, UUID)
    assert isinstance(value, stdlib_uuid.UUID)
    assert value.bytes == VALUE_BYTES
    assert str(value) == CANONICAL


@pytest.mark.parametrize(
    "value",
    [
        b"",
        b"\x00" * 15,
        b"\x00" * 17,
        "",
        COMPACT[:-1],
        CANONICAL + "0",
        COMPACT + "-----",
        "{" + CANONICAL + "}",
        "urn:uuid:" + CANONICAL,
        "é" * 5 + COMPACT[:27],
    ],
    ids=[
        "zero-bytes",
        "15-bytes",
        "17-bytes",
        "empty-string",
        "31-byte-string",
        "37-byte-string",
        "five-hyphens",
        "braced",
        "urn",
        "multibyte-over-36-bytes",
    ],
)
def test_uuid_rejects_invalid_encoded_lengths(value: bytes | str) -> None:
    with pytest.raises(ValueError):
        UUID(value)

@pytest.mark.parametrize(
    "value",
    [
        "g" + COMPACT[1:],
        "/" + COMPACT[1:],
        ":" + COMPACT[1:],
        "é" + COMPACT[1:],
        COMPACT[:-1] + " ",
        CANONICAL[:-1] + "g",
        CANONICAL[:24] + "_" + CANONICAL[25:],
        CANONICAL[:24] + "\x00" + CANONICAL[25:],
    ],
    ids=[
        "non-hex-letter",
        "below-zero",
        "above-nine",
        "non-ascii",
        "whitespace",
        "canonical-non-hex-letter",
        "canonical-underscore",
        "canonical-nul",
    ],
)
def test_uuid_rejects_invalid_hex_characters(value: str) -> None:
    with pytest.raises(ValueError):
        UUID(value)


@pytest.mark.parametrize(
    "value",
    [
        "-" + COMPACT,
        "-" + COMPACT + "-",
        "--" + COMPACT + "-",
        "----" + COMPACT,
        COMPACT + "----",
        COMPACT[:16] + "----" + COMPACT[16:],
        "1234567-81234-5678-9abc-def012345678",
        "12345678-123-45678-9abc-def012345678",
        "12345678-1234-567-89abc-def012345678",
        "12345678-1234-5678-9ab-cdef012345678",
    ],
    ids=[
        "one-leading",
        "two-at-boundaries",
        "three-at-boundaries",
        "four-leading-consecutive",
        "four-trailing-consecutive",
        "four-middle-consecutive",
        "first-canonical-hyphen-left",
        "second-canonical-hyphen-left",
        "third-canonical-hyphen-left",
        "fourth-canonical-hyphen-left",
    ],
)
def test_uuid_accepts_up_to_four_hyphens_in_arbitrary_positions(value: str) -> None:
    encoded = value.encode()
    assert 32 <= len(encoded) <= 36
    assert value.replace("-", "") == COMPACT
    assert UUID(value).bytes == VALUE_BYTES


@pytest.mark.parametrize(
    "value",
    [
        COMPACT[:-1] + "-",
        COMPACT[:-2] + "--",
        COMPACT[:-1] + "-----",
        COMPACT + "0",
        COMPACT + "00",
        COMPACT + "000",
        COMPACT + "0000",
        CANONICAL.replace("-", "0", 1),
    ],
    ids=[
        "31-digits-one-hyphen",
        "30-digits-two-hyphens",
        "31-digits-five-hyphens",
        "33-digits",
        "34-digits",
        "35-digits",
        "36-digits",
        "33-digits-three-hyphens",
    ],
)
def test_uuid_rejects_strings_decoding_to_wrong_byte_length(value: str) -> None:
    assert 32 <= len(value.encode()) <= 36
    with pytest.raises(ValueError):
        UUID(value)


@pytest.mark.parametrize(
    "value",
    [
        None,
        0,
        True,
        bytearray(VALUE_BYTES),
        memoryview(VALUE_BYTES),
        stdlib_uuid.UUID(CANONICAL),
        [0] * 16,
    ],
    ids=[
        "none",
        "integer",
        "boolean",
        "bytearray",
        "memoryview",
        "stdlib-uuid",
        "list",
    ],
)
def test_uuid_rejects_unsupported_input_types(value: object) -> None:
    with pytest.raises(TypeError):
        UUID(value)


def test_uuid_representation_and_properties_match_stdlib() -> None:
    value = UUID(VALUE_BYTES)
    expected = stdlib_uuid.UUID(bytes=VALUE_BYTES)

    assert str(value) == CANONICAL
    assert value.hex == COMPACT
    assert value.int == int(COMPACT, 16)
    assert value.bytes == VALUE_BYTES
    assert value.bytes_le == bytes.fromhex("78563412341278569abcdef012345678")
    assert value.fields == expected.fields
    assert value.time_low == expected.time_low
    assert value.time_mid == expected.time_mid
    assert value.time_hi_version == expected.time_hi_version
    assert value.clock_seq_hi_variant == expected.clock_seq_hi_variant
    assert value.clock_seq_low == expected.clock_seq_low
    assert value.time == expected.time
    assert value.clock_seq == expected.clock_seq
    assert value.node == expected.node
    assert value.urn == expected.urn
    assert value.version == expected.version
    assert value.variant == expected.variant
    assert value.is_safe == expected.is_safe


def test_stdlib_equality_hash_and_mapping_interoperability_is_symmetric() -> None:
    value = UUID(CANONICAL)
    expected = stdlib_uuid.UUID(CANONICAL)
    other = stdlib_uuid.UUID("12345678-1234-5678-9abc-def012345679")

    assert value == expected
    assert expected == value
    assert value != other
    assert other != value
    assert hash(value) == hash(expected)
    assert len({value, expected}) == 1
    assert {value: "picop"}[expected] == "picop"
    assert {expected: "stdlib"}[value] == "stdlib"


def test_stdlib_ordering_interoperability_is_symmetric() -> None:
    cycel_low = UUID("00000000000000000000000000000001")
    cycel_high = UUID("00000000000000000000000000000002")
    stdlib_low = stdlib_uuid.UUID(int=1)
    stdlib_high = stdlib_uuid.UUID(int=2)

    assert cycel_low < stdlib_high
    assert stdlib_low < cycel_high
    assert cycel_high > stdlib_low
    assert stdlib_high > cycel_low
    assert cycel_low <= stdlib_low
    assert stdlib_low <= cycel_low
    assert cycel_high >= stdlib_high
    assert stdlib_high >= cycel_high
    assert not cycel_low < stdlib_low
    assert not stdlib_low > cycel_low


@pytest.mark.parametrize(
    "other",
    [None, 1, COMPACT, object()],
    ids=["none", "integer", "string", "object"],
)
def test_unsupported_comparisons_follow_python_protocol(other: object) -> None:
    value = UUID(CANONICAL)

    assert (value == other) is False
    assert (other == value) is False
    assert (value != other) is True
    assert (other != value) is True
    with pytest.raises(TypeError):
        value < other  # type: ignore[operator]
    with pytest.raises(TypeError):
        other < value  # type: ignore[operator]
    with pytest.raises(TypeError):
        value <= other  # type: ignore[operator]
    with pytest.raises(TypeError):
        other >= value  # type: ignore[operator]


def test_uuid_repr_is_unambiguous() -> None:
    assert repr(UUID(CANONICAL)) == f"UUID('{CANONICAL}')"


@pytest.mark.parametrize("protocol", range(pickle.HIGHEST_PROTOCOL + 1))
def test_uuid_pickle_round_trip(protocol: int) -> None:
    value = UUID(CANONICAL)

    restored = pickle.loads(pickle.dumps(value, protocol=protocol))

    assert type(restored) is UUID
    assert restored == value
    assert restored.bytes == VALUE_BYTES


def _assert_uuid4_bytes(value: bytes) -> None:
    assert type(value) is bytes
    assert len(value) == 16
    assert value[6] & 0xF0 == 0x40
    assert value[8] & 0xC0 == 0x80
    parsed = stdlib_uuid.UUID(bytes=value)
    assert parsed.version == 4
    assert parsed.variant == stdlib_uuid.RFC_4122


def test_uuid4_bytes_has_required_type_length_version_and_variant() -> None:
    _assert_uuid4_bytes(uuid4_bytes())


def test_uuid4_has_required_type_version_and_variant() -> None:
    value = uuid4()

    assert type(value) is UUID
    assert isinstance(value, UUID)
    assert isinstance(value, stdlib_uuid.UUID)
    assert value.version == 4
    assert value.variant == stdlib_uuid.RFC_4122
    _assert_uuid4_bytes(value.bytes)


def _generate_values(factory: Callable[[], object], count: int) -> list[object]:
    return [factory() for _ in range(count)]


@pytest.mark.parametrize(
    "factory",
    [uuid4_bytes, uuid4],
    ids=["uuid4-bytes", "uuid4"],
)
def test_generated_values_are_unique_across_bounded_multithreaded_generation(
    factory: Callable[[], object],
) -> None:
    workers = 4
    values_per_worker = 256
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(_generate_values, factory, values_per_worker)
            for _ in range(workers)
        ]
        values = [value for future in futures for value in future.result()]

    assert len(values) == workers * values_per_worker
    assert len(set(values)) == len(values)


@pytest.mark.skipif(not hasattr(os, "fork"), reason="requires POSIX fork")
def test_uuid4_bytes_differ_between_parent_and_forked_child() -> None:
    uuid4_bytes()
    read_fd, write_fd = os.pipe()
    pid = os.fork()

    if pid == 0:
        os.close(read_fd)
        try:
            payload = uuid4_bytes()
            offset = 0
            while offset < len(payload):
                offset += os.write(write_fd, payload[offset:])
            os.close(write_fd)
        except BaseException:
            os._exit(1)
        os._exit(0)

    os.close(write_fd)
    try:
        parent_value = uuid4_bytes()
        child_value = bytearray()
        while len(child_value) < 16:
            chunk = os.read(read_fd, 16 - len(child_value))
            if not chunk:
                break
            child_value.extend(chunk)
    finally:
        os.close(read_fd)
        _, status = os.waitpid(pid, 0)

    assert os.waitstatus_to_exitcode(status) == 0
    assert len(child_value) == 16
    assert parent_value != bytes(child_value)
