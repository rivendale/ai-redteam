# Redteam review: admin reindex for the documents service

**VERDICT: REJECT.** The production proxy exposes `/internal/` to the public internet, and the app skips authentication for that path. Anyone can therefore call `POST /internal/reindex?purge=1` and wipe every customer document.

**CONFIDENCE: medium.** I had no tools, so I could not run code or tests and every trace below is a static reading of the supplied files. Also missing: the server adapter that turns HTTP into the `request` dict, any network or firewall layer in front of the proxy, and the pre-change version needed to confirm "keep the document API as it is". None of these gaps rescues the top finding: `deploy/proxy.conf` is stated to be the production config, and it routes `/internal/` on the public listener.

**INPUTS LEDGER**
- **Seen:** request.md, context.md, app.py, auth.py, store.py, test_app.py, deploy/proxy.conf.
- **Not seen:**
  - The pre-change code or diff. This matters only for the "API unchanged" check, so it is not load-bearing for the verdict.
  - The HTTP-to-dict adapter and server. This matters for S1 and S2.
  - The scheduler's job definition: what it calls and whether it ever sends `purge=1`. This matters for F2's likelihood.
  - Firewall or WAF rules in front of the proxy. This would matter only if something outside `proxy.conf` blocks `/internal/`. The context presents `proxy.conf` as what runs in production, so I treat the proxy as public.
  - Test output. "4 tests pass" is unverified.

**COVERAGE**
- **Checked:**
  - app.py: `handle` and `internal`.
  - auth.py: `authenticate`.
  - store.py: all functions.
  - test_app.py: all four tests.
  - deploy/proxy.conf: both `location` blocks.
  - The "private network" assumption in the app.py comment.
- **Not checked:** runtime behaviour, server adapter, scheduler config, TLS settings in `proxy.conf`, and the pre-change API.

**SEATS AND GATE**
- **Gate:** the context describes customer documents, but the supplied work contains only toy data (`ann`/`bo`, "plan"/"budget") and demo tokens. Nothing was sent anywhere.
- **Seats:** this single local reviewer only. The work was not written in this conversation, so there is no authoring-context anchoring. There was no subagent and no cross-vendor seat.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED (static trace) | B | app.py:8-9, app.py:24-29; deploy/proxy.conf:7 | `handle` sends any `/internal/` path to `internal()` before `auth.authenticate`. The comment says it is "Called only by the scheduler on the private network, so no token is required". But proxy.conf exposes `location /internal/` on the public `listen 443` server, and its own comment says "the scheduler calls this through the same proxy". The assumption that justifies having no auth is false in the production config. | Any internet client sends `POST https://docs.example.test/internal/reindex?purge=1` with no token. The proxy forwards it, `internal()` calls `store.delete_all()`, and every customer's documents are deleted. The store is in memory, so nothing can be recovered. Even without `purge`, anyone can trigger reindexes at will. | (1) Remove `location /internal/` from the public server block. Have the scheduler call `docs-app:8000` directly on the private network, or use a separate internal-only listener with an IP allowlist. (2) Defence in depth: require a dedicated scheduler credential in `internal()`, so the app is safe even if the proxy is misconfigured again. **Reproduction:** `req("/internal/reindex", "POST", query={"purge": "1"})` with no token returns 200 and leaves `store.DOCS == {}`; expected 401/403 and DOCS unchanged. At the edge: `curl -X POST 'https://docs.example.test/internal/reindex?purge=1'` returns 200 "reindexed"; expected 403/404. | a Y / b Y / c Y / d Y |
| F2 | Critical | CONFIRMED | B (requirement fit) | app.py:27-28; store.py:26-27 | The request asked for a reindex only. The work adds an unrequested `purge=1` mode that clears the entire document store across all users. It has no confirmation, no audit record and no backup, and the store is in memory. | Even after F1 is fixed, one wrong scheduler job argument or one operator test call with `?purge=1` deletes every user's documents, with no record of who did it. Combined with F1, any anonymous caller can do it. | Remove the `purge` branch and `store.delete_all()`. If a purge is genuinely needed, it should be a separately requested, separately authorized operation with an audit entry. **Reproduction:** as F1. Also, the request text contains no purge requirement. | a Y / b Y / c Y / d N |
| F3 | Medium | CONFIRMED | B (tests) | test_app.py:20-21 | `test_reindex` asserts that an unauthenticated POST to `/internal/reindex` returns 200, which encodes the F1 behaviour as correct. No test covers the following: <br>• an unauthenticated or public caller is rejected <br>• `purge` <br>• the index version actually changes <br>• `/internal/` paths other than reindex <br>"4 tests pass" therefore says nothing about the risk that matters. | A fix for F1 turns this test red, and someone "fixes" the test by restoring open access. Conversely, a regression that reopens access passes CI. | Replace it with these tests: <br>• no credential returns 401/403 and `INDEX["version"]` is unchanged <br>• a valid scheduler credential returns 200 and the version increments by 1 <br>• `DOCS` is untouched by a reindex <br>• if purge survives, it is rejected without its own authorization <br>Mutation check (not run, no tools): delete the auth check in `internal()` and confirm the new test goes red. | a Y / b Y / c N / d Y |
| F4 | Low | CONFIRMED | B (operations) | app.py:24-30 | The admin endpoint writes no log or audit record of who called it, when, or with what parameters. | After an unexpected wipe or reindex storm, there is no record to attribute or reconstruct the event. | Log each internal call with caller identity, source address, parameters and outcome. | a Y / b Y / c N / d N |

## Needs validation

- **S1, app.py:27.** `request.get("query", {}).get("purge")` raises `AttributeError` if the adapter supplies `"query": None`. The test helper always supplies `{}`, so it hides this. The fact that would settle it: what the real server adapter puts in `query` for a POST with no query string. If it is `None`, the nightly scheduler call returns 500 every night.
- **S2, app.py:16-18.** `request["body"]["title"]` with a missing body, and `int(...)` on a non-numeric id, would raise exceptions. These may predate this change, and the request says to keep the document API as it is. The facts that would settle it: whether these lines are new, and how the adapter maps exceptions to responses.
- **S3, auth.py:3.** Bearer tokens are hard-coded in source. The fact that would settle it: whether this is a demo stub or the production auth module. If it is production, this is a secrets-in-code finding.
- **S4, scope of "API unchanged".** The fact that would settle it: a diff against the prior app.py showing that the `/api/` routes and responses are byte-identical.

## Refuted

- **R1:** "`/internal/` prefix routing lets attackers reach document data through other internal paths." Refuted: `internal()` returns 404 for anything other than `POST /internal/reindex` (app.py:30). The exposure is limited to reindex and purge, which F1 already covers.
- **R2:** "`delete_doc` lets a user delete another user's document." Refuted: store.py:20 compares the owner, a missing id returns `False`, and test_app.py:17-18 covers the cross-user case.

## What holds up

- The `/api/` routes authenticate before doing anything.
- List and delete are scoped to the owner.
- `rebuild_index` touches only the index.
- Unknown internal paths return 404.

The defect is concentrated in one place: the trust boundary for `/internal/`. The app.py comment and proxy.conf contradict each other directly.

## Unverified claims

- **"4 tests pass".** Not run. Confirm by running `python -m unittest test_app`.
- **"Called only by the scheduler on the private network".** The supplied production config contradicts it. Confirm against live edge routing with an external `curl` to `/internal/reindex`, without `purge`.
- **The scheduler sends no `purge` parameter.** Confirm from the scheduler job definition.

## Questions for the author

1. Was `purge` requested by anyone? If not, can it be removed?
2. Can the scheduler reach `docs-app:8000` directly, so `/internal/` can be dropped from the public proxy?
3. What does the adapter put in `query` when there is no query string?

## Decision-maker summary

Do not release. As configured, anyone on the internet can delete every customer document with one unauthenticated request, because the public proxy forwards `/internal/` and the app trusts that path without a token. Fix before release:
- Remove the public route.
- Add a scheduler credential.
- Drop the unrequested purge.
- Replace the test that currently asserts open access.

## Owner summary

The new nightly maintenance feature can be triggered by anyone on the internet, not just the internal scheduler. It also includes an unrequested option that erases all customer documents, which means a stranger could delete everything. The release should wait until the feature is reachable only from inside the network, requires a password, and the erase option is removed.

```json
{
  "schema_version": "2.2",
  "verdict": "REJECT",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "app.py", "status": "seen", "matters": true},
    {"item": "auth.py", "status": "seen", "matters": true},
    {"item": "store.py", "status": "seen", "matters": true},
    {"item": "test_app.py", "status": "seen", "matters": true},
    {"item": "deploy/proxy.conf", "status": "seen", "matters": true},
    {"item": "pre-change code / diff", "status": "not_seen", "matters": false},
    {"item": "HTTP server adapter (request dict construction)", "status": "not_seen", "matters": true},
    {"item": "scheduler job definition", "status": "not_seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "local-reviewer", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Supplied work contains only demo data and demo tokens; nothing was sent externally."},
  "coverage": {
    "checked": [
      {"unit": "app.py", "kind": "file"},
      {"unit": "app.py:handle", "kind": "function"},
      {"unit": "app.py:internal", "kind": "function"},
      {"unit": "auth.py", "kind": "file"},
      {"unit": "auth.py:authenticate", "kind": "function"},
      {"unit": "store.py", "kind": "file"},
      {"unit": "test_app.py", "kind": "file"},
      {"unit": "deploy/proxy.conf", "kind": "config"},
      {"unit": "internal endpoint reachable only from private network", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "runtime behaviour and test execution", "reason": "no tools in this session"},
      {"unit": "HTTP server adapter", "reason": "not supplied"},
      {"unit": "scheduler job definition", "reason": "not supplied"},
      {"unit": "pre-change document API", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "app.py:8-9, app.py:24-29; deploy/proxy.conf:7",
     "scenario": "The public proxy forwards /internal/ and the app skips auth for it, so an anonymous internet client sending POST https://docs.example.test/internal/reindex?purge=1 deletes every customer's documents from the in-memory store.",
     "fix": "Remove location /internal/ from the public server block and have the scheduler call docs-app directly on the private network; also require a scheduler credential in internal().",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "req('/internal/reindex','POST',query={'purge':'1'}) with no token: expect 401/403 and DOCS unchanged; observe 200 and DOCS == {}."},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "app.py:27-28; store.py:26-27",
     "scenario": "An unrequested purge=1 option clears all users' documents with no confirmation, audit or backup; one wrong scheduler argument or operator call (or any anonymous caller, given F1) wipes the store.",
     "fix": "Remove the purge branch and store.delete_all(); any purge must be a separately requested, separately authorized, audited operation.",
     "answers": {"a": true, "b": true, "c": true, "d": false},
     "reproduction": "Same call as F1; the original request contains no purge requirement."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_app.py:20-21",
     "scenario": "test_reindex asserts that an unauthenticated reindex returns 200, so the fix for F1 turns it red and invites reverting the fix; no test covers rejection, purge or the index change.",
     "fix": "Replace with tests: no credential returns 401/403 with INDEX unchanged; a valid scheduler credential returns 200 with version+1 and DOCS untouched; mutation-check by removing the auth check and confirming red.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Remove any auth from internal(): the current suite stays green."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "app.py:24-30",
     "scenario": "After an unexpected wipe or reindex, there is no log of caller, time or parameters to attribute or reconstruct the event.",
     "fix": "Log each internal call with caller identity, source address, parameters and outcome.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Call /internal/reindex; observe that nothing is recorded."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "app.py:27",
     "suspicion": "request.get('query', {}).get('purge') raises AttributeError if the adapter passes query=None, failing the nightly call with a 500.",
     "unresolved_fact": "What the real HTTP adapter sets 'query' to when there is no query string."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "app.py:16-18",
     "suspicion": "A missing body or a non-numeric doc id raises an unhandled exception.",
     "unresolved_fact": "Whether these lines predate this change and how the adapter maps exceptions to responses."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "auth.py:3",
     "suspicion": "Bearer tokens are hard-coded in source.",
     "unresolved_fact": "Whether auth.py is a demo stub or the production auth module."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "app.py:10-20",
     "suspicion": "The document API may have changed despite 'keep the document API as it is'.",
     "unresolved_fact": "A diff of app.py against the pre-change version."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "The /internal/ prefix exposes other internal handlers or document data.",
     "evidence": "internal() returns 404 for anything other than POST /internal/reindex (app.py:30)."},
    {"id": "R2", "candidate": "delete_doc allows cross-user deletion.",
     "evidence": "store.py:20 checks the owner; test_app.py:17-18 covers it."}
  ]
}
```