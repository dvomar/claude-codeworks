# Stack checklist: library

Stack-specific deep-dive items. Subagents pull from here when `app_class = library`. Generic focus-area checklists are in `agents/security-auditor.md`; this file lists patterns that **only** make sense for a published library or SDK with no entry-point app.

## Frameworks covered

npm packages, Python packages (PyPI), Go modules, Rust crates, NuGet packages, Maven/Gradle artifacts, RubyGems, Composer packages.

## The one thing to get right

A library has **no runtime of its own — it inherits every caller's.** So there are only two kinds of finding: (1) the library mishandles input its callers will inevitably pass, and (2) the library's *defaults and API shape* lead correct-looking caller code into a hole. The second kind is the one everyone misses and it is usually the more valuable finding: an unsafe default ships the vulnerability to every consumer at once.

Also audit the **release pipeline**, not just the code. A compromised publish step is worse than any bug in the source.

## API-design issues (highest value here)

- **Unsafe default** — TLS verification off by default, `strict: false`, HTML escaping opt-in rather than opt-out, a permissive CORS/`Origin` default, deserialization of arbitrary types enabled. Secure-by-default with an explicit opt-out is the standard.
- **A footgun that looks fine at the call site** — a `render(template, data)` that auto-trusts `data`, an `exec(cmd)` convenience that shells out, or a `parse(input, { allowFunctions: true })` default.
- **Silent failure instead of an error** — signature verification that returns `false` where callers expect a throw, so `verify(...)` used in an `if`-less statement passes. Prefer throwing, or return a type callers cannot ignore.
- **Ambiguous types in a security-relevant argument** — accepting either a string or an object for a key/URL/path, so a caller's type confusion becomes an injection.
- **No way to do the safe thing** — no parameterized query API, no path-scoping option, no timeout parameter. Absence of the safe API is a finding.
- **Security fix released as a patch with no advisory** — consumers never learn to upgrade. Check `CHANGELOG`/releases for silent fixes.
- **Deprecated-but-exported unsafe helpers** still reachable from the public surface.

## Input-handling issues

- **ReDoS in a public regex** — any regex applied to caller-supplied strings with nested quantifiers (`(a+)+`, `(.*)*`, alternation with overlap). Libraries are the top source of real ReDoS because the input is always attacker-adjacent.
- **Prototype pollution** (JS) — a deep-merge, `set(obj, path, val)`, or query/config parser that writes `__proto__`, `constructor`, or `prototype` keys. Check every recursive assignment helper.
- **Path traversal in a path helper** — `resolve(base, userPath)` without canonicalizing and re-checking the prefix; and on Windows also drive-relative (`C:foo`) and UNC paths.
- **Insecure deserialization exposed as a feature** — `pickle`, `yaml.load`, `Marshal.load`, `ObjectInputStream`, `BinaryFormatter`, Jackson default typing. If the library must deserialize, restrict allowed types.
- **XML parsing with external entities enabled** → XXE. Check the parser configuration explicitly; several stdlibs default to unsafe.
- **Zip/tar extraction helpers** — Zip Slip, absolute paths, symlink members, decompression bombs, and no size/entry cap.
- **Integer/allocation limits** — a length prefix from input used to preallocate → memory exhaustion.
- **SSRF in an HTTP helper** — follows redirects by default across schemes/hosts, no way to pin or block link-local addresses.
- **Unicode/normalization pitfalls** in comparison or validation helpers (case-folding, homoglyphs, `NFKC` before vs after a check).

## Crypto-specific (if the library does any)

- **Non-constant-time comparison** of MACs, tokens, or password hashes — `==` instead of `hmac.compare_digest` / `crypto.timingSafeEqual` / `subtle.ConstantTimeCompare`.
- **IV/nonce reuse** — a fixed IV, or a counter that resets; and no guard against caller-supplied nonce reuse.
- **ECB mode, or CBC without a MAC** (encrypt-then-MAC or an AEAD is the answer).
- **Weak KDF for passwords** — a single SHA-256 round instead of Argon2/scrypt/bcrypt/PBKDF2 with a sane cost.
- **`Math.random()` / `rand()` for tokens, salts, or IDs** — must be a CSPRNG.
- **Rolling your own primitive** at all — flag it and say so plainly.

## Supply-chain and packaging

- **`postinstall` / `prepare` / `setup.py` executing at install time** — any network fetch or shell here runs on every consumer's machine and in their CI. This is the highest-severity packaging finding.
- **Secrets in the published artifact** — check what the package *actually ships*: `npm pack --dry-run`, `python -m build` + inspect the sdist, `dotnet pack`. A `.env`, `.npmrc`, private key, or CI token in the tarball is a live credential leak even if `.gitignore`d.
- **Missing `files`/`MANIFEST.in` allowlist** → the whole working tree ships, including `.git`, fixtures, and local config.
- **Publish workflow using a long-lived token** rather than trusted publishing/OIDC; and a release workflow triggerable by `pull_request_target` or with `permissions: write-all`.
- **Unpinned CI actions/images** (`uses: some/action@main`) in the release job.
- **Dependency hygiene** — no lockfile for the dev/publish path, dependencies pinned to floating ranges for security-relevant packages, abandoned transitive deps. Run the dep scanner (`references/dep-scanners.md`).
- **Typosquat/confusion surface** — an internal package name resolvable from a public registry (dependency confusion), or a scope that is unclaimed.
- **No provenance/signing** — no Sigstore attestation, no signed tags, no `--provenance` on publish.
- **`.npmrc`/`pip.conf` committed** with a registry token, even a read-only one.

## Common false positives in library

- "No authentication/authorization" — a library has no session; that is the caller's job unless the library ships an auth primitive.
- "No rate limiting", "no CSRF protection", "no CSP" — not a library's layer.
- Unsafe function *offered deliberately* with a clear name and documented warning (`execUnsafe`, `renderRaw`, `parseUntrusted`) where a safe default also exists. Note it; do not rank it high.
- Weak hashing used for cache keys, ETags, sharding, or deduplication rather than integrity.
- `eval`/`new Function` in a benchmark, codegen step, or build script that never ships in the package.
- Test fixtures containing keys, certificates, or passwords — verify they are excluded from the published artifact, then dismiss.
- Vulnerable **dev** dependency with no runtime path — report separately and at low severity.
