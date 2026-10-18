# cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False
from cypy.cycodecs cimport codec_known
include "_sink.pxi"

cpdef bint baseline_codec_known(bytes encoding, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    cdef object name = encoding.decode("ascii")
    import encodings as enc_mod
    search = enc_mod.search_function
    for k in range(n):
        tb_sink_ssize(k)
        r = search(name) is not None
        tb_sink_bint(r)
    return r

cpdef bint cypy_codec_known(bytes encoding, Py_ssize_t n):
    cdef Py_ssize_t k
    cdef bint r = False
    cdef const char *enc = encoding
    for k in range(n):
        r = codec_known(enc)
        tb_sink_bint(r)
    return r
