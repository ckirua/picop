# cygetargs consumer map

Cython cimport: `picop.cygetargs`. C varargs argument-parsing C-API for extension call sites; no Python wrapper.

| Symbol | Kind | Access | Decision | Expression or use | Contract | Python evidence | Cython evidence |
|---|---|---|---|---|---|---|---|
| <a id="PyArg_ParseTuple"></a>`picop.cygetargs.PyArg_ParseTuple` | function | cimport | specialized | Parse a Cython `args` tuple using a C-API format string and typed output pointers | Varargs; GIL required; success owns references according to the format; parse failure sets exception. [pxd](../../../../src/picop/cygetargs.pxd) | not-applicable: use normal Python argument binding. | not-applicable: cimport-only ABI call; no consumer timing. [tracker](../../../../docs/modules/038_cygetargs.md) |
| <a id="PyArg_ParseTupleAndKeywords"></a>`picop.cygetargs.PyArg_ParseTupleAndKeywords` | function | cimport | specialized | Parse tuple plus keyword dict at a Cython boundary | Varargs format, keyword-name array and typed outputs; GIL required; successful object outputs are owned refs. [pxd](../../../../src/picop/cygetargs.pxd) | not-applicable: use Python function argument binding. | not-applicable: no public wrapper/benchmark; [tracker](../../../../docs/modules/038_cygetargs.md) |
| <a id="PyArg_UnpackTuple"></a>`picop.cygetargs.PyArg_UnpackTuple` | function | cimport | specialized | Unpack positional tuple into Cython typed output pointers with min/max arity | Varargs; GIL required; failure sets exception. [pxd](../../../../src/picop/cygetargs.pxd) | not-applicable: use normal tuple unpacking or function parameters. | not-applicable: cimport-only; [tracker](../../../../docs/modules/038_cygetargs.md) |
