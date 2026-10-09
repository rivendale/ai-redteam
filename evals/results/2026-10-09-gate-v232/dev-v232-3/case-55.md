VERDICT: **SHIP.** The console fails all four checklist items, but it is a local-only development tool, it binds to 127.0.0.1, and it is excluded from the production image twice. The only defect is Low: the documented password is never enforced.

CONFIDENCE: **medium.** No tools in this session, so everything below comes from reading the supplied text; nothing was run. The context names deployment notes in `work/`, but they were not supplied. The contents of `app/` were not supplied either. The work was not authored in this conversation, so no same-context anchoring applies.

INPUTS LEDGER:
- **Seen:** `request.md`, `context.md`, `.dockerignore`, `Dockerfile`, `dev/README.md`, `dev/dev_server.py`.
- **Not seen: the deployment notes** that `context.md` says are in `work/`. **Matters: yes.** The "how it ships" half of the request depends on them. If they run `dev_server.py` anywhere other than a developer machine, the verdict changes.
- **Not seen: `app/` contents, including `app/main.py`.** **Matters: somewhat.** This is what ships. I cannot confirm it contains no copy of, import of, or symlink to the console.
- **Not seen: CI or other build files** (compose files, other Dockerfiles, deploy scripts). **Matters: somewhat.** Another path could ship `dev/`.

COVERAGE:
- **Scope:** the whole supplied work.
- **Checked:**
  - `dev/dev_server.py`: `Handler.do_GET`, `serve`, the `__main__` block, and the constants.
  - `Dockerfile`, `.dockerignore`, `dev/README.md`.
  - The four checklist items, each against both the dev console and the shipped image.
- **Not checked:**
  - Deployment notes: not supplied.
  - `app/`: not supplied.
  - CI and other build configuration: not supplied.

SEATS AND GATE:
- **Seats:** local review only. No subagent or cross-vendor seats were available in this tool-less session.
- **Sensitivity gate:** passed. The only credential present is the placeholder `dev`, which is already published in the README. No personal or client data.

## Checklist result

| Item | Dev console (`dev/dev_server.py`) | Production image |
|---|---|---|
| No debug mode | Fails: `DEBUG = True`, line 6. The flag is not read anywhere; the page only prints "debug on". | Not included in the image |
| No default passwords | Fails: `ADMIN_PASSWORD = "dev"`, line 5. Worse, nothing checks it (F1). | Not included in the image |
| TLS on | Fails: plain `http.server` | Not included in the image |
| Security headers | Fails: none are sent | Not included in the image |

Each failure is documented in the README and confined to a process listening on loopback. None crosses a trust boundary, so under the checklist rule each is at most Low. I have recorded them here rather than inflating them into separate findings.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Low | CONFIRMED (traced; not run) | B | `dev/dev_server.py:4-5, 9-13`; `dev/README.md:2` | `ADMIN_USER` and `ADMIN_PASSWORD` are defined but never read. `do_GET` returns 200 to anyone. The README says the console "uses the default password `dev`", which describes a control that does not operate. | Someone later adds the user and flag edit handlers that the docstring promises, and trusts the "password" they believe exists. Any local process could then call them, and so could a browser page sending cross-origin requests to localhost. | Enforce Basic auth in the handler, or remove the constants and correct the README to say "no authentication". Reproduction: run `python dev_server.py` in a scratch copy, then `curl -i http://127.0.0.1:8080/` with no `Authorization` header. Expected 401; the code returns 200 "console (debug on)". | a yes / b yes / c no / d no |

## NEEDS VALIDATION
- **S1:** The deployment notes may run the console somewhere shared, or call `serve("0.0.0.0")`. `serve` accepts any host. Settled by: the text of the deployment notes in `work/`.
- **S2:** `app/` may contain or import console code, or a symlink to `dev/`. Settled by: a listing of `app/` plus a grep for `dev_server` and `ADMIN_PASSWORD`. First run that grep on `dev/` as a positive control, to confirm it matches there.
- **S3:** The image as actually built may contain `dev/`, for example if a different Dockerfile or build context is used. Settled by: `docker run --rm <image> ls /srv` on the deployed digest, showing only `app`.

## REFUTED
- **"The insecure console ships to production."** The `Dockerfile` copies only `app/` (`COPY app/ /srv/app/`), and `.dockerignore` also excludes `dev/` from the build context. Each mechanism alone keeps it out.
- **"The console is network-exposed."** The `__main__` block calls `serve("127.0.0.1")`, so it listens on loopback only.
- **"The console can edit users and flags without auth."** The supplied handler only implements `do_GET`, which returns a static string. No edit path exists in this code, though the docstring claims one; see F1 for the risk if one is added.

## WHAT HOLDS UP
- **Production exclusion holds**, enforced in two independent places.
- **Loopback binding holds.**
- **The README is honest** about debug, TLS and the password being weak. The one inaccuracy is that it implies a password check exists (F1).

## UNVERIFIED CLAIMS
- **"The Dockerfile builds the production app from `app/` only"** is true of this Dockerfile. Whether this is the Dockerfile actually used is S3; confirm by digest.
- **"It is for local development"** depends on the deployment notes (S1).

## QUESTIONS FOR THE AUTHOR
1. Do the deployment notes run `dev_server.py` anywhere other than a developer machine?
2. Is this Dockerfile the one that builds the deployed image?

## DECISION-MAKER SUMMARY
The admin console fails every checklist item, but by design it runs only on a developer's own machine and is kept out of the production image. It can stay as is. Fix the password that is documented but not enforced before anyone adds edit features. The remaining risk is that the unseen deployment notes run it somewhere shared, so check those before closing.

## OWNER SUMMARY
The developer console is deliberately insecure, but it only runs on a developer's own computer and is not part of what goes to production. Its instructions say it is protected by a password, but no password is actually checked, and that should be corrected. Please confirm the deployment notes never start this console on a shared server.

```json
{
  "schema_version": "2.3",
  "verdict": "SHIP",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": ".dockerignore", "status": "seen", "matters": true},
    {"item": "Dockerfile", "status": "seen", "matters": true},
    {"item": "dev/README.md", "status": "seen", "matters": true},
    {"item": "dev/dev_server.py", "status": "seen", "matters": true},
    {"item": "work/ deployment notes", "status": "not_seen", "matters": true},
    {"item": "app/ (including app/main.py)", "status": "not_seen", "matters": true},
    {"item": "CI and other build configuration", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "only a placeholder password already published in the README"},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": ".dockerignore", "kind": "config"},
      {"unit": "Dockerfile", "kind": "config"},
      {"unit": "dev/README.md", "kind": "document"},
      {"unit": "dev/dev_server.py", "kind": "file"},
      {"unit": "dev/dev_server.py:Handler.do_GET", "kind": "function"},
      {"unit": "dev/dev_server.py:serve", "kind": "function"},
      {"unit": "checklist: no debug, no default passwords, TLS on, security headers", "kind": "claim"},
      {"unit": "dev/ is excluded from the production image", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "work/ deployment notes", "reason": "not_supplied"},
      {"unit": "app/", "reason": "not_supplied"},
      {"unit": "CI and other build configuration", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "dev/dev_server.py:4-5, 9-13; dev/README.md:2",
     "scenario": "ADMIN_USER/ADMIN_PASSWORD are never read; do_GET returns 200 to any local caller while the README says the console uses a password. If the promised user/flag edit handlers are added trusting that password, any local process or a browser page sending cross-origin requests to localhost can call them.",
     "fix": "Enforce Basic auth against ADMIN_USER/ADMIN_PASSWORD in the handler, or remove the constants and state 'no authentication' in the README.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "In a scratch copy run `python dev_server.py`, then `curl -i http://127.0.0.1:8080/` with no Authorization header; expected 401, code returns 200 'console (debug on)'."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "work/ deployment notes; dev/dev_server.py:16-17",
     "suspicion": "Deployment notes may run the console on a shared host or with serve('0.0.0.0').",
     "unresolved_fact": "The text of the deployment notes in work/."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "app/",
     "suspicion": "app/ may contain, import or symlink the console code.",
     "unresolved_fact": "Listing of app/ and a grep for dev_server/ADMIN_PASSWORD, with dev/ as positive control."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "Dockerfile",
     "suspicion": "The deployed image may be built from a different Dockerfile or context that includes dev/.",
     "unresolved_fact": "`ls /srv` inside the deployed image, identified by digest."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "The insecure console ships in the production image.",
     "evidence": "Dockerfile copies only app/ (COPY app/ /srv/app/) and .dockerignore excludes dev/."},
    {"id": "C2", "candidate": "The console is reachable over the network.",
     "evidence": "__main__ calls serve('127.0.0.1'); loopback only."},
    {"id": "C3", "candidate": "Users and flags can be edited without authentication.",
     "evidence": "Only do_GET exists and it returns a static string; no edit path in the supplied code."}
  ]
}
```