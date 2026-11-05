# cysentinel — sentinel markers in Cython

CPython 3.15 provides sentinel objects for distinct marker values. Use the
cimported checks before treating an object as a marker, and create named markers
with `sentinel_new`:

```cython
from picop.cysentinel cimport (
    sentinel_check,
    sentinel_check_exact,
    sentinel_new,
    sentinel_type,
)

cdef object MISS = sentinel_new("MISS")

cdef bint is_missing(object value):
    return sentinel_check_exact(value) and value is MISS

cdef bint is_sentinel(object value):
    return sentinel_check(value)
```

`sentinel_type()` returns the sentinel *type*, not an instance. Create marker
instances with `sentinel_new(name, module=None, repr=None)`. For example,
`sentinel_new("eof", module="mypackage", repr="<eof>")` creates a named marker;
the module is explicit and defaults to `None` rather than being inferred from
the caller. The type object itself is never a match for the checks:
`sentinel_check_exact(sentinel_type())` is `False`.
`sentinel_check` and `sentinel_check_exact` are equivalent: the sentinel type
cannot be subclassed, so there are no subtypes to distinguish. On Python 3.14 the
checks return `False`, while sentinel constructors raise `NotImplementedError`.
