# cylock consumer map

No Python-callable API. Package cimport path is `picop`; defining module is `picop.cylock`. Use these low-level synchronization APIs only in supported native Cython critical-section code.

| Symbol | Kind | Access | Decision | Expression or use | Contract | Python evidence | Cython evidence |
|---|---|---|---|---|---|---|---|
| <a id="PyMutex"></a>`picop.cylock.PyMutex` | type | cimport | companion | Declare a typed `PyMutex` for native synchronization. | CPython mutex type; availability/semantics are runtime-version-specific. [declaration](../../../../src/picop/cylock.pxd) | not-applicable: C-only type. | not-measured: no consumer benchmark recorded. |
| <a id="mutex_init"></a>`picop.cylock.mutex_init` | function | cimport | specialized | Initialize a `PyMutex` before use. | Native lock lifecycle; must initialize exactly as API requires and not race initialization. [declaration](../../../../src/picop/cylock.pxd) | not-applicable: no Python-callable API. | not-measured: no Cython consumer benchmark recorded. |
| <a id="mutex_is_locked"></a>`picop.cylock.mutex_is_locked` | function | cimport | specialized | Query lock state for diagnostics/coordination. | Observation is not a synchronization guarantee; lock may change immediately after query. [declaration](../../../../src/picop/cylock.pxd) | not-applicable: no Python-callable API. | not-measured: no Cython consumer benchmark recorded. |
| <a id="mutex_lock"></a>`picop.cylock.mutex_lock` | function | cimport | specialized | Acquire a typed `PyMutex` around a protected native operation. | Must pair with unlock; concurrency and interpreter lock rules apply. [declaration](../../../../src/picop/cylock.pxd) | not-applicable: no Python-callable API. | not-measured: no Cython consumer benchmark recorded. |
| <a id="mutex_unlock"></a>`picop.cylock.mutex_unlock` | function | cimport | specialized | Release a previously acquired typed `PyMutex`. | Only release a lock held by the current control flow as required; pair every acquire. [declaration](../../../../src/picop/cylock.pxd) | not-applicable: no Python-callable API. | not-measured: no Cython consumer benchmark recorded. |
