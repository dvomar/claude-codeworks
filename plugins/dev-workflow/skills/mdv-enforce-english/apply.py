#!/usr/bin/env python3
"""Install or refresh the language policy block in a project's CLAUDE.md.

The rewrite lives here rather than in the model so that it is deterministic and
idempotent: the same inputs always produce the same bytes, and a second run is a
no-op. The block is delimited by HTML comment markers, so everything a human wrote
around it survives untouched.

Run `test_apply.py` next to this file to check the behaviour after any change.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

START = "<!-- language-policy:start -->"
END = "<!-- language-policy:end -->"

HEADING = "## Language"
EXCEPTIONS_HEADING = "### Language exceptions"

BLOCK_RE = re.compile(re.escape(START) + r".*?" + re.escape(END), re.DOTALL)

POLICY = """\
- Code, comments, commit messages and Markdown files are written in **English** —
  identifiers, log messages, test names and documentation alike.
- Comments are short and specific, and exist only where the logic is not readable from
  the code itself. A comment says **why**; it never restates what the next line already
  says. Delete a comment rather than translate it if the code alone is clearer.
- User-facing product text is not code. UI strings, e-mail copy, and anything an end
  user reads stay in the product's own language, as do public URL segments, which
  cannot change without breaking shared links."""


class PolicyError(Exception):
    """A problem the human has to resolve; never raised for ordinary input."""


def clean_exception(raw: str) -> str:
    """One exception is one bullet, so it has to survive as a single line.

    Newlines would break the list and an embedded marker would truncate the block,
    so both are neutralised rather than trusted.
    """
    text = " ".join(raw.split())
    text = text.replace(START, "").replace(END, "")
    return " ".join(text.split())


def render(exceptions: list[str]) -> str:
    parts = [START, "", HEADING, "", POLICY]
    if exceptions:
        parts += ["", EXCEPTIONS_HEADING, ""]
        parts += [f"- {line}" for line in exceptions]
    parts += ["", END]
    return "\n".join(parts)


def existing_exceptions(block: str) -> list[str]:
    """Carry previously recorded exceptions over, so a bare re-run keeps them."""
    if EXCEPTIONS_HEADING not in block:
        return []
    tail = block.split(EXCEPTIONS_HEADING, 1)[1]
    out = []
    for raw in tail.splitlines():
        line = raw.strip()
        if line.startswith(END):
            break
        if line.startswith("- "):
            out.append(line[2:].strip())
    return out


def build(current: str, exceptions: list[str] | None) -> str:
    """Return the file content with exactly one policy block in it.

    A duplicated block is collapsed onto the first one. An unpaired marker is not
    guessed at: silently absorbing the text after a stray `start` would delete work,
    so it is reported instead.
    """
    matches = list(BLOCK_RE.finditer(current))
    outside = BLOCK_RE.sub("", current)
    if START in outside or END in outside:
        raise PolicyError(
            "found an unpaired language-policy marker. Remove the stray "
            f"'{START}' or '{END}' line by hand, then run this again."
        )

    kept = exceptions if exceptions is not None else (
        existing_exceptions(matches[0].group(0)) if matches else []
    )
    block = render(kept)

    if not matches:
        body = current.rstrip("\n")
        return (body + "\n\n" + block if body else block) + "\n"

    # Rebuild around the first block; drop the rest along with the blank lines that
    # only existed to separate them.
    out = current[: matches[0].start()] + block
    cursor = matches[0].end()
    for extra in matches[1:]:
        between = current[cursor : extra.start()]
        out += between if between.strip() else ""
        cursor = extra.end()
    out += current[cursor:]
    return out.rstrip("\n") + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--project", default=".", help="project root (default: cwd)")
    ap.add_argument(
        "--exception",
        action="append",
        dest="exceptions",
        help="project-specific exception; repeatable. Replaces the recorded list. "
        "Omit entirely to keep whatever is already there.",
    )
    ap.add_argument(
        "--check",
        action="store_true",
        help="exit 2 if CLAUDE.md would change, write nothing",
    )
    args = ap.parse_args()

    root = pathlib.Path(args.project)
    if not root.is_dir():
        print(f"ERROR: not a directory: {root}", file=sys.stderr)
        return 1
    target = root.resolve() / "CLAUDE.md"

    exceptions = None
    if args.exceptions is not None:
        exceptions = [c for c in (clean_exception(e) for e in args.exceptions) if c]

    try:
        current = target.read_text(encoding="utf-8") if target.exists() else ""
        updated = build(current, exceptions)
    except PolicyError as err:
        print(f"ERROR: {target}: {err}", file=sys.stderr)
        return 1
    except OSError as err:
        print(f"ERROR: cannot read {target}: {err}", file=sys.stderr)
        return 1
    except UnicodeDecodeError:
        print(f"ERROR: {target} is not valid UTF-8", file=sys.stderr)
        return 1

    if updated == current:
        print(f"unchanged: {target}")
        return 0
    if args.check:
        print(f"would change: {target}")
        return 2

    try:
        target.write_text(updated, encoding="utf-8")
    except OSError as err:
        print(f"ERROR: cannot write {target}: {err}", file=sys.stderr)
        return 1
    print(f"{'updated' if current else 'created'}: {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
