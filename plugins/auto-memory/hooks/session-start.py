#!/usr/bin/env python3
"""SessionStart hook: put the session's starting conditions into context.

Matcher: startup (NOT resume, NOT clear)
Reason: avoid noise on /clear (same project) or /resume (continuing work).

A SessionStart hook may return additionalContext on stdout, which Claude Code
injects into the session. That is worth far more than a stderr warning the agent
reads as noise: the three facts below are ones it would otherwise have to spend a
tool call discovering, or worse, assume.

Stays silent when there is nothing worth saying. This text costs tokens on every
single session, so it earns its place or it does not appear.
"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib import hooks_disabled, read_payload, project_dir, project_data_dir

LOUD_THRESHOLD = 10
KNOWLEDGE_FILES = ("tech-stack.md", "architecture.md", "backend.md", "frontend.md", "conventions.md")


def git(args: list[str], cwd: Path) -> str:
    try:
        out = subprocess.run(
            ["git", *args], cwd=cwd, capture_output=True, text=True, timeout=2
        )
        return out.stdout.strip() if out.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def knowledge_line(data_dir: Path) -> str:
    """Whether the agents have conventions to work from, or are flying blind."""
    kdir = data_dir / "knowledge"
    if not kdir.is_dir():
        return "- `.claude/knowledge/` does not exist — agents have no generated conventions. Run `/mdv-code-analyze-codebase` before any non-trivial change."
    present = [f for f in KNOWLEDGE_FILES if (kdir / f).is_file() and (kdir / f).stat().st_size > 0]
    if not present:
        return "- `.claude/knowledge/` is empty — agents have no generated conventions. Run `/mdv-code-analyze-codebase` before any non-trivial change."
    if len(present) < len(KNOWLEDGE_FILES):
        missing = ", ".join(f for f in KNOWLEDGE_FILES if f not in present)
        return f"- `.claude/knowledge/` has {len(present)}/{len(KNOWLEDGE_FILES)} files; missing: {missing}."
    return ""  # complete and healthy: nothing to say


def dirty_line(data_dir: Path) -> str:
    dirty_file = data_dir / ".knowledge-dirty.txt"
    if not dirty_file.is_file():
        return ""
    n = sum(1 for line in dirty_file.read_text(encoding="utf-8").splitlines() if line.strip())
    if n > LOUD_THRESHOLD:
        return f"- {n} source files changed since the last knowledge update — `/mdv-code-analyze-codebase` for a full refresh."
    if n:
        return f"- {n} source files pending a knowledge update — `/mdv-wrap-session` picks them up."
    return ""


def git_line(project: Path) -> str:
    branch = git(["branch", "--show-current"], project)
    if not branch:
        return ""
    porcelain = git(["status", "--porcelain"], project)
    changed = len([line for line in porcelain.splitlines() if line.strip()])
    if changed:
        return f"- Branch `{branch}`, {changed} uncommitted file(s) already in the working tree."
    return f"- Branch `{branch}`, working tree clean."


def main() -> int:
    if hooks_disabled():
        return 0

    payload = read_payload()
    project = project_dir(payload)
    data_dir = project_data_dir(payload)

    lines = [ln for ln in (knowledge_line(data_dir), dirty_line(data_dir), git_line(project)) if ln]
    if not lines:
        return 0

    context = "Session start state for this project:\n" + "\n".join(lines)
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context,
        }
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
