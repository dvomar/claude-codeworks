# security-auditor — prompt location

The `security-auditor` system prompt lives in exactly one place:

**`.claude/agents/security-auditor.md`**

Spawn it with `subagent_type: "security-auditor"`. If the registered subagent isn't
available, Read that file and inline its body (everything below the YAML frontmatter)
into a `general-purpose` agent instead.

This file used to hold a second copy of the prompt. The two drifted, so the copy was
removed — a fallback auditor that behaves differently from the primary one is worse
than no fallback at all.

Companion references the prompt points at:

- `../references/finding-schema.md` — the exact finding-object schema
- `../references/focus-areas.md` — focus-area definitions and depth mapping
- `../references/severity-rubric.md` — severity/confidence calibration
- `../references/dep-scanners.md` — per-ecosystem dependency scanners
