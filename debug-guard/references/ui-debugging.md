# UI debugging — browser, network, proxies, connectivity

The hardest debugging is when the bug is split across the **browser**, the **network**, a
**dev proxy**, a **reverse proxy** (nginx / traefik / cloud LB), and the **server**. Each layer
has its own visibility tools; each layer can lie about what the others did.

This is where vibe debugging burns the most time — clicking around in DevTools without a plan,
trying random proxy configs, copy-pasting CORS headers from Stack Overflow until something
works.

---

## The UI debugging mindset

Three principles. Hold them above everything else.

### 1. The Network tab is the truth

Console errors are summaries; the **Network tab has the actual data**. Before you read the
console, open Network. For every failed request, check:

- **Status code** — 200? 401? 403? **0**? (status 0 = browser blocked it before sending)
- **Method** — GET vs **OPTIONS** (preflight) vs POST
- **Request headers** — was `Authorization` actually sent? Cookies? `Content-Type`?
- **Response headers** — `Access-Control-Allow-Origin`? `Set-Cookie`? `Cache-Control`?
- **Request payload** — is the body actually what you think it is?
- **Response body** — what did the server actually return?
- **Timing** — DNS, TCP, TLS, waiting, download

90% of UI/connectivity bugs are solved by reading this carefully — but only if you actually look
at it before you start guessing.

### 2. DevTools open BEFORE the bug fires

The Network tab doesn't record what happened before you opened it (unless **"Preserve log"** +
reload). Same for Console, same for Performance. **Open DevTools first, then reproduce.**

For bugs that happen on page load: open DevTools → Network → check "Preserve log" and "Disable
cache" → reload.

### 3. Cross the wire boundary deliberately

The browser is one universe; the server is another. The wire is the single observable point
where both meet. When debugging is confusing, prove what crosses the wire in **both directions**:

| Direction              | How to verify                                  |
| ---------------------- | ---------------------------------------------- |
| What the browser sends | Network tab → request headers + payload        |
| What the server receives | Server-side log of headers + body            |
| What the server sends  | Server-side log of response                    |
| What the browser sees  | Network tab → response headers + body          |

If any of these four don't match what you expect, **that layer is where your bug lives.** Most
of the time it's the proxy in between, mangling something.

---

## The triage workflow for UI bugs

For any failed request, walk through these in order. Don't skip.

### Step 1 — Does the request even appear in the Network tab?

- **No** → the browser blocked it before sending. Look at the **Console** for the reason:
  CORS, mixed content (HTTPS page calling HTTP), CSP, ad-blocker / browser extension, network
  offline.
- **Yes** → continue to Step 2.

### Step 2 — What's the status code?

- **`0` or `(canceled)`** → blocked, timed out, or navigation cancelled. Not a real HTTP
  response — the request didn't complete a round trip.
- **`2xx`** → server says it worked. If the UI says otherwise, the bug is in **client-side
  handling** (parsing, state update, rendering). Stop blaming the network.
- **`3xx`** → redirect. Follow it. Did the redirect go where you expected? Is the redirect
  preserving auth?
- **`4xx`** → client error. Go to Step 3.
- **`5xx`** → server error. Move to server-side logs. Status tells you the layer is the
  application, not the network.

### Step 3 — 4xx specifics

| Status | Most likely cause                                              |
| ------ | -------------------------------------------------------------- |
| `400`  | Malformed request body / bad JSON / missing required field     |
| `401`  | Not authenticated. Was the auth header / cookie actually sent? |
| `403`  | Authenticated but forbidden. Role / permissions issue.         |
| `404`  | Wrong URL OR proxy didn't route. **Check `Request URL` exactly.** |
| `405`  | Method not allowed. POST where the route expects PUT?          |
| `415`  | Unsupported media type. Check `Content-Type` header.           |
| `422`  | Validation failed. Read the response body for field errors.    |
| `429`  | Rate limited. Check `Retry-After` header.                      |

### Step 4 — "blocked by CORS"

This message is downstream of the real failure. The real failure is in the **OPTIONS
preflight**:

1. Filter Network tab by `OPTIONS`. That's the request that failed.
2. Read the preflight response headers (next section).
3. The actual request you care about may not even fire if the preflight fails.

### Step 5 — `TypeError: Failed to fetch` / `NetworkError`

This is JS's generic "something prevented the fetch" message. It's not informative on its own.
Two places to look:
- **Console** — the *real* reason (CORS, mixed content, network offline, AbortError).
- **Network tab** — if the request shows status 0 or doesn't appear, the browser blocked it
  before the wire.

---

## CORS — the most-feared, most-misunderstood

CORS is a **browser-only** mechanism. It does not apply to curl, Postman, or server-to-server
calls. That's why "it works in Postman" is a misleading data point.

### What CORS actually does

When the browser sees a "cross-origin" request (different scheme/host/port from the page), it
either:

- **Simple requests** (GET/POST/HEAD with simple Content-Type and no custom headers): the
  browser sends the request but refuses to expose the response to JS if response headers don't
  allow it.
- **Preflighted requests** (custom headers like `Authorization`, methods like PUT/DELETE,
  Content-Type like `application/json`): the browser sends an **OPTIONS preflight** first, and
  refuses to send the actual request if the preflight response doesn't allow it.

### The CORS debugging checklist

1. **Find the preflight.** Filter Network tab by `OPTIONS`. That's the real failure surface.
2. **Read the preflight response headers.** They must include:
   - `Access-Control-Allow-Origin: <your origin>` (or `*`)
   - `Access-Control-Allow-Methods: <your method>` (e.g., `POST, GET, OPTIONS`)
   - `Access-Control-Allow-Headers: <your custom headers>` (e.g., `Authorization,
     Content-Type`)
   - If sending cookies: `Access-Control-Allow-Credentials: true` AND the origin must be
     **specific** (not `*`).
3. **Match exactly.** `https://app.foo.com` ≠ `https://app.foo.com:443` ≠ `http://app.foo.com`
   ≠ `https://app.foo.com/`. The browser is strict about origin matching.
4. **Cookies need both sides agreeing**: `credentials: 'include'` on the fetch AND
   `Access-Control-Allow-Credentials: true` on the server. Either one missing → no cookie.
5. **The server must respond to OPTIONS.** Many frameworks need explicit middleware. A `405
   Method Not Allowed` on OPTIONS means CORS middleware isn't wired up.

### Server-side CORS setup

- **Express**: `app.use(cors({ origin: 'https://app.foo.com', credentials: true }))`
- **FastAPI**: `app.add_middleware(CORSMiddleware, allow_origins=['https://app.foo.com'],
  allow_credentials=True, allow_methods=['*'], allow_headers=['*'])`
- **Next.js API routes**: set headers manually, or use `next.config.js` headers config, or use
  middleware.
- **Go (net/http)**: `rs/cors` package or hand-rolled middleware.
- **nginx in front**: see "Reverse proxies" below — easier to handle CORS at the proxy than in
  the app.

### What NOT to do

`Access-Control-Allow-Origin: *` in production. It seems to make the error go away but it opens
the API to any origin. **It also doesn't work with credentials** — the spec forbids `*` +
`Allow-Credentials: true`. Set a specific origin (or a small allowlist).

---

## Cookies — why they don't get sent

Most "I'm logged in but the API says 401" bugs are one of these:

1. **Missing `credentials: 'include'`** on `fetch` / `XMLHttpRequest`. Without it, cookies
   don't go cross-origin.
2. **`SameSite=Strict` or `Lax`** on the cookie blocking cross-site sends. For cross-site, you
   need `SameSite=None; Secure`.
3. **`Secure` flag with HTTP** — a cookie set with `Secure` won't be sent over HTTP, even on
   localhost (some browsers have a localhost exception, don't rely on it).
4. **Domain mismatch** — cookie set for `api.foo.com` won't be sent to `foo.com` (and vice
   versa unless the cookie's Domain attribute is `.foo.com`).
5. **Cookie too large** — most servers reject cookies over ~4KB total per request.
6. **Expired or `Max-Age=0`** — clock skew on the server, or the response intentionally cleared
   it.
7. **Session cookie lost on browser restart** — no `Max-Age` / `Expires` means session cookie,
   gone when the browser closes.

### Debugging

- **DevTools → Application → Cookies** — verify the cookie is actually there with the
  expected attributes.
- **Network tab → request headers** — was the `Cookie` header actually sent on this request?
- If the cookie *is* in Application but *not* in the Cookie header, you're hitting one of the
  rules above — usually SameSite, Secure, or credentials.

---

## Dev proxies — the right way

### Why dev proxies exist

In dev: frontend on `localhost:3000`, backend on `localhost:8000`. The browser sees these as
different origins → CORS. The dev proxy lets the frontend send requests to `/api/*` (same
origin as the page) and the dev server forwards them to the backend.

**Result**: no CORS in dev, simulates production same-origin setup.

### Next.js (App Router or Pages Router)

**Rewrites in `next.config.js`** (simplest, for pure proxying):

```js
// next.config.js
module.exports = {
  async rewrites() {
    return [
      { source: '/api/:path*', destination: 'http://localhost:8000/:path*' },
    ];
  },
};
```

**Route handlers** (when you need transformation or auth):

```ts
// app/api/[...path]/route.ts
export async function GET(req: Request, { params }: { params: Promise<{ path: string[] }> }) {
  const { path } = await params;
  const url = `http://localhost:8000/${path.join('/')}`;
  const res = await fetch(url, { headers: req.headers });
  return new Response(res.body, { status: res.status, headers: res.headers });
}
```

### Vite

```js
// vite.config.js
export default {
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        // rewrite: (path) => path.replace(/^\/api/, ''),  // if backend doesn't expect /api prefix
        // secure: false,  // backend uses self-signed cert
        // ws: true,       // for WebSocket support
      },
    },
  },
};
```

### webpack-dev-server / Create React App

```js
// CRA: src/setupProxy.js
const { createProxyMiddleware } = require('http-proxy-middleware');
module.exports = (app) => {
  app.use('/api', createProxyMiddleware({
    target: 'http://localhost:8000',
    changeOrigin: true,
    ws: true,
  }));
};
```

The simpler `package.json` `"proxy": "http://localhost:8000"` works for CRA but only proxies
what isn't a static asset — fragile. Use `setupProxy.js` for anything real.

### Common dev proxy failures

| Symptom                                          | Likely cause                                                                |
| ------------------------------------------------ | --------------------------------------------------------------------------- |
| 404 on `/api/*` from frontend                    | Proxy not configured, or path rewrite wrong                                 |
| 404 from backend but proxy is hit                | Path rewrite missing — backend doesn't expect the `/api` prefix             |
| Backend gets `Host: localhost:3000`              | Missing `changeOrigin: true`                                                |
| TLS errors hitting backend                       | Backend self-signed cert; need `secure: false`                              |
| HTTP works but WebSocket fails                   | Missing `ws: true`                                                          |
| Proxy hangs on slow requests                     | Default timeouts too short for the backend; configure them                  |
| Changes to proxy config not picked up            | Some dev servers need full restart, not just HMR                            |
| Frontend sees CORS errors *with* proxy           | You're calling the backend directly somewhere (check the URL in Network)    |

---

## Production reverse proxies

### nginx — the boilerplate you'll need 80% of the time

```nginx
location /api/ {
    proxy_pass http://backend:8000/;        # trailing slash matters — see below
    proxy_http_version 1.1;

    # Forward headers so backend knows the real client
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-Host $host;

    # WebSocket / HTTP-upgrade support
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";

    # Timeouts (raise for SSE / long-poll / slow APIs)
    proxy_connect_timeout 60s;
    proxy_send_timeout    60s;
    proxy_read_timeout    60s;

    # Buffers — raise for large uploads or responses
    client_max_body_size 10m;

    # Disable buffering for SSE / streaming responses
    # proxy_buffering off;
}
```

### The five nginx traps that bite everyone

1. **Trailing slash on `proxy_pass` rewrites the path; without it, the path is preserved.**
   - `proxy_pass http://backend:8000/;` → request `/api/foo` becomes `/foo` to the backend
   - `proxy_pass http://backend:8000;`  → request `/api/foo` becomes `/api/foo` to the backend
   - This is *the* most common nginx confusion. Mix it up and your backend gets the wrong path.

2. **Missing `X-Forwarded-*` headers.** Backend then thinks every request comes from the
   proxy's IP. Rate limiting by IP becomes useless, audit logs lose the real source, geo
   detection breaks.

3. **`X-Forwarded-Proto` missing or wrong.** Backend doesn't know the original was HTTPS — may
   redirect to HTTP, set cookies without Secure, return absolute URLs with `http://` prefix.

4. **WebSocket `Upgrade` header dropped.** Without `proxy_set_header Upgrade $http_upgrade;
   Connection "upgrade";`, the upgrade silently fails. Connection hangs, or you get a 200
   instead of 101.

5. **Buffer / body limits too small.** Large POST bodies get truncated with 413. Large
   response bodies stall. Default `client_max_body_size` is 1MB — too small for many real APIs.

### "Trust proxy" in your application

If your app is behind a proxy and reads request IPs / proto / host **without** trusting forwarded
headers, you get wrong values:

- **Express**: `app.set('trust proxy', 1)` (trust first hop) or `'loopback'` (trust local) or a
  specific IP. Now `req.ip` comes from `X-Forwarded-For`, `req.protocol` from
  `X-Forwarded-Proto`.
- **FastAPI / Starlette**: run uvicorn with `--proxy-headers` and `--forwarded-allow-ips='*'`
  (or specific IPs).
- **Django**: `SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')` and add
  `USE_X_FORWARDED_HOST = True`.
- **Go**: read headers manually or use `chi`/`gin` middleware.

Forget this and: rate limiting hits the proxy's IP, secure-cookie logic thinks every request is
HTTP, redirects send users to HTTP, geo blocks fail.

### Other reverse proxies — the same five concepts

The boilerplate differs but the **concepts are identical** across Traefik, Caddy, HAProxy,
AWS ALB, Cloudflare, GCP Load Balancer:

1. **Path handling** — does the proxy rewrite the path or preserve it?
2. **Forwarded headers** — is the proxy adding `X-Forwarded-*`? Is the backend reading them?
3. **WebSocket** — explicit config almost always required.
4. **Timeouts** — at the LB layer, often 30-60s by default; long-poll/SSE need higher.
5. **Buffer / body size** — default may be smaller than your app expects.

When debugging a new proxy, find where each of these five lives in its config.

---

## Corporate proxies and MITM certs

The pain you hit when your machine is behind a corporate proxy doing SSL inspection:

### Symptoms

- `npm install` / `pnpm install` / `pip install` fails with SSL errors
- `git clone` over HTTPS fails
- Browser works fine but CLI tools don't
- Error: "self signed certificate in certificate chain" / "unable to get local issuer
  certificate" / "x509: certificate signed by unknown authority"

### Why

The proxy is doing **SSL inspection**: terminating TLS, re-signing every cert with a corporate
root CA, presenting that cert to your client. Tools that don't trust that CA reject the certs.

### The fix

1. **Get the corporate root CA from IT.** Usually a `.crt` or `.pem` file.
2. **Set proxy env vars** (so HTTP libraries route through the corporate proxy):
   ```bash
   export HTTP_PROXY=http://proxy.corp:8080
   export HTTPS_PROXY=http://proxy.corp:8080
   export NO_PROXY=localhost,127.0.0.1,.internal.corp
   ```
   On Windows:
   ```powershell
   $env:HTTP_PROXY  = "http://proxy.corp:8080"
   $env:HTTPS_PROXY = "http://proxy.corp:8080"
   $env:NO_PROXY    = "localhost,127.0.0.1,.internal.corp"
   ```
3. **Tell each tool about the CA**:
   - **Node / npm**: `npm config set cafile C:/certs/corp-ca.crt` and
     `setx NODE_EXTRA_CA_CERTS C:/certs/corp-ca.crt`
   - **Python / pip**: `pip config set global.cert C:/certs/corp-ca.crt` and
     `setx REQUESTS_CA_BUNDLE C:/certs/corp-ca.crt` and `setx SSL_CERT_FILE C:/certs/corp-ca.crt`
   - **Git**: `git config --global http.sslCAInfo C:/certs/corp-ca.crt`
   - **Go**: `setx SSL_CERT_FILE C:/certs/corp-ca.crt`
   - **System trust store**: Windows `certmgr.msc` (Trusted Root); macOS Keychain; Linux
     `/usr/local/share/ca-certificates/` + `update-ca-certificates`.

### What you must NOT do

`NODE_TLS_REJECT_UNAUTHORIZED=0`, `PYTHONHTTPSVERIFY=0`, `GIT_SSL_NO_VERIFY=true`,
`git config http.sslVerify false`. These **disable TLS verification entirely** — you're now
vulnerable to actual MITM attacks, not just the corporate proxy. The corporate proxy was a
known MITM you authorized; turning off verification means *anyone* in the network path can be
one.

---

## WebSocket and Server-Sent Events debugging

WebSockets and SSE have their own failure modes that don't show up clearly in the regular
Network view.

### WebSocket

1. **Filter Network tab by `WS`.** That sub-tab shows the upgrade request and individual
   messages.
2. **Check the upgrade response.** It's an HTTP request with `Upgrade: websocket` that should
   return **`101 Switching Protocols`**. Anything else (200, 400, 404, 502) means the upgrade
   failed.
3. **The most common failure: proxy doesn't pass the `Upgrade` header.** "WebSocket works
   locally but not in prod" = 80% of the time this is the cause.
4. **Idle connections killed by LB.** Cloud LBs have idle timeouts (often 60s). Use ping/pong
   frames or `keepalive`.
5. **`wss://` vs `ws://`** — must match the page protocol. HTTPS page can't open `ws://`.
6. **Sub-protocol mismatch** — `Sec-WebSocket-Protocol` header. If client and server disagree,
   connection is rejected.

### Server-Sent Events (SSE / EventSource)

1. **No native automatic reconnection visibility.** Add logging on `onerror` and `onopen`.
2. **Common failure: buffering by the proxy.** nginx needs `proxy_buffering off` for SSE
   endpoints, or events arrive in batches at unpredictable times (or never).
3. **Common failure: wrong `Content-Type`.** Must be exactly `text/event-stream`.
4. **Compression breaks SSE.** Disable gzip / brotli for these endpoints.
5. **`Cache-Control: no-cache, no-transform`** required — proxies may transform otherwise.
6. **HTTP/2 limits concurrent SSE connections per origin.** A page with multiple SSE streams
   may hit it.

---

## Caching — why your fix didn't take effect

### The browser cache hierarchy

A request can be served from:

1. **Memory cache** — current tab session, blazing fast.
2. **Disk cache** — across tab sessions.
3. **Service worker cache** — programmatic; often what bites you.
4. **HTTP cache** — respects `Cache-Control`.
5. **The actual network** — finally.

The **Size column** in the Network tab tells you the source: `(memory cache)`, `(disk cache)`,
`(ServiceWorker)`, or the actual bytes.

### Debugging stale-code bugs

In order of escalating nukes:

1. **Hard reload** (Ctrl/Cmd+Shift+R) — bypasses HTTP cache but **NOT** the service worker.
2. **"Disable cache" checkbox in Network tab** — applies only while DevTools is open. Use this
   during dev.
3. **DevTools → Application → Service Workers → Unregister** — kills the service worker.
4. **DevTools → Application → Storage → Clear site data** — nuke everything for this origin.

If a bug only repros on a colleague's machine, walk them through these in order.

### Server-side / CDN cache

- **`Cache-Control: no-store`** for API responses that should never be cached.
- **`Cache-Control: max-age=N, must-revalidate`** to allow caching with revalidation.
- **`Age:` response header** — if it's high, you're getting a stale CDN copy. The CDN is
  caching even though you didn't expect it to.
- **`Vary` header** — if missing/wrong, the CDN may serve the wrong variant (English
  response to a French user, mobile to desktop).
- **Cache invalidation lag** — many CDNs take minutes to propagate purges.

### Caching the failure

A 4xx/5xx response can be cached by the browser or CDN if `Cache-Control` is wrong. You fix
the server; the user still sees the old error. **Always check `Cache-Control` on error
responses too.**

---

## CSP — Content Security Policy

If a `<script>`, `<img>`, `fetch`, or `WebSocket` is silently blocked:

1. **The Console tells you.** "Refused to load the script ... because it violates the
   following Content Security Policy directive: ..." Read it.
2. **The directive name tells you what to allow** — `script-src`, `connect-src` (for fetch /
   WebSocket / EventSource), `img-src`, `style-src`, `frame-src`, `font-src`.
3. **`'unsafe-inline'` and `'unsafe-eval'` are smells.** They make the error go away by
   defeating the protection. Prefer nonces / hashes for inline scripts; refactor away from
   `eval`.
4. **Test new policies with `Content-Security-Policy-Report-Only`** — logs violations without
   blocking them. Iterate, then promote to enforcing.

---

## UI-specific anti-patterns

In addition to the 15 general anti-patterns in `anti-patterns.md`:

### A. "It works in Postman, broken in the browser"

You compared two different things:
- Postman doesn't enforce CORS.
- Postman sends the headers you tell it to; your `fetch` only sends what the browser allows
  for that origin/method.
- Postman doesn't send your browser's cookies.

The bug is real; the comparison is misleading. **Check what the browser is actually sending in
the Network tab** — not what Postman is sending.

### B. "Clear cache and retry" without checking

Sometimes it's a cache; usually it's not. **Verify the cached resource is actually the cause**
before nuking everything. Otherwise you're back to "weird, working now" with no understanding.

### C. The proxy pile-up

Frontend → dev proxy → corporate proxy → reverse proxy → backend. When something fails,
isolate **which hop** loses the request by hitting layers directly:

1. Can you reach the backend from your machine? (`curl` directly)
2. Can the dev proxy reach the backend? (logs in the dev proxy)
3. Does the request reach the dev proxy at all? (logs)
4. Does it reach the reverse proxy? (access logs)
5. Does it reach the backend? (server logs)

Find the **first hop that doesn't see the request** — the bug is at the link just before it.
Don't change the topmost proxy first.

### D. "I added an exception for CORS"

If you've set `Access-Control-Allow-Origin: *` AND `Access-Control-Allow-Credentials: true`,
you've broken the spec — browsers **reject this combination**. Set a specific origin.

### E. The wildcard origin in production

`Access-Control-Allow-Origin: *` in prod means any website can call your API in the user's
context. If your API does anything stateful or returns sensitive data, this is a security bug,
not a config convenience.

### F. The "just disable TLS verification" fix

`NODE_TLS_REJECT_UNAUTHORIZED=0`, `--insecure` on curl, `verify=False` on requests. Each one
makes the immediate error go away by removing a security guarantee. **None of them is the
right fix.** The right fix is one of: install the right cert, fix the hostname, or update the
trust store.

### G. Mixing HTTP and HTTPS

The page is HTTPS; one fetch / image / script uses `http://`. Modern browsers block this as
"mixed content." Fix the URL (or use protocol-relative `//host/path`, though this is
discouraged now). Don't try to allow mixed content — it's blocked for a real reason.

### H. The "works on my browser but not theirs" punt

Different browsers enforce different things at different strictness:
- Safari is stricter about SameSite and third-party cookies (especially ITP).
- Firefox isolates third-party cookies more aggressively in private mode.
- Chrome rolls out new privacy defaults via incremental phases.

If a bug only hits one browser, that's a clue, not an excuse. The strictest browser is usually
showing you what the others will start blocking next year.

---

## Quick reference: error → likely cause

| Browser error / observation                                  | Likely cause                                                          |
| ------------------------------------------------------------ | --------------------------------------------------------------------- |
| `TypeError: Failed to fetch`                                 | CORS, mixed content, network offline, blocked by extension            |
| `Blocked by CORS policy`                                     | Preflight missing or wrong server headers — look at the OPTIONS req   |
| `Mixed Content: page loaded over HTTPS...`                   | Page is HTTPS, request URL is HTTP                                    |
| `net::ERR_CERT_AUTHORITY_INVALID`                            | Self-signed cert or untrusted CA                                      |
| `net::ERR_CERT_COMMON_NAME_INVALID`                          | Cert hostname doesn't match the URL                                   |
| `net::ERR_CONNECTION_REFUSED`                                | Nothing listening on that host/port                                   |
| `net::ERR_CONNECTION_RESET`                                  | Server killed the connection mid-request                              |
| `net::ERR_NAME_NOT_RESOLVED`                                 | DNS failure                                                           |
| `net::ERR_TUNNEL_CONNECTION_FAILED`                          | Proxy can't reach upstream                                            |
| `net::ERR_TOO_MANY_REDIRECTS`                                | Redirect loop, often HTTP↔HTTPS or auth-related                       |
| `net::ERR_BLOCKED_BY_CLIENT`                                 | Browser extension (ad blocker) blocked it                             |
| Status `0` in Network tab                                    | Browser blocked it (CORS, CSP, extension) — request never sent        |
| Status `304` unexpectedly                                    | Cached response — force-reload to bypass                              |
| Status `401` after login                                     | Auth cookie/token not sent or expired                                 |
| Status `403` from a logged-in user                           | Permission issue OR CSRF token missing                                |
| Status `404` on `/api/...`                                   | Dev proxy not routing, or path rewrite wrong                          |
| Status `405` on OPTIONS                                      | CORS preflight not handled by server                                  |
| Status `413 Payload Too Large`                               | Body exceeds proxy or server limit (`client_max_body_size`)           |
| Status `502 Bad Gateway`                                     | Reverse proxy can't reach upstream                                    |
| Status `504 Gateway Timeout`                                 | Upstream too slow for the proxy's timeout                             |
| `Refused to connect to ...`                                  | CSP `connect-src` blocking it                                         |
| WebSocket gives `200`/`404` instead of `101`                 | Proxy not forwarding `Upgrade` header                                 |
| WebSocket connects then dies after ~60s                      | LB idle timeout — add ping/pong                                       |
| SSE messages arrive in bursts                                | Proxy buffering (nginx: `proxy_buffering off`)                        |
| `SameSite cookie warning`                                    | Cookie blocked from cross-site send; needs `SameSite=None; Secure`    |
| `Request blocked: NotSameOriginAfterDefaultedToSameOriginByCoep` | Cross-Origin-Embedder-Policy / COEP mismatch                       |
