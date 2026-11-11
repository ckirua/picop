/* cyfunction_shim.h — version-gated function-watcher event ids.
 *
 * ``PyFunction_EVENT_MODIFY_QUALNAME`` is new in CPython 3.15.  Enum members
 * cannot be probed with ``#ifdef``, so the event id is exposed as a query that
 * returns ``-1`` when the event does not exist in this CPython release.
 */
#ifndef PICOP_CYFUNCTION_SHIM_H
#define PICOP_CYFUNCTION_SHIM_H

#include <Python.h>

static inline int picop_func_event_modify_qualname(void) {
#if PY_VERSION_HEX >= 0x030F0000
    return PyFunction_EVENT_MODIFY_QUALNAME;
#else
    return -1;
#endif
}

#endif /* PICOP_CYFUNCTION_SHIM_H */
