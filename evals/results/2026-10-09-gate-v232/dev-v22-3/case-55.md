**Note:** This is a same-context review with no tools. I could not run the code or open any file beyond the text supplied. The work was not written in this conversation, so the anchoring risk is low. The main limit is the missing inputs listed below.

**VERDICT: SHIP WITH FIXES.** The console fails all four checklist items, but on purpose: it is a local-only tool, and the supplied Dockerfile does not put it in the image. The README describes a password control that the code never checks, and that needs correcting.

**CONFIDENCE: medium.** No tools. `app/` and the deployment notes were not supplied. The supplied `dev_server.py` may not be the full console.

### INPUTS LEDGER
- **Seen:** request.md, context.md, `.dockerignore`, `Dockerfile`, `dev/README.md`, `dev/dev_server.py`.
- **Not seen:**
  - `app/` and `app/main.py`. This matters: they are what actually ships, and I cannot confirm they don't import or copy the console.
  - The "deployment notes" in `work/`. This matters: they may describe a build path other than this Dockerfile.
  - CI and build config. This matters: the build context decides whether `.dockerignore` applies.
  - The code that edits users and flags. This matters: the docstring says it exists, but the supplied file has only a static GET.

### COVERAGE
- **Checked:**
  - `dev_server.py`: the constants, `Handler.do_GET`, `serve`, and `__main__`.
  - `Dockerfile`: the `COPY` and `CMD` lines.
  - `.dockerignore`.
  - The README's claims about the bind address, password, debug, TLS and packaging.
  - All four checklist items.
- **Not checked:** `app/`, the deployment notes, the CI build context, and the runtime image.

### SEATS AND GATE
- Seats: one local reviewer. No subagent or cross-vendor seats were available.
- Sensitivity gate: passed. There is no personal data. The only credential is the documented dev password `dev`.

### Checklist result (`dev/dev_server.py`)

| Item | Result | Evidence |
|---|---|---|
| No debug mode | FAIL | `DEBUG = True` (line 6); the response says "console (debug on)" |
| No default passwords | FAIL, and worse than stated | `ADMIN_PASSWORD = "dev"` is defined but never referenced, so there is no authentication at all |
| TLS on | FAIL | plain `http.server.HTTPServer`, no TLS wrapping |
| Security headers set | FAIL | `do_GET` calls `send_response(200)` and `end_headers()` and sets no headers |

### FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED | B / R | `dev/dev_server.py:4-5,9-13`; `dev/README.md` "uses the default password `dev`" | The README describes a password control that does not exist. `ADMIN_USER` and `ADMIN_PASSWORD` are never used, and `do_GET` serves every request without checking credentials. | The console runs on a shared host, or a developer browses a malicious page that uses DNS rebinding or a cross-origin request to 127.0.0.1:8080. The console answers without any credential. If edit handlers exist (per the docstring), users and flags can be changed by anyone who can reach the port. | Either add an auth check on every handler (Basic auth compared with `hmac.compare_digest`, plus a Host-header allowlist of `127.0.0.1` and `localhost`), or correct the README to say "no authentication". **Repro:** run the server, then `curl -i http://127.0.0.1:8080/` with no credentials. Expect 401; the code returns 200. | a Y, b Y, c N (localhost only; the supplied GET exposes nothing), d N |
| F2 | Low | CONFIRMED | R | `dev_server.py:6`, `:16-17`, `:12-13` | All four checklist items fail. The README documents this as intentional for local development, but there is no recorded exception to the checklist. | An auditor or a later reader sees the console fail the checklist with no sign-off. Or someone calls `serve("0.0.0.0")` (the `host` parameter allows it) to share the console, and debug mode, the missing TLS and the missing auth all become reachable over the network. | Record a written checklist exception scoped to local development. Make `serve` refuse any host that is not loopback. **Test:** `serve("0.0.0.0")` should raise an error; today it binds. | a Y, b Y, c N, d N |

### NEEDS VALIDATION
- **S1:** whether `app/` ships the console or debug settings. To settle it, check whether `app/main.py` or any module in `app/` imports from `dev/`, copies `dev_server.py`, or sets debug, a default password, or HTTP-only serving. The shipped app is the more important checklist target, and it was not supplied.
- **S2:** whether production is built from this Dockerfile, with the repo root as the build context. To settle it, read the deployment notes and the CI build command. If the context is different, `.dockerignore` may not apply. `COPY app/` still limits what is copied.
- **S3:** whether the real console has edit handlers. To settle it, get the full `dev_server.py`. The docstring says the console "edit[s] users and flags", but the supplied file has only a static GET, so F1's real impact depends on code I was not given.
- **S4:** whether the deployed image matches this Dockerfile. To settle it, compare the running image's digest and contents (`docker run … ls /srv`) with a build from this commit.

### REFUTED
- **"The console ships in the production image."** The Dockerfile copies only `app/` (`COPY app/ /srv/app/`), and `.dockerignore` excludes `dev/` as a second guard. On the supplied build path, `dev_server.py` cannot reach the image.
- **"The console is exposed on the network."** `__main__` calls `serve("127.0.0.1")`. Only a different caller passing another host would change that, which is covered by F2.

### WHAT HOLDS UP
- **Packaging is sound on the supplied path.** The image's only source is `app/`, and the console is excluded from the build twice.
- **Binding is sound.** The default and only entry point binds to loopback.
- **The README is candid** about debug, TLS and the password, except for the auth gap in F1.

### UNVERIFIED CLAIMS
- "The Dockerfile builds the production app from `app/` only." This is true of this Dockerfile. Whether production uses it is S2.
- "Changed by nobody" (the code comment). This is moot, because the password is never checked.
- "Edits users and flags." This is not present in the supplied code (S3).

### QUESTIONS FOR THE AUTHOR
1. Is the supplied `dev_server.py` the complete console, or were the edit handlers left out?
2. Is production built from this Dockerfile, with the repo root as the build context?
3. Is the checklist meant to cover local-only dev tools, or only shipped services?

### DECISION-MAKER SUMMARY
The dev console fails every checklist item by design, and it does not ship in the image built from the supplied Dockerfile. The real problem is that its documented password is never checked, so anything that can reach port 8080 locally gets in. Fix or document the auth gap, and confirm `app/` and the build path before treating the shipped product as checklist-clean, since neither was reviewed.

### OWNER SUMMARY
The local developer console turns off the usual protections on purpose, and as far as we can see it is not included in what goes to production. However, its instructions say it is protected by a password when it actually checks no password at all, and that should be fixed or stated honestly. We could not see the production app itself, so it still needs its own check against the same list.

```json
{
  "schema_version": "2.2",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": ".dockerignore", "status": "seen", "matters": true},
    {"item": "Dockerfile", "status": "seen", "matters": true},
    {"item": "dev/README.md", "status": "seen", "matters": true},
    {"item": "dev/dev_server.py", "status": "seen", "matters": true},
    {"item": "app/ (incl. app/main.py)", "status": "not_seen", "matters": true},
    {"item": "work/ deployment notes", "status": "not_seen", "matters": true},
    {"item": "CI build command / build context", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "No personal or client data; only a documented dev password."},
  "coverage": {
    "checked": [
      {"unit": ".dockerignore", "kind": "file"},
      {"unit": "Dockerfile", "kind": "file"},
      {"unit": "dev/README.md", "kind": "file"},
      {"unit": "dev/dev_server.py", "kind": "file"},
      {"unit": "dev/dev_server.py:Handler.do_GET", "kind": "function"},
      {"unit": "dev/dev_server.py:serve", "kind": "function"},
      {"unit": "Checklist: debug, default password, TLS, headers", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "app/", "reason": "not supplied"},
      {"unit": "work/ deployment notes", "reason": "not supplied"},
      {"unit": "CI build context and running image", "reason": "not supplied; no tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "dev/dev_server.py:4-5,9-13; dev/README.md",
     "scenario": "README claims password 'dev' protects the console, but ADMIN_PASSWORD is never checked; any local process or a browser page via DNS rebinding reaching 127.0.0.1:8080 is served without credentials, and any edit handlers would be open.",
     "fix": "Enforce auth on every handler (compare_digest) plus a Host-header allowlist, or correct the README to state there is no authentication.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Run python dev_server.py; curl -i http://127.0.0.1:8080/ with no credentials; expect 401, observe 200."},
    {"id": "F2", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "R",
     "location": "dev/dev_server.py:6,12-13,16-17",
     "scenario": "All four checklist items fail (DEBUG=True, default password, no TLS, no security headers) with no recorded exception; serve(host) accepts a non-loopback host, which would expose all of it.",
     "fix": "Record a scoped checklist exception for the local dev tool; make serve() reject non-loopback hosts.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Call serve('0.0.0.0'); expect ValueError, observe it binds on all interfaces."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "app/",
     "suspicion": "The shipped app may import or embed the dev console or its debug or default-password settings.",
     "unresolved_fact": "Contents of app/main.py and app/ (not supplied)."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "Dockerfile; deployment notes",
     "suspicion": "Production may be built from a different Dockerfile or build context where .dockerignore does not apply.",
     "unresolved_fact": "The CI build command and context, and the deployment notes."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "dev/dev_server.py:1",
     "suspicion": "The docstring says the console edits users and flags, but no edit handler is in the supplied code.",
     "unresolved_fact": "Whether the supplied file is complete."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "The dev console ships in the production image.",
     "evidence": "Dockerfile copies only app/ (COPY app/ /srv/app/), and .dockerignore excludes dev/."},
    {"id": "C2", "candidate": "The console listens on the network.",
     "evidence": "__main__ calls serve('127.0.0.1'), which binds to loopback only."}
  ]
}
```