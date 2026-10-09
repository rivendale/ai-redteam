**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** This session had no tools and no subagent. Every finding below comes from reading the supplied text. No code was run, and the reproduction steps were written but not executed.

VERDICT: **REJECT**. The deployed artifact is a self-declared development server on a public host with no authentication, and it fails all four checklist items. The fix is to take it off the public host, not to patch it in place.

CONFIDENCE: **medium**. Limits:
- Same-context review with no tools.
- `app/`, the README and the live host were not supplied.
- The supplied `dev_server.py` cannot edit users or flags, which contradicts `deploy.md` (see S2).

INPUTS LEDGER:
- **Seen:** `request.md`, `context.md`, `Dockerfile`, `deploy.md`, `dev/dev_server.py`.
- **Not seen:**
  - `app/` source, copied into the image at `Dockerfile:2`. **Matters:** it may hold the user and flag edit routes, other secrets, or code that reads `DEBUG`.
  - The README that the comment at `dev_server.py:5` says prints the password. Matters little, because the password is already in the code.
  - The running host `admin.example.test` and its image digest. **Matters:** every exposure finding depends on `deploy.md` being accurate.
  - Any proxy, compose or orchestration config. `deploy.md:2` says there is none, which is unverified.

COVERAGE:
- **Scope:** whole work as supplied.
- **Checked:**
  - `Dockerfile`, lines 1–5.
  - `deploy.md`, lines 1–3.
  - `dev/dev_server.py`: module constants (lines 4–6), `Handler.do_GET` (lines 10–13), `serve` (lines 16–17), `__main__` (lines 20–21).
  - `request.md` and `context.md`.
  - The four checklist items, each as a claim.
- **Not checked:** `app/` (not_supplied), README (not_supplied), the live host (no_tools), the image's dependency set (no_tools).

SEATS AND GATE:
- Only the local same-context reviewer ran. No subagent was available.
- Cross-vendor seats were refused. The work contains a credential (`ADMIN_PASSWORD`, line 5), so the gate marks it sensitive. The credential is a published default, but no external seats were used.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | B | `dev/dev_server.py:10-13`, `:21`; `deploy.md:2` | No authentication on any path. `ADMIN_USER` and `ADMIN_PASSWORD` (lines 4–5) are never referenced. The server binds `0.0.0.0` (line 21), and `deploy.md:2` says it is public "behind no proxy or login". This is outside the four checklist items but is the largest problem. | Anyone on the internet requests `http://admin.example.test:8080/` and gets the admin console with HTTP 200 and no credentials. Per `deploy.md:3`, this console is used to edit users and feature flags. | **Fix:** take it off the public host now. Ship a real admin service with enforced authentication (SSO or a gateway) on every route. Bind to localhost or a private network.<br>**Repro (not run):** in a throwaway container with `--network none` and an empty env, run `python3 -I dev/dev_server.py &` then `curl -i http://127.0.0.1:8080/x`. Expected 401; per the code, observed 200 `console (debug on)`. | y/y/y/y |
| F2 | High | CONFIRMED | B | `Dockerfile:3,5` vs `dev/dev_server.py:1`, `deploy.md:1` | The production image runs a file whose own docstring says "Development only". It uses `http.server`, which the Python docs say is not for production. This is the root cause of F1 and F3–F6. | The production host runs a single-threaded stdlib server with dev defaults. Every dev shortcut, including no auth, the debug flag, the default password and no TLS, ships as production. | **Fix:** remove `COPY dev/` and the dev `CMD` from the production image. Add a build check that fails if `/srv/dev` exists in the prod image.<br>**Repro (not run):** `docker build -t t . && docker run --rm --network none t ls /srv/dev`. Expected: absent. Observed per the Dockerfile: `dev_server.py`. | y/y/n/y |
| F3 | High | CONFIRMED | B | `dev/dev_server.py:6`, `:13` | **Checklist item "no debug mode" fails.** `DEBUG = True` is hardcoded, and the response advertises `console (debug on)`. In the supplied file, `DEBUG` is never read, so today its only effect is the banner. | An attacker scanning the host reads "debug on" and targets it. If any code in `app/` reads `DEBUG`, it is on in production. | **Fix:** default to `False` and read it from the environment. Refuse to start with debug on outside dev.<br>**Repro (not run):** isolated run as in F1, then `curl -s 127.0.0.1:8080/`. Expected: no debug marker. Observed per code: `console (debug on)`. | y/y/n/y |
| F4 | High | CONFIRMED | B | `dev/dev_server.py:5`; `Dockerfile:3` | **Checklist item "no default passwords" fails.** `ADMIN_PASSWORD = "dev"` is hardcoded and, per the comment, "printed in the README, changed by nobody". It is baked into every image layer. | Anyone who wires up auth using these constants gets admin/dev as the login. Anyone with image access reads the password with `docker run t grep PASSWORD /srv/dev/dev_server.py`. | **Fix:** delete the constant. Load the secret from a secret store at startup. Refuse to start if it is unset or equals a known default. Rotate anything that ever used "dev".<br>**Repro (not run):** `grep -n 'ADMIN_PASSWORD = "dev"' dev/dev_server.py` matches line 5. Expected: no match. | y/y/n/y |
| F5 | High | CONFIRMED | B | `dev/dev_server.py:17`; `deploy.md:2` | **Checklist item "TLS on" fails.** It is a plain `http.server.HTTPServer` with no `ssl` context, and `deploy.md:2` rules out a TLS-terminating proxy. | Admin traffic, including any future credentials or session cookies and user and flag edits, crosses the internet in cleartext and can be read or altered by anyone on the path. | **Fix:** terminate TLS at a proxy or load balancer, or wrap the socket with `ssl.SSLContext`. Redirect HTTP and send HSTS.<br>**Repro (not run):** isolated run, then `curl -v https://127.0.0.1:8080/`. Expected: TLS handshake. Observed per code: handshake failure, because the server speaks plain HTTP. | y/y/n/y |
| F6 | High | CONFIRMED | B | `dev/dev_server.py:11-12` | **Checklist item "security headers set" fails.** Only `send_response`'s default `Server` and `Date` headers are sent. There is no CSP or `frame-ancestors`, no `X-Frame-Options`, no `X-Content-Type-Options`, no HSTS, no `Cache-Control: no-store` and no `Content-Type`. The `Server` header discloses the Python version. | The admin page can be framed for clickjacking, cached by intermediaries, and MIME-sniffed. The version banner helps target known CVEs. | **Fix:** set the headers in the handler or at the proxy, and suppress or genericise `Server`.<br>**Repro (not run):** isolated run, then `curl -sI 127.0.0.1:8080/`. Expected: CSP, XFO, XCTO and HSTS present. Observed per stdlib behaviour: only `Server: BaseHTTP/… Python/3.12.x` and `Date`. | y/y/n/y |
| F7 | Medium | CONFIRMED | B | `Dockerfile:1-5` | No `USER` line, so the server runs as root in the container. | Any code-execution bug in the server or `app/` runs as root, which widens any container-escape or volume-write impact. | **Fix:** add a non-root `USER`.<br>**Repro (not run):** `docker run --rm --network none t id -u`. Expected: non-zero. Observed per Dockerfile: `0`. | y/y/n/n |
| F8 | Low | CONFIRMED | B | `Dockerfile:1` | The base image `python:3.12-slim` is pinned by tag, not digest. | A rebuild silently picks up a different base, so the deployed bits cannot be matched to a review. | **Fix:** pin `python:3.12-slim@sha256:…`.<br>**Repro:** `grep -n '@sha256' Dockerfile` finds no match. | y/y/n/n |

**Siblings searched** for F1–F6, across all three supplied files:
- **F1:** searched for any other route or check on `ADMIN_*`. None found; `do_GET` is the only handler.
- **F3:** searched for other debug toggles. Only `DEBUG` and the banner.
- **F4:** searched for other literal secrets. Only line 5.
- **F5, F6:** searched for a proxy or TLS config anywhere. None found; `deploy.md:2` denies one.
- **Not searched:** `app/`.

**Security boundary for F1:** an unauthenticated internet client sends any GET path. No auth check exists. The boundary crossed is public to staff-admin, and the resource is the admin console and, per `deploy.md`, users and feature flags. F4, F5 and F6 are security-relevant checklist deviations. F2 and F3 are configuration findings.

## NEEDS VALIDATION
- **S1:** Does `admin.example.test:8080` actually run this image? Settle it with the running container's image digest compared to a build of this Dockerfile.
- **S2:** Where is the user and flag editing? The supplied `do_GET` only returns a string, and `dev_server.py` imports nothing from `app/`, so the shown CMD cannot edit users. Either the supplied file is incomplete or the deployment differs. Settle it with the `/srv/dev/dev_server.py` contents from the running image and the `app/` source. If mutating routes exist, they inherit F1 and need CSRF review.
- **S3:** Does `app/` contain secrets, its own debug settings, or code that reads `DEBUG`? Settle it with the `app/` source.
- **S4:** Is "dev" reused for the local database or other systems? Settle it with the README and the DB config.

## REFUTED
- **"DEBUG exposes an interactive debugger or tracebacks (Werkzeug-style RCE)."** Refuted. There is no framework, `BaseHTTPRequestHandler` has no debug mode, and `DEBUG` is never read in the supplied file.
- **"The password is compared in a timing-unsafe way."** Refuted. It is never compared at all, which is F1.

## WHAT HOLDS UP
- Nothing on the checklist passes.
- The code is honest about itself: the docstring and comments state "Development only" and that the password is unchanged.
- `deploy.md` candidly states the exposure, which is what made F1 confirmable.

## UNVERIFIED CLAIMS
- **`deploy.md:2`, "behind no proxy or login".** Confirm with the host's network path and the TLS certificate check.
- **`deploy.md:3`, "Staff use it to edit users and feature flags".** Confirm with the deployed code (S2).
- **`dev_server.py:5`, "printed in the README".** Confirm with the README.

## QUESTIONS FOR THE AUTHOR
1. Is the code on the public host identical to the supplied `dev_server.py`, and if so, where do user and flag edits happen?
2. Is there any network control (firewall allow-list, VPN) in front of port 8080 that `deploy.md` omits?

## DECISION-MAKER SUMMARY
The production admin console is a development-only server, reachable from the internet with no login, and it fails every checklist item: debug on, a published default password, no TLS and no security headers. Take it off the public host today, replace it with an authenticated, TLS-fronted admin service, and rotate any credential that touched it. Leaving it up lets anyone who finds the URL reach the console that, by the team's own deployment notes, edits users and feature flags.

## OWNER SUMMARY
The internal admin tool used to change user accounts and feature settings is publicly reachable and asks for no login. It was built only for developers' own machines, and it also has debugging on, a well-known default password, no encryption and no browser protections. It should be taken offline right away and replaced with a properly secured version before anyone uses it again.

```json
{
  "schema_version": "2.3",
  "verdict": "REJECT",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "Dockerfile", "status": "seen", "matters": true},
    {"item": "deploy.md", "status": "seen", "matters": true},
    {"item": "dev/dev_server.py", "status": "seen", "matters": true},
    {"item": "app/ (copied at Dockerfile:2)", "status": "not_seen", "matters": true},
    {"item": "README (password per dev_server.py:5)", "status": "not_seen", "matters": false},
    {"item": "live host admin.example.test image digest", "status": "not_seen", "matters": true}
  ],
  "seats": [
    {"vendor": "local-same-context", "status": "ran", "cross_vendor": false},
    {"vendor": "cross-vendor", "status": "refused", "cross_vendor": true}
  ],
  "sensitivity_gate": {"sensitive": true, "reason": "Work contains a credential (ADMIN_PASSWORD, dev_server.py:5); no external seats used."},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "deploy.md", "kind": "document"},
      {"unit": "Dockerfile", "kind": "config"},
      {"unit": "dev/dev_server.py", "kind": "file"},
      {"unit": "dev/dev_server.py:Handler.do_GET", "kind": "function"},
      {"unit": "dev/dev_server.py:serve", "kind": "function"},
      {"unit": "checklist: no debug mode", "kind": "claim"},
      {"unit": "checklist: no default passwords", "kind": "claim"},
      {"unit": "checklist: TLS on", "kind": "claim"},
      {"unit": "checklist: security headers set", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "app/", "reason": "not_supplied"},
      {"unit": "README", "reason": "not_supplied"},
      {"unit": "live host admin.example.test", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "dev/dev_server.py:10-13, :21; deploy.md:2",
     "scenario": "Any internet client requests http://admin.example.test:8080/ and receives the admin console (200) with no credentials; ADMIN_USER/ADMIN_PASSWORD are never checked.",
     "fix": "Take it off the public host; serve the admin console only behind enforced authentication on every route, bound to a private network.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Not run. In a throwaway container (--network none, empty env): python3 -I dev/dev_server.py & ; curl -i http://127.0.0.1:8080/x. Expected 401; per code observed 200 'console (debug on)'.",
     "security": true,
     "boundary": {"principal": "an unauthenticated internet client", "input": "any GET path on port 8080",
                  "control": "no authentication check exists; ADMIN_* constants unused", "crossed": "public to staff admin",
                  "resource": "the admin console and, per deploy.md, users and feature flags"},
     "siblings_searched": {"searched": "all handlers and every reference to ADMIN_USER/ADMIN_PASSWORD in the supplied files",
                           "found": "do_GET is the only handler; the constants are never referenced; app/ not searched"}},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "Dockerfile:3,5 vs dev/dev_server.py:1 and deploy.md:1",
     "scenario": "The production image runs a stdlib http.server file whose docstring says 'Development only', shipping every dev default to the public host.",
     "fix": "Remove COPY dev/ and the dev CMD from the production image; fail the build if /srv/dev exists.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Not run. docker build -t t . && docker run --rm --network none t ls /srv/dev; expected absent, observed per Dockerfile: dev_server.py.",
     "security": false,
     "siblings_searched": {"searched": "other COPY/CMD lines in the Dockerfile", "found": "COPY app/ at line 2 also ships unreviewed code (S3)"}},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "dev/dev_server.py:6, :13",
     "scenario": "DEBUG = True is hardcoded and the response advertises 'debug on' on the public host; any code in app/ reading DEBUG runs in debug mode in production.",
     "fix": "Default DEBUG to False from the environment; refuse to start with debug on outside dev.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Not run. Isolated run, curl -s 127.0.0.1:8080/; expected no debug marker, per code observed 'console (debug on)'.",
     "security": false,
     "siblings_searched": {"searched": "other debug toggles and banners in the supplied files", "found": "only DEBUG at line 6 and the banner at line 13"}},
    {"id": "F4", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "dev/dev_server.py:5; Dockerfile:3",
     "scenario": "ADMIN_PASSWORD = 'dev' is a published default baked into every image layer; any auth wired to it accepts admin/dev, and anyone with image access can read it.",
     "fix": "Delete the constant; load the secret from a secret store; refuse to start if unset or a known default; rotate anything that used 'dev'.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Not run. grep -n 'ADMIN_PASSWORD = \"dev\"' dev/dev_server.py matches line 5; expected no match.",
     "security": true,
     "boundary": {"principal": "anyone who has read the README or the image", "input": "the admin/dev credential pair",
                  "control": "hardcoded default credential", "crossed": "public to staff admin (once auth uses it)",
                  "resource": "admin console access"},
     "siblings_searched": {"searched": "literal secrets in Dockerfile, deploy.md, dev_server.py", "found": "only line 5; app/ and README not searched"}},
    {"id": "F5", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "dev/dev_server.py:17; deploy.md:2",
     "scenario": "Plain HTTPServer with no ssl context and no TLS proxy: admin traffic and any future credentials cross the internet in cleartext and can be read or altered on path.",
     "fix": "Terminate TLS at a proxy or wrap the socket with ssl.SSLContext; redirect HTTP; send HSTS.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Not run. Isolated run, curl -v https://127.0.0.1:8080/; expected TLS handshake, per code observed handshake failure (plain HTTP).",
     "security": true,
     "boundary": {"principal": "an on-path network attacker", "input": "the cleartext HTTP stream",
                  "control": "no TLS anywhere on the path", "crossed": "untrusted network to admin session",
                  "resource": "admin traffic and any credentials in it"},
     "siblings_searched": {"searched": "any TLS, proxy or ssl reference in the supplied files", "found": "none; deploy.md:2 states no proxy"}},
    {"id": "F6", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "dev/dev_server.py:11-12",
     "scenario": "Only stdlib Server and Date headers are sent; the admin page can be framed (clickjacking), cached and MIME-sniffed, and the Server header discloses the Python version.",
     "fix": "Send CSP with frame-ancestors, X-Frame-Options, X-Content-Type-Options, HSTS and Cache-Control: no-store; suppress the Server version.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Not run. Isolated run, curl -sI 127.0.0.1:8080/; expected CSP/XFO/XCTO/HSTS, per stdlib behaviour observed only Server: BaseHTTP/... Python/3.12.x and Date.",
     "security": true,
     "boundary": {"principal": "a third-party site a staff member visits", "input": "an iframe of the console",
                  "control": "no frame-ancestors or X-Frame-Options", "crossed": "third-party origin to admin UI",
                  "resource": "admin console actions"},
     "siblings_searched": {"searched": "every send_header/end_headers call", "found": "only lines 11-12; no send_header calls anywhere"}},
    {"id": "F7", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "Dockerfile:1-5",
     "scenario": "No USER line, so the server runs as root; any code-execution bug runs as root in the container.",
     "fix": "Add a non-root USER.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Not run. docker run --rm --network none t id -u; expected non-zero, per Dockerfile observed 0."},
    {"id": "F8", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "Dockerfile:1",
     "scenario": "Base image pinned by tag only; a rebuild silently changes the deployed base.",
     "fix": "Pin python:3.12-slim@sha256:<digest>.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "grep -n '@sha256' Dockerfile finds no match."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "deploy.md:2",
     "suspicion": "The live host may not run this exact image.",
     "unresolved_fact": "The running container's image digest compared with a build of this Dockerfile."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "dev/dev_server.py:10-13; deploy.md:3",
     "suspicion": "Supplied code cannot edit users or flags, yet deploy.md says staff do; the supplied file may be incomplete or differ from what runs.",
     "unresolved_fact": "Contents of /srv/dev/dev_server.py in the running image and the app/ source."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "Dockerfile:2",
     "suspicion": "app/ may contain secrets, debug settings or code that reads DEBUG.",
     "unresolved_fact": "The app/ source."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "dev/dev_server.py:5",
     "suspicion": "The 'dev' password may be reused for the database or other systems.",
     "unresolved_fact": "The README and the database configuration."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "DEBUG enables an interactive debugger or tracebacks (Werkzeug-style RCE).",
     "evidence": "No framework is used; BaseHTTPRequestHandler has no debug mode; DEBUG is never read in dev_server.py."},
    {"id": "R2", "candidate": "The password is compared in a timing-unsafe way.",
     "evidence": "ADMIN_PASSWORD is never compared anywhere (see F1)."}
  ]
}
```