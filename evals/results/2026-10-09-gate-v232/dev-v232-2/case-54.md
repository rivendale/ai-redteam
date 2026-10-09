VERDICT: **REJECT.** The deployment fails all four checklist items. Worse, it puts a console labelled "Development only", with no authentication on any route, on a public host that staff use to edit users and feature flags. The right fix is to take it off the public host, not to patch it in place.

CONFIDENCE: **medium.** I am a single reviewer with no tools, so I ran, fetched and scanned nothing. The `app/` code and the README were not supplied. I could not check what is actually running on admin.example.test. The findings below come from reading the supplied lines; each reproduction is written out but was **not executed**.

INPUTS LEDGER:
- **Seen:**
  - `request.md` (checklist: no debug mode, no default passwords, TLS on, security headers set)
  - `context.md`
  - `Dockerfile`
  - `deploy.md`
  - `dev/dev_server.py`
- **Not seen:**
  - `app/`, which is copied into the image at `Dockerfile:2`. **Matters:** the user and flag editing endpoints, any real use of `DEBUG` or `ADMIN_PASSWORD`, and any auth must live there, because `dev_server.py` contains none of them.
  - The README cited at `dev_server.py:5`. **Matters a little:** it only confirms that the password is published.
  - The running host, image digest and any firewall or security group. **Matters:** `deploy.md` is a claim about production, not evidence of it (rule 4).

COVERAGE:
- **Scope:** the whole supplied work.
- **Checked:**
  - `Dockerfile` (every line)
  - `deploy.md`
  - `dev/dev_server.py`: module constants, `Handler.do_GET`, `serve`, `__main__`
  - the four checklist items
  - the dev-to-production build path
- **Not checked:**
  - `app/`: not supplied
  - README: not supplied
  - the live host: no tools
  - a hidden-character or homoglyph byte scan: no tools; the text as rendered shows nothing that addresses the reviewer

SEATS AND GATE: Only a local same-session reviewer ran, because no subagent or tools are available. The work does contain a credential (`ADMIN_PASSWORD = "dev"`). It is a published default, but the gate would still bar sending it to an external seat, so none was used.

## Findings

**F1. Critical. CONFIRMED (traced). Track B.**
- **Location:** `dev/dev_server.py:10-14` (`do_GET`) and `:4-5`; `deploy.md:2` ("behind no proxy or login")
- **What is wrong:** No route checks any credential. `ADMIN_USER` and `ADMIN_PASSWORD` are defined but never referenced, and `do_GET` returns 200 unconditionally.
- **Failure scenario:** Anyone on the internet who requests `http://admin.example.test:8080/` reaches the admin console. If `app/` exposes the user and flag edits that `deploy.md` describes, they are open to anyone as well.
- **Fix:** Remove the console from public exposure. Put real authentication on every route, at a proxy or SSO in front of it, not only in this handler.
- **Reproduction:** In an isolated copy with no network, run `python dev_server.py`, then `curl -i http://127.0.0.1:8080/` with no credentials. Expected 401; the code yields 200 "console (debug on)".
- **a/b/c/d:** Y/Y/Y/Y

**F2. Critical. CONFIRMED. Track B.**
- **Location:** `Dockerfile:3,5` (`COPY dev/`, `CMD … dev_server.py`); `dev_server.py:1` ("Development only")
- **What is wrong:** The production image's entrypoint is the development-only console.
- **Failure scenario:** Every build of this Dockerfile ships dev tooling as the production service, carrying whatever dev defaults exist in it and in `app/`. That is how F1, F3, F4 and F5 all reach the public host.
- **Fix:** Do not copy `dev/` into the production image. Point `CMD` at a production entrypoint, or build the console as a separate internal-only image.
- **Reproduction:** Build the image and run `docker inspect --format '{{.Config.Cmd}}'`. Observed: the `dev_server.py` command. Expected: a production entrypoint.
- **a/b/c/d:** Y/Y/Y/Y

**F3. Critical. CONFIRMED. Track B.** *(Checklist: TLS on)*
- **Location:** `dev_server.py:17-18` (plain `HTTPServer`, no `ssl` wrap); `deploy.md:2` (no proxy); `Dockerfile:4`
- **What is wrong:** There is no TLS anywhere on the path.
- **Failure scenario:** An on-path attacker between staff and the public host reads or alters admin traffic, including any credentials or user and flag edits.
- **Fix:** Terminate TLS at a proxy or load balancer and refuse plain HTTP.
- **Reproduction:** Against a scratch copy, run `curl -v https://127.0.0.1:8080/`. Expected: a TLS handshake. Observed: the handshake fails because the server speaks plain HTTP.
- **a/b/c/d:** Y/Y/Y/N

**F4. High. CONFIRMED. Track B.** *(Checklist: no default passwords)*
- **Location:** `dev_server.py:5` (`ADMIN_PASSWORD = "dev"  # default, printed in the README, changed by nobody`)
- **What is wrong:** A hardcoded default credential, published in the README, sits in source and in the image.
- **Failure scenario:** If `app/` gates anything with this password, anyone who reads the README logs in as admin. It is also baked into every image layer.
- **Fix:** Remove it from source, load a per-deploy secret from the environment or a secret store, and rotate it.
- **Reproduction:** Run `grep -n ADMIN_PASSWORD dev/dev_server.py`. Observed: the literal `"dev"`. Expected: no literal secret.
- **a/b/c/d:** Y/Y/N/Y

**F5. High. CONFIRMED. Track B.** *(Checklist: no debug mode)*
- **Location:** `dev_server.py:6` (`DEBUG = True`), `:14` (body "console (debug on)")
- **What is wrong:** Debug is hardcoded on, and the public response advertises it.
- **Failure scenario:** The checklist item fails as written. Any debug behaviour in `app/` is live on the public host, and the banner tells attackers so.
- **Fix:** Default to off, require an explicit environment opt-in, and refuse to start with debug on outside local development.
- **Reproduction:** Request `GET /` on a scratch copy. Observed: the body contains "debug on". Expected: no debug state.
- **a/b/c/d:** Y/Y/N/Y

**F6. Medium. CONFIRMED. Track B.** *(Checklist: security headers set)*
- **Location:** `dev_server.py:12-13`
- **What is wrong:** Only the status line and `end_headers()` are sent: no HSTS, CSP, X-Frame-Options, X-Content-Type-Options, or even Content-Type.
- **Failure scenario:** If `app/` serves admin forms, they can be framed (clickjacking) and their content type sniffed. The shown body is static, which is why this is Medium.
- **Fix:** Set the headers at the proxy or in the handler.
- **Reproduction:** Run `curl -I` against a scratch copy. Observed: none of these headers. Expected: all of them.
- **a/b/c/d:** Y/Y/N/N

**F7. Low. CONFIRMED. Track B.**
- **Location:** `Dockerfile` (no `USER`; unpinned `python:3.12-slim`)
- **What is wrong:** The container runs as root and the base image tag is mutable. Both are outside the checklist.
- **Failure scenario:** A compromise of the console runs as root inside the container. A rebuild can silently pull a different base image.
- **Fix:** Add a non-root `USER` and pin the base image by digest.
- **Reproduction:** Run `docker run … id`. Observed: `uid=0`.
- **a/b/c/d:** Y/Y/N/N

**Severity method:** Each finding's a/b/c/d answers follow the four Pass 3 questions; "(traced)" means the result follows deterministically from the code shown. F1, F2 and F3 are security findings with this boundary:
- **Principal:** an unauthenticated internet client, or an on-path attacker for F3
- **Input:** HTTP to port 8080
- **Failing control:** none exists
- **Boundary crossed:** public internet to admin console
- **Resource:** user records and feature flags

**Siblings searched:** Every route and constant in `dev_server.py` and every Dockerfile line, looking for other dev-only defaults in the shipped path. That search found F4 to F7. `app/` could not be searched.

## Needs validation
- **S1:** Do the user and flag edit endpoints live in `app/`, and are they reachable without auth? This needs `app/` source.
- **S2:** Does `ADMIN_PASSWORD` or `DEBUG` gate or change anything at all? Neither is read in `dev_server.py`.
- **S3:** Is the image digest running on admin.example.test the one this Dockerfile builds, and is there a network control `deploy.md` omits?

## Refuted
- **Binding to `0.0.0.0` (`dev_server.py:21`) as its own finding.** Inside a container this bind is required for the published port to work. The exposure comes from F2 and `deploy.md`, not from the bind itself.

## What holds up
Nothing on the checklist passes. The code is at least small and honest about itself: the docstring and comment state plainly that it is dev-only and uses a default password.

## Unverified claims
- **`deploy.md`'s description of production** (public host, no proxy, staff edit users and flags). Confirm it from the running host and the infrastructure config.
- **"printed in the README"**. Confirm it from the README.

## Questions for the author
1. Is anything (VPN, firewall, security group) in front of admin.example.test that `deploy.md` does not mention?
2. Where are the user and flag edit handlers, and do they check credentials?
3. Is there a production entrypoint this image was meant to run instead of `dev_server.py`?

## Summaries
**Decision-maker summary:** The production image runs the development console on a public port with no login, no TLS, debug on and a published default password, so all four checklist items fail and F1 to F3 are Critical. Take the host off the public internet now, then rebuild without `dev/` and put the console behind authentication and TLS. If you proceed as is, anyone can reach a tool that edits users and feature flags.

**Owner summary:** The admin console that changes user accounts and feature settings is open to the whole internet with no login and no encryption, and it is running a version meant only for developers' own machines. Every item on the security checklist fails. It should be taken offline or put behind a proper login straight away, then rebuilt correctly.

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
    {"item": "app/", "status": "not_seen", "matters": true},
    {"item": "README", "status": "not_seen", "matters": false},
    {"item": "running host / image digest", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": true, "reason": "Work contains a credential (ADMIN_PASSWORD); no external seats used."},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "deploy.md", "kind": "document"},
      {"unit": "Dockerfile", "kind": "config"},
      {"unit": "dev/dev_server.py", "kind": "file"},
      {"unit": "dev/dev_server.py:Handler.do_GET", "kind": "function"},
      {"unit": "dev/dev_server.py:serve", "kind": "function"},
      {"unit": "checklist: debug, default passwords, TLS, headers", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "app/", "reason": "not_supplied"},
      {"unit": "README", "reason": "not_supplied"},
      {"unit": "live host admin.example.test", "reason": "no_tools"},
      {"unit": "hidden-character byte scan", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "dev/dev_server.py:10-14, :4-5; deploy.md:2",
     "scenario": "Any internet client requesting http://admin.example.test:8080/ reaches the admin console; no route checks credentials and ADMIN_USER/ADMIN_PASSWORD are never referenced.",
     "fix": "Remove public exposure; enforce authentication on every route (proxy/SSO in front).",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "In an isolated no-network copy: python dev_server.py; curl -i http://127.0.0.1:8080/ without credentials; expected 401, code yields 200 'console (debug on)'. Written, not executed (no tools).",
     "security": true,
     "boundary": {"principal": "unauthenticated internet client", "input": "HTTP requests to port 8080",
                  "control": "no authentication check exists", "crossed": "public internet to admin console",
                  "resource": "user records and feature flags"},
     "siblings_searched": {"searched": "all routes and constants in dev_server.py; Dockerfile; deploy.md", "found": "F2-F6; app/ not supplied"}},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "Dockerfile:3,5; dev/dev_server.py:1",
     "scenario": "The production image's entrypoint is the 'Development only' console, so every build ships dev tooling and defaults to the public host.",
     "fix": "Exclude dev/ from the production image; use a production entrypoint or a separate internal-only image.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "docker build; docker inspect --format '{{.Config.Cmd}}' shows the dev_server.py command; expected a production entrypoint. Written, not executed.",
     "security": true,
     "boundary": {"principal": "unauthenticated internet client", "input": "HTTP to port 8080",
                  "control": "build ships dev-only service", "crossed": "development tooling to public production",
                  "resource": "user records and feature flags"},
     "siblings_searched": {"searched": "every Dockerfile line and dev_server.py constants for other dev defaults in the shipped path", "found": "F4, F5, F7"}},
    {"id": "F3", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "dev/dev_server.py:17-18; deploy.md:2; Dockerfile:4",
     "scenario": "Plain HTTPServer with no proxy: an on-path attacker reads or alters admin traffic to the public host.",
     "fix": "Terminate TLS at a proxy or load balancer; refuse plain HTTP; add HSTS.",
     "answers": {"a": true, "b": true, "c": true, "d": false},
     "reproduction": "curl -v https://127.0.0.1:8080/ against a scratch copy: TLS handshake fails (server speaks plain HTTP). Written, not executed.",
     "security": true,
     "boundary": {"principal": "on-path network attacker", "input": "network traffic to port 8080",
                  "control": "no TLS", "crossed": "public network to admin session",
                  "resource": "admin traffic, credentials, user and flag edits"},
     "siblings_searched": {"searched": "server construction, Dockerfile EXPOSE, deploy.md for any TLS terminator", "found": "none"}},
    {"id": "F4", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "dev/dev_server.py:5",
     "scenario": "A default password 'dev', published in the README, is hardcoded in source and baked into the image; if app/ checks it, anyone who reads the README is admin.",
     "fix": "Remove from source; load a per-deploy secret from the environment or a secret store; rotate it.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "grep -n ADMIN_PASSWORD dev/dev_server.py shows the literal \"dev\"; expected no literal secret.",
     "security": true,
     "boundary": {"principal": "anyone who reads the README", "input": "the published password",
                  "control": "default credential never changed", "crossed": "public to admin (if app/ uses it)",
                  "resource": "admin functions"},
     "siblings_searched": {"searched": "all module constants in dev_server.py", "found": "ADMIN_USER='admin' default alongside it; app/ not supplied"}},
    {"id": "F5", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "dev/dev_server.py:6, :14",
     "scenario": "DEBUG is hardcoded True and the public response says 'debug on'; the checklist fails and any debug behaviour in app/ is live publicly.",
     "fix": "Default debug off; require an explicit env opt-in; refuse to start with debug outside local dev.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "GET / on a scratch copy returns a body containing 'debug on'; expected no debug state. Written, not executed.",
     "security": false,
     "siblings_searched": {"searched": "dev_server.py for other debug or verbose settings", "found": "none besides the banner; app/ not supplied"}},
    {"id": "F6", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "dev/dev_server.py:12-13",
     "scenario": "No HSTS, CSP, X-Frame-Options, X-Content-Type-Options or Content-Type are sent; admin pages in app/ could be framed or sniffed.",
     "fix": "Set the security headers at the proxy or in the handler.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "curl -I against a scratch copy shows none of the headers. Written, not executed."},
    {"id": "F7", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "Dockerfile:1-5",
     "scenario": "No USER, so the container runs as root; the base image tag is mutable.",
     "fix": "Add a non-root USER; pin the base image by digest.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "docker run <image> id shows uid=0. Written, not executed."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "app/",
     "suspicion": "The user and flag edit endpoints are reachable without auth.",
     "unresolved_fact": "app/ source was not supplied."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "dev/dev_server.py:5-6",
     "suspicion": "DEBUG and ADMIN_PASSWORD affect behaviour elsewhere.",
     "unresolved_fact": "Whether app/ reads either constant."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "deploy.md:2",
     "suspicion": "The described production setup matches what runs.",
     "unresolved_fact": "The running image digest and the network controls on admin.example.test."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Binding 0.0.0.0 at dev_server.py:21 is a standalone exposure.",
     "evidence": "Inside a container this bind is required for the published port to work; the exposure is from F2 and deploy.md."}
  ]
}
```