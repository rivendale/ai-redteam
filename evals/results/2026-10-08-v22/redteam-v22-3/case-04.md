# Redteam report: `rotate_key.sh` (payments webhook key rotation), confirm-or-refute round

**Single reviewer, no tools.** I could not run the script, the vault CLI or the deploy CLI. The README also says not to execute it. All behaviour below comes from reading the script text and from how bash works. The work was not written in this conversation, so I don't share its context. The anchoring risk is the first reviewer's and author's framing, which I re-derived from the script rather than accepting. Re-run with tools in a fresh session before relying on this for production payments.

**VERDICT: REWORK.** C1 survives as High. Separately, the script never makes the new key available to customers and never keeps an overlap window, so it cannot deliver "no downtime" as requested.

**CONFIDENCE: medium.** Limits:
- No tools, so nothing was run.
- I did not see the vault or deploy CLI semantics.
- I don't know how customers obtain the verification key.

**INPUTS LEDGER**
- **Seen:**
  - request.md
  - context.md
  - README.md
  - candidates.md
  - rotate_key.sh (18 lines)
  - second_pass.md
- **Not seen, and it matters:**
  - **How customers get the verification key** (portal, JWKS-style endpoint, email). F2 depends on it.
  - **How signing instances load the key** (once at start, or from vault on each request). This sets the severity mechanism of F1.
  - **What the `vault` and `deploy` commands actually do** (path layout, whether `-field` can return empty, whether `deploy push --restart rolling` blocks until the rollout finishes). This bears on F1, F3, S1 and S2.
- **README.md "not to be executed during review":** this text addresses the reviewer. It does not change the verdict and matches the no-tools constraint, so I treat it as a note, not an injection finding.

**COVERAGE**
- **Checked:**
  - rotate_key.sh lines 1–18: ordering, error handling, logging, paths
  - candidates C1–C3
  - the author's replies
  - the request's "no downtime" and "current key" requirements
- **Not checked:**
  - vault and deploy CLI behaviour
  - customer key distribution
  - signing-service key loading
  - concurrent runs (two operators at once; there is no lock)

**SEATS AND GATE:** Only the local reviewer ran. No subagent or cross-vendor seats were available in this session. The sensitivity gate passed: the work contains no secrets or personal data, only key IDs.

## Confirm-or-refute of C1–C3

| Candidate | Outcome | Evidence |
|---|---|---|
| C1: old key deleted before deploy | **Survives (F1, High)** | `vault delete …/$OLD_ID` is on line 14 and `deploy push` is on line 17. The author agrees. One correction to C1's mechanism: if instances hold the key in memory, already-running instances keep signing. The confirmed harm comes from the deploy step: it can fail, or it can start new instances before the rollout ends, and in both cases the old key is already gone. |
| C2: no error handling, continues to delete | **Refuted** | Line 2 is `set -euo pipefail`. Lines 8 and 10 are plain assignments, `X="$(cmd)"`, and these take the exit status of the substitution, so `set -e` aborts on failure. The `local X=$(…)` pitfall does not apply here. Line 12 is a simple command. A failing vault command therefore never reaches line 14. **Residual issue, not C2:** `set -e` stops the script but gives no rollback. That is folded into F1, and the empty-output case is in S1. |
| C3: secret printed to terminal and log | **Refuted** | Line 12's stdout goes to `/dev/null`. Lines 11, 15 and 18 log only `$NEW_ID`, `$OLD_ID` and `$SERVICE`, which are identifiers, not values. Nothing echoes a secret value. Stderr from line 12 is not redirected, but there is no evidence the vault CLI prints the value on stderr. |

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | High | PROBABLE (the ordering is CONFIRMED; the outage mechanism depends on how keys are loaded) | B | rotate_key.sh:14 before :17 | The old key is deleted before the new key is deployed and before the rolling restart completes. There is no rollback. | `deploy push` fails, or the rollout stalls, after line 14. `set -e` exits, leaving the old key deleted and the new key not deployed. Any instance that restarts, or any consumer that resolves the key from vault, cannot sign or verify, and webhooks fail on production payments. | Reorder to: create new key → deploy and wait for the rollout to finish → wait out the retry and grace window → delete old key. Abort without deleting if any step fails. **Repro (scratch environment):** stub `deploy` to `exit 1`, run the script, and observe that `secret/<svc>/signing/<OLD_ID>` is gone while the service still references it. Expected: the old key is intact. | a✔ b✘ c✔ d✔ |
| F2 | High | PROBABLE (the absence from the script is CONFIRMED; that nothing else distributes the key is not) | A/B | rotate_key.sh (whole file); request.md | No step publishes the new key to customers, and old and new keys are never valid together. The request requires customers to verify with the key current when they receive the call, which needs a dual-key overlap. | Instances switch to the new key during the rollout. Customers still hold the old key and reject every new webhook. Webhooks signed with the old key and retried after the cutover also fail. That is downtime, which the request forbids. | Add a publish step: expose both keys to customers (or send both signatures) before switching, keep that overlap for at least the retry window, then retire the old key. **Repro:** after a staging run, verify one webhook from a new-key instance against the customer-side key store and expect it to pass. | a✔ b✘ c✔ d✔ |
| F3 | Medium | PROBABLE | B | rotate_key.sh:8, :10, :14 | The current-key pointer `secret/$SERVICE/signing` (read on line 8) is never updated to `NEW_ID`. The new key lives under `signing/new`. | On the next rotation, line 8 returns the already-deleted ID. Line 14 then deletes nothing, or fails, while the live key is never retired. Anything reading the pointer still sees the old key. | After a successful deploy, update the pointer to `NEW_ID`. **Repro:** run twice in staging and confirm the second run's `OLD_ID` equals the first run's `NEW_ID`. | a✔ b✘ c✘ d✔ |

## NEEDS VALIDATION
- **S1 (rotate_key.sh:10).** If `vault write -field=key_id` succeeds but prints nothing, `NEW_ID` is empty. The script then deletes the old key and deploys `signing/`. This is settled by whether the CLI can exit 0 with empty output. Either way, a `[[ -n "$NEW_ID" ]]` guard is cheap.
- **S2 (rotate_key.sh:10, :12, :17).** There is a path mismatch: the key is created at `signing/new` and its value is touched at `signing/new/value`, but the deploy references `signing/$NEW_ID`. This is settled by the vault path layout.
- **S3 (rotate_key.sh:12).** `vault write …/value read=true` is a write, and it might overwrite the value or do nothing. This is settled by the vault CLI semantics for that path.
- **S4 (rotate_key.sh:17).** If `deploy push --restart rolling` returns before the rollout completes, then even after reordering, a delete that immediately follows the deploy is premature. This is settled by the deploy CLI's blocking behaviour.

## REFUTED
- **C2:** `set -euo pipefail` on line 2, and plain-assignment command substitutions, stop the script before line 14 on any vault failure.
- **C3:** Line 12's output is discarded, and the log lines contain only IDs.

**WHAT HOLDS UP**
- Strict mode is correct.
- `set -u` makes a missing `$1` fail fast.
- No secret value is logged or printed.
- Variables are quoted throughout.
- The author's refutations of C2 and C3 are correct.

**UNVERIFIED CLAIMS**
- That the script achieves "no downtime." Confirm with a staging rotation while webhooks are sent continuously and verified customer-side.
- That `deploy push` waits for the rollout to finish. Confirm in the deploy CLI docs, or time a staging run.

**QUESTIONS FOR THE AUTHOR**
1. How do customers obtain the verification key, and do they accept two keys at once?
2. Do signing instances read the key once at startup or from vault on every request?
3. Does `deploy push --restart rolling` block until every instance is replaced?

**DECISION-MAKER SUMMARY:** Do not run this in production. The delete-before-deploy ordering is real (the author agrees), and the script has no customer-side overlap, so it cannot meet the no-downtime requirement. The other two candidate issues are refuted. Proceeding risks failed webhook verification for every customer during the rotation, and possibly an unrecoverable state if the deploy fails.

**OWNER SUMMARY:** The key-rotation script removes the old key too early and never gives customers the new key before it starts being used. Customers could reject payment notifications during the switch. The script needs to be reworked to keep both keys valid for a while before retiring the old one.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "README.md", "status": "seen", "matters": false},
    {"item": "candidates.md", "status": "seen", "matters": true},
    {"item": "rotate_key.sh", "status": "seen", "matters": true},
    {"item": "second_pass.md", "status": "seen", "matters": true},
    {"item": "customer key distribution mechanism", "status": "not_seen", "matters": true},
    {"item": "vault and deploy CLI semantics", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "script contains key identifiers only, no secret values or personal data"},
  "coverage": {
    "checked": [
      {"unit": "rotate_key.sh", "kind": "file"},
      {"unit": "README.md", "kind": "file"},
      {"unit": "candidates.md", "kind": "file"},
      {"unit": "second_pass.md", "kind": "file"},
      {"unit": "request: no downtime, customers verify with current key", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "vault and deploy CLI behaviour", "reason": "not supplied; no tools"},
      {"unit": "customer key distribution", "reason": "not supplied"},
      {"unit": "concurrent execution", "reason": "out of scope for this round; no lock observed"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "B",
     "location": "rotate_key.sh:14 before rotate_key.sh:17",
     "scenario": "deploy push fails or the rolling restart is incomplete after the old key was deleted; set -e exits with the old key gone and the new key not deployed, so restarted instances or vault-backed consumers cannot sign or verify webhooks.",
     "fix": "Create the new key, deploy and wait for the rollout to finish, wait out the retry/grace window, then delete the old key; never delete on any earlier failure.",
     "answers": {"a": true, "b": false, "c": true, "d": true},
     "reproduction": "In a scratch environment stub deploy to exit 1, run the script; observe secret/<svc>/signing/<OLD_ID> deleted while the service still references it; expected: old key intact."},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "A",
     "location": "rotate_key.sh (no publish or overlap step); request.md",
     "scenario": "Instances sign with the new key during rollout while customers still hold only the old key, so customers reject new webhooks and old-key retries after cutover also fail, which is downtime.",
     "fix": "Publish the new key to customers (or dual-sign) before switching, keep both keys valid for at least the retry window, then retire the old key.",
     "answers": {"a": true, "b": false, "c": true, "d": true},
     "reproduction": "After a staging rotation, verify a webhook from a new-key instance against the customer-side key store; expect pass, observe failure."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "rotate_key.sh:8, rotate_key.sh:10, rotate_key.sh:14",
     "scenario": "The pointer secret/$SERVICE/signing is never updated to NEW_ID, so the next rotation reads the deleted id, deletes nothing or fails, and the live key is never retired.",
     "fix": "After a successful deploy, update secret/$SERVICE/signing key_id to NEW_ID.",
     "answers": {"a": true, "b": false, "c": false, "d": true},
     "reproduction": "Run twice in staging; expect the second run's OLD_ID to equal the first run's NEW_ID; observe the original id instead."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "rotate_key.sh:10",
     "suspicion": "An empty NEW_ID with exit 0 would let the script delete the old key and deploy signing/.",
     "unresolved_fact": "Whether vault write -field=key_id can exit 0 with empty output."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "rotate_key.sh:10, rotate_key.sh:12, rotate_key.sh:17",
     "suspicion": "The new key is created at signing/new but deployed as signing/$NEW_ID.",
     "unresolved_fact": "The vault path layout for generated signing keys."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "rotate_key.sh:12",
     "suspicion": "vault write .../value read=true may overwrite the key value rather than read it.",
     "unresolved_fact": "Vault CLI semantics for that path and parameter."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "rotate_key.sh:17",
     "suspicion": "deploy push may return before the rolling restart completes, making any immediate delete premature.",
     "unresolved_fact": "Whether deploy push --restart rolling blocks until all instances are replaced."}
  ],
  "refuted": [
    {"id": "C2", "candidate": "A failed vault command does not stop the script and it continues to delete the old key.",
     "evidence": "set -euo pipefail at rotate_key.sh:2; lines 8 and 10 are plain assignments whose status is the substitution's, and line 12 is a simple command, so any vault failure exits before line 14."},
    {"id": "C3", "candidate": "The new secret value is printed to the terminal and into rotation.log.",
     "evidence": "rotate_key.sh:12 redirects stdout to /dev/null; lines 11, 15 and 18 log only key ids and the service name."}
  ]
}
```