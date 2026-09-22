# Security Audit — {{project_name}}

**Date:** {{audit_date}}
**Depth:** {{audit_depth}}  
**Target:** `{{target}}`
**App class:** `{{app_class}}` (confidence: {{app_class_confidence}})
**Deployment exposure:** `{{deployment_exposure}}`
**Markers:** {{markers}}

---

## Executive summary

{{1-2 paragraphs. What was audited, what was found at a glance, what the top risks are. Plain language — should be readable by someone who can't read the code.}}

### Findings by severity

| Severity   | Count |
|------------|-------|
| Critical   | {{n_critical}} |
| High       | {{n_high}} |
| Medium     | {{n_medium}} |
| Low        | {{n_low}} |
| Info       | {{n_info}} |
| Suppressed | {{n_suppressed}} |

### Top urgencies (fix first)

1. **[{{F-001}}] {{title}}** — `{{file:line}}` — {{one-line fix}}
2. **[{{F-002}}] {{title}}** — `{{file:line}}` — {{one-line fix}}
3. **[{{F-003}}] {{title}}** — `{{file:line}}` — {{one-line fix}}

---

## Attack chains

{{Only if Deep + chains found. Otherwise skip section.}}

### C-1: {{Chain title}}

**Reaches:** {{Critical/High}} impact — {{e.g., "Cash payout to attacker"}}

**Steps:**
1. **[F-003]** {{step description}}
2. **[F-007]** {{step description}}
3. **[F-012]** {{step description}}

**Narrative:** {{2-3 sentences explaining how an attacker chains these.}}

**Break the chain by fixing:** {{which finding is the cheapest single fix that breaks the chain}}.

---

## Findings (sorted by severity, then focus area)

### Critical

#### F-001 — {{title}}

- **Focus area:** {{focus_area}}
- **Severity:** Critical
- **Confidence:** {{confidence}}
- **CWE:** {{cwe_list}} · **OWASP:** {{owasp_list}}

**Summary.** {{1-2 sentences}}

**Evidence.**
```{{lang}}
// {{file}}:{{line_start}}-{{line_end}}
{{snippet}}
```

**Impact.** {{what attacker gains}}

**Exploitability.** {{how reachable; trust boundary}}

**Deployment context.** {{LAN-only / internet-exposed / etc.}}

**Fix.** {{summary, then optional diff}}

```{{lang}}
{{before/after diff}}
```

**References.** {{links}}

---

#### F-002 — ...

(Repeat for each Critical, then High, Medium, Low, Info.)

---

## Suppressed findings (false positives)

| ID | Title | Rationale |
|---|---|---|
| F-FP-1 | {{title}} | {{why suppressed — e.g., "Test fixture; not reachable from prod code path."}} |

---

## Limitations

- {{e.g., "trivy not installed; container image not scanned."}}
- {{e.g., "Dynamic dispatch via reflection in Module X — static analysis incomplete."}}
- {{e.g., "Vendored DryIoc library (~16 KLOC) excluded from scan."}}

---

## Methodology

- Recon: see `.claude/security/recon.md` and `recon.json`.
- Subagents per focus area: {{list of focus areas actually run}}
- External tools used: {{list, or "static analysis only"}}
- Out-of-scope: {{paths excluded}}

## Next steps

1. Triage Critical + High with engineering lead within {{N}} days.
2. Verify any `confidence: low` findings via targeted manual review or runtime test.
3. Address attack-chain shortest fix first.
4. Schedule re-audit after fixes — diff the next `audit-*.md` against this one.
