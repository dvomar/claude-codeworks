List all git worktrees managed by `/worktree-new`. Joins the manifest (`.claude/worktrees.json`) with `git worktree list --porcelain` so you see active worktrees, orphans (in git but not in manifest), and gone entries (in manifest but missing on disk). Read-only — never mutates state.

## Input

`$ARGUMENTS` may contain:

- `--all` — also include entries with `status == "removed"` (default: hide them)
- `--json` — emit raw JSON instead of a human-readable table

## Steps

### 1. Resolve main repo and manifest

```bash
MAIN_REPO=$(dirname "$(git rev-parse --git-common-dir)")
MANIFEST="$MAIN_REPO/.claude/worktrees.json"
```

If `$MANIFEST` does not exist, print:

```
No worktrees yet. Use /worktree-new <TASK_ID> <description> to create one.
```

and exit.

### 2. Read manifest

```bash
jq '.worktrees' "$MANIFEST"
```

Filter out entries with `status == "removed"` unless `--all`.

### 3. Read git worktree list

```bash
git -C "$MAIN_REPO" worktree list --porcelain
```

Parse the porcelain output (records separated by blank lines; each record has `worktree <path>`, `HEAD <sha>`, `branch <ref>` or `detached`). Always exclude the record whose path equals `$MAIN_REPO`.

### 4. Compute join

For each manifest entry, find a matching git record by canonical absolute path. Categorize:

- **active** — in manifest AND in git AND path exists on disk
- **gone** — in manifest, but path is missing OR not in `git worktree list`
- **orphan** — in `git worktree list`, but no matching manifest entry (created by hand or another tool)

Path comparison must canonicalize first (resolve symlinks, normalize trailing slashes, e.g., via `realpath` or `cd "$p" && pwd -P`).

### 5. Compute live status

For each `active` entry:

```bash
DIRTY=$(git -C "$path" status --porcelain | wc -l | tr -d ' ')
```

- 0 → `clean`
- N>0 → `N dirty`

If the manifest entry already has `status: "init_failed"`, surface that label instead of `clean`/`dirty`.

For age, parse `created_at` (ISO8601 UTC) and format the delta as `Nm` / `Nh` / `Nd` / `Nw` (whichever fits best).

### 6. Format output

If `--json`:

```json
{
  "main_repo": "/abs/path",
  "active":  [ ...full manifest entries with computed dirty count... ],
  "orphan":  [ { "path": "...", "branch": "..." } ],
  "gone":    [ ...manifest entries... ]
}
```

Otherwise print a table. Compute column widths from data. Example:

```
TASK_ID    BRANCH                          AGE   STATUS         PATH
CF-42      task/CF-42-fix-payment-flow     2d    clean          ../repo-fix-payment-flow
TUKAS-7    task/TUKAS-7-add-csv-export     5h    3 dirty        ../repo-add-csv-export
INIT-9     task/INIT-9-broken              1d    init_failed    ../repo-broken
```

If there are orphans:

```

Orphans (in git, not tracked in manifest):
  feature/manual                           ../repo-manual
```

If there are gone entries:

```

Gone (in manifest, missing on disk — run /worktree-remove --prune to clean up):
  CF-99    task/CF-99-old-thing            ../repo-old-thing
```

Footer (only if there is at least one active or orphan):

```

Use /worktree-remove <TASK_ID> to remove a worktree.
```

### 7. Empty state

If manifest exists but contains no entries (and `git worktree list` shows only the main repo), print the same empty-state message from step 1.

## Rules

- Read-only. Never write to the manifest, never run git commands that mutate state.
- The manifest is not authoritative on its own — always cross-reference with `git worktree list`.
- Path matching MUST be canonical to avoid false orphan/gone classifications.
- Manifest stores `created_at` in UTC. Ages are computed from UTC; the table itself just shows relative age, no absolute timestamps.
- Display paths relative to `$MAIN_REPO/..` for readability when they live as siblings (e.g., `../repo-foo`); show absolute path otherwise.

## Examples

```
/worktree-list
/worktree-list --all
/worktree-list --json
```
