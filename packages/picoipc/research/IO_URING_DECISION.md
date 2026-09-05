# io_uring decision for the picoipc SPSC ring

## Summary

**picoipc does not use io_uring for the ring hot path.** The correct stack is POSIX shared memory (`shm_open` + `mmap`), SPSC sequence counters with acquire/release atomics, and Linux futex for consumer blocking.

## Why not io_uring here?

| Concern | Ring hot path | io_uring |
|---------|---------------|----------|
| Data location | Slots already in mapped SHM | Async read/write on FDs |
| Per-message work | Atomic seq bump + optional memcpy | Syscall batching for I/O |
| Blocking consumer | `FUTEX_WAIT` on `write_seq` | Poll/readiness on FDs |

Messages are **already in memory** after `mmap`. io_uring does not remove Python/C++ boundary cost or heap allocation on the consume path. It targets network, disk, and socket readiness — not in-process SPSC over mapped pages.

## Where io_uring fits in larger low-latency stacks

In typical trading/gateway C++ cores (not this repo), io_uring often appears in:

- event-loop / readiness reactors
- HTTPS clients with an `iouring` backend
- TLS sockets integrated with those reactors

The production SPSC SHM ring in those stacks uses the **same futex + mmap pattern** as picoipc, with env-tunable spin (`_SHM_SPIN_ITERS`, `_SHM_WAIT_MS`).

## Alternatives considered

1. **futex (current)** — low latency wake; no FD per message.
2. **eventfd + epoll** — optional experiment (`opt/eventfd-wake`); expect higher latency than futex for this pattern.
3. **Pure spin** — best throughput when consumer is always hot; bad for idle power and cross-core fairness.

## Conclusion

Keep futex for wake/wait. Optimize zero-copy APIs and Python bindings instead of adding io_uring to the ring.
