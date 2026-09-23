# Dev Workflow

Developer workflow tools — git branching and worktrees, commit preparation, time and cost estimation, integration proposals, an English-language policy for repositories, and HTML-to-PDF rendering.

## What's included

### Commands
- `/mdv-git-create-branch` — Create a new git branch from a task description with conventional naming
- `/mdv-worktree-new` — Create a git worktree for a task with branch, dependencies, `.claude/` symlinks and manifest tracking
- `/mdv-worktree-list` — List managed worktrees, including orphans and gone entries (read-only)
- `/mdv-worktree-remove` — Remove a managed worktree after checking for uncommitted and unmerged work
- `/mdv-html-to-pdf` — Render an HTML file to PDF via headless Chrome

### Skills
- `/mdv-git-prepare-commit` — Unstage all files, stage only relevant changes, and generate a concise commit title
- `/mdv-task-estimate` — Estimate time and cost of a development task
- `/mdv-integration-proposal` — Design an integration or feature as two HTML documents: internal and customer-facing
- `/mdv-enforce-english` — Record the English-language policy in CLAUDE.md and audit the repo for text that breaks it

## Installation

```
/plugin marketplace add dvomar/claude-codeworks
/plugin install dev-workflow@codeworks
```

## Usage

Create a branch for your task:
```
/mdv-git-create-branch Add user authentication
```

Prepare a clean commit:
```
/mdv-git-prepare-commit
```

Make a repository English and keep it that way:
```
/mdv-enforce-english
```
