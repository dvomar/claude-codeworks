---
name: task-estimate
description: Creates detailed time and cost estimate for a development task
user-invocable: true
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Bash, Task
---

# Skill: Task Estimation

Create a detailed time and cost estimate for the specified development task.

## Input

The skill argument contains the task description to estimate, optionally prefixed with parameter overrides.

## Configurable Parameters

These are the default values. Override any parameter by prefixing the task description with `--param value`:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--rate` | 100 | Hourly rate |
| `--lang` | en | Output language (`en` for English, or any language code) |
| `--dir` | docs/estimates | Output directory for the saved estimate file |
| `--currency` | USD | Currency label used in cost calculation |

### Examples

```
/task-estimate Implement user avatar upload
/task-estimate --rate 900 --lang en Implement user avatar upload
/task-estimate --rate 150 --dir docs/estimates --currency EUR Implement payment gateway integration
```

Parse the argument string: extract any `--key value` pairs as overrides, treat the remaining text as the task description. Use defaults for any parameter not explicitly provided.

## Procedure

### 1. Task Analysis

Explore the codebase using the Explore agent:
- Identify relevant existing code
- Determine which files will be affected
- Estimate scope of changes (number of files, lines of code)

### 2. Categorization

Determine the task category:

| Category | Typical Time | Criteria |
|----------|--------------|----------|
| New integration | 12-24h | New external system, new HW module |
| Extension of existing | 4-10h | New functionality in existing module |
| Modification/bugfix | 1-4h | Fix, logic change |
| Trivial change | 0.5-1h | Minor adjustment, configuration |

**Important:** This project has well-established patterns. Most new code follows existing templates. Factor this in — don't estimate as if building from scratch.

### 3. Phase-Based Estimate

Break down work into phases:

| Phase | % of Time | Description |
|-------|-----------|-------------|
| Analysis | 10-15% | Code exploration, understanding architecture |
| Design | 5-10% | Solution design |
| Implementation | 45-55% | Writing code |
| Testing | 15-20% | Manual testing, debugging |
| Refinement | 5-10% | Adjustments, code review |

### 4. Apply Buffer

- Known area: +5-10%
- New area (first implementation of this type): +15-25%
- External API dependency: +10-20%
- Hardware integration: +20-35%

**Rule:** Never apply multiple buffers additively. Pick the single highest applicable buffer. Total estimate should feel tight but achievable.

### 5. Generate Output

Use the template from `templates/estimate-template.md`. Fill in all placeholders with actual values.

Apply the configured parameters:
- Use `--rate` for hourly rate in cost calculation
- Use `--currency` for currency label
- Write the estimate in the language specified by `--lang` (translate all headings, labels, and descriptions)
- Save to the directory specified by `--dir`

## Output Format

1. **Display in terminal** — clear table with estimate
2. **Save to file** — `{dir}/YYYY-MM-DD-task-name.md`

Create filename from task description:
- Convert to lowercase
- Replace spaces with hyphens
- Remove special characters
- Add date prefix

## References

Read methodology: `.claude/knowledge/estimation-methodology.md`
See example: `.claude/skills/task-estimate/examples/example-estimate.md`
