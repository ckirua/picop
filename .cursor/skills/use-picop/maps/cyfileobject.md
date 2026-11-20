# cyfileobject consumer map

Python: `picop.cyfileobject`; package barrel: `picop`. Cython cimports: `picop.cyfileobject` and package `picop`.

| Symbol | Kind | Access | Decision | Expression or use | Contract | Python evidence | Cython evidence |
|---|---|---|---|---|---|---|---|
| <a id="file_from_fd"></a>`picop.cyfileobject.file_from_fd` | function | both | specialized | `open(fd, mode, buffering=..., encoding=..., errors=..., newline=..., closefd=...)` | CPython file construction from descriptor; name/mode are bytes and closefd controls descriptor ownership. [stub](../../../../src/picop/cyfileobject.pyi) | not-measured: no consumer comparison recorded. | not-measured: cimport availability is not performance evidence. |
| <a id="file_getline"></a>`picop.cyfileobject.file_getline` | function | both | candidate | `file.readline(n)` | Reads from file-like object; exact accepted object/error behavior is CPython API-specific. [stub](../../../../src/picop/cyfileobject.pyi) | not-measured: no per-case comparison recorded. | not-measured: no Cython consumer benchmark recorded. |
| <a id="file_write_object"></a>`picop.cyfileobject.file_write_object` | function | both | specialized | `file.write(obj)` | CPython file write API returns status integer rather than Python write's byte count; flags influence API behavior. [stub](../../../../src/picop/cyfileobject.pyi) | not-measured: no consumer comparison recorded. | not-measured: no Cython consumer benchmark recorded. |
| <a id="file_write_cstr"></a>`picop.cyfileobject.file_write_cstr` | function | both | specialized | `file.write(data.decode())` only where decoding is intended | Takes bytes C-string payload and file object; no general bytes/text equivalence; [stub](../../../../src/picop/cyfileobject.pyi). | not-measured: no consumer comparison recorded. | not-measured: cimport availability is not performance evidence. |
