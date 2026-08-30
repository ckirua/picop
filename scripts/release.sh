#!/usr/bin/env bash
# Tag + GitHub Release for cypy / picop. Pushing v* runs .github/workflows/publish.yml.
#
# Usage:
#   scripts/release.sh 1.44.17
#   scripts/release.sh --patch              # bump patch from __about__.py
#   scripts/release.sh --minor | --major
#   scripts/release.sh 1.44.17 --dry-run
#   scripts/release.sh 1.44.17 --skip-checks
#   scripts/release.sh 1.44.17 --title "short highlight"
#   scripts/release.sh 1.44.17 --notes-file path.md
#
# Requires: git, gh; clean main tracking origin/main (unless --allow-dirty).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

ABOUT="src/picop/__about__.py"
CHANGELOG="CHANGELOG.md"
DRY_RUN=0
SKIP_CHECKS=0
ALLOW_DIRTY=0
NO_PUSH=0
BUMP=""
VERSION=""
TITLE=""
NOTES_FILE=""

usage() {
  awk 'NR==1 {next} /^[^#]/ {exit} {sub(/^# ?/,""); print}' "$0"
  exit "${1:-0}"
}

die() { echo "error: $*" >&2; exit 1; }
info() { echo "==> $*"; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help) usage 0 ;;
    --dry-run) DRY_RUN=1; shift ;;
    --skip-checks) SKIP_CHECKS=1; shift ;;
    --allow-dirty) ALLOW_DIRTY=1; shift ;;
    --no-push) NO_PUSH=1; shift ;;
    --patch|--minor|--major) BUMP="${1#--}"; shift ;;
    --title) TITLE="${2:?}"; shift 2 ;;
    --notes-file) NOTES_FILE="${2:?}"; shift 2 ;;
    -*) die "unknown flag: $1 (see --help)" ;;
    *)
      [[ -z "$VERSION" ]] || die "unexpected extra arg: $1"
      VERSION="$1"
      shift
      ;;
  esac
done

[[ -n "$VERSION" || -n "$BUMP" ]] || usage 1
[[ -z "$VERSION" || -z "$BUMP" ]] || die "pass either VERSION or --patch/--minor/--major, not both"

current_version() {
  python3 -c "import pathlib,re; t=pathlib.Path('$ABOUT').read_text(); m=re.search(r'__version__\\s*=\\s*\"([^\"]+)\"', t); assert m, 'no __version__'; print(m.group(1))"
}

bump_version() {
  local cur="$1" kind="$2"
  python3 -c "
import sys
cur, kind = sys.argv[1], sys.argv[2]
parts = [int(x) for x in cur.split('.')]
if len(parts) != 3:
    raise SystemExit(f'expected X.Y.Z, got {cur!r}')
major, minor, patch = parts
if kind == 'major':
    major, minor, patch = major + 1, 0, 0
elif kind == 'minor':
    minor, patch = minor + 1, 0
elif kind == 'patch':
    patch += 1
else:
    raise SystemExit(kind)
print(f'{major}.{minor}.{patch}')
" "$cur" "$kind"
}

OLD="$(current_version)"
if [[ -n "$BUMP" ]]; then
  VERSION="$(bump_version "$OLD" "$BUMP")"
fi

[[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+([.][0-9]+)*([a-zA-Z0-9.+-]*)?$ ]] \
  || die "version must be PEP 440-ish X.Y.Z (got: $VERSION)"
[[ "$VERSION" != "$OLD" ]] || die "version $VERSION is already current in $ABOUT"

TAG="v${VERSION}"
TODAY="$(date -u +%Y-%m-%d)"
[[ -n "$TITLE" ]] || TITLE="release ${VERSION}"

info "release ${OLD} → ${VERSION} (tag ${TAG})"

# Preconditions
branch="$(git rev-parse --abbrev-ref HEAD)"
[[ "$branch" == "main" ]] || die "must be on main (on $branch)"
if [[ "$ALLOW_DIRTY" -eq 0 ]]; then
  git diff --quiet && git diff --cached --quiet \
    || die "working tree dirty (commit/stash, or pass --allow-dirty)"
fi
git fetch origin main --tags --quiet
git merge-base --is-ancestor HEAD origin/main \
  || die "local main is not based on origin/main; git pull first"
ahead="$(git rev-list --count origin/main..HEAD)"
behind="$(git rev-list --count HEAD..origin/main)"
[[ "$behind" -eq 0 ]] || die "main is behind origin/main by $behind; git pull first"
if [[ "$ahead" -ne 0 && "$ALLOW_DIRTY" -eq 0 ]]; then
  die "main is ahead of origin/main by $ahead; push or reset first"
fi
if git rev-parse "$TAG" >/dev/null 2>&1; then
  die "tag $TAG already exists"
fi
if gh release view "$TAG" >/dev/null 2>&1; then
  die "GitHub release $TAG already exists"
fi

if [[ "$SKIP_CHECKS" -eq 0 ]]; then
  info "preflight checks"
  python3 scripts/check_exports.py
  python3 scripts/grade_trackers.py
else
  info "skipping preflight checks"
fi

run() {
  if [[ "$DRY_RUN" -eq 1 ]]; then
    echo "dry-run: $*"
  else
    "$@"
  fi
}

info "bump $ABOUT"
if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "dry-run: set __version__ = \"$VERSION\""
else
  python3 -c "
from pathlib import Path
import re
p = Path('$ABOUT')
t = p.read_text()
nt, n = re.subn(r'(__version__\\s*=\\s*\")[^\"]+(\")', r'\\g<1>${VERSION}\\2', t, count=1)
assert n == 1, n
p.write_text(nt)
"
fi

info "update $CHANGELOG"
if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "dry-run: promote Unreleased / insert ## [$VERSION] — $TODAY — $TITLE"
else
  VERSION="$VERSION" TODAY="$TODAY" TITLE="$TITLE" python3 -c "
from pathlib import Path
import os, re
p = Path('$CHANGELOG')
text = p.read_text()
ver, today, title = os.environ['VERSION'], os.environ['TODAY'], os.environ['TITLE']
header = f'## [{ver}] — {today} — {title}'
pat = re.compile(r'^## \\[Unreleased\\][^\\n]*\\n', re.M)
if pat.search(text):
    text = pat.sub(header + '\\n', text, count=1)
elif re.search(rf'^## \\[{re.escape(ver)}\\]', text, re.M):
    pass
else:
    text = re.sub(
        r'(^# Changelog\\n\\n)',
        r'\\1' + header + '\\n\\n- (add highlights)\\n\\n',
        text,
        count=1,
        flags=re.M,
    )
p.write_text(text)
"
fi

info "refresh install pins (${OLD} → ${VERSION})"
pin_files=(README.md .cursor/skills/use-cypy/SKILL.md)
if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "dry-run: replace $OLD with $VERSION in: ${pin_files[*]}"
else
  for f in "${pin_files[@]}"; do
    [[ -f "$f" ]] || continue
    python3 -c "
from pathlib import Path
p = Path('$f')
t = p.read_text()
old, new = '$OLD', '$VERSION'
if old not in t:
    raise SystemExit(0)
p.write_text(t.replace(old, new))
print(f'  updated {p}')
"
  done
fi

msg="Release v${VERSION}: ${TITLE}."

info "commit"
run git add "$ABOUT" "$CHANGELOG" "${pin_files[@]}"
if [[ "$DRY_RUN" -eq 0 ]]; then
  if git diff --cached --quiet; then
    die "nothing staged to commit (changelog/pins already at $VERSION?)"
  fi
fi
run git commit -m "$msg"

if [[ "$NO_PUSH" -eq 1 ]]; then
  info "done (no push). Tag locally with: git tag -a $TAG -m \"cypy $TAG\""
  exit 0
fi

info "push main"
run git push origin main

info "tag + push $TAG"
run git tag -a "$TAG" -m "cypy $TAG"
run git push origin "$TAG"

NOTES_TMP="$(mktemp)"
cleanup() { rm -f "$NOTES_TMP"; }
trap cleanup EXIT

if [[ -n "$NOTES_FILE" ]]; then
  cp "$NOTES_FILE" "$NOTES_TMP"
else
  # Prefer CHANGELOG section body when present
  python3 -c "
from pathlib import Path
import re
text = Path('$CHANGELOG').read_text()
ver = '$VERSION'
m = re.search(rf'^## \\[{re.escape(ver)}\\][^\\n]*\\n(?P<body>.*?)(?=^## \\[|\\Z)', text, re.M | re.S)
body = (m.group('body').strip() if m else '- ${TITLE}')
print(f'''## Highlights
{body}

## Requires
- Python ≥ 3.14

## Install
\`\`\`bash
pip install \"picop=={ver}\"
# or: pip install \"picop @ git+https://github.com/ckirua/picop.git@v{ver}\"
\`\`\`
''')
" >"$NOTES_TMP"
fi

info "GitHub release $TAG"
run gh release create "$TAG" --title "cypy $TAG" --notes-file "$NOTES_TMP"

info "watching publish workflow (Ctrl+C to detach)"
if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "dry-run: gh run watch (publish.yml)"
else
  # Give Actions a moment to register the tag push
  sleep 3
  run_id="$(gh run list --workflow=publish.yml --branch "$TAG" --limit 1 --json databaseId --jq '.[0].databaseId // empty')"
  if [[ -z "$run_id" ]]; then
    run_id="$(gh run list --workflow=publish.yml --limit 1 --json databaseId,headBranch --jq "[.[] | select(.headBranch==\"$TAG\")][0].databaseId // empty")"
  fi
  if [[ -n "$run_id" ]]; then
    gh run watch "$run_id" --exit-status
    echo
    echo "PyPI: https://pypi.org/project/picop/${VERSION}/"
    echo "Verify: pip install \"picop==${VERSION}\" && python -c \"from picop.hot import bytes_len; assert bytes_len(b'ok')==2\""
  else
    echo "warn: publish run not found yet; check: gh run list --workflow=publish.yml"
  fi
fi
