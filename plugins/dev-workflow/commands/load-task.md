Load a ClickUp task by custom ID or name search and display its details.

## Input

The argument `$ARGUMENTS` contains either:
- A **custom ID** (e.g., `PROJ-123`, `TEAM-456`) — matches pattern `[A-Z]+-\d+`
- A **task name** or keywords to search for

## Steps

### If custom ID (matches `[A-Z]+-\d+`):

1. Use `mcp__clickup__clickup_get_task` with `task_id` set to the custom ID, `detail_level: "detailed"`, `subtasks: true`.
2. Display the task summary (see Output Format below).

### If task name / keywords:

1. Use `mcp__clickup__clickup_search` with `keywords` set to the input, filtered to `asset_types: ["task"]`.
2. If multiple results found, display a numbered list with task name, custom ID, status, and assignees. Ask the user which one they meant.
3. Once a task is selected, use `mcp__clickup__clickup_get_task` with `detail_level: "detailed"`, `subtasks: true` to load full details.
4. Display the task summary.

## Output Format

Display the task in this structured format:

```
## {custom_id}: {task_name}

- **Status:** {status}
- **Assignees:** {assignee names}
- **Priority:** {priority}
- **List:** {list name}
- **Due date:** {due_date or "—"}
- **URL:** {task url}

### Description
{task description, truncated to reasonable length}

### Subtasks
{list of subtasks with status if any, or "No subtasks"}
```

## Rules

- Always show the ClickUp URL so the user can open the task in browser.
- If the task has a long description, show a concise summary (first ~500 chars) and mention it's truncated.
- If search returns no results, say so and suggest checking the ID/name.
- Do NOT modify the task in any way — this is read-only.
