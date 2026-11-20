# cymarshal consumer map

Python: `picop.cymarshal`; package barrel: `picop`. Cython cimports: `picop.cymarshal` and package `picop`.

| Symbol | Kind | Access | Decision | Expression or use | Contract | Python evidence | Cython evidence |
|---|---|---|---|---|---|---|---|
| <a id="marshal_dumps"></a>`picop.cymarshal.marshal_dumps` | function | both | candidate | `marshal.dumps(value, version)` | Serialization format and supported values follow interpreter marshal version; not a stable interchange format. [stub](../../../../src/picop/cymarshal.pyi) | not-measured: no per-case consumer comparison recorded. | not-measured: cimport availability is not performance evidence. |
| <a id="marshal_loads"></a>`picop.cymarshal.marshal_loads` | function | both | candidate | `marshal.loads(data)` | Accepts bytes; untrusted input is unsafe and version compatibility is not guaranteed. [stub](../../../../src/picop/cymarshal.pyi) | not-measured: no per-case consumer comparison recorded. | not-measured: cimport availability is not performance evidence. |
