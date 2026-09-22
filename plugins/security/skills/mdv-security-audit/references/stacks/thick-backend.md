# Stack checklist: thick-backend

Stack-specific deep-dive items. Subagents pull from here when `app_class = thick-backend`. Generic focus-area checklists are in `agents/security-auditor.md`; this file lists patterns that **only** make sense for a long-running backend serving a single host — kiosk, embedded controller, on-prem appliance.

## Frameworks covered

ASP.NET Core with SignalR, .NET Worker Services / Windows Services, Node daemons with `ws`/`socket.io`, Python `asyncio`/`aiohttp` daemons, gRPC servers, MQTT clients/brokers, Qt/C++ services, systemd units.

## The one thing to get right

The threat model inverts. There is usually **no hostile internet and no multi-tenancy** — instead there is a person standing in front of the machine, and an operator LAN that is not trustworthy. So the findings that matter are: unauthenticated local transport, trust in "it only binds to localhost", secrets at rest on a device someone can open, and the update path. Web-app findings (XSS, CSRF, CSP) mostly do **not** apply — do not pad the report with them.

## Framework-specific issues

### SignalR

- **Hub methods are public API** — every `public` method on a `Hub` is callable by any connected client. `[Authorize]` on the hub class does not cover a method that has its own attribute, and no attribute at all means anonymous.
- **No auth on the hub at all** — common when "only our own UI connects". Anything on the host or LAN can connect.
- **`Clients.All.SendAsync` broadcasting per-client data** — verify group/user scoping (`Clients.User`, `Clients.Group`) instead of broadcast-and-filter-in-client.
- **Group membership never revoked** — `RemoveFromGroupAsync` missing on state change, so a client keeps receiving after losing the role.
- **`MaximumReceiveMessageSize` raised or disabled** → memory DoS from one local client.
- **Detailed errors enabled** (`EnableDetailedErrors = true`) → stack traces to clients.
- **Sticky assumptions with a single instance** — fine here, but note if a scale-out backplane (Redis) is configured with no auth.

### Raw WebSocket / socket.io

- **No handshake authentication** — token/cookie checked only on the HTTP page, not on the socket upgrade.
- **Missing origin check on upgrade** — a browser on the same host can connect from any page (cross-site WebSocket hijacking); `ws` does not check `Origin` for you.
- **No per-message authorization** — the socket authenticates once, then every message is trusted, including one that changes another entity.
- **No message size / rate cap** per connection.

### gRPC

- **Server with `ChannelCredentials.Insecure` / no TLS** on a non-loopback bind.
- **No interceptor for auth** — per-method authorization missing.
- **Reflection service enabled** in production, exposing the full schema.
- **Unbounded `MaxReceiveMessageSize`** and no deadline enforcement.

### MQTT

- **Anonymous broker access** (`allow_anonymous true`) or a shared static credential in the repo.
- **Wildcard subscriptions permitted** (`#`) letting any device read every topic.
- **No TLS on the broker link**, or `insecure_skip_verify` in the client.
- **Command topics without an authorization model** — any publisher can actuate hardware.

### .NET Worker / Windows Service

- **Service account is LocalSystem** when a constrained account would do.
- **Service binary path unquoted** with spaces → unquoted service path privilege escalation.
- **Writable install directory** — a non-admin user replacing the DLL/EXE gets code execution as the service account.
- **`Process.Start` with a relative executable name** → PATH hijack.

## Cross-cutting for this class

- **Bind address vs. reality** — `localhost`/`127.0.0.1` is a real boundary; `0.0.0.0` is not. Grep every listener and every `appsettings*.json` / `--urls` / compose port mapping. A dev override that publishes the port is the finding, even if code says loopback.
- **"It's on our LAN" as the only control** — state it explicitly as an assumption in the report, then check what breaks if the LAN is hostile (it usually is: shared VLAN, technician laptop, a second kiosk).
- **Secrets at rest on a physical device** — connection strings, API keys, device certificates in plaintext config. On Windows check for DPAPI/CNG usage; on Linux, file mode and whether the disk is encrypted. Assume the attacker can pull the drive.
- **Local admin/diagnostic endpoints** — a `/debug`, `/status`, or telnet-ish maintenance port with no auth.
- **Update / deployment path** — is the package signature verified before install? Is the update fetched over TLS with cert validation? An unsigned auto-update is the highest-severity finding in this class: it converts LAN access into persistent code execution.
- **Hardware I/O trust** (`hardware-io` focus area) — data from a bill validator, card reader, scanner, or PLC is *input*. Check length/type validation before parsing, and behavior on malformed frames. A device can be swapped or spoofed.
- **Physical attack surface** (`physical-attack-surface`) — exposed USB ports (HID injection, mass storage autorun), accessible serial/JTAG headers, kiosk-mode escape (dialogs, print, file pickers, `Ctrl+O`), unlocked BIOS/boot order, recovery partitions.
- **Native IPC** (`native-ipc`) — named pipes with a null/permissive DACL, Unix sockets with mode `0777`, shared memory without ACL, D-Bus methods without policy. These are the local privilege-escalation path.
- **Local database credentials** — SQL Server/PostgreSQL/SQLite on the same host; check for a blank/default password and whether the DB port is exposed beyond loopback.
- **Logging sensitive data** — PAN/track data, PII, full request bodies written to disk with no rotation or restrictive mode. Logs on a kiosk are physically retrievable.
- **Watchdog / restart loop as a control** — verify a crash cannot leave the machine in an open state (cash door, gate, unlocked session).
- **Time and offline behavior** — expired cert or clock skew causing fail-open; queued transactions replayed without idempotency after reconnect.

## Common false positives in thick-backend

- Missing CSRF/CSP/XSS hardening where there is no browser-rendered UI at all.
- Missing rate limiting on a loopback-only endpoint with a single trusted local client.
- Missing TLS on a genuine loopback bind (verify it really is loopback, then dismiss).
- "Hardcoded credential" that is a device-provisioning default overwritten at install — confirm the install path actually rotates it before dismissing.
- HTTP between two containers on an internal compose network with no published port.
- Permissive CORS on a service no browser ever calls.
