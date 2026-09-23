#!/usr/bin/env python3
"""Report developer-facing text in a repository that does not look like English.

Collecting the candidates is deterministic work, so it belongs in a script; deciding
whether a hit is a real violation or legitimate product text is judgement, so the
script never rewrites anything and never claims certainty.

Two signals, because either alone is too weak:

- **Non-ASCII letters.** Precise but blind — plenty of languages are written with
  bare ASCII, and a grep for diacritics gives a diacritics-free repository a clean
  bill of health it has not earned.
- **No English function words.** A run of four or more words containing none of
  `the`, `is`, `to`, `and`, `for`, `not`, … is very unlikely to be English prose.
  This is what catches "Prvni verze fakturace" or "Koncept".

Only comments, Markdown prose and commit subjects are scanned. String literals are
skipped by default because in most products they are user-facing text that the policy
deliberately protects; pass --strings when you suspect developer-facing log messages.

Known limit: a single word cannot be judged without a dictionary, so short accent-free
text ("Koncept") passes. That is usually the right call — one-word strings are nearly
always UI labels the policy protects anyway — but it means this is a net, not a proof.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys
import unicodedata

# Function words carry grammar rather than content, so they appear in almost any real
# English sentence and almost never survive translation.
ENGLISH_FUNCTION_WORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being", "to", "of",
    "in", "on", "at", "by", "for", "from", "with", "without", "and", "or", "but",
    "not", "no", "if", "then", "else", "when", "while", "so", "that", "this", "these",
    "those", "it", "its", "we", "you", "they", "he", "she", "as", "into", "over",
    "under", "than", "because", "which", "what", "who", "how", "why", "do", "does",
    "did", "can", "cannot", "could", "should", "would", "will", "must", "may",
    "has", "have", "had", "there", "here", "only", "also", "just", "still", "yet",
    "any", "all", "each", "every", "both", "same", "other", "per", "via", "up", "out",
}

# Commit subjects and short comments are usually imperative and carry no function
# words at all ("Fix login bug"), so they need a content vocabulary as well. These are
# the verbs and nouns that dominate English commit messages and code comments.
ENGLISH_COMMON = ENGLISH_FUNCTION_WORDS | {
    "add", "added", "allow", "apply", "avoid", "bump", "build", "cache", "call",
    "change", "check", "clean", "cleanup", "close", "config", "convert", "copy",
    "create", "delete", "deploy", "disable", "document", "drop", "enable", "ensure",
    "expose", "extract", "fail", "fix", "fixes", "handle", "hide", "implement",
    "improve", "init", "inline", "introduce", "keep", "let", "load", "log", "make",
    "merge", "migrate", "move", "note", "open", "parse", "pass", "prevent", "read",
    "refactor", "release", "remove", "rename", "render", "replace", "report", "reset",
    "return", "revert", "run", "save", "send", "set", "show", "skip", "split",
    "store", "support", "switch", "sync", "test", "tests", "update", "upgrade", "use",
    "using", "validate", "wire", "write", "bug", "error", "issue", "version", "value",
    "file", "files", "code", "data", "name", "list", "state", "user", "users", "page",
    "link", "links", "field", "flag", "order", "count", "group", "groups", "match",
    "time", "date", "text", "first", "last", "new", "old", "before", "after",
    "initial", "commit", "branch", "wip", "chore", "feat", "docs", "perf", "style",
    "ci", "api", "ui", "member", "members", "invite", "switch", "switching", "leave",
    "leaving", "usual", "slot", "management", "screen", "button", "label", "row",
    "list", "sheet", "modal", "dialog", "header", "footer", "session", "token",
    "cookie", "server", "client", "request", "response", "query", "column", "table",
    "index", "schema", "default", "defaults", "helper", "helpers", "fixture",
}

LINE_COMMENT = {
    ".ts": "//", ".tsx": "//", ".js": "//", ".jsx": "//", ".mjs": "//", ".cjs": "//",
    ".java": "//", ".c": "//", ".h": "//", ".cpp": "//", ".cs": "//", ".go": "//",
    ".rs": "//", ".swift": "//", ".kt": "//", ".scala": "//", ".php": "//",
    ".prisma": "//", ".dart": "//",
    ".py": "#", ".sh": "#", ".bash": "#", ".zsh": "#", ".rb": "#", ".yml": "#",
    ".yaml": "#", ".toml": "#", ".conf": "#", ".tf": "#", ".dockerfile": "#",
    ".sql": "--", ".lua": "--",
}
BLOCK_COMMENT = {
    ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".java", ".c", ".h", ".cpp", ".cs",
    ".go", ".rs", ".swift", ".kt", ".scala", ".php", ".css", ".scss", ".less",
    ".prisma", ".dart",
}
NAMED_AS_COMMENT_HASH = {"Dockerfile", "Makefile", ".env.example", ".gitignore"}

WORD_RE = re.compile(r"[^\W\d_]+", re.UNICODE)
BLOCK_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)


def has_non_ascii_letter(text: str) -> bool:
    return any(ord(ch) > 127 and unicodedata.category(ch).startswith("L") for ch in text)


QUOTED_RE = re.compile(r"""(["'`„“»])(?:(?!\1).){1,80}?["'`“”«]""")


def looks_non_english(
    text: str, min_words: int, vocabulary: set[str] = ENGLISH_COMMON
) -> str | None:
    """Return the reason this text looks non-English, or None if it looks fine.

    Quoted spans are dropped first: an English comment that names a Czech button by
    quoting it is exactly what the policy asks for, and flagging it every time would
    bury the real violations.
    """
    text = QUOTED_RE.sub(" ", text)
    if has_non_ascii_letter(text):
        return "non-ASCII letters"
    words = [w.lower() for w in WORD_RE.findall(text)]
    if len(words) < min_words:
        return None
    if any(w in vocabulary for w in words):
        return None
    return "no recognisable English words"


def comment_prefix(path: pathlib.Path) -> str | None:
    if path.name in NAMED_AS_COMMENT_HASH:
        return "#"
    return LINE_COMMENT.get(path.suffix.lower())


def strip_strings(line: str) -> str:
    """Blank out quoted text so a Czech UI label does not read as a Czech comment."""
    return re.sub(r"""(["'`])(?:\\.|(?!\1).)*\1""", '""', line)


def scan_markdown(text: str) -> list[tuple[int, str]]:
    out, fenced = [], False
    for i, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if line.startswith("```") or line.startswith("~~~"):
            fenced = not fenced
            continue
        if fenced or not line or line.startswith(("|", ">", "<!--")):
            continue
        prose = re.sub(r"`[^`]*`|\[[^\]]*\]\([^)]*\)|https?://\S+", " ", line)
        prose = re.sub(r"^[#>\-*+\d.\s]+", "", prose)
        if prose.strip():
            out.append((i, prose.strip()))
    return out


def scan_source(text: str, prefix: str | None, blocks: bool) -> list[tuple[int, str]]:
    """Pull comments out line by line, tracking block state.

    Strings are blanked before the scan because a glob like "**/*.test.ts" or a URL
    contains the very sequences that open a comment.
    """
    out: list[tuple[int, str]] = []
    in_block = False
    for i, raw in enumerate(text.splitlines(), 1):
        if in_block:
            end = raw.find("*/")
            body = (raw if end == -1 else raw[:end]).strip().lstrip("*").strip()
            if body:
                out.append((i, body))
            in_block = end == -1
            continue

        code = strip_strings(raw)
        line_at = code.find(prefix) if prefix else -1
        block_at = code.find("/*") if blocks else -1

        if block_at != -1 and (line_at == -1 or block_at < line_at):
            end = code.find("*/", block_at + 2)
            body = (code[block_at + 2 :] if end == -1 else code[block_at + 2 : end]).strip()
            if body.strip("*").strip():
                out.append((i, body.strip("*").strip()))
            in_block = end == -1
        elif line_at != -1:
            body = raw[line_at + len(prefix) :].strip() if prefix else ""
            if body:
                out.append((i, body))
    return out


def repo_files(root: pathlib.Path, include_untracked: bool) -> list[pathlib.Path]:
    cmd = ["git", "-C", str(root), "ls-files"]
    if include_untracked:
        cmd += ["--others", "--exclude-standard", "--cached"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        return sorted(p for p in root.rglob("*") if p.is_file())
    return [root / line for line in res.stdout.splitlines() if line]


def commit_subjects(root: pathlib.Path, limit: int) -> list[tuple[str, str]]:
    res = subprocess.run(
        ["git", "-C", str(root), "log", f"-{limit}", "--format=%h%x00%s"],
        capture_output=True,
        text=True,
    )
    if res.returncode != 0:
        return []
    out = []
    for line in res.stdout.splitlines():
        if "\0" in line:
            sha, subject = line.split("\0", 1)
            out.append((sha, subject))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--project", default=".", help="repository root (default: cwd)")
    ap.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="path prefix to skip, repeatable (e.g. docs/ for a foreign-language spec)",
    )
    ap.add_argument("--commits", type=int, default=50, help="commit subjects to check")
    ap.add_argument(
        "--strings",
        action="store_true",
        help="also scan quoted strings; noisy, since most are user-facing on purpose",
    )
    ap.add_argument(
        "--min-words",
        type=int,
        default=4,
        help="shortest run of words judged by the function-word test (default: 4)",
    )
    ap.add_argument("--strict", action="store_true", help="exit 3 when anything is found")
    args = ap.parse_args()

    root = pathlib.Path(args.project)
    if not root.is_dir():
        print(f"ERROR: not a directory: {root}", file=sys.stderr)
        return 1
    root = root.resolve()

    findings: list[tuple[str, int, str, str]] = []
    for path in repo_files(root, include_untracked=True):
        try:
            rel = path.relative_to(root).as_posix()
        except ValueError:
            continue
        if any(rel.startswith(x) for x in args.exclude) or not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        suffix = path.suffix.lower()
        if suffix in {".md", ".markdown"}:
            chunks = scan_markdown(text)
        elif suffix in {".html", ".htm", ".vue", ".svelte"}:
            chunks = [
                (text[: m.start()].count("\n") + 1, m.group(0)[4:-3].strip())
                for m in HTML_COMMENT_RE.finditer(text)
            ]
        else:
            prefix = comment_prefix(path)
            if prefix is None and suffix not in BLOCK_COMMENT:
                continue
            chunks = scan_source(text, prefix, suffix in BLOCK_COMMENT)

        if args.strings:
            for i, raw in enumerate(text.splitlines(), 1):
                for m in re.finditer(r"""(["'`])((?:\\.|(?!\1).){4,})\1""", raw):
                    chunks.append((i, m.group(2)))

        for line_no, chunk in chunks:
            reason = looks_non_english(chunk, args.min_words)
            if reason:
                findings.append((rel, line_no, chunk[:110], reason))

    bad_commits = [
        (sha, subject, reason)
        for sha, subject in commit_subjects(root, args.commits)
        # Subjects are short, so they get the wider vocabulary and a lower threshold.
        if (reason := looks_non_english(subject, 2, ENGLISH_COMMON))
    ]

    if findings:
        print(f"Suspect text in {len({f[0] for f in findings})} file(s):\n")
        current = None
        for rel, line_no, chunk, reason in findings:
            if rel != current:
                print(f"  {rel}")
                current = rel
            print(f"    {line_no}: {chunk}   [{reason}]")
        print()
    if bad_commits:
        print(f"Suspect commit subjects ({len(bad_commits)}):\n")
        for sha, subject, reason in bad_commits:
            print(f"  {sha} {subject}   [{reason}]")
        print()

    total = len(findings) + len(bad_commits)
    if total == 0:
        print("No suspect developer-facing text found.")
        return 0

    print(
        f"{total} candidate(s). These are candidates, not verdicts — classify each one:\n"
        "  violation  = comment, test name, commit subject, Markdown prose\n"
        "  legitimate = user-visible string, route segment, seed data, or a recorded exception\n"
        "Nothing was modified."
    )
    return 3 if args.strict else 0


if __name__ == "__main__":
    sys.exit(main())
