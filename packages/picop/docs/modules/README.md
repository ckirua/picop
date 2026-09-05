# Module trackers

One `NNN_cy{name}.md` per area — **`NNN` = QUEUE Order** (zero-padded, `001`…`055`).  
**Process docs are one level up:** [`../README.md`](../README.md), [`../PIPELINE.md`](../PIPELINE.md), [`../TEMPLATE.md`](../TEMPLATE.md).

Gold exemplar: [`001_cytuple.md`](001_cytuple.md).

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

## Absent

Orders `014_`…`055_` live in this directory (all decided at 1.0). See [`../README.md`](../README.md#status-complete--not-an-open-backlog) for phase-complete status — not an open promote backlog.
