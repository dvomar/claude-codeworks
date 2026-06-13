---
name: task-estimate
description: Creates time and cost estimate for a development task (calibrated for LLM-writes-code workflow — senior dev specifies, reviews and verifies)
user-invocable: true
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Bash, Task
---

# Skill: Task Estimation

Creates a realistic estimate for the **LLM-writes-code workflow**: the LLM (Claude Code, parallel agents) writes all code, unit tests and docs; the senior developer writes the assignment, makes design decisions, supervises, reviews the output, and does everything the LLM physically cannot — runtime/HW verification, MR process, coordination, deployment. **Billed effort = senior hours.** LLM wall-clock is reported as informative only.

## Input

Argument = task description, optionally prefixed with `--key value` overrides.

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--rate` | 875 | Hourly rate in CZK |
| `--lang` | cs | Output language (`cs` / `en`) |
| `--dir` | docs/odhady | Output directory |
| `--currency` | CZK | Currency label |

```
/task-estimate Implement user avatar upload
/task-estimate --rate 900 --lang en Implement user avatar upload
```

Parse `--key value` pairs as overrides, treat the rest as task description.

## Procedure

1. **Analyze codebase** with Glob/Grep/Read (use parallel Explore agents pro broader scope). Identify affected files, similar implementations, existing patterns to reuse.
2. **Categorize** using table below → gives **LLM wall-clock** (informative) and **senior supervision/design** base.
3. **List senior-only work items** (verification checklist below) — these are estimated at full price, NOT discounted by LLM.
4. **Estimate phases** using % table below; sum to get pre-buffer senior total.
5. **Apply ONE buffer** (highest applicable). Never additively.
6. **Compute calendar hours** from senior effort hours using multiplier rule.
7. **Generate output** using `templates/estimate-template.md`. Save to `{dir}/YYYY-MM-DD-task-name.md` (lowercase, hyphenated).

## Categorization (LLM writes the code)

| Category | LLM wall-clock | Senior design+supervision | Criteria |
|----------|----------------|---------------------------|----------|
| New integration | 2–5 h | 1–2.5 h | New external system, new HW module, new cross-repo feature |
| Extension of existing | 0.5–2 h | 0.5–1 h | New functionality in existing module |
| Modification / bugfix | 0.2–0.5 h | 0.2–0.5 h | Fix, logic change |
| Trivial | < 0.2 h | 0.1 h | Config tweak, doc, renaming |

**Supervision rule of thumb:** senior design+supervision ≈ **0.5× LLM wall-clock** (zadání, mid-flight rozhodnutí, průběžná kontrola). U dobře ohraničených portů mezi vlastními codebase klesá k 0.3×.

**Kalibrace vůči starému senior-píše-kód modelu:** samotné kódování ≈ **10–15 %** původních hodin; celý task včetně lidské verifikace ≈ **25–35 %**. (Referenční bod: printer-paper-states 06/2026 — původní odhad 40–60 h, realita ~4 h LLM-supervised + ~8 h senior-only = ~12 h.)

## Phases (% of senior effort total)

| Phase | % | Why this share |
|-------|---|----------------|
| Zadání & design | 15–20 % | Senior píše prompt/spec, dělá architektonická rozhodnutí; LLM nezrychlí user latency |
| Supervize LLM implementace | 20–30 % | Sledování průběhu, mid-flight korekce, odpovědi na dotazy; kód samotný píše LLM |
| Code review výstupu | 15–20 % | Plausible-but-wrong je hlavní riziko LLM kódu — review se NEškrtá, je to hlavní quality gate |
| Runtime / HW verifikace | 25–40 % | Fyzický test na zařízení, smoke na živém systému — LLM nezrychlí vůbec; u HW tasků dominantní fáze |
| MR / předání / koordinace | 10–15 % | MR proces, FE/QA koordinace, číselníky, release notes |

## Senior-only verification checklist

Při kroku 3 projdi a oceň plnou sazbou vše, co platí:

- [ ] Test na fyzickém HW (tiskárna, cash device, terminál) — typicky 2–4 h per zařízení/platforma
- [ ] Runtime smoke na živém/staging systému
- [ ] MR review kolegou + zapracování připomínek
- [ ] Koordinace s FE/jiným týmem (kódy, kontrakty, release pořadí)
- [ ] Deploy / konfigurace na místě / per-site zapnutí feature flagu
- [ ] Přístupy, credentials, VPN do klientské sítě

## Buffer (pick the single highest applicable)

- Known area, existing patterns: **+5 %**
- LLM-unfamiliar domain (proprietární protokol, nedokumentované API) — vyšší riziko plausible-but-wrong: **+15 %**
- External API dependency: **+10 %**
- Hardware integration: **+25 %** (fyzické testování LLM nezrychlí; driver chování se ověří až na místě)
- Multiple parallel sub-features in one task: **+10 %**

## Effort → Calendar multiplier

Senior effort hours ≠ wall-clock. Apply multiplier based on expected workflow:

| Workflow | Multiplier |
|----------|-----------|
| Dedicated focused session | ×1.0 |
| Normální pracovní den (mítingy, kontext switch) | ×1.8 |
| Roztažený přes více dnů s interrupts | ×2.5 |

**Default:** ×1.8. Override v risks/notes pokud kontext napovídá jinak. LLM wall-clock běží paralelně se supervizí — do calendar se nepřičítá zvlášť.

## Cost rule

`Cost = senior_effort_hours × rate × currency`

LLM wall-clock se **nefakturuje po hodinách** (token náklady řeš případně jako samostatnou položku v poznámce). Calendar hours jsou **informativní** (delivery timeline), ne fakturovatelné. Pokud klient bill-by-calendar, zmiň v `Rizika`.

## What the LLM does NOT speed up (estimate at full price)

- Runtime smoke testing on live system / hardware
- User/stakeholder decision latency
- Human MR review approval
- Deployment, ops, monitoring setup, per-site config rollout
- Acquiring credentials / env access
- Domain knowledge transfer requiring stakeholder
- Cross-team release coordination (FE číselníky, translations sync)

These map to the `Runtime/HW verifikace` and `MR/předání` phases — if the task is unusually heavy on them (multi-site rollout, several HW devices), add explicit line items instead of stretching the phase %.

## What the LLM DOES absorb (don't bill as senior hours)

- Psaní kódu, unit testů, šablon, configů, docs
- Codebase discovery (parallel Explore agents)
- Build/test iterace, oprava kompilačních chyb
- Mock/simulátor testy spustitelné lokálně
- První self-review pass (skill /code-review)

## References

- Template: `templates/estimate-template.md`
- Example: `examples/dms3-estimate.md` (legacy senior-writes-code calibration — historical reference, ne baseline)
- Kalibrace 06/2026: printer-paper-states (2×BE + 2×FE port; odhad 40–60 h → realita ~12 h senior)
