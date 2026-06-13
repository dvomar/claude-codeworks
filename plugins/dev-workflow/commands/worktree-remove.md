Remove a git worktree managed by `/worktree-new`. Performs safety checks (dirty working tree, unmerged commits) before destructive operations. Updates the manifest atomically.

## Input

`$ARGUMENTS`:

- **TASK_ID** — required (e.g., `CF-42`). If missing, ask the user.
- `--force` — bypass dirty / unmerged-commit checks
- `--keep-branch` — do not delete the local branch
- `--prune` — fully delete the manifest entry (default: mark `status: "removed"`)

## Steps

### 1. Resolve main repo and manifest

```bash
MAIN_REPO=$(dirname "$(git rev-parse --git-common-dir)")
MANIFEST="$MAIN_REPO/.claude/worktrees.json"
```

If `$MANIFEST` does not exist, fail with: `No worktrees registered. Nothing to remove.`

### 2. Lookup entry

Find the entry where `task_id == TASK_ID` and `status` is `active` OR `init_failed`:

```bash
ENTRY=$(jq --arg id "$TASK_ID" \
  '.worktrees[] | select(.task_id == $id and (.status == "active" or .status == "init_failed"))' \
  "$MANIFEST")
```

If empty:

- If an entry exists with `status == "removed"`, tell the user it's already removed and offer `--prune` to delete the record entirely.
- Otherwise fail: `No active worktree for TASK_ID '<id>'. Run /worktree-list.`

Extract `path`, `branch`, `base_branch` from the entry.

### 3. Check whether the path still exists

```bash
PATH_EXISTS=$( [ -d "$path" ] && echo 1 || echo 0 )
```

If the path is gone, skip the safety checks (there is nothing to lose locally) and jump straight to step 5 — but still confirm with the user before deleting the branch.

### 4. Safety checks (skip if `--force` or path missing)

**Dirty working tree:**

```bash
DIRTY=$(git -C "$path" status --porcelain | wc -l | tr -d ' ')
if [ "$DIRTY" -gt 0 ]; then
  echo "Worktree has $DIRTY uncommitted change(s). Re-run with --force to discard them."
  exit 1
fi
```

**Unmerged commits:**

```bash
git -C "$MAIN_REPO" fetch origin "$base_branch" --quiet 2>/dev/null || true

if git -C "$MAIN_REPO" rev-parse --verify --quiet "origin/$base_branch" >/dev/null; then
  CMP="origin/$base_branch"
else
  CMP="$base_branch"
fi

AHEAD=$(git -C "$MAIN_REPO" rev-list --count "$CMP..$branch" 2>/dev/null || echo 0)
if [ "$AHEAD" -gt 0 ]; then
  echo "Branch '$branch' has $AHEAD commit(s) not in $CMP. Re-run with --force to discard them."
  exit 1
fi
```

**Stash entries (informational, not blocking):**

```bash
STASH_COUNT=$(git -C "$path" stash list 2>/dev/null | wc -l | tr -d ' ')
[ "$STASH_COUNT" -gt 0 ] && echo "Warning: $STASH_COUNT stash entries on this branch will be lost."
```

### 5. Remove worktree

If `$PATH_EXISTS == 1`:

```bash
if [ -n "$FORCE" ]; then
  git -C "$MAIN_REPO" worktree remove --force "$path"
else
  git -C "$MAIN_REPO" worktree remove "$path"
fi
```

If `$PATH_EXISTS == 0`:

```bash
git -C "$MAIN_REPO" worktree prune
```

### 6. Delete branch (skip if `--keep-branch`)

```bash
if git -C "$MAIN_REPO" show-ref --verify --quiet "refs/heads/$branch"; then
  if [ -n "$FORCE" ]; then
    git -C "$MAIN_REPO" branch -D "$branch"
  else
    if ! git -C "$MAIN_REPO" branch -d "$branch" 2>/dev/null; then
      echo "Branch '$branch' is not fully merged. Re-run with --force to delete, or use --keep-branch to keep it."
      exit 1
    fi
  fi
fi
```

### 7. Update manifest (atomic)

If `--prune` (or the entry is already `status: "removed"`):

```bash
jq --arg id "$TASK_ID" '.worktrees |= map(select(.task_id != $id))' "$MANIFEST" > "$MANIFEST.tmp"
```

Otherwise mark removed:

```bash
NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)
jq --arg id "$TASK_ID" --arg now "$NOW" \
  '.worktrees |= map(if .task_id == $id then .status = "removed" | .removed_at = $now else . end)' \
  "$MANIFEST" > "$MANIFEST.tmp"
```

Then atomically:

```bash
mv "$MANIFEST.tmp" "$MANIFEST"
```

### 8. Print summary

```
Removed worktree:
  task:     {TASK_ID}
  branch:   {branch}  ({deleted | kept})
  path:     {path}    ({removed | already missing})
  manifest: {marked removed | pruned}
```

## Rules

- Never delete uncommitted work without `--force`.
- Never delete unmerged commits without `--force`.
- Manifest writes are atomic (`tmp` + `mv`).
- If the worktree path is already missing, run `git worktree prune` instead of `git worktree remove`.
- The main repo itself is never in the manifest, but defensively refuse to operate on `$MAIN_REPO` if somehow targeted.
- After a successful remove, the branch is deleted by default. Use `--keep-branch` to preserve it (e.g., for an in-flight PR that should stay reviewable).

## Examples

```
/worktree-remove CF-42                           # safe remove if clean
/worktree-remove CF-42 --force                   # discard uncommitted changes / unmerged commits
/worktree-remove CF-42 --keep-branch             # keep the branch (e.g., open PR)
/worktree-remove CF-42 --prune                   # remove + delete manifest entry entirely
/worktree-remove CF-42 --force --keep-branch     # combine flags
```
