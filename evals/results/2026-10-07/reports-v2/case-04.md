**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No tools were available in this session, so nothing was executed. That matches the README instruction not to run the script. Every evidence label below comes from reading the code.

VERDICT: **REWORK**. C1 survives and is a production-breaking ordering bug. The script also never creates an overlap window in which both keys verify, and that window is the core of "no downtime".

CONFIDENCE: **medium**. Limits: this is a same-context review with no execution. The behaviour of `vault` and `deploy` is unverified. The script uses `generate=true`, `read=true` and `-field=key_id` on `write`, which looks like a custom secrets engine rather than stock KV. How customers obtain the "current" key is not stated.

INPUTS LEDGER:
- Seen: request.md, context.md, README.md, candidates.md, rotate_key.sh, second_pass.md.
- Not seen, and it matters: how customers fetch or receive the current verification key. The no-downtime requirement depends entirely on this.
- Not seen, and it matters: the semantics of the vault engine mounted at `secret/` and of `deploy push --restart rolling`. In particular, whether `deploy push` blocks until the rollout finishes and exits non-zero on failure.
- Not seen, and it matters less: whether running instances read the key from vault per request or cache it at startup. This changes the C1 mechanism but not the verdict.

SEATS AND GATE: one local same-context reviewer ran. No subagent or cross-vendor seats were available. Sensitivity gate passed: the work contains no secrets, PII or client data.

## Confirm-or-refute round on C1–C3

**C1 (delete before deploy): CONFIRMED, with the mechanism refined.**
- Order in the script: `vault delete ".../signing/$OLD_ID"` comes before `deploy push ... --restart rolling`. The author agrees.
- The failure does not depend on whether instances cache the key:
  - The old key is destroyed irreversibly before the new key is live anywhere.
  - Any customer or instance that resolves the old key id during the rolling restart fails. Webhook retries of calls already signed with the old key also fail.
  - If `deploy push` fails, `set -e` stops the script after the delete. The fleet is then left signing with a key that no longer exists, and there is nothing to roll back to.

**C2 (no error handling): REFUTED.**
- Line 2 is `set -euo pipefail`.
- Plain assignments like `OLD_ID="$(vault read ...)"` take the exit status of the command substitution, so errexit fires on failure. These assignments are not masked by `local` or `export`.
- A bare `vault write ... > /dev/null` also fails the script.
- A failing vault command therefore cannot reach `vault delete`. The author's rebuttal holds.
- One residual gap is noted as F4 below: errexit only helps if the CLIs exit non-zero on failure.

**C3 (secret printed or logged): REFUTED.**
- The only value-reading command sends stdout to `/dev/null`.
- Log lines contain only `$NEW_ID` and `$OLD_ID`.
- `deploy push --secret "signing/$NEW_ID"` passes a path, not the value, so the secret is not exposed in `ps` or argv.
- Theoretical stderr leakage is not evidence of exposure. The author's rebuttal holds.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 (C1) | High | CONFIRMED | B | `rotate_key.sh` `vault delete` line, before the `deploy push` line | The old key is deleted before the new key is deployed, and no rollback is possible. | During the rolling restart, or after a failed deploy, signatures made with the old key cannot be verified. Customers' webhook verification fails, and the old key cannot be restored. | Delete the old key last, only after the deploy is confirmed healthy. See finding 2 for the grace period. | confirmed |
| 2 | High | PROBABLE (the customer key-distribution path was not seen) | B / drift | Whole script; the request's "no downtime" requirement | Even with the steps reordered, there is no window in which both keys are accepted. Old-key delete follows the deploy directly. | Mid-rollout, old and new instances sign with different keys, so verification fails against whichever key the customer treats as "current". Retries of calls signed before rotation fail once the old key is gone. | Three phases: (1) publish the new key to customers as valid, alongside the old one; (2) deploy signing with the new key and wait for rollout to finish; (3) delete the old key after the retry window expires. Test: send webhooks continuously through a staging rotation and assert zero verification failures. | confirmed (strongest defence: "customers cache old keys". Not stated anywhere, and retries still break.) |
| 3 | Medium | PROBABLE | B | The `OLD_ID` read of `secret/$SERVICE/signing` field `key_id`; no corresponding write anywhere | The "current" pointer is never updated to `NEW_ID`. The new key is created under `signing/new`. | Anything that resolves "current" through this pointer, such as customer key lookup, still gets the deleted old id. On the next run, `OLD_ID` is the already-deleted key, so the delete fails, or the wrong key gets deleted. | Promote `NEW_ID` atomically to `signing.key_id` at the right phase. Test: run the rotation twice in staging. | n/a |
| 4 | Medium | UNVERIFIED | B | `deploy push ... --restart rolling` | Unknown whether the command blocks until rollout completes and exits non-zero on failure. | If it returns right after starting the rollout, "deployed" is logged and later steps run against a half-rolled fleet. | Check the CLI docs, or add an explicit rollout-status wait and health check. | n/a |
| 5 | Medium | UNVERIFIED | B (hallucination) | `vault write -field=key_id .../signing/new generate=true`; `vault write .../new/value read=true` | Stock Vault KV would simply store `generate=true` as data and return no `key_id`. These calls only work with a custom engine. The `read=true` line has no visible purpose. | On stock KV, `NEW_ID` comes back empty or the command errors. `set -e` probably stops the script, but the design does not work there. | Confirm which engine is mounted at `secret/`. Remove the `read=true` line or document why it is needed. | n/a |
| 6 | Low | CONFIRMED | B | `>> rotation.log` | The log path is relative to the current working directory, and the log has no timestamps. | The audit trail ends up scattered across directories or is lost. | Use an absolute path and add timestamps. | n/a |

## WHAT HOLDS UP
- Error propagation via `set -euo pipefail`. C2 is refuted.
- Secret handling: no value appears in logs, stdout or argv. C3 is refuted.
- Missing `$1` fails fast under `set -u`.

## UNVERIFIED CLAIMS
- That `vault write ... generate=true` returns a `key_id`. Settle by checking the engine docs or running against staging vault.
- That `deploy push` waits for the rollout to finish. Settle with the CLI docs or an exit-code test that deliberately fails a rollout.
- How customers learn the current key. Ask the author or read the verification docs.

## QUESTIONS FOR THE AUTHOR
1. How do customers get the verification key: a fetch per call, a cached key, or a manual update? This decides how long the overlap window must be.
2. What is the webhook retry horizon? The old key must stay valid at least that long.
3. Is `secret/` a custom key engine, and what promotes a key to "current"?

## DECISION-MAKER SUMMARY
Do not run this against production. It destroys the old signing key before the new one is live and never provides a period in which both keys verify, so customers will see signature failures during every rotation. Rework it as publish, then deploy and wait, then expire after the retry window. C2 and C3 were correctly refuted and need no action.

```json
{
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "customer key distribution mechanism", "status": "not_seen", "matters": true},
    {"item": "vault engine / deploy CLI semantics", "status": "not_seen", "matters": true},
    {"item": "rotate_key.sh, candidates.md, second_pass.md, request.md, context.md", "status": "seen", "matters": true}
  ],
  "seats": [{"vendor": "same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "candidate_rulings": {"C1": "confirmed", "C2": "refuted: set -euo pipefail aborts on failed command substitution in plain assignment", "C3": "refuted: value read goes to /dev/null; log holds ids only"},
  "findings": [
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "B", "location": "rotate_key.sh: vault delete line precedes deploy push line",
     "scenario": "Old key irreversibly deleted before new key is live; during rolling restart or after a failed deploy, old-key signatures cannot be verified and there is no rollback",
     "fix": "Delete old key only after deploy is confirmed healthy and the grace window has passed", "status": "confirmed"},
    {"severity": "High", "evidence_level": "PROBABLE", "track": "B", "location": "rotate_key.sh (whole flow) vs request 'no downtime'",
     "scenario": "No dual-key acceptance window: mixed fleet during rollout and retries of pre-rotation calls fail customer verification even if steps are reordered",
     "fix": "Publish new key as valid alongside old, deploy and wait for completion, expire old key after the retry horizon; staging test with continuous webhook traffic asserting zero failures", "status": "confirmed"},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "B", "location": "rotate_key.sh: OLD_ID read of secret/$SERVICE/signing key_id; no write promoting NEW_ID",
     "scenario": "Current-key pointer still names the deleted key; key lookups resolve to it, and the next rotation targets a nonexistent or wrong key",
     "fix": "Atomically promote NEW_ID to the current pointer; test by running rotation twice in staging", "status": "n/a"},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "track": "B", "location": "rotate_key.sh: deploy push --restart rolling",
     "scenario": "If the command returns before rollout completes or exits 0 on rollout failure, later steps run against a half-rolled fleet",
     "fix": "Add an explicit rollout-status wait and health check; verify exit-code behaviour", "status": "n/a"},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "track": "B", "location": "rotate_key.sh: vault write ... generate=true / read=true",
     "scenario": "On stock Vault KV these store literal data and return no key_id; the design depends on an unconfirmed custom engine",
     "fix": "Confirm the engine mounted at secret/; remove or justify the read=true line", "status": "n/a"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "B", "location": "rotate_key.sh: >> rotation.log",
     "scenario": "Relative, untimestamped log scatters across working directories and weakens the audit trail",
     "fix": "Use an absolute log path and add timestamps", "status": "n/a"}
  ]
}
```
