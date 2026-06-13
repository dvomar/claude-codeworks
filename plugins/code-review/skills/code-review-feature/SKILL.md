---
name: code-review-feature
description: 3-pass review of specific files by path — conventions, patterns, quality. Complements the built-in /code-review (which reviews the current git diff); use this to review arbitrary existing files, not just pending changes. Advisory only (terminal output). Tech-stack agnostic.
---

# Code Review (by path)

Performs a thorough 3-pass review of the file(s) you point it at and outputs findings directly in the terminal.

Unlike the built-in `/code-review` (which reviews the current git diff, and can `--fix` / `--comment` / run an `ultra` cloud pass), this skill reviews **whole files at an arbitrary path** — useful for auditing existing code that isn't part of a pending change.

## Usage

```
/code-review-feature <path> [path2 ...]
```

Examples:
```
/code-review-feature src/services/OrderService.cs
/code-review-feature src/services/UserService.cs src/api/UserEndpoint.cs
```

## Instructions

### Step 1: Load code and context

1. Resolve the target path(s). If a directory or long list is given and there are more than ~10 source files, review in batches and tell the user exactly what was covered and what was deferred — do NOT silently read a large tree into context.
2. Read all target files using the Read tool.
3. Conventions are provided via CLAUDE.md and MEMORY.md (auto-injected) — the primary reference for what is correct. For deeper per-layer detail than the CLAUDE.md summary, selectively Read the relevant `.claude/knowledge/` files for the target's layer (e.g. `conventions.md` and `backend.md` for server code, `frontend.md` for client code). Read only what's relevant.
4. For each target file, use Glob to find **similar existing files** in the same folder/layer. Read 2-3 of them — comparison with established code is the most reliable way to spot inconsistencies.

### Step 2: Pass 1 — Conventions and style

Check against the conventions from CLAUDE.md / MEMORY.md / `.claude/knowledge/`:

- Naming (files, types, methods, fields, variables) — consistent with conventions?
- File placement — correct location per the project's structure?
- One type per file (if that's the project's rule) — no unexpected nested types?
- Code structure — member order, import/using order
- Dependency registration / wiring — follows the project convention?
- Formatting — matches the enforced style?

### Step 3: Pass 2 — Design and patterns

- Dependency injection / object construction — correct usage and lifetimes?
- Service / data-access / validation patterns — match how similar code in the same layer does it?
- Layering — does the code respect the project's layer boundaries (no layer reaching past its neighbors, no logic living where the project's structure says it shouldn't)?
- Async / concurrency — correct usage, no blocking calls, cancellation propagated where the project expects it?
- Error handling — uses the project's exception types and conventions correctly?
- **Comparison with similar existing code** — does the reviewed code follow the same patterns as established code in the same layer?

### Step 4: Pass 3 — Quality and correctness

- Logic correctness — edge cases, off-by-one, null/empty handling?
- Performance — N+1 queries, unnecessary iterations, missing caching. Label these as hypotheses — static review can't measure.
- Security — obvious input-handling, injection, or auth-check problems. This is a LIGHT pass; for a real security review use the `security-audit` skill.
- Code smells — long methods, too many parameters, deep nesting, magic values?
- DRY — duplicate code that should be extracted (but don't force premature abstraction)?
- Readability — understandable without extra context?
- Tests — do they exist, cover critical paths, follow the project's test conventions?

### Step 5: Output findings

Format each finding as:

```
### [C1] filename:line — Brief description
**Pass**: 1 (Conventions) | 2 (Patterns) | 3 (Quality)
**Severity**: CRITICAL | WARNING | SUGGESTION
**Confidence**: High | Medium | Low — for correctness/perf/security claims, state what would confirm it
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
- **State confidence** — for correctness, performance, and security claims, give a confidence level and what would confirm it; don't present a guess as a fact
- **Don't nitpick** — ignore minor stylistic issues that don't conflict with conventions or that a linter/formatter already catches
- **Positive feedback** — always highlight what is well done
- **No file generation** — output everything directly in the terminal
- **Be constructive** — explain *why* something is a problem, not just *that* it is
- **Severity matters** — clearly distinguish blocking issues from nice-to-haves
