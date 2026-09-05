#!/usr/bin/env bash
# Headless eq-issue grind for ckirua/picop (run inside tmux).
# Usage: scripts/eq_loop_tmux.sh
# Stop:  tmux kill-session -t cypy-eq
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
LOG_DIR="${ROOT}/.eq_loop_logs"
mkdir -p "$LOG_DIR"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
LOG="${LOG_DIR}/run_${STAMP}.log"

PROMPT='Repo ckirua/picop at /home/dev/cypy. Continue the [eq/…] helper loop.

Rules (strict):
- One open GitHub issue whose title starts with "[eq/" per run. Skip #44 unless asked.
- Pick lowest issue number among remaining open [eq/ titles (after #19 on main; next is typically #20+).
- Fresh branch from origin/main. Mirror existing *_eq / *_ne / str_* siblings.
- Export cypy (+ hot/buffers/containers when siblings do); .pyi; tracker; CHANGELOG bump; examples smoke; check_exports + grade_trackers.
- Push; gh pr create with Closes #N; merge only if CI green. On red CI: comment and STOP the loop.
- Do not force-push main; do not skip hooks; do not touch feat/evlib-aiofastnet or non-[eq/ work.
- If no matching open issues remain (except #44), print DONE_EQ_LOOP and exit 0.
- See docs/AGENT_LOOPS.md.

Execute now: implement the next issue end-to-end.'

echo "=== eq loop start ${STAMP} ===" | tee -a "$LOG"
echo "log: $LOG" | tee -a "$LOG"

while true; do
  # Stop when only #44 (or nothing) remains
  LEFT=$(gh issue list -R ckirua/picop --state open --limit 100 --json number,title \
    --jq '[.[] | select(.title | startswith("[eq/")) | select(.number != 44)] | length' 2>/dev/null || echo "?")
  echo "$(date -u +%H:%M:%SZ) open_eq_excluding_44=${LEFT}" | tee -a "$LOG"
  if [[ "$LEFT" == "0" ]]; then
    echo "DONE_EQ_LOOP" | tee -a "$LOG"
    exit 0
  fi

  # Ensure clean-ish main before each agent tick
  git fetch origin --prune >>"$LOG" 2>&1 || true
  git checkout main >>"$LOG" 2>&1 || true
  git pull --ff-only origin main >>"$LOG" 2>&1 || true

  echo "$(date -u +%H:%M:%SZ) agent tick begin" | tee -a "$LOG"
  set +e
  agent -p --trust --force --workspace "$ROOT" "$PROMPT" 2>&1 | tee -a "$LOG"
  rc=${PIPESTATUS[0]}
  set -e
  echo "$(date -u +%H:%M:%SZ) agent tick end rc=${rc}" | tee -a "$LOG"

  if grep -q 'DONE_EQ_LOOP' <<<"$(tail -n 40 "$LOG")"; then
    exit 0
  fi
  # Brief pause between issues (CI / rate limits)
  sleep 20
done
