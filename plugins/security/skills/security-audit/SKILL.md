---
name: security-audit
description: Performs security audits of applications and codebases — language- and stack-agnostic. Triggers on requests to audit security, find vulnerabilities, security review, pentest a codebase, check for security holes, OWASP scan, threat modeling, or any phrasing like "is this secure", "find security issues", "audit my app", "zkontroluj bezpečnost", "najdi bezpečnostní díry". Use this skill whenever the user asks about application security, even informally — including reviewing a single file/PR for security issues, validating an implementation, hardening recommendations, or auditing dependencies. Works on any stack and any application class: web fullstack/SPA/API, thick clients (.NET kiosks, Electron, Tauri, WPF, Qt, mobile), CLI tools, libraries. Produces a prioritized markdown report with concrete fixes plus a machine-readable findings.json.
---

# Security Audit

Multi-phase, language-agnostic security audit. Orchestrates `security-auditor` subagents to find, prioritize, and propose fixes for vulnerabilities in **any codebase** — web apps, APIs, thick/native clients, kiosk backends, mobile apps, CLI tools, libraries.

The skill adapts to the target by **detecting the application class** (web-fullstack / web-spa / web-backend / thick-backend / desktop / mobile / cli / library) and gating focus areas accordingly. A kiosk backend like CashMachine5 gets `realtime-transport`, `hardware-io`, `native-ipc`, `physical-attack-surface` checks instead of XSS/CSP nonsense. A pure React SPA gets web-frontend checks but skips hardware-io.

## When to use

- "Audit security of [project]", "find vulnerabilities", "is this secure?"
- "Zkontroluj bezpečnost", "najdi bezpečnostní díry", "udělej security review"
- Reviewing auth flows, payment handlers, API endpoints, file uploads, hardware drivers, IPC handlers
- After a feature is implemented and before it ships
- Validating an external integration (Stripe webhook, OAuth, terminal SDK, ERP integration)
- Hardening review of a kiosk / thick client before deployment

## Workflow

```
0. Ask depth → 1. Recon + app-class detect → 2. Scan (parallel agents, gated by class) → 3. Triage → 4. Report
```

### Phase 0: Choose depth

Ask the user via `AskUserQuestion` (in Claude Code) or plain prompt. **Two options:**

- **Quick scan (5–10 min)** — Static analysis only. OWASP Top 10 + secrets + deps + class-specific basics. Best for PR review, small codebases, fast feedback.
- **Deep audit (20–40 min)** — Quick + business logic, crypto correctness, race conditions, attack chains, threat modeling, infra/platform hardening, physical attack surface (where applicable).

Also confirm:
- **Target path** (default: current working directory)
- **Out-of-scope paths** (e.g., `node_modules`, `.next`, `dist`, `bin/`, `obj/`, vendored libs, auto-generated migrations)

### Phase 1: Recon + app-class detection

**Do this yourself — don't delegate.** Output `recon.json` (machine) + `recon.md` (human) into `.claude/security/`.

1. **Stack detection** — read whichever manifests exist:
   - JS/TS: `package.json`, `tsconfig.json`, `next.config.*`, `nuxt.config.*`, `electron-builder.*`, `tauri.conf.json`
   - .NET: `*.sln`, `*.csproj`, `*.fsproj`, `appsettings*.json`, `Program.cs`
   - Python: `pyproject.toml`, `requirements*.txt`, `Pipfile`, `manage.py`
   - Ruby: `Gemfile`, `config/application.rb`
   - Go: `go.mod`, `main.go`
   - Rust: `Cargo.toml`
   - Java/Kotlin: `pom.xml`, `build.gradle*`, `AndroidManifest.xml`
   - PHP: `composer.json`
   - Swift/iOS: `Package.swift`, `Info.plist`, `*.xcodeproj`
   - Flutter/Dart: `pubspec.yaml`
   - C/C++: `CMakeLists.txt`, `conanfile.txt`, `vcpkg.json`
   - Other: `mix.exs` (Elixir), `rebar.config` (Erlang), `cabal.project` (Haskell)

2. **App-class detection** — use `references/app-class-detection.md` rules. Output one of:
   `web-fullstack | web-spa | web-backend | thick-backend | desktop | mobile | cli | library | hybrid`.
   Confirm the detected class with the user in one sentence before launching Phase 2.

3. **Entry points** — find:
   - HTTP routes / API handlers / webhooks
   - SignalR / WebSocket / gRPC / Server-Sent Events hubs and message handlers
   - Background workers, scheduled jobs, message queue consumers
   - CLI entrypoints (argv parsing, stdin readers)
   - IPC channels (Electron IPC, COM, named pipes, D-Bus, XPC)
   - Deeplinks / custom URL schemes / intent filters
   - File watchers, drop folders, scanned barcodes/QR ingestion
   - **Hardware buses** — serial/USB/COM/SPI/GPIO drivers (kiosks, embedded)

4. **Trust boundaries** — where untrusted input enters:
   - Network: request body / query / headers / cookies / WebSocket frames
   - File: uploaded files, config files watched, drop folders
   - User: form input, deeplink params, barcode/QR payloads
   - Other processes: IPC messages, COM calls, named-pipe data
   - Hardware: serial frames, USB descriptors, device responses (may be attacker-controlled if HW is physical)
   - Environment: env vars read at runtime, command-line args
   - Third-party: webhook callbacks, OAuth redirects, ERP/terminal SDK responses

5. **Sensitive operations** — payments, auth, file system writes, shell exec, raw SQL/NoSQL, deserialization, crypto operations, PII handling, logging of any of the above.

6. **Secrets surface** — `.env*`, `appsettings*.json`, `*.config`, `Settings/*.json`, CI/CD configs (`.github/`, `.gitlab-ci.yml`, `azure-pipelines.yml`), Dockerfiles, Kubernetes manifests, terraform state.

7. **Deployment exposure (critical for severity scoring)** — is the app:
   - Internet-exposed? Public ingress?
   - LAN-only? Air-gapped?
   - On a kiosk physically accessible to the public?
   - Local-only (CLI on developer machine)?
   This **massively changes severity** of identical findings. CM5 SignalR without `[Authorize]` is Medium on LAN, Critical if VPN-exposed.

Write `recon.md` (~15 lines, human-readable) and `recon.json` (structured — see `references/recon-schema.md`) into `.claude/security/`. Create the directory if missing. If `.claude/security/` is not writable, fall back to `<repo>/security-audit/` or echo to chat.

### Phase 2: Scan (parallel agents, gated by app-class)

Spawn `security-auditor` subagents **in parallel** — one per relevant focus area. Each agent receives:
- **focus_area** (e.g., `injection`, `auth`, `realtime-transport`)
- **app_class** (from recon)
- **depth** (quick | deep)
- **recon_excerpt** — relevant slice of `recon.json` (entry points, sensitive ops, file globs for this area)
- **scope_paths** — included paths; **exclude_paths** — out-of-scope

Use `subagent_type: "security-auditor"` if registered (it is — see `.claude/agents/security-auditor.md`). If unavailable, fall back to `subagent_type: "general-purpose"` and inline the system prompt from `agents/security-auditor.md`.

**Focus area selection — full matrix in `references/focus-areas.md`.** Compressed summary:

| Focus area | Always-on app-classes (Quick) |
|---|---|
| `injection` | web-*, thick-backend, desktop, mobile, cli, library |
| `auth` | web-fullstack, web-backend, thick-backend, desktop, mobile |
| `access-control` | web-fullstack, web-backend, thick-backend, desktop, mobile |
| `secrets` | **all classes** |
| `crypto` | **all classes** |
| `deps` | **all classes** |
| `input-validation` | **all classes** |
| `web-frontend` | web-fullstack, web-spa |
| `realtime-transport` | thick-backend, web-* (if WebSocket/SSE/gRPC detected) |

**Deep-only adds (gated by class):**

| Focus area | Classes |
|---|---|
| `business-logic` | web-fullstack, web-backend, thick-backend, desktop, mobile |
| `hardware-io` | thick-backend, desktop (if HW detected) |
| `native-ipc` | thick-backend, desktop, mobile |
| `local-storage` | thick-backend, desktop, mobile, web-spa (LocalStorage/IndexedDB), cli |
| `update-channel` | desktop, mobile, thick-backend (if auto-update), cli (if self-update) |
| `platform-hardening` | thick-backend, desktop, mobile, web-backend |
| `physical-attack-surface` | thick-backend (kiosk), desktop (kiosk-mode) |
| `logging-pii` | web-*, thick-backend, desktop, mobile |
| `infra` | web-fullstack, web-backend, thick-backend |
| `mobile-platform` | mobile |
| `threat-model` | **all classes except cli** |

**Don't run an area that has no targets** (e.g., skip `web-frontend` for a CLI; skip `hardware-io` for a SaaS API). The agent matrix in `references/focus-areas.md` is authoritative.

**External tools** the agents may invoke if installed (see `references/dep-scanners.md` for the full list):
- Universal: `osv-scanner`, `trivy fs`, `semgrep --config=auto`, `gitleaks`, `trufflehog`
- Per-stack: `npm audit`, `dotnet list package --vulnerable`, `pip-audit`, `govulncheck`, `cargo audit`, `bundle audit`, `mvn dependency-check`, `composer audit`
Missing tools → fall back to static analysis. Note missing tools as a `limitations` field in the report.

Each agent returns a JSON array of findings — schema in `references/finding-schema.md`.

### Phase 3: Triage

Collect findings from all agents. Then:

1. **Deduplicate** — same root cause flagged by multiple agents collapses into one finding with multiple `references[]`. Hashing by `(file, line_range, vulnerability_class)` is a reasonable start.
2. **Re-score severity** using `references/severity-rubric.md`. **Severity = impact × exploitability × scope, scaled by deployment exposure** (from recon). Don't trust individual agent severities — you have the global view and the deployment context.
3. **Build attack chains** (Deep only) — can two Mediums combine into a Critical? E.g., IDOR + missing rate limit = mass enumeration; weak service-menu password + reachable from LAN + ability to enable shell exec command = RCE. Document chains as a separate section.
4. **Suppress false positives** — be honest. Common FPs: test fixtures with fake secrets, intentional `eval` in build scripts, dev-only debug routes guarded by env flag, mock credentials in `appsettings.Development.json`, code under `#if DEBUG`. Mark these `confidence: "false-positive-suppressed"` with rationale, don't silently drop them.

### Phase 4: Report

Generate two files in `.claude/security/`:

1. **`audit-YYYY-MM-DD.md`** — human-readable report. Use `assets/report-template.md`.
2. **`findings.json`** — machine-readable, schema in `references/finding-schema.md`.

Then in chat, summarize concisely:
- Total findings by severity (Critical / High / Medium / Low / Info)
- Top 3 most urgent (one-line fix each)
- Attack chains, if any
- Path to full report
- Offer to walk through any specific finding or generate patches

## Operating principles

**Honesty over completeness.** If you can't verify exploitability statically, say "potential" not "confirmed". Use `confidence: low|medium|high`. Don't pad the report.

**Cite code locations.** Every finding must include `file:line` (or `file:line_start-line_end`). Vague findings ("auth seems weak somewhere") are useless and erode trust.

**Concrete fixes.** Not "use stronger validation" but a specific code diff, library suggestion, or config change. If non-trivial, write the actual replacement.

**Respect scope.** If the user said "audit the payment module", don't sprawl into the marketing site.

**No theatrical paranoia.** Quality > quantity. Don't flag every `useState` to inflate the count. If a "Medium" is actually Info, mark it Info.

**Deployment context dominates severity.** A SignalR hub without `[Authorize]` on a LAN-only kiosk is Medium. The same hub VPN-exposed is Critical. Severity without exposure context is meaningless — re-score using the rubric.

**Preserve unknown-by-design.** Some apps (CM5) intentionally have no JWT/auth — they rely on network isolation. Flag it once with deployment context, don't repeat it per endpoint.

**Tool fallbacks, not tool dependencies.** Missing `osv-scanner` is a `limitations` line in the report, not a stop sign.

## Quick reference

- App-class detection: `references/app-class-detection.md`
- Focus-area × app-class matrix: `references/focus-areas.md`
- Subagent system prompt: `agents/security-auditor.md` (also registered at `.claude/agents/security-auditor.md`)
- Finding schema: `references/finding-schema.md`
- Recon schema: `references/recon-schema.md`
- Severity rubric: `references/severity-rubric.md`
- Dep scanners by stack: `references/dep-scanners.md`
- Report template: `assets/report-template.md`
- Stack-specific checklists: `references/stacks/`
