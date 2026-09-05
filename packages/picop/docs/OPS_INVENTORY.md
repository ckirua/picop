# Public ops inventory

Checklist for every public barrel helper imported from `cy*` in
[`src/cypy/__init__.py`](../src/cypy/__init__.py).

Status vocabulary:

| Status | Meaning |
|--------|---------|
| `pending` | No timed `session.compare` yet |
| `tierA` | Timed Tier A vs plain Python |
| `tierB` | Timed Tier B (cdef vs typed Cython); Tier A also present |
| `n/a (reason)` | Explicit skip — no stable baseline / side effects |

Gate: [`scripts/ops_inventory_coverage.py`](../scripts/ops_inventory_coverage.py)
(`--strict` requires zero `pending`).
Related: [`EQ_INVENTORY.md`](EQ_INVENTORY.md) · [`EQ_INVENTORY_TIERB.md`](EQ_INVENTORY_TIERB.md)
· [`OPS_INVENTORY_TIERB.md`](OPS_INVENTORY_TIERB.md).

## Summary

| Metric | Count |
|--------|------:|
| Public barrel helpers | 438 |
| `tierA` | 308 |
| `tierB` | 119 |
| `pending` | 0 |
| `n/a` | 11 |

## Checklist

| Helper | Status | Notes |
|--------|--------|-------|
| `ansi_bg8` | tierB | Tier A+B compare labels present |
| `ansi_bold` | tierB | Tier A+B compare labels present |
| `ansi_fg256` | tierA | Tier A `session.compare` present |
| `ansi_fg8` | tierB | Tier A+B compare labels present |
| `ansi_reset` | tierA | Tier A `session.compare` present |
| `ansi_strip` | tierA | Tier A `session.compare` present |
| `ansi_wrap` | tierA | Tier A `session.compare` present |
| `array_check` | tierB | Tier A+B compare labels present |
| `array_check_exact` | tierA | Tier A `session.compare` present |
| `array_clone` | tierA | Tier A `session.compare` present |
| `array_copy` | tierA | Tier A `session.compare` present |
| `array_eq` | tierB | Tier A+B compare labels present |
| `array_extend` | tierA | Tier A `session.compare` present |
| `array_len` | tierB | Tier A+B compare labels present |
| `array_ne` | tierB | Tier A+B compare labels present |
| `array_resize` | tierA | Tier A `session.compare` present |
| `array_resize_smart` | tierA | Tier A `session.compare` present |
| `array_zero` | tierA | Tier A `session.compare` present |
| `bool_check` | tierB | Tier A+B compare labels present |
| `bool_eq` | tierB | Tier A+B compare labels present |
| `bool_false` | tierA | Tier A `session.compare` present |
| `bool_from_long` | tierA | Tier A `session.compare` present |
| `bool_true` | tierA | Tier A `session.compare` present |
| `buf_check` | tierB | Tier A+B compare labels present |
| `buf_copy_data` | tierA | Tier A `session.compare` present |
| `buf_eq` | tierB | Tier A+B compare labels present |
| `bytearray_check` | tierB | Tier A+B compare labels present |
| `bytearray_check_exact` | tierB | Tier A+B compare labels present |
| `bytearray_concat` | tierA | Tier A `session.compare` present |
| `bytearray_contains` | tierB | Tier A+B compare labels present |
| `bytearray_eq` | tierB | Tier A+B compare labels present |
| `bytearray_from_object` | tierA | Tier A `session.compare` present |
| `bytearray_len` | tierB | Tier A+B compare labels present |
| `bytearray_ne` | tierB | Tier A+B compare labels present |
| `bytearray_resize` | tierA | Tier A `session.compare` present |
| `bytearray_size` | tierA | Tier A `session.compare` present |
| `bytes_bytearray_eq` | tierB | Tier A+B compare labels present |
| `bytes_check` | tierB | Tier A+B compare labels present |
| `bytes_check_exact` | tierB | Tier A+B compare labels present |
| `bytes_contains` | tierB | Tier A+B compare labels present |
| `bytes_endswith` | tierB | Tier A+B compare labels present |
| `bytes_eq` | tierB | Tier A+B compare labels present |
| `bytes_from_object` | tierA | Tier A `session.compare` present |
| `bytes_len` | tierB | Tier A+B compare labels present |
| `bytes_ne` | tierB | Tier A+B compare labels present |
| `bytes_size` | tierA | Tier A `session.compare` present |
| `bytes_startswith` | tierB | Tier A+B compare labels present |
| `calliter_check` | tierA | Tier A `session.compare` present |
| `calliter_new` | tierA | Tier A `session.compare` present |
| `capsule_check_exact` | tierB | Tier A+B compare labels present |
| `capsule_eq` | tierB | Tier A+B compare labels present |
| `capsule_is_valid` | tierA | Tier A `session.compare` present |
| `cell_check` | tierB | Tier A+B compare labels present |
| `cell_eq` | tierB | Tier A+B compare labels present |
| `cell_get` | tierA | Tier A `session.compare` present |
| `cell_new` | tierA | Tier A `session.compare` present |
| `cell_set` | tierA | Tier A `session.compare` present |
| `codec_backslashreplace_errors` | tierA | Tier A `session.compare` present |
| `codec_decode` | tierA | Tier A `session.compare` present |
| `codec_decoder` | tierA | Tier A `session.compare` present |
| `codec_encode` | tierA | Tier A `session.compare` present |
| `codec_encoder` | tierA | Tier A `session.compare` present |
| `codec_ignore_errors` | tierA | Tier A `session.compare` present |
| `codec_incremental_decoder` | tierA | Tier A `session.compare` present |
| `codec_incremental_encoder` | tierA | Tier A `session.compare` present |
| `codec_known` | tierB | Tier A+B compare labels present |
| `codec_lookup_error` | tierA | Tier A `session.compare` present |
| `codec_namereplace_errors` | tierA | Tier A `session.compare` present |
| `codec_register` | n/a (global codec registry mutation) | explicit skip |
| `codec_register_error` | n/a (global error-handler registry mutation) | explicit skip |
| `codec_replace_errors` | tierA | Tier A `session.compare` present |
| `codec_stream_reader` | tierA | Tier A `session.compare` present |
| `codec_stream_writer` | tierA | Tier A `session.compare` present |
| `codec_strict_errors` | tierA | Tier A `session.compare` present |
| `codec_xmlcharrefreplace_errors` | tierA | Tier A `session.compare` present |
| `complex_check` | tierB | Tier A+B compare labels present |
| `complex_check_exact` | tierA | Tier A `session.compare` present |
| `complex_eq` | tierB | Tier A+B compare labels present |
| `complex_from_doubles` | tierA | Tier A `session.compare` present |
| `complex_imag_as_double` | tierA | Tier A `session.compare` present |
| `complex_real_as_double` | tierA | Tier A `session.compare` present |
| `context_eq` | tierB | Tier A+B compare labels present |
| `conv_cstr_to_double` | tierB | Tier A+B compare labels present |
| `conv_stricmp` | tierB | Tier A+B compare labels present |
| `conv_strnicmp` | tierA | Tier A `session.compare` present |
| `ctx_check_exact` | tierB | Tier A+B compare labels present |
| `ctx_copy` | tierA | Tier A `session.compare` present |
| `ctx_copy_current` | tierA | Tier A `session.compare` present |
| `ctx_enter` | n/a (Context stack mutation; no fair tight loop) | explicit skip |
| `ctx_exit` | n/a (Context stack mutation; no fair tight loop) | explicit skip |
| `ctx_new` | tierA | Tier A `session.compare` present |
| `ctxtoken_check_exact` | tierA | Tier A `session.compare` present |
| `ctxvar_check_exact` | tierA | Tier A `session.compare` present |
| `ctxvar_new` | tierA | Tier A `session.compare` present |
| `ctxvar_reset` | tierA | Tier A `session.compare` present |
| `ctxvar_set` | tierA | Tier A `session.compare` present |
| `deque_eq` | tierB | Tier A+B compare labels present |
| `descr_is_data` | tierB | Tier A+B compare labels present |
| `dict_check` | tierB | Tier A+B compare labels present |
| `dict_check_exact` | tierA | Tier A `session.compare` present |
| `dict_clear` | tierA | Tier A `session.compare` present |
| `dict_contains` | tierB | Tier A+B compare labels present |
| `dict_copy` | tierA | Tier A `session.compare` present |
| `dict_del` | tierA | Tier A `session.compare` present |
| `dict_eq` | tierB | Tier A+B compare labels present |
| `dict_get` | tierB | Tier A+B compare labels present |
| `dict_get_ref` | tierA | Tier A `session.compare` present |
| `dict_get_with_error` | tierA | Tier A `session.compare` present |
| `dict_len` | tierB | Tier A+B compare labels present |
| `dict_merge` | tierA | Tier A `session.compare` present |
| `dict_merge_from_seq2` | tierA | Tier A `session.compare` present |
| `dict_new` | tierA | Tier A `session.compare` present |
| `dict_pop` | tierA | Tier A `session.compare` present |
| `dict_proxy` | tierA | Tier A `session.compare` present |
| `dict_set` | tierA | Tier A `session.compare` present |
| `dict_setdefault` | tierA | Tier A `session.compare` present |
| `dict_setdefault_ref` | tierA | Tier A `session.compare` present |
| `dict_size` | tierA | Tier A `session.compare` present |
| `dict_update` | tierA | Tier A `session.compare` present |
| `dt_date_check` | tierB | Tier A+B compare labels present |
| `dt_date_check_exact` | tierA | Tier A `session.compare` present |
| `dt_date_day` | tierA | Tier A `session.compare` present |
| `dt_date_eq` | tierB | Tier A+B compare labels present |
| `dt_date_month` | tierA | Tier A `session.compare` present |
| `dt_date_new` | tierA | Tier A `session.compare` present |
| `dt_date_year` | tierA | Tier A `session.compare` present |
| `dt_datetime_check` | tierA | Tier A `session.compare` present |
| `dt_datetime_check_exact` | tierA | Tier A `session.compare` present |
| `dt_datetime_day` | tierA | Tier A `session.compare` present |
| `dt_datetime_eq` | tierB | Tier A+B compare labels present |
| `dt_datetime_hour` | tierA | Tier A `session.compare` present |
| `dt_datetime_microsecond` | tierA | Tier A `session.compare` present |
| `dt_datetime_minute` | tierA | Tier A `session.compare` present |
| `dt_datetime_month` | tierA | Tier A `session.compare` present |
| `dt_datetime_new` | tierA | Tier A `session.compare` present |
| `dt_datetime_second` | tierA | Tier A `session.compare` present |
| `dt_datetime_year` | tierA | Tier A `session.compare` present |
| `dt_time_check` | tierA | Tier A `session.compare` present |
| `dt_time_check_exact` | tierA | Tier A `session.compare` present |
| `dt_time_eq` | tierB | Tier A+B compare labels present |
| `dt_time_hour` | tierA | Tier A `session.compare` present |
| `dt_time_microsecond` | tierA | Tier A `session.compare` present |
| `dt_time_minute` | tierA | Tier A `session.compare` present |
| `dt_time_new` | tierA | Tier A `session.compare` present |
| `dt_time_second` | tierA | Tier A `session.compare` present |
| `dt_timedelta_check` | tierA | Tier A `session.compare` present |
| `dt_timedelta_check_exact` | tierA | Tier A `session.compare` present |
| `dt_timedelta_days` | tierA | Tier A `session.compare` present |
| `dt_timedelta_eq` | tierB | Tier A+B compare labels present |
| `dt_timedelta_microseconds` | tierA | Tier A `session.compare` present |
| `dt_timedelta_new` | tierA | Tier A `session.compare` present |
| `dt_timedelta_seconds` | tierA | Tier A `session.compare` present |
| `file_from_fd` | n/a (FD ownership / I/O) | explicit skip |
| `file_getline` | tierA | Tier A `session.compare` present |
| `file_write_cstr` | n/a (file I/O side effects) | explicit skip |
| `file_write_object` | n/a (file I/O side effects) | explicit skip |
| `float_as_double` | tierA | Tier A `session.compare` present |
| `float_check` | tierB | Tier A+B compare labels present |
| `float_check_exact` | tierA | Tier A `session.compare` present |
| `float_eq` | tierB | Tier A+B compare labels present |
| `float_from_cstr` | tierA | Tier A `session.compare` present |
| `float_from_double` | tierA | Tier A `session.compare` present |
| `frozenset_check` | tierA | Tier A `session.compare` present |
| `frozenset_check_exact` | tierA | Tier A `session.compare` present |
| `frozenset_empty` | tierA | Tier A `session.compare` present |
| `frozenset_eq` | tierB | Tier A+B compare labels present |
| `frozenset_new` | tierA | Tier A `session.compare` present |
| `func_check` | tierB | Tier A+B compare labels present |
| `func_eq` | tierB | Tier A+B compare labels present |
| `func_get_closure` | tierA | Tier A `session.compare` present |
| `func_get_code` | tierA | Tier A `session.compare` present |
| `func_get_defaults` | tierA | Tier A `session.compare` present |
| `func_get_globals` | tierA | Tier A `session.compare` present |
| `func_get_module` | tierA | Tier A `session.compare` present |
| `func_new` | tierA | Tier A `session.compare` present |
| `func_set_closure` | tierA | Tier A `session.compare` present |
| `func_set_defaults` | tierA | Tier A `session.compare` present |
| `gc_collect` | n/a (process-global GC) | explicit skip |
| `gc_disable` | n/a (process-global GC) | explicit skip |
| `gc_enable` | n/a (process-global GC) | explicit skip |
| `gc_is_enabled` | tierB | Tier A+B compare labels present |
| `gen_check` | tierB | Tier A+B compare labels present |
| `gen_check_exact` | tierA | Tier A `session.compare` present |
| `gen_eq` | tierB | Tier A+B compare labels present |
| `int_eq` | tierB | Tier A+B compare labels present |
| `iter_check` | tierB | Tier A+B compare labels present |
| `iter_eq` | tierB | Tier A+B compare labels present |
| `iter_next` | tierA | Tier A `session.compare` present |
| `list_append` | tierA | Tier A `session.compare` present |
| `list_as_tuple` | tierA | Tier A `session.compare` present |
| `list_check` | tierB | Tier A+B compare labels present |
| `list_check_exact` | tierA | Tier A `session.compare` present |
| `list_clear` | tierA | Tier A `session.compare` present |
| `list_copy` | tierA | Tier A `session.compare` present |
| `list_empty` | tierA | Tier A `session.compare` present |
| `list_eq` | tierB | Tier A+B compare labels present |
| `list_extend` | tierA | Tier A `session.compare` present |
| `list_get` | tierB | Tier A+B compare labels present |
| `list_get_checked` | tierB | Tier A+B compare labels present |
| `list_get_ref` | tierA | Tier A `session.compare` present |
| `list_insert` | tierA | Tier A `session.compare` present |
| `list_len` | tierB | Tier A+B compare labels present |
| `list_reverse` | tierA | Tier A `session.compare` present |
| `list_set_item` | tierA | Tier A `session.compare` present |
| `list_set_slice` | tierA | Tier A `session.compare` present |
| `list_size` | tierA | Tier A `session.compare` present |
| `list_slice` | tierA | Tier A `session.compare` present |
| `list_sort` | tierA | Tier A `session.compare` present |
| `long_as_double` | tierA | Tier A `session.compare` present |
| `long_as_long` | tierA | Tier A `session.compare` present |
| `long_as_long_overflow` | tierA | Tier A `session.compare` present |
| `long_as_longlong` | tierA | Tier A `session.compare` present |
| `long_as_ssize` | tierA | Tier A `session.compare` present |
| `long_as_ulong` | tierA | Tier A `session.compare` present |
| `long_as_ulong_mask` | tierA | Tier A `session.compare` present |
| `long_as_ulonglong` | tierA | Tier A `session.compare` present |
| `long_as_ulonglong_mask` | tierA | Tier A `session.compare` present |
| `long_check` | tierB | Tier A+B compare labels present |
| `long_check_exact` | tierA | Tier A `session.compare` present |
| `long_eq` | tierB | Tier A+B compare labels present |
| `long_from_double` | tierA | Tier A `session.compare` present |
| `long_from_long` | tierA | Tier A `session.compare` present |
| `long_from_longlong` | tierA | Tier A `session.compare` present |
| `long_from_size` | tierA | Tier A `session.compare` present |
| `long_from_ssize` | tierA | Tier A `session.compare` present |
| `long_from_ulong` | tierA | Tier A `session.compare` present |
| `long_from_ulonglong` | tierA | Tier A `session.compare` present |
| `map_check` | tierB | Tier A+B compare labels present |
| `map_del` | tierA | Tier A `session.compare` present |
| `map_del_cstr` | tierA | Tier A `session.compare` present |
| `map_eq` | tierB | Tier A+B compare labels present |
| `map_getitem_cstr` | tierA | Tier A `session.compare` present |
| `map_has_key` | tierA | Tier A `session.compare` present |
| `map_has_key_cstr` | tierA | Tier A `session.compare` present |
| `map_items` | tierA | Tier A `session.compare` present |
| `map_keys` | tierA | Tier A `session.compare` present |
| `map_len` | tierA | Tier A `session.compare` present |
| `map_setitem_cstr` | tierA | Tier A `session.compare` present |
| `map_values` | tierA | Tier A `session.compare` present |
| `marshal_dumps` | tierB | Tier A+B compare labels present |
| `marshal_loads` | tierA | Tier A `session.compare` present |
| `memoryview_check` | tierB | Tier A+B compare labels present |
| `memoryview_eq` | tierB | Tier A+B compare labels present |
| `memoryview_from_object` | tierA | Tier A `session.compare` present |
| `memoryview_get_contiguous` | tierA | Tier A `session.compare` present |
| `memoryview_ne` | tierB | Tier A+B compare labels present |
| `method_check` | tierB | Tier A+B compare labels present |
| `method_eq` | tierB | Tier A+B compare labels present |
| `method_get_function` | tierA | Tier A `session.compare` present |
| `method_get_self` | tierA | Tier A `session.compare` present |
| `method_new` | tierA | Tier A `session.compare` present |
| `mod_add_cstr` | tierA | Tier A `session.compare` present |
| `mod_add_int` | tierA | Tier A `session.compare` present |
| `mod_add_object_ref` | tierA | Tier A `session.compare` present |
| `mod_check` | tierB | Tier A+B compare labels present |
| `mod_check_exact` | tierA | Tier A `session.compare` present |
| `mod_eq` | tierB | Tier A+B compare labels present |
| `mod_get_filename` | tierA | Tier A `session.compare` present |
| `mod_get_name` | tierA | Tier A `session.compare` present |
| `mod_import` | tierA | Tier A `session.compare` present |
| `mod_import_object` | tierA | Tier A `session.compare` present |
| `mod_magic_number` | tierA | Tier A `session.compare` present |
| `mod_new` | tierA | Tier A `session.compare` present |
| `mod_new_object` | tierA | Tier A `session.compare` present |
| `mod_reload` | n/a (module reload side effects) | explicit skip |
| `num_abs` | tierA | Tier A `session.compare` present |
| `num_add` | tierA | Tier A `session.compare` present |
| `num_and` | tierA | Tier A `session.compare` present |
| `num_as_ssize` | tierA | Tier A `session.compare` present |
| `num_check` | tierB | Tier A+B compare labels present |
| `num_divmod` | tierA | Tier A `session.compare` present |
| `num_eq` | tierB | Tier A+B compare labels present |
| `num_float` | tierA | Tier A `session.compare` present |
| `num_floordiv` | tierA | Tier A `session.compare` present |
| `num_index` | tierA | Tier A `session.compare` present |
| `num_index_check` | tierA | Tier A `session.compare` present |
| `num_inplace_add` | tierA | Tier A `session.compare` present |
| `num_inplace_and` | tierA | Tier A `session.compare` present |
| `num_inplace_floordiv` | tierA | Tier A `session.compare` present |
| `num_inplace_lshift` | tierA | Tier A `session.compare` present |
| `num_inplace_matmul` | tierA | Tier A `session.compare` present |
| `num_inplace_mod` | tierA | Tier A `session.compare` present |
| `num_inplace_mul` | tierA | Tier A `session.compare` present |
| `num_inplace_or` | tierA | Tier A `session.compare` present |
| `num_inplace_pow` | tierA | Tier A `session.compare` present |
| `num_inplace_rshift` | tierA | Tier A `session.compare` present |
| `num_inplace_sub` | tierA | Tier A `session.compare` present |
| `num_inplace_truediv` | tierA | Tier A `session.compare` present |
| `num_inplace_xor` | tierA | Tier A `session.compare` present |
| `num_invert` | tierA | Tier A `session.compare` present |
| `num_long` | tierA | Tier A `session.compare` present |
| `num_lshift` | tierA | Tier A `session.compare` present |
| `num_matmul` | tierA | Tier A `session.compare` present |
| `num_mod` | tierA | Tier A `session.compare` present |
| `num_mul` | tierA | Tier A `session.compare` present |
| `num_neg` | tierA | Tier A `session.compare` present |
| `num_or` | tierA | Tier A `session.compare` present |
| `num_pos` | tierA | Tier A `session.compare` present |
| `num_pow` | tierA | Tier A `session.compare` present |
| `num_rshift` | tierA | Tier A `session.compare` present |
| `num_sub` | tierA | Tier A `session.compare` present |
| `num_truediv` | tierA | Tier A `session.compare` present |
| `num_xor` | tierA | Tier A `session.compare` present |
| `obj_as_fd` | tierA | Tier A `session.compare` present |
| `obj_bytes` | tierA | Tier A `session.compare` present |
| `obj_call` | tierA | Tier A `session.compare` present |
| `obj_call_object` | tierA | Tier A `session.compare` present |
| `obj_callable` | tierA | Tier A `session.compare` present |
| `obj_delattr` | tierA | Tier A `session.compare` present |
| `obj_delattr_cstr` | tierA | Tier A `session.compare` present |
| `obj_delitem` | tierA | Tier A `session.compare` present |
| `obj_dir` | tierA | Tier A `session.compare` present |
| `obj_eq` | tierB | Tier A+B compare labels present |
| `obj_format` | tierA | Tier A `session.compare` present |
| `obj_getattr` | tierA | Tier A `session.compare` present |
| `obj_getattr_cstr` | tierA | Tier A `session.compare` present |
| `obj_getitem` | tierA | Tier A `session.compare` present |
| `obj_hasattr` | tierA | Tier A `session.compare` present |
| `obj_hasattr_cstr` | tierA | Tier A `session.compare` present |
| `obj_hash` | tierA | Tier A `session.compare` present |
| `obj_isinstance` | tierA | Tier A `session.compare` present |
| `obj_issubclass` | tierA | Tier A `session.compare` present |
| `obj_istrue` | tierA | Tier A `session.compare` present |
| `obj_iter` | tierA | Tier A `session.compare` present |
| `obj_len` | tierB | Tier A+B compare labels present |
| `obj_length_hint` | tierA | Tier A `session.compare` present |
| `obj_not` | tierA | Tier A `session.compare` present |
| `obj_repr` | tierA | Tier A `session.compare` present |
| `obj_richcompare` | tierA | Tier A `session.compare` present |
| `obj_richcompare_bool` | tierA | Tier A `session.compare` present |
| `obj_setattr` | tierA | Tier A `session.compare` present |
| `obj_setattr_cstr` | tierA | Tier A `session.compare` present |
| `obj_setitem` | tierA | Tier A `session.compare` present |
| `obj_size` | tierA | Tier A `session.compare` present |
| `obj_str` | tierA | Tier A `session.compare` present |
| `obj_type` | tierB | Tier A+B compare labels present |
| `range_eq` | tierB | Tier A+B compare labels present |
| `seq_check` | tierA | Tier A `session.compare` present |
| `seq_concat` | tierA | Tier A `session.compare` present |
| `seq_contains` | tierA | Tier A `session.compare` present |
| `seq_count` | tierA | Tier A `session.compare` present |
| `seq_del` | tierA | Tier A `session.compare` present |
| `seq_del_slice` | tierA | Tier A `session.compare` present |
| `seq_eq` | tierB | Tier A+B compare labels present |
| `seq_get` | tierB | Tier A+B compare labels present |
| `seq_index` | tierA | Tier A `session.compare` present |
| `seq_inplace_concat` | tierA | Tier A `session.compare` present |
| `seq_inplace_repeat` | tierA | Tier A `session.compare` present |
| `seq_len` | tierB | Tier A+B compare labels present |
| `seq_list` | tierA | Tier A `session.compare` present |
| `seq_repeat` | tierA | Tier A `session.compare` present |
| `seq_set` | tierA | Tier A `session.compare` present |
| `seq_set_slice` | tierA | Tier A `session.compare` present |
| `seq_size` | tierA | Tier A `session.compare` present |
| `seq_slice` | tierA | Tier A `session.compare` present |
| `seq_tuple` | tierA | Tier A `session.compare` present |
| `seqiter_check` | tierB | Tier A+B compare labels present |
| `seqiter_new` | tierA | Tier A `session.compare` present |
| `set_add` | tierA | Tier A `session.compare` present |
| `set_any_check` | tierA | Tier A `session.compare` present |
| `set_any_check_exact` | tierA | Tier A `session.compare` present |
| `set_check` | tierB | Tier A+B compare labels present |
| `set_check_exact` | tierA | Tier A `session.compare` present |
| `set_clear` | tierA | Tier A `session.compare` present |
| `set_contains` | tierB | Tier A+B compare labels present |
| `set_copy` | tierA | Tier A `session.compare` present |
| `set_discard` | tierA | Tier A `session.compare` present |
| `set_empty` | tierA | Tier A `session.compare` present |
| `set_eq` | tierB | Tier A+B compare labels present |
| `set_len` | tierB | Tier A+B compare labels present |
| `set_new` | tierA | Tier A `session.compare` present |
| `set_pop` | tierA | Tier A `session.compare` present |
| `set_size` | tierA | Tier A `session.compare` present |
| `set_update` | tierA | Tier A `session.compare` present |
| `slice_check` | tierB | Tier A+B compare labels present |
| `slice_eq` | tierB | Tier A+B compare labels present |
| `slice_indices_ex` | tierA | Tier A `session.compare` present |
| `slice_new` | tierA | Tier A `session.compare` present |
| `slice_unpack` | tierA | Tier A `session.compare` present |
| `str_all_alnum_ascii` | tierA | Tier A `session.compare` present |
| `str_all_alpha_ascii` | tierA | Tier A `session.compare` present |
| `str_all_digits` | tierA | Tier A `session.compare` present |
| `str_as_or_empty` | tierA | Tier A `session.compare` present |
| `str_char_at` | tierA | Tier A `session.compare` present |
| `str_check` | tierB | Tier A+B compare labels present |
| `str_check_exact` | tierB | Tier A+B compare labels present |
| `str_cmp` | tierB | Tier A+B compare labels present |
| `str_concat` | tierA | Tier A `session.compare` present |
| `str_concat3` | tierA | Tier A `session.compare` present |
| `str_concat4` | tierA | Tier A `session.compare` present |
| `str_contains` | tierB | Tier A+B compare labels present |
| `str_endswith` | tierA | Tier A `session.compare` present |
| `str_eq` | tierB | Tier A+B compare labels present |
| `str_first_char` | tierA | Tier A `session.compare` present |
| `str_ge` | tierB | Tier A+B compare labels present |
| `str_gt` | tierB | Tier A+B compare labels present |
| `str_is` | tierB | Tier A+B compare labels present |
| `str_is_blank` | tierA | Tier A `session.compare` present |
| `str_is_empty` | tierA | Tier A `session.compare` present |
| `str_is_not` | tierA | Tier A `session.compare` present |
| `str_last_char` | tierA | Tier A `session.compare` present |
| `str_le` | tierB | Tier A+B compare labels present |
| `str_len` | tierB | Tier A+B compare labels present |
| `str_lt` | tierB | Tier A+B compare labels present |
| `str_ne` | tierA | Tier A `session.compare` present |
| `str_none_to_empty` | tierA | Tier A `session.compare` present |
| `str_not_empty` | tierA | Tier A `session.compare` present |
| `str_or_empty` | tierA | Tier A `session.compare` present |
| `str_or_none` | tierA | Tier A `session.compare` present |
| `str_startswith` | tierA | Tier A `session.compare` present |
| `time_monotonic` | tierA | Tier A `session.compare` present |
| `time_perf_counter` | tierA | Tier A `session.compare` present |
| `time_wall` | tierB | Tier A+B compare labels present |
| `tuple_check` | tierB | Tier A+B compare labels present |
| `tuple_check_exact` | tierB | Tier A+B compare labels present |
| `tuple_eq` | tierB | Tier A+B compare labels present |
| `tuple_get` | tierB | Tier A+B compare labels present |
| `tuple_get_checked` | tierB | Tier A+B compare labels present |
| `tuple_len` | tierB | Tier A+B compare labels present |
| `tuple_pack2` | tierA | Tier A `session.compare` present |
| `tuple_pack3` | tierA | Tier A `session.compare` present |
| `tuple_pack4` | tierA | Tier A `session.compare` present |
| `tuple_size` | tierB | Tier A+B compare labels present |
| `tuple_slice` | tierA | Tier A `session.compare` present |
| `type_check` | tierB | Tier A+B compare labels present |
| `type_check_exact` | tierA | Tier A `session.compare` present |
| `type_eq` | tierB | Tier A+B compare labels present |
| `type_is_subtype` | tierA | Tier A `session.compare` present |
| `uintern` | tierB | Tier A+B compare labels present |
| `unicode_eq` | tierB | Tier A+B compare labels present |
| `uutf8_bytes` | tierB | Tier A+B compare labels present |
| `weakref_check` | tierB | Tier A+B compare labels present |
| `weakref_check_proxy` | tierA | Tier A `session.compare` present |
| `weakref_check_ref` | tierA | Tier A `session.compare` present |
| `weakref_eq` | tierB | Tier A+B compare labels present |
| `weakref_get_object` | tierA | Tier A `session.compare` present |
| `weakref_new_proxy` | tierA | Tier A `session.compare` present |
| `weakref_new_ref` | tierA | Tier A `session.compare` present |
