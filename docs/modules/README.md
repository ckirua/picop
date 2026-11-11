# Module trackers

One `NNN_cy{name}.md` per area — **`NNN` = QUEUE Order** (zero-padded, `001`…`069`; Order 069 extends existing tracker [`036_cydescr.md`](036_cydescr.md)).
**Process docs are one level up:** [`../README.md`](../README.md), [`../PIPELINE.md`](../PIPELINE.md), [`../TEMPLATE.md`](../TEMPLATE.md).

Gold exemplar: [`001_cytuple.md`](001_cytuple.md).

**Tracker grades:** 67 modules / 67 trackers grade A (`grades: A=67 B=0 C=0 total=67`).

## Present

| Order | Tracker | Maps to | Format |
|------:|---------|---------|--------|
| 1 | [001_cytuple.md](001_cytuple.md) | `cpython.tuple` | **v2 exemplar** |
| 2 | [002_cybytes.md](002_cybytes.md) | `cpython.bytes` | v2 |
| 3 | [003_cydict.md](003_cydict.md) | `cpython.dict` | v2 |
| 4 | [004_cylist.md](004_cylist.md) | `cpython.list` | v2 |
| 5 | [005_cyset.md](005_cyset.md) | `cpython.set` | **v2** |
| 6 | [006_cystr.md](006_cystr.md) | `cpython.unicode` (str helpers) | **v2** |
| 7 | [007_cyunicode.md](007_cyunicode.md) | `cpython.unicode` (UTF-8/intern) | **v2** |
| 8 | [008_cyansi.md](008_cyansi.md) | custom (terminal SGR) | **v2** |
| 9 | [009_cygc.md](009_cygc.md) | `Python.h` GC | **v2** |
| 10 | [010_cyerr.md](010_cyerr.md) | `cpython.exc` | **v2** |
| 11 | [011_cymem.md](011_cymem.md) | `cpython.mem` | **v2** |
| 12 | [012_cythread.md](012_cythread.md) | `cpython.pythread` | **v2** |
| 13 | [013_cyatomic.md](013_cyatomic.md) | custom (C11 `stdatomic`) | **v2** |
| 56 | [056_cycall.md](056_cycall.md) | `Python.h` call / vectorcall | v2 |
| 57 | [057_cyfrozendict.md](057_cyfrozendict.md) | `cpython.frozendict` (3.15+) | v2 |
| 58 | [058_cysentinel.md](058_cysentinel.md) | `Python.h` sentinel objects (3.15+) | v2 |
| 59 | [059_cyframe.md](059_cyframe.md) | `cpython.frame` | v2 |
| 60 | [060_cycode.md](060_cycode.md) | `cpython.code` | v2 |
| 61 | [061_cytraceback.md](061_cytraceback.md) | `cpython.traceback` | v2 |
| 62 | [062_cymonitoring.md](062_cymonitoring.md) | `cpython/monitoring.h` (PEP 670), cimport-only | v2 |
| 63 | [063_cylock.md](063_cylock.md) | `cpython.lock` / `cpython.pylock` (`PyMutex`) | v2 |
| 64 | [064_cyhash.md](064_cyhash.md) | `cpython/pyhash.h` | v2 |
| 65 | [065_cywarnings.md](065_cywarnings.md) | `Python.h` warning APIs | v2 |

| 66 | [066_cypicklebuf.md](066_cypicklebuf.md) | `cpython/picklebufobject.h` (3.15+) | v2 |
| 68 | [068_cysys.md](068_cysys.md) | `cpython/sysmodule.h` | v2 |
| 69 | [036_cydescr.md](036_cydescr.md) | `cpython.descrobject` (descriptor helpers) | v2 |

## Absent

Orders `014_`…`055_` live in this directory (all decided at 1.0); no orders are absent. See [`../README.md`](../README.md#status-complete--not-an-open-backlog) for phase-complete status — not an open promote backlog.

