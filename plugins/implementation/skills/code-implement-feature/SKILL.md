---
name: code-implement-feature
description: Complete feature implementation workflow. Orchestrator-led clarification, then spec-writer → task-planner → implementer (all Opus 4.8), closed by a /code-review-feature gate.
---

# Feature Implementation Workflow

This skill orchestrates a high-quality feature implementation pipeline. The orchestrator (this main session) runs the **interactive clarification itself**, then delegates spec, planning, and implementation to specialized agents, and closes with a `/code-review-feature` gate.

## Models

All pipeline agents run on the top **Opus** tier at `xhigh` reasoning effort (`model: opus`, `effort: xhigh`) — both the preparation (`req-clarifier` scout, `spec-writer`, `task-planner`) and the implementation (`implementer`). The architectural judgment baked into the spec/plan and the convention-correctness of the generated code are both high-stakes: a spec/plan that misreads the project's conventions, or code that quietly violates them, produces subtly-wrong results — so neither stage is downgraded. The `opus` alias auto-tracks the latest Opus, which keeps this template portable across projects; to freeze a specific version, replace `opus` with an exact model ID (e.g. `claude-opus-4-8`).

## Prerequisites

Conventions live in CLAUDE.md and MEMORY.md (auto-injected). For detail, the agents read `.claude/knowledge/`. If the `## Codebase Conventions (Auto-Generated)` section is empty, run `/code-analyze-codebase` first.

## When to Use

- Implement a new feature or functionality
- Make a significant code change that benefits from planning + review

## Workflow Overview

```
User Request
    ↓
┌─────────────────────────────────────────────┐
│ 1. Clarification (ORCHESTRATOR, Opus 4.8)    │
│    • optional: req-clarifier scout gathers   │
│      context + proposes questions            │
│    • orchestrator asks user (AskUserQuestion)│
│      — 1-3 rounds, then confirm              │
│    → orchestrator writes clarifications.md   │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│ 2. spec-writer (Opus 4.8)                    │
│    • formal spec, 3x dimensional self-review │
│    → task-spec.md                            │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│ 3. task-planner (Opus 4.8)                   │
│    • ordered sub-tasks by dependency         │
│    → task-breakdown.md                        │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│ 4. implementer (Opus 4.8) — ONE call         │
│    • loops ALL sub-tasks in order            │
│    • focused self-check per sub-task         │
│    → working code + tests                    │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│ 5. /code-review-feature gate — reviews the   │
│    files the implementer changed             │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│ 6. Cleanup (ORCHESTRATOR) — ask user to      │
│    remove .claude/tasks/[feature-name]/      │
└─────────────────────────────────────────────┘
    ↓
Feature Complete
```

## Output Structure

```
.claude/tasks/[feature-name]/
├── clarifications.md   # written by the orchestrator from the Q&A
├── task-spec.md        # from spec-writer
└── task-breakdown.md   # from task-planner (TOC + full breakdown in one file)
```

Self-reviews are performed inline by each agent (no separate review files). The real review is the `/code-review-feature` gate on the files the implementer changed. The orchestrator removes the folder after review passes.

## Quality Gates

### Gate 1: Requirements (orchestrator + req-clarifier scout)
- Context loaded, similar code identified
- All questions answered, user confirms understanding

### Gate 2: Specification (spec-writer)
- Pass 1: Completeness · Pass 2: Convention compliance · Pass 3: Feasibility

### Gate 3: Planning (task-planner)
- Dependencies identified · sub-tasks 15-60 min · verification checklists included

### Gate 4: Implementation (implementer)
- Per sub-task: correctness + conventions + KISS self-check, build passes

### Gate 5: Review (/code-review-feature)
- Independent review of the files the implementer changed — separate from the author who wrote them

## Best Practices

1. **Be thorough in clarification** — sharp requirements save time later.
2. **Let spec-writer complete all reviews** — don't skip quality gates.
3. **Trust the dependency order** — the implementer executes sub-tasks in sequence.
4. **Don't skip the /code-review-feature gate** — it's the independent review.

### When to Skip Parts
- **Small changes**: skip clarification, start at spec-writer.
- **Crystal-clear requirements**: start at task-planner.
- **Bug fixes**: implementer with a clear scope, then /code-review-feature.

## Integration with Other Skills

- **After**: `/code-optimize` for performance optimization.
- **Before**: `/code-analyze-codebase` if conventions are missing.

## Execution (BLOCKING — do not just describe the workflow)

When `/code-implement-feature [description]` is invoked, you (the orchestrator) MUST run this pipeline. Do NOT summarize and stop — execute it.

1. Derive a kebab-case `[feature-name]` from the description and create `.claude/tasks/[feature-name]/`.
2. **CLARIFY — you do this yourself, NOT a subagent:**
   - a. *(Optional)* Call `Agent` with `subagent_type: "req-clarifier"`, passing the feature description, to get a context + proposed-questions packet. This keeps heavy codebase search out of your context. It returns a packet — it does NOT talk to the user.
   - b. Ask the user the clarifying questions via `AskUserQuestion`. Run 1-3 rounds until requirements are clear, then confirm the summary.
   - c. Write the confirmed requirements to `clarifications.md`.
   - Do NOT expect a subagent to run interactive Q&A — subagents run to completion and cannot pause for the user.
3. Call `Agent` with `subagent_type: "spec-writer"`, pointing at `clarifications.md`. Wait for `task-spec.md`.
4. Call `Agent` with `subagent_type: "task-planner"`, pointing at `task-spec.md`. Wait for `task-breakdown.md`.
5. Call `Agent` with `subagent_type: "implementer"` **ONCE**, passing the breakdown file. It loops through ALL sub-tasks in order in a single context and returns when every sub-task is `[x]` and the build passes. (For an unusually large breakdown — more than ~8 sub-tasks — you may split into sequential batches, but NEVER run sub-tasks in parallel: later ones depend on earlier ones.)
6. **REVIEW gate:** run the `/code-review-feature` skill on the files the implementer created/modified (collect the paths from the implementer's report). Address findings (re-invoke `implementer` or fix directly) until the review is clean.
7. **CLEANUP:** report a short summary of what was implemented, then ask the user whether to delete `.claude/tasks/[feature-name]/` (default: delete). You own this step — the implementer does not delete scaffolding.

Skip earlier steps only if the user explicitly says so (e.g. "skip clarification, the spec is already written"). Otherwise run the full pipeline.

## Example Usage

```
User: /code-implement-feature Add product category management with CRUD operations
Assistant:
[Optionally calls req-clarifier scout → context + proposed questions]
[Asks the user via AskUserQuestion — scope, fields, validation, UI — 1-3 rounds, confirms]
[Writes clarifications.md]
[Calls spec-writer → task-spec.md]
[Calls task-planner → task-breakdown.md with 6 sub-tasks]
[Calls implementer ONCE → loops all 6 sub-tasks, each built + self-checked]
[Runs /code-review-feature on the changed files → addresses findings]
[Reports completion and asks whether to delete .claude/tasks/product-category-management/]
```
