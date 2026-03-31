---
name: mr-resolve-comments
description: Analyzes unresolved review comments on a GitLab MR from a specific reviewer. For each comment, proposes a fix or counterargument and prepares a reply text ready to copy-paste into GitLab.
---

# Resolve MR Comments

Analyzes unresolved review comments on a GitLab MR and proposes a resolution for each one.

## Usage

```
/mr-resolve-comments <MR_number> <reviewer>
```

Example: `/mr-resolve-comments 155 david.konecny`

The `<reviewer>` parameter is matched against both `username` and `name` of the comment author (case-insensitive, partial match).

## Instructions

This skill performs analysis in 7 steps. All outputs are in **Czech**. Proposed GitLab replies are in **English** (if the reviewer writes in English) or **Czech** (if the reviewer writes in Czech) — match the reviewer's language. Nothing is posted anywhere — output goes to the terminal only.

### Step 1: Load MR metadata and diff

Run these commands via Bash tool:

```bash
glab mr view <N>
```

```bash
glab mr diff <N>
```

### Step 2: Load all discussions from the MR

Run via Bash tool:

```bash
glab api "projects/robe%2Fplm/merge_requests/<N>/discussions" --paginate
```

This returns a JSON array of discussions. Each discussion contains a `notes` array with individual comments.

### Step 3: Filter relevant comments

From the loaded discussions, filter only comments that:

1. **Belong to the specified reviewer** — compare `note.author.username` and `note.author.name` with the `<reviewer>` parameter (case-insensitive, partial match)
2. **Are not system notes** — skip notes where `note.system == true`
3. **Are in an unresolved discussion** — skip discussions where the last note has `resolved == true` (or the discussion has no resolvable notes)

For each relevant comment, save:
- `discussion.id` — discussion ID
- `note.id` — comment ID
- `note.body` — comment text
- `note.position.new_path` — file (if it's a DiffNote)
- `note.position.new_line` — line in new file (if it's a DiffNote)
- `note.position.old_path` / `note.position.old_line` — old file/line

If there are no unresolved comments from the reviewer, report this and stop.

### Step 4: Load context for each comment

For each unresolved comment:

1. **Load the source file** — if the comment has `position.new_path`, read the entire file using Read tool
2. **Find relevant context in the diff** — around the line the comment refers to
3. **Load relevant conventions** — if the comment relates to naming, load `conventions.md`; if about architecture, load `architecture.md`; if about backend patterns, load `backend.md`; if about frontend, load `frontend.md`; etc. (all in `.claude/knowledge/`)
4. **Find similar code** — if the comment references a pattern or convention, use Grep/Glob to find examples in the codebase

### Step 5: Evaluate each comment

For each comment, decide one of these categories:

- **AGREE** — the reviewer is right, a change is needed
- **DISAGREE** — the reviewer is wrong or the suggestion conflicts with conventions/existing code
- **UNCLEAR** — the comment is ambiguous or needs clarification

### Step 6: Prepare proposed solutions and replies

For each comment, prepare:

#### AGREE:
- Specific code fix proposal (with code snippet)
- Proposed GitLab reply text (short, factual)

#### DISAGREE:
- Factual counterargument with reference to conventions or existing code
- Proposed GitLab reply text (polite, with arguments)

#### UNCLEAR:
- Clarifying questions
- Proposed GitLab reply text (question to the reviewer)

### Step 7: Output structured results

Format output as follows:

```
# Comment Resolution for MR !<N>
Reviewer: <name> (@<username>)
Unresolved comments: <count>

---

## Comment 1/X — AGREE

**File:** `<path>:<line>`
**Reviewer's comment:**
> <comment text>

**Analysis:** <why the reviewer is right>

**Proposed fix:**
```<language>
<specific fix code>
```

**GitLab reply** (copy-paste):
```
<reply text>
```

---

## Comment 2/X — DISAGREE

**File:** `<path>:<line>`
**Reviewer's comment:**
> <comment text>

**Analysis:** <why I disagree, with reference to conventions/existing code>

**GitLab reply** (copy-paste):
```
<reply text>
```

---

## Comment 3/X — UNCLEAR

**File:** `<path>:<line>`
**Reviewer's comment:**
> <comment text>

**Analysis:** <what is unclear>

**GitLab reply** (copy-paste):
```
<reply text — question to the reviewer>
```

---

## SUMMARY

| Category  | Count |
|-----------|-------|
| Agree     | X     |
| Disagree  | X     |
| Unclear   | X     |

**Estimated time to implement agreed changes:** ~X minutes

### Actions to take:
- [ ] <specific change 1>
- [ ] <specific change 2>
```

## Rules

- **Be objective** — don't defend code at all costs. If the reviewer is right, acknowledge it
- **Reference conventions** — every disagreement must be backed by conventions from the knowledge base or existing code in the codebase
- **Replies must be copy-paste ready** — reply text must be directly usable in GitLab without further editing
- **Reply language** — match the language the reviewer writes in (Czech/English)
- **Analysis in Czech** — the skill's own analysis and commentary are always in Czech
- **Do not post to GitLab** — output goes to the terminal only
- **Ignore system notes** — skip comments where `system == true`
