# Redteam: confirm-or-refute round on `rotate_key.sh` (payments webhook key rotation)

**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No subagent and no tools were available. The candidates and the author's reply came in with the work, so this review may anchor on their framing. Every claim below comes from reading the text. Nothing was executed, which also matches the README.

---

**VERDICT: REWORK.** C1 holds and is Critical: the script deletes the live signing key before the replacement is deployed. Separately, the script never makes the new key "current" and never waits for the rollout, so it does not deliver the zero-downtime rotation that was asked for.

**CONFIDENCE: medium.** Three things limit it:
- This is a same-context review.
- There were no tools, so nothing was run.
- The semantics of the vault secrets engine and the `deploy` CLI were not supplied (custom `generate=true` and `read=true` parameters, and whether `deploy push` blocks).
- How customers learn the current key was not supplied.

**INPUTS LEDGER**

| Item | Status | Matters? |
|---|---|---|
| request.md, context.md | seen | yes |
| rotate_key.sh, candidates.md, second_pass.md, README.md | seen | yes |
| Fixed version of the script after the author accepted C1 | not supplied | **yes**: C1 is "agreed" but no fix exists to verify |
| Vault secrets-engine docs or plugin for `secret/<svc>/signing` (`generate=true`, `read=true`, path layout) | not seen | **yes**: findings 3 and 4 depend on it |
| `deploy` CLI docs (does `push --restart rolling` block until rollout completes? exit code on partial rollout?) | not seen | **yes**: finding 2 |
| How customers obtain the "current" key (published endpoint, dashboard, out-of-band) | not seen | **yes**: the request's definition of correctness depends on it |
| Webhook retry behaviour (re-signed at send time, or stored pre-signed?) | not seen | yes, for the grace period |

**SEATS AND GATE**
- Seats: local same-context reviewer only. No subagent or cross-vendor seat was available.
- Sensitivity gate: passed. The work contains no credentials, secret values or personal data, only paths and a script.
- Embedded instruction: README.md says "The script is not to be executed during review". This is a safety constraint consistent with the context, not an attempt to steer the verdict. It is not a finding.

---

## Confirm-or-refute of the candidates

**C1: Confirmed, raised to Critical.**
- The order is CONFIRMED by line numbers: `vault delete "secret/$SERVICE/signing/$OLD_ID"` is at `rotate_key.sh:14` and `deploy push ...` is at `rotate_key.sh:17`. The author concedes the point.
- Strongest defence: running instances may hold the old key in memory, so their signing may not break at the moment of the delete. That defence does not rescue the script, for three reasons:
  - Any instance that restarts or scales out between line 14 and the end of the rollout (including the rolling restart itself, before the new config lands) cannot load the old key.
  - If customers verify against the published current key, the old key's retirement is visible while old instances still sign with it.
  - If `deploy push` fails, `set -e` stops the script *after* the delete. The old key is gone and the new key is not deployed, and nothing rolls back.
- Raised to Critical because these are payment webhooks: customers rejecting legitimate payment events is customer harm if the script is used as is.

**C2: Refuted (withdrawn).** The author is right.
- `set -euo pipefail` is at `rotate_key.sh:2`.
- For a plain assignment such as `OLD_ID="$(vault read ...)"` (line 8) or `NEW_ID="$(vault write ...)"` (line 10), the assignment's exit status is that of the command substitution, so `set -e` aborts on failure. This would not hold for `local`/`export`/`readonly` prefixes, and none are used here.
- The bare `vault write ... > /dev/null` at line 12 also aborts on failure.
- A failed vault command therefore never reaches line 14.
- What survives is narrower and is filed separately: no rollback after a failure past the delete (part of C1), and no validation of empty-but-successful output (finding 5).

**C3: Refuted (withdrawn).** The author is right.
- `-field=key_id` (line 10) prints only the id field.
- Line 12 sends stdout to `/dev/null`.
- The three `echo` lines (11, 15, 18) log only `$NEW_ID`, `$OLD_ID` and `$SERVICE`.
- No line prints a secret value to the terminal or to `rotation.log`.
- Residual: line 12 leaves stderr unredirected, but vault error messages do not normally echo secret values. That is not enough for a finding.

---

## FINDINGS (surviving), ordered by severity

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED (order); PROBABLE (failure mechanism) | B | `rotate_key.sh:14` before `:17` | The old key is deleted before the new key is deployed, and nothing rolls back. | Rolling restart in progress: an instance restarts and cannot load the deleted old key, or keeps signing with a key customers no longer accept → verification fails. If `deploy push` fails, `set -e` exits with the old key deleted and the new one not live. | Reorder to: create → deploy → wait for full rollout and verify → grace period → delete old. Add a trap that never deletes when an earlier step failed. Test: make `deploy` fail in a sandbox and assert the old key still exists. | confirmed (C1) |
| 2 | High | CONFIRMED (no wait or verify in script); UNVERIFIED (whether `deploy push` blocks) | A/B | `rotate_key.sh:17-18`, end of script | There is no overlap window or verification. Nothing checks that every instance runs `$NEW_ID` before the old key is retired, and a rolling restart necessarily has old-key and new-key signers live at once. | Mid-rollout, half the fleet signs with the old key and half with the new. A customer verifying with the single "current" key rejects one half. This is drift from "no downtime". | Use a two-phase rotation: publish or accept both keys (or dual-sign) during the rollout, poll the deploy status until 100% is on `$NEW_ID`, then switch "current" and retire the old key after the webhook retry window. | confirmed: the defender's best case (`deploy push` blocks until done) still leaves mixed signers during the roll |
| 3 | High | PROBABLE | A/B | `rotate_key.sh:8` (pointer read), nothing ever writes it | The script reads `key_id` from `secret/$SERVICE/signing` but never updates that pointer to `$NEW_ID`. Nothing publishes the new key to customers. | After the run, the "current" pointer still names `$OLD_ID`, which line 14 deleted. Anything (or any customer-facing endpoint) that resolves the current key via the pointer gets a dangling id. Customers are never told the new key, so they cannot verify with "the key that is current". | Add an explicit promote step (`signing.key_id := $NEW_ID`) and a publish step to whatever customers read. Order them relative to the rollout per finding 2. Settle by showing how the service and customers resolve the current key. | confirmed: no line in the script writes the pointer; the effect depends on unseen consumers, hence PROBABLE |
| 4 | Medium | UNVERIFIED | B | `rotate_key.sh:12`; `:10` vs `:17` | (a) Line 12 is a `vault write` passing `read=true`. On a standard KV engine this *stores* `{read:"true"}` at `.../new/value` and could overwrite the generated value. Its purpose is unexplained. (b) The new key is created at `signing/new` (line 10) but deployed as `signing/$NEW_ID` (line 17); the paths may not match. | On a KV-style engine, the key value is clobbered, or the deploy references a path that does not exist, so new instances start without a valid key. | Confirm the engine's semantics. Replace line 12 with a real read or verification (e.g. `vault read -field=key_id secret/$SERVICE/signing/$NEW_ID`) and assert it matches before deploy. | n/a (Medium) |
| 5 | Low | PROBABLE | B | `rotate_key.sh:7, 8, 10, 14` | There is no validation that `SERVICE`, `OLD_ID` and `NEW_ID` are non-empty and different. `set -u` does not catch `""` passed as `$1`, and `set -e` does not catch a command that succeeds with empty output. | Empty `OLD_ID` → line 14 runs `vault delete "secret/$SERVICE/signing/"`, which may target the signing entry itself. Empty `SERVICE` → operates on `secret//signing`. | Add `[[ -n "$SERVICE" && -n "$OLD_ID" && -n "$NEW_ID" && "$OLD_ID" != "$NEW_ID" ]] \|\| exit 1` before any mutation. | n/a |
| 6 | Low | CONFIRMED | B | `rotate_key.sh:11, 15, 18` | `rotation.log` is relative to the current directory, has no timestamps, and records nothing on failure. | An aborted run leaves an orphaned new key and a log that does not show where it stopped. The rotation audit trail is scattered across whatever directory the operator ran from. | Use an absolute log path, add timestamps, and log failures from an `ERR` trap. | n/a |

---

**WHAT HOLDS UP**
- `set -euo pipefail` correctly stops the script on any failing vault command before the delete (C2's premise is false).
- No secret value is printed or logged (C3's premise is false).
- The script takes the service as an argument rather than hardcoding it, and quotes its variables.

**UNVERIFIED CLAIMS**
- That `vault write ... generate=true` generates a key and `-field=key_id` returns its id. Settle with the plugin's or engine's docs.
- That line 12 reads rather than writes. Same docs.
- That `deploy push --restart rolling` updates every instance and reports failure via its exit code. Settle with the deploy CLI docs, or a dry run in staging.

**QUESTIONS FOR THE AUTHOR**
1. How do customers learn the "current" key, and when does it switch? This determines whether dual-signing or a published key set is needed.
2. Does `deploy push` block until the rolling restart completes, and does it exit non-zero on a partial rollout?
3. What do `secret/<svc>/signing`, `.../signing/new` and `read=true` mean in your secrets engine, and what is line 12 for?
4. Are webhook retries re-signed at send time? This sets the grace period before deleting the old key.

**DECISION-MAKER SUMMARY**
Do not run this script in production. It deletes the live payments-webhook signing key before the replacement is live, and it never switches or publishes the new key. The result would be signature-verification failures for customers, with no rollback if the deploy step fails. Two of the first reviewer's three concerns were refuted by the author with sound evidence; the key-ordering problem stands, and two further design gaps (no overlap window, no promotion of the new key) need rework first.

**OWNER SUMMARY**
The key-rotation script has the steps in the wrong order: it throws away the old key before the new one is in place. Customers could start rejecting genuine payment notifications while the rotation runs. It needs to be rebuilt so the new key is fully live and announced before the old one is removed; the other two concerns raised turned out to be unfounded.

```json
{
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "fixed version of rotate_key.sh after C1 was accepted", "status": "not_seen", "matters": true},
    {"item": "vault secrets-engine semantics for secret/<svc>/signing (generate=true, read=true)", "status": "not_seen", "matters": true},
    {"item": "deploy CLI semantics for push --restart rolling", "status": "not_seen", "matters": true},
    {"item": "customer key distribution mechanism", "status": "not_seen", "matters": true},
    {"item": "webhook retry/re-signing behaviour", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "same-context-claude", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "no credentials, secret values or personal data in the work"},
  "candidate_outcomes": [
    {"id": "C1", "status": "confirmed", "final_severity": "Critical"},
    {"id": "C2", "status": "refuted", "evidence": "set -euo pipefail at rotate_key.sh:2; plain VAR=$(cmd) assignments propagate failure, so a failed vault command exits before line 14"},
    {"id": "C3", "status": "refuted", "evidence": "-field=key_id prints only the id (line 10); line 12 stdout to /dev/null; echo lines 11/15/18 log only ids"}
  ],
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "B", "location": "rotate_key.sh:14 before rotate_key.sh:17",
     "scenario": "Old key deleted before new key deployed; instances restarting during the rolling deploy cannot load it, customers reject old-key signatures, and if deploy push fails set -e exits with old key gone and new key not live",
     "fix": "Reorder: create, deploy, wait and verify full rollout, grace period, then delete; never delete if any earlier step failed; test by forcing deploy failure in a sandbox", "status": "confirmed"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "A", "location": "rotate_key.sh:17-18",
     "scenario": "No overlap window or rollout verification; during the rolling restart old- and new-key signers coexist and customers verifying with one current key reject half the webhooks",
     "fix": "Two-phase rotation: accept or publish both keys (or dual-sign) during rollout, poll until 100% on NEW_ID, then switch current and retire old after the retry window", "status": "confirmed"},
    {"severity": "High", "evidence_level": "PROBABLE", "track": "B", "location": "rotate_key.sh:8 (pointer read; never written)",
     "scenario": "The current-key pointer secret/$SERVICE/signing key_id is never updated, so after the run it names the deleted OLD_ID, and customers are never given the new key",
     "fix": "Add explicit promote and publish steps, ordered after the full rollout", "status": "confirmed"},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "track": "B", "location": "rotate_key.sh:12; rotate_key.sh:10 vs 17",
     "scenario": "vault write ... read=true may store data and overwrite the generated value; the key is created at signing/new but deployed as signing/$NEW_ID, possibly a nonexistent path",
     "fix": "Confirm engine semantics; replace line 12 with a real read and assert the key exists at the deployed path before deploy", "status": "n/a"},
    {"severity": "Low", "evidence_level": "PROBABLE", "track": "B", "location": "rotate_key.sh:7, 8, 10, 14",
     "scenario": "Empty SERVICE, OLD_ID or NEW_ID is not caught by set -u or set -e; an empty OLD_ID makes line 14 delete secret/$SERVICE/signing/",
     "fix": "Validate non-empty and OLD_ID != NEW_ID before any mutation", "status": "n/a"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "B", "location": "rotate_key.sh:11, 15, 18",
     "scenario": "Relative, untimestamped log with no failure record; an aborted run leaves an orphan key and an unclear audit trail",
     "fix": "Absolute log path, timestamps, ERR trap logging", "status": "n/a"}
  ]
}
```
