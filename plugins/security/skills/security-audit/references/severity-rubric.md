# Severity rubric

Severity is **not absolute** — it depends on (impact × exploitability × scope) **scaled by deployment exposure**. Two identical bugs in different deployments get different severities. This is intentional.

## Inputs

- **Impact** (what attacker gains): RCE / data loss / money loss / privilege escalation / info disclosure / DoS / nuisance.
- **Exploitability** (how easy): remote unauthenticated / remote authenticated / adjacent network / physical / requires chain.
- **Scope** (how many users / how much data): all users / single user / all records / single record.
- **Deployment exposure** (from recon): internet-exposed-public / internet-exposed-internal / lan-only-corporate / lan-only-kiosk / local-developer / airgapped.

## Severity decision table

Start from the impact row, adjust by exploitability/exposure modifiers.

| Impact | Remote unauth + internet-exposed | Remote auth + internet | LAN-only-corporate | LAN-only-kiosk | Physical access only | Local-developer |
|---|---|---|---|---|---|---|
| RCE on server | Critical | Critical | High | High | Medium | Low |
| Cash payout / direct money loss | Critical | Critical | High | High | Critical (kiosk pulls cash) | Low |
| Read all user data / PII | Critical | High | High | Medium | High (PII on device) | Low |
| Read one user's data (IDOR) | High | High | Medium | Medium | Medium | Low |
| Write any data / tamper | Critical | High | High | Medium | High | Low |
| Privilege escalation | Critical | Critical | High | High | High | Low |
| Auth bypass | Critical | High | High | High | High | Low |
| DoS (crash / hang) | High | Medium | Medium | Medium | Low | Info |
| Info disclosure (non-PII config) | Medium | Medium | Low | Low | Low | Info |
| Defense-in-depth gap (no header, weak cipher when unused) | Low | Low | Low | Low | Low | Info |
| Tech-debt / hardening | Info | Info | Info | Info | Info | Info |

## Modifiers

- **Confidence-adjusted display**: If `severity = high` but `confidence = low`, label in the report as "High (unverified)". Don't downgrade — uncertainty is its own dimension.
- **Chain modifier**: If a finding is a **step** in a documented attack chain that reaches Critical impact, you may promote it by one level (e.g., Medium → High) and link the chain ID.
- **Scope amplifier**: One affected record = no change. All-records-of-all-users = +1 level. Multi-tenant data leak across tenants = +1 level on top.
- **Money / safety markers**: If `markers` includes `money-handling`, `physical-public-access`, `health-data`, `child-safety`, treat "Medium" floor for relevant findings.
- **Sensitive ops with no logging/audit**: +1 confidence if you can't reconstruct the attack — *not* a severity boost, but call it out in fix.

## Demotions

- **Dev-only code path (`#if DEBUG`, `appsettings.Development.json`, `NODE_ENV !== "production"`)** → demote to Info unless it leaks into prod. Verify the gate, then demote.
- **Test fixtures** → Info or suppress (with rationale).
- **Vendored / archived / unreachable code** → suppress.
- **Deprecated module being removed** → Info if removal is scheduled (cite the issue/PR).

## Example calibrations (CashMachine5 reference)

| Finding | Default | Adjusted | Why |
|---|---|---|---|
| SignalR hubs have no `[Authorize]` | Critical (web) | High | Deployment is LAN-only-kiosk; severity floor for cash kiosk is High, not Critical, until VPN-exposure proven. |
| Service-menu password compared with `==` | High | High | Constant-time fix; LAN-attacker can brute-force; markers include `money-handling`. |
| Service-menu password stored in plaintext JSON | High | High | Same as above. |
| `appsettings.Development.json` contains `sa/YourStrong@Passw0rd` | Critical (looks like a secret) | Info | Dev-only file, value is sample, gated. Suppress with rationale. |
| `RebuildDatabaseOnStartup: true` in shipped config | Critical (data loss) | Critical | Real risk — confirm it's not in prod appsettings.json. |
| `Process.Start` with concatenated args in `PrintService` | High | High | Reachable via PrintHub from LAN. |
| Card PAN in `_logger.LogInformation(...)` | Critical (PCI) | Critical | Marker `money-handling`; logs go to disk + Sentry. |
| MD5 used for non-security hash (filename hashing) | Medium (default) | Info | Cite usage; not a security function. |

## Calibration check (sanity)

Before finalizing severity, ask:
1. Could a fresh hire reading this report tell "fix today" from "fix this quarter"? If everything looks similar, your distribution is off.
2. Is anything labeled Critical that **doesn't** require immediate action? Demote.
3. Is anything labeled Low that, if exploited, would cost the company a real dollar amount? Promote.
4. Does the report make sense to someone who doesn't know the codebase? If not, add deployment_context to the finding.
