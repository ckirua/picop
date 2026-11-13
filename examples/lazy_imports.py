"""Per-interpreter lazy-import controls (CPython 3.15+).

Order 079: ``set_lazy_import_mode("all")`` defers module registration; a
module imported after the mode change stays out of ``sys.modules`` until
first use. Restore the previous mode when done.

Run: python examples/lazy_imports.py
"""
import sys

from picop import lazy_import_mode, lazy_imports_supported, set_lazy_import_mode

if not lazy_imports_supported():
    raise SystemExit("lazy import controls require CPython 3.15 or newer")

original = lazy_import_mode()
print(f"mode: {original}")

set_lazy_import_mode("all")
print(f"mode: {lazy_import_mode()}")

import wave  # deferred: not registered in sys.modules yet
print("wave in sys.modules:", "wave" in sys.modules)
wave.open  # first use materializes the module
print("wave in sys.modules:", "wave" in sys.modules)

set_lazy_import_mode(original)
print(f"mode restored: {lazy_import_mode()}")