#!/usr/bin/env python3
"""Claude Code statusline, three lines:
  1. model · effort · dir · branch · PR · lines changed
  2. prompt cache | ctx % | 5h limit | 7d limit
  3. in/out tokens · cost | Claude Code version

Reads the statusline JSON payload on stdin. Cumulative tokens are summed from the
session transcript — "in" = input + cache read + cache creation, "out" = output —
since the payload's context_window.* fields reflect only the current context
window, not the whole-session total. The sum is cached per session and only the
newly appended part of the transcript is read on each refresh. Runs locally and
consumes no API tokens.
"""
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

DIM = "\033[2m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
MAGENTA = "\033[35m"
CLAUDE_ORANGE = "\033[38;2;217;119;87m"  # Claude brand terracotta #D97757 (24-bit color)
RESET = "\033[0m"

EFFORT_COLORS = {"low": DIM, "medium": GREEN, "high": YELLOW, "xhigh": MAGENTA}
RAINBOW = ("\033[31m", "\033[33m", "\033[32m", "\033[36m", "\033[34m", "\033[35m")


def human(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}k"
    return str(n)


TOKEN_CACHE_DIR = Path(tempfile.gettempdir()) / "claude-statusline"


def load_token_cache(cache_file: Path, transcript: Path) -> dict:
    """Cached running sum, or a fresh one when missing, corrupt, or the transcript shrank."""
    fresh = {"path": str(transcript), "offset": 0, "in": 0, "out": 0, "last_id": None}
    try:
        cache = json.loads(cache_file.read_text())
    except Exception:
        return fresh
    if cache.get("path") != str(transcript) or cache.get("offset", 0) > transcript.stat().st_size:
        return fresh
    return cache


def sum_transcript_tokens(transcript_path: str, session_id: str) -> tuple[int, int]:
    """Sum session tokens as (input incl. cache read/write, output).

    Reads only what was appended since the last run (offset cached per session).
    Claude Code writes one transcript row per content block, each repeating the
    message's usage, so consecutive rows with the same message id count once.
    """
    p = Path(transcript_path) if transcript_path else None
    if not p or not p.is_file():
        return 0, 0
    cache_file = TOKEN_CACHE_DIR / f"{session_id or p.stem}.json"
    cache = load_token_cache(cache_file, p)

    with p.open("rb") as f:
        f.seek(cache["offset"])
        chunk = f.read()
    complete = chunk[: chunk.rfind(b"\n") + 1]  # a half-written last line waits for the next run

    for line in complete.splitlines():
        try:
            row = json.loads(line)
        except Exception:
            continue
        if row.get("type") != "assistant":
            continue
        message = row.get("message", {}) or {}
        message_id = message.get("id")
        if message_id and message_id == cache["last_id"]:
            continue
        cache["last_id"] = message_id
        usage = message.get("usage", {}) or {}
        cache["in"] += (
            (usage.get("input_tokens") or 0)
            + (usage.get("cache_read_input_tokens") or 0)
            + (usage.get("cache_creation_input_tokens") or 0)
        )
        cache["out"] += usage.get("output_tokens") or 0

    if complete:
        cache["offset"] += len(complete)
        try:
            TOKEN_CACHE_DIR.mkdir(exist_ok=True)
            tmp = cache_file.with_suffix(".tmp")
            tmp.write_text(json.dumps(cache))
            os.replace(tmp, cache_file)  # atomic: a cancelled run never leaves a torn cache
        except Exception:
            pass
    return cache["in"], cache["out"]


def git_branch(cwd: str) -> str:
    try:
        out = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=cwd or None,
            capture_output=True,
            text=True,
            timeout=1,
        )
        return out.stdout.strip()
    except Exception:
        return ""


def ctx_color(pct: float) -> str:
    if pct >= 80:
        return RED
    if pct >= 50:
        return YELLOW
    return GREEN


def braille_bar(pct: float, width: int = 5) -> str:
    """Mini progress bar from braille cells, single-dot resolution (8 dots per cell).

    Each cell fills dot by dot, row-wise from bottom-left to top-right
    (⡀⣀⣄⣤⣦⣶⣷⣿); the unfilled track is dim. Width 5 → 40 steps, 2.5 % per dot.
    A partial cell shows only its filled dots — one glyph can't carry two colors.
    """
    partials = "⡀⣀⣄⣤⣦⣶⣷"
    dots = max(0, min(width * 8, round(pct / 100 * width * 8)))
    full, rem = divmod(dots, 8)
    color = ctx_color(pct)
    bar = ""
    if full or rem:
        bar += f"{color}{'⣿' * full}{partials[rem - 1] if rem else ''}{RESET}"
    empty = width - full - (1 if rem else 0)
    if empty:
        bar += f"{DIM}{'⣿' * empty}{RESET}"
    return bar


def effort_segment(data: dict) -> str:
    """Reasoning effort, one color per level; 'max' is rainbow.

    Empty when the current model does not support the effort parameter.
    """
    level = (data.get("effort", {}) or {}).get("level")
    if not level:
        return ""
    if level == "max":
        return "".join(
            f"{RAINBOW[i % len(RAINBOW)]}{ch}" for i, ch in enumerate("✦max✦")
        ) + RESET
    return f"{EFFORT_COLORS.get(level, '')}{level}{RESET}"


def reset_in(resets_at) -> str:
    """'1h23m' until the rate-limit window resets, or '' if unknown/past."""
    try:
        secs = int(resets_at) - int(time.time())
    except Exception:
        return ""
    if secs <= 0:
        return ""
    h, m = divmod(secs // 60, 60)
    d, h = divmod(h, 24)
    if d:
        return f"{d}d{h}h"
    return f"{h}h{m:02d}m" if h else f"{m}m"


def limit_segment(data: dict, window: str, label: str) -> str:
    """Rate-limit usage for one window ('five_hour'/'seven_day').

    Empty when absent (non-subscriber / pre-first-response).
    """
    win = (data.get("rate_limits", {}) or {}).get(window, {}) or {}
    pct = win.get("used_percentage")
    if pct is None:
        return ""
    try:
        pct = float(pct)
    except Exception:
        return ""
    seg = f"{DIM}{label}{RESET} {braille_bar(pct)} {ctx_color(pct)}{int(pct)}%{RESET}"
    left = reset_in(win.get("resets_at"))
    if left:
        seg += f" {DIM}↻{left}{RESET}"
    return seg


PR_STATE_COLORS = {"approved": GREEN, "changes_requested": RED, "pending": YELLOW, "draft": DIM}


def link(url: str, text: str) -> str:
    """OSC 8 hyperlink (Cmd+click in iTerm2/Kitty/WezTerm; plain text elsewhere)."""
    return f"\033]8;;{url}\033\\{text}\033]8;;\033\\"


def pr_segment(data: dict) -> str:
    """Clickable '#123' (GitHub PR) or '!123' (GitLab MR), colored by review state."""
    pr = data.get("pr", {}) or {}
    number = pr.get("number")
    if not number:
        return ""
    sigil = "!" if pr.get("kind") == "mr" else "#"
    color = PR_STATE_COLORS.get(pr.get("review_state"), "")
    text = f"{color}{sigil}{number}{RESET}"
    return link(pr["url"], text) if pr.get("url") else text


def lines_segment(data: dict) -> str:
    """'+156 −23' lines changed this session; empty when nothing changed."""
    cost = data.get("cost", {}) or {}
    added = cost.get("total_lines_added") or 0
    removed = cost.get("total_lines_removed") or 0
    if not added and not removed:
        return ""
    return f"{GREEN}+{added}{RESET} {RED}−{removed}{RESET}"


def cache_segment(data: dict) -> str:
    """Prompt cache: time until it goes cold + session hit ratio.

    Warm with ≥5 min left is green, under 5 min yellow, cold dim — a cold cache
    means the next message re-writes the whole prefix at full price.
    """
    pc = data.get("prompt_cache", {}) or {}
    if not pc.get("caching_observed"):
        return ""
    left = reset_in(pc.get("expires_at")) if pc.get("warm") else ""
    if left:
        secs = int(pc["expires_at"]) - int(time.time())
        state = f"{GREEN if secs >= 300 else YELLOW}●{left}{RESET}"
    else:
        state = f"{DIM}○cold{RESET}"
    seg = f"{DIM}cache{RESET} {state}"
    ratio = pc.get("hit_ratio")
    if ratio is not None:
        seg += f" {DIM}{int(float(ratio) * 100)}%{RESET}"
    return seg


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0

    model = (data.get("model", {}) or {}).get("display_name", "?")
    workspace = data.get("workspace", {}) or {}
    cwd = workspace.get("current_dir") or data.get("cwd") or ""
    dir_name = Path(cwd).name if cwd else "?"

    cost = (data.get("cost", {}) or {}).get("total_cost_usd", 0.0) or 0.0
    ctx = data.get("context_window", {}) or {}
    pct = ctx.get("used_percentage") or 0
    try:
        pct = float(pct)
    except Exception:
        pct = 0.0

    tok_in, tok_out = sum_transcript_tokens(
        data.get("transcript_path", ""), data.get("session_id", "")
    )
    branch = git_branch(cwd)
    sep = f"  {DIM}|{RESET}  "

    line1 = f"{CYAN}[{model}]{RESET}"
    effort = effort_segment(data)
    if effort:
        line1 += f" {effort}"
    line1 += f" {DIM}{dir_name}{RESET}"
    if branch:
        line1 += f" {DIM}⎇ {branch}{RESET}"
    for seg in (pr_segment(data), lines_segment(data)):
        if seg:
            line1 += f" {seg}"

    line2 = f"{DIM}ctx{RESET} {braille_bar(pct)} {ctx_color(pct)}{int(pct)}%{RESET}"
    cache_seg = cache_segment(data)
    if cache_seg:
        line2 = f"{cache_seg}{sep}{line2}"
    for window, label in (("five_hour", "5h"), ("seven_day", "7d")):
        seg = limit_segment(data, window, label)
        if seg:
            line2 += f"{sep}{seg}"

    line3 = f"in {human(tok_in)} · out {human(tok_out)}  ${cost:.2f}"
    version = data.get("version")
    if version:
        line3 += f"{sep}{CLAUDE_ORANGE}v{version}{RESET}"

    print(line1)
    print(line2)
    print(line3)
    return 0


if __name__ == "__main__":
    sys.exit(main())
