# cycall

Python import `from picop.cycall import call_noargs, call_onearg, call_twoargs`; package barrel aliases are available. These three are Python-only. Raw Cython vectorcall helpers are not part of this catalog surface. See [stub](../../../../src/picop/cycall.pyi), [pxd](../../../../src/picop/cycall.pxd), [implementation](../../../../src/picop/cycall.pyx).

| Symbol | Kind | Access | Decision | Expression or use | Contract | Python evidence | Cython evidence |
|---|---|---|---|---|---|---|---|
| <a id="call_noargs"></a>`picop.cycall.call_noargs` | function | python | candidate | `callable()` | Calls object with no arguments; requires callable and preserves its exceptions/return value. See [stub](../../../../src/picop/cycall.pyi). | not-measured: no recorded winning case; harness availability alone is not evidence. | not-applicable: not exported for Cython cimport in source manifest. |
| <a id="call_onearg"></a>`picop.cycall.call_onearg` | function | python | candidate | `callable(arg)` | One positional argument; preserves callable behavior and exceptions. See [stub](../../../../src/picop/cycall.pyi). | not-measured: no recorded winning case. | not-applicable: not exported for Cython cimport in source manifest. |
| <a id="call_twoargs"></a>`picop.cycall.call_twoargs` | function | python | candidate | `callable(arg0, arg1)` | Two positional arguments; uses vectorcall; preserves Python call semantics. See [stub](../../../../src/picop/cycall.pyi). | not-measured: no recorded winning case. | not-applicable: not exported for Cython cimport in source manifest. |
