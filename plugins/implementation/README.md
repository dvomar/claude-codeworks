# Implementation

End-to-end implementation workflow — from requirements clarification through spec writing, task planning, and guided implementation with self-review at each stage.

## What's included

### Agents
- **req-clarifier** — Interactively clarifies requirements through Q&A sessions
- **spec-writer** — Creates formal task specifications with 3x self-review
- **task-planner** — Breaks specifications into ordered sub-tasks for step-by-step implementation
- **implementer** — Implements sub-tasks with 3x self-review following project conventions

### Skills
- `/code-implement-feature` — Complete feature implementation workflow using all 4 agents with quality gates
- `/code-quick-implement` — Fast implementation following documented conventions, skipping the full workflow

## Installation

```
/plugin marketplace add dvomar/claude-codeworks
/plugin install implementation@codeworks
```

## Usage

Full guided implementation with quality gates:
```
/code-implement-feature
```

Quick implementation when requirements are clear:
```
/code-quick-implement
```
