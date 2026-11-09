"""Codec registry and error-handler helpers wrapping ``PyCodec_*``.

Prefer :mod:`codecs` from Python unless you need C-API registration or lookup
on hot paths. Encoding / error names take ``bytes``, not ``str``. See
:doc:`/user_guide/safety`.
"""

def codec_register(search_function: object) -> int:
    """Register a codec search function (``PyCodec_Register``).

    Notes
    -----
    Returns ``0`` on success; errors raise — do not use the status as a bool.
    """
    ...

def codec_known(encoding: bytes) -> bool:
    """Return True if ``encoding`` is a known codec (``PyCodec_KnownEncoding``).

    Notes
    -----
    ``encoding`` must be ``bytes``, not ``str``. See :doc:`/user_guide/safety`.
    """
    ...

def codec_encoder(encoding: bytes) -> object:
    """Return the encoder for ``encoding`` (``PyCodec_Encoder``).

    Notes
    -----
    ``encoding`` must be ``bytes``, not ``str``.
    """
    ...

def codec_decoder(encoding: bytes) -> object:
    """Return the decoder for ``encoding`` (``PyCodec_Decoder``).

    Notes
    -----
    ``encoding`` must be ``bytes``, not ``str``.
    """
    ...

def codec_incremental_encoder(encoding: bytes, errors: bytes | None = None) -> object:
    """Return an incremental encoder (``PyCodec_IncrementalEncoder``).

    Notes
    -----
    Slower than the plain-Python equivalent ``_inc_enc`` (Tier A 1.02x);
    codec/error-handler bridge for extension authors.

    ``encoding`` / ``errors`` must be ``bytes`` when provided, not ``str``.
    """
    ...

def codec_incremental_decoder(encoding: bytes, errors: bytes | None = None) -> object:
    """Return an incremental decoder (``PyCodec_IncrementalDecoder``).

    Notes
    -----
    Slower than the plain-Python equivalent ``codecs.incremental_decoder(enc)``
    (Tier A 1.03x); codec/error-handler bridge for extension authors.

    ``encoding`` / ``errors`` must be ``bytes`` when provided, not ``str``.
    """
    ...

def codec_stream_reader(encoding: bytes, stream: object, errors: bytes | None = None) -> object:
    """Return a stream reader (``PyCodec_StreamReader``).

    Notes
    -----
    ``encoding`` / ``errors`` must be ``bytes`` when provided, not ``str``.
    """
    ...

def codec_stream_writer(encoding: bytes, stream: object, errors: bytes | None = None) -> object:
    """Return a stream writer (``PyCodec_StreamWriter``).

    Notes
    -----
    ``encoding`` / ``errors`` must be ``bytes`` when provided, not ``str``.
    """
    ...

def codec_register_error(name: bytes, error: object) -> int:
    """Register a codec error callback (``PyCodec_RegisterError``).

    Notes
    -----
    ``name`` must be ``bytes``. Returns ``0`` on success; errors raise — do not
    use the status as a bool.
    """
    ...

def codec_lookup_error(name: bytes) -> object:
    """Lookup a codec error callback (``PyCodec_LookupError``).

    Notes
    -----
    ``name`` must be ``bytes``, not ``str``.
    """
    ...

def codec_strict_errors(exc: object) -> object:
    """Strict error handler (``PyCodec_StrictErrors``).

    Notes
    -----
    Slower than the plain-Python equivalent ``codecs.lookup(enc).decode(b,
    'strict')`` (Tier A 4.12x); codec/error-handler bridge for extension authors.
    """
    ...

def codec_ignore_errors(exc: object) -> object:
    """Ignore error handler (``PyCodec_IgnoreErrors``).

    Notes
    -----
    Slower than the plain-Python equivalent ``codecs.ignore_errors`` (Tier A 1.20x);
    codec/error-handler bridge for extension authors.
    """
    ...

def codec_replace_errors(exc: object) -> object:
    """Replace error handler (``PyCodec_ReplaceErrors``).

    Notes
    -----
    Slower than the plain-Python equivalent ``codecs.replace_errors`` (Tier A
    1.03x); codec/error-handler bridge for extension authors.
    """
    ...

def codec_xmlcharrefreplace_errors(exc: object) -> object:
    """XML charref replace handler."""
    ...

def codec_backslashreplace_errors(exc: object) -> object:
    """Backslash replace handler.

    Notes
    -----
    Slower than the plain-Python equivalent ``codecs.backslashreplace_errors`` (Tier
    A 1.03x); codec/error-handler bridge for extension authors.
    """
    ...

def codec_namereplace_errors(exc: object) -> object:
    """Name replace handler.

    Notes
    -----
    Slower than the plain-Python equivalent ``codecs.namereplace_errors`` (Tier A
    1.03x); codec/error-handler bridge for extension authors.
    """
    ...

def codec_decode(o: object, encoding: bytes, errors: bytes | None = None) -> object:
    """Decode ``o`` with ``encoding`` via ``PyCodec_Decode``.

    Notes
    -----
    Slower than the plain-Python equivalent ``lambda b, e, err: b.decode(e.decode(),
    (err or b'strict').decode())`` (Tier A 1.39x); codec/error-handler bridge for
    extension authors.
    """
    ...

def codec_encode(o: object, encoding: bytes, errors: bytes | None = None) -> object:
    """Encode ``o`` with ``encoding`` via ``PyCodec_Encode``.

    Notes
    -----
    Slower than the plain-Python equivalent ``lambda s, e, err: s.encode(e.decode(),
    (err or b'strict').decode())`` (Tier A 1.20x); codec/error-handler bridge for
    extension authors.
    """
    ...
