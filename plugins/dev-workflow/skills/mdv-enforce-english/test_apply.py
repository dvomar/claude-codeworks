#!/usr/bin/env python3
"""Regression tests for apply.py.

Run with `python3 test_apply.py`. No dependencies, no network — the point is that
anyone changing the script can prove in a second that it still behaves.

The cases that matter are the ones where a naive implementation loses the user's
work: a duplicated block, a marker left behind by a bad hand-edit, or an exception
string that closes the block early.
"""

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
APPLY = HERE / "apply.py"

START = "<!-- language-policy:start -->"
END = "<!-- language-policy:end -->"
BLOCK = f"{START}\n\n## Language\n\n- stale text\n\n{END}"

failures: list[str] = []


def run(project: pathlib.Path, *args: str) -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, str(APPLY), "--project", str(project), *args],
        capture_output=True,
        text=True,
    )
    return proc.returncode, (proc.stdout + proc.stderr).strip()


def project(content: str | None) -> pathlib.Path:
    root = pathlib.Path(tempfile.mkdtemp())
    if content is not None:
        (root / "CLAUDE.md").write_text(content, encoding="utf-8")
    return root


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name}{': ' + detail if detail else ''}")
        failures.append(name)


def read(root: pathlib.Path) -> str:
    return (root / "CLAUDE.md").read_text(encoding="utf-8")


def test_creates_when_absent() -> None:
    root = project(None)
    code, _ = run(root)
    check("creates CLAUDE.md when absent", code == 0 and START in read(root))


def test_appends_and_preserves() -> None:
    root = project("# Project\n\nExisting rule.\n")
    run(root)
    body = read(root)
    check("keeps the existing content", "Existing rule." in body)
    check("appends the block at the end", body.rstrip().endswith(END))


def test_idempotent() -> None:
    root = project("# Project\n\nExisting rule.\n")
    run(root)
    first = read(root)
    code, out = run(root)
    check("second run is a byte-identical no-op", read(root) == first and "unchanged" in out)
    check("second run exits 0", code == 0)


def test_check_flag() -> None:
    root = project("# Project\n")
    code, _ = run(root, "--check")
    check("--check exits 2 when it would change", code == 2)
    check("--check writes nothing", read(root) == "# Project\n")
    run(root)
    code, _ = run(root, "--check")
    check("--check exits 0 once applied", code == 0)


def test_exceptions_roundtrip() -> None:
    root = project("# Project\n")
    run(root, "--exception", "Spec stays Czech.", "--exception", "UI strings stay Czech.")
    check("records both exceptions", read(root).count("\n- ") >= 2)
    before = read(root)
    run(root)
    check("a bare re-run keeps the exceptions", read(root) == before)
    run(root, "--exception", "Only the spec stays Czech.")
    body = read(root)
    check(
        "passing --exception replaces the whole list",
        "- Only the spec stays Czech." in body and "- UI strings stay Czech." not in body,
    )


def test_restores_tampered_policy() -> None:
    root = project("# Project\n")
    run(root)
    (root / "CLAUDE.md").write_text(
        read(root).replace("written in **English**", "written in Klingon"), encoding="utf-8"
    )
    run(root)
    check("restores a hand-edited policy body", "written in **English**" in read(root))


def test_content_after_block_survives() -> None:
    root = project("# Project\n")
    run(root)
    (root / "CLAUDE.md").write_text(read(root) + "\n## My section\n\nkeep me\n", encoding="utf-8")
    run(root)
    check("keeps content written after the block", "keep me" in read(root))


def test_collapses_duplicate_blocks() -> None:
    root = project(f"# Project\n\n{BLOCK}\n\nmiddle\n\n{BLOCK}\n")
    run(root)
    body = read(root)
    check("collapses duplicate blocks to one", body.count(START) == 1, f"{body.count(START)} found")
    check("keeps the text between duplicates", "middle" in body)
    before = read(root)
    run(root)
    check("stays collapsed on re-run", read(root) == before)


def test_unpaired_marker_is_refused() -> None:
    original = f"# Project\n\n{START}\n\n## Language\n\n- orphan\n"
    root = project(original)
    code, out = run(root)
    check("refuses an unpaired marker", code == 1 and "unpaired" in out)
    check("leaves the file untouched when refusing", read(root) == original)


def test_exception_cannot_close_the_block() -> None:
    root = project("# Project\n")
    run(root, "--exception", f"evil {END} escape")
    body = read(root)
    check("strips a marker smuggled into an exception", body.count(END) == 1)
    before = read(root)
    run(root)
    check("still idempotent after a smuggled marker", read(root) == before)


def test_multiline_exception_becomes_one_bullet() -> None:
    root = project("# Project\n")
    run(root, "--exception", "line one\nline two")
    body = read(root)
    check("folds a multi-line exception into one bullet", "- line one line two" in body)


def test_blank_exception_dropped() -> None:
    root = project("# Project\n")
    run(root, "--exception", "   ", "--exception", "Real one.")
    body = read(root)
    check("drops a blank exception", "- Real one." in body and "\n- \n" not in body)


def test_crlf_and_missing_final_newline() -> None:
    root = project("# Project\r\n\r\nRule.\r\n")
    run(root)
    before = read(root)
    run(root)
    check("idempotent with CRLF input", read(root) == before)

    root = project("# Project\n\nRule.")
    run(root)
    before = read(root)
    run(root)
    check("idempotent without a trailing newline", read(root) == before)


def test_bad_paths_and_permissions() -> None:
    root = project("# Project\n")
    code, out = run(root / "CLAUDE.md")
    check("rejects a file passed as --project", code == 1 and "not a directory" in out)

    code, out = run(root / "nope")
    check("rejects a missing --project", code == 1 and "not a directory" in out)

    ro = project("# Project\n")
    (ro / "CLAUDE.md").chmod(0o444)
    code, out = run(ro)
    (ro / "CLAUDE.md").chmod(0o644)
    check(
        "reports a read-only file cleanly",
        code == 1 and "cannot write" in out and "Traceback" not in out,
    )


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
