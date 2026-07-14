---
name: integration-proposal
description: Produce a feature/integration design proposal in TWO self-contained HTML documents from one analysis — an internal management doc (code-grounded, file:line, scope/sizing, risks) and a customer-facing doc (business language, flow, no internals). Backed by multi-codebase discovery, direct code verification, business-decision clarification, and convention-fit architecture (+ PDF). Use when asked to design or propose an integration/feature architecture or flow for approval ("navrhni architekturu/flow", "návrh integrace", "podklad pro vedení", "návrh pro zákazníka", "design proposal").
user-invocable: true
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, Task, AskUserQuestion
---

# Skill: Integration / Feature Design Proposal

Produces the kind of document `docs/integration-proposals/withdrawal-tukas/vyplata-hotovosti-tukas-navrh.html` is: a **decision-ready proposal** for a new feature or third-party integration, grounded in the actual codebase, suitable for management/stakeholder approval.

The value of such a document does **not** come from the HTML template — it comes from the **work done before** writing it: multi-codebase discovery, direct verification, and clarifying the decisions that change the design. The template only presents that work. Do the work; don't skip to the HTML.

## When to use

- "Navrhni architekturu a flow pro <feature>" / "design the integration for X"
- "Potřebuju podklad pro vedení / ke schválení"
- Scoping a new ERP/HW/payment integration before implementation
- Comparing how something was done in a predecessor codebase and porting the design

Not for: implementing the feature (use `/code-implement-feature`), pure cost numbers (use `/task-estimate`), or codebase convention docs (use `/code-analyze-codebase`).

## Inputs

Argument = the feature/integration to design. Optional `--key value` overrides.

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--target` | current repo | Repo where the feature will live |
| `--refs` | known siblings | Reference repos to mine for prior art (comma-sep paths) |
| `--dir` | `docs/<kebab-feature>` | Output directory |
| `--lang` | cs | Deliverable language (audience-driven; internal Czech = `cs`) |

Known reference repos in this org (use unless `--refs` given): `/Users/mw/Develop/Projects/Czech-Kiosk/cashmachine4be` (legacy predecessor — best design template), `/Users/mw/Develop/Projects/Czech-Kiosk/cashmachine2` (older generation).

## Procedure

### Phase 1 — Frame & locate
State the feature in **business terms** and name the **opposite/related existing flow** (e.g. payout ↔ payment). From `CLAUDE.md` + `.claude/knowledge/` identify where it would live (hubs, services, modules, DI, naming conventions). Output: a one-paragraph framing + the ecosystem anchors you'll reuse.

### Phase 2 — Multi-codebase discovery (parallel)
Fan out **Explore agents in a single message** (one per repo) so they run concurrently:
- **Target repo**: does it already exist — whole / skeleton / none? Enumerate what **exists vs missing** across every layer (interface/contract, hub/API, orchestration service, hardware/IO adapter, DB entity + controller, DI wiring, notifications, FE contract), each with **file:line**. Demand an explicit verdict.
- **Each reference repo**: trace the full flow — entry/trigger → orchestration → hardware/IO → state machine → persistence → ERP/3rd-party → receipt → FE contract → failure/partial/timeout handling. This is your **design template**.

Tell every agent to (a) distinguish closely-related-but-different operations (e.g. "change during payment" vs "standalone payout"), (b) return file:line + code excerpts, not prose only.

### Phase 3 — Verify critical claims directly
Do **not** trust agent summaries for anything load-bearing. `Read` the actual files for: the core contract/interface, the key DTO, the hub/API method, the orchestration service, and the ERP/IO client. Confirm with exact file:line: stubs, half-finished branches, bugs, and **security issues** (secrets/PINs/tokens logged, missing auth). This direct verification is what makes the proposal trustworthy and the file:line references correct.

### Phase 4 — Clarify business decisions
Identify the **2–4 forks that materially change the design and cannot be inferred from code**. Typical: trigger/UX model, authorization method, failure policy (refuse vs partial vs round), idempotency/reconciliation policy, limits. Ask via **`AskUserQuestion`**, each option carrying a short recommendation and trade-off. Fold answers into the design; leave genuinely-undecided ones as **"open questions for management"** in the doc. Note in the doc which choices were the user's vs your defaults.

### Phase 5 — Design & document (TWO files)
Synthesize a **KISS architecture that reuses existing patterns** (name them explicitly), with the **smallest new surface** (fewest files/LOC, easy to delete later). Include edge-case/reconciliation thinking — especially the **dangerous branch** (a side-effect done but its confirmation failed). Then emit **both** HTML deliverables from one analysis (below) and **offer to render them to PDF** via the `html-to-pdf` skill.

## Two documents, one analysis

Same discovery and design produce two audience-tuned files. **They share the feature, flow and decisions; they differ in disclosure level.**

| | Internal (`-navrh-interni.html`) | Customer (`-navrh-zakaznik.html`) |
|---|---|---|
| Template | `templates/proposal-internal-template.html` | `templates/proposal-customer-template.html` |
| Audience | vedení / dev — decision & build | klient — value & buy-in |
| Visual | structured/corporate (withdrawal style) | designed/visual (Raiffeisen style) |
| Language | business + technical | business only |

**HARD RULE — the customer doc must NEVER contain:** code identifiers (class/interface/method names), file paths or `file:line`, our internal architecture component names, repo/generation names (cm5be/cm4be/cm2), our internal scope sizing (S/M/L) or effort/hours, "what already exists in our codebase", security issues found in our code, or names of our other clients. When in doubt, leave it out of the customer doc.

**Reframes (internal → customer):** "what we must build / current state" → **"Jak to funguje"** (the flow); "open questions" → **"Co potřebujeme od vás"** (their prerequisites/decisions); internal risks → **"Co ověříme před spuštěním"** (validation in business terms); architecture diagram → **actor legend + flow** (no component internals).

## Section map

| Section | Internal | Customer |
|---------|:---:|:---:|
| Header + status badge | ✅ | ✅ (eyebrow + lede, no "Návrh k schválení" badge) |
| Manažerské shrnutí + "rozhodnutí, která potřebujeme" | ✅ | — |
| Co to přináší (business benefits) | ◻ | ✅ |
| Současný stav — exists vs missing, **file:line**, cross-generation table | ✅ | — (never) |
| Navrhovaná architektura — layer diagram, existing-vs-new, reused conventions | ✅ | — |
| Actor legend | ◻ | ✅ |
| Flow — internal: guard/ERP/critical tags · customer: "Jak to funguje", actor accents | ✅ | ✅ |
| Decision branch (OK / error) | ✅ | ✅ |
| Hraniční stavy & reconciliace (incl. side-effect-done-but-confirm-failed) | ✅ | — |
| Rozsah prací + **size S/M/L** | ✅ | — (never) |
| Otevřené otázky (internal: for mgmt/3rd party) | ✅ | — |
| Co potřebujeme od vás (customer prerequisites/decisions) | ◻ | ✅ |
| Rizika — mark **make-or-break** | ✅ | — |
| Co ověříme před spuštěním (validation, business terms) | — | ✅ |
| Návrh postupu (phases) | ◻ | ◻ |
| Odhad pracnosti — delegate to `/task-estimate` | ◻ | ◻ (only as price, never sizing) |

Drop sections that don't apply; never ship empty placeholders.

## Quality bar (what separates a valuable doc from a generic one)

- **Grounded:** every "exists / missing / stub" claim cites **file:line**. No hand-waving.
- **Honest:** name the stubs, bugs and security issues you found (e.g. "hub logs the PIN in plaintext"). Don't gloss to look tidy. (Matches the repo's honesty-over-agreement rule.)
- **Convention-fit & minimal:** reuse named existing patterns; the new surface is as small as possible (KISS — fewer files, fewer LOC, easy to delete). Call out *why* it fits the ecosystem.
- **Decision-oriented:** a manager can approve or choose from it; open questions are explicit, each with a recommendation.
- **Edge-case aware:** always include the failure branch where the irreversible action succeeded but its confirmation/reporting failed, and how it reconciles.
- **Self-contained:** inline CSS, no external fonts/CDN; renders offline and to PDF; print CSS with `@page`/`break-inside`.

## Output & visual

- **Two** self-contained HTML files in `{dir}/`: `<kebab-feature>-navrh-interni.html` and `<kebab-feature>-navrh-zakaznik.html`.
- Both inline their CSS (no CDN), are print/PDF-ready (`@page` + `break-inside`), and derive from the **same** analysis — only the disclosure level differs (see "Two documents, one analysis").
- Internal visual = withdrawal style (structure/completeness). Customer visual = Raiffeisen style (numbered spine, decision branches, actor legend, validation grid). Set the customer `--accent` to the client's/partner's brand colour.
- Language follows the audience (`cs` default for both here; the customer doc is business-only).
- After writing, **re-scan the customer doc for leaks** (run the HARD RULE checklist — grep for class names, file paths, `cm5be`/`cm4be`, S/M/L), print both paths, note which is internal-only, and **offer `/html-to-pdf`** for the handover PDFs.

## References

- **Internal gold standard** (completeness + code-grounding + decision framing): `docs/withdrawal-tukas/vyplata-hotovosti-tukas-navrh.html`
- **Customer-style reference** (spine, decision OK/error branches, actor legend, validation grid): `docs/raiffeisen-instant-qr/flow.html`
- **Templates:** `templates/proposal-internal-template.html` · `templates/proposal-customer-template.html`
- **Costing:** `/task-estimate` (its internal `-odhad` / client `-nabidka` split mirrors this skill's two-doc model) · **Discovery:** Explore agents, `/code-analyze-codebase` · **PDF:** `html-to-pdf` skill
- Default reference repos: cm4be (legacy), cm2 (older) under `/Users/mw/Develop/Projects/Czech-Kiosk/`
