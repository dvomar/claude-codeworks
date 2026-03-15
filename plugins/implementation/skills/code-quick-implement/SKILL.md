---
name: code-quick-implement
description: Implement new features following all documented conventions. Automatically loads and applies conventions from knowledge base. Use for any new development.
---

# Quick Implementation

Fast implementation for **well-defined, smaller tasks** without the full planning workflow.

## When to Use

Use `/code-quick-implement` when:
- Requirements are **clear and specific**
- Task is **small to medium** (1-3 files)
- You **know exactly what you want**
- No need for Q&A or formal specification

**For larger/unclear features**, use `/code-implement-feature` instead.

## Comparison

| | `/code-quick-implement` | `/code-implement-feature` |
|---|---|---|
| Q&A | ❌ | ✅ 2-3 rounds |
| Specification | ❌ | ✅ Formal spec |
| Sub-tasks | ❌ | ✅ Breakdown |
| Self-review | ✅ Final only | ✅ 3x per stage |
| Speed | Fast | Thorough |

## How to Use

```
/code-quick-implement Create a new UserValidator
/code-quick-implement Add ProductService with CRUD operations
/code-quick-implement Create Button component with variants
```

## Process

```
Request
   ↓
1. Load conventions from .claude/knowledge/
   ↓
2. Find similar code (2-3 examples)
   ↓
3. Implement following patterns
   ↓
4. Validate against conventions
   ↓
Done ✅
```

## What It Does

1. **Loads conventions** from `.claude/knowledge/`
2. **Finds similar code** in the codebase
3. **Creates implementation plan** (brief)
4. **Implements** following exact patterns
5. **Validates** against conventions

## Prerequisites

Conventions are available in CLAUDE.md and MEMORY.md (auto-injected). If the `## Codebase Conventions (Auto-Generated)` section is empty, run `/code-analyze-codebase`.

## Examples

### Example 1: Create Validator
```
/code-quick-implement Create ProductValidator with name and price validation
```

### Example 2: Create Component
```
/code-quick-implement Create UserAvatar component with size variants
```

### Example 3: Create Service
```
/code-quick-implement Create OrderService with GetById and Create methods
```

## Convention Loading

The skill automatically loads from `.claude/knowledge/`:
- `tech-stack.md` — dependencies, versions
- `architecture.md` — project structure, file placement
- `backend.md` — API, data access, auth, validation patterns
- `frontend.md` — components, styling, state, i18n patterns
- `conventions.md` — naming, formatting, testing conventions

## Validation Checklist

After implementation:
- [ ] Files in correct locations
- [ ] Naming matches conventions
- [ ] Patterns match similar code
- [ ] Exports/registrations added
- [ ] Tests if required

## When to Switch to `/code-implement-feature`

Use the full workflow when:
- Requirements are unclear → need Q&A
- Scope is large → need breakdown
- Multiple components → need planning
- High risk → need formal review
