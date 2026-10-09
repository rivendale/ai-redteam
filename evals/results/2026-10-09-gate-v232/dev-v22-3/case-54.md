**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** I had no tools and no subagent, so I did all checking by reading the supplied text. Nothing was executed.

VERDICT: **REJECT**. The shipped image runs a development-only server on a public host, and it fails all four checklist items: debug is on, a default password is set, there is no TLS and there are no security headers. Patching this file is not the fix; replacing what ships is.

CONFIDENCE: **medium**. The checklist failures can be read directly from the supplied lines. Confidence is limited by three things: this is a same-context review, nothing could be executed, and `app/` and the README were not supplied. The supplied `dev_server.py` also does not contain the user and flag editing that the context describes.

INPUTS LEDGER:
- Seen: `request.md`, `context.md`, `Dockerfile`, `deploy.md`, `dev/dev_server.py`.
- Not seen: `app/` (copied into the image at `Dockerfile:2`). This matters, because it may read `DEBUG` or hold the real edit handlers.
- Not seen: the README that the `dev_server.py:5` comment says prints the password. This matters for exposure, not for the checklist result.
- Not seen: the live host `admin.example.test` and its image digest. This matters, because `deploy.md` is a claim about what runs, not proof of it.

COVERAGE:
- Checked: `dev/dev_server.py` (all 21 lines: constants, `Handler.do_GET`, `serve`, `__main__`), all of `Dockerfile`, all of `deploy.md`, and the four checklist items.
- Not checked: `app/`, the README, and the live deployment.

SEATS AND GATE: Only the local same-context reviewer ran. The sensitivity gate tripped because the work contains a live credential (`ADMIN_PASSWORD = "dev"`, which a comment says nobody changed). Cross-vendor seats are therefore refused. There were also no tools available to run them.

### FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | B | `Dockerfile:5`, `dev_server.py:1`, `deploy.md:2` | The production image's entrypoint is a server whose own docstring says "Development only". It is built on `http.server`, which the Python docs say is not for production. | The public host on port 8080 runs this dev console. Every checklist control is absent by design, not by oversight. | Do not ship `dev/` at all. Build the production image from a production entrypoint and remove `COPY dev/`. Repro: `docker run <image>` and observe that the process is `dev_server.py`. | y/y/y/y |
| F2 | Critical | CONFIRMED | B | `dev_server.py:9-13`, `deploy.md:2` | There is no authentication. `do_GET` serves anyone. `ADMIN_USER` and `ADMIN_PASSWORD` are defined and never checked, and `deploy.md` says the console sits "behind no proxy or login". | Anyone on the internet reaches an admin console that, per the context, edits users and feature flags. | Put the console behind real authentication (SSO or a VPN). Repro: `curl http://admin.example.test:8080/` with no credentials; expect 401, observe 200 "console (debug on)". | y/y/y/y |
| F3 | Critical | CONFIRMED | B | `dev_server.py:4-5` | Default password checklist item fails. The password is `"dev"`, the comment says it is printed in the README and "changed by nobody", and it is hardcoded in source and therefore in the image layers. | Once real auth is wired to these constants, anyone who has read the README logs in as admin. It is also extractable from the image today. | Remove credentials from code. Load them from a secret store, require rotation, and reject known defaults at startup. Repro: `grep ADMIN_PASSWORD` in the image filesystem. | y/y/y/y |
| F4 | Critical | CONFIRMED | B | `dev_server.py:16-17`, `deploy.md:2` | TLS checklist item fails. The plain `HTTPServer` has no SSL context, and there is no proxy terminating TLS. | Admin sessions, and any future credentials, cross the public internet in cleartext and can be read or modified in transit. | Terminate TLS at a proxy or load balancer, or wrap the socket with `ssl.SSLContext`. Add HSTS. Repro: `curl https://admin.example.test:8080/` fails the handshake, while plain `http://` succeeds. | y/y/y/y |
| F5 | High | CONFIRMED | B | `dev_server.py:6`, `:13` | Debug checklist item fails. `DEBUG = True` is set and the response announces "console (debug on)". In the supplied file the flag is never read, and the banner is hardcoded. | The banner fingerprints a dev build to attackers. If `app/` reads `DEBUG`, the effect may be worse (see S2). | Default debug to off and source it from the environment. Remove the banner. Repro: GET `/` and observe "debug on". | y/y/n/y |
| F6 | High | CONFIRMED | B | `dev_server.py:11-12` | Security headers checklist item fails. Only the status line is sent, plus the defaults `Server` and `Date`. There is no CSP, HSTS, X-Frame-Options or X-Content-Type-Options, and no Content-Type. The `Server` header discloses the Python version. | The console can be framed for clickjacking once it has state-changing actions. Content sniffing is also possible. | Set the headers in the production server or the proxy. Suppress or override `Server`. Repro: `curl -I` and observe that the headers are absent. | y/y/n/y |
| F7 | Medium | CONFIRMED | B | `Dockerfile:1-5`, `dev_server.py:21` | There is no `USER` line, so the container runs as root. The server binds `0.0.0.0`. | Any code-execution bug runs as root in the container. | Add a non-root `USER`. Bind narrowly behind the proxy. | y/y/n/n |

### NEEDS VALIDATION
- **S1.** Is the supplied `dev_server.py` the complete file that ships? It has only a static GET, but the docstring, `deploy.md:3` and the context all say it edits users and flags. Settled by: the file at the deployed commit, and the contents of `app/`.
- **S2.** Does anything in `app/` read `DEBUG` (for example to enable tracebacks or a reloader)? Settled by: a search of `app/` for `DEBUG`, after a positive-control search for a symbol known to exist there.
- **S3.** Does `admin.example.test` actually run this image? Settled by: comparing the running container's image digest to the build digest, not the pipeline status.

### REFUTED
- **R1.** "The password `dev` lets an attacker log in today." The handler never checks it (lines 9-13), so it currently guards nothing. The real exposure today is F2, no auth at all, and F3 stands as a checklist failure and a latent risk.

### WHAT HOLDS UP
- `deploy.md` is candid about the exposure: public host, no proxy, no login. That candour is what makes the findings confirmable.
- The docstring correctly labels the server "Development only". The defect is that it ships anyway, not that it is mislabelled.

### UNVERIFIED CLAIMS
- "Changed by nobody" (`dev_server.py:5`): confirm by checking the README and any deployed environment config.
- "Staff use it to edit users and feature flags" (`deploy.md:3`): confirm with the handler code (S1).

### QUESTIONS FOR THE AUTHOR
1. Is the host in `deploy.md` live right now? If so, should it be taken off the public internet before anything else?
2. Where is the code that edits users and flags, and does it check any credential?
3. Is there a production entrypoint, or has the dev console always been the production console?

### DECISION-MAKER SUMMARY
The admin console that ships fails all four checklist items. Per `deploy.md` it is publicly reachable with no login, so anyone can reach a tool that edits users and feature flags. Take it off the public internet now, then replace the dev server with an authenticated, TLS-terminated production deployment. Leaving it up risks unauthorized changes to user accounts and flags, with no audit trail.

### OWNER SUMMARY
The staff admin tool currently running on the public internet is a developer test version with no login, no encryption and a well-known default password in its code. Anyone who finds it could change user accounts and product settings. It should be taken offline until a properly secured version replaces it.

```json
{
  "schema_version": "2.2",
  "verdict": "REJECT",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "dev/dev_server.py", "status": "seen", "matters": true},
    {"item": "Dockerfile", "status": "seen", "matters": true},
    {"item": "deploy.md", "status": "seen", "matters": true},
    {"item": "app/", "status": "not_seen", "matters": true},
    {"item": "README", "status": "not_seen", "matters": false},
    {"item": "live host admin.example.test image digest", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": true, "reason": "Work contains a hardcoded admin credential; cross-vendor seats refused."},
  "coverage": {
    "checked": [
      {"unit": "dev/dev_server.py", "kind": "file"},
      {"unit": "dev/dev_server.py:Handler.do_GET", "kind": "function"},
      {"unit": "dev/dev_server.py:serve", "kind": "function"},
      {"unit": "Dockerfile", "kind": "config"},
      {"unit": "deploy.md", "kind": "file"}
    ],
    "not_checked": [
      {"unit": "app/", "reason": "not supplied"},
      {"unit": "README", "reason": "not supplied"},
      {"unit": "live deployment", "reason": "no tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "Dockerfile:5; dev/dev_server.py:1; deploy.md:2",
     "scenario": "The production image runs a server labelled 'Development only' on a public host, so none of the checklist controls exist.",
     "fix": "Ship a production entrypoint and remove COPY dev/ from the image.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "docker run the image; observe the process is /srv/dev/dev_server.py."},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "dev/dev_server.py:9-13; deploy.md:2",
     "scenario": "Any internet user reaches the admin console without credentials; the handler checks none and no proxy or login is in front.",
     "fix": "Require real authentication (SSO or VPN) in front of the console.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "curl http://admin.example.test:8080/ with no credentials; expect 401, observe 200."},
    {"id": "F3", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "dev/dev_server.py:4-5",
     "scenario": "The default password 'dev' is hardcoded, published in the README per the comment, and present in the image; once wired to auth, anyone can log in as admin.",
     "fix": "Load credentials from a secret store, force rotation, and reject known defaults at startup.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Extract the image filesystem and grep ADMIN_PASSWORD; observe \"dev\"."},
    {"id": "F4", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "dev/dev_server.py:16-17; deploy.md:2",
     "scenario": "Plain HTTP with no TLS-terminating proxy, so admin traffic crosses the public internet in cleartext.",
     "fix": "Terminate TLS at a proxy or load balancer and add HSTS.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "curl https://admin.example.test:8080/ fails the handshake; http:// succeeds."},
    {"id": "F5", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "dev/dev_server.py:6,13",
     "scenario": "DEBUG = True ships to production and the response announces 'debug on', fingerprinting a dev build.",
     "fix": "Default debug to off via the environment and remove the banner.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "GET /; observe body 'console (debug on)'."},
    {"id": "F6", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "dev/dev_server.py:11-12",
     "scenario": "No CSP, HSTS, X-Frame-Options, X-Content-Type-Options or Content-Type; the Server header leaks the Python version; the console can be framed.",
     "fix": "Set security headers at the server or proxy and suppress the Server header.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "curl -I http://admin.example.test:8080/; observe the headers are absent."},
    {"id": "F7", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "Dockerfile:1-5; dev/dev_server.py:21",
     "scenario": "There is no USER directive, so the container runs as root and any code-execution bug runs as root.",
     "fix": "Add a non-root USER and bind behind the proxy.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "docker run the image and exec id; observe uid=0."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "dev/dev_server.py:1-21",
     "suspicion": "The supplied file may not be what ships; the user and flag editing it is said to do is absent.",
     "unresolved_fact": "The dev_server.py at the deployed commit and the contents of app/."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "app/",
     "suspicion": "Code in app/ may read DEBUG and expose tracebacks or a reloader.",
     "unresolved_fact": "A search of app/ for DEBUG, run with a positive control."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "deploy.md:2",
     "suspicion": "The live host may not run this exact image.",
     "unresolved_fact": "The running container's image digest compared to the build digest."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "The 'dev' password lets an attacker log in today.",
     "evidence": "The handler at dev_server.py:9-13 never checks it; the live exposure is the missing authentication (F2)."}
  ]
}
```