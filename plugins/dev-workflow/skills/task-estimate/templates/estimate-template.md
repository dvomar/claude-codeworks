# Odhad: {{TASK_NAME}}

**Datum:** {{DATE}}
**Kategorie:** {{CATEGORY}}
**Model práce:** kód píše LLM, senior zadává / reviduje / verifikuje

## Popis úkolu

{{DESCRIPTION}}

## Rozsah

- **Nové soubory:** {{NEW_FILE_COUNT}}
- **Modifikované soubory:** {{MODIFIED_FILE_COUNT}}
- **Odhad LOC:** ~{{LOC}}

### Dotčené soubory
{{FILES}}

## Časový odhad (senior hodiny)

| Fáze | Hodiny | Popis |
|------|--------|-------|
| Zadání & design | {{DESIGN_H}} | {{DESIGN_DESC}} |
| Supervize LLM implementace | {{SUPERVISION_H}} | {{SUPERVISION_DESC}} |
| Code review výstupu | {{REVIEW_H}} | {{REVIEW_DESC}} |
| Runtime / HW verifikace | {{VERIFY_H}} | {{VERIFY_DESC}} |
| MR / předání / koordinace | {{HANDOFF_H}} | {{HANDOFF_DESC}} |
| Buffer ({{BUFFER_PCT}}%) | {{BUFFER_H}} | {{BUFFER_REASON}} |
| **Effort total (senior)** | **{{EFFORT_H}} h** | Fakturovatelná práce |
| **Calendar (×{{MULTIPLIER}})** | **{{CALENDAR_H}} h** | Wall-clock s běžnými interrupts |

*Informativně: LLM implementace ~{{LLM_WALLCLOCK_H}} h wall-clock (běží souběžně se supervizí, nefakturuje se po hodinách).*

## Cena

| Položka | Hodnota |
|---------|---------|
| Effort (senior) | {{EFFORT_H}} h |
| Sazba | {{RATE}} {{CURRENCY}}/h |
| **Celková cena** | **{{COST}} {{CURRENCY}}** |

Calendar hours jsou informativní (delivery timeline), ne fakturovatelné.

## Klíčové soubory

{{KEY_FILES}}

## Senior-only položky (LLM nezrychlí)

{{SENIOR_ONLY_ITEMS}}

## Co odhad NEzahrnuje

{{EXCLUDED}}

## Rizika a poznámky

{{RISKS}}

---
*Estimate created with Claude Code task-estimate skill (LLM-writes-code calibration)*
