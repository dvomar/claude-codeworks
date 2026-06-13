---
name: code-optimize
description: Analyzes code for optimization opportunities - performance, memory, readability. Advisory only (no fixes applied); complements /code-review (correctness bugs) and /simplify (applies cleanups). Use after code review passes. Tech-stack agnostic.
---

# Code Optimization

Analyzes code for optimization opportunities and presents actionable findings directly in the terminal.

## Usage

```
/code-optimize <path> [--focus performance|memory|readability|all]
```

- `<path>` — file or directory to analyze
- `--focus` — narrow the analysis to a specific category (default: `all`)
  - `performance` — queries, algorithms, async, caching, I/O
  - `memory` — allocations, collection sizing, disposal, leaks
  - `readability` — naming, complexity, nesting, method length
  - `all` — run all three categories

Examples:
```
/code-optimize src/services/OrderService.cs
/code-optimize src/services/OrderService.cs --focus performance
```

## Instructions

### Step 1: Load code and context

1. Resolve `<path>`. If it is a directory, list the target source files first. If there are more than ~10, analyze in batches and tell the user exactly what was covered and what was deferred — do NOT silently read a large tree into context (it blows the session budget and hides what was skipped). For very large targets, prefer running the skill per-subdirectory.
2. Read the target file(s) using the Read tool.
3. Conventions are provided via CLAUDE.md and MEMORY.md (auto-injected). For deeper per-layer detail than the CLAUDE.md summary, selectively Read the relevant `.claude/knowledge/` files for the target's layer — `backend.md` and `conventions.md` for server code, `frontend.md` for client code, `architecture.md` / `tech-stack.md` as needed. Read only what's relevant to the target, not all of them.
4. For each target file, use Glob to find **similar files** in the same folder/layer — comparison with existing code helps identify inconsistencies and missed patterns.

### Step 2: Analyze

Based on `--focus` (or all categories if not specified), look for concrete optimization opportunities in the loaded code.

**Performance**: N+1 queries, inefficient loops/iterations, blocking async calls, missing caching, suboptimal algorithm complexity, redundant I/O.

**Memory**: Unnecessary allocations in hot paths, string building in loops, wrong collection types, missing disposal, unbounded growth.

**Readability**: Complex conditionals that should be extracted, deep nesting, long methods, magic values, unclear naming, missing early returns.

**Respect established patterns — do NOT flag them as issues or propose changing them.** Conventions the project has deliberately adopted (documented in CLAUDE.md and `.claude/knowledge/`) are not inefficiencies: e.g. its chosen money/precision types and arithmetic, object/DI lifetimes and how data-access objects are created and disposed, read-query patterns, and real-time/transport broadcast patterns. Optimizing *within* an established pattern is fine; replacing the pattern is not.

Do NOT list generic best practices. Only report issues actually present in the code.

### Step 3: Output findings

Format each finding as:

```
## [H1] filename:line — Brief description
**Category**: Performance | Memory | Readability
**Impact**: High | Medium | Low
**Effort**: Low | Medium | High
**Confidence**: High | Medium | Low — for Performance, state what would confirm it (profiling, query plan, load test); a guess is not a fact
**Behavior-preserving**: Yes | Risk — if Risk, state exactly what observable behavior could change

**Problem:** What is wrong and why it matters.

**Current code:**
<relevant snippet>

**Proposed fix:**
<concrete fix — must keep observable behavior identical>
```

Use IDs: `H` = high impact, `M` = medium, `L` = low. Number sequentially (H1, H2, M1, M2, L1...).

End with a summary table:

```
| Impact | Count |
|--------|-------|
| High   | X     |
| Medium | X     |
| Low    | X     |

Recommended order: H1, H2, M3, ... (sorted by impact/effort ratio)
```

## Rules

- **Be specific** — every finding must include filename, line, and a concrete fix
- **Compare with existing code** — if a pattern is established in the codebase, reference it
- **Preserve behavior** — every proposed fix must keep observable behavior identical; if it can't, mark it `Behavior-preserving: Risk` and explain. Especially critical for financial, transactional, or other correctness-sensitive code.
- **Performance findings are hypotheses** — static analysis can't measure; give each a confidence level and say what would confirm it. Never present a guess as a measured fact.
- **Don't fight conventions** — never flag or "optimize" the established patterns listed in Step 2
- **No generic advice** — only report real issues found in the analyzed code
- **No file generation** — output everything directly in the terminal
- **Respect the focus** — if `--focus` is set, only analyze that category
