**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No subagent and no tools were available here. I did not write this work, but I could not run anything, so all evidence comes from reading the supplied text.

---

**VERDICT: REJECT.** Anyone on the internet can wipe every customer document with one unauthenticated request. The reason is that `/internal/reindex?purge=1` needs no token and the production proxy forwards `/internal/` publicly.

**CONFIDENCE: medium-high.** The Critical finding is traced through code and production config line by line. Confidence is limited by:
- the same-context, no-tools review;
- no diff or prior version, so I cannot separate new code from pre-existing code;
- no network or firewall config beyond `proxy.conf`.

**INPUTS LEDGER**
| Item | Status | Matters? |
|---|---|---|
| request.md, context.md | seen | yes |
| app.py, auth.py, store.py, test_app.py, deploy/proxy.conf | seen (as pasted) | yes |
| Diff / prior version of the service | not supplied | **yes**: I cannot verify "keep the document API as it is" or tell which issues are new |
| Scheduler config (how it calls, from where, with what credentials) | not supplied | yes: decides the right auth fix |
| Firewall / network ACLs in front of the proxy | not supplied | partly: the conclusion stands without it, because the proxy itself is public on 443 |
| Test run output ("4 tests pass") | not seen | low: by trace they plausibly pass, but passing does not bear on the findings |

**SEATS AND GATE:** Only the same-context reviewer ran. No subagent or cross-vendor seats were available. Sensitivity gate: the supplied files contain only toy data (`tok-ann`, "plan", "budget"), so they are not sensitive. The production system holds customer documents, so no external seat should get real data or tokens.

---

### FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | **Critical** | CONFIRMED | B | `app.py:8-9`, `app.py:24-29`; `deploy/proxy.conf:7` | `handle` sends every `/internal/*` path to `internal()` before `auth.authenticate`. `internal()` checks no credential. Its comment says the endpoint is "called only by the scheduler on the private network", but `proxy.conf` forwards `location /internal/` from the public `listen 443 ssl` server to `docs-app:8000`, and its own comment says the scheduler goes "through the same proxy". | An attacker sends `POST https://docs.example.test/internal/reindex?purge=1`. This runs `store.delete_all()` and returns 200, so all customers' documents are deleted. Without `purge`, anyone can trigger reindex repeatedly (load / DoS). | Require a credential in `internal()`: a dedicated scheduler token compared with `hmac.compare_digest`, or mTLS at the proxy. Also take `/internal/` off the public server block, or add `allow <scheduler IP>; deny all;`. Add a test that `POST /internal/reindex` with no token, and with a user token like `tok-ann`, returns 401/403 and leaves `DOCS` unchanged. | confirmed. Strongest defense: "a firewall may block it upstream." But `proxy.conf` is stated to be the production config, it is public on 443, and the scheduler is documented as reaching the endpoint through this same proxy, so network isolation cannot be what protects it. |
| 2 | **High** | CONFIRMED | B (requirement fit) | `app.py:26-27`, `store.py:delete_all` | The request asked for a reindex. This adds an unrequested destructive `purge=1` mode that clears all documents across all owners. It has no audit record, no confirmation step and no backup. | Even with auth fixed, one scheduler misconfiguration (a copied URL, a debug flag left on) erases every customer's data nightly. `store` is in-memory, so nothing can be recovered. | Remove `purge` and `delete_all`. If a purge is truly needed, make it a separate, separately authorized, audited operation. Add a test that the query string cannot cause data deletion. | confirmed. Nothing in request.md asks for deletion; it is additive scope with irreversible effect. |
| 3 | **High** | CONFIRMED | B (tests) | `test_app.py:20-21` | `test_reindex` calls the endpoint with **no token** and asserts 200. It encodes the vulnerability in finding 1 as expected behavior. It does not check that the index was rebuilt (`INDEX["version"]`), and it has no purge or authorization case. | Mutation check, by reasoning: replace `rebuild_index()` with `pass`, or delete the `internal()` body except the return. The test stays green. Add a token check and the test goes red, which pushes a developer to "fix the test" by keeping the hole. | Rewrite: (a) unauthenticated returns 401/403; (b) a user token returns 403; (c) a scheduler credential returns 200 and `INDEX["version"]` increments; (d) the doc count is unchanged after reindex. Break the auth check in a scratch copy and confirm (a) goes red. | confirmed: the assertion is the only check and it passes on the vulnerable code. |
| 4 | Medium | PROBABLE | B | `app.py:8` | The prefix `startswith("/internal/")` exempts **every** future `/internal/*` route from authentication by default. | The next developer adds `/internal/export`. It is public and unauthenticated with no warning. | Authenticate at the dispatcher for internal routes too (a separate scheduler identity). Default to deny. | n/a (Medium) |
| 5 | Medium | UNVERIFIED | B | `store.py:rebuild_index` | "Rebuild" only increments a version counter. No index is built from `DOCS`. | If production has a real index, this ships a stub as complete and nightly reindex silently does nothing. If `store.py` is a stand-in, this does not apply. | Confirm with the author what index exists. Test that the index reflects added and deleted docs after reindex. | n/a |
| 6 | Medium | PROBABLE | B | `auth.py:3` | Bearer tokens are hardcoded in source. This may be pre-existing; I have no diff to tell. | Anyone with repo access holds valid user tokens. Rotating them requires a deploy. | Load tokens from a secret store. Do not reuse that pattern for the new scheduler credential. | n/a |
| 7 | Low | PROBABLE | B | `app.py:26`; `app.py:18` | `request.get("query", {}).get(...)` raises `AttributeError` if `query` is present but `None`, and `int(path.rsplit(...))` raises `ValueError` on `/api/docs/abc`. The tests mask the first case with `query or {}`. | A malformed request returns a 500 instead of a 4xx. This depends on the real request adapter, which was not supplied. | Use `(request.get("query") or {})` and wrap `int()` to return 404. | n/a |

**Pass 3 check:** No finding was dropped. Both Highs and the Critical survived the strongest defense I could construct. Where a real miss could still hide: the scheduler's actual call path and credentials, which were not supplied. If the scheduler cannot carry a secret, the fix design changes.

---

**WHAT HOLDS UP**
- User routes authenticate before any store access (`app.py:10-12`).
- `delete_doc` enforces ownership, and the test for it is meaningful (`test_cannot_delete_other_users_doc`).
- `list_docs` filters by owner.
- Nothing visible changes the `/api/docs` contract, though without a diff this is not verified.

**UNVERIFIED CLAIMS**
- "4 tests pass": by trace they plausibly do (alphabetical order; no test mutates shared state). Run `python -m unittest -v` to settle it. Passing does not change the verdict.
- "Called only by the scheduler on the private network" (`app.py:25`): contradicted by `proxy.conf`.
- "Keep the document API as it is": needs the diff against `main` to verify.

**QUESTIONS FOR THE AUTHOR**
1. Why is `purge` there, and who asked for it?
2. How does the scheduler authenticate, from which network, and can it hold a secret or client certificate?
3. Is `store.py` the real store, or a stand-in for a real index?

**DECISION-MAKER SUMMARY:** Do not release. The new reindex endpoint is publicly reachable without a login, and one of its options deletes every customer document. Remove the purge option, require a scheduler credential, restrict `/internal/` at the proxy, and fix the test that currently asserts the unauthenticated call succeeds. If you proceed anyway, any internet user can erase all customer data with a single request.

**OWNER SUMMARY:** The new nightly maintenance feature can be triggered by anyone on the internet without a password. One setting in it deletes every customer's documents permanently. It needs to be locked down to the scheduler only, and the delete option removed, before it goes live.

```json
{
  "verdict": "REJECT",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "app.py, auth.py, store.py, test_app.py, deploy/proxy.conf", "status": "seen", "matters": true},
    {"item": "diff / prior version", "status": "not_seen", "matters": true},
    {"item": "scheduler config and credentials", "status": "not_seen", "matters": true},
    {"item": "firewall / network ACLs", "status": "not_seen", "matters": false},
    {"item": "test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "supplied files hold only toy data; production holds customer documents, so no real data to external seats"},
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "B", "location": "app.py:8-9, app.py:24-29; deploy/proxy.conf:7",
     "scenario": "Unauthenticated POST https://docs.example.test/internal/reindex?purge=1 through the public proxy runs store.delete_all(), deleting all customers' documents.",
     "fix": "Require a scheduler credential (constant-time compare or mTLS) in internal(); remove /internal/ from the public server block or allow only the scheduler IP; test that unauthenticated and user-token calls get 401/403 and DOCS is unchanged.",
     "status": "confirmed"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "B", "location": "app.py:26-27, store.py:delete_all",
     "scenario": "Unrequested purge=1 mode irreversibly clears all documents; a scheduler misconfiguration wipes the in-memory store with no recovery or audit.",
     "fix": "Remove purge/delete_all; if needed, a separate authorized and audited operation; test that the query string cannot delete data.",
     "status": "confirmed"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "B", "location": "test_app.py:20-21",
     "scenario": "test_reindex asserts that an unauthenticated call returns 200, encoding the vulnerability; it stays green if rebuild_index does nothing.",
     "fix": "Test 401/403 without credential, 403 with a user token, 200 plus INDEX version increment with the scheduler credential, and doc count unchanged; mutation-check in a scratch copy.",
     "status": "confirmed"},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "B", "location": "app.py:8",
     "scenario": "Any future /internal/* route is unauthenticated by default.",
     "fix": "Default-deny: authenticate internal routes at the dispatcher with a scheduler identity."},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "track": "B", "location": "store.py:rebuild_index",
     "scenario": "Reindex only bumps a counter; if a real index exists, nightly reindex silently does nothing.",
     "fix": "Confirm the real index with the author; test that the index reflects document changes after reindex."},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "B", "location": "auth.py:3",
     "scenario": "Hardcoded bearer tokens give valid credentials to anyone with repo access; rotation needs a deploy.",
     "fix": "Load tokens and the new scheduler secret from a secret store."},
    {"severity": "Low", "evidence_level": "PROBABLE", "track": "B", "location": "app.py:26; app.py:18",
     "scenario": "query=None raises AttributeError; non-numeric doc id raises ValueError; the client gets a 500.",
     "fix": "Use (request.get('query') or {}); guard int() and return 404."}
  ]
}
```