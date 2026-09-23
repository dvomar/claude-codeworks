---
name: mdv-enforce-english
description: Make a repository's developer-facing text English and keep it that way — records the language policy in CLAUDE.md (code, comments, commit messages and Markdown in English; comments only where the code is not self-explanatory) and audits the repo for text that breaks it. Use this whenever someone sets up a new project, asks to "make the repo English", "enforce English", "write the language rule into CLAUDE.md", complains that non-English comments or commit messages keep creeping in, or asks whether a codebase is consistently in one language — even if they don't name the policy or the file.
---

# Enforce English

Two jobs, both backed by a script so the result does not depend on how carefully you
read a diff:

- `apply.py` writes the policy into `CLAUDE.md` so every later session inherits it.
- `audit.py` reports developer-facing text that breaks the policy.

Neither script guesses. `apply.py` refuses rather than risk deleting work, and
`audit.py` never modifies anything — classifying a hit is judgement, and judgement is
your job, not the script's.

## Process

### 1. Locate the project root

```bash
git rev-parse --show-toplevel 2>/dev/null || pwd
```

`CLAUDE.md` at that path is the target. Everything else in the file is left untouched;
the policy lives inside `<!-- language-policy:start -->` / `<!-- language-policy:end -->`
markers.

### 2. Decide the exceptions

Most products have text that must **not** be anglicised. Work out whether this repo has
any, from evidence rather than assumption:

- Are UI strings, e-mail copy or error messages in another language? Open a component
  or a template and look.
- Are route segments or public URLs non-English? Renaming those breaks shared links.
- Is there a specification, contract or legal document in another language?
- Is there seed or fixture data in another language?

Each exception becomes one short line naming concrete paths.

Two things that are **not** exceptions, so don't record them: a proper noun (a product,
company or place name), and a domain term with no good English equivalent used inside an
otherwise-English sentence — "stored in minor units (haléře)" is fine English prose that
happens to contain a Czech word. Exceptions are for whole categories of text that stay
in another language, not for individual words.

If the repo is English throughout, pass no exceptions at all.

### 3. Write the policy

```bash
python3 <skill-dir>/apply.py --project "$(git rev-parse --show-toplevel)" \
  --exception "Specification in docs/ stays in its original language." \
  --exception "UI strings and e-mail copy stay in the product language."
```

- Omit `--exception` entirely on a re-run to keep whatever is already recorded.
- Passing `--exception` at all **replaces** the recorded list, so pass the full set.
- `--check` writes nothing and exits `2` if the file would change, `0` if it would not.

It prints `created:`, `updated:` or `unchanged:` and exits `0`. Report which. Two cases
it handles so you don't have to check first: a **duplicated block** is collapsed onto the
first one, keeping the text between the copies; an **unpaired marker** left by a bad
hand-edit makes it exit `1` and change nothing, because guessing where the block ended
would delete whatever followed. Remove the stray line by hand and re-run.

### 4. Audit

```bash
python3 <skill-dir>/audit.py --project "$(git rev-parse --show-toplevel)" \
  --exclude docs/ --exclude .claude/
```

Pass `--exclude` for every path covered by an exception — a foreign-language spec
directory otherwise drowns the real findings. Other flags: `--commits N` (default 50),
`--strings` to also scan string literals (noisy — most are user-facing on purpose, but
it is how you find a non-English log message), `--strict` to exit `3` when anything is
found, for CI.

It scans comments, Markdown prose and commit subjects, flagging text with non-ASCII
letters or with no recognisable English words. **The second test is the one that
matters**: a plain `grep` for diacritics gives a repository whose non-English text
happens to be accent-free a clean bill of health it has not earned — "Prvni verze
fakturace" has nothing to grep for. Quoted spans are dropped before the test, since an
English comment that names a foreign UI button by quoting it is exactly what the policy
asks for.

The output is candidates, not verdicts. Classify each:

- **Violation** — comment, identifier, test name, commit subject, Markdown prose.
- **Legitimate** — user-visible string, route segment, seed data, spec document, proper
  noun, or anything covered by a recorded exception.

Report the violations individually; for the legitimate ones give a count and the reason
they are fine. Then stop — fixing is step 5, and only on request.

### 5. Fixing violations (only when asked)

- Translate comments faithfully. They usually carry the *why* behind a decision, and
  that reasoning is the valuable part — do not flatten it into a restatement of the code.
- Drop a comment instead of translating it when the code alone already says it.
- Never touch a string without first checking whether a user sees it.
- Never rename a route segment or a public URL.
- Rewrite commit subjects with `git filter-branch --msg-filter` or an interactive
  rebase, and only on a branch that has not been shared, or with the user's explicit
  agreement to force-push.
- Re-run the project's own checks afterwards (lint, typecheck, formatter, tests), and
  `audit.py` again to confirm the count dropped.

## Example

Before — `CLAUDE.md` in a Czech-built invoicing tool:

```markdown
# Fakturace

Internal invoicing tool for the accounting team.
```

After `apply.py --exception "User-visible status labels in src/invoice.ts stay Czech."`,
the file keeps everything above and gains the marked block; `audit.py` then reports the
Czech README line, the Czech comment in `src/invoice.ts`, and the commit subject
`Prvni verze fakturace`, while leaving the `STATUS_LABELS` values alone.

## Rules

- Both scripts are the source of truth for behaviour. Edit them rather than hand-editing
  the generated block, and keep `test_apply.py` and `test_audit.py` green — run them
  after changing a script, not on every ordinary use of the skill.
- Running the skill twice must produce no diff. If it does, that is a bug in `apply.py`.
- Never anglicise user-facing product text. The policy explicitly protects it.
- Never create a `CLAUDE.md` outside the project root.
- The generated block survives Prettier untouched: Prettier defaults to
  `proseWrap: "preserve"`, so it never rewraps the lines regardless of `printWidth`. If a
  project sets `proseWrap: "always"`, run the formatter once and commit the result — from
  then on it is stable again.
