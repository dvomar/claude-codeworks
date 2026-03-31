Load a ClickUp task by custom ID or name search and display its details. Optionally start time tracking.

## Input

The argument `$ARGUMENTS` contains either:
- A **custom ID** (e.g., `ROBE-4991`, `ROBE-123`) — matches pattern `[A-Z]+-\d+`
- A **task name** or keywords to search for

## Steps

### If custom ID (matches `[A-Z]+-\d+`):

1. Use `mcp__clickup__clickup_get_task` with `task_id` set to the custom ID, `detail_level: "detailed"`, `subtasks: true`.
2. In parallel, use `mcp__clickup__clickup_get_task_comments` with the same `task_id` to load comments.
3. In parallel, use `mcp__clickup__clickup_search` with `keywords` set to the custom ID, filtered to `asset_types: ["attachment"]` to find attachments.
4. Display the task summary (see Output Format below).

### If task name / keywords:

1. Use `mcp__clickup__clickup_search` with `keywords` set to the input, filtered to `asset_types: ["task"]`.
2. If multiple results found, display a numbered list with task name, custom ID, status, and assignees. Ask the user which one they meant.
3. Once a task is selected, use `mcp__clickup__clickup_get_task` with `detail_level: "detailed"`, `subtasks: true` to load full details.
4. In parallel, use `mcp__clickup__clickup_get_task_comments` with the task ID to load comments.
5. In parallel, use `mcp__clickup__clickup_search` with `keywords` set to the custom ID, filtered to `asset_types: ["attachment"]` to find attachments.
6. Display the task summary.

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

### Comments
{list of comments with author and date, or "No comments"}

### Attachments
{list of attachments with file name and URL if any, or "No attachments"}
```

## After displaying the task

Ask the user: **"Start time tracking on this task? If yes, which tag? (core / org / test)"**

- If the user confirms and picks a tag, use `mcp__clickup__clickup_start_time_tracking` with the task ID and `tags` set to the chosen tag (e.g., `["core"]`).
- If the user confirms without picking a tag, ask again — a tag is required.
- If no, do nothing.

## Rules

- Always show the ClickUp URL so the user can open the task in browser.
- If the task has a long description, show a concise summary (first ~500 chars) and mention it's truncated.
- If search returns no results, say so and suggest checking the ID/name.
- Do NOT modify the task in any way (except optionally starting time tracking when the user confirms).
- For comments, show the most recent 10 comments. If there are more, mention the total count.
- For attachments, show file name and URL for each. Note that attachment content (images, PDFs) cannot be displayed directly.
