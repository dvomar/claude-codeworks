# Recon schema (`recon.json`)

The orchestrator (Phase 1) writes this. Subagents (Phase 2) consume a slice of it.

```jsonc
{
  "schema_version": "1.0",
  "audit_date": "2026-05-25",
  "target": "/abs/path/to/repo",
  "scope_paths": ["src/", "CashMachine5/"],
  "exclude_paths": ["node_modules", "bin", "obj", ".next", "dist", "Database/Migrations"],
  "depth": "quick|deep",

  "stack": {
    "primary_languages": [".NET 8 / C#", "TypeScript"],
    "frameworks": ["ASP.NET Core", "SignalR", "EF Core 8"],
    "package_managers": ["NuGet", "npm"],
    "manifests": [
      "CashMachine5/CashMachine5.csproj",
      "package.json",
      "package-lock.json"
    ]
  },

  "app_class": "thick-backend",
  "app_class_confidence": "high",
  "deployment_exposure": "lan-only-kiosk|lan-only-corporate|internet-exposed-public|internet-exposed-internal|local-developer|airgapped",
  "markers": ["payment", "kiosk", "physical-public-access", "money-handling", "pii-light"],

  "entry_points": [
    {
      "type": "signalr-hub",
      "path": "SignalRApi/Hubs/CashPaymentHub.cs",
      "endpoint": "/CashPaymentHub",
      "methods": ["StartAcceptPayment", "CancelPayment"],
      "auth": "none",
      "notes": "All hub methods accept sessionId from client; no [Authorize]"
    },
    {
      "type": "http-route",
      "path": "Program.cs:601",
      "endpoint": "/health",
      "methods": ["GET"],
      "auth": "none"
    },
    {
      "type": "hardware-bus",
      "path": "NMD050API/Driver.cs",
      "endpoint": "COM3 (serial 9600 8N1)",
      "protocol": "NMD050 proprietary",
      "auth": "none — physical-attack-surface"
    }
  ],

  "trust_boundaries": [
    {
      "boundary": "LAN → SignalR endpoint",
      "untrusted": true,
      "controls": "none — no auth on hubs"
    },
    {
      "boundary": "Hardware device → driver parser",
      "untrusted": "device firmware trusted; untrusted if attacker can swap USB device",
      "controls": "none — drivers assume well-formed frames"
    },
    {
      "boundary": "Customer barcode scan → ScanInvoiceIdHub",
      "untrusted": true,
      "controls": "minimal — variable-symbol regex"
    }
  ],

  "sensitive_operations": [
    { "op": "Cash payout", "path": "CashService/CashService.cs", "exposure_via": ["CashPaymentHub", "ServiceMenuHub"] },
    { "op": "Card payment", "path": "TerminalPayment/TerminalService.cs", "exposure_via": ["TerminalPaymentHub"] },
    { "op": "Service menu auth", "path": "SignalRApi/Hubs/AuthHub.cs", "exposure_via": ["AuthHub.Login"] },
    { "op": "Print receipt", "path": "Print/PrintService.cs", "exposure_via": ["PrintHub"] },
    { "op": "Email dispatch", "path": "EmailSMTP/EmailSMTPController.cs", "exposure_via": ["internal only"] }
  ],

  "secrets_surface": [
    { "path": "CashMachine5/appsettings.json", "contains": ["ConnectionStrings", "EnabledDevices"], "in_git": true },
    { "path": "CashMachine5/appsettings.Development.json", "contains": ["sa password"], "in_git": true, "dev_only": true },
    { "path": "CashMachine5/Settings/AccessToServiceMenuSettings.json", "contains": ["service-menu PINs"], "in_git": true, "review_required": true },
    { "path": "CashMachine5/Settings/EmailSMTPSettings.json", "contains": ["SMTP creds"], "in_git": "depends" }
  ],

  "deps_manifests": [
    { "stack": "dotnet", "manifest": "CashMachine5.sln", "lockfile": "packages.lock.json (per-project)", "scanner": "dotnet list package --vulnerable" },
    { "stack": "npm", "manifest": "package.json", "lockfile": "package-lock.json", "scanner": "npm audit --json" }
  ],

  "platform": {
    "os_target": ["windows", "macos-dev"],
    "runtime": [".NET 8"],
    "containers": false,
    "ci": ".github/workflows/" 
  },

  "notes": "Free-form 1-3 sentences capturing anything that doesn't fit above."
}
```

## What each subagent receives (recon_excerpt)

The orchestrator slices the relevant fields per focus area to keep agent context small.

| Focus area | Excerpt fields |
|---|---|
| injection | entry_points, sensitive_operations, scope_paths |
| auth | entry_points (where auth=none), sensitive_operations (auth-related), markers |
| access-control | entry_points, sensitive_operations, deployment_exposure |
| secrets | secrets_surface, deps_manifests (for hardcoded keys), scope_paths |
| crypto | sensitive_operations (crypto-related), scope_paths |
| deps | deps_manifests, platform |
| input-validation | entry_points, trust_boundaries, scope_paths |
| web-frontend | entry_points (browser-facing), stack.frameworks, scope_paths |
| realtime-transport | entry_points (signalr/ws/grpc), trust_boundaries, deployment_exposure |
| business-logic | sensitive_operations, markers, scope_paths |
| hardware-io | entry_points (hardware-bus), trust_boundaries (hardware), scope_paths |
| native-ipc | entry_points (ipc/com/deeplinks), scope_paths |
| local-storage | secrets_surface, platform.os_target, scope_paths |
| update-channel | deps_manifests (updater libs), platform, scope_paths |
| platform-hardening | platform, deployment_exposure, scope_paths |
| physical-attack-surface | markers (kiosk/public), deployment_exposure, scope_paths |
| logging-pii | sensitive_operations (PII), markers, scope_paths |
| infra | platform.containers, platform.ci, scope_paths |
| mobile-platform | platform.os_target, stack.frameworks, scope_paths |
| threat-model | full recon |
