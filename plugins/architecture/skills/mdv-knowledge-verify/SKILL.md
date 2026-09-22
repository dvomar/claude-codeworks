---
name: mdv-knowledge-verify
description: 'Check whether .claude/knowledge/ still describes the code it claims to describe. Takes the falsifiable claims out of architecture.md, conventions.md, backend.md, frontend.md and tech-stack.md — directories that should exist, naming rules that should hold, versions that should match the lockfile — verifies each against the repository, and reports claim, reality and a proposed correction. Advisory: it never edits the knowledge docs itself. Use when the docs feel stale, after a refactor or dependency bump, before trusting them on an unfamiliar project, or when an agent follows a rule that no longer matches the code: "platí ještě knowledge", "jsou konvence aktuální", "zkontroluj knowledge", "are the conventions still true", "verify the knowledge docs", "these docs look stale".'
argument-hint: "[--only architecture|conventions|backend|frontend|tech-stack] [--max 40]"
user-invocable: true
allowed-tools: Read, Grep, Glob, Bash
---

# Verify knowledge

`.claude/knowledge/` is what every agent in this setup treats as convention truth. It is
generated once by `/mdv-code-analyze-codebase` and then only ever appended to by
`/mdv-wrap-session`. Nothing checks whether it is still *correct*.

That matters more since `/mdv-code-analyze-codebase` stopped distilling a summary into
CLAUDE.md: this is now the only feedback loop on whether the knowledge docs describe
reality. A stale rule does not fail loudly — it silently steers every implementation and
review toward a pattern the codebase abandoned months ago.

This skill reads the docs, keeps only the claims that can be checked, checks them, and
reports. It does not edit; a wrong doc is corrected by a human who knows which side is
right, or by re-running the analyzer for that layer.

## What counts as checkable

Only a claim that some observation could prove false. Everything else is skipped without
comment — the point is a short report of real contradictions, not a long one padded with
things nobody can adjudicate.

| Checkable | Not checkable |
|---|---|
| "Validators live in `businessLayer/validators/`" | "Keep the code clean" |
| "Components are PascalCase, hooks are `useX`" | "Prefer readable names" |
| "React 18.2, EF Core 8" | "The architecture is layered" |
| "API routes are under `src/app/api/`" | "Error handling is consistent" |
| "Tests are `*.spec.ts` next to the source" | "Follow existing patterns" |

## Process

### 1. Gate

If `.claude/knowledge/` is missing or empty, there is nothing to verify: say so, point at
`/mdv-code-analyze-codebase`, stop. With `--only`, read just that file.

### 2. Extract claims

Read each doc and pull out the checkable claims as a list of
`{doc, line, claim, kind}`, where kind is one of **path**, **naming**, **version**,
**placement** or **structure**. Keep the line number — the report is useless without it.

Cap at `--max` (default 40), highest-value first: placement and naming rules steer the
most agent behaviour, so they come before cosmetic ones.

### 3. Verify each claim

Cheap checks, no builds, no installs:

- **path** — does the directory or file exist? `test -d`, `Glob`.
- **placement** — do the files that should be there, actually live there? Sample the
  real locations with `Glob` and compare.
- **naming** — sample the **20 most recently modified** matching files
  (`git log --name-only --pretty=format: -n 200 | …`) and measure conformance. Recent
  files show the convention in force now; the whole tree averages in history that has
  already been abandoned. Report a rate, not a verdict: "17/20 conform, 3 do not" is
  information, "broken" is not.
- **version** — compare against the real manifest or lockfile: `package.json`,
  `*.csproj`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `*.lock`.
- **structure** — does the module or layer the doc names still exist?

A claim that is true is not reported. Silence is the pass condition.

### 4. Report

Only contradictions, grouped by doc, each one:

```
conventions.md:42
  claim:    Components are PascalCase under src/components/
  reality:  14/20 recent components are PascalCase; 6 are kebab-case under src/ui/
  suggest:  Two conventions are in use. Confirm which is current, then correct the doc
            — or the six files.
```

Close with a one-line verdict per doc — `ok`, `N contradictions`, or `not checked` —
and a single recommendation:

- **1–3 contradictions** → correct the doc by hand; it is faster and preserves the parts
  that are right.
- **More than a third of the claims wrong** → that layer has moved. Re-run
  `/mdv-code-analyze-codebase` rather than patching claim by claim.
- **A claim is right and the code is wrong** → say so explicitly. The doc being outvoted
  by the code is not automatically the doc being wrong, and this is the one judgement
  call worth surfacing every time.

## When to run it

- After a refactor that moved directories, or a dependency bump.
- On an unfamiliar project, before trusting `.claude/knowledge/` for real work.
- When `.claude/.knowledge-dirty.txt` has been long for a while — `/mdv-wrap-session` adds
  to the docs, it does not re-check what is already there.
- When an agent keeps following a rule that no longer matches the code. That is the
  symptom this exists for.
