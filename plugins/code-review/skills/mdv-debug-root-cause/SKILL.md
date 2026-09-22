---
name: mdv-debug-root-cause
description: 'Find why something actually breaks and fix that cause, not the symptom — a failing test, a crash, a wrong value, an intermittent fault, a regression that used to work. Reproduces first and refuses to edit until it can, narrows with bisect, logs and a minimal case, states a falsifiable hypothesis, proves it before touching code, then closes with a regression test that fails on the old code. Use whenever something is reported broken rather than missing: "tohle padá", "proč to nefunguje", "zjisti proč", "rozbilo se to po", "občas to spadne", "vrací to špatnou hodnotu", "najdi příčinu", "why does this fail", "this used to work", "debug this", "the test is red", "it works locally". Prefer this over jumping straight to an edit whenever the cause is not already obvious from the error.'
argument-hint: "<co je rozbité — chyba, test, symptom> [--from <commit/tag, který ještě fungoval>]"
user-invocable: true
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, AskUserQuestion, Agent
---

# Debug: root cause

CLAUDE.md says root causes only, no band-aids. This is how that gets enforced instead
of hoped for. Six steps, in order. Step 1 is a gate, not a suggestion.

The failure mode this exists to prevent: reading an error, recognising its shape,
editing the line it points at, and finding the symptom gone while the cause is still
there. That fix survives until the next input that takes a different path through the
same bug.

## 1. Reproduce — a hard gate

**Until the failure reproduces on demand, do not edit a single line of source.**

Get to a command that fails, reliably, and write it down. Whatever the reproduction is,
it must be something you can run again after the fix and watch turn green.

**Already reproduced for you.** A complete, deterministic failure handed over with the
relevant source — a pasted CI log, a test output, a stack trace with the file it points
at — *is* the reproduction. Record what it shows and move to step 2. Do not insist on
re-running it before you will think, and do not stall when you have no shell to re-run
it with: say in one line that you are working from the provided output, then continue.
An agent that deadlocks on its own gate is worse than one that never had the gate.

If it will not reproduce:

- **Intermittent** — run it in a loop (`for i in $(seq 50); do …; done`) and record the
  rate. A 3-in-50 failure is reproducible; it just needs a loop around it. Do not treat
  a rate as "cannot reproduce".
- **Environment-dependent** — get the difference explicitly: versions, env vars, data,
  clock, locale, architecture. "Works locally" is a clue about the environment, not a
  verdict on the bug.
- **Only in production** — reproduce against a copy of the real input. Ask the user for
  the payload, the row, the log line.
- **Genuinely not reproducible** — stop and say so. Report what you tried, what you
  would need (a log level, an input sample, access), and ask. A fix aimed at a failure
  you have never seen is a guess, and shipping it makes the next investigation harder
  because now nobody knows which change mattered.

## 2. Narrow

Shrink the surface until the remaining suspect area is small enough to read. Pick
whichever of these the failure allows, cheapest first:

- **Bisect in time.** `git bisect` when it used to work. `--from` skips the hunt for a
  good commit. Automate it (`git bisect run <cmd>`) whenever the reproduction is a
  command — it is faster than judging each step by hand and it cannot be swayed by
  what you expect to find.
- **Bisect in input.** Halve the failing input until removing anything makes the
  failure disappear. The minimal case usually names the cause by itself.
- **Bisect in the stack.** Assert or log the value at the boundary between layers and
  ask where it stops being correct. Walking in from the boundary beats stepping out
  from the crash site — the crash is where it surfaced, not where it went wrong.
- **Read the actual error.** Full stack trace, innermost exception, the errno behind
  the wrapper. Do not stop at the top frame or the library's own message.

Keep the main context clean: when narrowing means grepping through a large log, a build
output or a long trace, delegate that read to an `Agent` and take back the conclusion.

## 3. Hypothesise — one sentence, falsifiable

Write the hypothesis down before going further, in the form:

> **`<specific thing>` is `<specific state>` when `<specific condition>`, which causes
> `<observed symptom>`.**

"Something in the cache is wrong" is not a hypothesis. "`GetCustomer` returns the
previous tenant's row because the cache key omits `tenantId`, so a second tenant
reading within the TTL sees the first tenant's data" is.

If you cannot write it that sharply, go back to step 2 — you have not narrowed enough,
and the sharpness of the sentence is the measure of that, not your confidence.

## 4. Prove it

State what must be true if the hypothesis holds, then go and look. A log line, a
breakpoint value, a query, a one-off script, a targeted test.

**Prove before editing.** A fix that makes the symptom disappear is not evidence the
hypothesis was right — the edit may have changed timing, ordering or a side effect.
Once the code has moved, you can no longer tell the difference.

If the evidence contradicts the hypothesis, that is the step working. Say what it ruled
out and return to step 3. Two or three wrong hypotheses with evidence beat one right
guess without it, because only the first kind leaves the next person something to read.

## 5. Fix the cause

Fix the thing the evidence names, and nothing else.

- The edit belongs where the cause is, not where the symptom appeared.
- No defensive `try/catch`, null guard or retry around a cause you understand. Those are
  band-aids, and CLAUDE.md rules them out.
- Follow the project's conventions from `.claude/knowledge/` — this is still ordinary
  code, and a fix that violates the surrounding patterns is a second problem.
- Resist widening. A second bug found on the way gets written down and raised, not
  quietly bundled into this change.

If the real fix is large or architectural, stop and put the options to the user:
the minimal correct fix, the proper one, and what each costs. Do not silently pick the
band-aid because it is smaller.

## 6. Regression test

**The test must fail on the old code.** Write it, revert the fix (`git stash`), watch it
go red, restore the fix, watch it go green. A test that passes either way protects
nothing and will be trusted anyway, which is worse than having no test.

Put it where the project keeps its tests, named after the behaviour rather than the
bug number. Then re-run the step 1 reproduction and confirm it is gone.

## Report

Short, and in this order:

1. **Symptom** — what was observed.
2. **Cause** — the hypothesis that survived, at `file:line`.
3. **Evidence** — what proved it.
4. **Fix** — what changed and why there.
5. **Test** — the regression test, and confirmation it fails without the fix.
6. **Not fixed** — anything found on the way and deliberately left. Never drop these
   silently; they are the most valuable part of the report for whoever reads it next.
