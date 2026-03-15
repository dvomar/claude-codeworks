---
name: code-implement-feature
description: Complete feature implementation workflow using 4 specialized agents. Guides from requirements through implementation with quality gates.
---

# Feature Implementation Workflow

This skill orchestrates the **4-agent implementation workflow** for high-quality feature development.

## Prerequisites

Conventions are available in CLAUDE.md and MEMORY.md (auto-injected into agent context). If the `## Codebase Conventions (Auto-Generated)` section is empty, run `/code-analyze-codebase` first.

## When to Use

Use `/code-implement-feature` when you need to:
- Implement a new feature or functionality
- Make significant code changes
- Build something that requires planning and review

## Workflow Overview

```
User Request
    ↓
┌─────────────────────────────────────┐
│ 1. req-clarifier                    │
│    • 2-3 rounds of Q&A             │
│    • Loads conventions              │
│    • Finds similar code             │
│    → clarifications.md              │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 2. spec-writer                      │
│    • Creates formal specification   │
│    • 3x self-review                 │
│    → task-spec.md                   │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 3. task-planner                     │
│    • Breaks into sub-tasks          │
│    • Orders by dependencies         │
│    → task-breakdown.md              │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 4. implementer (per sub-task)       │
│    • Implements code                │
│    • 3x self-review per task        │
│    → working code + tests           │
└─────────────────────────────────────┘
    ↓
Feature Complete ✅
```

## How to Use

### Option 1: Full Workflow
```
/code-implement-feature Add user authentication with JWT tokens
```

This will run all 4 agents in sequence.

### Option 2: Individual Agents
You can also call agents individually:

```
# Step 1: Clarify requirements
Use req-clarifier to clarify requirements for [feature]

# Step 2: Create specification
Use spec-writer to create spec from clarifications

# Step 3: Plan tasks
Use task-planner to create task breakdown

# Step 4: Implement each sub-task
Use implementer to execute Sub-Task 1.1
Use implementer to execute Sub-Task 1.2
...
```

## Output Structure

Workflow artifacts are split between two locations:

```
.claude/tasks/[feature-name]/           # Working documents
├── clarifications.md                   # From req-clarifier
├── task-spec.md                        # From spec-writer
├── task-breakdown.md                   # From task-planner
├── task-quick-ref.md
└── implementation-log.md               # From implementer

.claude/analysis-archive/[feature-name]/ # Process artifacts (reviews, summaries)
├── spec-reviews/
│   ├── review-pass-1.md                # Completeness
│   ├── review-pass-2.md                # Conventions
│   └── review-pass-3.md                # Feasibility
├── spec-summary.md
└── implementation-reviews/
    ├── subtask-1.1-review-1.md
    ├── subtask-1.1-review-2.md
    ├── subtask-1.1-review-3.md
    └── ...
```

**Important:** All review and summary files MUST be written to `.claude/analysis-archive/`, NOT to `.claude/tasks/`. This keeps working documents lean for agent context consumption.

## Quality Gates

### Gate 1: Requirements (req-clarifier)
- User confirms understanding
- All questions answered
- Similar code identified

### Gate 2: Specification (spec-writer)
- Pass 1: Completeness ✅
- Pass 2: Convention compliance ✅
- Pass 3: Feasibility ✅

### Gate 3: Planning (task-planner)
- Dependencies identified
- Sub-tasks are 15-60 min each
- Verification checklists included

### Gate 4: Implementation (implementer)
For EACH sub-task:
- Pass 1: Correctness ✅
- Pass 2: Conventions ✅
- Pass 3: Quality ✅

## Best Practices

### For Best Results:
1. **Be patient with req-clarifier** - thorough requirements save time later
2. **Let spec-writer complete all reviews** - don't skip quality gates
3. **Follow task order** - sub-tasks are sequenced by dependencies
4. **Don't skip implementation reviews** - 3x review catches issues early

### When to Skip Parts:
- **Small changes**: Skip req-clarifier, start with spec-writer
- **Well-defined tasks**: If requirements are crystal clear, start with task-planner
- **Bug fixes**: May only need implementer with clear scope

## Integration with Other Skills

### After Implementation:
- Use `/code-review` for additional code review
- Use `/code-optimize` for performance optimization

### Before Implementation:
- Conventions are in CLAUDE.md/MEMORY.md. If missing, run `/code-analyze-codebase`

## Workflow Execution

When you invoke `/code-implement-feature [description]`:

1. **Start req-clarifier** with the feature description
2. **Wait for Q&A** to complete and user confirmation
3. **Run spec-writer** on the clarifications
4. **Run task-planner** on the spec
5. **For each sub-task**, run implementer sequentially
6. **Report completion** with summary of work done

## Example Usage

```
User: /code-implement-feature Add product category management with CRUD operations