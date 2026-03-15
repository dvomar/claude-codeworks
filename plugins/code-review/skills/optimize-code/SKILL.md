---
name: optimize-code
description: Analyzes code for optimization opportunities - performance, memory, readability. Use after code review passes.
---

# Code Optimization

This skill analyzes code for optimization opportunities using the **code-optimizer** agent.

## Prerequisites

Conventions are available in CLAUDE.md and MEMORY.md (auto-injected). If the `## Codebase Conventions (Auto-Generated)` section is empty, run `/analyze-codebase`.

## When to Use

Use `/optimize-code` when you need to:
- Improve performance
- Reduce memory usage
- Enhance readability
- Identify refactoring opportunities

## How to Use

```
/optimize-code path/to/file.ts
```

With specific focus:
```
/optimize-code path/to/file.ts --focus performance
/optimize-code path/to/file.ts --focus memory
/optimize-code path/to/file.ts --focus readability
```

## Analysis Categories

### Performance
- N+1 queries
- Inefficient LINQ/loops
- Missing caching
- Blocking async calls
- Algorithm efficiency

### Memory
- Object allocations
- String concatenation in loops
- Collection sizing
- Proper disposal
- Memory leaks

### Readability
- Complex conditionals
- Long methods
- Magic numbers
- Deep nesting
- Unclear naming

### Maintainability
- Code duplication
- Extensibility issues
- Testability
- Anti-patterns

## Output

Optimization report: `.claude/optimizations/[file-name]-optimization-report.md`

### Impact Levels
- **High**: Significant improvement, worth the effort
- **Medium**: Moderate improvement
- **Low**: Minor polish

## Example

```
User: /optimize-code src/services/OrderService.ts

Agent: Optimization analysis completed!

📊 Report: .claude/optimizations/OrderService-optimization-report.md

Summary:
- High-impact optimizations: 2
- Medium-impact optimizations: 3
- Low-impact improvements: 4

Estimated Performance Gain: 40%
Estimated Memory Reduction: 15%

Top Recommendations:
1. Fix N+1 query at line 45 - Impact: High, Effort: Low
2. Add caching for GetCategories - Impact: High, Effort: Medium
3. Use StringBuilder in BuildReport - Impact: Medium, Effort: Low

See full report for code examples and benchmarks.
```

## Integration

After optimization:
- Implement high-impact, low-effort changes first
- Run tests after each optimization
- Re-measure performance
