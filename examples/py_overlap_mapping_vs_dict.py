"""Overlap playbook: known ``dict`` → cydict; unknown mapping → cymapping.

Run: python examples/py_overlap_mapping_vs_dict.py
"""

from __future__ import annotations

from types import MappingProxyType

from picop import dict_contains, dict_get, dict_len, map_check, map_has_key, map_len

def main() -> None:
    known: dict[str, int] = {"a": 1, "b": 2}
    # Known concrete dict → typed Core helpers
    assert dict_len(known) == 2
    assert dict_get(known, "a") == 1
    assert dict_contains(known, "b")

    # Unknown mapping-like (proxy) → protocol helpers
    proxy = MappingProxyType(known)
    assert map_check(proxy)
    assert map_has_key(proxy, "a")
    assert map_len(proxy) == 2

    # map_* also works on dict, but prefer dict_* when the type is known
    assert map_has_key(known, "a")
    print("ok mapping vs dict", dict_len(known), map_len(proxy))

if __name__ == "__main__":
    main()
