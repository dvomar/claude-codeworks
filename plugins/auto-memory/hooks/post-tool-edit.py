#!/usr/bin/env python3
"""PostToolUse hook: track source files changed since last knowledge update.

Matcher: Edit|Write|MultiEdit
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib import hooks_disabled, read_payload, project_data_dir


SOURCE_EXTS = {
    ".cs", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs",
    ".py", ".go", ".rb", ".java", ".kt", ".rs", ".php",
    ".vue", ".svelte",
}


def is_source(p: Path) -> bool:
    if p.suffix not in SOURCE_EXTS:
        return False
    parts = set(p.parts)
    skip = {"node_modules", ".git", "bin", "obj", "dist", "build",
            "__pycache__", ".next", ".venv", "vendor", "coverage"}
    return not (parts & skip)


def main() -> int:
    if hooks_disabled():
        return 0

    payload = read_payload()
    tool_input = payload.get("tool_input", {}) or {}
    file_path = tool_input.get("file_path") or tool_input.get("path")
    if not file_path:
        return 0

    p = Path(file_path)
    if not is_source(p):
        return 0

    # Always store absolute, resolved paths so reruns dedup correctly
    # (resolve() works even for files that don't exist yet)
    abs_path = str(p.resolve())

    data_dir = project_data_dir(payload)
    dirty_file = data_dir / ".knowledge-dirty.txt"

    existing = set()
    if dirty_file.exists():
        existing = {l for l in dirty_file.read_text().splitlines() if l.strip()}
    existing.add(abs_path)
    dirty_file.write_text("\n".join(sorted(existing)) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
