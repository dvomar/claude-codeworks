Create a new git branch from the current branch based on the task description provided as argument.

## Input

The argument `$ARGUMENTS` contains the task description (may be in Czech or English).

## Steps

1. Run `git branch --show-current` to get the current branch name.
2. Analyze the task description to determine:
   - **Branch type prefix**: `feat/` for new features, `fix/` for bug fixes, `refactor/` for refactoring, `docs/` for documentation, `test/` for test changes, `chore/` for maintenance tasks.
   - **Branch name**: Translate the task into a short, descriptive English kebab-case name (3-5 words max). Remove articles and filler words.
3. Construct the branch name as `{prefix}{kebab-case-name}` (e.g., `feat/add-user-export`, `fix/node-ordering-bug`).
4. Create the branch: `git checkout -b {branch-name}`
5. Confirm to the user: show the created branch name and the base branch it was created from.

## Rules

- Always translate Czech task descriptions to English for the branch name.
- Keep branch names concise — max 5 words after the prefix.
- Use only lowercase letters, numbers, and hyphens in the name part.
- Do NOT push the branch — only create it locally.
- If `$ARGUMENTS` is empty, ask the user for a task description.

## Examples

| Task description | Branch name |
|---|---|
| "přidat export uživatelů do CSV" | `feat/add-user-csv-export` |
| "opravit řazení specifikačních nodů" | `fix/specification-node-ordering` |
| "refaktorovat autentizační middleware" | `refactor/auth-middleware` |
| "přidat testy pro datagrid filtrování" | `test/datagrid-filtering` |
| "add bulk delete for network nodes" | `feat/bulk-delete-network-nodes` |
