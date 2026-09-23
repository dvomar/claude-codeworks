# Auto-Memory

Session observability plus memory and knowledge maintenance for Claude Code — with **no headless subagents and no separate API cost**.

Earlier versions spawned background `claude -p` subprocesses on every `/clear` or `/exit`. That cost a separate API session, ran even on trivial sessions, and was auto-denied when writing to `.claude/`. This version moves the intelligence into a **manual skill that runs in your live session** (full context, full model, normal write permissions) and keeps only zero-cost Python in the hooks.

## What's included

### Statusline (`statusline.py`)
A two-line statusline rendered below the prompt. Line 1: model · directory · git branch. Line 2: cumulative session tokens (summed from the transcript), session cost in USD, context-window %, and — for Claude.ai Pro/Max — the 5-hour rate-limit usage with time-to-reset. Runs locally, consumes **zero API tokens**, refreshes after each assistant message.

### Skill (`skills/mdv-wrap-session/`)
- **`/mdv-wrap-session`** — run manually right before `/clear` or `/exit`. Two passes:
  - **Rules and memory** (inline): reviews the *live conversation* for what is worth keeping and routes it — a shared convention or pitfall becomes a rule in `.claude/rules/`, anything personal or one-off becomes a memory (`user`/`feedback`/`project`/`reference`) in your auto-memory dir. Better context than re-reading a transcript, and no extra session.
  - **Knowledge** (delegated): hands the dirty-file list to the `knowledge-updater` agent, which surgically updates `.claude/knowledge/*.md` and clears the list.
  - A skill cannot trigger `/clear` itself, so it finishes by telling you to run it.

### Hooks (`hooks/`)
- **`session-end.py`** — fires on `/clear` and `/exit`. Aggregates token usage from the transcript into `.claude/.session-summary.jsonl` and, if source files are pending, prints a reminder to run `/mdv-wrap-session`. No subagents.
- **`post-tool-edit.py`** — fires after every `Edit`/`Write`/`MultiEdit` of a source file. Appends the path to `.claude/.knowledge-dirty.txt` for the next `/mdv-wrap-session`.
- **`session-start.py`** — fires on CLI startup. Warns if `.knowledge-dirty.txt` has accumulated a large backlog.
- **`lib.py`** — shared helpers; includes the `CLAUDE_HOOKS_DISABLED` env-var bail-out.

### Agent (`agents/`)
- **`knowledge-updater`** — incrementally edits `.claude/knowledge/*.md` for a small dirty set. Conservative; clears the dirty list only on full success. Used by `/mdv-wrap-session`.

### Settings fragment (`settings.json`)
Merges into `~/.claude/settings.json`:
- `statusLine` → `python3 ~/.claude/statusline.py`
- `SessionEnd` matcher `clear|prompt_input_exit`, `PostToolUse` matcher `Edit|Write|MultiEdit`, `SessionStart` matcher `startup`

## Installation

```
/plugin marketplace add dvomar/claude-codeworks
/plugin install auto-memory@codeworks
```

The installer copies `statusline.py` and the hooks to `~/.claude/`, the `knowledge-updater` agent to the project `.claude/agents/`, the `mdv-wrap-session` skill to `.claude/skills/`, and merges the settings fragment into `~/.claude/settings.json` (preserving existing top-level keys).

## Usage

- During work: `post-tool-edit` quietly tracks changed source files; the statusline shows live token/cost/context/rate-limit.
- Before ending a session: run **`/mdv-wrap-session`**, review what it proposes to keep, then `/clear`.
- On `/clear`/`/exit`: the token summary is appended to `.session-summary.jsonl`.

## Files written per project

```
<project>/.claude/
├── .session-summary.jsonl     # one row per /clear or /exit (token totals, model breakdown)
└── .knowledge-dirty.txt        # absolute paths of changed source files since last /mdv-wrap-session
```

## Requirements

- Python 3 (stdlib only)
- `jq` (for the settings-merge step at install time)
- `git` (statusline branch segment; optional)

## Token cost

The hooks and statusline make no LLM calls (≈0 tokens). `/mdv-wrap-session` runs in your existing session on your existing model, so it adds only the tokens of the work it does — no separate API session.
