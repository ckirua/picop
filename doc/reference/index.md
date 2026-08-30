# API reference

Public Python / `cpdef` surface only. Cimport-only and `cdef` symbols stay in the Cython SDK (see {doc}`/user_guide/quickstart`) and are not listed here.

Docstrings for compiled helpers are taken from adjacent `.pyi` stubs when the runtime object has no `__doc__`.

## Module map

| Area | Modules |
|------|---------|
| **Hot / facades** | {mod}`picop.hot`, {mod}`picop.containers`, {mod}`picop.buffers`, {mod}`picop.protocols` |
| **Core containers** | {mod}`picop.cydict`, {mod}`picop.cylist`, {mod}`picop.cytuple`, {mod}`picop.cyset`, {mod}`picop.cydeque`, {mod}`picop.cyrange` |
| **Bytes / str** | {mod}`picop.cybytes`, {mod}`picop.cybytearray`, {mod}`picop.cystr`, {mod}`picop.cyunicode`, {mod}`picop.cyansi` |
| **Buffers** | {mod}`picop.cyarray`, {mod}`picop.cymemoryview`, {mod}`picop.cybuffer`, {mod}`picop.cyslice` |
| **Protocols** | {mod}`picop.cymapping`, {mod}`picop.cysequence`, {mod}`picop.cynumber`, {mod}`picop.cyobject` |
| **Scalars / object model** | {mod}`picop.cybool`, {mod}`picop.cylong`, {mod}`picop.cyfloat`, {mod}`picop.cycomplex`, {mod}`picop.cytype`, {mod}`picop.cyfunction`, {mod}`picop.cymethod`, {mod}`picop.cymodule`, … |
| **Runtime** | {mod}`picop.cydatetime`, {mod}`picop.cycodecs`, {mod}`picop.cymarshal`, {mod}`picop.cyfileobject`, {mod}`picop.cyweakref`, {mod}`picop.cypycapsule`, {mod}`picop.cycontextvars`, {mod}`picop.cytime`, {mod}`picop.cygc` |
| **UUID** | {mod}`picop.uuid` |

```{toctree}
:maxdepth: 2

picop
```
