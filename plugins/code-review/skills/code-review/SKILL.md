---
name: code-review
description: Comprehensive 3-pass code review for conventions, patterns, and quality. Use after implementation. Tech-stack agnostic.
---

# Code Review

Performs a thorough 3-pass code review of local files and outputs findings directly in the terminal.

## Usage

```
/code-review <path> [path2 ...]
```

Examples:
```
/code-review src/services/OrderService.cs
/code-review src/services/UserService.cs src/controllers/UserController.cs
```

## Instructions

### Step 1: Load code and context

1. Read all target files using Read tool.
2. Conventions are provided via CLAUDE.md and MEMORY.md (auto-injected). Use them as the primary reference for what is correct.
3. For each target file, use Glob to find **similar existing files** in the same folder/layer (e.g., other services, other controllers). Read 2-3 of them — comparison with existing code is the most reliable way to spot inconsistencies.

### Step 2: Pass 1 — Conventions and style

Check against conventions from CLAUDE.md / MEMORY.md:

- Naming (files, classes, methods, fields, variables) — consistent with conventions?
- File placement — correct location per project structure?
- One type per file — no nested classes/records/enums?
- Code structure — member order, using/import order
- DI registration — follows project convention?
- Braces, formatting — matches enforced style?

### Step 3: Pass 2 — Design and patterns

- Dependency injection — correct usage, proper lifetimes?
- Service/Repository/Validation patterns — match how similar code does it?
- Layering — API layer doesn't call DAL directly, no business logic in controllers?
- Async/await — correct usage, no blocking calls, CancellationToken propagation?
- Error handling — uses project-specific exception types correctly?
- **Comparison with similar existing code** — does the reviewed code follow the same patterns as established code in the same layer?

### Step 4: Pass 3 — Quality and correctness

- Logic correctness — edge cases, off-by-one, null handling?
- Performance — N+1 queries, unnecessary iterations, missing caching?
- Security — SQL injection, XSS, improper input handling, auth checks?
- Code smells — long methods, too many parameters, deep nesting, magic values?
- DRY — duplicate code that should be extracted?
- Readability — is the code understandable without additional context?
- Tests — do they exist, cover critical paths, follow project test conventions?

### Step 5: Output findings

Format each finding as:

```
### [C1] filename:line — Brief description
**Pass**: 1 (Conventions) | 2 (Patterns) | 3 (Quality)
**Severity**: CRITICAL | WARNING | SUGGESTION
**Problem:** What is wrong and why.
**Fix:**
<concrete fix or code example>
```

Use IDs: `C` = critical, `W` = warning, `S` = suggestion. Number sequentially (C1, C2, W1, W2, S1...).

After all findings, add:

```
## Positive findings
- <what is well done>
- <which patterns are correctly followed>

## Summary

| Severity   | Count |
|------------|-------|
| Critical   | X     |
| Warning    | X     |
| Suggestion | X     |

**Verdict:** APPROVE | APPROVE WITH COMMENTS | CHANGES REQUESTED
```

## Rules

- **Be specific** — every finding must include filename, line, and a concrete fix
- **Compare with existing code** — if a pattern is established, reference the file where it's done correctly
- **Don't nitpick** — ignore minor stylistic issues that don't conflict with conventions or aren't caught by linters
- **Positive feedback** — always highlight what is well done
- **No file generation** — output everything directly in the terminal
- **Be constructive** — explain *why* something is a problem, not just *that* it is
- **Severity matters** — clearly distinguish blocking issues from nice-to-haves
