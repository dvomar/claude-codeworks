# Code Review

Code review and debugging toolkit — multi-pass reviews of files and merge/pull requests, root-cause debugging, optimization suggestions, and refactoring cleanup.

## What's included

### Agents
- **refactor-cleaner** — Finds and removes dead code, unused dependencies, and stale exports

### Skills
- `/mdv-code-review-feature` — 3-pass review of specific files by path — conventions, patterns, quality
- `/mdv-review-pr` — Review an open GitLab MR or GitHub PR from the terminal and leave inline draft comments
- `/mdv-mr-resolve-comments` — Analyze unresolved MR comments and propose fixes or counterarguments with ready-to-paste replies
- `/mdv-debug-root-cause` — Reproduce a failure, prove its cause, fix that cause, and close with a regression test
- `/mdv-code-optimize` — Analyze code for performance, memory, and readability improvements (advisory only)

## Installation

```
/plugin marketplace add dvomar/claude-codeworks
/plugin install code-review@codeworks
```

## Usage

Review specific files:
```
/mdv-code-review-feature src/orders/service.ts
```

Review a merge or pull request (no number lists the open ones):
```
/mdv-review-pr 123
```

Find why something breaks:
```
/mdv-debug-root-cause the checkout test fails since yesterday
```
