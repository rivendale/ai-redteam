**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** I did not write this work, but no subagent or tools were available. Everything below comes from a static read of the three supplied files. Nothing was executed, and the reproduction steps are written for someone else to run.

VERDICT: **REWORK**. The image runs a development-only server with no authentication check on a public host, and it fails all four checklist items. Patching individual lines will not fix that; the server needs to be replaced.

CONFIDENCE: **medium**. Limits: no tools, so the running host and `app/` were not checked. The deployment note describes capabilities (editing users and flags) that the supplied code does not have, so the deployed code may differ from what I reviewed.

**Checklist result (from the supplied code)**

| Item | Result | Where |
|---|---|---|
| No debug mode | FAIL | `dev/dev_server.py:6`, `:13` |
| No default passwords | FAIL (and the password is never checked, see F1) | `dev/dev_server.py:5` |
| TLS on | FAIL | `dev/dev_server.py:17`, `deploy.md:2` |
| Security headers set | FAIL | `dev/dev_server.py:11-12` |

Checklist status and severity are recorded separately. Under Pass 3 item 4, a checklist deviation that crosses no trust boundary is at most Low. That is why some FAILs are rated Low.

INPUTS LEDGER:
- Seen: request.md, context.md, `Dockerfile`, `deploy.md`, `dev/dev_server.py`.
- Not seen: `app/`. It is copied into the image at `Dockerfile:2`. It could contain the user and flag editing code and could use `ADMIN_PASSWORD` or `DEBUG`. **Matters.**
- Not seen: the README. The comment at `:5` says the password is printed there. Matters little, because the password is already in source.
- Not seen: the running host or the deployed image digest. `deploy.md` is a claim, not a check of what is actually running. **Matters.**
- Not seen: host firewall or security-group rules for port 8080. **Matters** for how exposed the console really is.

COVERAGE:
- Scope: the whole supplied work, meaning `dev/dev_server.py` and how it ships.
- Checked: request.md, context.md, `Dockerfile` (all lines), `deploy.md` (all lines), `dev/dev_server.py` (module docstring, constants, `Handler.do_GET`, `serve`, `__main__`).
- Not checked: `app/` (not supplied), README (not supplied), the running host (no tools), and a byte-level scan for hidden or bidirectional characters (no tools; nothing visible in the text).

SEATS AND GATE: Only a local self-review ran. No subagent or cross-vendor seats were available or requested. Sensitivity gate: no personal, client or financial data. The only credential is the published default `dev`. The gate passed, but it was moot because no external seat ran.

### FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | High | CONFIRMED (code); production exposure per `deploy.md` | B | `dev/dev_server.py:9-13` | No authentication on any path. `ADMIN_USER` and `ADMIN_PASSWORD` (`:4-5`) are defined but never referenced. `do_GET` answers every request with 200. | `deploy.md:2` says the console is on a public host, port 8080, "behind no proxy or login". Any anonymous internet client reaches the admin console. | **Fix:** require authentication on every handler, deny by default, and put an authenticating proxy or SSO in front. **Repro (isolated container, no network, empty env):** `python3 -I dev/dev_server.py`, then `curl -i http://127.0.0.1:8080/`. Expected 401; static trace says 200 with `console (debug on)`. | a✔ b✔ c✘ d✔ |
| F2 | High | CONFIRMED | B | `Dockerfile:3,5`; `dev/dev_server.py:1` | The image's only entrypoint is a module whose docstring says "Development only". It is built on `http.server`, which the Python docs say is not for production. `deploy.md:1-2` calls this image production. | Every production request is served by a dev tool. This is the root cause behind F1 and F3-F6: no auth, no TLS, no headers and debug on are all inherited from shipping the wrong component. | **Fix:** do not ship `dev/` in the production image. Build a production entrypoint (a real WSGI/ASGI server behind TLS and auth) or take the console off the public host. **Repro:** `docker inspect --format '{{.Config.Cmd}}' <image>` shows `python /srv/dev/dev_server.py`. Compare with the digest running on the host. | a✔ b✔ c✘ d✔ |
| F3 | Medium | CONFIRMED | B | `dev/dev_server.py:17`; `deploy.md:2` | Plain HTTP. No `ssl` wrapping, and per the deployment note no TLS-terminating proxy. | An on-path attacker (shared Wi-Fi, a hostile network) can read and alter admin traffic. Once F1 is fixed, credentials would also cross in cleartext, which would raise this to High. | **Fix:** terminate TLS (proxy or `ssl.SSLContext.wrap_socket`) and redirect or refuse HTTP. **Repro:** with the server running, `openssl s_client -connect 127.0.0.1:8080` fails the handshake and `curl http://...` succeeds. | a✔ b✔ c✘ d✘ |
| F4 | Low | CONFIRMED | B | `dev/dev_server.py:11-12` | `send_response(200)` is followed directly by `end_headers()`. No HSTS, CSP, X-Frame-Options, X-Content-Type-Options or even Content-Type is set. The stdlib also adds a `Server:` header with the Python version (verify with the repro). | The checklist item fails. Today the body is a static string, so no browser attack is reachable yet. Once real forms exist, clickjacking and MIME sniffing apply. | **Fix:** set the headers centrally, in the proxy or in a shared `end_headers` override, and suppress the version string. **Repro:** `curl -si http://127.0.0.1:8080/ \| sed '/^\r$/q'` shows only `Server` and `Date`. | a✔ b✔ c✘ d✘ |
| F5 | Low | CONFIRMED | B | `dev/dev_server.py:5` | Hard-coded default password `"dev"`, committed to source, baked into the image, and per the comment published in the README and never changed. | The checklist item fails. In the supplied code the password guards nothing (see F1), so it crosses no boundary by itself. If anything in `app/` authenticates with it, this becomes High or Critical (see S2). | **Fix:** remove it from source, load a per-deployment secret from the environment or a secret store, and fail closed at startup when it is unset. Rotate wherever `dev` was ever accepted. **Repro:** `grep -n ADMIN_PASSWORD dev/dev_server.py` gives one definition and no use. `docker run --rm <image> grep -r '"dev"' /srv/dev` shows it inside the image. | a✔ b✔ c✘ d✘ |
| F6 | Low | CONFIRMED | B | `dev/dev_server.py:6`, `:13` | `DEBUG = True` is set unconditionally, and the response advertises "debug on". In the supplied code `DEBUG` is never read. | The checklist item fails, and the banner tells scanners this is a debug build. If `app/` reads the flag, impact depends on what it enables (S2). | **Fix:** default `DEBUG` to off from the environment and refuse to start with debug on outside dev. Remove the banner. **Repro:** `curl -s http://127.0.0.1:8080/` returns `console (debug on)`. | a✔ b✔ c✘ d✘ |
| F7 | Low | CONFIRMED | B | `Dockerfile` (no `USER` line) | `python:3.12-slim` runs as root by default, and the Dockerfile never drops privileges. | Any future code-execution bug in the console runs as root inside the container. | **Fix:** add a non-root `USER` and a read-only filesystem where possible. **Repro:** `docker run --rm --network none <image> id -u` prints `0`. | a✔ b✔ c✘ d✘ |

The sibling search for F1 and F2 covered every reference to `ADMIN_USER`, `ADMIN_PASSWORD` and `DEBUG` in the supplied files, every handler method (only `do_GET` exists), and both `Dockerfile` and `deploy.md` for any proxy, login or TLS layer. No other auth check exists in the supplied code. The sibling defects that share F2's root cause are F3-F6, each listed separately.

F1 boundary: an anonymous internet client sends any HTTP request to port 8080. No credential check exists, so it crosses from the internet into the admin console. The confirmed resource is the console endpoint itself. Users and flags are in play only if the deployed code differs (S1).

### NEEDS VALIDATION
- **S1:** `deploy.md:3` says staff edit users and flags with this console. The supplied `dev_server.py` has no edit code, and it imports nothing from `app/` even though `app/` is copied into the image. **Unresolved fact:** which code actually runs on the host (image digest and the `dev_server.py` inside it). If it can edit users or flags, F1 becomes **Critical**, because unauthenticated internet users could modify accounts.
- **S2:** Whether anything in `app/` authenticates with `ADMIN_PASSWORD` or reads `DEBUG`. **Unresolved fact:** the contents of `app/`. If either is used, F5 or F6 rises to High or Critical.
- **S3:** Whether a host firewall or security group limits port 8080 despite `deploy.md`. **Unresolved fact:** the network rules on the host. This changes how likely F1 is to be exploited, not whether the defect exists.
- **S4:** `HTTPServer` is single-threaded, and the handler sets no timeout. One idle connection may block all staff. **Unresolved fact:** run `nc 127.0.0.1 8080` and send nothing, then check whether a second `curl --max-time 5` times out (isolated copy only).

### REFUTED
- **"Binding `0.0.0.0` (`:21`) is a defect."** Inside a container this is required for port publishing. Exposure is decided by how the host publishes the port and by `deploy.md`, both already covered by F1 and F2.
- **"`DEBUG` enables tracebacks or code execution."** In the supplied code `DEBUG` is never read. The only effect is the banner (F6). The `app/` case remains open as S2.
- **"The work contains instructions aimed at the reviewer."** The comment "changed by nobody" describes the situation; it is not an instruction to the reviewer. No injection was found.

### WHAT HOLDS UP
The deployment note is candid: it states the public host, the lack of a proxy and the lack of a login, which made the exposure easy to trace. The server writes only a static string, so the supplied code has no injection sinks or unsafe deserialization. The `0.0.0.0` bind is normal for a container.

### UNVERIFIED CLAIMS
- "The image built from the Dockerfile is what runs on the public host" (`deploy.md:2`). Confirm by comparing the running container's image digest with a fresh build.
- "Staff use it to edit users and feature flags" (`deploy.md:3`). The supplied code contradicts this. Confirm against the deployed code (S1).
- "Printed in the README, changed by nobody" (`dev_server.py:5`). Confirm from the README and the host configuration.

### QUESTIONS FOR THE AUTHOR
1. Is the `dev_server.py` in the running image the one supplied here? If not, please supply the deployed one and `app/`.
2. Does any code path accept `admin`/`dev`?
3. Is port 8080 reachable from the internet today, or filtered at the network layer?

### DECISION-MAKER SUMMARY
The production admin console is a development-only server with no login, no TLS, no security headers, debug on and a published default password, and it is reported to be on a public host. Take it off the public internet or put an authenticating TLS proxy in front of it now, then replace it with a production server. If the deployed version really edits users and flags as the deployment note says, anyone online can change accounts until this is done.

### OWNER SUMMARY
The tool staff use to manage users and settings is a developer test program, and it is open to the internet with no password check and no encryption. It fails every item on the security checklist. It should be taken offline or placed behind a proper login right away, then replaced with a version built for real use.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "Dockerfile", "status": "seen", "matters": true},
    {"item": "deploy.md", "status": "seen", "matters": true},
    {"item": "dev/dev_server.py", "status": "seen", "matters": true},
    {"item": "app/", "status": "not_seen", "matters": true},
    {"item": "README", "status": "not_seen", "matters": false},
    {"item": "running host / deployed image digest", "status": "not_seen", "matters": true},
    {"item": "host firewall rules for port 8080", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-self-no-subagent", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "No personal, client or financial data; the only credential is the published default 'dev'."},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "deploy.md", "kind": "document"},
      {"unit": "Dockerfile", "kind": "config"},
      {"unit": "dev/dev_server.py", "kind": "file"},
      {"unit": "dev/dev_server.py:Handler.do_GET", "kind": "function"},
      {"unit": "dev/dev_server.py:serve", "kind": "function"},
      {"unit": "deploy.md: image is what runs publicly with no proxy or login", "kind": "claim"},
      {"unit": "deploy.md: staff edit users and flags with it", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "app/", "reason": "not_supplied"},
      {"unit": "README", "reason": "not_supplied"},
      {"unit": "running host and deployed image", "reason": "no_tools"},
      {"unit": "byte-level scan for hidden/bidi characters", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "dev/dev_server.py:9-13",
     "scenario": "Handler never checks ADMIN_USER/ADMIN_PASSWORD; with the console on a public host behind no proxy or login (deploy.md:2), any anonymous internet client reaches the admin console.",
     "fix": "Require authentication on every handler, deny by default, and front the console with an authenticating proxy or SSO.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "In an isolated container with no network: python3 -I dev/dev_server.py; curl -i http://127.0.0.1:8080/ ; expected 401, static trace gives 200 'console (debug on)'. Not executed (no tools).",
     "security": true,
     "boundary": {"principal": "any anonymous internet client", "input": "any HTTP request to port 8080",
                  "control": "no credential check exists; ADMIN_USER/ADMIN_PASSWORD are never referenced",
                  "crossed": "internet to admin console", "resource": "the admin console (users and flags if the deployed code differs, see S1)"},
     "siblings_searched": {"searched": "all references to ADMIN_USER, ADMIN_PASSWORD, DEBUG; all handler methods; Dockerfile and deploy.md for proxy, login or TLS",
                           "found": "no auth check anywhere in supplied code; same-root siblings F2-F6 listed separately"}},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "Dockerfile:3,5",
     "scenario": "The production image's only entrypoint is dev/dev_server.py, documented as 'Development only' and built on http.server; deploy.md states this image runs on the public host, so every production request is served by a dev tool lacking auth, TLS and headers.",
     "fix": "Exclude dev/ from the production image; ship a production server behind TLS and auth, or remove the console from the public host.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "docker inspect --format '{{.Config.Cmd}}' <image> shows python /srv/dev/dev_server.py; compare with the digest running on the host. Not executed (no tools).",
     "security": true,
     "boundary": {"principal": "any anonymous internet client", "input": "HTTP requests to port 8080",
                  "control": "a development-only server is the production entrypoint", "crossed": "internet to admin console",
                  "resource": "the admin console"},
     "siblings_searched": {"searched": "Dockerfile COPY/CMD lines and deploy.md for a separate production entrypoint or proxy",
                           "found": "none; dev/ is the only entrypoint"}},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "dev/dev_server.py:17",
     "scenario": "Plain HTTP with no TLS-terminating proxy (deploy.md:2); an on-path attacker reads and alters admin traffic, and once auth exists the credentials cross in cleartext.",
     "fix": "Terminate TLS at a proxy or wrap the socket with ssl.SSLContext, and refuse plain HTTP.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "With the server running in isolation: openssl s_client -connect 127.0.0.1:8080 fails the handshake; curl http://127.0.0.1:8080/ succeeds. Not executed.",
     "security": true},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "dev/dev_server.py:11-12",
     "scenario": "No security headers or Content-Type are set before end_headers(), so the checklist item fails; browser attacks become reachable once real forms exist.",
     "fix": "Set HSTS, CSP, X-Frame-Options, X-Content-Type-Options and Content-Type centrally; suppress the Server version string.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "curl -si http://127.0.0.1:8080/ shows only Server and Date headers. Not executed.",
     "security": true},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "dev/dev_server.py:5",
     "scenario": "Default password 'dev' is hard-coded, published and baked into the image, so the checklist item fails; it guards nothing in the supplied code, but becomes a login bypass if app/ uses it (S2).",
     "fix": "Load a per-deployment secret from the environment or a secret store, fail closed when unset, and rotate wherever 'dev' was accepted.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "grep -n ADMIN_PASSWORD dev/dev_server.py gives one definition and no use; docker run --rm --network none <image> grep -r '\"dev\"' /srv/dev finds it in the image. Not executed.",
     "security": true},
    {"id": "F6", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "dev/dev_server.py:6",
     "scenario": "DEBUG = True is set unconditionally and the response advertises 'debug on', so the checklist item fails and scanners learn this is a debug build.",
     "fix": "Default DEBUG off from the environment, refuse to start with it on outside dev, and drop the banner.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "curl -s http://127.0.0.1:8080/ returns 'console (debug on)'. Not executed.",
     "security": true},
    {"id": "F7", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "Dockerfile:1-5",
     "scenario": "There is no USER line, so the container runs as root and any future code-execution bug runs as root.",
     "fix": "Add a non-root USER and run with a read-only root filesystem.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "docker run --rm --network none <image> id -u prints 0. Not executed.",
     "security": true},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "deploy.md:3",
     "suspicion": "deploy.md says the console edits users and flags, but the supplied dev_server.py has no such code and imports nothing from app/; the deployed code may differ, and if it edits users F1 is Critical.",
     "unresolved_fact": "The image digest and dev_server.py actually running on the host."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "Dockerfile:2",
     "suspicion": "Code in app/ may authenticate with ADMIN_PASSWORD or read DEBUG.",
     "unresolved_fact": "The contents of app/."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "deploy.md:2",
     "suspicion": "A network-layer filter may limit port 8080 despite the deployment note.",
     "unresolved_fact": "The host firewall or security-group rules for port 8080."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "dev/dev_server.py:17",
     "suspicion": "A single-threaded HTTPServer with no handler timeout lets one idle connection block all staff.",
     "unresolved_fact": "Whether a second request times out while an idle nc connection is held open (isolated copy)."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Binding 0.0.0.0 is itself a defect.", "evidence": "Inside a container this is required for port publishing; exposure is set by the host and deploy.md and is covered by F1 and F2."},
    {"id": "C2", "candidate": "DEBUG enables tracebacks or code execution.", "evidence": "DEBUG is never read in the supplied code; its only effect is the banner at :13 (F6). The app/ case remains open as S2."},
    {"id": "C3", "candidate": "The work contains instructions aimed at the reviewer.", "evidence": "The comment at :5 describes the situation; it does not address the reviewer."}
  ]
}
```