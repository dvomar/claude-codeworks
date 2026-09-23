# Architecture

Architecture and codebase analysis toolkit. Generates a complete knowledge base for any project — tech stack, conventions, patterns, and file structure rules — checks that it still matches the code, and maps a project into an Obsidian vault.

## What's included

### Agents
- **architect** — Makes design decisions, evaluates trade-offs, prevents over-engineering
- **architecture-analyzer** — Analyzes project architecture, directory structure, and dependencies
- **tech-stack-analyzer** — Detects all frameworks, libraries, and their versions
- **conventions-analyzer** — Extracts naming, formatting, imports, and coding conventions
- **backend-analyzer** — Analyzes API routes, data access, auth, validation, and middleware
- **frontend-analyzer** — Analyzes components, styling, state management, forms, and routing

### Skills
- `/mdv-code-analyze-codebase` — Run all analyzer agents to generate a complete project knowledge base
- `/mdv-knowledge-verify` — Check whether `.claude/knowledge/` still describes the code and propose corrections
- `/mdv-obsidian-project-scope` — Phase 1: map what a system can do into an Obsidian vault
- `/mdv-obsidian-project-depth` — Phase 2: trace how its critical paths actually work (sequence, data flow, blast radius)

## Installation

```
/plugin marketplace add dvomar/claude-codeworks
/plugin install architecture@codeworks
```

## Usage

Start working on a new project by generating its knowledge base:
```
/mdv-code-analyze-codebase
```

This creates documentation files in `.claude/knowledge/` covering tech stack, conventions, patterns, and architecture.

Check later that the knowledge base has not drifted from the code:
```
/mdv-knowledge-verify
```
