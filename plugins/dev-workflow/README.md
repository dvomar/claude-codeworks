# Dev Workflow

Developer workflow tools — git branching, task loading, commit preparation, live testing, and effort estimation.

## What's included

### Commands
- `/create-branch` — Create a new git branch from a task description with conventional naming
- `/load-task` — Load a ClickUp task by ID or name and display its details

### Skills
- `/prepare-commit` — Unstage all files, stage only relevant changes, and generate a concise commit title
- `/live-test` — Test features against local Docker containers, rebuilding services if needed
- `/estimate-task` — Estimate task effort with structured methodology and examples

## Installation

```
/plugin marketplace add dvomar/claude-codeworks
/plugin install dev-workflow@codeworks
```

## Usage

Create a branch for your task:
```
/create-branch Add user authentication
```

Prepare a clean commit:
```
/prepare-commit
```

Test against Docker:
```
/live-test
```
