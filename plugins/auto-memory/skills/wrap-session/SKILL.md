---
name: wrap-session
description: End-of-session wrap-up. Reviews the live conversation for memories worth keeping, updates .claude/knowledge/ docs for files changed this session, and keeps the Obsidian vault (capabilities + open defects) current. Run manually right before /clear or /exit.
---

# Wrap Session

Captures everything worth persisting from the current session **before** you clear or exit.

Run this in the live session (not headless): it already has the full conversation in context and writes with normal interactive permissions — so it's smarter and cheaper than spawning headless agents on every exit.

## When to use

- Manually, at the end of a substantive session, right before `/clear` or `/exit`.
- Skip it for trivial sessions (a quick question, no decisions, no file edits) — there's nothing to capture.

## Three layers, three owners

Before you write anything, know which layer a fact belongs to. Writing the same fact into two layers guarantees they drift apart.

| Layer | Written for | Owns |
|---|---|---|
| **auto-memory** (`~/.claude/projects/<proj>/memory/`) | **the agent** — reloaded every session | how to work here: preferences, corrections, non-obvious mechanics, why decisions were made |
| **`.claude/knowledge/*.md`** | **the agent writing code** | conventions, architecture, where things go |
| **Obsidian vault** (`<vault>/<Project>/`) | **humans** | what the system can do (`Sekce/`) and what's broken (`Nálezy/`) |

The hard boundary that matters: **open defects live in the vault, not in memory.** Memory keeps at most a one-line pointer (`→ vault CM5-0XX`). A defect needs a body, evidence and acceptance criteria — memory is the wrong shape for that, and two copies of "is it fixed?" will disagree within a month.

## Process

Run the three passes in order. Any pass may be a no-op — that's fine, say so and move on.

### Pass 1 — Memory (runs inline, in this session)

You already lived this conversation, so review it directly — don't delegate this to a subagent that would only re-read a transcript from disk.

1. Load the authoritative rules: read the `# auto memory` section of `~/.claude/CLAUDE.md` (types, when-to-save, what-NOT-to-save, body structure). Your system prompt already contains these — re-skim them.
2. Read the existing `MEMORY.md` index in your auto-memory directory to avoid duplicates.
3. Review **this session's** conversation for candidates:
   - **feedback** — corrections the user gave ("don't…", "stop…") OR approaches they validated ("yes, that's right").
   - **project** — decisions, deadlines, who/why behind the work, that aren't derivable from code or git.
   - **user** — role, expertise, preferences revealed this session.
   - **reference** — pointers to external systems (Linear, Slack, dashboards, URLs).
   - Skip anything ephemeral, code-derivable, or already in CLAUDE.md. When unsure, skip.
   - **A candidate that is really an open defect ("X is broken", "Y is unfixed", "⚠️ OPEN…") is not a memory — hand it to Pass 3.** Memory may keep the mechanics (how it works, why it's tricky) plus a `→ vault CM5-0XX` pointer, but the defect's *status* belongs in exactly one place: the vault.
4. If there are candidates, present them as a short numbered list and ask which to save (the user may edit or reject). For each accepted one, write the memory file + add its line to `MEMORY.md`, following the format in the auto-memory spec.
5. If there are none, say "No memories worth saving this session" and move on.

### Pass 2 — Knowledge (delegate to the knowledge-updater agent)

The dirty list at `.claude/.knowledge-dirty.txt` tracks source files edited this session (populated by the PostToolUse hook). Updating `.claude/knowledge/*.md` needs reading those files + the knowledge docs — keep that out of the main context by delegating.

1. Check `.claude/.knowledge-dirty.txt`. If it's missing or empty → "No files pending knowledge update" and skip this pass.
2. If it has entries, launch the **knowledge-updater** agent via the Agent tool with a self-contained prompt:

   > Use the knowledge-updater workflow. PROJECT_DIR is the current project root. Read the dirty list at `.claude/.knowledge-dirty.txt` (absolute paths, one per line). For each file, decide which `.claude/knowledge/*.md` doc it affects (architecture / backend / frontend / conventions / tech-stack) and make minimal surgical edits — never rewrite whole files, skip files with no architectural change. Clear the dirty list (`> .claude/.knowledge-dirty.txt`) ONLY if every needed edit succeeded or none were needed; on partial failure leave the failed paths. Report which docs you updated and how many files you skipped.

3. Relay the agent's summary (which docs changed, what was skipped).

### Pass 3 — Obsidian vault (runs inline, propose-then-write)

Keeps the vault built by `/obsidian-project-scope` alive: the capability map (`Sekce/`) and the open-defect register (`Nálezy/`).

**Gate — skip fast.** Vault root defaults to `~/Library/Mobile Documents/iCloud~md~obsidian/Documents`. If `<vault>/<ProjectName>/` doesn't exist → "No vault for this project" and skip. Most projects have no vault; don't create one here (that's `/obsidian-project-scope`'s job).

**Do not write straight to disk.** Unlike Pass 2, the vault is a hand-curated, human-facing knowledge base. Gather candidates, present them as a numbered list, let the user accept/edit/reject, *then* write. Same interaction model as Pass 1.

Three triggers, and **only** these three. Most sessions fire none of them — that's the expected outcome, not a failure.

#### Trigger 1 — did what the system can DO change?

Not "did code change" — code changes every session. **Did a capability appear, disappear, or change shape?** Concrete signals (check `.claude/.knowledge-dirty.txt` and the session's diff):

- a new key in the composition-root switch / feature registry (`EnabledDevices` & friends)
- a new API surface: hub, controller, route, exported command
- a new implementation of a capability interface (`IInvoiceService`, `ICashDeviceService*`, …)
- a project added to or removed from the build file
- a capability deleted or deliberately disabled

**Fixing a bug inside an existing capability is NOT this.** If the answer is "the system does the same things, just correctly now" → no `Sekce/` edit. Guard this hard: the vault's whole value is that it says *what*, not *how*. Implementation detail leaking in is how it dies.

When it does fire: propose a **minimal surgical edit** to the affected `Sekce/` note, in that note's voice. Never rewrite a note wholesale.

#### Trigger 2 — did a known defect get closed?

Scan `Nálezy/` for notes with `status: open` whose subject was touched this session. For each one actually fixed:

- flip `status: open` → `status: done`
- add `fixed: <commit-sha>` (and the date) to the frontmatter
- tick the `Hotovo, když` checkboxes that are genuinely met — **not the ones that aren't.** A defect fixed in code but unverified on hardware is not done; say so in the note rather than ticking the box.
- update the row in `Nálezy/_Nálezy.md`

If the commit doesn't exist yet (wrap-session usually runs after committing, but not always), say so and use the branch name — don't invent a sha.

**This is the highest-value part of Pass 3.** It's what makes the vault a living register instead of a snapshot that rots. It's cheap, unambiguous, and nobody else will do it.

#### Trigger 3 — was a new defect discovered?

Bugs are mostly found *while working*, not during audits. Anything that surfaced this session and is a defect — "this returns BUSY every time", "this guard never fires", "the docs describe a module that doesn't exist" — gets a new note in `Nálezy/`, in the format `/obsidian-project-scope` defines:

- frontmatter: `id` (next free number), `type` (bug/gap/drift), `severity` (by cost of failure, not effort), `status: open`, `area` (`[[Sekce note]]`), `evidence` (`file:line` — no evidence, no note), `source` (where it came from)
- body: **what's wrong → how it shows up in production → what to do about it → done when** (checkboxes)
- add a row to `Nálezy/_Nálezy.md`

A defect you can't reproduce or point at is a hunch. Write it as an open question in the note, not as a finding.

#### Finally

Validate the wikilinks (a broken `[[link]]` in a fresh vault is invisible until someone clicks it):

```bash
python3 - <<'EOF'
import os, re, glob
ROOT = "<vault>/<Project>"
files = glob.glob(os.path.join(ROOT, "**", "*.md"), recursive=True)
names = {os.path.splitext(os.path.basename(f))[0] for f in files}
broken = [(os.path.basename(f), re.split(r'\\?\||#', raw)[0].strip())
          for f in files
          for raw in re.findall(r'\[\[(.+?)\]\]', open(f, encoding="utf-8").read())
          if re.split(r'\\?\||#', raw)[0].strip() not in names]
print(f"notes: {len(files)} | broken: {broken or 'none'}")
EOF
```

The vault lives in iCloud, not git — there's nothing to commit, and nothing to roll back if you write junk. That's the reason Pass 3 asks before writing.

### Finish

Print a one-line summary of all three passes, then tell the user:

> Done. Run `/clear` (or `/exit`) now to end the session.

A skill cannot trigger `/clear` itself — that's a CLI built-in — so the user runs it.

## Notes

- This skill replaces the old SessionEnd headless spawns. The hook now only logs token usage; all intelligence lives here.
- The three passes are independent — if one is a no-op, still run the others.
- Pass 3 needs a vault built by `/obsidian-project-scope` first. Create vs. maintain: that skill creates the map, this one keeps it true.
