Create a new git worktree for a task with full setup: branch, dependencies, selective `.claude/` symlinks, CLAUDE.md overlay, and manifest tracking. Universal across projects — picks up project-specific behavior via an optional `worktree-init.sh` hook.

## Input

`$ARGUMENTS` may contain a task ID and optional description, plus flags. If `$ARGUMENTS` is empty or insufficient, ask the user for:

- **TASK_ID** — task identifier (e.g., `CF-42`, `TUKAS-7`, `#123`)
- **TASK_DESCRIPTION** — short description used to derive the branch slug

Optional flags (parse out of `$ARGUMENTS`):

- `--base <branch>` — override base branch (default: auto-detect)
- `--offline` — skip `git fetch`, use local base branch HEAD
- `--no-hook` — skip running `.claude/worktree-init.sh`
- `--no-deps` — skip dependency-install fallback when no hook is present

## Steps

### 1. Resolve repository context

```bash
MAIN_REPO=$(dirname "$(git rev-parse --git-common-dir)")
PROJECT_NAME=$(basename "$MAIN_REPO")
```

`git-common-dir` returns the **main repo's** `.git` even when invoked from inside a worktree — this is what makes the command re-entrant. NEVER use `git rev-parse --show-toplevel` here (it returns the current worktree, which may be a child worktree).

### 2. Determine BASE_BRANCH

If `--base` not given, auto-detect:

```bash
BASE_BRANCH=$(git -C "$MAIN_REPO" symbolic-ref refs/remotes/origin/HEAD 2>/dev/null \
  | sed 's@^refs/remotes/origin/@@')

if [ -z "$BASE_BRANCH" ]; then
  for b in main master develop; do
    if git -C "$MAIN_REPO" show-ref --verify --quiet "refs/heads/$b"; then
      BASE_BRANCH=$b; break
    fi
  done
fi

[ -z "$BASE_BRANCH" ] && { echo "ERROR: cannot determine base branch"; exit 1; }
```

### 3. Normalize names

Compute these (do the normalization yourself rather than relying on a specific tool):

- **TASK_SLUG**: from `TASK_DESCRIPTION` → lowercase, strip diacritics (NFKD + drop combining marks), replace any non-`[a-z0-9-]` run with `-`, collapse repeated `-`, trim leading/trailing `-`, max 40 chars. If `TASK_DESCRIPTION` empty, derive from `TASK_ID` lowercased.
- **TASK_ID_SAFE**: `TASK_ID` with `/` → `-` and any other non-`[A-Za-z0-9#_-]` stripped.
- **BRANCH_PREFIX**: `${CLAUDE_WORKTREE_BRANCH_PREFIX:-task/}`
- **BRANCH_NAME**: `${BRANCH_PREFIX}${TASK_ID_SAFE}-${TASK_SLUG}`
- **WORKTREE_DIR**: `${MAIN_REPO}/../${PROJECT_NAME}-${TASK_SLUG}` resolved to an absolute path

### 4. Pre-flight checks (fail-fast — no state changes yet)

1. **Idempotency**: read `${MAIN_REPO}/.claude/worktrees.json` if it exists. If an entry has matching `task_id` and `status == "active"`, print its existing path and exit 0:
   ```
   Worktree for {TASK_ID} already exists at {path}.
   Run /worktree-list to see all worktrees.
   ```
2. **Branch collision**: `git -C "$MAIN_REPO" show-ref --verify --quiet "refs/heads/$BRANCH_NAME"` → if exists, fail with the conflicting name.
3. **Path collision**: `[ -e "$WORKTREE_DIR" ]` → fail with the conflicting path.
4. **Origin reachable** (skip if `--offline`): `git -C "$MAIN_REPO" ls-remote origin HEAD &>/dev/null` → on failure, ask the user whether to continue offline.

### 5. Fetch base ref

If not `--offline`:

```bash
git -C "$MAIN_REPO" fetch origin "$BASE_BRANCH" --quiet
BASE_REF="origin/$BASE_BRANCH"
```

If `--offline`:

```bash
BASE_REF="$BASE_BRANCH"
```

Do NOT `git pull` on the main repo. `git pull` can produce merge commits or fail on dirty state.

### 6. Create worktree

```bash
git -C "$MAIN_REPO" worktree add -b "$BRANCH_NAME" --no-track "$WORKTREE_DIR" "$BASE_REF"
BASE_COMMIT=$(git -C "$WORKTREE_DIR" rev-parse --short HEAD)
```

`--no-track` is required: without it, Git auto-sets the new branch's upstream to `$BASE_REF` (typically `origin/main`), so a later `git push` targets main and prompts the user to fork. With `--no-track`, the first `git push -u origin <branch>` sets the correct upstream.

If this fails, abort — nothing yet to roll back.

### 7. Selectively symlink `.claude/` (with per-child merge for content dirs)

Goal: every agent / command / skill / knowledge entry / rule available in the main repo's `.claude/` should be reachable in the worktree, regardless of whether the project tracks part of `.claude/` in git.

Three rules:

1. **Skip per-worktree state** — never symlink `worktrees.json`, `settings.local.json`, `memory`.
2. **Fast path** — if the worktree doesn't yet have an entry for `<item>`, symlink the whole thing (file or directory).
3. **Merge path for content directories** — if the worktree DOES have a real directory at `.claude/<item>` (because `<item>` is partially tracked in git for this branch), and `<item>` is a known **content directory**, then for each direct child of `$MAIN_REPO/.claude/<item>/` that's missing in the worktree's copy, drop a symlink. This is what was missing in the first PLM run: tracked `agents/gitlab-mr-reviewer.md` caused the whole `agents/` to be skipped, hiding the other 13 agents.

Content directories (children are independent units — each `.md` agent / command / rule, each skill subdirectory):

```
agents commands skills knowledge rules
```

For non-content directories that already exist in the worktree (e.g. a hypothetical project-specific config dir), stay opaque and leave them alone — file-by-file merge there could combine things that aren't independent.

```bash
mkdir -p "$WORKTREE_DIR/.claude"

SKIP=(worktrees.json settings.local.json memory)
MERGE_DIRS=(agents commands skills knowledge rules)

is_in_list() {
  local needle=$1; shift
  local item
  for item in "$@"; do [ "$item" = "$needle" ] && return 0; done
  return 1
}

SYMLINKED=()      # items symlinked at top level (fast path)
MERGED=()         # content dirs where missing children were symlinked
KEPT=()           # items left as tracked files (couldn't merge)

for src in "$MAIN_REPO"/.claude/*; do
  [ -e "$src" ] || continue
  base=$(basename "$src")

  is_in_list "$base" "${SKIP[@]}" && continue

  dst="$WORKTREE_DIR/.claude/$base"

  # Fast path
  if [ ! -e "$dst" ] && [ ! -L "$dst" ]; then
    ln -s "$src" "$dst"
    SYMLINKED+=("$base")
    continue
  fi

  # Merge path: both are directories AND base is a known content dir AND dst is a real dir (not a symlink already)
  if [ -d "$src" ] && [ -d "$dst" ] && [ ! -L "$dst" ] && is_in_list "$base" "${MERGE_DIRS[@]}"; then
    added=0
    for child_src in "$src"/*; do
      [ -e "$child_src" ] || continue
      child_base=$(basename "$child_src")
      child_dst="$dst/$child_base"
      if [ ! -e "$child_dst" ] && [ ! -L "$child_dst" ]; then
        ln -s "$child_src" "$child_dst"
        added=$((added+1))
      fi
    done
    [ "$added" -gt 0 ] && MERGED+=("$base(+$added)")
    continue
  fi

  # Tracked file or unknown directory type — leave alone
  KEPT+=("$base")
done
```

**Skipped items (always):**

- `settings.local.json` — per-worktree permissions
- `worktrees.json` — manifest lives only in the main repo
- `memory/` — Claude Code uses its own per-path memory directory; worktree gets a clean memory by design

**Why iterate instead of a hardcoded list:** new top-level items in `.claude/` get picked up automatically. Add new content directory names to `MERGE_DIRS` only if the project introduces a new convention.

Surface `SYMLINKED`, `MERGED`, `KEPT` in the final summary so the user understands what's symlinked, what was merged file-by-file, and what stayed as tracked content (no auto-updates from source-of-truth).

### 8. Write CLAUDE.md overlay

Some projects track `CLAUDE.md` in git. Writing over it would clobber the tracked file, so pick the overlay target conditionally:

```bash
if [ -f "$WORKTREE_DIR/CLAUDE.md" ]; then
  # CLAUDE.md is tracked in this branch — write to CLAUDE.local.md instead.
  # Claude Code loads both CLAUDE.md and CLAUDE.local.md from cwd, and
  # CLAUDE.local.md is conventionally gitignored.
  OVERLAY_FILE="$WORKTREE_DIR/CLAUDE.local.md"
  IMPORT_LINE=""
elif [ -f "$MAIN_REPO/CLAUDE.md" ]; then
  # Main repo has CLAUDE.md but worktree doesn't (e.g. gitignored). Write
  # overlay as CLAUDE.md and @-import the main one so it loads alongside.
  OVERLAY_FILE="$WORKTREE_DIR/CLAUDE.md"
  IMPORT_LINE="@$MAIN_REPO/CLAUDE.md"
else
  # No CLAUDE.md anywhere — overlay stands alone.
  OVERLAY_FILE="$WORKTREE_DIR/CLAUDE.md"
  IMPORT_LINE=""
fi
```

Write `$OVERLAY_FILE` with this content (substitute placeholders, append the import line at the end if non-empty):

```markdown
# Task: {TASK_ID} — {TASK_DESCRIPTION}

## Task metadata
- ID: {TASK_ID}
- Branch: {BRANCH_NAME}
- Base: {BASE_BRANCH} @ {BASE_COMMIT}
- Created: {YYYY-MM-DD}
- Worktree: {WORKTREE_DIR}
- Main repo: {MAIN_REPO}

## Goal / Definition of done
<!-- Fill in -->

## Context
<!-- Ticket link, design notes, PM input -->

## Decisions
<!-- Architectural / implementation decisions made during this task -->

## Open questions
<!-- -->

## Progress
- [ ] ...

---

{IMPORT_LINE}
```

The `@<path>` line is a Claude Code import directive. Use the absolute path so it resolves regardless of cwd. When `CLAUDE.md` is already present in the worktree (tracked case), the import line is unnecessary — the main file auto-loads from cwd alongside `CLAUDE.local.md`.

Surface in the final summary which file was written so the user knows where to add their task notes.

### 9. Copy env files (best effort)

```bash
for f in .env .env.local .env.development; do
  [ -f "$MAIN_REPO/$f" ] && cp "$MAIN_REPO/$f" "$WORKTREE_DIR/$f"
done
```

Never copy `.env.example` — it's a template, not real config.

### 10. Update manifest (atomic)

```bash
mkdir -p "$MAIN_REPO/.claude"
MANIFEST="$MAIN_REPO/.claude/worktrees.json"
[ -f "$MANIFEST" ] || echo '{"version":1,"worktrees":[]}' > "$MANIFEST"

NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)
NEW_ENTRY=$(jq -n \
  --arg task_id "$TASK_ID" \
  --arg task_description "$TASK_DESCRIPTION" \
  --arg slug "$TASK_SLUG" \
  --arg branch "$BRANCH_NAME" \
  --arg path "$WORKTREE_DIR" \
  --arg base_branch "$BASE_BRANCH" \
  --arg base_commit "$BASE_COMMIT" \
  --arg created_at "$NOW" \
  '{task_id:$task_id, task_description:$task_description, slug:$slug, branch:$branch, path:$path, base_branch:$base_branch, base_commit:$base_commit, created_at:$created_at, status:"active"}')

jq ".worktrees += [$NEW_ENTRY]" "$MANIFEST" > "$MANIFEST.tmp" && mv "$MANIFEST.tmp" "$MANIFEST"
```

### 11. Append manifest to .gitignore (idempotent)

```bash
GITIGNORE="$MAIN_REPO/.gitignore"
LINE=".claude/worktrees.json"
[ -f "$GITIGNORE" ] || touch "$GITIGNORE"
grep -qxF "$LINE" "$GITIGNORE" || printf '\n# claude worktree manifest\n%s\n' "$LINE" >> "$GITIGNORE"
```

### 12. Run init hook or fallback

If `--no-hook` not set and `${MAIN_REPO}/.claude/worktree-init.sh` exists and is executable:

```bash
(
  cd "$WORKTREE_DIR" && \
  WORKTREE_TASK_ID="$TASK_ID" \
  WORKTREE_TASK_DESCRIPTION="$TASK_DESCRIPTION" \
  WORKTREE_BRANCH="$BRANCH_NAME" \
  WORKTREE_BASE_BRANCH="$BASE_BRANCH" \
  WORKTREE_BASE_COMMIT="$BASE_COMMIT" \
  WORKTREE_PATH="$WORKTREE_DIR" \
  WORKTREE_MAIN_REPO="$MAIN_REPO" \
  bash "$MAIN_REPO/.claude/worktree-init.sh"
)
INIT_EXIT=$?
INIT_MODE="hook"
```

If hook missing AND `--no-deps` not set, run a fallback in `$WORKTREE_DIR`. Detect by lockfile/project file presence and run the matching command:

| Marker file | Command |
|---|---|
| `pnpm-lock.yaml` | `pnpm install` |
| `yarn.lock` | `yarn install` |
| `package-lock.json` or `package.json` | `npm install` |
| `requirements.txt` | `pip install -r requirements.txt` |
| `Pipfile.lock` | `pipenv install` |
| `poetry.lock` | `poetry install` |
| `go.mod` | `go mod download` |
| `Gemfile` | `bundle install` |
| `Cargo.toml` | `cargo fetch` |
| `*.sln` or `*.csproj` | `dotnet restore` |
| _(none)_ | record `skipped` |

Set `INIT_MODE="fallback:<tool>"` or `INIT_MODE="skipped"`.

If init exit code is non-zero:

- Update manifest entry: set `status: "init_failed"` (atomic update via jq + tmp + mv).
- Print a warning, but **do NOT remove the worktree**. The user fixes locally.

If init succeeds, the manifest entry stays `active`.

### 13. Print summary

```
Worktree ready:
  task:     {TASK_ID} — {TASK_DESCRIPTION}
  branch:   {BRANCH_NAME}
  base:     {BASE_BRANCH} @ {BASE_COMMIT}
  path:     {WORKTREE_DIR}
  overlay:  {basename of OVERLAY_FILE}  ({with-@import | standalone | alongside-tracked-CLAUDE.md})
  symlinks: {comma-list from SYMLINKED — fast-path symlinks at .claude/ top level}
  merged:   {comma-list from MERGED — content dirs where missing children were symlinked, e.g. agents(+13)}
  kept:     {comma-list from KEPT — tracked files/dirs left untouched (or "none")}
  init:     {ok | failed | skipped}  ({INIT_MODE})

Next step (run in a new terminal):
  cd "{WORKTREE_DIR}" && claude
```

If `pbcopy` is available on the system, also pipe `cd "{WORKTREE_DIR}" && claude` to it and append a line `(copied to clipboard)`.

The `kept` line matters: any item left as a tracked file won't auto-update when the source-of-truth `.claude/` changes — the user has to rebase onto a branch with the new content (or delete the tracked file before the next worktree run).

## Hook contract

A project may provide `<main-repo>/.claude/worktree-init.sh` (must be executable). When present, it runs after worktree creation with:

- **cwd** = the new worktree directory
- **env**:
  - `WORKTREE_TASK_ID`
  - `WORKTREE_TASK_DESCRIPTION`
  - `WORKTREE_BRANCH`
  - `WORKTREE_BASE_BRANCH`
  - `WORKTREE_BASE_COMMIT`
  - `WORKTREE_PATH`
  - `WORKTREE_MAIN_REPO`
- **exit 0** = success; non-zero = mark worktree `init_failed` in the manifest

Example for a .NET project:

```bash
#!/usr/bin/env bash
set -e
dotnet restore CashMachine5.sln /p:SkipZebraScanner=true
```

Example for a Bun monorepo:

```bash
#!/usr/bin/env bash
set -e
bun install
bun run codegen
```

## Rules

- Always derive `MAIN_REPO` from `git rev-parse --git-common-dir`. Never `--show-toplevel`.
- Never `git pull` on the main repo. Always `git fetch` + create worktree from `origin/<base>`.
- Pre-flight checks must fail-fast before any state mutation.
- All manifest writes are atomic (write to `$MANIFEST.tmp`, then `mv`).
- `.claude/` items are **symlinked**, never copied — so improvements in main repo propagate instantly. Exception: items already present in the worktree (because the project tracks them in git) are left untouched; they cannot be symlinked over.
- `CLAUDE.md` is similarly conditional: if the project tracks it, the task overlay goes to `CLAUDE.local.md` instead. Both files load when both are present.
- Init failure does NOT roll back the worktree. Mark `init_failed` and let the user resolve it.
- macOS/Linux only in v1. Windows symlink/junction handling is a TODO.

## Examples

| Invocation | Branch | Path |
|---|---|---|
| `/worktree-new CF-42 fix payment flow` | `task/CF-42-fix-payment-flow` | `../<repo>-fix-payment-flow` |
| `/worktree-new TUKAS-7 add CSV export` | `task/TUKAS-7-add-csv-export` | `../<repo>-add-csv-export` |
| `/worktree-new #123 quick patch --offline` | `task/123-quick-patch` | `../<repo>-quick-patch` |
| `/worktree-new CF-42 refactor auth --base develop` | `task/CF-42-refactor-auth` (from `origin/develop`) | `../<repo>-refactor-auth` |
