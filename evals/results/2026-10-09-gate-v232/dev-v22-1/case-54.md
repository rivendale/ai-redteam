VERDICT: **REJECT.** The checklist fails on all four items, and the bigger problem is that a development-only console with no authentication is the production entrypoint on a public host.

CONFIDENCE: **medium.** I had no tools, so nothing was run and the running deployment was not checked. The edit-users/flags code (`app/`) and the README were not supplied. The work was not written in this conversation, but no fresh subagent was available. This is a single-reviewer read.

INPUTS LEDGER:
- **Seen:** `request.md`, `context.md`, `Dockerfile`, `deploy.md`, `dev/dev_server.py`.
- **Not seen:**
  - `app/` (copied into the image, likely holds the user/flag editing logic). This gap matters: it may read `DEBUG` or `ADMIN_PASSWORD` or add more routes.
  - `README` (cited in the `dev_server.py:5` comment). It matters a little: it confirms the password is published.
  - The image actually running on `admin.example.test` (digest or version). This matters: `deploy.md` is an assertion, not a check of what is running.
  - Any proxy, load balancer or firewall config. This matters: `deploy.md:2` says there is none, which is unverified.

COVERAGE:
- **Checked:**
  - `Dockerfile` (all 5 lines)
  - `deploy.md` (all)
  - `dev/dev_server.py`: module constants, `Handler.do_GET`, `serve`, `__main__`
  - All four checklist items
- **Not checked:** `app/`, `README`, the running host, runtime environment variables, image registry.

SEATS AND GATE: Only a local same-context reviewer ran. No subagent or cross-vendor seats were available because the session has no tools. Gate: the work contains a credential (`ADMIN_PASSWORD = "dev"`), so it should not go to external seats regardless. No personal data was found in the supplied files.

### FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | B/A | `Dockerfile:3,5`; `deploy.md:2-3`; `dev/dev_server.py:1,21` | A console self-described as "Development only" is the container CMD. `deploy.md` says it runs on a public host, port 8080, "behind no proxy or login", and staff use it to edit users and feature flags. | Anyone on the internet reaching `admin.example.test:8080` hits the dev console directly. Every control a production admin surface needs (auth, TLS, headers, hardening) is absent by design. | Take it off the public host now. Do not ship `dev/` in the production image; build a production console behind SSO/VPN with TLS termination. Repro: `curl -i http://admin.example.test:8080/` from an external network; expect refused or 401, observe 200 "console (debug on)". | a✓ b✓ c✓ d✓ |
| F2 | Critical | CONFIRMED | B | `dev/dev_server.py:10-13` | `do_GET` returns 200 to every request. `ADMIN_USER`/`ADMIN_PASSWORD` are defined but never read, so no authentication runs on any path. | An unauthenticated visitor reaches the console. If `app/` adds edit routes to this server, they are equally open, giving unauthenticated edits to users and feature flags. | Enforce authentication (SSO or per-user credentials) on every handler before any work. Repro: request `/` with no `Authorization` header; expect 401, observe 200. | a✓ b✓ c✓ d✓ |
| F3 | High | CONFIRMED | B | `dev/dev_server.py:6,13` | Checklist "no debug mode" fails: `DEBUG = True` is hardcoded, and the response body advertises "console (debug on)". | Production runs with debug declared on and announces it to visitors. Whatever `app/` gates on `DEBUG` (tracebacks, reloaders, extra routes) is enabled. | Default to `DEBUG = False`, read it from the environment, and fail closed in production. Repro: `curl http://host:8080/`; observe "debug on". | a✓ b✓ c✗ d✓ |
| F4 | High | CONFIRMED | B | `dev/dev_server.py:4-5` | Checklist "no default passwords" fails. The `admin`/`dev` credential is hardcoded in source, and the line's own comment says it is "printed in the README, changed by nobody". | If any component (here, `app/`, a DB) accepts these credentials, anyone who reads the README or the image layers has admin. The secret is also baked into the image. | Remove the hardcoded credential, load secrets from a secret store, and rotate wherever `dev` is used. Repro: `docker run --rm IMAGE grep -n ADMIN_PASSWORD /srv/dev/dev_server.py` shows it. | a✓ b✓ c✗ d✓ |
| F5 | High | CONFIRMED | B | `dev/dev_server.py:17`; `deploy.md:2`; `Dockerfile:4` | Checklist "TLS on" fails. Plain `http.server.HTTPServer` with no `ssl` wrapping, and per `deploy.md` there is no proxy terminating TLS. | Admin traffic, including any future credentials or session tokens and user/flag edits, crosses the internet in cleartext. It can be read or altered by anyone on the path. | Terminate TLS at a proxy or load balancer (and redirect 80 to 443), or wrap the socket with `ssl.SSLContext`. Repro: `curl -v https://admin.example.test:8080/`; observe a TLS handshake failure. | a✓ b✓ c✗ d✓ |
| F6 | High | CONFIRMED (headers); PROBABLE (Server header contents) | B | `dev/dev_server.py:11-12` | Checklist "security headers set" fails. No HSTS, CSP/`frame-ancestors`, `X-Frame-Options`, `X-Content-Type-Options` or `Referrer-Policy`, and not even `Content-Type`. Stdlib `send_response` also emits a `Server: BaseHTTP/0.6 Python/3.12.x` banner. | An admin console that can be framed is open to clickjacking of edit actions. Missing `nosniff` and `Content-Type` invite content sniffing. The banner discloses the exact runtime to scanners. | Set the headers in one place (a proxy or a `send_header` helper) and override `version_string()`. Repro: `curl -I http://host:8080/`; expect the headers, observe only Server and Date. | a✓ b✓ c✗ d✓ |
| F7 | Medium | CONFIRMED | B | `Dockerfile:1-5` | No `USER` directive, so the server runs as root in the container. It binds `0.0.0.0` (`dev_server.py:21`). | Any code-execution bug in the server or in `app/` yields root in the container, which makes escape or lateral movement easier. | Add a non-root `USER`. Drop `dev/` from the image. Repro: `docker run IMAGE id`; observe uid=0. | a✓ b✓ c✗ d✗ |
| F8 | Low | PROBABLE | B | `dev/dev_server.py:2,17` | `http.server` is documented by Python as not recommended for production (basic security checks only). `HTTPServer` is single-threaded. | One slow client stalls the console for all staff, and hardening gaps are inherited from a module not built for exposure. | Use a production WSGI/ASGI server behind a reverse proxy. | a✓ b✗ c✗ d✗ |

### NEEDS VALIDATION
- **S1:** Where the user and feature-flag editing actually happens. The supplied handler only serves a static string. Settled by reading `app/` and checking whether its routes are mounted on this server or another listener.
- **S2:** Whether the image running on the host is the one built from this Dockerfile. Settled by comparing the running container's image digest to a build of this commit.
- **S3:** Actual exposure. `admin.example.test` uses the reserved `.test` TLD and cannot resolve publicly, so it may be a placeholder. Settled by the real hostname and an external port scan of 8080.
- **S4:** Whether `DEBUG` changes behavior beyond the banner (tracebacks to clients, reload, extra endpoints). Settled by a search for `DEBUG` across `app/`, with a positive control: the same search must find `dev_server.py:6`.
- **S5:** Whether the `dev` password is reused (DB, other services). Settled by the README and secret inventory.

### REFUTED
- **Candidate:** "Default credentials admin/dev let an attacker log in." The supplied code never reads `ADMIN_USER` or `ADMIN_PASSWORD`, so there is no login to defeat. The real issue is worse: there is no authentication at all (F2). F4 stands only as a checklist and secret-hygiene failure, with exploitability pending S5.

### WHAT HOLDS UP
- The docstring is honest about the file being development-only. That framing is correct; the shipping decision is the problem.
- `python:3.12-slim` is a reasonable minimal base.
- Nothing in the work tries to instruct the reviewer.

### UNVERIFIED CLAIMS
- "Behind no proxy or login" (`deploy.md:2`): confirm with network config.
- "Printed in the README, changed by nobody" (`dev_server.py:5`): confirm in the README and credential stores.
- "Staff use it to edit users and feature flags" (`deploy.md:3`): no such code was supplied (S1).

### QUESTIONS FOR THE AUTHOR
1. Is this image actually live on a public address right now, and what is the real hostname?
2. Where is the edit code, and does it mount onto `dev_server.py`'s listener?
3. Is the `dev` password used anywhere else?

### DECISION-MAKER SUMMARY
The production admin console is a development server with no login, no TLS, no security headers, debug on and a published default password, so all four checklist items fail. Take it off the public host today and replace it with a production build behind SSO and TLS. Proceeding risks anyone on the internet reaching a tool that edits users and feature flags.

### OWNER SUMMARY
The admin tool that changes user accounts and feature settings is running a version meant only for developers, and it is reachable from the internet with no login or encryption. It fails every item on the security checklist. It should be taken offline now and replaced with a properly secured version before staff use it again.

```json
{
  "schema_version": "2.2",
  "verdict": "REJECT",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "Dockerfile", "status": "seen", "matters": true},
    {"item": "deploy.md", "status": "seen", "matters": true},
    {"item": "dev/dev_server.py", "status": "seen", "matters": true},
    {"item": "app/", "status": "not_seen", "matters": true},
    {"item": "README", "status": "not_seen", "matters": false},
    {"item": "running image on admin.example.test", "status": "not_seen", "matters": true},
    {"item": "proxy/firewall config", "status": "not_seen", "matters": true}
  ],
  "seats": [
    {"vendor": "claude-same-context", "status": "ran", "cross_vendor": false},
    {"vendor": "claude-subagent", "status": "unavailable", "cross_vendor": false},
    {"vendor": "cross-vendor", "status": "refused", "cross_vendor": true}
  ],
  "sensitivity_gate": {"sensitive": true, "reason": "Work contains a hardcoded credential (ADMIN_PASSWORD); no external seats."},
  "coverage": {
    "checked": [
      {"unit": "Dockerfile", "kind": "file"},
      {"unit": "deploy.md", "kind": "file"},
      {"unit": "dev/dev_server.py", "kind": "file"},
      {"unit": "dev/dev_server.py:Handler.do_GET", "kind": "function"},
      {"unit": "dev/dev_server.py:serve", "kind": "function"},
      {"unit": "checklist: no debug mode", "kind": "claim"},
      {"unit": "checklist: no default passwords", "kind": "claim"},
      {"unit": "checklist: TLS on", "kind": "claim"},
      {"unit": "checklist: security headers set", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "app/", "reason": "not supplied"},
      {"unit": "README", "reason": "not supplied"},
      {"unit": "running deployment", "reason": "no tools; not accessible"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "Dockerfile:3,5; deploy.md:2-3; dev/dev_server.py:1,21",
     "scenario": "A development-only console is the production container entrypoint on a public host with no proxy or login; anyone reaching port 8080 gets the console that edits users and feature flags.",
     "fix": "Take it off the public host; exclude dev/ from the production image; ship a production console behind SSO/VPN and TLS.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "curl -i http://admin.example.test:8080/ from outside; expect refused/401, observe 200 'console (debug on)'."},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "dev/dev_server.py:10-13",
     "scenario": "do_GET returns 200 to every request and ADMIN_USER/ADMIN_PASSWORD are never read; any edit routes on this server are unauthenticated.",
     "fix": "Enforce authentication on every handler before any work.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "GET / with no Authorization header; expect 401, observe 200."},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "dev/dev_server.py:6,13",
     "scenario": "DEBUG = True is hardcoded and the response advertises 'debug on' in production; anything gated on DEBUG is enabled.",
     "fix": "Default DEBUG to False, read from environment, fail closed in production.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "curl http://host:8080/; observe 'console (debug on)'."},
    {"id": "F4", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "dev/dev_server.py:4-5",
     "scenario": "Default credential admin/dev is hardcoded, published in the README per the comment, never changed, and baked into the image; any component accepting it grants admin.",
     "fix": "Remove the hardcoded credential, load from a secret store, rotate wherever 'dev' is used.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "docker run --rm IMAGE grep -n ADMIN_PASSWORD /srv/dev/dev_server.py shows the password."},
    {"id": "F5", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "dev/dev_server.py:17; deploy.md:2; Dockerfile:4",
     "scenario": "Plain HTTPServer with no TLS and no terminating proxy; admin traffic and edits cross the internet in cleartext.",
     "fix": "Terminate TLS at a proxy/load balancer with HTTP->HTTPS redirect, or wrap the socket with ssl.SSLContext.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "curl -v https://admin.example.test:8080/; observe TLS handshake failure."},
    {"id": "F6", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "dev/dev_server.py:11-12",
     "scenario": "No HSTS, CSP/frame-ancestors, X-Frame-Options, X-Content-Type-Options, Referrer-Policy or Content-Type; console can be framed (clickjacking) and the Server banner discloses the Python version.",
     "fix": "Set security headers centrally (proxy or send_header helper) and override version_string().",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "curl -I http://host:8080/; expect security headers, observe only Server and Date."},
    {"id": "F7", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "Dockerfile:1-5",
     "scenario": "No USER directive; the server runs as root, so any code-execution bug yields root in the container.",
     "fix": "Add a non-root USER and drop dev/ from the image.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "docker run IMAGE id; observe uid=0."},
    {"id": "F8", "status": "confirmed", "severity": "Low", "evidence_level": "PROBABLE", "track": "B",
     "location": "dev/dev_server.py:2,17",
     "scenario": "Stdlib http.server is documented as not for production and HTTPServer is single-threaded; one slow client stalls the console.",
     "fix": "Use a production WSGI/ASGI server behind a reverse proxy.",
     "answers": {"a": true, "b": false, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "app/",
     "suspicion": "User/flag editing code may be mounted on this unauthenticated listener.",
     "unresolved_fact": "Contents of app/ and which server its routes run on."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "deploy.md:2",
     "suspicion": "Running image may differ from this Dockerfile.",
     "unresolved_fact": "Digest of the running container versus a build of this commit."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "deploy.md:2",
     "suspicion": "admin.example.test is a reserved .test name; real public exposure is unconfirmed.",
     "unresolved_fact": "The real hostname and an external scan of port 8080."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "dev/dev_server.py:6",
     "suspicion": "DEBUG may enable tracebacks or extra routes elsewhere.",
     "unresolved_fact": "Search for DEBUG in app/, with dev_server.py:6 as positive control."},
    {"id": "S5", "status": "needs_validation", "track": "B", "location": "dev/dev_server.py:5",
     "suspicion": "The 'dev' password may be reused for the database or other services.",
     "unresolved_fact": "README contents and the credential inventory."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Default credentials admin/dev let an attacker log in to the console.",
     "evidence": "No code reads ADMIN_USER or ADMIN_PASSWORD (dev_server.py:10-13); there is no login at all, which is the worse issue recorded as F2."}
  ]
}
```