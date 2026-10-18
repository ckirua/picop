/*
 * Copyright (C) 2016-present the asyncpg authors and contributors.
 * UUID text parsing is adapted from the Apache-2.0-licensed implementation;
 * see NOTICE and LICENSES/Apache-2.0.txt for attribution and license terms.
 */
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdint.h>
#include <string.h>

#include "_uuid_native.h"

typedef PyObject *(*uuid_integer_from_bytes_func)(const unsigned char bytes[16]);

static PyObject *
uuid_integer_from_native_bytes(const unsigned char bytes[16])
{
    return PyLong_FromUnsignedNativeBytes(
        bytes, 16, Py_ASNATIVEBYTES_BIG_ENDIAN);
}

static uint64_t
read_be64(const unsigned char *bytes)
{
    return ((uint64_t)bytes[0] << 56) | ((uint64_t)bytes[1] << 48) |
           ((uint64_t)bytes[2] << 40) | ((uint64_t)bytes[3] << 32) |
           ((uint64_t)bytes[4] << 24) | ((uint64_t)bytes[5] << 16) |
           ((uint64_t)bytes[6] << 8) | (uint64_t)bytes[7];
}

static PyObject *
uuid_integer_from_30bit_digits(const unsigned char bytes[16])
{
    void *storage;
    PyLongWriter *writer = PyLongWriter_Create(0, 5, &storage);
    uint32_t *digits;
    uint64_t high, low;

    if (writer == NULL) {
        return NULL;
    }
    /* The writer owns the eventual int: no temporary bigint or digit copy.
     * Fill the public 30-bit layout selected at module initialization. */
    digits = storage;
    high = read_be64(bytes);
    low = read_be64(bytes + 8);
    digits[0] = (uint32_t)(low & UINT64_C(0x3fffffff));
    digits[1] = (uint32_t)((low >> 30) & UINT64_C(0x3fffffff));
    digits[2] = (uint32_t)(((low >> 60) | (high << 4)) &
                           UINT64_C(0x3fffffff));
    digits[3] = (uint32_t)((high >> 26) & UINT64_C(0x3fffffff));
    digits[4] = (uint32_t)(high >> 56);
    return PyLongWriter_Finish(writer);
}


typedef struct {
    unsigned char bytes[16];
    unsigned char initial_call;
} UUIDData;

typedef struct {
    PyObject *base_int;
    PyObject *base_is_safe;
    PyObject *safe_unknown;
    PyObject *capsule;
    descrsetfunc base_int_set;
    descrsetfunc base_is_safe_set;
    uuid_integer_from_bytes_func integer_from_bytes;
} UUIDState;

static UUIDData *
uuid_data(PyObject *obj)
{
    return (UUIDData *)PyObject_GetTypeData(obj, Py_TYPE(obj));
}

static UUIDState *
uuid_state(PyTypeObject *type)
{
    return (UUIDState *)PyType_GetModuleState(type);
}

static int
parse_value(PyObject *input, unsigned char out[16])
{
    const unsigned char *text;
    Py_ssize_t length;
    Py_ssize_t i;
    int half_byte = -1;
    int byte_count = 0;

    if (PyBytes_Check(input)) {
        char *bytes;

        if (PyBytes_AsStringAndSize(input, &bytes, &length) < 0) {
            return -1;
        }
        if (length != 16) {
            PyErr_Format(PyExc_ValueError,
                         "16 bytes were expected, got %zd", length);
            return -1;
        }
        memcpy(out, bytes, 16);
        return 0;
    }

    if (!PyUnicode_Check(input)) {
        PyErr_Format(PyExc_TypeError,
                     "a bytes or str object expected, got %R", input);
        return -1;
    }

    text = (const unsigned char *)PyUnicode_AsUTF8AndSize(input, &length);
    if (text == NULL) {
        return -1;
    }
    if (length < 32 || length > 36) {
        PyErr_Format(PyExc_ValueError,
                     "invalid UUID %R: length must be between 32..36 characters, got %zd",
                     input, length);
        return -1;
    }

    for (i = 0; i < length; i++) {
        unsigned char ch = text[i];
        int digit;

        if (ch == '-') {
            continue;
        }
        if (ch >= '0' && ch <= '9') {
            digit = ch - '0';
        }
        else if (ch >= 'a' && ch <= 'f') {
            digit = ch - 'a' + 10;
        }
        else if (ch >= 'A' && ch <= 'F') {
            digit = ch - 'A' + 10;
        }
        else {
            if (ch >= 0x20 && ch <= 0x7e) {
                PyObject *character = PyUnicode_FromOrdinal(ch);
                if (character == NULL) {
                    return -1;
                }
                PyErr_Format(PyExc_ValueError,
                             "invalid UUID %R: unexpected character %R",
                             input, character);
                Py_DECREF(character);
            }
            else {
                PyErr_Format(PyExc_ValueError,
                             "invalid UUID %R: unexpected character", input);
            }
            return -1;
        }

        /* Match the original parser: reject any digit beyond 16 bytes before
         * writing another nibble, including an odd 33rd digit. */
        if (byte_count == 16) {
            PyErr_Format(PyExc_ValueError,
                         "invalid UUID %R: decodes to more than 16 bytes",
                         input);
            return -1;
        }
        if (half_byte < 0) {
            half_byte = digit << 4;
        }
        else {
            out[byte_count++] = (unsigned char)(half_byte | digit);
            half_byte = -1;
        }
    }

    if (byte_count != 16) {
        PyErr_Format(PyExc_ValueError,
                     "invalid UUID %R: decodes to less than 16 bytes", input);
        return -1;
    }
    return 0;
}

static int
initialize_base_slots(PyObject *self, const unsigned char bytes[16])
{
    UUIDState *state = uuid_state(Py_TYPE(self));
    PyObject *integer;

    integer = state->integer_from_bytes(bytes);
    if (integer == NULL) {
        return -1;
    }

    if (state->base_int_set(state->base_int, self, integer) < 0) {
        Py_DECREF(integer);
        return -1;
    }
    Py_DECREF(integer);

    if (state->base_is_safe_set(state->base_is_safe, self,
                                state->safe_unknown) < 0) {
        return -1;
    }

    memcpy(uuid_data(self)->bytes, bytes, 16);
    return 0;
}

static PyObject *
uuid_new(PyTypeObject *type, PyObject *args, PyObject *kwargs)
{
    static char *keywords[] = {"inp", NULL};
    PyObject *input;
    PyObject *self;
    unsigned char bytes[16];

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "O:UUID", keywords,
                                     &input)) {
        return NULL;
    }
    if (parse_value(input, bytes) < 0) {
        return NULL;
    }

    self = type->tp_alloc(type, 0);
    if (self == NULL) {
        return NULL;
    }
    uuid_data(self)->initial_call = 1;
    if (initialize_base_slots(self, bytes) < 0) {
        Py_DECREF(self);
        return NULL;
    }
    return self;
}

static int
uuid_init(PyObject *self, PyObject *args, PyObject *kwargs)
{
    UUIDData *data = uuid_data(self);
    int status = 0;

    (void)args;
    (void)kwargs;

    Py_BEGIN_CRITICAL_SECTION(self);
    if (data->initial_call) {
        data->initial_call = 0;
    }
    else {
        PyErr_SetString(PyExc_TypeError, "UUID objects are immutable");
        status = -1;
    }
    Py_END_CRITICAL_SECTION();

    return status;
}

static PyObject *
uuid_from_buffer(PyTypeObject *type, const unsigned char bytes[16])
{
    PyObject *self = type->tp_alloc(type, 0);

    if (self == NULL) {
        return NULL;
    }
    uuid_data(self)->initial_call = 0;
    if (initialize_base_slots(self, bytes) < 0) {
        Py_DECREF(self);
        return NULL;
    }
    return self;
}

static PyObject *
api_from_buffer(PyTypeObject *type, const unsigned char *bytes)
{
    return uuid_from_buffer(type, bytes);
}

static const unsigned char *
api_data(PyObject *obj)
{
    return uuid_data(obj)->bytes;
}

static int
api_parse(PyObject *obj, unsigned char *out)
{
    return parse_value(obj, out);
}

static PyType_Slot uuid_slots[] = {
    {Py_tp_new, uuid_new},
    {Py_tp_init, uuid_init},
    {0, NULL}
};

static PyType_Spec uuid_spec = {
    .name = "picop.uuid._uuid.UUID",
    .basicsize = -(int)sizeof(UUIDData),
    .itemsize = 0,
    .flags = Py_TPFLAGS_DEFAULT,
    .slots = uuid_slots
};

static int
native_exec(PyObject *module)
{
    UUIDState *state = (UUIDState *)PyModule_GetState(module);
    PyObject *uuid_module = NULL;
    PyObject *base = NULL;
    PyObject *safe_enum = NULL;
    PyObject *type = NULL;
    PyObject *bases = NULL;
    PyObject *capsule = NULL;

    {
        const PyLongLayout *layout = PyLong_GetNativeLayout();
        const uint16_t marker = 1;
        int host_endianness =
            (*(const unsigned char *)&marker == 1) ? -1 : 1;

        state->integer_from_bytes = uuid_integer_from_native_bytes;
        if (layout->bits_per_digit == 30 &&
            layout->digit_size == sizeof(uint32_t) &&
            layout->digits_order == -1 &&
            layout->digit_endianness == host_endianness) {
            state->integer_from_bytes = uuid_integer_from_30bit_digits;
        }
    }

    uuid_module = PyImport_ImportModule("uuid");
    if (uuid_module == NULL) {
        goto error;
    }
    base = PyObject_GetAttrString(uuid_module, "UUID");
    if (base == NULL) {
        goto error;
    }

    state->base_int = PyObject_GetAttrString(base, "int");
    if (state->base_int == NULL) {
        goto error;
    }
    state->base_is_safe = PyObject_GetAttrString(base, "is_safe");
    if (state->base_is_safe == NULL) {
        goto error;
    }
    state->base_int_set = (descrsetfunc)PyType_GetSlot(
        Py_TYPE(state->base_int), Py_tp_descr_set);
    state->base_is_safe_set = (descrsetfunc)PyType_GetSlot(
        Py_TYPE(state->base_is_safe), Py_tp_descr_set);
    if (state->base_int_set == NULL || state->base_is_safe_set == NULL) {
        PyErr_SetString(PyExc_RuntimeError,
                        "stdlib UUID base descriptors are not writable");
        goto error;
    }

    safe_enum = PyObject_GetAttrString(uuid_module, "SafeUUID");
    if (safe_enum == NULL) {
        goto error;
    }
    state->safe_unknown = PyObject_GetAttrString(safe_enum, "unknown");
    if (state->safe_unknown == NULL) {
        goto error;
    }

    bases = PyTuple_Pack(1, base);
    if (bases == NULL) {
        goto error;
    }
    type = PyType_FromModuleAndSpec(module, &uuid_spec, bases);
    if (type == NULL) {
        goto error;
    }
    if (PyModule_AddObjectRef(module, "UUID", type) < 0) {
        goto error;
    }

    {
        static const PicopUUIDAPI api = {
            PICOP_UUID_API_VERSION,
            api_from_buffer,
            api_data,
            api_parse
        };
        capsule = PyCapsule_New((void *)&api, PICOP_UUID_CAPSULE, NULL);
        if (capsule == NULL) {
            goto error;
        }
        state->capsule = Py_NewRef(capsule);
        if (PyModule_AddObjectRef(module, "_C_API", capsule) < 0) {
            goto error;
        }
    }

    Py_DECREF(capsule);
    Py_DECREF(type);
    Py_DECREF(bases);
    Py_DECREF(safe_enum);
    Py_DECREF(base);
    Py_DECREF(uuid_module);
    return 0;

error:
    Py_XDECREF(capsule);
    Py_XDECREF(type);
    Py_XDECREF(bases);
    Py_XDECREF(safe_enum);
    Py_XDECREF(base);
    Py_XDECREF(uuid_module);
    return -1;
}

static int
native_traverse(PyObject *module, visitproc visit, void *arg)
{
    UUIDState *state = (UUIDState *)PyModule_GetState(module);
    if (state == NULL) {
        return 0;
    }

    Py_VISIT(state->base_int);
    Py_VISIT(state->base_is_safe);
    Py_VISIT(state->safe_unknown);
    Py_VISIT(state->capsule);
    return 0;
}

static int
native_clear(PyObject *module)
{
    UUIDState *state = (UUIDState *)PyModule_GetState(module);
    if (state == NULL) {
        return 0;
    }

    Py_CLEAR(state->base_int);
    Py_CLEAR(state->base_is_safe);
    Py_CLEAR(state->safe_unknown);
    Py_CLEAR(state->capsule);
    return 0;
}

static void
native_free(void *module)
{
    /* Failed execution can deallocate the module without a GC clear pass. */
    (void)native_clear((PyObject *)module);
}

static PyModuleDef_Slot native_slots[] = {
    {Py_mod_exec, native_exec},
    {Py_mod_gil, Py_MOD_GIL_NOT_USED},
    {0, NULL}
};

static struct PyModuleDef native_module = {
    PyModuleDef_HEAD_INIT,
    "_uuid_native",
    NULL,
    sizeof(UUIDState),
    NULL,
    native_slots,
    native_traverse,
    native_clear,
    native_free
};

PyMODINIT_FUNC
PyInit__uuid_native(void)
{
    return PyModuleDef_Init(&native_module);
}
