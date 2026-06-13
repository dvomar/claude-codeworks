#!/usr/bin/env python3
"""SessionStart hook: warn if knowledge is stale (>10 dirty files).

Matcher: startup (NOT resume, NOT clear)
Reason: avoid noise on /clear (same project) or /resume (continuing work).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib import hooks_disabled, read_payload, project_data_dir, log_stderr


LOUD_THRESHOLD = 10


def main() -> int:
    if hooks_disabled():
        return 0

    payload = read_payload()
    data_dir = project_data_dir(payload)
    dirty_file = data_dir / ".knowledge-dirty.txt"
    if not dirty_file.exists():
        return 0

    n = sum(1 for l in dirty_file.read_text().splitlines() if l.strip())
    if n > LOUD_THRESHOLD:
        log_stderr(
            f"knowledge stale: {n} files changed since last update — "
            f"run /code-analyze-codebase for full refresh"
        )
    # 1-10 dirty files: knowledge-updater handled it on previous SessionEnd, stay quiet
    return 0


if __name__ == "__main__":
    sys.exit(main())
