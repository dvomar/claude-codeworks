# Code Review

Comprehensive code review toolkit with multi-pass analysis, optimization suggestions, refactoring cleanup, and GitLab MR integration.

## What's included

### Agents
- **code-reviewer** — 3-pass code review checking conventions, patterns, and quality
- **code-optimizer** — Analyzes code for performance, memory, and readability improvements
- **refactor-cleaner** — Finds and removes dead code, unused dependencies, and stale exports

### Skills
- `/code-review` — Run a structured 3-pass code review on changed files
- `/code-optimize` — Analyze code for optimization opportunities after review passes
- `/mr-review-gitlab` — Review a GitLab MR directly from the terminal with structured findings
- `/mr-resolve-comments` — Analyze unresolved MR comments and propose fixes or counterarguments
- `/code-review-guide` — Guide for effective code review practices and constructive feedback

## Installation

```
/plugin marketplace add dvomar/claude-codeworks
/plugin install code-review@codeworks
```

## Usage

After implementation, run a code review:
```
/code-review
```

Review a GitLab merge request:
```
/mr-review-gitlab 123
```

Optimize code after review passes:
```
/code-optimize
```
