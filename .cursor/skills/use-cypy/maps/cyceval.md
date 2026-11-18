# cyceval consumer map

No Python-callable API. Package cimport path is `picop`; defining Cython module path is `picop.cyceval`. These legacy process-wide CPython evaluator helpers are not replacements for ordinary Python expressions.

| Symbol | Kind | Access | Decision | Expression or use | Contract | Python evidence | Cython evidence |
|---|---|---|---|---|---|---|---|
| <a id="eval_init_threads"></a>`picop.cyceval.eval_init_threads` | function | cimport | specialized | No direct replacement: retained Cython cimport for legacy `PyEval_InitThreads()` integration. | On CPython 3.14+ after runtime startup, `PyEval_InitThreads()` is a no-op; process-wide/legacy only. [pxd](../../../../src/picop/cyceval.pxd) | not-applicable: no Python API to compare. | not-measured: no Cython consumer benchmark recorded. |
| <a id="eval_threads_initialized"></a>`picop.cyceval.eval_threads_initialized` | function | cimport | specialized | No direct replacement: retained Cython query for legacy thread-init state. | Always returns True since PyEval_ThreadsInitialized removal; do not infer thread/GIL attachment. [pxd](../../../../src/picop/cyceval.pxd) | not-applicable: no Python API to compare. | not-measured: no Cython consumer benchmark recorded. |
