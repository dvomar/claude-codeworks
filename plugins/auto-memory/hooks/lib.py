"""Shared helpers for Claude Code hooks.

All hooks check CLAUDE_HOOKS_DISABLED env var first to prevent recursive
firing when a hook spawns a subagent via `claude -p`.
"""
import json
import os
import sys
from pathlib import Path


def hooks_disabled() -> bool:
    """Bail out if hooks are disabled (set when spawning subagents)."""
    return bool(os.environ.get("CLAUDE_HOOKS_DISABLED"))


def read_payload() -> dict:
    """Hooks receive JSON payload on stdin."""
    try:
        return json.loads(sys.stdin.read() or "{}")
    except Exception:
        return {}


def project_dir(payload: dict) -> Path:
    """Resolve project root from payload or env."""
    cwd = payload.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    return Path(cwd)


def project_data_dir(payload: dict) -> Path:
    """Returns <project>/.claude/, ensuring it exists."""
    d = project_dir(payload) / ".claude"
    d.mkdir(parents=True, exist_ok=True)
    return d


def memory_dir_for(project: Path) -> Path:
    """Maps a project path to its global auto-memory dir.

    Mirrors Claude Code's encoding: absolute path with '/' replaced by '-'.
    Example: /Users/mw/foo -> ~/.claude/projects/-Users-mw-foo/memory
    """
    encoded = str(project.resolve()).replace("/", "-")
    return Path.home() / ".claude" / "projects" / encoded / "memory"


def log_stderr(msg: str) -> None:
    """Print to stderr; visible in Claude Code's hook output."""
    print(f"[hook] {msg}", file=sys.stderr, flush=True)


def append_jsonl(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
