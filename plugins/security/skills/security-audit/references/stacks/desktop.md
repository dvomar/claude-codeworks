# Stack checklist: desktop

Stack-specific deep-dive items. Subagents pull from here when `app_class = desktop`. Generic focus-area checklists are in `agents/security-auditor.md`; this file lists patterns that **only** make sense for a GUI app running on the user's own machine.

## Frameworks covered

Electron, Tauri, WPF, WinForms, MAUI, Qt, GTK, Swing/JavaFX, Avalonia, Flutter desktop.

## The one thing to get right

The user already owns the machine, so "user can read the binary" is not a finding. What matters is **whether remote content can reach native capability**, and whether the app weakens the machine for its own user (bad ACLs, unsigned updates, a local port, a custom URI scheme). Rank by "what does a malicious web page or a same-machine low-priv process get".

## Framework-specific issues

### Electron

- **`nodeIntegration: true`** with any remote or user-influenced content → straight to RCE. The finding is the combination; note which window loads what.
- **`contextIsolation: false`** — preload and page share a realm, so prototype tampering from the page reaches privileged code. Must be `true` (default since v12; check for an explicit downgrade).
- **`sandbox: false`** on a renderer showing untrusted content.
- **`webSecurity: false`** — disables same-origin policy entirely.
- **Overbroad preload bridge** — `contextBridge.exposeInMainWorld('api', { invoke: (ch, ...a) => ipcRenderer.invoke(ch, ...a) })` re-exposes the whole IPC surface. The bridge must expose named, validated operations only.
- **IPC handlers without argument validation** — `ipcMain.handle('readFile', (e, p) => fs.readFile(p))` is arbitrary file read; add path normalization plus an allowlisted base directory.
- **No sender check in IPC** — validate `event.senderFrame` / `senderId` so an iframe or a second window cannot call privileged channels.
- **`shell.openExternal(userUrl)`** — `file://`, `smb://` and (on Windows) other handlers can execute. Allowlist the scheme to `https:`/`mailto:`.
- **`shell.openPath` / `child_process` with user-derived arguments** → command injection.
- **Missing `will-navigate` / `setWindowOpenHandler` guards** — the app navigates itself to arbitrary origins, and `window.open` creates unrestricted windows.
- **`allowRunningInsecureContent`, `experimentalFeatures`, `enableBlinkFeatures`** enabled.
- **Custom protocol handler registered** (`app.setAsDefaultProtocolClient`) — deeplink arguments arrive from any web page; treat them as tainted input and parse strictly. On Windows also check argument injection into the launch command.
- **ASAR is not protection** — flag secrets in the bundle, but as "shipped secret", not "obfuscation missing". Also check `asarUnpack` for native binaries with weak file permissions.
- **Auto-update without signature verification** (`electron-updater` with a self-hosted feed over HTTP, or `verifyUpdateCodeSignature` disabled) → persistent RCE.
- **Outdated Electron major** — the Chromium inside carries known CVEs; report the version and its support status.

### Tauri

- **Overbroad `allowlist` / capability set** — `fs: { all: true }`, `shell: { all: true }`, `shell.execute`, or `scope: ["**"]`. Scope each to the narrowest path/command.
- **`dangerousRemoteDomainIpcAccess`** granting IPC to a remote origin.
- **`#[tauri::command]` taking a path or command string** without canonicalization and an allowlist.
- **CSP disabled or `null`** in `tauri.conf.json`.
- **Updater `pubkey` absent or endpoint over HTTP.**

### WPF / WinForms / MAUI / Avalonia

- **Secrets in `App.config` / `appsettings.json` in plaintext** — check for DPAPI (`ProtectedData`), CNG, or a credential-manager call.
- **`Process.Start` with a concatenated argument string** → argument/command injection; use `ProcessStartInfo.ArgumentList`.
- **`XamlReader.Load` on user-supplied XAML** → object instantiation.
- **`BinaryFormatter`, `SoapFormatter`, `NetDataContractSerializer`, `LosFormatter`** → deserialization RCE.
- **Install directory under `C:\ProgramData` or a world-writable path** with the app loading DLLs from it → DLL planting/hijack.
- **Unsigned assemblies / no Authenticode signature** on the installer.
- **Embedded WebView (`WebView2`, `CefSharp`)** — `AllowExternalDrop`, host-object bridging (`AddHostObjectToScript`), and navigation to untrusted origins.
- **`ClickOnce` deployment over HTTP.**

### Qt / GTK / Java

- **`QProcess` / `Runtime.exec` with a shell string** → injection; pass an argument vector.
- **`QWebEngineView` loading remote content** with local file access or JS bridges enabled.
- **`QSettings` / `java.util.prefs` storing tokens in plaintext** (registry or `~/.config`) — check file mode.
- **Java deserialization** of untrusted bytes (`ObjectInputStream`).
- **Loading plugins/libraries from a relative or user-writable path** → hijack.

## Cross-framework

- **Local listening port** — many desktop apps open one for IPC or a companion browser extension. Any web page can reach `127.0.0.1`; require an origin check plus a per-launch token, not just "it's localhost".
- **Custom URI scheme** — the single most common desktop entry point from the web. Validate and canonicalize every parameter; never pass it into a shell, a file path, or an auto-update URL.
- **Credential storage** — is it DPAPI / Keychain / libsecret, or a plaintext file? Report the mechanism, and check the file mode when it is a file.
- **Update channel** — TLS with certificate validation, signature verified before apply, and no downgrade to an older signed version.
- **File permissions after install** — a writable app directory turns any local user into an attacker against every other user of the machine.
- **Path traversal in import/export** — archive extraction (`zip`/`tar`) without checking entries for `..` and absolute paths (Zip Slip), and symlink entries.
- **Logs and crash dumps** — tokens or PII written to `%APPDATA%`/`~/Library/Logs`, and third-party crash reporting that uploads them.
- **Bundled runtime / dependency versions** — the vendored Node, Chromium, OpenSSL, or JRE is part of your attack surface.

## Common false positives in desktop

- "Secret in the binary/ASAR" for a value that is genuinely public (telemetry DSN, publishable API key, update feed URL).
- Missing CSP/CSRF in a window that only ever loads bundled local content with `contextIsolation: true` — verify the loaded origins first.
- `nodeIntegration: true` on a window that loads a single bundled file and never navigates. Still worth a note, but not critical.
- User-writable config in the user's own profile — that is the design, not a hole.
- Hardcoded localhost ports and dev-server URLs behind an `isDev` guard.
- "Weak crypto" in a checksum used for cache invalidation, not integrity.
