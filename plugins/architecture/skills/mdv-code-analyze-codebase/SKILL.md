---
name: mdv-code-analyze-codebase
description: Comprehensive codebase analysis - runs all analyzer agents to extract tech stack, architecture, patterns, conventions. Use this when starting work on a new project or when conventions documentation is missing.
---

# Complete Codebase Analysis

This skill orchestrates all analyzer agents to create comprehensive documentation of ANY codebase type.

## Supported Project Types

The analyzers automatically detect and handle:
- **JavaScript/TypeScript**: Next.js, React, Vue, Angular, Node.js, Express, NestJS
- **.NET/C#**: ASP.NET Core, Blazor, Console apps, Class libraries
- **Python**: Django, Flask, FastAPI
- **Ruby**: Rails, Sinatra
- **Go**: Standard Go projects
- **Rust**: Cargo projects
- **Java/Kotlin**: Spring Boot, Gradle, Maven
- **PHP**: Laravel, Symfony

## How to Use

```
/mdv-code-analyze-codebase
```

## Analysis Process

### Phase 1: Technology Stack
Use **tech-stack-analyzer**:
- Project type (auto-detected)
- Runtime/SDK versions
- All dependencies and versions
- Development tools and CI/CD

Output: `.claude/knowledge/tech-stack.md`

### Phase 2: Architecture & File Structure
Use **architecture-analyzer**:
- Architecture pattern identification
- Directory structure (tree, 4 levels)
- Module inventory (path + purpose + layer)
- Dependency rules
- File placement decision trees
- Path aliases and folder conventions

Output: `.claude/knowledge/architecture.md`

### Phase 3: Backend Patterns
Use **backend-analyzer**:
- API route/endpoint patterns
- Data access patterns
- Authentication & authorization
- Validation patterns
- Error handling
- Middleware/pipeline
- Configuration & environment
- Email/notifications
- Rate limiting & security

Output: `.claude/knowledge/backend.md`

### Phase 4: Frontend Patterns
Use **frontend-analyzer**:
- Component patterns (Server/Client split, lazy loading)
- Styling patterns (framework, tokens, responsive)
- State management
- Form patterns
- Routing & navigation
- i18n/l10n patterns
- Accessibility
- Performance patterns
- Animation & transitions

Output: `.claude/knowledge/frontend.md`

### Phase 5: Coding Conventions
Use **conventions-analyzer**:
- Naming conventions (files, code elements)
- Code formatting (indentation, quotes, semicolons)
- Import organization order
- Component/class member order
- Type definition conventions
- Testing conventions
- DO/DON'T quick reference

Output: `.claude/knowledge/conventions.md`

## Output Structure

```
.claude/knowledge/           # 5 compact files (~850 lines total)
├── tech-stack.md            # Dependencies, versions, tooling (~150 lines)
├── architecture.md          # Structure, modules, file placement (~200 lines)
├── backend.md               # Server-side patterns & conventions (~250 lines)
├── frontend.md              # Client-side patterns & conventions (~250 lines)
└── conventions.md           # Cross-cutting coding style (~200 lines)
```

### Phase 6: Verification

There is no distillation step into CLAUDE.md. `.claude/knowledge/` is the single source
of generated convention truth, and every skill and agent that needs conventions reads it
directly. Hand-written rules are a separate layer that belongs in `.claude/rules/` and is
never written by an analyzer — these five files are overwritten wholesale on every run. A second, summarized copy inside CLAUDE.md drifts from it within weeks, and
then the two disagree with no way to tell which one is right.

Verify instead that the run landed:

1. All five files exist under `.claude/knowledge/` and none is empty.
2. Each names concrete things from **this** project — real directories, real class or
   component names, real library versions. A file full of generic advice means the
   analyzer had no sample to generalize from; say so rather than presenting it as fact.
3. Report per file: created or updated, line count, and anything the analyzer marked
   uncertain.

Tell the user to read the output. This is also the check on whether the analyzers
understood the project — when `architecture.md` claims something unexpected, correct it
by hand now. From that moment it is the source of truth every other agent works from.

## Quality Assurance

Each analyzer performs **3 inline self-review passes** (completeness, accuracy, clarity) and fixes issues before finalizing its output.

## Instructions

Launch all five analyzers **in parallel** — one message, five `Agent` calls. They are
independent: each writes its own file and none reads another's output, so there is
nothing to serialize. Run sequentially, the analysis costs five analyzers of wall-clock
time; run in parallel, it costs one.

```
> Use tech-stack-analyzer to analyze the technology stack.
> Use architecture-analyzer to analyze the project architecture and file structure.
> Use backend-analyzer to analyze server-side patterns.
> Use frontend-analyzer to analyze client-side patterns.
> Use conventions-analyzer to extract coding conventions.
```

Once all five have returned, run Phase 6 and report:

- Project type(s) detected
- Key findings from each analysis
- Which knowledge files were written, and which came back thin or generic
- Where the files live, so the user can read them and correct what is wrong

## Re-Analysis

Run again when:
- You switch to a new project
- Major dependencies added/removed
- Architecture changes
- Conventions updated
- After major refactoring
