#!/usr/bin/env python3
"""Claude Code statusline: model · dir · branch | in/out tokens · cost | ctx % | 5h/7d limits.

Reads the statusline JSON payload on stdin. Cumulative tokens are summed from the
session transcript — "in" = input + cache read + cache creation, "out" = output —
since the payload's context_window.* fields reflect only the current context
window, not the whole-session total. Runs locally and consumes no API tokens.
"""
import json
import subprocess
import sys
import time
from pathlib import Path

DIM = "\033[2m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
RESET = "\033[0m"


def human(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}k"
    return str(n)


def sum_transcript_tokens(transcript_path: str) -> tuple[int, int]:
    """Sum session tokens as (input incl. cache read/write, output)."""
    p = Path(transcript_path) if transcript_path else None
    if not p or not p.is_file():
        return 0, 0
    tok_in = tok_out = 0
    with p.open() as f:
        for line in f:
            try:
                row = json.loads(line)
            except Exception:
                continue
            if row.get("type") != "assistant":
                continue
            usage = (row.get("message", {}) or {}).get("usage", {}) or {}
            tok_in += (
                (usage.get("input_tokens") or 0)
                + (usage.get("cache_read_input_tokens") or 0)
                + (usage.get("cache_creation_input_tokens") or 0)
            )
            tok_out += usage.get("output_tokens") or 0
    return tok_in, tok_out


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

    tok_in, tok_out = sum_transcript_tokens(data.get("transcript_path", ""))
    branch = git_branch(cwd)

    seg_left = f"{CYAN}[{model}]{RESET} {DIM}{dir_name}{RESET}"
    if branch:
        seg_left += f" {DIM}⎇ {branch}{RESET}"

    seg_mid = f"\U0001f525 in {human(tok_in)} · out {human(tok_out)}  ${cost:.2f}"
    seg_ctx = f"{DIM}ctx{RESET} {braille_bar(pct)} {ctx_color(pct)}{int(pct)}%{RESET}"

    line2 = f"{seg_mid}  {DIM}|{RESET}  {seg_ctx}"
    for window, label in (("five_hour", "5h"), ("seven_day", "7d")):
        seg = limit_segment(data, window, label)
        if seg:
            line2 += f"  {DIM}|{RESET}  {seg}"

    print(seg_left)
    print(line2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
