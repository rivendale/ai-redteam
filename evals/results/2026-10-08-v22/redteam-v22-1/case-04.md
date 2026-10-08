VERDICT: **REWORK**. The script deletes the old key before the new one is deployed, never makes the new key "current", and has no overlap window, so it cannot rotate the key with zero downtime.

CONFIDENCE: **medium**. The ordering defect is confirmed from the script text. Limits:
- This is a same-context review: anchoring risk, so re-run in a fresh session before relying on it for production payments.
- No tools were available, so nothing was executed.
- The inputs that decide how customers learn the "current" key were not supplied.

INPUTS LEDGER:
- **Seen:**
  - `request.md` (verbatim)
  - `context.md`
  - `rotate_key.sh` (18 lines)
  - `candidates.md` (C1 to C3)
  - `second_pass.md` (the author's replies)
  - `README.md`
- **Not seen:**
  - How customers obtain the key they verify with (an endpoint, dashboard or published key). **Matters**: F2 and F3 depend on it.
  - The secrets engine mounted at `secret/`. **Matters** for S1.
  - Documentation for the `deploy` CLI, in particular whether `push --restart rolling` blocks until rollout completes. **Matters** for S2.
  - The service's signing code, in particular whether it caches the key or reads it per request. **Matters** for S3.
  - The author's fix for C1. **Matters**: a plain swap of the two commands does not fix the problem (see F3).
  - Tests: none exist.
- **Instruction inside the work:** `README.md` says "The script is not to be executed during review." This is an operational safety note, not an attempt to steer the verdict. It changes nothing here because no tools were available, so it is not raised as a finding.

COVERAGE:
- **Checked:**
  - `rotate_key.sh`, lines 1 to 18
  - each candidate C1, C2 and C3 against the script
  - each author reply in `second_pass.md`
  - the assumption that `set -e` covers command-substitution assignments
  - the assumption that "current" is updated
- **Not checked:**
  - the vault engine semantics
  - `deploy` CLI behaviour
  - the service signing code
  - the customer-side verification flow

SEATS AND GATE: same-context review only; no subagent or cross-vendor seats were available. Sensitivity gate: not sensitive. The work contains no secret values, only paths and variable names.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 (was C1, **survives, raised to Critical**) | Critical | CONFIRMED | B | `rotate_key.sh:14` (`vault delete …`) runs before `:17` (`deploy push …`) | The old key is destroyed while every instance still signs with it. There is no rollback. | (1) Between lines 14 and 17, and for the whole rolling restart, instances signing with the old key produce signatures that no longer match a live key, and any instance that reloads from vault finds the key gone. (2) If `deploy push` fails, `set -e` stops the script *after* the delete. The old key is gone, the new key is never deployed, and webhooks stay broken until someone intervenes by hand. | Delete only after rollout is confirmed complete and after the overlap window in F3. Add a `trap` that aborts before any delete on failure. **Repro:** put stub `vault` and `deploy` scripts first on `PATH`, each appending `$0 $*` to `calls.log`, then run `rotate_key.sh svc`. Expected: the `vault delete` line appears after `deploy push`. Observed: it appears before. Then make the stub `deploy` exit 1. Expected: no `vault delete` in the log. Observed: present. | a✓ b✓ c✓ d✓ |
| F2 | High | PROBABLE | B/A | `rotate_key.sh:8` reads `secret/$SERVICE/signing` field `key_id`. Nothing ever writes it. | The "current key" pointer is never moved to `NEW_ID`. The request defines correctness as customers verifying with "the key that is current". | After a run, `signing.key_id` still names the deleted old key while the service signs with `NEW_ID`. Customers or services that resolve "current" through it verify against a dead key, so every webhook fails. A second run reads the stale `OLD_ID` again and never retires the key that is actually deployed. | Promote `NEW_ID` explicitly, by writing `key_id=$NEW_ID` to `secret/$SERVICE/signing`, at the right step of the sequence in F3. **Repro:** with the same stub `vault`, assert that `calls.log` contains a write of `key_id=<NEW_ID>` to `secret/svc/signing`. Today there is none. | a✓ b✗ c✓ d✓ |
| F3 | High | PROBABLE | A/B | Whole design, lines 10 to 17 | Even with F1's two lines swapped, there is no overlap window. During a rolling restart, part of the fleet signs with the old key and part with the new one, and customers check against a single "current" key. | Mid-rollout, whichever key customers treat as current, webhooks signed with the other key fail verification. That is downtime, which the request forbids. Retries of webhooks signed before the switch also fail if the old key is deleted immediately. | Rotate in stages: (1) create the new key and publish it as an *accepted* key alongside the old one, or dual-sign; (2) deploy and wait for rollout completion, verified on the running instances; (3) switch "current"; (4) wait out the retry and delivery window; (5) delete the old key. **Repro:** run against staging with two instances and a verifier that holds only the current key. Send webhooks continuously during the rollout. Expected: zero verification failures. Predicted: failures from the instances not yet restarted. | a✓ b✗ c✓ d✓ |

## NEEDS VALIDATION
- **S1** (`rotate_key.sh:10,12`): `vault write … generate=true` and `vault write …/new/value read=true` only make sense on a custom engine. On a KV engine, line 10 stores a literal `generate=true` field and generates no key. Line 12 *writes* `{read: "true"}` to `…/new/value` rather than reading anything, and could overwrite the key material. Also, a fixed path `signing/new` is overwritten on every run. **Fact that settles it:** which secrets engine is mounted at `secret/`, and what its API does with these fields.
- **S2** (`:17`): whether `deploy push --restart rolling` returns only after every instance is serving the new key. If it returns early, deleting the key right after it is still premature. **Fact that settles it:** the `deploy` CLI documentation, or observed behaviour.
- **S3** (`:14`): whether running instances keep the key in memory or fetch it from vault per signature. This decides whether old instances break immediately at line 14 or only when they restart. F1 holds either way because of the failed-deploy path. **Fact that settles it:** the service's signing code.

## REFUTED
- **C2** ("no error handling; a failed vault command continues to the delete"): **refuted.**
  - Line 2 is `set -euo pipefail`.
  - Lines 8 and 10 are plain `VAR="$(cmd)"` assignments. The exit status of such an assignment is the substitution's status, so errexit fires. This would not hold under `local`, `export` or `readonly`, and none of those are used.
  - Line 12 is a simple command, so it is covered as well.
  - No failing vault command can reach line 14.
  - The narrower true point, that there is no rollback when the *deploy* fails, is part of F1.
- **C3** ("the secret value is printed to the terminal and into rotation.log"): **refuted.**
  - Line 12's stdout goes to `/dev/null`.
  - The log lines (11, 15, 18) interpolate only `$NEW_ID` and `$OLD_ID`, which are key ids.
  - No command echoes the value.
  - Line 12's stderr is not redirected, but vault does not write secret values to stderr. Line 12's real problem is S1, not exposure.

## WHAT HOLDS UP
- Strict mode (`set -euo pipefail`) correctly stops the script on any vault failure before the delete.
- A missing `$1` aborts on the unbound variable.
- Secret values never reach the log.
- The author's replies to C2 and C3 are correct. The author's concession on C1 is correct, but C1 understates the problem: it is Critical, and swapping the two lines alone does not fix it.

## UNVERIFIED CLAIMS
- "No downtime." Nothing in the script supports it. Confirm it with the staging test described under F3.
- That `vault write … generate=true` returns a usable key id. Confirm against the engine documentation, or with one call in staging.

## QUESTIONS FOR THE AUTHOR
1. How do customers get the key they verify with, and does that path read `secret/$SERVICE/signing`?
2. Can customers accept two keys at once (current and next), or can the service dual-sign?
3. What engine is at `secret/`, and what do `generate=true` and `read=true` do there?
4. Does `deploy push --restart rolling` block until the rollout completes?

## DECISION-MAKER SUMMARY
Do not run this script in production. It deletes the live signing key before the replacement is deployed, and if the deploy step fails the service is left with no working key. Rework it into a staged rotation (publish both keys, deploy, confirm, switch, wait, delete) and test it in staging under continuous webhook traffic first.

## OWNER SUMMARY
The script that changes the payments signing key removes the old key too early. While it runs, and especially if any step fails, customers would be unable to verify payment notifications from us. It needs to be redesigned so the old and new keys work side by side until the switch is complete, and tested before use.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "rotate_key.sh", "status": "seen", "matters": true},
    {"item": "candidates.md", "status": "seen", "matters": true},
    {"item": "second_pass.md", "status": "seen", "matters": true},
    {"item": "README.md", "status": "seen", "matters": false},
    {"item": "customer key-distribution mechanism", "status": "not_seen", "matters": true},
    {"item": "vault secrets engine at secret/", "status": "not_seen", "matters": true},
    {"item": "deploy CLI documentation", "status": "not_seen", "matters": true},
    {"item": "service signing code", "status": "not_seen", "matters": true},
    {"item": "author's fix for C1", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Work contains paths and variable names only, no secret values or personal data."},
  "coverage": {
    "checked": [
      {"unit": "rotate_key.sh", "kind": "file"},
      {"unit": "candidates.md", "kind": "file"},
      {"unit": "second_pass.md", "kind": "file"},
      {"unit": "README.md", "kind": "file"},
      {"unit": "set -e applies to VAR=$(cmd) assignments", "kind": "assumption"},
      {"unit": "current key pointer is updated", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "vault engine at secret/", "reason": "not supplied"},
      {"unit": "deploy CLI", "reason": "not supplied"},
      {"unit": "service signing code", "reason": "not supplied"},
      {"unit": "customer verification flow", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "rotate_key.sh:14 before rotate_key.sh:17",
     "scenario": "vault delete removes the old key while all instances still sign with it; if deploy push then fails, set -e exits after the delete, leaving no live key deployed and webhooks failing verification.",
     "fix": "Delete the old key only after rollout completion is verified and an overlap window has passed; add a trap that aborts before any delete on failure.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Put stub vault/deploy first on PATH, each logging calls to calls.log; run rotate_key.sh svc. Expected: vault delete appears after deploy push; observed: before. With stub deploy exiting 1, expected no vault delete; observed present."},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "B",
     "location": "rotate_key.sh:8 (secret/$SERVICE/signing key_id read, never written)",
     "scenario": "After rotation the current-key pointer still names the deleted old key while the service signs with NEW_ID; anything resolving 'current' through it verifies against a dead key, and the next run reads a stale OLD_ID.",
     "fix": "Write key_id=$NEW_ID to secret/$SERVICE/signing at the promotion step of a staged rotation.",
     "answers": {"a": true, "b": false, "c": true, "d": true},
     "reproduction": "With a stub vault logging calls, assert a write of key_id=<NEW_ID> to secret/svc/signing; none occurs today."},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "A",
     "location": "rotate_key.sh:10-17 (overall sequence)",
     "scenario": "During the rolling restart, part of the fleet signs with the old key and part with the new; customers verifying with a single current key reject one set, and retried old-key webhooks fail once the old key is deleted.",
     "fix": "Staged rotation: publish the new key as accepted alongside the old (or dual-sign), deploy and verify completion, switch current, wait the retry window, then delete the old key.",
     "answers": {"a": true, "b": false, "c": true, "d": true},
     "reproduction": "In staging with two instances and a verifier holding only the current key, send webhooks continuously through the rollout; expected zero verification failures, predicted failures from not-yet-restarted instances."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "rotate_key.sh:10,12",
     "suspicion": "generate=true and read=true may be stored as literal fields on a KV engine; line 12 may overwrite key material, and the fixed path signing/new is reused every run.",
     "unresolved_fact": "Which secrets engine is mounted at secret/ and how it handles these fields."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "rotate_key.sh:17",
     "suspicion": "deploy push --restart rolling may return before all instances run the new key.",
     "unresolved_fact": "Whether the deploy CLI blocks until rollout completion."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "rotate_key.sh:14",
     "suspicion": "Running instances may fail to sign immediately after the delete if they fetch the key per request.",
     "unresolved_fact": "Whether the service caches the signing key in memory or reads it from vault per signature."}
  ],
  "refuted": [
    {"id": "C2", "candidate": "A failed vault command does not stop the script and it continues to delete the old key.",
     "evidence": "set -euo pipefail at line 2; lines 8 and 10 are plain VAR=$(cmd) assignments whose status is the substitution's, so errexit fires; line 12 is a simple command. No failing vault call reaches line 14. The missing rollback on deploy failure is part of F1."},
    {"id": "C3", "candidate": "The new secret value is printed to the terminal and into rotation.log.",
     "evidence": "Line 12 stdout goes to /dev/null; log lines 11, 15 and 18 interpolate only key ids ($NEW_ID, $OLD_ID); no command echoes the value."}
  ]
}
```