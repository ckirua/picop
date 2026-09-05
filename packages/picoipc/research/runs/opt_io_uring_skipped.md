# opt/io_uring — skipped (documentation only)

## Verdict

**No branch.** io_uring is out of scope for SPSC POSIX SHM rings.

## Rationale

See `research/IO_URING_DECISION.md`. Hot path is mmap + atomics + futex; ull uses io_uring only for HTTP/TLS readiness, not for `SpscRing` data transfer.

## Gate

N/A — no code change.
