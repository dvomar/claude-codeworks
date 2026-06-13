# Finding schema

Both subagents (output) and orchestrator (final `findings.json`) use this schema.

## Single finding (JSON object)

```jsonc
{
  // Required
  "id": "string",                          // unique within this audit; subagents may use "<focus_area>-<n>", orchestrator reassigns to "F-001" sequence
  "focus_area": "string",                  // one of the 19 focus areas
  "title": "string",                       // short, specific. Bad: "auth issue". Good: "Service-menu password compared with == (timing attack)"
  "severity": "critical|high|medium|low|info",
  "confidence": "low|medium|high",         // low = likely needs runtime verification, medium = strong static signal, high = certain
  "summary": "string",                     // one sentence
  "evidence": [
    {
      "file": "string",                    // path relative to repo root
      "line_start": 0,                     // 1-indexed
      "line_end": 0,                       // 1-indexed; same as line_start for single-line
      "snippet": "string"                  // optional; up to ~10 lines
    }
  ],
  "impact": "string",                      // what an attacker achieves
  "exploitability": "string",              // how reachable; cite trust boundary
  "fix": {
    "summary": "string",                   // 1-2 sentences
    "diff": "string"                       // optional; before/after code or unified diff
  },

  // Optional
  "cwe": ["CWE-89", "..."],                // list of CWE IDs
  "owasp": ["A03:2021 — Injection"],       // OWASP Top 10 references
  "references": ["https://..."],            // external links
  "deployment_context": "string",          // copied from recon at triage time
  "attack_chain": ["F-007", "F-012"],      // IDs of other findings that chain with this one (filled at triage)
  "false_positive_rationale": "string",   // if confidence is "false-positive-suppressed"
  "tags": ["payment", "kiosk", "pci"]      // free-form tags
}
```

## Full report file (`findings.json`)

```jsonc
{
  "schema_version": "1.0",
  "audit_date": "2026-05-25",
  "audit_depth": "deep",
  "target": "/Users/mw/Develop/Projects/Czech-Kiosk/cashmachine5be",
  "app_class": "thick-backend",
  "deployment_exposure": "lan-only-kiosk",
  "markers": ["payment", "kiosk", "physical-public-access"],
  "limitations": [
    "trivy not installed; static analysis only for infra",
    "dotnet list package --vulnerable timed out at 60s; partial dep coverage"
  ],
  "summary": {
    "critical": 2,
    "high": 5,
    "medium": 11,
    "low": 7,
    "info": 3,
    "false_positives_suppressed": 4
  },
  "attack_chains": [
    {
      "id": "C-1",
      "title": "LAN attacker → service menu → cash payout",
      "severity": "critical",
      "steps": ["F-003", "F-007", "F-012"],
      "narrative": "Attacker on hotel LAN reaches AuthHub (no [Authorize]), brute-forces 4-digit PIN (F-003), enters service menu, invokes ServiceMenuHub.PayoutTest (F-007) which dispenses arbitrary amount with no business-rule check (F-012)."
    }
  ],
  "findings": [
    { /* finding 1 */ },
    { /* finding 2 */ }
  ]
}
```

## Severity guidance (short — full rubric in `severity-rubric.md`)

| Severity | Use when |
|---|---|
| `critical` | Direct compromise possible by remote unauthenticated attacker; money / PII / RCE; or kiosk physical attacker can extract cash |
| `high` | Direct compromise but requires auth, adjacency, or one extra step; loss of integrity for sensitive data |
| `medium` | Requires non-trivial chaining; partial info disclosure; weakened defenses |
| `low` | Defense-in-depth gap; very hard to exploit; or info-only |
| `info` | Not a vulnerability — guidance / hardening suggestion / observation |

## Confidence guidance

| Confidence | Use when |
|---|---|
| `high` | Code path is clear; vulnerable pattern is unambiguous; static analysis sufficient |
| `medium` | Pattern is suspicious; would need runtime check or harder-to-follow code path to confirm |
| `low` | Inference from limited code visibility; should be verified by humans / runtime test |

## Bad finding examples (avoid)

```json
{ "title": "Code looks insecure", "severity": "high", "evidence": [] }              // ❌ vague, no evidence
{ "title": "Possible XSS somewhere in /admin/", "severity": "critical" }            // ❌ no file:line
{ "title": "Use of useState may leak data", "severity": "medium" }                  // ❌ false-positive padding
{ "title": "Hardcoded password 'YourStrong@Passw0rd' in appsettings.Development",
  "severity": "critical" }                                                          // ❌ dev secrets, should be info or suppressed
```

## Good finding example

```json
{
  "id": "F-007",
  "focus_area": "access-control",
  "title": "ServiceMenuHub methods callable by any LAN client (no [Authorize])",
  "severity": "high",
  "confidence": "high",
  "cwe": ["CWE-862"],
  "owasp": ["A01:2021 — Broken Access Control"],
  "summary": "Every method on ServiceMenuHub — including PayoutTest, EmptyCashbox, ResetCounters — is reachable by any client connected to the SignalR endpoint, without any auth or session ownership check.",
  "evidence": [
    {
      "file": "SignalRApi/Hubs/ServiceMenuHub.cs",
      "line_start": 1,
      "line_end": 12,
      "snippet": "[SignalRHub]\npublic class ServiceMenuHub : Hub {\n    public async Task<Response> PayoutTest(string sessionId, ...) { ... }"
    }
  ],
  "impact": "Anyone on the LAN can invoke sensitive cash-management methods without authentication.",
  "exploitability": "Trivial — SignalR endpoint is bound to 0.0.0.0:5000; no [Authorize] anywhere in the project.",
  "deployment_context": "thick-backend / kiosk / LAN-only. Severity is High (not Critical) because attacker must be on the kiosk's LAN; would become Critical if VPN'd or accidentally internet-exposed.",
  "fix": {
    "summary": "Either (a) bind hub to 127.0.0.1 and proxy through a hub-internal auth check tied to the service-menu PIN session, or (b) add a connection-level token check via SignalR middleware that requires a valid AuthHub login before accepting any ServiceMenuHub call.",
    "diff": "// SignalRApi/Hubs/ServiceMenuHub.cs\n// add a token check at hub entry:\npublic override async Task OnConnectedAsync() {\n    var token = Context.GetHttpContext()?.Request.Query[\"serviceToken\"].FirstOrDefault();\n    if (!_serviceMenuAuth.IsValidToken(token)) {\n        Context.Abort();\n        return;\n    }\n    await base.OnConnectedAsync();\n}"
  },
  "references": ["https://owasp.org/Top10/A01_2021-Broken_Access_Control/"]
}
```
