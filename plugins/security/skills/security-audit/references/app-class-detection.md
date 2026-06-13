# App-class detection

The audit adapts to the **application class**. Pick exactly one (or `hybrid` if two are equally weighted). Confirm with the user in Phase 0 before scanning.

## Classes

| Class | Definition |
|---|---|
| `web-fullstack` | Server-rendered or hybrid app with both server-side routes and a frontend (Next.js with API routes, Rails, Django w/ templates, ASP.NET MVC) |
| `web-spa` | Pure client app — no own backend in this repo (React/Vue/Svelte/Angular static build, talks to remote API) |
| `web-backend` | HTTP/REST/GraphQL API with no own UI (Express API, FastAPI, ASP.NET Web API, Spring Boot REST) |
| `thick-backend` | Long-running backend for a single host: kiosk, embedded, on-prem desktop server. Often realtime transport (SignalR/WS/gRPC) instead of REST. CashMachine5 is the archetype. |
| `desktop` | GUI app running on user machines (Electron, Tauri, WPF, WinForms, Qt, GTK, Swing, JavaFX) |
| `mobile` | iOS/Android/RN/Flutter app distributed via app stores |
| `cli` | Command-line tool, script, or daemon without GUI |
| `library` | Published library/SDK consumed by other code; no entry-point app |
| `hybrid` | Repo contains two non-trivial app types (monorepo with web + mobile, etc.). Detect each separately. |

## Detection signals

Scan the **repo root + first 2 levels** for these. First strong signal wins. Resolve ties with the **deployment exposure** info from the user.

### web-fullstack
- `next.config.*` **AND** `app/` or `pages/api/` directory
- `nuxt.config.*` **AND** `server/api/` directory
- `config/routes.rb` + ERB templates (Rails)
- `manage.py` + `templates/` (Django)
- ASP.NET MVC: `*.csproj` with `Microsoft.AspNetCore.Mvc` + `Views/` directory + Controllers
- Express/Koa + EJS/Pug/Handlebars template engine + static folder
- SvelteKit `+page.server.ts` + `+page.svelte`

### web-spa
- `package.json` with `react|vue|svelte|angular|solid` **AND** no server entry (no `next.config`, no `nuxt.config`, no `server/`, no `app.js`/`server.ts`)
- Build output is static (`vite build`, `webpack` SPA config, `ng build`)
- No HTTP server registered in code

### web-backend
- Express/Fastify/Koa/NestJS with **no** template engine
- FastAPI / Flask app object with no Jinja templates
- ASP.NET Web API (`MapControllers`, no `MapRazorPages`, no `Views/`)
- Spring Boot with `@RestController` only
- Hono / Bun.serve / Deno.serve API
- Go `net/http` / chi / gin / echo
- Rails API mode (`config.api_only = true`)

### thick-backend
- ASP.NET Core with **SignalR** (`MapHub<>`) as primary transport, REST minimal/absent
- Long-running .NET service registering hardware drivers (serial/COM/USB references)
- Java service with `Spring WebFlux` / RSocket on a single host
- Custom protocol over TCP/Unix socket as primary IO
- Codebase contains hardware vendor SDKs (ITL, NMD, MEI, JCM, ccTalk, SSP protocol)
- "Kiosk" / "POS" / "ATM" / "embedded" in README or project name
- `EnabledDevices` / similar runtime device list in config
- Talks to local SQL Server / SQLite on the same host
- No public ingress; deployment is "ship a server to each site"

### desktop
- `electron-builder.*`, `electron/`, `main.js` with `BrowserWindow`
- `tauri.conf.json`, `src-tauri/`
- WPF: `*.csproj` with `<UseWPF>true</UseWPF>` or `.xaml` + `App.xaml`
- WinForms: `*.csproj` with `<UseWindowsForms>true</UseWindowsForms>`
- Qt: `*.pro` / `CMakeLists.txt` with `find_package(Qt)`
- GTK: `gtk-rs`, `pygobject`
- Swing/JavaFX: `javax.swing.*`, `javafx.application.Application`
- Avalonia: `<UseAvalonia>` / `Avalonia.Application`
- MAUI/Xamarin desktop

### mobile
- iOS: `Info.plist` + `*.xcodeproj/`, `Package.swift` with UIKit/SwiftUI
- Android: `AndroidManifest.xml` + `build.gradle` with `com.android.application`
- React Native: `metro.config.js`, `react-native` in `package.json`
- Flutter: `pubspec.yaml` with `flutter` sdk
- Capacitor / Cordova / Ionic mobile
- MAUI mobile

### cli
- `bin/` with executable scripts, `package.json` `"bin"` field
- Python `console_scripts` entry point, no Flask/FastAPI/Django
- Go `main` package with `flag` parsing, no HTTP server
- Rust `bin/` target with `clap` or `structopt`
- Single-file Bash/zsh script
- `oclif` / `commander` / `yargs` / `click` / `cobra` as primary framework

### library
- `package.json` with `"main"` + `"types"` + no app entry; `"private": false` or published
- `pyproject.toml` with `[project.scripts]` empty; package metadata indicates library
- `Cargo.toml` with `[lib]` and no `[[bin]]`
- `pom.xml` with `<packaging>jar</packaging>` consumed by other projects
- `*.csproj` with `<IsPackable>true</IsPackable>` and no entry-point host
- README starts with "A library for…" / "An SDK for…"

### hybrid
Two of the above with comparable size. Examples:
- Monorepo with `apps/web` (web-fullstack) + `apps/mobile` (mobile)
- Backend repo (web-backend) with bundled admin UI (web-spa)
- Thick backend (thick-backend) with a Windows tray app (desktop)

For `hybrid`, run the audit per sub-app or pick the primary class based on scope.

## Algorithm

```
1. Glob for top-level manifests (package.json, *.sln, *.csproj, pyproject.toml, Cargo.toml, pom.xml, build.gradle*, Gemfile, go.mod, composer.json, pubspec.yaml, Package.swift, mix.exs, CMakeLists.txt).
2. Read each (or first ~100 lines) — collect: framework names, dependencies, project type tags.
3. Score each class using the signals above. Strongest signal wins. Ties → use deployment exposure from the user.
4. If two classes both score ≥ 2 strong signals → "hybrid", prompt user to pick primary or to audit each separately.
5. Confirm class with the user in one sentence: "Detected: thick-backend (.NET 8 + SignalR + ITL hardware drivers). Audit as kiosk? [y/n/other]"
```

## Special markers (boost severity if present)

| Marker | Effect |
|---|---|
| Project handles money / payment / settlement / dispense / cashbox | Boost `business-logic` priority; severity floor for money math is High |
| Project is kiosk / public-facing physical device | Adds `physical-attack-surface` focus area; service-menu password severity is Critical |
| Project handles PII / health / financial data | Adds compliance overlay (GDPR/HIPAA/PCI) hints to logging-pii and access-control |
| Project is internet-exposed | Default severity assumption is "high blast radius"; weak auth = Critical |
| Project is LAN-only / air-gapped | Default severity assumption is "scoped blast radius"; weak auth = Medium/High depending on attacker model |

Capture these in `recon.json` under `markers` so the orchestrator can apply them at triage time.
