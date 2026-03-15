---
name: code-analyze-codebase
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
/code-analyze-codebase
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

.claude/analysis-archive/    # Process artifacts (not for agents)
├── reviews/
│   └── [domain]-review-[1-3].md
├── summaries/
└── indexes/
```

**Important:** Self-review outputs, summaries, and index files MUST be written to `.claude/analysis-archive/`, NOT to `.claude/knowledge/`. The knowledge directory contains only conventions that agents read during implementation.

### Phase 6: Convention Summarization
After all analyzers complete, distill key rules into CLAUDE.md and MEMORY.md:

1. Read all analysis files from `.claude/knowledge/`
2. Extract **rules only** (no code examples, no verbose descriptions)
3. Write ~60-80 lines into CLAUDE.md `## Codebase Conventions (Auto-Generated)` section (between the `<!-- Auto-generated -->` markers)
4. Write ~10-15 lines into MEMORY.md `## Conventions Summary (Auto-Generated)` section

**What to include in CLAUDE.md section:**
- Naming conventions (files, components, hooks, variables, constants)
- Code patterns (imports order, export style, error handling, async patterns)
- File placement rules (where components, hooks, lib, API routes go)
- Design patterns used (DI, lazy loading, server/client split)
- Styling patterns (card, button, input conventions)
- Testing conventions (framework, file naming, patterns)
- DO/DON'T quick reference

**What to include in MEMORY.md section:**
- Top 5-10 most important conventions as bullet points
- Key patterns that agents need for every task

**Important:** These sections replace the need for agents to bulk-load `.claude/knowledge/` files. Keep them concise — rules only, no code blocks.

## Quality Assurance

Each analyzer performs **3 self-review passes**:
- **Pass 1**: Completeness check
- **Pass 2**: Accuracy verification
- **Pass 3**: Clarity validation

Review artifacts are saved to `.claude/analysis-archive/reviews/`.

## Instructions

Run all five analyzers in sequence:

```
> Use tech-stack-analyzer to analyze the technology stack.
> Use architecture-analyzer to analyze the project architecture and file structure.
> Use backend-analyzer to analyze server-side patterns.
> Use frontend-analyzer to analyze client-side patterns.
> Use conventions-analyzer to extract coding conventions.
```

After all analyses complete:

1. **Phase 6**: Read all `.claude/knowledge/` files, distill key rules (no code examples) into:
   - CLAUDE.md `## Codebase Conventions (Auto-Generated)` section
   - MEMORY.md `## Conventions Summary (Auto-Generated)` section
2. Summarize:
   - Project type(s) detected
   - Key findings from each analysis
   - Location of documentation files
   - Confirmation that CLAUDE.md and MEMORY.md convention sections were updated

## Re-Analysis

Run again when:
- You switch to a new project
- Major dependencies added/removed
- Architecture changes
- Conventions updated
- After major refactoring
