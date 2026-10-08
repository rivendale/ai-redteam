**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** I had no tools, so I did not run the script, the vault CLI or the deploy CLI. Every judgment below comes from reading the script text against documented bash semantics.

**VERDICT: REWORK.** C1 holds and is worse than reported: the script deletes the only valid key before the new one is live. It also never makes the new key "current", and it has no overlap window, which a no-downtime rotation needs.

**CONFIDENCE: medium.** Three things limit it: this is a same-context review, I could not run anything, and I did not see the vault secrets-engine layout, the deploy CLI's semantics, or how customers get the current key.

**INPUTS LEDGER**

| Item | Status | Matters |
|---|---|---|
| request.md, context.md, candidates.md, second_pass.md, rotate_key.sh, README.md | seen | — |
| Vault mount/engine behind `secret/` (KV or a custom plugin supporting `generate=true`, `read=true`) | not seen | **yes**: lines 10 and 12 depend on it |
| `deploy` CLI docs (does `--restart rolling` block until the rollout finishes; exit codes) | not seen | **yes**: decides whether "deployed" is ever true when it is logged |
| How customers obtain the verification key (published endpoint, dashboard, read from `secret/$SERVICE/signing`) | not seen | **yes**: decides whether the new key ever reaches customers |
| Webhook signer code (single or multiple signatures; retry queue keeps the original signature or re-signs) | not seen | yes: affects the overlap design |

README's "not to be executed during review" is an ordinary operational constraint, not an attempt to steer the verdict, so it is not a finding.

**SEATS AND GATE:** Only the local same-context reviewer ran. No subagent or cross-vendor seats were available. Sensitivity gate: the script contains no secrets or personal data (it handles key ids, not key values), so the gate passed.

## Confirm-or-refute round on C1–C3

**C1 (delete before deploy): CONFIRMED, raised to Critical.**
- The order in rotate_key.sh is: `vault delete "secret/$SERVICE/signing/$OLD_ID"` (line 14), then `deploy push ... --restart rolling` (line 17).
- The author concedes it, and the text bears it out.
- Raised to Critical because of what happens when the deploy fails. Suppose `deploy push` fails (auth expired, bad rollout). `set -e` then exits *after* the delete. The service is left signing with a key that no longer exists, and there is no rollback. On a production payments webhook, that means customers reject payment events.

**C2 (no error handling): REFUTED as stated.**
- Line 2 is `set -euo pipefail`.
- Every vault call is either a plain `VAR="$(cmd)"` assignment or a bare command. Under `set -e`, a plain assignment takes the exit status of its command substitution, so a failed `vault read` or `vault write` aborts the script before line 14. (The masking case is `local`/`export VAR=$(...)`, and the script uses neither.)
- The author's defense holds. What `set -e` does *not* provide (no rollback, no empty-value check) is filed as a new finding (#4), not as C2.

**C3 (secret printed to terminal and log): REFUTED.**
- Line 10 uses `-field=key_id`, so only the id is emitted.
- Line 11 logs `$NEW_ID`, which is an id.
- Line 12's stdout goes to `/dev/null`.
- `deploy push` receives the path `signing/$NEW_ID`, not the value.
- No line writes a key value to the terminal or to rotation.log. Line 12 has a separate problem, filed as #3.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | B | rotate_key.sh:14 vs :17 | The old key is deleted before the new key is deployed, and nothing rolls back. | Instances keep signing with the deleted old key until the rolling restart reaches them. If `deploy push` fails, `set -e` exits with the old key already gone. Either way, customers fail verification on payment webhooks. | Order: create → deploy and wait for the rollout to complete → overlap window → retire the old key. Add a `trap` that aborts before any delete if a deploy or health check fails. | confirmed (C1) |
| 2 | High | PROBABLE | B/A (drift) | whole script; line 8 vs line 10 | No overlap window, and the new key never becomes "current". `secret/$SERVICE/signing` (where OLD_ID is read) is never updated to NEW_ID; the new key lives only under `.../signing/new`. A rolling restart also means old and new signers run side by side. | This holds even with #1 fixed. A customer who has switched to the new key rejects calls from instances not yet restarted, plus queued retries signed earlier. A customer who reads "current" from `signing` still gets OLD_ID, which no longer exists. Either way, "no downtime" is not met. | Publish the new key as *accepted alongside* the old one, or have the signer emit both signatures (header carrying multiple `v1=` values). Promote NEW_ID to current. Retire the old key only after the rollout completes plus the maximum retry age. Test: replay a webhook signed by an old-key instance mid-rollout and confirm it verifies. | confirmed: no line writes NEW_ID to `secret/$SERVICE/signing`. It stays PROBABLE only because I have not seen how customers get the key. |
| 3 | Medium | UNVERIFIED | B (hallucination) | rotate_key.sh:10, :12 | `vault write ... generate=true` and `vault write .../value read=true` rely on engine behavior I could not check. On a KV engine, line 12 *writes* `{read: "true"}` at `signing/new/value`; it does not read anything. | On a KV mount, line 12 creates or overwrites a secret, and line 10 does not generate a key at all. At best line 12 is dead code, since its output is discarded. | Confirm the mount type (`vault secrets list`). Use `vault read` or `kv get` for reads. Remove line 12 if nothing consumes it. | n/a (Medium) |
| 4 | Medium | PROBABLE | B | rotate_key.sh:8, :10, :17–18 | No validation of results. An empty `NEW_ID` or `OLD_ID` passes `set -u`, since the variable is set but empty. The script also does not check that the rollout actually finished before logging "deployed". | Vault exits 0 with an empty field → line 14 runs `vault delete secret/$SERVICE/signing/` (it deletes whatever that path resolves to), and deploy pushes `signing/`. If the deploy CLI returns before the rollout finishes, the log claims success during a partial rollout. | Add `[[ -n $OLD_ID && -n $NEW_ID && $OLD_ID != $NEW_ID ]] \|\| exit 1`. Poll the rollout status, then check that the running instances report NEW_ID. | n/a |
| 5 | Low | CONFIRMED | B | rotate_key.sh:8–17 | No lock against two runs at once. `rotation.log` is relative to the cwd. | Two operators run it together → two new keys, and one is deployed while the other is orphaned. Logs end up scattered across directories. | Take a lock (vault CAS or `flock`) and use an absolute log path with timestamps. | n/a |

## WHAT HOLDS UP
- `set -euo pipefail` does stop the script on any failed vault or deploy command, so C2 is refuted.
- No key value reaches stdout, rotation.log or the command line, so C3 is refuted.
- Logging ids rather than values is the right choice.

## UNVERIFIED CLAIMS
- That `generate=true` creates a key on this mount. Settle it with the mount type and the plugin docs.
- That `deploy push --restart rolling` blocks until the rollout is complete. Settle it with the CLI docs, or with a dry run against staging.
- How customers learn the current key. Settle it with the customer-facing key distribution docs and code.

## QUESTIONS FOR THE AUTHOR
1. Where do customers get the verification key, and can they accept two keys during the overlap?
2. Can the signer emit two signatures per webhook?
3. How long can a webhook retry carry an old signature?

## DECISION-MAKER SUMMARY
Do not run this in production. It deletes the live signing key before the replacement is deployed and never publishes the new key as current. A failed or slow deploy would make customers reject payment webhooks. Of the first review's findings, C1 is confirmed (raised to Critical); C2 and C3 are refuted on the evidence; the larger gap is the missing overlap window.

## OWNER SUMMARY
The key-rotation script would cause customers to reject our payment notifications while it runs, and would leave things broken if the deploy step fails. The concerns about leaking the secret and about ignoring errors were checked and do not hold. The script needs to be reworked so the old and new keys are both accepted for a while before the old one is removed.

```json
{
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "vault engine behind secret/", "status": "not_seen", "matters": true},
    {"item": "deploy CLI semantics", "status": "not_seen", "matters": true},
    {"item": "customer key distribution", "status": "not_seen", "matters": true},
    {"item": "webhook signer code", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "only key ids, no secrets or personal data"},
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "B", "location": "rotate_key.sh:14 vs :17",
     "scenario": "Old key deleted before the new key is deployed; instances still sign with the deleted key during the rolling restart, and a failed deploy exits with no valid key and no rollback; customers reject payment webhooks.",
     "fix": "Create, deploy and wait for the rollout, overlap, then retire the old key; trap and abort before any delete on failure.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "PROBABLE", "track": "B", "location": "rotate_key.sh:8,:10 (whole script)",
     "scenario": "NEW_ID is never promoted to secret/$SERVICE/signing and there is no overlap window; during the mixed rollout and retries, customers on either key fail verification.",
     "fix": "Accept both keys or dual-sign during the overlap; promote NEW_ID; retire the old key after the rollout plus the max retry age; replay test mid-rollout.", "status": "confirmed"},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "track": "B", "location": "rotate_key.sh:10,:12",
     "scenario": "On a KV mount, line 12 writes {read:true} rather than reading, and generate=true is not a KV feature.",
     "fix": "Confirm the mount type; use vault read/kv get; remove line 12 if unused."},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "B", "location": "rotate_key.sh:8,:10,:17-18",
     "scenario": "Empty ids pass set -u and lead to deleting secret/$SERVICE/signing/; deploy logged as done before the rollout completes.",
     "fix": "Validate the ids are non-empty and distinct; poll the rollout and verify instances report NEW_ID."},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "B", "location": "rotate_key.sh:8-17",
     "scenario": "Two concurrent runs create two keys and orphan one; log written to whatever the cwd is.",
     "fix": "Lock (flock or vault CAS); absolute timestamped log path."}
  ],
  "candidate_outcomes": {"C1": "confirmed (raised to Critical)", "C2": "refuted: set -euo pipefail on line 2 aborts on plain-assignment command substitution", "C3": "refuted: only key ids reach the log; line 12 stdout goes to /dev/null"}
}
```