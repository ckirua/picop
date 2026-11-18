# `cydescr` consumer map

Python import: `picop.cydescr`; package barrel also exports these functions. Cython cimport from `picop.cydescr`.

| Symbol | Kind | Access | Decision | Expression or use | Contract | Python evidence | Cython evidence |
|---|---|---|---|---|---|---|---|
| <a id="descr_is_data"></a>`picop.cydescr.descr_is_data` | function | both | candidate | `hasattr(type(descr), '__set__') or hasattr(type(descr), '__delete__')` | Descriptor data-ness follows type-level descriptor protocol; custom metaclass behavior may differ from naive instance inspection. [stub](../../../../src/picop/cydescr.pyi) | not-measured: no module tracker/performance result recorded | not-measured: no consumer baseline recorded |
| <a id="descr_name"></a>`picop.cydescr.descr_name` | function | both | specialized | `type(descr).__name__` | Returns CPython descriptor's declared name, not its class name; supports method/member/getset/wrapper descriptor objects. [stub](../../../../src/picop/cydescr.pyi) | not-measured: no comparable standard-library expression recorded | not-measured: no consumer baseline recorded |
| <a id="descr_objclass"></a>`picop.cydescr.descr_objclass` | function | both | specialized | `descr.__objclass__` | Defining type for supported CPython descriptors; arbitrary user objects may lack this attribute or use custom behavior. [stub](../../../../src/picop/cydescr.pyi) | not-measured: no comparable benchmark recorded | not-measured: no consumer baseline recorded |
