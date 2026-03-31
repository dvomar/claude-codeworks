---
name: code-optimize
description: Analyzes code for optimization opportunities - performance, memory, readability. Use after code review passes. Tech-stack agnostic.
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

1. Read the target file(s) using Read tool.
2. Conventions are provided via CLAUDE.md and MEMORY.md (auto-injected). Use them to understand project-specific patterns.
3. For each target file, use Glob to find **similar files** in the same folder/layer — comparison with existing code helps identify inconsistencies and missed patterns.

### Step 2: Analyze

Based on `--focus` (or all categories if not specified), look for concrete optimization opportunities in the loaded code.

**Performance**: N+1 queries, inefficient loops/iterations, blocking async calls, missing caching, suboptimal algorithm complexity, redundant I/O.

**Memory**: Unnecessary allocations in hot paths, string building in loops, wrong collection types, missing disposal, unbounded growth.

**Readability**: Complex conditionals that should be extracted, deep nesting, long methods, magic values, unclear naming, missing early returns.

Do NOT list generic best practices. Only report issues actually present in the code.

### Step 3: Output findings

Format each finding as:

```
## [H1] filename:line — Brief description
**Category**: Performance | Memory | Readability
**Impact**: High | Medium | Low
**Effort**: Low | Medium | High

**Problem:** What is wrong and why it matters.

**Current code:**
<relevant snippet>

**Proposed fix:**
<concrete fix>
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
- **No generic advice** — only report real issues found in the analyzed code
- **No file generation** — output everything directly in the terminal
- **Respect the focus** — if `--focus` is set, only analyze that category
