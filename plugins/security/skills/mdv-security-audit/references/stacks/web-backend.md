# Stack checklist: web-backend

Stack-specific deep-dive items. Subagents pull from here when `app_class = web-backend`. Generic focus-area checklists are in `agents/security-auditor.md`; this file lists patterns that **only** make sense for an HTTP/REST/GraphQL API with no UI of its own.

## Frameworks covered

Express, Fastify, NestJS, Koa, Hapi, FastAPI, Flask, Django REST Framework, Rails API, Laravel API, Spring Boot, ASP.NET Web API, Go `net/http` / Chi / Gin, Axum / Actix.

## The one thing to get right

With no UI, **every route is the attack surface and authorization is per-object, not per-route.** The highest-yield sweep is: enumerate every route, and for each one ask (a) who may call it, (b) which record does it touch, and (c) is the caller's ownership of *that* record checked. Missing (c) is IDOR and it is the most common real finding in this class.

## Framework-specific issues

### Express / Koa / Fastify

- **Middleware order** — `app.use(auth)` registered *after* a route means that route is public. Read the file top-to-bottom; order is the control.
- **`app.use(express.json({ limit }))` absent** → unbounded body → memory DoS. Default in Express is 100kb, but `body-parser` raw/text often set higher.
- **Route params straight into a query** — `req.params.id` into `knex.raw`, `sequelize.query`, `mongo.find({$where})`.
- **`req.query` object/array confusion** — `?id[$ne]=1` arrives as an object; a Mongo query built from it becomes an operator injection. Validate types, not just presence.
- **`trust proxy` unset while rate-limiting on IP** — every request looks like the proxy's IP, so the limit is global; or set to `true` blindly, letting a client spoof `X-Forwarded-For`.
- **Error handler leaking `err.stack`** in the JSON response.
- **`cors({ origin: true })` with `credentials: true`** — reflects any origin and allows cookies. That is a full CSRF/read primitive.

### NestJS

- **Guard applied at controller but not on a sub-route** with its own decorator.
- **`ValidationPipe` without `whitelist: true` / `forbidNonWhitelisted`** → mass assignment through extra DTO fields.
- **`@Param('id')` used without an ownership check in the service layer** — the classic IDOR shape here.

### FastAPI / Flask / DRF

- **FastAPI `Depends(get_current_user)` missing on a router** — check `include_router(..., dependencies=…)` vs per-endpoint.
- **Pydantic model reused for input and output** — an internal field (`is_admin`, `password_hash`) becomes both settable and readable.
- **DRF `permission_classes` defaulting to `AllowAny`** via `DEFAULT_PERMISSION_CLASSES`; and `queryset` not filtered by `request.user` → object-level leak.
- **Flask `debug=True`** → Werkzeug console = RCE.
- **SQLAlchemy `text()` / `.filter(text(f"..."))` with interpolation** → SQLi.

### Spring Boot

- **`permitAll()` / `.anyRequest().permitAll()`** in the security config.
- **CSRF disabled globally** — acceptable for a stateless token API, a finding if session cookies are used.
- **`@PreAuthorize` on the interface but not the implementation**, or absent on a new method.
- **Actuator endpoints exposed** — `/actuator/env`, `/heapdump`, `/mappings` unauthenticated.
- **Jackson polymorphic typing (`enableDefaultTyping`, `@JsonTypeInfo`)** → deserialization RCE.

### ASP.NET Web API

- **`[Authorize]` missing** on a controller/action, or `[AllowAnonymous]` left from debugging.
- **Model binding overposting** — bind to a DTO, not the EF entity.
- **`FromSqlRaw` with interpolation** → SQLi (`FromSqlInterpolated` is the safe one).
- **`BinaryFormatter` / `NetDataContractSerializer`** → deserialization RCE.

### Go

- **`http.ServeMux` path prefix matching** — `/admin/` pattern does not protect `/admin` and vice versa.
- **Middleware wrapping only some routes** — verify the chain per registration.
- **`fmt.Sprintf` into SQL** → SQLi; `database/sql` placeholders are the fix.

## Cross-framework

- **Route inventory vs authorization matrix** — build the table. Every row without an explicit rule is a finding.
- **IDOR / object-level authz** — `WHERE id = ?` must also carry `AND owner_id = current_user`. Check list endpoints too: filtering in the client is not filtering.
- **JWT validation** — is `alg` pinned? Is `none` rejected? Is the signature actually verified (`decode` vs `verify`)? Are `exp`, `aud`, `iss` checked? Is the key fetched from a JWKS URL that the token itself controls (`jku`/`kid` traversal)?
- **Mass assignment** — allowlist on input DTOs everywhere, especially `PATCH`.
- **Rate limiting and lockout** on auth, password reset, OTP, and any expensive endpoint. Absent limiter = credential stuffing + enumeration.
- **User enumeration** — differing responses/timing for "unknown email" vs "wrong password", and on registration and reset.
- **SSRF** — any endpoint fetching a user-supplied URL (webhooks, image import, PDF render, oEmbed). Check for allowlist, and for the cloud metadata endpoint (`169.254.169.254`) plus redirect-following and DNS rebinding.
- **Webhook receivers without signature verification** — Stripe/GitHub/Slack style HMAC must be verified against the **raw** body before JSON parsing, in constant time.
- **GraphQL** — introspection in prod, no depth/complexity limit, batching amplification, per-field authz missing, error messages leaking the schema.
- **Pagination without an upper bound** — `?limit=1000000` as a cheap DoS.
- **Mongo/NoSQL operator injection** — `$where`, `$regex` from user input; and `$ne`/`$gt` via query-string type coercion.
- **File upload** — content-type sniffed vs trusted, extension allowlist, size cap, path traversal in filename, storage outside webroot, and no execution bit.
- **Verbose errors and stack traces** in non-dev environments; `X-Powered-By` / `Server` version banners.
- **Secrets in env dumps** — a `/debug`, `/config`, or `/health` route echoing configuration.
- **CORS** — reflected origin, `*` with credentials, or an allowlist matched by `startsWith` (`evil-myapp.com` passes a `myapp.com` prefix test).

## Common false positives in web-backend

- Missing CSRF protection on a stateless bearer-token API that never reads cookies.
- Raw SQL built entirely from literals and enum values with no user-controlled substring.
- "Hardcoded secret" in `conftest.py`, fixtures, `docker-compose.yml` for local dev, or `.env.example`.
- Permissive CORS in a config branch guarded by `if ENV == "development"`.
- `AllowAnonymous` on genuinely public endpoints — health checks, OpenAPI docs, login, webhook receivers (which authenticate by signature instead).
- Missing rate limit at the app layer when an API gateway/WAF in front provides it — confirm it exists before dismissing.
