# `cyiterator` consumer map

Import/cimport from `picop.cyiterator`; package barrel access is also available where exported.

| Symbol | Kind | Access | Decision | Expression or use | Contract | Python evidence | Cython evidence |
|---|---|---|---|---|---|---|---|
| <a id="iter_check"></a>`picop.cyiterator.iter_check` | function | both | candidate | `isinstance(value, collections.abc.Iterator)` | CPython iterator-protocol check; avoid treating arbitrary iterables as iterators. [stub](../../../../src/picop/cyiterator.pyi) | not-measured: no recorded benchmark | not-measured: no typed consumer benchmark |
| <a id="iter_eq"></a>`picop.cyiterator.iter_eq` | function | both | candidate | `a is b` | Iterator identity comparison, not elementwise comparison or iterator advancement. [stub](../../../../src/picop/cyiterator.pyi) | not-measured: no recorded benchmark | not-measured: no typed consumer benchmark |
| <a id="iter_next"></a>`picop.cyiterator.iter_next` | function | both | specialized | `next(iterator, None)` | Wraps PyIter_Next; returns `None` on exhaustion, making exhausted and yielded-None ambiguous; errors propagate. [stub](../../../../src/picop/cyiterator.pyi) | not-measured: no recorded benchmark | not-measured: no typed consumer benchmark |
| <a id="itereq"></a>`picop.cyiterator.itereq` | function | cimport | legacy | `iter_eq(a, b)` | Retained Cython alias for iterator identity comparison; prefer `iter_eq` for new code. [pxd](../../../../src/picop/cyiterator.pxd) | not-applicable: Cython-only alias | not-measured: no separate baseline |
