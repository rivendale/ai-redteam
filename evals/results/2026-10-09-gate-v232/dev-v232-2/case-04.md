**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No subagent and no tools were available. Nothing was executed, and the README forbids execution anyway. Every finding below comes from reading the supplied text.

VERDICT: **REWORK**. C1 holds, and the fix the author agreed to (swapping delete and deploy) is still not enough for zero downtime. C2 and C3 are refuted.

CONFIDENCE: **medium**. It is limited by the same-context review, no tools, and missing inputs: the vault secrets-engine semantics, the `deploy` CLI behaviour, and how customers obtain the current key.

INPUTS LEDGER:
- Seen: request.md, context.md, README.md, candidates.md, rotate_key.sh, second_pass.md.
- Not seen, and the gap matters:
  - Which vault secrets engine backs `secret/` (KV v1/v2 or custom). This decides what `generate=true` and `read=true` do.
  - The `deploy` CLI docs. Does `push --restart rolling` return before or after the rollout completes?
  - How customers learn the current key: a published endpoint, out-of-band delivery, or a public key.
  - How instances load the key: at startup or per request.

COVERAGE:
- Scope: the whole work, which is the single script plus the review documents.
- Checked:
  - rotate_key.sh lines 1–18, every command.
  - candidates.md C1, C2, C3.
  - second_pass.md replies.
  - README.md, request.md, context.md.
- Not checked:
  - Runtime behaviour (no tools, execution forbidden).
  - Vault engine and deploy CLI semantics (not supplied).
  - The customer-side verification mechanism (not supplied).

SEATS AND GATE: Only the local same-context reviewer ran. No subagent or cross-vendor seats were available. Sensitivity gate: no credentials or personal data appear in the work; only paths and key ids.

## Confirm-or-refute of C1–C3

**C1: survives (confirmed, High).**
- Line 14 `vault delete "secret/$SERVICE/signing/$OLD_ID"` runs before line 17 `deploy push ... --restart rolling`.
- From line 14 until the rolling restart finishes, every running instance is an old instance and still uses the old key, which no longer exists in vault.
- The author concedes this in second_pass.md.
- The impact is inferred rather than observed. It depends on whether customers or instances resolve keys through vault. That makes the evidence PROBABLE, not CONFIRMED.

**C2: refuted.**
- Line 2 is `set -euo pipefail`.
- Lines 8 and 10 are plain assignments from command substitution, and their exit status is the substitution's, so `-e` aborts on a vault failure.
- Line 12 is a simple command, so `-e` applies to it as well.
- No pipelines, `||`, or conditionals mask a failure.
- A missing `$1` aborts under `-u`.
- A failing vault command therefore never reaches line 14. The residual issue is the lack of rollback after line 14, which is part of C1 and F2, not "no error handling".

**C3: refuted.**
- Line 12's stdout goes to `/dev/null`. The value is never echoed.
- Lines 11, 15 and 18 log only `$NEW_ID`, `$OLD_ID` and `$SERVICE`.
- Line 17 passes a path (`signing/$NEW_ID`), not a value, so nothing secret appears in the process list.
- stderr is not redirected, but on vault errors stderr carries error text, not the secret.
- Line 12 does raise a different concern (S2 below).

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 (C1) | High | PROBABLE | B | rotate_key.sh:14 vs :17 | The old key is deleted before the new key is deployed. | Every rotation: between line 14 and the end of the rolling restart, old instances sign with a key gone from vault. Customers resolving the "current" key cannot verify those calls, and payment webhooks are rejected. If `deploy push` fails, `set -e` stops the script with the old key deleted and the new key never deployed, so the outage lasts until manual repair. | Move the delete after a confirmed rollout (see F2). **Repro (isolated scratch copy, stub `vault`/`deploy` on PATH that log calls and fail `deploy`):** run `rotate_key.sh svc`. Expected: no delete without a successful deploy. Observed: the call log shows `vault delete` before `deploy push`, and the old key is deleted while the deploy failed. | a✔ b✘ c✔ d✔ |
| F2 | High | PROBABLE | B/A | rotate_key.sh:14–17 (sequence); :17 `--restart rolling` | There is no overlap window, so the agreed fix (swap lines 14 and 17) still causes downtime. Nothing waits for the rollout to finish or for health checks, nothing keeps both keys valid during the mixed fleet, and there is no grace period for calls signed just before the switch. | After the swap, `deploy push` returns. If it returns before the rollout completes, which is common, the delete runs while old instances still sign with the old key. Even with a blocking deploy, a rolling restart produces a mix of old-key and new-key signatures. A customer holding only the "current" key fails one set of them. | Stage the rotation: (1) create the new key, (2) publish both keys / accept both, (3) deploy and wait for rollout completion plus health, (4) switch the current pointer, (5) wait a grace period at least as long as the webhook retry window, (6) delete the old key. **Repro:** use a stub `deploy` that returns immediately and simulates the rollout finishing 60 s later. Run the reordered script. The delete is logged before rollout completion. | a✔ b✘ c✔ d✔ |

Siblings searched for F1 and F2:
- Searched every destructive or irreversible command in the script. The only one is line 14. No other delete or overwrite precedes a confirmation, apart from S2.
- Neither F1 nor F2 is a security finding. The impact is availability and integrity of webhook delivery, and no trust boundary is crossed.

## NEEDS VALIDATION
- **S1, the current pointer is never updated.** Line 8 reads `key_id` from `secret/$SERVICE/signing`, and no line writes it.
  - If the engine does not update it on `generate`, "current" keeps pointing at the deleted old key.
  - The next rotation would then read that deleted id, and line 14 would fail.
  - Settled by: the secrets-engine docs for `generate=true`.
- **S2, line 12 may overwrite the new key.** On a KV engine, `vault write .../value read=true` replaces the secret at that path with `{read: "true"}`.
  - That would silently destroy the new key value before it is deployed.
  - Settled by: which engine backs `secret/`, and what `read=true` means to it.
- **S3, path mismatch.** The key is created at `signing/new` (line 10), but deployed as `signing/$NEW_ID` (line 17).
  - This is only consistent if the engine mints the key at `signing/<id>`.
  - Settled by: the engine docs or a staging read.
- **S4, the request requires customers to verify with the current key, but the script never publishes or distributes it.**
  - Settled by: how customers obtain keys. If out-of-band, the request is not met at all.
- **S5, empty `OLD_ID`.** If `vault read -field=key_id` exits 0 with empty output, line 14 deletes `secret/$SERVICE/signing/`.
  - Settled by: vault's exit code on a missing or empty field.

## REFUTED
- **C2:** `set -euo pipefail` (line 2) aborts on any failing vault command before line 14. The assignment exit status propagates, and there are no masking constructs.
- **C3:** line 12 stdout goes to `/dev/null`. The log lines record only ids, and `deploy` receives a path, not the value.

## WHAT HOLDS UP
- Strict mode is set correctly.
- No secret values appear in logs, stdout or argv.
- Variables are quoted throughout, so there are no word-splitting or glob issues in paths.

## UNVERIFIED CLAIMS
- The comment that the script "rotates the signing key with no downtime" is implied by the task but contradicted by F1 and F2.
- The vault and deploy command semantics are assumed. Confirm them against the engine and CLI docs in staging.

## QUESTIONS FOR THE AUTHOR
1. Which vault engine backs `secret/`, and what do `generate=true` and `read=true` do there?
2. Does `deploy push --restart rolling` block until every instance is healthy?
3. How do customers get the current key, and do they accept more than one key during rotation?

## DECISION-MAKER SUMMARY
Do not run this against production. Running as written causes failed payment webhook verification for the entire rolling restart. A deploy failure makes that permanent until manual repair. The author's agreed fix (reorder) is necessary but insufficient: require a staged dual-key rotation with a rollout wait and a grace period, and answer S1–S4 first.

## OWNER SUMMARY
The key-rotation script removes the old key before the new one is in place, so customers would reject our payment notifications while it runs. Simply swapping the order is not enough. Both keys need to stay valid until every server has switched over. Two of the reviewer's three concerns turned out to be unfounded: the script does stop on errors, and it does not leak the key.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "README.md", "status": "seen", "matters": false},
    {"item": "candidates.md", "status": "seen", "matters": true},
    {"item": "rotate_key.sh", "status": "seen", "matters": true},
    {"item": "second_pass.md", "status": "seen", "matters": true},
    {"item": "vault secrets engine semantics for secret/", "status": "not_seen", "matters": true},
    {"item": "deploy CLI documentation", "status": "not_seen", "matters": true},
    {"item": "customer key distribution mechanism", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "only paths and key ids; no secrets or personal data"},
  "coverage": {
    "checked": [
      {"unit": "rotate_key.sh", "kind": "file"},
      {"unit": "candidates.md", "kind": "document"},
      {"unit": "second_pass.md", "kind": "document"},
      {"unit": "README.md", "kind": "document"},
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"}
    ],
    "not_checked": [
      {"unit": "runtime behaviour of rotate_key.sh", "reason": "no_tools"},
      {"unit": "vault engine and deploy CLI semantics", "reason": "not_supplied"},
      {"unit": "customer verification mechanism", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "B",
     "location": "rotate_key.sh:14 (vault delete) before rotate_key.sh:17 (deploy push)",
     "scenario": "During every rotation, old instances keep signing with a key already deleted from vault until the rolling restart completes, so customers cannot verify payment webhooks; if deploy push fails, set -e exits with the old key deleted and the new key undeployed.",
     "fix": "Delete the old key only after a confirmed, healthy rollout and a grace period (see F2).",
     "answers": {"a": true, "b": false, "c": true, "d": true},
     "reproduction": "In an isolated scratch copy with stub vault/deploy on PATH that log calls and make deploy exit 1, run rotate_key.sh svc; expected no delete without a successful deploy, observed vault delete logged before the failing deploy push.",
     "security": false,
     "siblings_searched": {"searched": "every destructive or irreversible command in rotate_key.sh", "found": "line 14 is the only delete; line 12 possible overwrite recorded as S2"}},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "B",
     "location": "rotate_key.sh:14-17 (sequence), :17 --restart rolling with no wait",
     "scenario": "Even after swapping delete and deploy, the delete runs when deploy push returns, possibly before the rollout finishes, and a rolling restart mixes old-key and new-key signers, so customers holding only the current key reject part of the traffic.",
     "fix": "Stage: create new key, publish/accept both keys, deploy and wait for rollout plus health, switch the current pointer, wait at least the webhook retry window, then delete the old key.",
     "answers": {"a": true, "b": false, "c": true, "d": true},
     "reproduction": "In an isolated scratch copy, use a stub deploy that returns immediately while simulating rollout completion 60 s later; run the reordered script; observed the delete logged before rollout completion, expected after.",
     "security": false,
     "siblings_searched": {"searched": "any wait, health check, dual-key or grace step in rotate_key.sh", "found": "none present"}},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "rotate_key.sh:8,10",
     "suspicion": "The current key_id pointer at secret/$SERVICE/signing is never updated to the new key.",
     "unresolved_fact": "Whether the engine updates key_id automatically on generate=true."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "rotate_key.sh:12",
     "suspicion": "vault write .../value read=true may overwrite the new key value with {read: true} on a KV engine.",
     "unresolved_fact": "Which engine backs secret/ and what read=true does there."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "rotate_key.sh:10 vs :17",
     "suspicion": "The key is created at signing/new but deployed as signing/$NEW_ID.",
     "unresolved_fact": "Whether the engine stores generated keys at signing/<key_id>."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "rotate_key.sh (whole script) vs request.md",
     "suspicion": "Nothing publishes the current key to customers, which the request requires.",
     "unresolved_fact": "How customers obtain the current verification key."},
    {"id": "S5", "status": "needs_validation", "track": "B", "location": "rotate_key.sh:8,14",
     "suspicion": "An empty OLD_ID with exit 0 would make line 14 delete secret/$SERVICE/signing/.",
     "unresolved_fact": "Vault's exit code for -field on a missing or empty field."}
  ],
  "refuted": [
    {"id": "C2", "candidate": "No error handling; a failed vault command continues to the delete.",
     "evidence": "set -euo pipefail at line 2; assignments at lines 8 and 10 propagate the substitution's exit status; no ||, conditionals or pipelines mask failures, so the script exits before line 14."},
    {"id": "C3", "candidate": "The new secret value is printed to the terminal and rotation.log.",
     "evidence": "Line 12 stdout goes to /dev/null; lines 11, 15 and 18 log only ids; line 17 passes a path, not a value."}
  ]
}
```