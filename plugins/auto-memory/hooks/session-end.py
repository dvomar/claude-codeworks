#!/usr/bin/env python3
"""SessionEnd hook: aggregate token usage and append a session summary.

Matcher: clear|prompt_input_exit

Note: memory proposing and knowledge updates are NOT done here. Spawning
headless `claude -p` subagents on every exit cost a separate API session,
ran on trivial sessions, and was auto-denied on `.claude/` writes in
non-interactive mode. That work now lives in the `/wrap-session` skill, run
manually in the live session (full context, no extra session, writes work).
"""
import json
import sys
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


def aggregate_transcript(transcript_path: Path) -> dict:
    """Sum tokens from all assistant messages in the transcript."""
    totals = {
        "input": 0, "output": 0,
        "cache_read": 0, "cache_creation": 0,
        "turns": 0, "models": {},
    }
    if not transcript_path.is_file():
        return totals
    with transcript_path.open() as f:
        for line in f:
            try:
                row = json.loads(line)
            except Exception:
                continue
            if row.get("type") != "assistant":
                continue
            msg = row.get("message", {}) or {}
            usage = msg.get("usage", {}) or {}
            model = msg.get("model", "unknown")
            totals["turns"] += 1
            totals["input"] += usage.get("input_tokens", 0) or 0
            totals["output"] += usage.get("output_tokens", 0) or 0
            totals["cache_read"] += usage.get("cache_read_input_tokens", 0) or 0
            totals["cache_creation"] += usage.get("cache_creation_input_tokens", 0) or 0
            totals["models"][model] = totals["models"].get(model, 0) + 1
    return totals


def write_session_summary(data_dir: Path, payload: dict, totals: dict) -> Path:
    summary = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "reason": payload.get("reason"),
        "session_id": payload.get("session_id"),
        "tokens": totals,
    }
    path = data_dir / ".session-summary.jsonl"
    append_jsonl(path, summary)
    return path


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
    tp = payload.get("transcript_path") or ""
    transcript: Path | None = Path(tp) if tp else None
    data_dir = project_data_dir(payload)

    totals = aggregate_transcript(transcript) if transcript else {
        "input": 0, "output": 0, "cache_read": 0, "cache_creation": 0,
        "turns": 0, "models": {},
    }
    write_session_summary(data_dir, payload, totals)

    reason = payload.get("reason", "?")
    log_stderr(
        f"session-end ({reason}): {totals['turns']} turns | "
        f"in={totals['input']} out={totals['output']} "
        f"cache_read={totals['cache_read']} cache_create={totals['cache_creation']}"
    )
    pending = dirty_file_count(data_dir)
    if pending:
        log_stderr(f"{pending} files pending knowledge update — run /wrap-session before clearing to capture them")
    return 0


if __name__ == "__main__":
    sys.exit(main())
