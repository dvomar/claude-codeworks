# Architecture

Architecture and codebase analysis toolkit. Generates a complete knowledge base for any project — tech stack, conventions, patterns, and file structure rules.

## What's included

### Agents
- **architect** — Makes design decisions, evaluates trade-offs, prevents over-engineering
- **architecture-analyzer** — Analyzes project architecture, directory structure, and dependencies
- **tech-stack-analyzer** — Detects all frameworks, libraries, and their versions
- **conventions-analyzer** — Extracts naming, formatting, imports, and coding conventions
- **backend-analyzer** — Analyzes API routes, data access, auth, validation, and middleware
- **frontend-analyzer** — Analyzes components, styling, state management, forms, and routing

### Skills
- `/code-analyze-codebase` — Run all analyzer agents to generate a complete project knowledge base

## Installation

```
/plugin marketplace add dvomar/claude-codeworks
/plugin install architecture@codeworks
```

## Usage

Start working on a new project by generating its knowledge base:
```
/code-analyze-codebase
```

This creates documentation files in `.claude/knowledge/` covering tech stack, conventions, patterns, and architecture.
