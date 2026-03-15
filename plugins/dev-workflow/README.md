# Dev Workflow

Developer workflow tools — git branching, task loading, commit preparation, live testing, and effort estimation.

## What's included

### Commands
- `/git-create-branch` — Create a new git branch from a task description with conventional naming
- `/task-load-clickup` — Load a ClickUp task by ID or name and display its details

### Skills
- `/git-prepare-commit` — Unstage all files, stage only relevant changes, and generate a concise commit title
- `/test-live` — Test features against local Docker containers, rebuilding services if needed
- `/task-estimate` — Estimate task effort with structured methodology and examples

## Installation

```
/plugin marketplace add dvomar/claude-codeworks
/plugin install dev-workflow@codeworks
```

## Usage

Create a branch for your task:
```
/git-create-branch Add user authentication
```

Prepare a clean commit:
```
/git-prepare-commit
```

Test against Docker:
```
/test-live
```
