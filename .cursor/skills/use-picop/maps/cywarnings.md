# cywarnings consumer map

Python: `picop.cywarnings`; package barrel: `picop`. Cython cimports: `picop.cywarnings` and package `picop`.

| Symbol | Kind | Access | Decision | Expression or use | Contract | Python evidence | Cython evidence |
|---|---|---|---|---|---|---|---|
| <a id="warn_ex"></a>`picop.cywarnings.warn_ex` | function | both | candidate | `warnings.warn(message, category, stacklevel=stacklevel)` | Calls CPython warning machinery; filter behavior and warning registry remain observable. [stub](../../../../src/picop/cywarnings.pyi) | recorded: case-dependent; Tier A CPython 3.14.7, ignored warning: 1.04x vs `warnings.warn`, but 0.85x vs `warnings.warn(stacklevel=2)`; mean 0.94x. [tracker](../../../../docs/modules/065_cywarnings.md) | recorded: Tier B CPython 3.14.7 Linux, typed Cython loop `warn_ex` 1.02x vs baseline; [tracker](../../../../docs/modules/065_cywarnings.md). |
| <a id="warn_explicit"></a>`picop.cywarnings.warn_explicit` | function | both | specialized | `warnings.warn_explicit(message, category, filename, lineno, module=module, registry=registry)` | Explicit module/registry/filename/line alter warning bookkeeping; [stub](../../../../src/picop/cywarnings.pyi). | not-measured: no consumer comparison recorded. | not-measured: no Cython consumer benchmark recorded. |
| <a id="warnings_module"></a>`picop.cywarnings.warnings_module` | function | both | specialized | `sys.modules.get("warnings")` | Returns warnings module or None; lookup behavior depends on module initialization. [stub](../../../../src/picop/cywarnings.pyi) | not-measured: no consumer comparison recorded. | not-measured: cimport availability is not performance evidence. |
