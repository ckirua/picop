"""Generate and inspect a C-backed UUID value."""

import uuid

from picop.uuid import UUID, uuid4, uuid4_bytes

value = uuid4()
raw = uuid4_bytes()

assert type(value) is UUID
assert isinstance(value, uuid.UUID)
assert value.version == 4
assert UUID(raw).version == 4
print(value)
