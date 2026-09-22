# Dependency scanners by stack

The `deps` focus area agent picks scanners based on detected stack. **Read-only invocations only.** Never run `--fix`, never install dependencies.

## Universal (try first — works across stacks)

| Tool | Install | Command | Output |
|---|---|---|---|
| **osv-scanner** | `brew install osv-scanner` / [GitHub release](https://github.com/google/osv-scanner) | `osv-scanner --recursive --format=json .` | JSON; covers most ecosystems |
| **trivy** | `brew install aquasecurity/trivy/trivy` | `trivy fs --scanners=vuln,secret,misconfig --format=json --quiet .` | JSON; also catches secrets + IaC misconfigs |
| **semgrep** | `pip install semgrep` / `brew install semgrep` | `semgrep --config=auto --json --quiet --error .` | JSON; SAST rules across many languages |
| **gitleaks** | `brew install gitleaks` | `gitleaks detect --no-banner --format=json --source=.` | JSON; secret scanning |
| **trufflehog** | `brew install trufflehog` | `trufflehog filesystem . --json --no-update` | JSON; deeper secret scan |

## Per-stack ecosystem scanners

### Node.js / JavaScript / TypeScript

| Tool | Command |
|---|---|
| `npm audit` | `npm audit --json` (in dir with `package.json` + lockfile) |
| `yarn audit` | `yarn npm audit --json` (Berry) or `yarn audit --json` (Classic) |
| `pnpm audit` | `pnpm audit --json` |
| `bun audit` | not available as of 2026-05; use osv-scanner |
| `npm outdated` | `npm outdated --json` (not a vuln scanner, but signals abandoned deps) |

### .NET / C# / F#

| Tool | Command |
|---|---|
| `dotnet list package --vulnerable` | `dotnet list package --vulnerable --include-transitive --format json` (requires `dotnet restore` first) |
| `dotnet list package --deprecated` | `dotnet list package --deprecated --include-transitive --format json` |
| **NuGetDefense** (Roslyn analyzer) | runs at build time; check `*.csproj` for `<PackageReference Include="NuGetDefense">` |

### Python

| Tool | Command |
|---|---|
| `pip-audit` | `pip-audit --format=json` (works with `requirements.txt` or installed env) |
| `safety` | `safety check --json` |
| `bandit` | `bandit -r . -f json` (SAST, not deps) |

### Ruby

| Tool | Command |
|---|---|
| `bundle-audit` | `bundle audit check --update --format=json` |
| `brakeman` | `brakeman --format=json --quiet` (Rails SAST) |

### Go

| Tool | Command |
|---|---|
| `govulncheck` | `govulncheck -json ./...` |
| `nancy` | `go list -json -m all \| nancy sleuth -o json` |

### Rust

| Tool | Command |
|---|---|
| `cargo audit` | `cargo audit --json` |
| `cargo deny` | `cargo deny check --format=json` |

### Java / Kotlin / Scala

| Tool | Command |
|---|---|
| `mvn dependency-check` | `mvn org.owasp:dependency-check-maven:check -DfailBuildOnCVSS=0` (slow first run, downloads NVD) |
| `gradle dependencyCheckAnalyze` | with `org.owasp.dependencycheck` plugin |
| OWASP DC standalone | `dependency-check.sh --project P --scan . --format JSON` |

### PHP

| Tool | Command |
|---|---|
| `composer audit` | `composer audit --format=json` |
| `local-php-security-checker` | `local-php-security-checker --format=json` |

### Swift / iOS

| Tool | Command |
|---|---|
| SwiftPM | no built-in vuln scanner; use `osv-scanner` on `Package.resolved` |
| CocoaPods | `pod audit` (community plugin) or `osv-scanner` |

### Flutter / Dart

| Tool | Command |
|---|---|
| `dart pub outdated` | `dart pub outdated --json` (not a vuln scanner; signals stale deps) |
| osv-scanner | works on `pubspec.lock` |

### Elixir

| Tool | Command |
|---|---|
| `mix deps.audit` | community tool |
| `mix hex.audit` | built-in for retirement notices |

### Container images / IaC

| Tool | Command |
|---|---|
| `trivy image` | `trivy image --format=json <image>:<tag>` |
| `trivy config` | `trivy config --format=json .` (Dockerfile, K8s, Terraform) |
| `hadolint` | `hadolint --format=json Dockerfile` |
| `checkov` | `checkov -d . --output=json` (IaC) |
| `kube-score` | `kube-score score *.yaml --output-format=json` |

## Scanner output triage

For each scanner result, the agent must:
1. Filter to `severity >= medium` (Quick) or all (Deep).
2. **Deduplicate** by `(package_name, vulnerable_version_range, CVE)`.
3. Check **reachability** — is the vulnerable function actually called? If you can grep-confirm it's unused, demote one level and note it.
4. Note **fix path**: minimum upgrade version, or workaround if no fix.
5. Emit one finding per package-CVE (not per scanner-line — scanners often duplicate across transitive paths).

## When no scanner is available

Static heuristics — agent should:
1. Read manifest + lockfile.
2. Compare package names against a small **known-risky list** (you can inline: `lodash<4.17.21`, `axios<1.6.0`, `Newtonsoft.Json<13.0.1`, etc.).
3. Note in `limitations[]` that scanner was unavailable and CVE coverage is partial.
4. Flag suspicious patterns: very recently published (typosquat risk), maintainer changed recently, post-install scripts present.

## False-positive rules for deps

- Dev-only deps (`devDependencies`, `<PackageReference IncludeAssets="..." />` with build-only assets, `[dev-dependencies]` in Cargo, `group :development` in Gemfile): only flag if CVE allows build-time code exec / supply chain.
- Test fixtures: never flag.
- Vendored libs we don't touch: note as "vendored — out of scope" and skip.
