# Stack checklist: web-fullstack

Stack-specific deep-dive items. Subagents pull from here when `app_class = web-fullstack`. Generic focus-area checklists are in `agents/security-auditor.md`; this file lists patterns that **only** make sense for fullstack web frameworks.

## Frameworks covered

Next.js (App / Pages router), Nuxt 3, SvelteKit, Remix, Rails, Django, Laravel, Phoenix, ASP.NET MVC + Razor Pages.

## Framework-specific issues

### Next.js (App Router)

- **Server actions reachable by anyone** — `'use server'` functions are callable by any client. Verify auth check **inside** the action body, not just on the page that calls it.
- **Middleware bypass via specific paths** — `matcher` config in `middleware.ts` skips internal Next paths (`/_next`, `/api/auth`). Verify the matcher covers all your protected routes.
- **`searchParams` are tainted** — any prop derived from URL is attacker-controlled. Watch for raw embedding in `dangerouslySetInnerHTML`.
- **`getServerSession` / `auth()` returning null** — make sure all sensitive server components handle null session by redirect/throw, not silent fall-through.
- **Route handler `GET` doing mutations** — CSRF-prone; should be `POST`.
- **`revalidatePath` / `revalidateTag` exposed via params** — attacker can DoS your cache.
- **`unstable_cache` with user input in key** — cache poisoning.
- **`Image` component with user-supplied src** — SSRF through image optimization endpoint.

### Next.js (Pages Router)

- **`getServerSideProps` with `params` / `query` injected into DB without sanitization** — SQLi / NoSQLi.
- **`/api/*` routes lack default rate limiting** — Next doesn't ship one.
- **`req.headers.host` trust** — used for absolute URL construction; X-Forwarded-Host attacks if behind proxy without `trust proxy`.

### Nuxt 3

- **`useState` server/client mismatch** — sensitive data leaked to client via SSR payload.
- **`runtimeConfig.public` exposed to client** — any secret accidentally placed there is public.
- **Server routes (`server/api/`) lack auth middleware by default**.

### SvelteKit

- **`load` functions run on both server and client** — server-only data goes in `+page.server.ts`. Mixing leaks.
- **`form actions` need CSRF** — SvelteKit does provide CSRF, verify `csrf.checkOrigin` is not disabled.
- **`PUBLIC_*` env vars are inlined into bundle** — never put secrets there.

### Remix

- **`loader` data is sent to browser** — sensitive fields must be stripped before return.
- **`action` functions need explicit auth**; no implicit guard.
- **`useFetcher().submit` lacks CSRF protection** unless you opt-in.

### Rails

- **Strong parameters bypass via mass assignment** — `params.permit(:everything)` or absent.
- **Brakeman warnings not addressed** — run `brakeman` and triage.
- **`raw`, `html_safe`, `<%==` with user input** → XSS.
- **`find_by_sql`, `where(string)` with interpolation** → SQLi.
- **Default Devise config** — missing `paranoid: true`, no email enumeration protection.
- **Mass-assignment in `update` / `create` without permit**.
- **Open redirect via `redirect_to params[:url]`**.

### Django

- **`raw()`, `extra()`, `cursor.execute("..." % param)`** → SQLi.
- **`mark_safe` / `|safe` with user content** → XSS.
- **`DEBUG=True` in prod** → secrets/stack traces.
- **`ALLOWED_HOSTS=['*']`** → host header attacks.
- **CSRF exempt views** — count them.
- **Custom user model without proper password validators**.
- **`@login_required` missing on sensitive views** — also check `@permission_required`.
- **Pickle deserialization in cache backend**.

### Laravel

- **`DB::raw` with user input** → SQLi.
- **`{!! $x !!}` Blade unescaped** → XSS.
- **Mass assignment without `$fillable` / `$guarded`**.
- **CSRF disabled via `VerifyCsrfToken::except`**.
- **`APP_DEBUG=true` in prod** → secrets in error pages.
- **`Storage::disk('local')->put($user_path, …)`** — path traversal.
- **`Hash::check` vs `==`** — verify constant-time.

### Phoenix (Elixir)

- **`raw/1` in EEx templates** with user data → XSS.
- **`Ecto.Adapters.SQL.query!` with interpolation** → SQLi.
- **CSRF protection disabled in router**.
- **LiveView events accept any params** — handle invalid types explicitly.

### ASP.NET MVC / Razor Pages

- **`@Html.Raw(model.Untrusted)`** → XSS.
- **`SqlCommand` with concatenated strings** → SQLi (use parameterized).
- **Anti-forgery token missing** on POST actions — `[ValidateAntiForgeryToken]` or global filter.
- **`[AllowAnonymous]` on controllers that should require auth**.
- **Model binding without `[Bind]` allowlist** → mass assignment.
- **Custom `RouteHandler` writing to response without encoding**.
- **`Server.Transfer` / `Response.Redirect` with user-supplied URL** → open redirect.

## Cross-framework

- **Server-side render leaks** — any `props`/`data` returned from server includes secrets. Diff what's serialized.
- **API routes shared with backend module** — verify auth is consistently applied.
- **GraphQL** (if applicable): introspection enabled in prod, no query depth/complexity limit, missing per-field authz.
- **Reverse proxy headers** — `X-Forwarded-For`, `X-Real-IP` trusted without proxy allowlist.
- **CSP** — present? `nonce`-based vs `unsafe-inline`?
- **HSTS** — `Strict-Transport-Security` header set with adequate max-age + `includeSubDomains`?
- **Cookie flags** — `HttpOnly`, `Secure`, `SameSite=Lax|Strict` for session cookies.

## Common false positives in fullstack web

- `dangerouslySetInnerHTML` with sanitized HTML (DOMPurify, sanitize-html called immediately before).
- `eval` in webpack runtime, framework internals, build tools.
- `Math.random()` for cosmetic / non-security uses.
- "Hardcoded password" in test fixtures, `.env.example`, README examples.
