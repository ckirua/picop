# Agent loops for eq-helper issues

How to grind through open `[eq/…]` enhancement issues on [ckirua/picop](https://github.com/ckirua/picop) with Cursor — in chat (`/loop`) or unattended in **tmux** (CLI / SDK).

## Resume pointer (2026-07-22)

**Eq loop complete** on `main` through **#44** (Runtime stretch checklist +
`context_eq`; version ≥ 1.42.0). No open `[eq/…]` issues remain. See
[`EQ_RUNTIME.md`](EQ_RUNTIME.md).

## Scope (always bake into the prompt)

| Filter | Value |
|--------|--------|
| Repo | `ckirua/picop` (workspace `/home/dev/cypy` or clone) |
| Titles | start with `[eq/` (tiers: buffer, string, container, scalar, misc, new-module, stretch) |
| Skip | stretch umbrellas only when already closed / documented |
| Order | tier tag in title, then issue number ascending (`#4`–`#6`, then `#8`+) |
| Cadence | **one issue per tick**; no parallel eq PRs in the same run |
| Merge | only if CI green; on red CI → note on PR/issue and **stop** |
| Stop | no matching open `[eq/…]` issues left, or operator stop |

Shipped already (do not re-file): `str_eq` / `str_ne`, `bytes_eq`. Early buffer issues: `#4` bytearray, `#5` array, `#6` memoryview.

Issue list:

```bash
gh issue list -R ckirua/picop --state open --search 'in:title [eq/'
```

---

## 1. Chat `/loop` (IDE session)

`/loop` is **tied to the Cursor chat session**. It wakes via monitored shell sentinels in that session — not a substitute for tmux on a detached box.

### Syntax

```text
/loop [interval] <prompt>
```

- Leading interval: `/loop 5m …`, `/loop 30s …`, `/loop 2h …`
- Trailing interval: `… every 5m`
- **No interval:** dynamic mode — agent chooses the next delay (prefer this when waiting on CI)
- Units: `30s`, `5m`, `2h`, `1d`

You type `/loop …` in chat; the agent arms the wake loop. To stop: ask to stop the loop (agent kills sleeper/watcher PIDs and does not re-arm).

### Recommended dynamic prompt

Paste as the `/loop` body (or `/loop` alone then the body):

```text
Repo: ckirua/picop. One eq-helper enhancement issue per iteration.

Each tick:
1. List open issues whose title starts with `[eq/` (exclude #44). Order by tier tag in the title, then by issue number ascending (#4–#6, then #8+).
2. Pick exactly one next issue that is still open and not already completed by an open/merged PR for that helper.
3. Implement on a fresh branch; keep scope to that issue only.
4. Open a PR that closes the issue; wait for CI.
5. If CI is green and policy allows, merge and confirm the issue is closed.
6. If CI is red or merge fails: do not merge; leave a short note on the PR/issue; STOP the loop.
7. If no matching open issues remain (after skipping #44): STOP the loop and summarize what landed.

Do not start a second parallel PR for another eq issue in the same tick. Do not touch non-`[eq/` issues.
```

Fixed cadence alternative:

```text
/loop 30m <same body>
```

Use `45m` / `1h` if merges usually take longer than 30 minutes.

---

## 2. Cursor CLI agent in tmux (unattended)

Use headless CLI when the work should survive detach / SSH disconnect. Each `agent -p` is a **one-shot**; iteration state lives in GitHub issues + your shell loop.

Docs: [Headless CLI](https://cursor.com/docs/cli/headless), [CLI parameters](https://cursor.com/docs/cli/reference/parameters).

### One-shot in a session

```bash
tmux new -s cypy-eq
cd /home/dev/cypy   # or your clone

# once: agent login   # and/or export CURSOR_API_KEY=...

agent -p --trust --force \
  --workspace /home/dev/cypy \
  "Repo ckirua/picop. Next open issue titled [eq/ (skip #44), lowest number / tier order.
   Implement only that issue, open PR with Closes, merge if CI green; else stop and report."

# detach: Ctrl-b d
# reattach: tmux attach -t cypy-eq
```

| Flag | Why |
|------|-----|
| `-p` / `--print` | Headless; prints to stdout (required for scripting) |
| `--trust` | Skip workspace trust prompt (headless) |
| `--force` / `--yolo` | Allow commands without interactive approve |

Optional: `--output-format json` for machine-readable runs.

### Shell loop over all scoped issues

```bash
tmux new -s cypy-eq-loop
cd /home/dev/cypy

PROMPT='One [eq/ issue only (skip #44), tier then lowest number.
Implement, PR with Closes, merge if CI green; if CI red exit non-zero and do not continue.
Do not touch non-[eq/ issues.'

while true; do
  # rough emptiness check — refine with jq to exclude #44 if needed
  n=$(gh issue list -R ckirua/picop --state open --search 'in:title [eq/' --json number -q 'length')
  if [ "$n" -eq 0 ]; then
    echo "No open [eq/ issues left."
    break
  fi

  agent -p --trust --force --workspace /home/dev/cypy "$PROMPT"
  status=$?
  if [ "$status" -ne 0 ]; then
    echo "Agent failed (status=$status); stopping."
    break
  fi
  sleep 30
done
```

Keep a second tmux pane for `gh pr checks` / logs if you want to watch live.

---

## 3. Cursor SDK in tmux

Same outer loop as §2, but each tick calls `Agent.prompt(...)` (TypeScript `@cursor/sdk` or Python `cursor-sdk`) with `local.cwd` set to the cypy checkout and `CURSOR_API_KEY` set. Prefer this when you need structured streaming, resume IDs, or custom logging around each issue.

See [TypeScript SDK](https://cursor.com/docs/sdk/typescript) / [Python SDK](https://cursor.com/docs/sdk/python) and the repo skill `.cursor/skills-cursor/sdk/SKILL.md` (Cursor install) for patterns.

---

## 4. What belongs where

| Approach | Detachable (tmux)? | Best for |
|----------|--------------------|----------|
| Chat `/loop` | No (IDE chat + wake) | Interactive grind while you watch |
| `agent -p` + bash/`tmux` | Yes | Overnight / SSH / long issue queues |
| Cursor SDK script + `tmux` | Yes | Custom orchestration / CI glue |
| Cursor Automations | Cloud-scheduled (not local tmux) | Repo/PR triggers — different surface |

`/loop` does **not** run inside tmux by itself. For tmux, use CLI or SDK and encode the same stop rules in the prompt.

---

## 5. Safety checklist

- One issue per tick; no stacked eq PRs.
- Skip **#44** unless intentionally expanding stretch work.
- Merge only on green CI; halt the loop on failure.
- Do not force-push `main`; do not skip hooks unless explicitly required.
- Prefer fresh branches named after the helper (`feat/bytes_ne`, `feat/list_eq`, …).
- After merge: confirm the issue closed (`Closes #N` / `Fixes #N` in the PR body).

---

## See also

- Issue backlog: https://github.com/ckirua/picop/issues?q=is%3Aissue+is%3Aopen+in%3Atitle+%5Beq%2F
- Ship flow: [`PIPELINE.md`](PIPELINE.md)
- Agent norms: [`../AGENTS.md`](../AGENTS.md)
