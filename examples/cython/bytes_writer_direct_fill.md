# BytesWriter direct fill (Order 080)

Use direct fill when the producer already knows the output length and can write
into a C buffer without creating a Python object for each chunk. Otherwise,
`write()` remains the simpler interface.

```cython
from libc.string cimport memcpy
from picop.cybytes cimport BytesWriter

cdef bytes fill_chunks(const char* src, Py_ssize_t n, Py_ssize_t plen):
    cdef Py_ssize_t i
    cdef char* p
    cdef BytesWriter writer = BytesWriter(n * plen)
    for i in range(n):
        p = writer.grow(plen)
        memcpy(p, src, plen)
    return writer.finish()
```

`grow()` reserves uninitialized bytes and returns the start of that region. If
you need to keep a partial result, truncate on finish:

```cython
cdef bytes finish_partial(const char* src, Py_ssize_t reserved,
                          Py_ssize_t written):
    cdef char* p
    cdef BytesWriter writer = BytesWriter(reserved)
    p = writer.grow(reserved)
    memcpy(p, src, written)
    return writer.finish_with_size(written)
```

A later `grow()` may reallocate the buffer; any pointer captured before it is
invalid. Write all reserved bytes before `finish()`, or use
`finish_with_size(written)` to discard the unused tail.

Measured (`bench/tier_b/cybytes.py`, 2,000,000 parts, CPython 3.14.7 / 3.15.0rc2): direct fill is
**0.61x** / **0.90x** of a hinted `write()` loop; reserving the whole buffer once and
filling in place is **0.36x** / **0.21x** of per-chunk `grow()`. At 200,000 parts on 3.15
the two paths are within run-to-run noise — reserve up front when the total length is
known, otherwise `write()` is fine.
