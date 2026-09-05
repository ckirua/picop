# cycodecs.pxd
# Codec registry helpers. Public docs in ``cycodecs.pyi``.

cdef extern from "Python.h":
    int PyCodec_Register(object search_function) except -1
    int PyCodec_KnownEncoding(const char *encoding) noexcept
    object PyCodec_Encode(object o, const char *encoding, const char *errors)
    object PyCodec_Decode(object o, const char *encoding, const char *errors)
    object PyCodec_Encoder(const char *encoding)
    object PyCodec_Decoder(const char *encoding)
    object PyCodec_IncrementalEncoder(const char *encoding, const char *errors)
    object PyCodec_IncrementalDecoder(const char *encoding, const char *errors)
    object PyCodec_StreamReader(const char *encoding, object stream, const char *errors)
    object PyCodec_StreamWriter(const char *encoding, object stream, const char *errors)
    int PyCodec_RegisterError(const char *name, object error) except -1
    object PyCodec_LookupError(const char *name)
    object PyCodec_StrictErrors(object exc)
    object PyCodec_IgnoreErrors(object exc)
    object PyCodec_ReplaceErrors(object exc)
    object PyCodec_XMLCharRefReplaceErrors(object exc)
    object PyCodec_BackslashReplaceErrors(object exc)
    object PyCodec_NameReplaceErrors(object exc)


cpdef inline int codec_register(object search_function) except -1:
    return PyCodec_Register(search_function)


cpdef inline bint codec_known(const char *encoding) noexcept:
    return PyCodec_KnownEncoding(encoding) != 0


cpdef inline object codec_encode(object o, const char *encoding, const char *errors=NULL):
    return PyCodec_Encode(o, encoding, errors)


cpdef inline object codec_decode(object o, const char *encoding, const char *errors=NULL):
    return PyCodec_Decode(o, encoding, errors)


cpdef inline object codec_encoder(const char *encoding):
    return PyCodec_Encoder(encoding)


cpdef inline object codec_decoder(const char *encoding):
    return PyCodec_Decoder(encoding)


cpdef inline object codec_incremental_encoder(const char *encoding, const char *errors=NULL):
    return PyCodec_IncrementalEncoder(encoding, errors)


cpdef inline object codec_incremental_decoder(const char *encoding, const char *errors=NULL):
    return PyCodec_IncrementalDecoder(encoding, errors)


cpdef inline object codec_stream_reader(const char *encoding, object stream, const char *errors=NULL):
    return PyCodec_StreamReader(encoding, stream, errors)


cpdef inline object codec_stream_writer(const char *encoding, object stream, const char *errors=NULL):
    return PyCodec_StreamWriter(encoding, stream, errors)


cpdef inline int codec_register_error(const char *name, object error) except -1:
    return PyCodec_RegisterError(name, error)


cpdef inline object codec_lookup_error(const char *name):
    return PyCodec_LookupError(name)


cpdef inline object codec_strict_errors(object exc):
    return PyCodec_StrictErrors(exc)


cpdef inline object codec_ignore_errors(object exc):
    return PyCodec_IgnoreErrors(exc)


cpdef inline object codec_replace_errors(object exc):
    return PyCodec_ReplaceErrors(exc)


cpdef inline object codec_xmlcharrefreplace_errors(object exc):
    return PyCodec_XMLCharRefReplaceErrors(exc)


cpdef inline object codec_backslashreplace_errors(object exc):
    return PyCodec_BackslashReplaceErrors(exc)


cpdef inline object codec_namereplace_errors(object exc):
    return PyCodec_NameReplaceErrors(exc)
