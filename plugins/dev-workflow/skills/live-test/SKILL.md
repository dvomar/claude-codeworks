---
name: live-test
description: Test newly implemented features or fixes against local Docker containers. Rebuilds services if needed.
---

# Live Test

Tests recently implemented features or fixes against locally running Docker containers. Rebuilds stale services, designs test scenarios, and executes them with proper authentication.

## Process

Follow these steps in order:

### 1. Understand the project setup

Read `CLAUDE.md` to get Docker configuration, ports, service tokens, API paths, and authentication requirements.

### 2. Identify what to test

Analyze recent changes to understand what was implemented:

```bash
git diff
git diff --staged
git log --oneline -3
```

Read the changed source files to understand the feature or fix being tested.

### 3. Check Docker state

```bash
docker compose ps
```

If infrastructure services (database, cache, message broker) are not running, start them first:

```bash
docker compose up -d
```

### 4. Ensure current code is deployed

Compare container state with local changes:
- Check if the affected service container is running
- If local source files are newer than the container build, or if the container is not running, rebuild:

```bash
docker compose build <service> --no-cache
docker compose up -d <service> --force-recreate --no-deps
```

Wait for service startup by checking logs or polling the health endpoint:

```bash
docker compose logs --tail=50 <service>
curl -s http://localhost:<port>/health
```

### 5. Map changes to services

Determine which service(s) to test based on changed files. Read `docker-compose.yml` (or equivalent) to understand the mapping between source code directories and services.

### 6. Design test scenarios

Based on the changes, create test scenarios covering:

- **Happy path** — main functionality works as expected
- **Edge cases** — empty data, non-existent IDs, boundary conditions
- **Data integrity** — existing data is unaffected
- **Error handling** — proper error responses for invalid input

### 7. Execute tests

Run curl commands with proper authentication (get auth details from project config):

```bash
curl -s -w "\nHTTP Status: %{http_code}\n" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  "http://localhost:<port>/api/<path>"
```

Verify:
- HTTP status codes match expectations
- Response bodies contain expected data
- Error responses have proper structure

### 8. Check database state (when relevant)

For data-modifying operations, verify database consistency by querying the database container directly.

### 9. Report results

Display a summary table of all test scenarios:

| # | Scenario | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | ... | 200 OK | 200 OK | PASS |
| 2 | ... | 404 Not Found | 404 Not Found | PASS |

Include any notable observations, warnings, or follow-up recommendations.

## Rules

- Always use `--no-cache` when rebuilding Docker images to ensure fresh code.
- Wait for service health before running tests.
- Get authentication details from project configuration, not hardcoded values.
- Test against `localhost` with mapped ports from Docker Compose.
- If infrastructure services are not running, start them before proceeding.
- Never modify production data or configuration.
