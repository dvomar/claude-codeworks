---
name: prepare-commit
description: Unstage all files, stage only implementation-relevant changes, and generate a concise English commit title.
---

# Prepare Commit

Prepares a clean, focused commit by staging only relevant implementation files and proposing a Conventional Commits title.

## Process

Follow these steps in order:

### 1. Clear staging area

```bash
git reset HEAD
```

### 2. Analyze working tree changes

Run `git status` and `git diff` to see all modified, added, and untracked files.

### 3. Read recent commit history

```bash
git log --oneline -10
```

Use this to match the repository's commit message style and conventions.

### 4. Identify relevant files

From the working tree changes, determine which files belong to the current implementation or fix.

**Always exclude** (unless user explicitly asks to include them):
- `.claude/` directory
- `docs/` directory
- `scripts/` directory
- `implementation_plans/` directory
- `REPORT-*` files
- `debug-*` files
- `*.md` files in the repository root (except source code documentation that is part of the feature)
- `*.txt` files in the repository root

**Always include**:
- Source code changes (`.cs`, `.ts`, `.js`, `.json` config changes tied to the feature)
- Migration files related to the implementation
- Test files related to the implementation
- Validator, converter, and service files that are part of the feature

Use judgment: if a file change is clearly unrelated to the main body of work, exclude it.

### 5. Stage relevant files

```bash
git add <file1> <file2> ...
```

Stage only the identified relevant files by name. Never use `git add -A` or `git add .`.

### 6. Show staged changes

```bash
git diff --staged --stat
```

Display this for user review.

### 7. Generate commit title

Create a short, concise English commit title following Conventional Commits format:
- Prefix: `feat:`, `fix:`, `refactor:`, `test:`, `docs:`, `chore:`, etc.
- Max ~72 characters
- Describes the **what** and **why** based on the actual staged diff content
- No `Co-Authored-By` lines, no AI mentions, no Claude references

### 8. Present results

Display:
- List of staged files
- List of excluded files (and why)
- Proposed commit title

Then **stop**. Do NOT create the commit. The user will confirm, adjust, or ask for changes.

## Rules

- Never auto-commit. Only prepare the staging area and propose a title.
- Never stage files from the exclusion list unless the user explicitly requests it.
- If there are no relevant changes to stage, report that clearly and stop.
- If unsure whether a file is relevant, ask the user.
