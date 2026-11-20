# Consumer replacement catalog

This is the authoritative, source-derived consumer inventory. It covers the complete Python `cy` barrel and package-cimport surface, documented example-used direct cimports, explicit class members, and UUID exports/members. It does not claim coverage of every raw C declaration or every direct-only package API. Module maps are exhaustive within that boundary; counts are computed by the checker, not maintained here. Coverage is not an optimization-function count or a speed claim.

## Module maps

| Module | Map | Surface |
|---|---|---|
| cyansi | [cyansi](maps/cyansi.md) | ANSI helpers |
| cyarray | [cyarray](maps/cyarray.md) | Arrays |
| cyatomic | [cyatomic](maps/cyatomic.md) | Atomics |
| cybool | [cybool](maps/cybool.md) | Booleans |
| cybuffer | [cybuffer](maps/cybuffer.md) | Buffers |
| cybytearray | [cybytearray](maps/cybytearray.md) | Byte arrays |
| cybytes | [cybytes](maps/cybytes.md) | Bytes and writers |
| cycall | [cycall](maps/cycall.md) | Calls |
| cycellobject | [cycellobject](maps/cycellobject.md) | Cells |
| cyceval | [cyceval](maps/cyceval.md) | Evaluation |
| cycode | [cycode](maps/cycode.md) | Code objects |
| cycodecs | [cycodecs](maps/cycodecs.md) | Codecs |
| cycomplex | [cycomplex](maps/cycomplex.md) | Complex numbers |
| cycontextvars | [cycontextvars](maps/cycontextvars.md) | Context variables |
| cyconversion | [cyconversion](maps/cyconversion.md) | Conversions |
| cycriticalsection | [cycriticalsection](maps/cycriticalsection.md) | Critical sections |
| cydatetime | [cydatetime](maps/cydatetime.md) | Date and time |
| cydeque | [cydeque](maps/cydeque.md) | Deques |
| cydescr | [cydescr](maps/cydescr.md) | Descriptors |
| cydict | [cydict](maps/cydict.md) | Dictionaries |
| cyerr | [cyerr](maps/cyerr.md) | Errors |
| cyfileobject | [cyfileobject](maps/cyfileobject.md) | Files |
| cyfloat | [cyfloat](maps/cyfloat.md) | Floats |
| cyframe | [cyframe](maps/cyframe.md) | Frames |
| cyfrozendict | [cyfrozendict](maps/cyfrozendict.md) | Frozen dictionaries |
| cyfunction | [cyfunction](maps/cyfunction.md) | Functions |
| cygc | [cygc](maps/cygc.md) | Garbage collection |
| cygenobject | [cygenobject](maps/cygenobject.md) | Generators |
| cygetargs | [cygetargs](maps/cygetargs.md) | Argument parsing |
| cyhash | [cyhash](maps/cyhash.md) | Hashing |
| cyiterator | [cyiterator](maps/cyiterator.md) | Iterators |
| cyiterobject | [cyiterobject](maps/cyiterobject.md) | Iterator objects |
| cylist | [cylist](maps/cylist.md) | Lists |
| cylock | [cylock](maps/cylock.md) | Locks |
| cylong | [cylong](maps/cylong.md) | Integers and writers |
| cylongintrepr | [cylongintrepr](maps/cylongintrepr.md) | Integer internals |
| cymapping | [cymapping](maps/cymapping.md) | Mappings |
| cymarshal | [cymarshal](maps/cymarshal.md) | Marshal |
| cymem | [cymem](maps/cymem.md) | Memory |
| cymemoryview | [cymemoryview](maps/cymemoryview.md) | Memory views |
| cymethod | [cymethod](maps/cymethod.md) | Methods |
| cymodule | [cymodule](maps/cymodule.md) | Modules |
| cymonitoring | [cymonitoring](maps/cymonitoring.md) | Monitoring |
| cynumber | [cynumber](maps/cynumber.md) | Numeric protocols |
| cyobject | [cyobject](maps/cyobject.md) | Object protocols |
| cypicklebuf | [cypicklebuf](maps/cypicklebuf.md) | Pickle buffers |
| cypycapsule | [cypycapsule](maps/cypycapsule.md) | Capsules |
| cypylifecycle | [cypylifecycle](maps/cypylifecycle.md) | Lifecycle |
| cypyport | [cypyport](maps/cypyport.md) | Portability |
| cypystate | [cypystate](maps/cypystate.md) | Interpreter state |
| cyrange | [cyrange](maps/cyrange.md) | Ranges |
| cyref | [cyref](maps/cyref.md) | References |
| cysentinel | [cysentinel](maps/cysentinel.md) | Sentinels |
| cysequence | [cysequence](maps/cysequence.md) | Sequences |
| cyset | [cyset](maps/cyset.md) | Sets |
| cyslice | [cyslice](maps/cyslice.md) | Slices |
| cystr | [cystr](maps/cystr.md) | Strings |
| cysys | [cysys](maps/cysys.md) | System state |
| cythread | [cythread](maps/cythread.md) | Threads |
| cytime | [cytime](maps/cytime.md) | Time |
| cytraceback | [cytraceback](maps/cytraceback.md) | Tracebacks |
| cytuple | [cytuple](maps/cytuple.md) | Tuples |
| cytype | [cytype](maps/cytype.md) | Types |
| cyunicode | [cyunicode](maps/cyunicode.md) | Unicode and writers |
| cyversion | [cyversion](maps/cyversion.md) | Version |
| cywarnings | [cywarnings](maps/cywarnings.md) | Warnings |
| cyweakref | [cyweakref](maps/cyweakref.md) | Weak references |
| uuid | [UUID](maps/uuid.md) | UUID exports and stubbed members |

## Navigate by expression or use

These links are navigation into authoritative rows, not classifications or migration recommendations.

| Area | Maps |
|---|---|
| Containers | [`dict.get`](maps/cydict.md#dict_get), [list indexing](maps/cylist.md#list_get), [set membership](maps/cyset.md#set_contains), [tuple indexing](maps/cytuple.md#tuple_get) |
| Strings and buffers | [bytes membership](maps/cybytes.md#bytes_contains), [string membership](maps/cystr.md#str_contains), [Unicode](maps/cyunicode.md#unicode_eq), [buffer size](maps/cybuffer.md#buf_nbytes) |
| Numeric and struct | [integer sign](maps/cylong.md#long_is_zero), [float unpack](maps/cyfloat.md#float_unpack8), [complex construction](maps/cycomplex.md#complex_from_doubles) |
| Calls and object protocols | [object calls](maps/cyobject.md#obj_call), [type dictionaries](maps/cytype.md#type_get_dict), [functions](maps/cyfunction.md#func_check), [methods](maps/cymethod.md#method_check) |
| Datetime, context, stdlib | [datetime](maps/cydatetime.md#dt_datetime_new), [context variables](maps/cycontextvars.md#ctxvar_new), [clocks](maps/cytime.md#time_monotonic) |
| Runtime and extension plumbing | [error state](maps/cyerr.md#err_occurred), [allocation](maps/cymem.md#mem_malloc), [thread locks](maps/cythread.md#thread_allocate_lock), [atomics](maps/cyatomic.md#atomic_load_relaxed), [mutexes](maps/cylock.md#mutex_lock) |
| Writers | [bytes finish](maps/cybytes.md#BytesWriter-finish), [Unicode finish](maps/cyunicode.md#UnicodeWriter-finish), [integer writer](maps/cylong.md#long_writer_create) |
| UUID | [UUID generation](maps/uuid.md#uuid4) |
