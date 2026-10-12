---
name: mdv-improve-system
description: Cross-session self-improvement. Mines past Claude Code transcripts in ~/.claude/projects for corrections the user keeps repeating (interrupts, rejected tool calls with a reason, "don't…", "again…", "always/never…"), clusters them into rules and, after approval, routes each one the same way /mdv-wrap-session does - a shared convention into .claude/rules/, a personal preference into auto memory. Run manually every week or two, or when the same correction keeps coming back.
argument-hint: "[all] [days=N] [full]"
disable-model-invocation: true
allowed-tools: Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/extract_corrections.py *) Read Glob Grep
---

# Improve System

`/mdv-wrap-session` captures what the **current** session taught. This skill looks
back across **all past sessions** and finds what keeps going wrong: a correction made
once is noise, the same correction in three sessions is a missing rule.

It writes nothing until the user approves the proposal.

## Arguments

`$ARGUMENTS` may contain, in any order:
- `all` - scan every project, not only the current repository
- `days=N` - only sessions modified in the last N days (default 30, which matches the default `cleanupPeriodDays`)
- `full` - ignore the last-run marker and rescan the whole window

## Step 1 - Extract candidates

Claude Code keeps each session as `~/.claude/projects/<project>/<session>.jsonl`. The
bundled script reads them, keeps sessions whose `cwd` lies inside this repository's
git root, and writes a scored list of user messages that look like corrections, each
with the assistant action that preceded it. It skips subagent transcripts, system
reminders, command output, compaction summaries and every session that ran this skill.

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/extract_corrections.py \
  [--all-projects] --days <N> [--since-last-run, unless `full`] \
  --out <scratchpad or temp dir>/improve-system-candidates.md
```

Read the output file. If it reports 0 sessions, tell the user and stop. Mention that
Claude Code deletes transcripts older than `cleanupPeriodDays` (default 30) and that
raising it in `~/.claude/settings.json`, for example `"cleanupPeriodDays": 365`, gives
later runs more history.

## Step 2 - Judge every candidate

The scores are heuristics that narrow the haystack. Decide each item yourself and keep
it only when it corrects **how Claude works**, in a way that will come up again:

- Keep: tool and command choices, code conventions, workflow steps ("run the tests
  before saying done"), boundaries ("ask before deleting"), communication preferences,
  repeated misunderstandings of the project (wrong module, wrong service, wrong DB).
- Drop: ordinary next-task prompts, bug reports about the code itself, anything tied
  to one file or one moment.
- Never carry secrets, credentials, customer data or personal data into a rule or a
  memory, even as an example.

A candidate that is really an open defect ("X is still broken") is not a rule. Leave it
to the vault, as `/mdv-wrap-session` does.

## Step 3 - Cluster and rank

Group kept items by the underlying rule, not by wording. For each cluster note: the rule
as one imperative sentence, occurrences, distinct sessions, one short quote as evidence,
and whether it is shared or personal.

Propose a cluster only if it appears in **2+ distinct sessions**, or once but stated as
standing ("always", "never", "vždy", "nikdy", "remember", "from now on"), or once as the
reason for a rejected tool call.

## Step 4 - Compare with what already exists

`.claude/rules/` and `CLAUDE.md` of this repository are already in your context; do not
spend a Read on them. Read only what is not loaded:
- the auto-memory index `MEMORY.md` and any `feedback` memory files it points to
- `~/.claude/CLAUDE.md` when a cluster looks cross-project

Label each cluster:
- **NEW** - covered nowhere
- **STRENGTHEN** - already written, still violated: make the wording concrete and
  verifiable, or propose a hook, because a rule is guidance and a hook is enforcement
- **CONFLICT** - contradicts an existing rule or memory: show both, the user decides
- **COVERED** - written and working: drop it from the proposal

## Step 5 - Route

Route by the same boundary `/mdv-wrap-session` uses: would it apply to a teammate doing
the same task?

| Cluster | Destination |
|---|---|
| Shared convention, pitfall or working rule for this repo | `.claude/rules/<topic>.md` - change the specific rule that is now wrong instead of appending a conflicting one; one topic per file; `paths:` frontmatter when it only applies to some files |
| Personal, about this user or this machine | auto memory, type `feedback`: a memory file plus its line in `MEMORY.md` |
| Personal and true in every project (`all` runs) | propose a line for `~/.claude/CLAUDE.md`, where rules shared by every project live |
| Multi-step procedure | propose a new skill; do not inline it into a rule |
| Must hold every time with no exception | propose a PreToolUse hook; do not create it without explicit approval |

## Step 6 - Propose, then wait

Show one compact table: `# | rule | status | evidence (count, sessions, short quote) | destination`.

Ask with AskUserQuestion (multiSelect) which items to apply; without it, ask in plain
text and wait. The user may also edit a rule or move it to the other layer. Apply only
what was approved.

## Step 7 - Write

- One concise, verifiable line per rule: "Use `pnpm`, never `npm` or `yarn`", not "use
  the right package manager".
- Above each new or changed rule add a provenance comment:
  `<!-- mdv-improve-system YYYY-MM-DD: 3x in 2 sessions -->`. Claude Code strips block
  HTML comments from CLAUDE.md and rules before they reach the context, so it costs no
  tokens and tells the next reader where the rule came from.
- STRENGTHEN edits the existing line in place. Never leave two versions of one rule.
- Keep every rules file well under 200 lines; split by topic before it grows past that.
- Memories follow the auto-memory format in `~/.claude/CLAUDE.md`.

## Step 8 - Finish

Record the run so the next one reads only newer sessions:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/extract_corrections.py [--all-projects] --mark-run
```

Skip the marker when the user approved nothing and wants to rerun with other settings.

Summarise in a few lines: sessions scanned, rules added, strengthened and skipped, which
files changed, and any hook or skill proposal still waiting for a decision. A rules file
changed silently is a rule nobody trusts, so name every file you touched.
