#!/usr/bin/env python3
"""SessionEnd hook: append the session's tokens and cost to .session-summary.jsonl.

Matcher: every reason — a session ended by closing the terminal costs as much as one
ended by /exit.

The numbers are Claude Code's own `cost-state` transcript row, not a sum of the
per-message usage: that one misses subagents and Claude Code's internal calls. On
/clear the row is written only after this hook returns, so the hook hands the
payload to a detached copy of itself that waits for it. See README → Hooky.

Note: memory proposing and knowledge updates are NOT done here. Spawning
headless `claude -p` subagents on every exit cost a separate API session,
ran on trivial sessions, and was auto-denied on `.claude/` writes in
non-interactive mode. That work now lives in the `/mdv-wrap-session` skill, run
manually in the live session (full context, no extra session, writes work).
"""
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib import (
    hooks_disabled,
    read_payload,
    project_data_dir,
    log_stderr,
    append_jsonl,
)

WAIT_FOR_COST_STATE_SECONDS = 30
TOKEN_FIELDS = {
    "input": "inputTokens",
    "output": "outputTokens",
    "cache_read": "cacheReadInputTokens",
    "cache_creation": "cacheCreationInputTokens",
}


def read_transcript(transcript_path: Path) -> list[dict]:
    rows = []
    with transcript_path.open() as f:
        for line in f:
            try:
                rows.append(json.loads(line))
            except Exception:
                continue
    return rows


def count_api_calls(rows: list[dict]) -> int:
    """Main-thread API calls; Claude Code writes one row per content block, so each message id counts once."""
    return len({
        row["message"]["id"]
        for row in rows
        if row.get("type") == "assistant"
        and (row.get("message") or {}).get("id")
        and row["message"].get("model") != "<synthetic>"
    })


def final_cost_state(rows: list[dict]) -> dict | None:
    """The cost-state row written after the last assistant message; None until Claude Code writes it."""
    state = None
    for row in rows:
        if row.get("type") == "assistant":
            state = None
        elif row.get("type") == "cost-state":
            state = row
    return state


def usage_by_model(cost_state: dict) -> dict:
    return {
        model: {
            **{key: usage.get(field, 0) or 0 for key, field in TOKEN_FIELDS.items()},
            "cost_usd": usage.get("costUSD", 0.0) or 0.0,
        }
        for model, usage in (cost_state.get("modelUsage") or {}).items()
    }


def start_detached_copy(payload: dict) -> None:
    """Run the recording in a copy of this hook that outlives Claude Code's wait on the hook."""
    child = subprocess.Popen(
        [sys.executable, __file__, "--record"],
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    child.stdin.write(json.dumps(payload).encode())
    child.stdin.close()


def record_session(payload: dict) -> None:
    transcript = Path(payload.get("transcript_path") or "")
    if not transcript.is_file():
        return
    rows = read_transcript(transcript)
    api_calls = count_api_calls(rows)
    if not api_calls:
        return
    cost_state = final_cost_state(rows)
    deadline = time.monotonic() + WAIT_FOR_COST_STATE_SECONDS
    while cost_state is None and time.monotonic() < deadline:
        time.sleep(0.5)
        rows = read_transcript(transcript)
        cost_state = final_cost_state(rows)

    append_jsonl(project_data_dir(payload) / ".session-summary.jsonl", {
        "ts": datetime.now(timezone.utc).isoformat(),
        "reason": payload.get("reason"),
        "session_id": payload.get("session_id"),
        "turns": api_calls,
        "cost_source": "claude-code" if cost_state else "missing",
        "cost_usd": cost_state.get("totalCostUSD", 0.0) if cost_state else 0.0,
        "models": usage_by_model(cost_state) if cost_state else {},
    })


def dirty_file_count(data_dir: Path) -> int:
    """How many source files are pending a knowledge update."""
    dirty_file = data_dir / ".knowledge-dirty.txt"
    if not dirty_file.exists():
        return 0
    return len([l for l in dirty_file.read_text().splitlines() if l.strip()])


def main() -> int:
    if hooks_disabled():
        return 0
    payload = read_payload()
    if "--record" in sys.argv:
        record_session(payload)
        return 0

    start_detached_copy(payload)
    pending = dirty_file_count(project_data_dir(payload))
    if pending:
        log_stderr(f"{pending} files pending knowledge update — run /mdv-wrap-session before clearing to capture them")
    return 0


if __name__ == "__main__":
    sys.exit(main())
