# cybytes

| Field | Value |
|-------|--------|
| Status | present |
| Maps to | `cpython.bytes` (`Cython/Includes/cpython/bytes.pxd`) |
| Sources | `src/picop/cybytes.pxd`, `cybytes.pyx`, `cybytes.pyi` |
| Surface | public + cimport |
| Tracker lifecycle | decided (tier A + depth) |
| Format | v2 |
| Indexed | full |

## Why

Scanner hot paths plus full include try-all. Depth showed pure `memmem` **loses** to CPython `stringlib` on large haystacks; hybrid threshold + uninit/`_PyBytes_Resize` semantics documented below.

## Inventory

| Symbol | Layer | Kind | Export | Notes |
|--------|-------|------|--------|-------|
| bcheck | cypy | cpdef | public | `PyBytes_Check` |
| bcheck_exact | cypy | cpdef | public | `PyBytes_CheckExact` |
| blen | cypy | cpdef | public | `PyBytes_GET_SIZE` |
| bsize | cypy | cpdef | public | `PyBytes_Size` |
| bcontains | cypy | cpdef | public | `memchr`/`memmem` if `hlen≤256` else `in` |
| beq | cypy | cpdef | public | identity/len/`memcmp` (soft); preferred `bytes_eq` |
| bne | cypy | cpdef | public | `not beq` (soft); preferred `bytes_ne` |
| bba_eq / bytes_bytearray_eq | cypy | cpdef | public | bytes↔bytearray (either order) len+`memcmp`; soft `bba_eq`; not `hot` |
| bstartswith | cypy | cpdef | public | prefix len + `memcmp` (soft); preferred `bytes_startswith` |
| bendswith | cypy | cpdef | public | suffix len + tail `memcmp` (soft); preferred `bytes_endswith` |
| bfrom_object | cypy | cpdef | public | `PyBytes_FromObject` |
| BytesWriter | cypy | `cdef class` | public | Order 074: incremental builder — public `PyBytesWriter` API on 3.15+, internal `_PyBytesWriter` mirror in `cybytes_shim.h` on 3.8-3.14; `write` / `write_char` / `finish` / `discard`, context-manager |
| BytesWriter.size | cypy | `cpdef` | public | Order 080: `PyBytesWriter_GetSize` (3.15+) / tracked logical size (3.8-3.14) |
| BytesWriter.grow | cypy | `cdef` | cimport | Order 080: `PyBytesWriter_GrowAndUpdatePointer` (3.15+) / `_PyBytesWriter_Prepare` mirror; negative `extra` rewinds |
| BytesWriter.data | cypy | `cdef` | cimport | Order 080: `PyBytesWriter_GetData` (3.15+) / `pos - written` mirror |
| BytesWriter.finish_with_size | cypy | `cdef` | cimport | Order 080: `PyBytesWriter_FinishWithSize` (3.15+) / `_PyBytesWriter_Finish` at `base + size` |
| bas_string | cypy | cdef | cimport | `PyBytes_AS_STRING` |
| bas_string_checked | cypy | cdef | cimport | `PyBytes_AsString` (rejects non-bytes) |
| bfrom_string | cypy | cdef | cimport | `PyBytes_FromString` |
| bfrom_string_and_size | cypy | cdef | cimport | `PyBytes_FromStringAndSize` |
| bnew | cypy | cdef | cimport | uninit buffer — **not public** |
| bconcat | cypy | cdef | cimport | `PyBytes_Concat` |
| bconcat_and_del | cypy | cdef | cimport | `PyBytes_ConcatAndDel` |
| bresize | cypy | cdef | cimport | `_PyBytes_Resize` |
| PyBytes_Check / Exact | C-API | used-by | — | → checks |
| PyBytes_GET_SIZE / Size | C-API | used-by | — | → `blen` / `bsize` |
| PyBytes_AS_STRING / AsString | C-API | used-by | — | → `bas_string*` |
| PyBytes_AsStringAndSize | C-API | tried | — | covered by pointer + `blen` |
| PyBytes_FromObject / FromString* | C-API | used-by | — | → from_* / bnew |
| PyBytes_FromFormat / V | C-API | tried | — | varargs; no public wrap |
| PyBytes_Concat* | C-API | used-by | — | → `bconcat` / `bconcat_and_del` |
| _PyBytes_Resize | C-API | used-by | — | → `bresize` |
| PyBytes_Format / Intern* / Decode* / Encode* | C-API | tried | — | **not exported** on 3.14 `.so` |

## Workflow status

| Function | Status | Why |
|----------|--------|-----|
| bcontains | APPROVED | primary small **0.20x**; hybrid fixes large regression |
| beq | APPROVED | mirror `streq`; identity/len + `memcmp`; see Bench |
| bne / bytes_ne | APPROVED | `not beq` — API sibling of `str_ne` |
| bba_eq / bytes_bytearray_eq | APPROVED | Tier A **0.47–0.61x** vs `==` (issue #43); not `hot` |
| bstartswith / bytes_startswith | APPROVED | prefix len + `memcmp` (mirror `str_startswith`) |
| bendswith / bytes_endswith | APPROVED | suffix len + tail `memcmp` (mirror `str_endswith`) |
| blen / bsize | APPROVED | **0.59x**; prefer `blen` typed |
| bcheck / exact | APPROVED | **0.56x** / **0.55x** |
| bfrom_object | APPROVED | **0.60x** |
| BytesWriter | APPROVED | Order 074: beats `bytearray` (0.85x) and `+=` (0.02x); loses to `b''.join` on materialized parts (3.32x) — streaming builder, documented in PERF_PARITY |
| BytesWriter.size | APPROVED | Order 080 public accessor (additive minor); class already Tier A/B gated |
| BytesWriter.grow / data / finish_with_size | APPROVED (cimport) | Order 080: direct fill beats `write()` in a `cdef` loop (**0.61x**, 3.14 / see Bench); no Python-side win → cimport only |
| FinishWithPointer | REJECTED | Order 080: no capability `grow()` + `finish_with_size()` don't already give (`FinishWithPointer` = `FinishWithSize(buf - GetData())`) |
| `PyBytesWriter_Format` | REJECTED | Order 080: C varargs; `("%d" % n).encode()` + `write()` has no bench case |
| `cy_bytes_writer_grow` pointer arithmetic | APPROVED (build fix) | Order 083: `GetData(...) + GetSize(...)` is `void *` arithmetic — gcc/clang accept it as a GNU extension, MSVC rejects it (`error C2036`), which broke the Windows wheels of `picop-v3.10.0`. Cast to `char *` before the offset; `scripts/check_shims_pedantic.py` now compiles every shim with `-std=c11 -pedantic-errors -Werror` in the release preflight and on every PR, and `wheels.yml` builds a `cp315-win_amd64` wheel as the MSVC probe |
| bas_string* / from_string* | APPROVED (cimport) | C pointers / builders |
| bnew | APPROVED (cimport) | uninit ≠ `bytes(n)`; unsafe as public |
| bconcat / bconcat_and_del / bresize | APPROVED (cimport) | ownership/`*pv` semantics — cdef |
| Format / Intern / codecs | REJECTED | missing 3.14 ABI |
| FromFormat | REJECTED | varargs |
| AsStringAndSize helper | REJECTED | redundant with pointer + len |

## Lifecycle

| Field | Value |
|-------|--------|
| Freeze | **1.0 Core** — public + documented cimport; see COVERAGE § 1.0 freeze |
| Iteration | 11 |
| Last pass | 2026-11-16 — Order 083 build follow-up to 080: MSVC-safe `grow` pointer cast, strict-C11 shim gate, Windows wheel check on PRs. Earlier: Order 080 `BytesWriter` direct fill (`grow` / `data` / `finish_with_size` / `size`), Tier B on 3.14 + 3.15 |
| Next action | — |

## Decision log

| Function | Hypothesis | Bench / probe | Result | Decision | Iteration |
|----------|------------|---------------|--------|----------|-----------|
| bcontains | Beat `in` always | scale 6…8KiB | win &lt;256B; **lose** ≥1KiB on pure memmem | hybrid ≤256 → APPROVED | 4 |
| beq | Beat `==` on typed bytes | short/1KiB eq+ne | wins short; ~tie/win 1KiB | APPROVED (public + hot) | 6 |
| bba_eq / bytes_bytearray_eq | Cross-type vs `==` | Tier A both dirs + 1KiB | **0.47–0.61x** | APPROVED (public, not hot) | 8 |
| BytesWriter | Internal bytes writer beats Python builders? | Tier A builder bench + Tier B cdef loop | 0.02x vs `+=`, 0.85x vs bytearray, 3.32x vs join; Tier B 0.21x vs append+join | APPROVED (streaming niche) | 9 |
| BytesWriter direct fill (Order 080) | `grow()` + `memcpy` beats `write()` when the loop is already typed | Tier B cdef loop, 2M parts, 3.14.7 + 3.15.0rc2 | **0.61x** (3.14) vs hinted `write()`; grow-once **0.36x**; vs `bytearray` slice fill **0.06x** | APPROVED (cimport) — public `size()` only | 10 |
| `Grow` vs hint amortization | Does per-chunk `grow()` cost reallocations? | Tier B, hinted vs unhinted grow | 0.97x (3.14) — ~tie; overallocation absorbs it | APPROVED; hint still recommended | 10 |
| `FinishWithPointer` | Second finish variant worth wrapping? | 3.15 source (`bytesobject.c`) | `size = buf - data()` then `FinishWithSize` — already expressible | REJECTED | 10 |
| `PyBytesWriter_Format` | Wrap varargs writer | 3.15 source | varargs ABI, no typed-caller bench case | REJECTED | 10 |
| blen / bsize | Beat `len` | harness | **0.59x** | APPROVED | 4 |
| bcheck* | Beat isinstance | harness | **0.40–0.56x** | APPROVED | 4 |
| bfrom_object | Beat `bytes(buf)` | harness | **0.60x** | APPROVED | 4 |
| bnew | Beat `bytes(n)` | semantics | faster but **uninit leak** | REJECTED public → **cdef** | 4 |
| bconcat / bconcat_and_del | Unique-only / +DECREF | source | unique in-place; else new object | APPROVED (cimport) | 5 |
| bresize | Like tuple SystemError | CPython source | non-unique **copies** (no BadInternalCall) | APPROVED (cimport) | 4 |
| Format/Intern/codecs | Wrap | `nm` 3.14 | missing symbols | REJECTED | 3 |

## Bench results

Harness: [`bench/cybytes_bench.py`](../../bench/cybytes_bench.py) · tier A · 3.14 · `N=80_000` × 5 · warmup 0  
**Primary:** small multi-byte hit → **~0.20x** · **`bytes_eq`** short/1KiB → **0.59–0.68x** vs Python `==`

| operation | case | cypy mean±σ | p99 | ratio | p99× | verdict |
|-----------|------|-------------|-----|-------|------|---------|
| bcontains | small multi hit | — | — | **~0.20x** | — | APPROVED |
| bcontains | small 1-byte hit | — | — | ~0.19x | — | APPROVED |
| bcontains | small miss | — | — | ~0.20x | — | APPROVED |
| bcontains | 1KiB late hit | — | — | ~1.00x | — | ~tie (hybrid) |
| bcontains | 8KiB miss | — | — | ~1.03x | — | ~tie (hybrid) |
| beq | eq same | 0.97±0.03ms | 1.00ms | **0.59x** | 0.58x | APPROVED |
| beq | ne same-len | 1.01±0.01ms | 1.02ms | **0.61x** | 0.59x | APPROVED |
| beq | ne short | 0.99±0.04ms | 1.05ms | **0.60x** | 0.60x | APPROVED |
| beq | eq 1KiB | 0.94±0.02ms | 0.97ms | **0.59x** | 0.59x | APPROVED |
| beq | ne 1KiB | 1.56±0.02ms | 1.59ms | **0.68x** | 0.67x | APPROVED |
| beq | eq empty | 0.93±0.02ms | 0.95ms | **0.59x** | 0.59x | APPROVED |
| blen | blen | — | — | **~0.60x** | — | APPROVED |
| bsize | bsize | — | — | ~0.61x | — | APPROVED |
| bcheck | bytes | — | — | ~0.50x | — | APPROVED |
| bcheck | str | — | — | ~0.40x | — | APPROVED |
| bcheck_exact | bytes | — | — | ~0.59x | — | APPROVED |
| bfrom_object | memoryview | — | — | ~0.61x | — | APPROVED |

### Pre-hybrid scale (evidence for threshold)

Pure `memmem` vs `in` (ad-hoc, before hybrid): hlen=6 → ~0.20x; 64 → ~0.40x; **256 → ~1.00x**; 1024 → ~1.9x; 8192 → ~2.7x. Threshold **256** chosen at crossover.

### Tier B (Cython baseline)

Harness: [`bench/tier_b/cybytes.py`](../../bench/tier_b/cybytes.py) · `cybytes_tb.pyx` · CPython 3.14 · Linux x86_64 · `CPY_TIERB_N=2_000_000` × `runs=5`  
Ratio = cypy `cdef` loop / typed Cython baseline loop (opaque + sink). **Informational** — does not reopen Tier A.

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| bcontains | small multi hit | 3.91±0.06ms | 3.97ms | 103.07±0.59ms | **0.04x** | 0.04x | cypy faster |
| beq | equal | 2.52±0.01ms | 2.53ms | 2.53±0.01ms | **1.00x** | 0.99x | ~tie |
| blen | small | 2.97±0.20ms | 3.20ms | 2.84±0.10ms | **1.05x** | 1.11x | baseline faster |
| bcheck | bytes | 2.48±0.01ms | 2.49ms | 2.51±0.02ms | **0.99x** | 0.98x | ~tie |
| bcheck_exact | bytes | 2.96±0.19ms | 3.22ms | 2.83±0.14ms | **1.05x** | 1.08x | baseline faster |

**Tier B takeaway:** primary `bcontains` **0.04x** vs typed `in` (memmem path wins in cdef loop). `beq` **~tie** vs typed `==` (win is Tier A Python call overhead).

### `bytes_bytearray_eq` (Tier A depth)

Harness: [`bench/cybytes_bench.py`](../../bench/cybytes_bench.py) · N=80_000 × runs=11 · CPython 3.14

| operation | case | cypy mean±σ | p99 | ratio | p99× | verdict |
|-----------|------|-------------|-----|-------|------|---------|
| bytes_bytearray_eq | bytes→ba eq | 1.08±0.06ms | 1.19ms | **0.50x** | 0.52x | APPROVED |
| bytes_bytearray_eq | ba→bytes eq | 1.05±0.03ms | 1.09ms | **0.49x** | 0.48x | APPROVED |
| bytes_bytearray_eq | bytes→ba ne | 1.04±0.02ms | 1.09ms | **0.47x** | 0.46x | APPROVED |
| bytes_bytearray_eq | eq 1KiB cross | 1.57±0.03ms | 1.64ms | **0.59x** | 0.59x | APPROVED |
| bytes_bytearray_eq | ne 1KiB cross | 1.59±0.03ms | 1.65ms | **0.61x** | 0.60x | APPROVED |
| bytes_bytearray_eq | bytes↔bytes | 0.96±0.06ms | 1.07ms | **0.59x** | 0.64x | APPROVED |
| bytes_bytearray_eq | ba↔ba | 1.05±0.02ms | 1.08ms | **0.49x** | 0.49x | APPROVED |
| bytes_bytearray_eq | empty cross | 0.99±0.04ms | 1.07ms | **0.47x** | 0.48x | APPROVED |

### Tier B — `*_eq` (inventory)

Harness: [`bench/tier_b/cyeq_inventory.py`](../../bench/tier_b/cyeq_inventory.py) · `cyeq_*_tb.pyx` · CPython 3.14 · Linux x86_64 · `CPY_TIERB_N=2_000_000` (heavy shapes `N/40`) × `runs=5`  
Ratio = cypy `cdef` loop / typed Cython baseline `==` loop (opaque + sink). **Informational** — does not reopen Tier A.

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| bytes_eq | eq short | 2.53±0.02ms | 2.56ms | 2.53±0.01ms | **1.00x** | 1.00x | ~tie |
| bytes_eq | ne short | 2.90±0.02ms | 2.93ms | 2.57±0.02ms | **1.13x** | 1.12x | baseline faster |
| bytes_eq | eq 1KiB | 0.06±0.00ms | 0.06ms | 0.07±0.00ms | **0.95x** | 0.87x | cypy faster |
| bytes_bytearray_eq | bytes→ba eq | 3.41±0.02ms | 3.43ms | 18.01±0.09ms | **0.19x** | 0.19x | cypy faster |
| bytes_bytearray_eq | ba→bytes eq | 3.49±0.09ms | 3.62ms | 15.68±0.26ms | **0.22x** | 0.22x | cypy faster |
| bytes_bytearray_eq | bytes→ba ne | 3.80±0.04ms | 3.83ms | 18.60±0.07ms | **0.20x** | 0.20x | cypy faster |

**Tier B `*_eq` notes:**
- **`bytes_eq`:** Equal ~tie; ne **1.13x** lose (extra len/memcmp vs Cython `==`). 1KiB eq **0.95x**. Matches prior `cybytes` Tier B.
- **`bytes_bytearray_eq`:** **0.19–0.22x** win — typed memcmp path beats Cython cross-type `==` (buffer protocol / coerce).

### ne / startswith / endswith inventory (Tier A + B)

Harness: [`bench/cyne_search_inventory_bench.py`](../../bench/cyne_search_inventory_bench.py) · Tier B [`bench/tier_b/cyne_search.py`](../../bench/tier_b/cyne_search.py) · N=80_000 × runs=11 (A) / `CPY_TIERB_N=2_000_000` × runs=5 (B).

| operation | case | ratio A | ratio B | note |
|-----------|------|---------|---------|------|
| `bytes_ne` | eq/ne short + 1KiB | **0.59–0.67x** | **0.68–0.95x** | pass |
| `bytes_startswith` | hit/miss + 1KiB | **0.60–0.61x** | **0.74x** hit | pass |
| `bytes_endswith` | hit/miss + 1KiB | **0.57–0.60x** | **0.89x** hit | pass |

### BytesWriter (Order 074 builder bench)

Harness: [`bench/cybytes_bench.py`](../../bench/cybytes_bench.py) · CPython 3.14.7 · Linux x86_64 · 80,000 short parts per build, 20 builds sampled × `runs=5`

| operation | case | cypy mean±σ | p99 | ratio | p99× | verdict |
|-----------|------|-------------|-----|-------|------|---------|
| BytesWriter | hint 160k vs `b''.join` | 62.15±8.86ms | 77.22ms | **3.47x** | 3.58x | baseline wins (single C pass) |
| BytesWriter | no hint vs `b''.join` | 57.51±0.94ms | 58.46ms | **3.32x** | 2.89x | crossover documented |
| BytesWriter | no hint vs `bytearray`+`bytes()` | 57.67±0.87ms | 58.81ms | **0.85x** | 0.83x | pass (≥5% gate) |
| BytesWriter | no hint vs `b += p` | 58.39±0.40ms | 58.85ms | **0.02x** | 0.02x | pass |
| BytesWriter | hint vs no hint (3.14.7, Order 075) | 61.03±1.05ms | 61.97ms | **0.97x** | 0.96x | hint honoured; marginal win |
| BytesWriter | hint vs no hint (3.15.0rc2, Order 075) | 70.32±1.16ms | 71.85ms | **1.00x** | 1.01x | hint now honoured via `Create(hint)` + `Resize(0)`; tie — amortized overallocation absorbs the gain, per-write dispatch dominates |

**Tier B — `BytesWriter` in a cdef loop** (`bench/tier_b/cybytes.py` + `cybytes_tb.pyx`, N=2,000,000 parts): `cypy_bwriter` 25.73±0.13ms vs `list.append`+`join` baseline 121.15±4.88ms -> **0.21x** (p99 0.20x). The writer wins big when the loop can dispatch in C: no 2M-element part list is materialized.

### BytesWriter direct fill (Order 080, Tier B)

Harness: [`bench/tier_b/cybytes.py`](../../bench/tier_b/cybytes.py) · [`bench/tier_b/cybytes_tb.pyx`](../../bench/tier_b/cybytes_tb.pyx) · `CPY_TIERB_N=2_000_000` (scale row `200_000`) × `runs=5` · Linux x86_64. Ratio = direct-fill loop / typed baseline loop. **Informational** — `grow()` / `data()` / `finish_with_size()` are cimport-only, so there is no Tier A row to reopen; the `BytesWriter` class keeps its existing Tier A/B compare labels.

**CPython 3.14.7 (internal `_PyBytesWriter_Prepare` mirror)**

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| BytesWriter.grow | `grow()`+`memcpy` vs `write()`, both hinted | 17.92±0.41ms | 18.58ms | 29.31±0.56ms | **0.61x** | 0.62x | cypy faster (≥5% gate) |
| BytesWriter.grow | no hint vs hint (grow path) | 19.69±0.32ms | 20.11ms | 20.40±1.64ms | 0.97x | 0.87x | ~tie — `Prepare` overallocates |
| BytesWriter.grow | `grow(n)` once vs `grow(plen)` per chunk | 7.03±0.33ms | 7.45ms | 19.40±0.35ms | **0.36x** | 0.38x | cypy faster |
| BytesWriter.grow | vs `bytearray(n*plen)` slice fill | 19.64±0.66ms | 20.40ms | 329.21±24.54ms | **0.06x** | 0.06x | cypy faster |
| BytesWriter.grow | scale: 200k parts | 1.76±0.03ms | 1.80ms | 2.66±0.06ms | **0.66x** | 0.66x | cypy faster |

**CPython 3.15.0rc2 (public `PyBytesWriter_Grow` / `GrowAndUpdatePointer`)** — repeat run in brackets

| operation | case | cypy mean±σ | p99 | cy-base mean±σ | ratio | p99× | note |
|-----------|------|-------------|-----|----------------|-------|------|------|
| BytesWriter.grow | `grow()`+`memcpy` vs `write()`, both hinted | 32.29±0.90ms | 33.50ms | 36.05±0.36ms | **0.90x** | 0.92x | pass (≥5% gate); repeat **0.93x** |
| BytesWriter.grow | no hint vs hint (grow path) | 33.68±0.45ms | 34.28ms | 35.88±2.25ms | 0.94x | 0.87x | pass; repeat 1.04x (noise) |
| BytesWriter.grow | `grow(n)` once vs `grow(plen)` per chunk | 7.36±1.26ms | 9.50ms | 34.98±0.36ms | **0.21x** | 0.27x | cypy faster; repeat **0.20x** |
| BytesWriter.grow | vs `bytearray(n*plen)` slice fill | 35.15±1.39ms | 37.30ms | 308.51±12.93ms | **0.11x** | 0.11x | cypy faster; repeat **0.12x** |
| BytesWriter.grow | scale: 200k parts | 3.68±0.99ms | 5.36ms | 3.44±0.03ms | 1.07x | 1.54x | baseline faster (repeat 1.06x) |

Probe notes: 3.14 and 3.15 both build the same shim; the internal mirror tracks its own `written` field because `Prepare` returns the new write pointer and the buffer base is not recoverable from it. `Grow` on 3.15 goes through `byteswriter_resize(..., overallocate=1)`, the same amortized growth `WriteBytes` uses, so per-chunk `grow()` costs only the extra argument passing — visible as the small 3.15 margin. Direct fill wins everywhere the loop is already typed; at 200k parts on 3.15 the two paths are within noise.

## Experiment conclusions

**Tier B `*_eq` inventory:** see section **Tier B — `*_eq` (inventory)** table. Equal ~tie; ne **1.13x** lose (extra len/memcmp vs Cython `==`). 1KiB eq **0.95x**. Matches prior `cybytes` Tier B.

**ne/search inventory:** `bytes_ne` / `bytes_startswith` / `bytes_endswith` all gate-pass Tier A; Tier B still ahead of typed Cython `!=` / `startswith` / `endswith`.

**Tier B:** primary `bcontains` **0.04x** vs typed `in` (memmem path wins in cdef loop).

| Topic | Finding |
|-------|---------|
| Why small win | Avoids Python `sq_contains` / `stringlib` call overhead; `memchr`/`memmem` on tiny buffers |
| Why large lose | CPython `bytes_contains` → `_Py_bytes_contains` / `stringlib_find` (not exported); glibc `memmem` slower here past ~256B |
| Fix | `hlen > 256` → fall back to `needle in haystack` |
| `beq` / `bytes_eq` | Identity + len short-circuit + `memcmp` on `PyBytes_AS_STRING` (mirror `streq`). Tier A **0.59–0.68x** vs Python `==`; Tier B ~tie vs typed Cython `==` — export to `cypy.hot` |
| `bne` / `bytes_ne` | `not beq` — API sibling of `str_ne`; public + hot |
| `bba_eq` / `bytes_bytearray_eq` | Cross-type ``bytes``↔``bytearray`` via type check + `AS_STRING` + `memcmp`. Tier A **0.47–0.61x** vs Python `==` (both directions + 1KiB). Not `hot` (prefer typed `bytes_eq` / `bytearray_eq` when types known). Distinct from `buf_eq` (buffer protocol / views). |
| `bstartswith` / `bytes_startswith` | prefix len + `memcmp`; public + hot |
| `bendswith` / `bytes_endswith` | suffix len + tail `memcmp`; public + hot |
| `bnew` | `FromStringAndSize(NULL,n)` leaves **previous heap contents**; `bytes(n)` zeros — **cdef only** |
| `_PyBytes_Resize` | Unlike `_PyTuple_Resize`, non-unique path **allocates a copy** and DECREFs old `*pv` (expects owned ref). Mis-wrapping without owning the ref is UB |
| `PyBytes_Concat` / `ConcatAndDel` | Unique+exact → resize in place; else new object via `SETREF`. Both aliased (`bconcat`, `bconcat_and_del`) |
| `AsString` | `TypeError` on `bytearray`; `AS_STRING` is unchecked typed `bytes` |
| `BytesWriter` (Order 074) | CPython has **no public** bytes-writer API before 3.15; the wrapper uses `PyBytesWriter_Create/WriteBytes/Finish/Discard` on 3.15+ and mirrors the internal `_PyBytesWriter` (`Init`/`Prepare`/`Finish`/`Dealloc`) in `cybytes_shim.h` on 3.8-3.14 — those functions are non-static in the interpreter (exported for `_pickle`) and link directly. Python-level per-write dispatch (~60 ns) is the cost: join wins when parts are materialized (3.32x), the writer wins vs `bytearray` (0.85x) and crushes `+=` (0.02x). In a `cdef` loop it is ~5x faster than append+join — the right tool is streaming, not batch. Order 075: the `max_size` hint is honoured on all supported versions — 3.8-3.14 via internal `Prepare`, 3.15+ via `PyBytesWriter_Create(hint)` + `PyBytesWriter_Resize(writer, 0)` (there is no pure reservation call: `Create(size)` pre-writes and `Resize` sets the logical size too, but rewinding to 0 never shrinks the allocation, so the buffer starts as reserved capacity). On 3.14 the hint barely matters (3.47x vs 3.32x). |
| `BytesWriter` direct fill (Order 080) | `grow(extra)` + `memcpy` removes the per-chunk Python object: **0.61x** vs hinted `write()` on 3.14, **0.90x** on 3.15 (repeat 0.93x). Reserving once and filling in place is the fast shape (**0.36x** / **0.21x** vs per-chunk `grow()`), and any typed `bytearray` slice fill is ~10-16x slower. On 3.15 `Grow` and `WriteBytes` share `byteswriter_resize(..., overallocate=1)`, so the margin is only the dispatch saved — the win is largest when the chunk pointer is already C-typed. Public surface stays `write()`/`finish()`/`size()`; `grow()`/`data()`/`finish_with_size()` are cimport-only because a raw `char *` cannot be safely handed to Python. |
| `BytesWriter` safety | The writer owns its buffer; `finish()` consumes it (NULL-checked guard, `RuntimeError` on reuse), `discard()` frees it, `__dealloc__` releases an unclosed writer. `Prepare` and `grow()` may reallocate, so the wrapper always re-assigns `pos` from the return value — cached pointers into the buffer are invalid after each `grow()`/`write()`. Bytes reserved by `grow()` are uninitialized: write them, or truncate with `finish_with_size(written)`. The wrapper range-checks `finish_with_size()` before calling CPython, whose `FinishWithSize` discards the writer on a bad size. |
| 3.14 ABI | No Format / Intern / Decode / Encode exports |

## Done when

- [x] Full inventory
- [x] Try-all + **depth** (scale, hybrid, uninit, resize≠tuple, ABI)
- [x] Bench results + experiment conclusions
- [x] Before merge: `.pyi` one-liners; lean `.pxd`; `bnew` not public
- [x] `bytes_eq` / `beq` (issue #2) — public + hot
- [x] `bytes_ne` / `bne` (issue #8) — public + hot
- [x] `bytes_startswith` / `bstartswith` (issue #12) — public + hot
- [x] `bytes_endswith` / `bendswith` (issue #13) — public + hot
- [x] `bytes_bytearray_eq` / `bba_eq` (issue #43) — public (not hot); cross-link `buf_eq`
- [x] Order 074: `BytesWriter` class, tests, builder bench (Tier A + B), PERF_PARITY row, example + cimport smoke
- [x] Order 080: `size()` public, `grow()` / `data()` / `finish_with_size()` cimport-only, Tier B evidence on 3.14 + 3.15, `FinishWithPointer` / `Format` rejected, direct-fill recipe + smoke-demo coverage
