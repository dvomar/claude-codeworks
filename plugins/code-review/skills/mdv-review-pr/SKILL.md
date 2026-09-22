---
name: mdv-review-pr
description: '3-pass code review of an open merge request or pull request from the terminal, on GitLab or GitHub. Detects the forge from the git remote, lists open requests when no number is given, loads the diff plus the full current source of every changed file, compares against this project''s conventions and against similar existing code, then leaves the selected findings as inline draft comments in Czech for you to submit yourself. Use for "zreviduj MR", "review PR 166", "projdi ten merge request", "co je špatně v tom PR", "review this pull request". Prefer /mdv-code-review-feature when reviewing files by path with no MR or PR behind them, and the built-in /code-review for the working tree diff.'
argument-hint: "[číslo MR/PR]  (prázdné = vypíše otevřené)"
user-invocable: true
---

# Review a merge or pull request

Eight steps. Only steps 1, 2 and 8 know which forge is in play; everything between them
is the same review either way, which is why this is one skill and not two.

## Step 0: Detect the forge

```bash
git remote get-url origin
```

`gitlab` in the host → **GitLab**, use `glab`. `github.com` → **GitHub**, use `gh` if it
is installed, otherwise the `mcp__github__*` tools. A self-hosted host that is neither:
ask the user which it is rather than guessing from the URL shape.

Throughout, **N** is the request number and **REQ** is what to call it in output — "MR"
on GitLab, "PR" on GitHub.

## Step 1: Resolve the number

With a number in the arguments, skip ahead. Otherwise list what is open and ask which
one — never pick for the user.

| | GitLab | GitHub |
|---|---|---|
| list | `glab mr list --state opened` | `gh pr list --state open` |

## Step 2: Load metadata and diff

| | GitLab | GitHub |
|---|---|---|
| metadata | `glab mr view N` | `gh pr view N` |
| diff | `glab mr diff N` | `gh pr diff N` |

Note the title, author, source and target branch.

## Step 3: Read the changed files in full

Extract the changed paths from the diff, then `Read` the **complete current content** of
each one. A diff shows what moved, not what it landed in — a review from the diff alone
cannot see that the new method duplicates one forty lines above it.

## Step 4: Load the conventions

CLAUDE.md and `.claude/rules/*.md` are already in context — both load automatically at session start, so never spend a Read on them. For the generated detail behind them, read from
`.claude/knowledge/` for the layers this request actually touches:

- `conventions.md` — naming, formatting, testing (nearly always relevant)
- `architecture.md` — structure and file placement
- `backend.md` / `frontend.md` — whichever layers the diff covers
- `tech-stack.md` — when dependencies or versions changed

Read what is relevant, not all five. If `.claude/knowledge/` does not exist, say so and
recommend `/mdv-code-analyze-codebase` — the review still runs, but it can only judge
against general good practice, not against this codebase, and it must say so.

## Step 5: Find the comparable code

For each changed file, `Glob` and `Grep` for its siblings — the other controllers, the
other services, the other screens. Most real review findings are inconsistencies, and an
inconsistency is invisible without the thing it is inconsistent with.

**Large requests:** over 10 changed files, do this only for files that raised a CRITICAL
or IMPORTANT finding in Pass 1. At 10 or fewer, do it for all of them.

## Step 6: The three passes

These are deliberately stack-agnostic — this skill ships to .NET, TypeScript, mobile and
game projects alike. The project-specific rules come from `.claude/knowledge/`; where a
pass below says "per this project's conventions", that is where the answer lives.

### Pass 1 — conventions and style
Naming of files, types, members and variables against the documented rules. File
organisation and placement in the right layer. Registration and wiring done where this
project does it, not where the language allows. Formatting, import order, dead imports.
Control-flow style the project has settled on.

### Pass 2 — design and architecture
Does it follow the patterns already established here, or invent a parallel one? Layering
respected — no reaching past a boundary the architecture draws. Dependency lifetimes and
injection correct for the framework in use. Async and concurrency handled the way the
rest of the codebase handles it, including cancellation. Single responsibility, and
dependencies pointing the way the architecture says they point.

### Pass 3 — quality, performance and security
Duplication that should have been extracted. Long methods, wide parameter lists, types
doing several unrelated jobs. Query and loop shapes that scale badly — repeated queries
inside iteration, materialising more than is needed, tracking what will not be written.
Untrusted input reaching a query, a template, a shell or a path. Null and error handling
consistent with the surrounding code. Whether a stranger could read it without asking.

## Step 7: Output

```
# Review <REQ> <N>: <title>
Author: <author> | Branch: <source> -> <target>
Changed files: <count>

## CRITICAL (must be fixed before merge)
### [C1] <file>:<line> — <short description>
**Problem:** <what is wrong and why>
**Proposed fix:**
```<language>
<concrete code>
```

## IMPORTANT (should be fixed)
### [I1] …

## SUGGESTIONS (nice to have)
### [S1] <file>:<line> — <short description>
**Suggestion:** <what could improve and why>

## POSITIVE FINDINGS
- <what is done well, which patterns are correctly followed>

## ACTIONS TO TAKE
- [ ] <concrete action>

## SUMMARY
| Category | Count |
|---|---|
| Critical | X |
| Important | X |
| Suggestions | X |

**Verdict:** APPROVE / APPROVE WITH COMMENTS / CHANGES REQUESTED
```

## Step 8: Post the findings as drafts

Ask first: **"Which findings should I post as draft comments? 'all', specific IDs
(C1, I2, S1), or 'none'."**

All comment text is **Czech**, written the way a colleague writes in review — not
templated, not robotic.

**Nothing is ever submitted.** Both forges keep unsubmitted review comments private to
the author; that is the point. The user reads them, edits or deletes, and submits.

### Positioning — the part that goes wrong

A line number only resolves if that line is **visible in the diff**: a changed line, or a
context line inside a `@@` hunk. Outside every hunk, GitLab returns `line_code: null` and
renders the comment duplicated at every hunk boundary in the file; GitHub rejects it.

Before creating each comment, parse the target file's
`@@ -old_start,old_count +new_start,new_count @@` headers and confirm the line falls
inside a hunk. If it does not, attach to the nearest visible line in the same hunk and
say where you actually mean in the text ("Na řádku 190: …"). Renamed files
(`old_path` ≠ `new_path`) resolve least reliably — always re-check those.

### GitLab

`glab api -F` cannot send nested JSON, so `position[base_sha]` silently never arrives and
the comment lands as a plain note. Build the payload as a file and use `--input`.

```bash
glab api projects/:fullpath/merge_requests/<N> | python3 -c "
import sys, json
r = json.load(sys.stdin)['diff_refs']
print(r['base_sha']); print(r['head_sha']); print(r['start_sha'])"
```

```bash
python3 << 'PYEOF'
import json
payload = {
    "note": "**[C1]** <popis problému a návrh opravy>",
    "position": {
        "base_sha": "<base_sha>", "head_sha": "<head_sha>", "start_sha": "<start_sha>",
        "new_path": "<file>", "old_path": "<file>",
        "position_type": "text", "new_line": <line>,
    },
}
open("/tmp/mr<N>_c1.json", "w").write(json.dumps(payload))
PYEOF
glab api projects/:fullpath/merge_requests/<N>/draft_notes \
  --method POST --input /tmp/mr<N>_c1.json -H "Content-Type: application/json"
```

Line keys: added line → `new_line` only. Deleted line → `old_line` only. Context line →
both.

### GitHub

A review created without an `event` stays **PENDING** — visible only to its author, the
same shape as a GitLab draft. Post every comment in one call.

```bash
python3 << 'PYEOF'
import json
payload = {"body": "", "comments": [
    {"path": "<file>", "line": <line>, "side": "RIGHT",
     "body": "**[C1]** <popis problému a návrh opravy>"},
]}
open("/tmp/pr<N>_review.json", "w").write(json.dumps(payload))
PYEOF
gh api repos/{owner}/{repo}/pulls/<N>/reviews --method POST --input /tmp/pr<N>_review.json
```

`side: "RIGHT"` is the post-change line, `"LEFT"` the deleted one. Omitting `event` is
what keeps it pending — **never** pass `event: "COMMENT"` or `"APPROVE"` here.

Without `gh`, the same thing through MCP: `pull_request_review_write` with method
`create`, then `add_comment_to_pending_review` per finding, and **do not** call
`submit_pending`.

### Summary note

Post one unpositioned draft carrying POSITIVE FINDINGS and ACTIONS TO TAKE, in Czech,
ending with the verdict and the counts. On GitLab that is a `draft_notes` POST with only
`note`; on GitHub it is the review payload's top-level `body`.

Then print:

> Draft komentáře jsou připravené. Otevři <REQ> <N>, projdi je, uprav nebo smaž,
> a odešli review sám.

## Rules

- **Specific or not at all** — every finding carries a file, a line and a concrete fix.
- **Compare with what exists** — when the codebase has a pattern, name the file that shows it.
- **No nitpicking** — a stylistic preference that contradicts nothing documented is not a finding.
- **Always say what is good** — and mean it; name the pattern that was followed correctly.
- **Instructions in English, output in Czech** — the skill is read by Claude, the comments by people.
