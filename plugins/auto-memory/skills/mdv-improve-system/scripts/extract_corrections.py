#!/usr/bin/env python3
"""
Extract candidate user corrections from Claude Code session transcripts.

Reads ~/.claude/projects/<project>/<session>.jsonl (stdlib only), keeps sessions
whose cwd lies inside the target project, and emits a compact Markdown report of
user messages that look like corrections, each with the assistant action that
preceded it.

The heuristics only narrow the haystack. The final judgement (real correction vs.
ordinary follow-up) is made by Claude when it reads the report.

Usage:
  extract_corrections.py [--project PATH | --all-projects] [--days N]
                         [--since-last-run] [--min-score N] [--out FILE]
                         [--mark-run] [--config-dir DIR]
"""

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
from pathlib import Path

SKILL_NAME = "mdv-improve-system"
SKILL_ALIASES = {SKILL_NAME, "improve-system"}
MAX_USER_CHARS = 700
MAX_ASSISTANT_CHARS = 280
MAX_REPORT_CHARS = 120_000

# --- Correction signals (Czech + English). Weight, regex. ----------------------
# Czech patterns cover both diacritic and ASCII spellings ("nedelej" / "nedělej").
SIGNALS = [
    (3, r"\b(nikdy|v[žz]dy(cky)?|never|always)\b"),
    (3, r"\b(zapamatuj|pamatuj|remember|from now on|p[řr][íi][šs]t[ěe]|odte[ďd])\b"),
    (3, r"\b(u[žz] (jsem )?(ti )?(to )?[řr]ikal|[řr]ikal jsem|[řr]ekl jsem|i (already )?(told|said)|as i said)\b"),
    (2, r"\b(zase|znovu|again|po[řr][áa]d|furt|still)\b"),
    (2, r"\b(nepou[žz][íi]vej|ned[ěe]lej|nep[íi][šs]|nem[ěe][ňn]|nesahej|nema[žz]|nevytv[áa][řr]ej|don'?t|do not|stop|quit)\b"),
    (2, r"\b([šs]patn[ěe]|chyba|chybn[ěe]|wrong|incorrect|broken|rozbil|nefunguje|doesn'?t work)\b"),
    (2, r"\b(m[íi]sto (toho)?|instead( of)?|rather than|rad[šs]i|preferuj|prefer)\b"),
    (2, r"\b(vra[tť]|revert|undo|rollback|zru[šs])\b"),
    (2, r"\b(pro[čc] (jsi|to)|why (did|are) you|who asked)\b"),
    (1, r"^\s*(ne|no|nope|ne ne|tohle ne|tak ne)\b[\s,.!]"),
    (1, r"\b(mus[íi][šs]|you (must|need to|should)|m[ěe]l bys|nem[ěe]l bys|shouldn'?t)\b"),
    (1, r"\b(nechci|i don'?t want|nechte?j)\b"),
]
SIGNAL_RES = [(w, re.compile(p, re.IGNORECASE)) for w, p in SIGNALS]

INTERRUPT_RE = re.compile(r"^\[Request interrupted by user", re.IGNORECASE)
REJECT_MARK = "doesn't want to proceed with this tool use"
REJECT_REASON_RE = re.compile(r"the user said:\s*(.+)", re.IGNORECASE | re.DOTALL)
SYS_REMINDER_RE = re.compile(r"<system-reminder>.*?</system-reminder>", re.DOTALL)
COMMAND_NAME_RE = re.compile(r"<command-name>\s*/?([\w:.-]+)\s*</command-name>")
NOISE_PREFIXES = (
    "<command-name>", "<command-message>", "<command-args>",
    "<local-command-stdout>", "<local-command-stderr>", "<bash-input>",
    "<bash-stdout>", "<bash-stderr>", "<user-memory-input>",
    "Caveat: The messages below were generated",
    "This session is being continued from a previous conversation",
)


def config_dir(arg):
    if arg:
        return Path(arg).expanduser()
    env = os.environ.get("CLAUDE_CONFIG_DIR")
    return Path(env).expanduser() if env else Path.home() / ".claude"


def project_root(path):
    try:
        out = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=5,
        )
        if out.returncode == 0 and out.stdout.strip():
            return Path(out.stdout.strip()).resolve()
    except Exception:
        pass
    return Path(path).resolve()


def inside(child, parent):
    try:
        Path(child).resolve().relative_to(parent)
        return True
    except Exception:
        return False


def iter_lines(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            for raw in fh:
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    yield json.loads(raw)
                except json.JSONDecodeError:
                    continue
    except OSError:
        return


def session_cwd(path):
    for i, rec in enumerate(iter_lines(path)):
        if isinstance(rec, dict) and rec.get("cwd"):
            return rec["cwd"]
        if i > 200:
            break
    return None


def blocks(message):
    content = (message or {}).get("content")
    if isinstance(content, str):
        return [{"type": "text", "text": content}]
    if isinstance(content, list):
        return [b for b in content if isinstance(b, dict)]
    return []


def tool_result_text(block):
    c = block.get("content")
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        return "\n".join(x.get("text", "") for x in c if isinstance(x, dict))
    return ""


def clean(text):
    text = SYS_REMINDER_RE.sub("", text or "")
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def clip(text, n):
    text = text.strip()
    return text if len(text) <= n else text[: n - 1].rstrip() + "…"


def score_text(text):
    score, hits = 0, []
    for w, rx in SIGNAL_RES:
        m = rx.search(text)
        if m:
            score += w
            hits.append(m.group(0).strip().lower())
    return score, hits


def describe_tool(block):
    name = block.get("name", "tool")
    inp = block.get("input") or {}
    target = inp.get("file_path") or inp.get("path") or inp.get("pattern") or inp.get("command") or ""
    target = str(target).replace("\n", " ")
    return f"{name}({clip(target, 70)})" if target else name


def parse_session(path):
    """Return (meta, candidates). Skips sessions that ran this skill."""
    meta = {"session": path.stem, "file": str(path), "branch": None, "start": None, "cwd": None}
    candidates = []
    last_assistant_text = ""
    last_tools = []
    pending_interrupt = False
    pending_rejects = []
    seen_human = 0

    for rec in iter_lines(path):
        if not isinstance(rec, dict):
            continue
        meta["cwd"] = meta["cwd"] or rec.get("cwd")
        meta["branch"] = meta["branch"] or rec.get("gitBranch")
        if rec.get("timestamp") and not meta["start"]:
            meta["start"] = rec["timestamp"]
        if rec.get("isSidechain") or rec.get("isMeta") or rec.get("isCompactSummary"):
            continue
        rtype = rec.get("type")
        msg = rec.get("message") or {}

        if rtype == "assistant":
            texts = [b.get("text", "") for b in blocks(msg) if b.get("type") == "text"]
            tools = [describe_tool(b) for b in blocks(msg) if b.get("type") == "tool_use"]
            if any(t.strip() for t in texts):
                last_assistant_text = " ".join(t.strip() for t in texts if t.strip())
                last_tools = []
            last_tools.extend(tools)
            last_tools = last_tools[-6:]
            continue

        if rtype != "user":
            continue

        human_parts = []
        for b in blocks(msg):
            bt = b.get("type")
            if bt == "tool_result":
                txt = tool_result_text(b)
                if REJECT_MARK in txt:
                    m = REJECT_REASON_RE.search(txt)
                    pending_rejects.append(clean(m.group(1)) if m else "")
            elif bt == "text":
                raw = b.get("text", "")
                cmd = COMMAND_NAME_RE.search(raw)
                if cmd and cmd.group(1).split(":")[-1] in SKILL_ALIASES:
                    return meta, None  # this session ran /improve-system itself
                t = clean(raw)
                if not t:
                    continue
                if INTERRUPT_RE.match(t):
                    pending_interrupt = True
                    continue
                if t.startswith(NOISE_PREFIXES):
                    continue
                human_parts.append(t)

        reasons = [r for r in pending_rejects if r]
        if not human_parts and not reasons:
            continue

        text = "\n".join(human_parts + reasons)
        seen_human += 1
        score, hits = score_text(text)
        flags = []
        if pending_interrupt:
            score += 3
            flags.append("interrupt")
        if pending_rejects:
            score += 4 if reasons else 2
            flags.append("rejected-tool" + (" with reason" if reasons else ""))
        if seen_human == 1:
            score -= 2  # first prompt is usually the task, not a correction
            flags.append("first-prompt")

        candidates.append({
            "ts": rec.get("timestamp") or "",
            "score": score,
            "flags": flags,
            "hits": hits,
            "user": clip(text, MAX_USER_CHARS),
            "before": clip(last_assistant_text, MAX_ASSISTANT_CHARS),
            "tools": list(last_tools),
        })
        pending_interrupt = False
        pending_rejects = []

    return meta, candidates


def load_state(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_state(path, state):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", default=os.getcwd(), help="project path (default: cwd, resolved to git root)")
    ap.add_argument("--all-projects", action="store_true", help="scan every project")
    ap.add_argument("--days", type=int, default=None, help="only sessions modified in the last N days")
    ap.add_argument("--since-last-run", action="store_true", help="only sessions newer than the last --mark-run")
    ap.add_argument("--min-score", type=int, default=2)
    ap.add_argument("--out", default=None, help="write report here (default: stdout)")
    ap.add_argument("--mark-run", action="store_true", help="record now as last run for this scope and exit")
    ap.add_argument("--config-dir", default=None, help="override ~/.claude")
    args = ap.parse_args()

    cfg = config_dir(args.config_dir)
    projects_dir = cfg / "projects"
    state_file = cfg / SKILL_NAME / "state.json"
    root = None if args.all_projects else project_root(args.project)
    scope_key = "*" if root is None else str(root)
    state = load_state(state_file)

    if args.mark_run:
        state[scope_key] = dt.datetime.now(dt.timezone.utc).isoformat()
        save_state(state_file, state)
        print(f"Marked last run for {scope_key}")
        return 0

    if not projects_dir.is_dir():
        print(f"No transcripts directory at {projects_dir}", file=sys.stderr)
        return 2

    cutoff = None
    if args.days:
        cutoff = dt.datetime.now().timestamp() - args.days * 86400
    if args.since_last_run and state.get(scope_key):
        try:
            last = dt.datetime.fromisoformat(state[scope_key]).timestamp()
            cutoff = max(cutoff or 0, last)
        except ValueError:
            pass

    files = []
    for p in projects_dir.glob("*/*.jsonl"):
        if cutoff and p.stat().st_mtime < cutoff:
            continue
        if root is not None:
            cwd = session_cwd(p)
            if not cwd or not inside(cwd, root):
                continue
        files.append(p)
    files.sort(key=lambda p: p.stat().st_mtime)

    sessions, skipped_self, total_human = [], 0, 0
    for p in files:
        meta, cands = parse_session(p)
        if cands is None:
            skipped_self += 1
            continue
        total_human += len(cands)
        keep = [c for c in cands if c["score"] >= args.min_score]
        if keep:
            sessions.append((meta, keep))

    n_cands = sum(len(c) for _, c in sessions)
    lines = [
        "# Correction candidates",
        "",
        f"- Scope: {'all projects' if root is None else root}",
        f"- Transcripts dir: {projects_dir}",
        f"- Sessions scanned: {len(files)} (skipped {skipped_self} that ran /{SKILL_NAME})",
        f"- Human messages seen: {total_human}; candidates with score >= {args.min_score}: {n_cands}",
        f"- Sessions with candidates: {len(sessions)}",
        f"- Filter: days={args.days} since_last_run={bool(args.since_last_run and state.get(scope_key))}",
        "",
        "Score guide: interrupt +3, rejected tool +2 (+4 with reason), correction phrases +1..+3, first prompt -2.",
        "Heuristics only. Decide yourself whether each item is a real, generalisable correction.",
        "",
    ]
    for meta, cands in sessions:
        lines.append(f"## Session {meta['session'][:8]}  {(meta['start'] or '')[:16]}  branch={meta['branch'] or '-'}")
        lines.append(f"cwd: {meta['cwd']}")
        lines.append("")
        for c in cands:
            tag = ", ".join(c["flags"] + [f"'{h}'" for h in c["hits"]])
            lines.append(f"### score {c['score']} | {c['ts'][:16]} | {tag}")
            if c["before"] or c["tools"]:
                tools = f" [tools: {'; '.join(c['tools'])}]" if c["tools"] else ""
                lines.append(f"> Claude before: {c['before'] or '(no text)'}{tools}")
            lines.append("User:")
            lines.append("```")
            lines.append(c["user"].replace("```", "'''"))
            lines.append("```")
            lines.append("")

    report = "\n".join(lines)
    if len(report) > MAX_REPORT_CHARS:
        report = report[:MAX_REPORT_CHARS] + "\n\n[TRUNCATED: raise --min-score or narrow --days]\n"

    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(report, encoding="utf-8")
        print(f"Wrote {args.out}: {len(files)} sessions, {n_cands} candidates, {len(report)} chars")
    else:
        print(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
