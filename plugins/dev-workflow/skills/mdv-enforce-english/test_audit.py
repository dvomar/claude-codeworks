#!/usr/bin/env python3
"""Regression tests for audit.py.

Run with `python3 test_audit.py`. The cases below are the ones that made earlier
versions of the script useless in opposite directions: missing accent-free foreign
text, and burying real findings under English that merely quotes a foreign label.
"""

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
AUDIT = HERE / "audit.py"

failures: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name}{': ' + detail if detail else ''}")
        failures.append(name)


def repo(files: dict[str, str], commit_subject: str = "Add initial files") -> pathlib.Path:
    root = pathlib.Path(tempfile.mkdtemp())
    for name, content in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    subprocess.run(["git", "-C", str(root), "init", "-q"], check=True)
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
    subprocess.run(
        ["git", "-C", str(root), "-c", "user.email=t@t", "-c", "user.name=t",
         "commit", "-q", "-m", commit_subject],
        check=True,
    )
    return root


def audit(root: pathlib.Path, *args: str) -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, str(AUDIT), "--project", str(root), *args],
        capture_output=True,
        text=True,
    )
    return proc.returncode, proc.stdout + proc.stderr


def test_finds_accented_comment() -> None:
    root = repo({"src/a.ts": "// Zaokrouhlení podle zákona o DPH.\nexport const a = 1;\n"})
    _, out = audit(root)
    check("finds an accented comment", "Zaokrouhlení" in out)


def test_finds_accent_free_commit_subject() -> None:
    root = repo({"a.txt": "x\n"}, commit_subject="Prvni verze fakturace")
    _, out = audit(root)
    check(
        "finds an accent-free foreign commit subject",
        "Prvni verze fakturace" in out,
        "this is the case a diacritics grep cannot see",
    )


def test_english_commit_subjects_pass() -> None:
    for subject in ("Fix login bug", "Add user authentication", "Initial commit",
                    "Update dependencies", "Refactor group settings"):
        root = repo({"a.txt": "x\n"}, commit_subject=subject)
        _, out = audit(root)
        check(f"English subject not flagged: {subject!r}", subject not in out)


def test_terse_english_comment_passes() -> None:
    root = repo({"src/a.ts": "/** Group management: members, invite, usual slot. */\n"})
    _, out = audit(root)
    check("terse English JSDoc not flagged", "Group management" not in out)


def test_quoted_foreign_label_passes() -> None:
    root = repo({"src/a.ts": '// Cancelled or played: only "Vypsat stejný zápas"\n'})
    _, out = audit(root)
    check("English comment quoting a foreign label not flagged", "Vypsat" not in out)


def test_glob_is_not_a_comment() -> None:
    root = repo({"vitest.config.ts": 'export default { include: ["tests/**/*.test.ts"] };\n'})
    _, out = audit(root)
    check("a glob containing /* is not read as a comment", "include:" not in out)


def test_strings_skipped_by_default() -> None:
    files = {
        "src/a.ts": 'const L = { draft: "Koncept" };\n'
        'console.log("Uzivatel nebyl nalezen v databazi");\n'
    }
    root = repo(files)
    _, out = audit(root)
    check("string literals skipped by default", "Uzivatel" not in out)
    _, out = audit(root, "--strings")
    check("--strings surfaces a foreign log message", "Uzivatel" in out)
    check(
        "a one-word UI label stays unflagged even with --strings",
        "Koncept" not in out,
        "single words cannot be judged without a dictionary, and most are UI labels",
    )


def test_exclude_and_strict() -> None:
    root = repo({"docs/spec.md": "Toto je specifikace v cizim jazyce.\n"})
    _, out = audit(root, "--exclude", "docs/")
    check("--exclude drops a whole directory", "No suspect" in out)
    code, _ = audit(root, "--strict")
    check("--strict exits 3 on findings", code == 3)
    code, _ = audit(root, "--exclude", "docs/", "--strict")
    check("--strict exits 0 when clean", code == 0)


def test_bad_project_path() -> None:
    code, out = audit(pathlib.Path("/definitely/not/here"))
    check("rejects a missing --project", code == 1 and "not a directory" in out)


def main() -> int:
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            print(name[5:].replace("_", " "))
            fn()
    print()
    if failures:
        print(f"{len(failures)} FAILED: {', '.join(failures)}")
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
