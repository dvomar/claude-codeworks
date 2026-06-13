---
name: wrap-session
description: End-of-session wrap-up. Reviews the live conversation for memories worth keeping and updates .claude/knowledge/ docs for files changed this session. Run manually right before /clear or /exit.
---

# Wrap Session

Captures everything worth persisting from the current session **before** you clear or exit.

Run this in the live session (not headless): it already has the full conversation in context and writes with normal interactive permissions — so it's smarter and cheaper than spawning headless agents on every exit.

## When to use

- Manually, at the end of a substantive session, right before `/clear` or `/exit`.
- Skip it for trivial sessions (a quick question, no decisions, no file edits) — there's nothing to capture.

## Process

Run the two passes in order. Either pass may be a no-op — that's fine, say so and move on.

### Pass 1 — Memory (runs inline, in this session)

You already lived this conversation, so review it directly. Do **not** spawn the `memory-proposer` agent (it re-reads a transcript from disk — strictly worse than your live context).

1. Load the authoritative rules: read the `# auto memory` section of `~/.claude/CLAUDE.md` (types, when-to-save, what-NOT-to-save, body structure). Your system prompt already contains these — re-skim them.
2. Read the existing `MEMORY.md` index in your auto-memory directory to avoid duplicates.
3. Review **this session's** conversation for candidates:
   - **feedback** — corrections the user gave ("don't…", "stop…") OR approaches they validated ("yes, that's right").
   - **project** — decisions, deadlines, who/why behind the work, that aren't derivable from code or git.
   - **user** — role, expertise, preferences revealed this session.
   - **reference** — pointers to external systems (Linear, Slack, dashboards, URLs).
   - Skip anything ephemeral, code-derivable, or already in CLAUDE.md. When unsure, skip.
4. If there are candidates, present them as a short numbered list and ask which to save (the user may edit or reject). For each accepted one, write the memory file + add its line to `MEMORY.md`, following the format in the auto-memory spec.
5. If there are none, say "No memories worth saving this session" and move on.

### Pass 2 — Knowledge (delegate to the knowledge-updater agent)

The dirty list at `.claude/.knowledge-dirty.txt` tracks source files edited this session (populated by the PostToolUse hook). Updating `.claude/knowledge/*.md` needs reading those files + the knowledge docs — keep that out of the main context by delegating.

1. Check `.claude/.knowledge-dirty.txt`. If it's missing or empty → "No files pending knowledge update" and skip this pass.
2. If it has entries, launch the **knowledge-updater** agent via the Agent tool with a self-contained prompt:

   > Use the knowledge-updater workflow. PROJECT_DIR is the current project root. Read the dirty list at `.claude/.knowledge-dirty.txt` (absolute paths, one per line). For each file, decide which `.claude/knowledge/*.md` doc it affects (architecture / backend / frontend / conventions / tech-stack) and make minimal surgical edits — never rewrite whole files, skip files with no architectural change. Clear the dirty list (`> .claude/.knowledge-dirty.txt`) ONLY if every needed edit succeeded or none were needed; on partial failure leave the failed paths. Report which docs you updated and how many files you skipped.

3. Relay the agent's summary (which docs changed, what was skipped).

### Finish

Print a one-line summary of both passes, then tell the user:

> Done. Run `/clear` (or `/exit`) now to end the session.

A skill cannot trigger `/clear` itself — that's a CLI built-in — so the user runs it.

## Notes

- This skill replaces the old SessionEnd headless spawns. The hook now only logs token usage; all intelligence lives here.
- Both passes are independent — if one is a no-op, still run the other.
