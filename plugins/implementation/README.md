# Implementation

End-to-end implementation workflow — requirements clarification, spec writing, task planning, and implementation, closed by a review gate.

## What's included

### Agents
- **req-clarifier** — Gathers codebase context and proposes sharp clarifying questions (the Q&A itself runs in your session)
- **spec-writer** — Creates a formal task specification from the clarifications
- **task-planner** — Breaks the specification into ordered sub-tasks
- **implementer** — Implements all sub-tasks in dependency order with a focused self-check per sub-task

### Skills
- `/mdv-code-implement-feature` — Complete feature workflow: clarification, then spec-writer → task-planner → implementer, closed by a `/mdv-code-review-feature` gate

The review gate uses `/mdv-code-review-feature` from the `code-review` plugin; install both.

## Installation

```
/plugin marketplace add dvomar/claude-codeworks
/plugin install implementation@codeworks
/plugin install code-review@codeworks
```

## Usage

```
/mdv-code-implement-feature Add CSV export to the orders list
```
