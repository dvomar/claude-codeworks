# Stack checklist: .NET + SignalR thick-backend / kiosk

For `app_class = thick-backend` on .NET 8 + ASP.NET Core + SignalR with hardware drivers. Archetype: CashMachine5.

Generic checklists live in `agents/security-auditor.md`; this file covers patterns specific to this stack.

## Deployment context defaults

- **LAN-only** by default — internet exposure would be a deployment misconfig, not the design.
- **Physically accessible** — kiosks live in lobbies, atriums, hotel lobbies, transit hubs.
- **No public auth** — service menu is the only gated UI; customer UI is unauthenticated by design.
- **Hardware-attached** — cash recyclers, bill validators, scanners, printers, terminals all reachable from the service.

Severity scaling: see `severity-rubric.md` calibration table. **Money + physical access dominates.**

## Realtime transport — SignalR

- **Hub authorization** — `[Authorize]` absent on every hub is **by design** in CM5 (and similar). Flag once with deployment context, not per hub. Document the assumed trust boundary.
- **Hub method validation** — every parameter from client is untrusted; validate at the top of every hub method. Default to "reject if missing required field".
- **`Clients.All` broadcasts** — the project pattern is "broadcast to all, FE filters by `sessionId`". This means **any connected client sees all sessions' events**. If `Clients.All` carries any sensitive data (PAN, PII, full receipt details, settlement totals), flag it. Fix: use `Clients.Client(connectionId)` or groups keyed by sessionId.
- **Per-connection rate limiting** — SignalR doesn't ship one. Flag absence on hubs that trigger HW actions (CashPaymentHub, ServiceMenuHub).
- **Hub method idempotency** — if calling `StartXxx` twice causes double-dispense, that's a bug + a vuln.
- **Hub disconnection cleanup** — race between client disconnect and ongoing fire-and-forget operation can leave HW in inconsistent state.
- **Transport fallback** — if WebSocket downgrades to long-polling over HTTP without TLS, traffic is visible on LAN; check Kestrel HTTPS config.

## Service-menu auth

- **Password file location** — typically `Settings/AccessToServiceMenuSettings.json`. Check:
  - File ACL: not world-readable; ideally only the service account.
  - Storage: plaintext PIN is the current pattern; flag as **High** with deployment context.
  - Comparison: must be constant-time. `==` on strings in C# is timing-sensitive on the JIT path (varies by length). Use `CryptographicOperations.FixedTimeEquals`.
- **PIN strength** — 4-digit PIN against LAN-attacker = 10k attempts. Even with 200ms latency that's ~30 min. Add per-IP rate limit on `AuthHub.Login`.
- **Session token leakage** — if login returns a long-lived bearer that any other hub doesn't validate, attacker only needs to crack PIN once.

## Hardware drivers

- **Untrusted device frames** — drivers parsing serial/USB frames assume well-formed input. If an attacker can physically attach a different USB device that enumerates as the bill validator's COM class, they can send arbitrary commands back. Flag absence of:
  - device-identity check at handshake
  - bounds check on incoming length/length-prefix fields
  - protocol-level signature/HMAC (most vendor protocols don't have one — note it)
- **Device responses fed into business logic without validation** — a malicious device could report "cashbox is empty" or "10,000 CZK was dispensed when 100 was requested".
- **Watchdog / safety timer** — runaway dispense loop must have a cap. Flag dispenser loops without max-cycle / max-amount.
- **Cashbox-state invariants** — if a crash leaves cashbox lid unlocked, that's a vuln.
- **Hardware vendor SDK trust** — ITL/NMD/MEI SDKs may run with high privilege; check if you're running the .NET process as Administrator only because the SDK demanded it. Reduce.

## Native IPC / COM / serial

- **COM references** — `[ComImport]` interfaces accept calls from any local process. If the COM server is registered system-wide and exposes sensitive ops, audit.
- **Named pipes** — `NamedPipeServerStream` without `PipeAccessRule` / SD = world-accessible.
- **Custom URL schemes / deep links** — kiosk shouldn't accept any (no browser context), but if it does, validate scheme allowlist.

## Local storage

- **`appsettings.Development.json`** — sample creds OK if `Development` is never the deployed environment. Confirm.
- **`Settings/*.json`** — SMTP creds, terminal API tokens, ERP API tokens. Check:
  - Plaintext vs DPAPI / Windows Credential Manager.
  - File ACL.
  - Whether `git-tracked` (often yes, with per-deployment overrides — flag this as risky).
- **Connection strings with passwords** — DPAPI-encrypt or use Windows Auth.
- **SQL Server local instance** — service-account access; `sa` must not be the app account.

## Print / Email modules

- **PrintHub commands** — if a hub method can write arbitrary content to the printer, that's a "infinite paper" / "supply exhaustion" DoS. Bound batch size.
- **Print templates with user input** — template injection (Razor / Liquid / similar). Verify the template engine escapes by default.
- **EmailSMTP** — if hub method can dispatch arbitrary emails, that's spam relay. Restrict to fixed recipients or require approval.
- **EmailToFiles** — writes attachments to disk. Path traversal on filename. PII in files at rest.
- **PAN / CVV / track data in templates or logs** — PCI violation. **Critical.**

## Money math

- **Always `MoneyAmount.PennyValue` (haléř, integer)** — flag any `float`/`double`/`decimal` arithmetic on money. Project rule per CLAUDE.md.
- **Integer overflow** — `int.MaxValue` haléř = ~21M CZK. Cashbox totals stay well under but **lifetime counters** can overflow. Use `long` or `checked` arithmetic.
- **Negative payout** — if dispense amount can be negative (signed math bug), it could mean "credit the customer" instead of "debit cashbox". Flag every dispense entry point for sign validation.
- **Denomination mismatch** — payout of 700 CZK with only 1000-CZK notes in stock should refuse, not partial-pay.

## EF Core / SQL Server

- **`FromSqlRaw` / `ExecuteSqlRaw` with interpolation** → SQLi. Use `FromSqlInterpolated` (parameterizes) or LINQ.
- **`AsNoTracking()` rule** — read queries should be AsNoTracking. If a tracked query then writes back without auth, that's an authz gap (also covered under access-control).
- **`db.Database.Migrate()` on startup** — fine in this project; **`EnsureDeleted()` + `EnsureCreated()`** must be guarded by config flag (`RebuildDatabaseOnStartup`). Flag if guard is missing or default-true in production appsettings.
- **DbContext lifetime** — singletons must use `IDbContextFactory<>`. Misuse = data corruption, but not directly a security issue unless concurrent writes corrupt money totals.

## Platform-hardening (Windows kiosk)

- **Kiosk-mode** — Windows Assigned Access, ShellLauncher, AppLocker. Verify present.
- **Service account** — not LocalSystem unless required. Use a low-priv account.
- **Auto-update** — Windows Update enabled? App self-update? Code-signing certificate?
- **USB autorun** — disabled at OS policy level?
- **Remote desktop / VNC** — disabled or jump-host only?
- **Network shares** — kiosk shouldn't mount SMB to anywhere; if it does, scope tight.
- **Defender / EDR** — present?

## CM5-specific severity defaults

| Pattern | Default severity (CM5 LAN-kiosk) |
|---|---|
| Service menu PIN brute-force possible | High |
| `[Authorize]` absent on hubs | High (one finding, not per hub) |
| `Clients.All` carries PAN / track data | Critical |
| `Clients.All` carries session ID + payment amount | Medium (info-disclosure, no PII) |
| Hardware driver: no length check on incoming frame | Medium (requires physical USB swap) |
| Hardware driver: no device-identity handshake | Medium |
| `EnsureDeleted` reachable in any prod config | Critical |
| `appsettings.Development.json` with sample DB password | Info (suppress with rationale) |
| `RebuildDatabaseOnStartup: true` default | High if default; Info if dev-only flag |
| Money math in `decimal` instead of haléř integer | Medium (correctness; can be exploited via rounding) |
| MD5 hash of receipt content for filename | Info (not security use) |
