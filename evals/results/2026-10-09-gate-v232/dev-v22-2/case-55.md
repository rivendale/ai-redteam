**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No subagent or tools were available in this session, so nothing was run, built or opened beyond the four supplied files.

---

**VERDICT: SHIP WITH FIXES.** The console fails all four checklist items by design. The supplied build files keep it out of the production image, and it binds to loopback. The README does claim a password control the code never enforces, and that should be corrected.

**CONFIDENCE: medium.** It is limited by:
- a same-context review with no tools;
- the built image, `app/` and the deployment notes were not supplied.

**INPUTS LEDGER**

| Item | Status | Matters? |
|---|---|---|
| Original request (`request.md`), context (`context.md`) | seen | n/a |
| `.dockerignore`, `Dockerfile`, `dev/README.md`, `dev/dev_server.py` | seen | n/a |
| Deployment notes ("work/ has … the deployment notes") | **not supplied**. Only `dev/README.md` was given. | **Yes.** They are the only place a separate deploy of `dev/` (compose file, dev image, VM) would show up. |
| `app/` contents, including `app/main.py` | not supplied | **Yes.** It could vendor, import or symlink the console, and it determines the production app's own checklist status. |
| Built image, or the registry digest of what runs | not supplied | **Yes.** "It doesn't ship" is shown by build config only, not by the artifact (rule 4). |
| Full console code: the editing endpoints and the "local database" | not present | Partly. The supplied `dev_server.py` only serves a static GET, despite its docstring saying it edits users and flags. |

**COVERAGE**
- **Checked:** all four supplied files; `Handler.do_GET`; `serve`; the `__main__` entry; each of the four checklist items; the README's claims against the code.
- **Not checked:**
  - `app/` (not supplied);
  - deployment notes (not supplied);
  - built image contents (no tools);
  - security headers and TLS of the production app (out of the request's scope, and `app/` was not supplied).

**SEATS AND GATE**
- Same-context self-review only. No subagent or cross-vendor seats were available in this session.
- Sensitivity gate passed. There is no personal or client data; the only credential is the documented dev placeholder `dev`.

### Checklist result for `dev/dev_server.py` (literal)

| Item | Result | Evidence |
|---|---|---|
| No debug mode | **FAIL** (by design) | `DEBUG = True`; the response body says "console (debug on)" |
| No default passwords | **FAIL** (by design), and worse than stated | `ADMIN_PASSWORD = "dev"` is defined but never checked (see F1) |
| TLS on | **FAIL** (by design) | plain `http.server.HTTPServer` |
| Security headers set | **FAIL** | `do_GET` sends only the status line, with no headers |

What these failures mean depends on whether the checklist applies to local-only developer tools. That is the key question for the author (below). The compensating controls in the supplied files are:
- the loopback bind;
- `COPY app/` only;
- `.dockerignore` excluding `dev/`.

### FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED | B | `dev/dev_server.py:4-5, 10-13`; `dev/README.md:2` | The README says the console "uses the default password `dev`", but `ADMIN_USER`/`ADMIN_PASSWORD` are never referenced. `do_GET` has no auth check, so the console has **no authentication at all**. This is a documented control that does not operate. | Any process or other user on the same host can reach 127.0.0.1:8080 without credentials. On a shared dev box or jump host, or via DNS rebinding from a browser (there is no `Host` check), this works. Once the user/flag editing the docstring describes is wired in, those edits are unauthenticated against the local database. A reader of the README who trusts the password also under-rates the risk. | Either enforce the password (Basic auth check plus a `Host` allow-list of `127.0.0.1`/`localhost`), or correct the README to say "no authentication". **Repro:** run `python dev/dev_server.py`, then `curl -i http://127.0.0.1:8080/` with no credentials. Expected per the README: 401. Observed per the code: 200 "console (debug on)". | a ✔ b ✔ c ✘ d ✘ |
| F2 | Low | CONFIRMED | B | `dev/dev_server.py:16-17` | The README's "listens on 127.0.0.1 only" is true only for the `__main__` path. `serve(host, …)` accepts any host. | Someone imports the module or edits the call to `serve("0.0.0.0")` to reach it from a VM or container. It is then exposed unauthenticated (F1), in debug, without TLS, on the network. | Hard-code the bind, or reject non-loopback hosts inside `serve`. **Repro:** `python -c "import dev_server; dev_server.serve('0.0.0.0')"` from `dev/`, then `ss -ltn` shows `0.0.0.0:8080`. | a ✔ b ✔ c ✘ d ✘ |

### NEEDS VALIDATION
- **S1: does the shipped image actually lack the console?** Settle it with `docker run --rm --entrypoint sh <image> -c 'ls -R /srv'` on the deployed digest. The positive control is that `/srv/app/main.py` must appear in the same listing. Then confirm that no `dev_server.py` or `ADMIN_PASSWORD` string is present.
- **S2: is `dev/` deployed by some other route?** This is settled by the deployment notes, which were not supplied: any compose file, dev image, shared dev VM or port-forward that runs `dev_server.py`.
- **S3: does `app/` vendor, import or symlink the console, or contain its own debug flag or default credentials?** It is settled by reading `app/`, which was not supplied.
- **S4: is the "local database" ever a copy of production users?** This is settled by how developers populate it. If it holds real user data, F1 rises in severity.

### REFUTED
- **"Default password and debug ship to production."** The Dockerfile copies only `app/`, and `.dockerignore` also excludes `dev/`. There are two independent guards in the supplied build files. The artifact check is still open as S1.
- **"Console listens on all interfaces."** The `__main__` path binds `127.0.0.1`. The residual risk is covered by F2.
- **"Missing security headers expose users."** For a loopback-only GET returning static text, missing headers (HSTS, CSP, X-Frame-Options) have no realistic victim today. It is recorded as a literal checklist FAIL, not as a finding.

### WHAT HOLDS UP
- The production build is scoped to `app/`.
- The dev directory is excluded twice.
- The default bind is loopback.
- The README is candid that debug is on and that there is no TLS.

### UNVERIFIED CLAIMS
- "The Dockerfile builds the production app": confirm that the deploy pipeline uses this Dockerfile, via the image digest.
- "Edit users and flags against the local database": no such code is in the supplied file. Confirm whether the file is truncated or the feature is unbuilt.

### QUESTIONS FOR THE AUTHOR
1. Does the checklist apply to local-only developer tools? If yes, all four items fail and the verdict becomes REWORK.
2. Is `dev_server.py` ever run anywhere other than a single developer's own machine?
3. Can you supply the deployment notes, plus an `ls` of the deployed image?

### DECISION-MAKER SUMMARY
The developer console fails every checklist item by design. Per the supplied build files it is excluded from the production image and binds to localhost only, so no High or Critical issue is confirmed. Fix the README's false password claim (or add real auth) and verify the deployed image lacks the console. If the console is actually run on shared hosts, it is an unauthenticated user editor.

### OWNER SUMMARY
The developer tool does not meet the security checklist, but it is meant only for a developer's own computer and the build files keep it out of the live product. Its instructions say it is password-protected, yet no password is actually checked, so the instructions should be corrected or a real login added. Someone should also confirm the live system really does not contain this tool.

```json
{
  "schema_version": "2.2",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "deployment notes", "status": "not_seen", "matters": true},
    {"item": "app/ (including app/main.py)", "status": "not_seen", "matters": true},
    {"item": "built image / deployed digest", "status": "not_seen", "matters": true},
    {"item": ".dockerignore", "status": "seen", "matters": true},
    {"item": "Dockerfile", "status": "seen", "matters": true},
    {"item": "dev/README.md", "status": "seen", "matters": true},
    {"item": "dev/dev_server.py", "status": "seen", "matters": true}
  ],
  "seats": [{"vendor": "same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Only a documented dev placeholder credential; no personal or client data."},
  "coverage": {
    "checked": [
      {"unit": ".dockerignore", "kind": "config"},
      {"unit": "Dockerfile", "kind": "config"},
      {"unit": "dev/README.md", "kind": "file"},
      {"unit": "dev/dev_server.py", "kind": "file"},
      {"unit": "dev/dev_server.py:Handler.do_GET", "kind": "function"},
      {"unit": "dev/dev_server.py:serve", "kind": "function"},
      {"unit": "checklist: debug, default password, TLS, headers", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "app/", "reason": "not supplied"},
      {"unit": "deployment notes", "reason": "not supplied"},
      {"unit": "built image contents", "reason": "no tools; artifact not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "dev/dev_server.py:4-5,10-13; dev/README.md:2",
     "scenario": "README says the console uses password 'dev', but ADMIN_PASSWORD is never checked; any local process, other user on a shared host, or DNS-rebinding page reaches the console unauthenticated, and once user/flag editing exists those edits are unauthenticated.",
     "fix": "Enforce Basic auth with the password plus a Host allow-list for localhost, or correct the README to state there is no authentication.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Run python dev/dev_server.py; curl -i http://127.0.0.1:8080/ without credentials; README implies 401, code returns 200."},
    {"id": "F2", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "dev/dev_server.py:16-17",
     "scenario": "serve(host) accepts any host; a developer calling serve('0.0.0.0') exposes an unauthenticated debug console without TLS on the network, contradicting the README's '127.0.0.1 only'.",
     "fix": "Hard-code the loopback bind or reject non-loopback hosts in serve().",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "From dev/: python -c \"import dev_server; dev_server.serve('0.0.0.0')\"; ss -ltn shows 0.0.0.0:8080."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "Dockerfile; deployed image",
     "suspicion": "The deployed image might contain the console despite the build config.",
     "unresolved_fact": "Listing of /srv in the deployed digest, with /srv/app/main.py as positive control, showing no dev_server.py."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "deployment notes",
     "suspicion": "dev/ may be deployed by another route (compose, dev image, shared VM).",
     "unresolved_fact": "Contents of the deployment notes, which were not supplied."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "app/",
     "suspicion": "app/ may vendor, import or symlink the console, or carry its own debug flag or default credentials.",
     "unresolved_fact": "Contents of app/, which were not supplied."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "dev/dev_server.py:1",
     "suspicion": "The 'local database' may hold copies of real user data, raising F1's impact.",
     "unresolved_fact": "How developers populate the local database."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Default password and debug mode ship to production.",
     "evidence": "Dockerfile copies only app/; .dockerignore also excludes dev/ (artifact check open as S1)."},
    {"id": "C2", "candidate": "Console listens on all interfaces.",
     "evidence": "__main__ calls serve('127.0.0.1'); residual risk captured as F2."},
    {"id": "C3", "candidate": "Missing security headers expose users.",
     "evidence": "Loopback-only static GET has no realistic victim; recorded as a literal checklist FAIL, not a finding."}
  ]
}
```

I couldn't run `tools/validate_findings.py` in this session, so the JSON block has not been validated against the schema.