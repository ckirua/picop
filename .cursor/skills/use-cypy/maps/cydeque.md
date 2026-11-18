# cydeque consumer map

Python: `picop.cydeque`; package barrel: `picop`. Cython cimport path: `picop.cydeque` and package `picop`.

| Symbol | Kind | Access | Decision | Expression or use | Contract | Python evidence | Cython evidence |
|---|---|---|---|---|---|---|---|
| <a id="deque_eq"></a>`picop.cydeque.deque_eq` | function | both | candidate | `a == b` | Deque equality uses Python equality semantics; [stub](../../../../src/picop/cydeque.pyi). | not-measured: no per-case consumer comparison recorded. | not-measured: cimport availability is not performance evidence. |
