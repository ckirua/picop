#ifndef PICOP_CYMONITORING_SHIM_H
#define PICOP_CYMONITORING_SHIM_H

#include <stdint.h>

/* PEP 670 event ids, in order. `PY_MONITORING_EVENT_BRANCH` (18) is deprecated
   in 3.14+ and is deliberately left out of the scope, so `monitoring_scope`
   enables the 18 live events. Callers still need 19 state slots: the
   interpreter's state array is indexed by event id and reserves slot 18. */
static const uint8_t cypy_monitoring_all_events[18] = {
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17
};

#define PICOP_MONITORING_SCOPE_EVENT_COUNT 18
#define PICOP_MONITORING_STATE_SLOTS 19

#endif
