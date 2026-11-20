# `cyrange` consumer map

Python import: `picop.cyrange`; package barrel exports `range_eq`. Cython cimport from `picop.cyrange`.

| Symbol | Kind | Access | Decision | Expression or use | Contract | Python evidence | Cython evidence |
|---|---|---|---|---|---|---|---|
| <a id="range_eq"></a>`picop.cyrange.range_eq` | function | both | candidate | `a == b` | Intended for range values; same represented-sequence equality, including different endpoints/steps describing the same sequence. Falls back to rich comparison for non-range objects; no benchmark evidence in module tracker. [stub](../../../../src/picop/cyrange.pyi) | not-measured: no recorded case evidence found | not-measured: no Cython consumer baseline recorded |
