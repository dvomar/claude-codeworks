---
name: review-code
description: Comprehensive 3-pass code review for conventions, patterns, and quality. Use after implementation.
---

# Code Review

This skill performs comprehensive code review using the **code-reviewer** agent.

## Prerequisites

Conventions are available in CLAUDE.md and MEMORY.md (auto-injected). If the `## Codebase Conventions (Auto-Generated)` section is empty, run `/analyze-codebase`.

## When to Use

Use `/review-code` when you need to:
- Review code after implementation
- Check convention compliance
- Verify pattern usage
- Assess code quality before merge

## How to Use

```
/review-code path/to/file.ts
```

Or for multiple files:
```
/review-code src/services/UserService.ts src/services/AuthService.ts
```

## 3-Pass Review

### Pass 1: Convention Compliance
- Naming conventions
- File organization
- Code style
- Documentation

### Pass 2: Pattern Consistency
- Dependency injection
- Service/Repository patterns
- Error handling patterns
- Async/await patterns
- Comparison with similar code

### Pass 3: Quality Assessment
- SOLID principles
- Code smells
- Performance concerns
- Security issues
- Testing coverage

## Output

Review report saved to: `.claude/reviews/[file-name]-code-review.md`

### Severity Levels
- 🔴 **Critical**: Must fix before merge
- 🟡 **Warning**: Should fix
- 🟢 **Info**: Nice to have

## Integration

After review:
- Fix critical issues
- Re-run review if needed
- Use `/optimize-code` for performance improvements

## Example

```
User: /review-code src/services/ProductService.ts

Agent: Code review completed!

📊 Review: .claude/reviews/ProductService-code-review.md

Summary:
- Status: ⚠️ Approved with Comments
- Critical issues: 1 🔴
- Warnings: 3 🟡
- Suggestions: 5 🟢

Pass 1 - Conventions: 1 issue (missing _ prefix on field)
Pass 2 - Patterns: 2 issues (DI pattern differs from similar)
Pass 3 - Quality: Method too long at line 45

See full report for details and fixes.
```
