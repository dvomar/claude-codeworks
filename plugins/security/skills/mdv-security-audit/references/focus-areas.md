# Focus area × app-class matrix

This file is **authoritative** for which focus areas to run for a given app class and depth. The orchestrator (SKILL.md Phase 2) uses this table to decide which `security-auditor` subagents to spawn.

Legend: `Q` = run in Quick scan, `D` = run in Deep audit only, `—` = skip for this class, `?` = run only if a relevant signal was found in recon.

| Focus area | web-fullstack | web-spa | web-backend | thick-backend | desktop | mobile | cli | library |
|---|---|---|---|---|---|---|---|---|
| **injection** | Q | — | Q | Q | Q | Q | Q | Q |
| **auth** | Q | — | Q | Q | Q | Q | — | — |
| **access-control** | Q | — | Q | Q | Q | Q | — | — |
| **secrets** | Q | Q | Q | Q | Q | Q | Q | Q |
| **crypto** | Q | Q | Q | Q | Q | Q | Q | Q |
| **deps** | Q | Q | Q | Q | Q | Q | Q | Q |
| **input-validation** | Q | Q | Q | Q | Q | Q | Q | Q |
| **web-frontend** | Q | Q | — | — | ?¹ | — | — | — |
| **realtime-transport** | ?² | — | ?² | Q | — | — | — | — |
| **business-logic** | D | — | D | D | D | D | — | — |
| **hardware-io** | — | — | — | D | ?³ | — | — | — |
| **native-ipc** | — | — | — | D | D | D | — | — |
| **local-storage** | — | D | — | D | D | D | D | — |
| **update-channel** | — | — | ?⁴ | ?⁴ | D | D | ?⁴ | — |
| **platform-hardening** | D | — | D | D | D | D | — | — |
| **physical-attack-surface** | — | — | — | ?⁵ | ?⁵ | — | — | — |
| **logging-pii** | D | — | D | D | D | D | — | — |
| **infra** | D | — | D | D | — | — | — | — |
| **mobile-platform** | — | — | — | — | — | D | — | — |
| **threat-model** | D | D | D | D | D | D | — | D |

### Conditional gating notes

1. **`web-frontend` for desktop**: only if the desktop app uses a webview / Electron renderer / Tauri webview.
2. **`realtime-transport` for web**: only if WebSocket / SignalR / SSE / gRPC detected in deps or code (`socket.io`, `ws`, `Microsoft.AspNetCore.SignalR`, `@grpc/grpc-js`, `EventSource`).
3. **`hardware-io` for desktop**: only if serial/USB/HID/COM access detected (`SerialPort`, `WebUSB`, `node-hid`, `libusb`, `IO.Ports`).
4. **`update-channel`**: only if an auto-update mechanism is present (`electron-updater`, `Squirrel`, `Sparkle`, custom downloader, App Store/Play Store flag is N/A since OS handles signing).
5. **`physical-attack-surface`**: only if the app runs in kiosk mode / on physically accessible public device (markers from recon: "kiosk", "POS", "ATM", "self-service").

## Cost control — focus-area clustering for Quick scans

Spawning 8–9 parallel agents per Quick scan is reasonable, but if you want to reduce parallelism for small codebases (<500 LOC), cluster:

- **cluster-input** = `injection` + `input-validation` (overlap heavy)
- **cluster-secrets** = `secrets` + `crypto` (often co-located)
- **cluster-authz** = `auth` + `access-control` (always go together)
- **cluster-deps** = `deps` (standalone, runs scanner CLIs)
- **cluster-ui** = `web-frontend` (only for web)
- **cluster-rt** = `realtime-transport` (only if applicable)

Default: one agent per focus area (no clustering). Cluster only when explicitly asked or when codebase is tiny.

## Adding a new focus area

To extend the matrix:
1. Add a row to the table above with classes Q/D/—.
2. Add a checklist section in `.claude/agents/security-auditor.md` and `agents/security-auditor.md`.
3. If conditional, add a numbered note above.
4. (Optional) add a stack-specific deep-dive in `references/stacks/`.

## Re-checking when a class change is plausible

If the codebase ambiguously straddles two classes (e.g., a Rails app being migrated to API-only), run **both** column unions:
- `web-fullstack ∪ web-backend` → run all areas that appear in either column.
- `thick-backend ∪ desktop` → covers an Electron-fronted kiosk like some POS systems.
