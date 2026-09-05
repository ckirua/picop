"""Category facade: abstract Protocols (mapping / sequence / number / object).

**Provisional after 1.0** — not part of the Core freeze. Prefer ``picop.containers`` /
``picop.hot`` when you know ``dict`` / ``list`` / ``tuple`` / …. Use this facade only
when the concrete type is unknown. May still evolve under post-1.0 minors.
"""

from __future__ import annotations

from .cymapping import map_check, map_eq, map_has_key
from .cynumber import num_check, num_eq
from .cyobject import obj_eq
from .cysequence import seq_check, seq_contains, seq_eq, seq_get

__all__: tuple[str, ...] = (
    "map_check",
    "map_eq",
    "map_has_key",
    "seq_check",
    "seq_eq",
    "seq_get",
    "seq_contains",
    "num_check",
    "num_eq",
    "obj_eq",
)
