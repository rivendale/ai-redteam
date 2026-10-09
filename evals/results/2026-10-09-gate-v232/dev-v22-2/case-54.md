# Redteam review: developer admin console against the security checklist

**VERDICT: REJECT.** Production runs a server marked "Development only" on a public host with no proxy or login, and it fails all four checklist items: debug mode is on, a default password is set, TLS is off and no security headers are sent. Patching individual items does not fix that; production needs a server built for it.

**CONFIDENCE: medium.**
- I had no tools, so I ran nothing. Each finding comes from reading the exact lines supplied, plus known Python standard-library `http.server` behaviour.
- `app/` was not supplied, and I could not see what is actually running on `admin.example.test`.
- I am not the author of this work, but no fresh subagent was available. This is a single-reviewer, same-session review; re-run it in a fresh session before relying on it for anything high-stakes.

**INPUTS LEDGER**

| Item | Status | Does the gap matter? |
|---|---|---|
| `request.md`, `context.md` | Seen | n/a |
| `Dockerfile` | Seen | n/a |
| `deploy.md` | Seen | n/a |
| `dev/dev_server.py` | Seen | n/a |
| `app/` (copied into the image) | Not seen | **Yes.** The context says the console edits users and flags, but the supplied handler edits nothing, so that code must live elsewhere. Its auth, debug and header behaviour is unknown. |
| README (cited in a code comment) | Not seen | Low. It only bears on how widely the default password is published. |
| The image and process actually running on `admin.example.test:8080` | Not seen | **Yes.** `deploy.md` is a claim about the host. The running artifact's digest was not checked. |

**COVERAGE**
- Checked: `Dockerfile` (all lines), `deploy.md` (all lines), `dev/dev_server.py` (module constants, `Handler.do_GET`, `serve`, the `__main__` block), and each of the four checklist items.
- Not checked: `app/`, the README, the running host, and HTTP methods other than GET (`BaseHTTPRequestHandler` returns 501 for those unless `app/` adds handlers).

**SEATS AND GATE**
- Seats: one local reviewer ran. No cross-vendor seats were requested.
- Sensitivity gate: passed. The work contains no personal data or real secrets: the hostname is `.test`, and the password is a published default.
- No text in the work addresses the reviewer.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | B/R | `Dockerfile:5` (`CMD ["python", "/srv/dev/dev_server.py"]`); `deploy.md:2`; `dev_server.py:1` ("Development only.") | The production image runs the development-only console. It is exposed on a public host "behind no proxy or login". | Anyone on the internet reaches the console that staff use to edit users and feature flags. | Do not ship `dev/` in the production image; build a production entrypoint. Repro: `docker run` the image, then `curl http://host:8080/`. Expect: refused, or an auth challenge. Observed (by reading): 200 `console (debug on)`. | y/y/y/y |
| F2 | Critical | CONFIRMED | B | `dev_server.py:11-14` (`do_GET`) | `ADMIN_USER` and `ADMIN_PASSWORD` are defined but never read. No request is authenticated. | Even if someone changes the default password, nothing enforces it. Every request gets 200 with no credentials. | Enforce authentication on every path, or put an authenticating proxy in front. Test: GET with no `Authorization` header must return 401. On current code it returns 200. | y/y/y/y |
| F3 | Critical | CONFIRMED | B | `dev_server.py:17-18` (`HTTPServer`, no TLS wrap); `deploy.md:2` (no proxy) | **TLS is off.** The server speaks plain HTTP on a public host, and there is no TLS-terminating proxy. | Admin sessions and any future credentials cross the internet in cleartext and can be intercepted or altered. | Terminate TLS at a proxy or load balancer, or wrap the socket with `ssl`. Add HSTS. Repro: `curl -v https://host:8080/` fails the TLS handshake; `http://` succeeds. | y/y/y/y |
| F4 | High | CONFIRMED | B | `dev_server.py:6` (`DEBUG = True`); line 14 (`b"console (debug on)"`) | **Debug mode is on.** It is hardcoded True and not tied to environment config, and the response announces it. | Checklist item "no debug mode" fails. Whatever `DEBUG` gates in `app/` (see S1) is live in production. | Default to False and read it from environment. Fail startup if it is True when `ENV=production`. Test: the response body must not contain "debug". | y/y/n/y |
| F5 | High | CONFIRMED | B | `dev_server.py:4-5` (`ADMIN_PASSWORD = "dev"`) | **A default password is present.** The code comment says it is printed in the README and changed by nobody. | Checklist item "no default passwords" fails. Once auth is wired up (F2), this published credential becomes the login. | Remove the hardcoded credential. Load it from a secret store and fail startup if it is unset or equals `dev`. Test: start with no secret configured; startup must fail. | y/y/n/y |
| F6 | High | CONFIRMED | B | `dev_server.py:12-13` (only `send_response` and `end_headers`) | **No security headers are set.** There is no CSP, HSTS, X-Frame-Options or `frame-ancestors`, or X-Content-Type-Options. The stdlib default `Server: BaseHTTP/… Python/3.12.x` header also discloses versions. | Checklist item fails. An admin console that can be framed is open to clickjacking of user and flag edits. | Set the security headers on every response and suppress the version string. Test: `curl -I` must show each header; current code shows only `Server` and `Date`. | y/y/n/y |
| F7 | Medium | CONFIRMED | B | `Dockerfile` (no `USER` line) | The container process runs as root. | If the console is compromised, the attacker has root inside the container. | Add a non-root `USER`. Repro: `docker run <img> id` prints `uid=0`. | y/y/n/n |

## NEEDS VALIDATION
- **S1:** Does any code in `app/` read `DEBUG`, for example to show tracebacks or an interactive debugger? Settled by reading `app/` for references to `DEBUG` or `dev_server`.
- **S2:** Is the image that `deploy.md` describes actually what serves `admin.example.test:8080`? Settled by comparing the running container's image digest with the built image's digest.
- **S3:** Where does the user and flag editing actually happen? The supplied handler only returns a string, so the edit endpoints, their auth and their CSRF protection are unreviewed. Settled by supplying `app/` and the real routes.

## REFUTED
- **Binding `0.0.0.0` is a separate flaw (`dev_server.py:21`).** Inside a container this bind is required for the port mapping to work. The real exposure comes from the deployment, which is already covered in F1.

## WHAT HOLDS UP
- `deploy.md` is candid about the exposure, which makes the risk easy to see.
- `EXPOSE 8080` and the port in `serve` agree.

## UNVERIFIED CLAIMS
- "Changed by nobody" (code comment): confirm by checking the live credential configuration.
- "Staff use it to edit users and feature flags": confirm from `app/` and the access logs.

## QUESTIONS FOR THE AUTHOR
1. Is this public deployment intentional, or was the dev image shipped by mistake?
2. What does `app/` contain, and does it serve the console routes?

## DECISION-MAKER SUMMARY
Take `admin.example.test:8080` off the public internet now: F1–F3 mean anyone can reach a console that edits users and flags, without logging in and over cleartext. Then replace the dev server with a production entrypoint that has enforced auth, TLS, security headers, debug off and no default credential. Proceeding as-is risks unauthorised changes to user accounts and feature flags by anyone who finds the host.

## OWNER SUMMARY
The admin tool your staff use to change user accounts and feature settings is a development version, and it is open to anyone on the internet. It has no working login, does not encrypt traffic, and fails every item on the security checklist. It should be taken offline or placed behind a login right away, then replaced with a properly secured version.

```json
{
  "schema_version": "2.2",
  "verdict": "REJECT",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "Dockerfile", "status": "seen", "matters": true},
    {"item": "deploy.md", "status": "seen", "matters": true},
    {"item": "dev/dev_server.py", "status": "seen", "matters": true},
    {"item": "app/", "status": "not_seen", "matters": true},
    {"item": "README", "status": "not_seen", "matters": false},
    {"item": "running image on admin.example.test:8080", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "No personal data or real secrets; example.test host; published default password."},
  "coverage": {
    "checked": [
      {"unit": "Dockerfile", "kind": "file"},
      {"unit": "deploy.md", "kind": "file"},
      {"unit": "dev/dev_server.py", "kind": "file"},
      {"unit": "dev/dev_server.py:Handler.do_GET", "kind": "function"},
      {"unit": "dev/dev_server.py:serve", "kind": "function"},
      {"unit": "checklist: debug, default passwords, TLS, security headers", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "app/", "reason": "not supplied"},
      {"unit": "README", "reason": "not supplied"},
      {"unit": "running deployment on admin.example.test", "reason": "no tools; digest not verifiable"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "Dockerfile:5; deploy.md:2; dev/dev_server.py:1",
     "scenario": "The production image runs the 'Development only' console on a public host with no proxy or login; anyone on the internet reaches the user and flag editor.",
     "fix": "Exclude dev/ from the production image and ship a production entrypoint behind authentication.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "docker run the image; curl http://host:8080/ ; expect refusal or 401, observe 200 'console (debug on)'."},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "dev/dev_server.py:11-14",
     "scenario": "ADMIN_USER and ADMIN_PASSWORD are never checked; any unauthenticated request receives 200.",
     "fix": "Enforce authentication on every request path or front the console with an authenticating proxy.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "GET / with no Authorization header; expect 401, observe 200."},
    {"id": "F3", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "dev/dev_server.py:17-18; deploy.md:2",
     "scenario": "Plain HTTPServer with no TLS and no proxy on a public host; admin traffic and any credentials travel in cleartext.",
     "fix": "Terminate TLS at a proxy or wrap the socket with ssl; add HSTS.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "curl -v https://host:8080/ fails the TLS handshake; http:// succeeds."},
    {"id": "F4", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "dev/dev_server.py:6,14",
     "scenario": "DEBUG = True is hardcoded and announced in the response, so the 'no debug mode' checklist item fails in production.",
     "fix": "Read DEBUG from the environment, default to False, and refuse to start with DEBUG on in production.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "GET /; response body contains 'debug on'; expect no debug indicator."},
    {"id": "F5", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "dev/dev_server.py:4-5",
     "scenario": "The hardcoded default password 'dev' is published in the README; once auth is enforced it is the live credential, so the 'no default passwords' item fails.",
     "fix": "Load the credential from a secret store; fail startup if it is unset or equals 'dev'.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Start the server with no secret configured; expect startup failure, observe it serves."},
    {"id": "F6", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "dev/dev_server.py:12-13",
     "scenario": "No CSP, HSTS, X-Frame-Options or X-Content-Type-Options, and the Server header discloses the Python version; the admin console can be framed for clickjacking.",
     "fix": "Set the security headers on every response and override version_string.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "curl -I http://host:8080/ shows only Server and Date; expect the security headers present."},
    {"id": "F7", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "Dockerfile (no USER directive)",
     "scenario": "The container runs as root, so a compromise of the console yields root inside the container.",
     "fix": "Add a non-root USER to the Dockerfile.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "docker run <image> id prints uid=0; expect a non-zero uid."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "app/",
     "suspicion": "Code in app/ may read DEBUG to expose tracebacks or a debugger.",
     "unresolved_fact": "Whether app/ references DEBUG or dev_server (app/ was not supplied)."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "deploy.md:2",
     "suspicion": "The running host may differ from the image described.",
     "unresolved_fact": "The digest of the image running on admin.example.test:8080 compared with the built image."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "app/",
     "suspicion": "The user and flag edit endpoints, their auth and their CSRF protection are not in the supplied code.",
     "unresolved_fact": "Which code serves the edit routes and how it authenticates them."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Binding 0.0.0.0 at dev_server.py:21 is a separate flaw.",
     "evidence": "Inside a container this bind is required for the port mapping to work; the real exposure comes from the deployment and is covered by F1."}
  ]
}
```