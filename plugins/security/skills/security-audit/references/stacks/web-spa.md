# Stack checklist: web-spa

Stack-specific deep-dive items. Subagents pull from here when `app_class = web-spa`. Generic focus-area checklists are in `agents/security-auditor.md`; this file lists patterns that **only** make sense for a pure client app with no backend in this repo.

## Frameworks covered

React (Vite / CRA), Vue 3, Svelte, Angular, SolidJS, Astro (static output), Ember.

## The one thing to get right

A SPA ships to the attacker's machine. **Nothing in the bundle is a secret and no client-side check is a control.** Most real findings here are one of two things: a secret that should never have been shipped, or a server-side control that only exists in the client. Report the missing server-side check as the finding — "hidden the button" is not authorization.

## Framework-specific issues

### React

- **`dangerouslySetInnerHTML` with any non-literal** → XSS. Sanitizer must run immediately before, in the same expression.
- **`href={userValue}`** → `javascript:` URI XSS. React does not block it on `a.href`.
- **`useEffect` fetch without abort** — not security, but auth-state races: a stale response can repopulate a view after logout.
- **Secrets via `import.meta.env.VITE_*` / `REACT_APP_*`** — both are inlined into the bundle at build time. Any name here is public.
- **`localStorage` for JWT/refresh tokens** — readable by any XSS. Prefer `HttpOnly` cookies set by the API.
- **Client-side route guards only** (`<PrivateRoute>`) — verify the API enforces the same rule; the route guard is cosmetic.

### Vue 3

- **`v-html` with user content** → XSS.
- **`:href` / `:src` bound to user value** → `javascript:` and `data:` URIs.
- **`runtimeConfig.public` / `VITE_*`** — client-visible by definition.
- **Template compilation from a runtime string** (`compile()` on user input) → arbitrary expression execution.

### Angular

- **`bypassSecurityTrustHtml` / `TrustUrl` / `TrustScript`** — every call is a deliberate hole; each needs justification.
- **`[innerHTML]` with untrusted value** — Angular sanitizes, but `bypassSecurityTrust*` defeats it.
- **JIT template compilation on user input** → expression injection.
- **`HttpClient` interceptor attaching the token to every origin** — leaks the bearer to third-party hosts. Scope by URL allowlist.

### Svelte

- **`{@html userValue}`** → XSS.
- **`PUBLIC_*` env vars inlined into the bundle** — never secrets.

## Cross-framework

- **Secrets in the bundle** — grep the built output, not just source: `grep -rE '(api[_-]?key|secret|token|password|Bearer )' dist/`. Findings in `dist/` are shipped, and a build artifact committed to the repo is already public.
- **Source maps published to production** — `dist/**/*.map` reveals original source and often comments/credentials. Check the deploy config, not just local build.
- **Token storage** — `localStorage`/`sessionStorage` are XSS-readable; in-memory + `HttpOnly` refresh cookie is the safe shape. Also check whether the token is written to a cookie without `Secure`.
- **OAuth/OIDC implicit flow, or auth code without PKCE** — a public client must use authorization code + PKCE. An `client_secret` in a SPA is a finding regardless of flow.
- **`postMessage` handlers without an `origin` check** — `window.addEventListener('message', …)` that never compares `event.origin` accepts messages from any embedding page.
- **CORS misread as a control** — the SPA cannot enforce anything with CORS; if the repo contains a dev proxy that adds `Access-Control-Allow-Origin: *`, verify it is not shipped.
- **`target="_blank"` without `rel="noopener"`** — reverse tabnabbing (minor, but real on older browsers).
- **Third-party script tags / tag managers** — any injected script runs with full DOM access; check for SRI (`integrity`) on CDN `<script>`/`<link>`.
- **CSP delivered by the host** — a static SPA usually has none. Check `_headers`, `vercel.json`, `netlify.toml`, `nginx.conf`, or the meta tag.
- **Dependency surface** — SPAs pull huge trees; run the dep scanner (see `references/dep-scanners.md`) and check `postinstall` scripts in `package.json`.
- **Prototype pollution in client state** — deep-merge helpers (`lodash.merge`, hand-rolled `assign`) applied to `JSON.parse` of a URL param or `postMessage` payload.
- **Client-side redirect from a query param** — `location.href = params.get('next')` → open redirect and `javascript:` execution.

## Common false positives in web-spa

- `dangerouslySetInnerHTML` / `v-html` / `{@html}` fed by a sanitizer (DOMPurify, sanitize-html) called immediately before.
- "Hardcoded key" that is a **publishable** key by design — Stripe `pk_*`, Supabase anon key, Firebase web config, Sentry public DSN, Google Maps browser key. These are meant to ship; the real question is whether the *server* enforces scope (RLS, key restrictions). Report that instead, if it is missing.
- `eval` inside webpack/Vite runtime, framework internals, or a bundled polyfill.
- `Math.random()` for keys, animation, or cache-busting.
- Missing CSRF token — irrelevant for a token-in-header SPA calling a cookie-less API.
- Missing `HttpOnly` on a cookie the SPA never uses for auth (locale, theme).
