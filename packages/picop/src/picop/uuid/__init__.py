"""Fast C-backed UUID values and version 4 generation."""

from __future__ import annotations

from ._uuid import UUID, uuid4, uuid4_bytes

__all__ = ("UUID", "uuid4", "uuid4_bytes")
