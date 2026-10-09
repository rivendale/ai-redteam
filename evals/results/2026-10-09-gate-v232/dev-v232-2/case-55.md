# Redteam report: developer admin console vs. security checklist

**Review conditions.** I had no tools in this session. I read only the four files supplied. I could not run anything, open the deployment notes or inspect `app/`. One reviewer only; no subagent or cross-vendor seats were available.

**VERDICT: SHIP.** The console fails all four checklist items, but that is by design for a loopback-only developer tool, and nothing supplied shows it shipping or being reachable off the developer's machine.

**CONFIDENCE: medium.** Three things limit it:
- The deployment notes the context mentions were not supplied.
- `app/` was not supplied.
- I could not build the image to confirm `dev/` is absent from it.

## INPUTS LEDGER

| Item | Status | Matters? |
|---|---|---|
| `request.md`, `context.md` | seen | — |
| `.dockerignore`, `Dockerfile`, `dev/README.md`, `dev/dev_server.py` | seen | — |
| Deployment notes ("work/ has … the deployment notes") | **not supplied** | **Yes.** This is the main way the console could ship or be exposed (a compose file, a dev container publishing 8080, a run step). |
| `app/` (contents of the production image) | not supplied | **Yes.** If `app/` imports or vendors anything from `dev/`, the `.dockerignore` exclusion does not help. |
| Build invocation (context dir, any `Dockerfile.dockerignore`, CI config) | not supplied | **Yes, moderately.** The claim that the image excludes `dev/` depends on how the image is built. |

## COVERAGE

**Scope:** the dev console file and how it ships, using the four supplied files.

**Checked:**
- `dev/dev_server.py`, every line: constants, `Handler.do_GET`, `serve`, and `__main__`.
- `Dockerfile`, all three lines.
- `.dockerignore`.
- `dev/README.md`, each claim in it.
- Each of the four checklist items.

**Not checked:**
- Deployment notes, `app/` and CI/build config: not supplied.
- Runtime behaviour and the built image contents: no tools.

**SEATS AND GATE:** I was the only reviewer, with no tools, and the work was not produced in this conversation. The sensitivity gate passed: the only credential is a placeholder `dev`, already published in the README. No external seats ran because none were available.

## Checklist status (what was asked)

| Checklist item | `dev/dev_server.py` | Production image (`Dockerfile`) |
|---|---|---|
| No debug mode | **Fails:** `DEBUG = True` (line 6) | Not determinable; `app/` not supplied |
| No default passwords | **Fails:** `ADMIN_PASSWORD = "dev"` (line 5), published in the README. It is also never checked (F1). | Not determinable |
| TLS on | **Fails:** plain `http.server.HTTPServer` (line 17) | Not determinable; no TLS config visible in the Dockerfile, which is normal if TLS terminates upstream |
| Security headers set | **Fails:** no headers, only `end_headers()` (lines 11–12) | Not determinable |

These failures are contained by two things:
- **Loopback bind.** `serve("127.0.0.1")` at line 21.
- **Image exclusion.** The image copies only `app/` (`Dockerfile:2`), and `.dockerignore:1` excludes `dev/` from the build context.

Neither is a crossed trust boundary on the evidence supplied, so none of the failures is above Low.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Low | CONFIRMED | B | `dev/dev_server.py:4-5, 9-13`; `dev/README.md:2` | There is no authentication at all. `ADMIN_USER` and `ADMIN_PASSWORD` are defined but never read. The README says the console "uses the default password `dev`", which is false: it uses none. | Any local process, or another user on a shared host, can reach `127.0.0.1:8080` with no credentials. There is also no `Host` header check, so a web page the developer visits can reach it through DNS rebinding. Today the handler only returns a static string, so nothing is exposed. That changes as soon as the user and flag editing described in the docstring is added. | **Fix:** either enforce the credential in the handler (and reject unexpected `Host` values), or delete the unused constants and correct the README. **Reproduction (not run):** `python dev/dev_server.py`, then `curl -i http://127.0.0.1:8080/` with no auth. Expect 401; the code yields 200 `console (debug on)`. | a ✓ b ✓ c ✗ d ✗ |
| F2 | Low | CONFIRMED | B | `dev/dev_server.py:6, 13` | Debug is on, and the response announces it. | The tool is local only, so impact is nil unless it is exposed. | **Fix:** default `DEBUG` from an environment variable, off by default. **Reproduction (not run):** `curl http://127.0.0.1:8080/` returns `console (debug on)`. | a ✓ b ✓ c ✗ d ✗ |
| F3 | Low | CONFIRMED | B | `dev/dev_server.py:5`; `dev/README.md:2` | A hard-coded default password is published in the README. The comment says it is "changed by nobody". | It only matters if F1 is fixed and the server is exposed: then `admin`/`dev` is a known credential. | **Fix:** read the password from an environment variable and refuse to start without one, or generate one per run and print it. **Reproduction (not run):** `grep -n ADMIN_PASSWORD dev/dev_server.py` shows the literal `"dev"`. | a ✓ b ✓ c ✗ d ✗ |
| F4 | Low | CONFIRMED | B | `dev/dev_server.py:11-12, 17` | There is no TLS and no security headers (CSP, `X-Frame-Options`, `X-Content-Type-Options`). | On loopback, TLS adds little. Missing framing and CSP headers matter once the console has state-changing pages that a malicious page could frame or forge requests to. | **Fix:** add the headers in the handler now; they are cheap. Document that TLS is out of scope for a loopback-only tool. **Reproduction (not run):** `curl -i http://127.0.0.1:8080/` shows no security headers. | a ✓ b ✓ c ✗ d ✗ |

No Critical or High findings. I found nothing supplied that puts the console inside a trust boundary it should not be in.

## NEEDS VALIDATION

- **Do the deployment notes, a compose file or a dev container run `dev_server.py`, publish port 8080, or call `serve("0.0.0.0")`?** `serve()` accepts any host, and only `__main__` pins loopback. If the console is exposed anywhere, F1 becomes High or Critical, because it is an unauthenticated admin console that edits users and flags.
- **Is the supplied `dev_server.py` the real console?** The docstring and context say it edits users and flags, but the code only has a static GET. If a fuller version exists, F1 and F4 need re-rating against it.
- **Does `app/` import from or copy anything in `dev/`?** Does the build use the repository root as context with this `.dockerignore`, and is there no `Dockerfile.dockerignore` overriding it? This settles "`dev/` is not in the image". The positive control would be `docker run --rm <image> ls /srv/app` and a search of the image filesystem for `dev_server`.

## REFUTED

- **"The default password and debug mode ship to production."** `Dockerfile:2` copies only `app/`, and `.dockerignore:1` excludes `dev/`. Nothing in the supplied files puts `dev/` in the image.
- **"The console is network-reachable."** `dev/dev_server.py:21` binds `127.0.0.1`. No supplied file calls `serve` with another host.

## WHAT HOLDS UP

- **Containment.** The loopback bind plus exclusion from the image is the right way to contain a deliberately insecure dev tool.
- **Honest README.** The README states the trade-offs plainly, apart from the auth inaccuracy in F1.
- **Minimal image.** The Dockerfile copies one directory, with no secrets or build args.

## UNVERIFIED CLAIMS

- **"The Dockerfile builds the production app from `app/` only."** Confirm by building the image and listing `/srv/app`.
- **"Listens on 127.0.0.1 only."** True for `__main__`. Confirm that no other caller of `serve()` exists, by searching the repository and the deployment notes.
- **"Edits users and flags."** No such code is present.

## QUESTIONS FOR THE AUTHOR

1. Do the deployment notes or any dev container run this console or publish port 8080?
2. Is this the complete `dev_server.py`, or is the user and flag editing code elsewhere?
3. Is the production image built from the repository root with this `.dockerignore`?

## DECISION-MAKER SUMMARY

The dev console fails every checklist item by design, but on the supplied files it is loopback-only and excluded from the production image, so ship. Before relying on that, check the deployment notes for anything that runs or exposes the console. Fix the missing authentication (F1) before any real edit functionality is added. If the console is exposed anywhere, this becomes an unauthenticated admin console and the verdict changes to REWORK.

## OWNER SUMMARY

The developer console is deliberately insecure, but it only runs on a developer's own machine and is left out of the production build, so it is acceptable as it stands. Despite what its notes say, it currently has no password check at all; that should be fixed before it gains the ability to change users or settings. Someone should confirm that no deployment setup runs this console where others can reach it.

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
    {"item": "deployment notes (work/)", "status": "not_seen", "matters": true},
    {"item": "app/", "status": "not_seen", "matters": true},
    {"item": "build/CI configuration", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Only credential is the published placeholder 'dev'."},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "dev/dev_server.py", "kind": "file"},
      {"unit": "dev/dev_server.py:Handler.do_GET", "kind": "function"},
      {"unit": "dev/dev_server.py:serve", "kind": "function"},
      {"unit": "Dockerfile", "kind": "config"},
      {"unit": ".dockerignore", "kind": "config"},
      {"unit": "dev/README.md", "kind": "document"},
      {"unit": "checklist: no debug, no default passwords, TLS, security headers", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "deployment notes (work/)", "reason": "not_supplied"},
      {"unit": "app/", "reason": "not_supplied"},
      {"unit": "built image contents and runtime behaviour", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "dev/dev_server.py:4-5,9-13; dev/README.md:2",
     "scenario": "ADMIN_USER/ADMIN_PASSWORD are never checked; any local process, other local user, or a DNS-rebinding web page reaches the console without credentials. The README claims a password is used. Harmless today because the handler only returns a static string.",
     "fix": "Enforce the credential and a Host-header allowlist in the handler, or remove the constants and correct the README.",
     "reproduction": "Not run: python dev/dev_server.py; curl -i http://127.0.0.1:8080/ without auth; expect 401, code yields 200 'console (debug on)'.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F2", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "dev/dev_server.py:6,13",
     "scenario": "DEBUG = True is hard-coded and announced in the response; matters only if the console is exposed.",
     "fix": "Default DEBUG from an environment variable, off by default.",
     "reproduction": "Not run: curl http://127.0.0.1:8080/ returns 'console (debug on)'.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "dev/dev_server.py:5; dev/README.md:2",
     "scenario": "Hard-coded default password 'dev' is published in the README; it becomes a known credential if auth is enforced and the server is exposed.",
     "fix": "Read the password from an environment variable and refuse to start without one, or generate one per run.",
     "reproduction": "Not run: grep -n ADMIN_PASSWORD dev/dev_server.py shows the literal \"dev\".",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "dev/dev_server.py:11-12,17",
     "scenario": "Plain HTTP with no CSP, X-Frame-Options or X-Content-Type-Options; once state-changing pages exist, a malicious page could frame or forge requests to them.",
     "fix": "Send security headers from the handler; document TLS as out of scope for a loopback-only tool.",
     "reproduction": "Not run: curl -i http://127.0.0.1:8080/ shows no security headers.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "deployment notes (not supplied); dev/dev_server.py:16-17",
     "suspicion": "A deployment, compose file or dev container may run the console or call serve() on a non-loopback host.",
     "unresolved_fact": "Contents of the deployment notes and any compose or devcontainer config."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "dev/dev_server.py:1",
     "suspicion": "The supplied file may not be the real console; the docstring describes user and flag editing that is absent.",
     "unresolved_fact": "Whether a fuller dev_server.py with state-changing handlers exists."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "Dockerfile:2; .dockerignore:1",
     "suspicion": "dev/ could reach the image through app/ imports or a different build context or ignore file.",
     "unresolved_fact": "Contents of app/, the build context used, and the absence of Dockerfile.dockerignore; confirm with docker run --rm <image> ls -R /srv/app."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Default password and debug mode ship to production.",
     "evidence": "Dockerfile:2 copies only app/; .dockerignore:1 excludes dev/."},
    {"id": "C2", "candidate": "The console is network-reachable.",
     "evidence": "dev/dev_server.py:21 binds 127.0.0.1; no other supplied caller of serve()."}
  ]
}
```