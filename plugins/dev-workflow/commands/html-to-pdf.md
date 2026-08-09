---
description: Render an HTML file to PDF via headless Chrome. Self-contained — works in any project, no project-local script required. Defaults to one long single page mirroring the HTML; `--divide` gives classic A4 pagination for paper.
argument-hint: "[vstup.html] [výstup.pdf] [--divide] [--width 920]"
---

Render an HTML file to PDF via headless Chrome. Self-contained — works in any project, no project-local script required.

By **default** the PDF is **one long single page** that mirrors the HTML (no A4 pagination, no page-break white gaps). Pass `--divide` for classic A4 multi-page output (the document's own print CSS decides the breaks) — use it when the result is meant to be printed on paper.

## Input

`$ARGUMENTS`:
- _empty_ → find HTML files in the current project; if there is one obvious candidate use it, otherwise ask the user which to convert.
- one path → the HTML file to convert (relative paths resolve from the project root).
- two paths → `<input.html> <output.pdf>`.
- flags (anywhere): `--divide` = A4 pagination instead of one long page; `--width N` = layout width in CSS px for long mode (default 920).

## Steps

1. Resolve `INPUT` (and optional `OUTPUT`) and any flags from `$ARGUMENTS` as above. Verify `INPUT` exists; if not, tell the user and stop.
2. Default `OUTPUT` = `INPUT` with `.html` replaced by `.pdf` (next to the source).
3. Fast path: if `~/.claude/scripts/html2pdf.sh` is executable, run it (passing flags through) and skip to step 6:
   `~/.claude/scripts/html2pdf.sh [--divide] [--width N] "<INPUT>" "<OUTPUT>"`
   The script defaults to the single long page (driving Chrome via the DevTools Protocol to measure the exact content height) and auto-falls-back to A4 if Node.js/WebSocket is unavailable.
4. Otherwise (script absent) locate a Chromium-based browser (first match wins):
   - `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`
   - `/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary`
   - `/Applications/Chromium.app/Contents/MacOS/Chromium`
   - `/Applications/Brave Browser.app/Contents/MacOS/Brave Browser`
   - `/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge`
   If none found, tell the user to install Google Chrome and stop.
5. Render with an absolute `file://` path (this manual fallback produces **A4 paginated** output — the long-page mode needs the script in step 3):
   `"<CHROME>" --headless=new --disable-gpu --no-pdf-header-footer --virtual-time-budget=3000 --print-to-pdf="<OUTPUT>" "file://<ABSOLUTE INPUT>"`
6. Confirm the `OUTPUT` path and open it on macOS: `open "<OUTPUT>"`.

## Rules

- Do NOT modify the HTML — only render it.
- Correct background colors require the HTML's print CSS to set `print-color-adjust:exact` (Chrome prints backgrounds in headless print-to-pdf by default; this guarantees it).
- Output PDF lands next to the HTML unless a second argument overrides it.
- Single render action only; no unrelated changes.
