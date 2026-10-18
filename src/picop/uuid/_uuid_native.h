#ifndef PICOP_UUID_NATIVE_H
#define PICOP_UUID_NATIVE_H
#include <Python.h>
typedef struct {
    unsigned int version;
    /* New reference on success; NULL with an exception on failure. */
    PyObject *(*from_buf)(PyTypeObject *, const unsigned char *);
    /* Borrowed immutable storage, valid while the UUID owner is alive. */
    const unsigned char *(*data)(PyObject *);
    int (*parse)(PyObject *, unsigned char *);
} PicopUUIDAPI;
#define PICOP_UUID_API_VERSION 1
#define PICOP_UUID_CAPSULE "picop.uuid._uuid_native._C_API"
#endif
