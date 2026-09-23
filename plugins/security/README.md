# Security

Language- and stack-agnostic security audit. Produces a prioritized markdown report plus a
machine-readable `findings.json`.

## What's included

### Skills
- `/mdv-security-audit` — Detects the application class, gates focus areas to that class, runs scanners in parallel, then triages and reports

### Agents
- **security-auditor** — Scans a single focus area (injection, auth, secrets, crypto, deps, realtime-transport, hardware-io, …) and returns JSON findings. Invoked in parallel by the skill, not directly

## Installation

```
/plugin marketplace add dvomar/claude-codeworks
/plugin install security@codeworks
```

## Usage

```
/mdv-security-audit
/mdv-security-audit src/api
```

Works on any stack and any application class — web fullstack/SPA/API, thick clients
(.NET kiosks, Electron, Tauri, WPF, Qt, mobile), CLI tools and libraries. The app-class
gate is the point: a kiosk backend gets `realtime-transport`, `hardware-io` and
`physical-attack-surface` checks instead of XSS/CSP findings that cannot apply to it.

Also triggers on informal phrasing — "is this secure", "find security issues",
"zkontroluj bezpečnost".
