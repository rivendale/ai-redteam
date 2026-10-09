VERDICT: **REWORK**. C1 survives the confirm-or-refute round and is Critical: the script deletes the only key the running service signs with before the replacement is deployed, and it has no rollback. Separately, a rolling restart with a single "current" key cannot meet the no-downtime requirement as written.

CONFIDENCE: **medium**. I had no tools, so I could not run the script, read the vault mount configuration, or read the deploy CLI or service code. I am a single reviewer who read the first reviewer's candidates and the author's replies, so there is an anchoring risk. Re-run in a fresh session with the vault and deploy configuration before relying on this for production payments.

INPUTS LEDGER:
- **Seen:** request.md, context.md, README.md, candidates.md, rotate_key.sh, second_pass.md.
- **Not seen, and the gap matters:**
  - The secrets engine mounted at `secret/`. It decides what `generate=true`, `read=true` and `-field=key_id` actually do.
  - The `deploy` CLI's `push --secret` semantics.
  - How the service loads the signing key: once at startup, or from vault on each request.
  - How customers obtain the "current" key. This decides how bad the rotation-window failure is.

COVERAGE:
- **Checked:** every line of rotate_key.sh (1–18), candidates C1–C3, the author's replies, and the README.
- **Not checked:** vault engine behaviour, deploy CLI behaviour, service key loading, the customer key-distribution mechanism.

SEATS AND GATE: one local reviewer ran. No subagent or cross-vendor seats were available because this session has no tools. The sensitivity gate passed: no secrets, personal data or client data appear in the work, only the paths and the names of key IDs.

## Confirm-or-refute round

**C1 is CONFIRMED and raised to Critical.**
- Line 14 (`vault delete "secret/$SERVICE/signing/$OLD_ID"`) runs before line 17 (`deploy push ... --restart rolling`). The author concedes the ordering.
- Defending it as strongly as I can: if instances hold the key in memory, deleting it from vault might not break signing during the rollout. Even so, this does not save the script, because `set -euo pipefail` (line 2) interacts badly with the order. If `deploy push` fails after line 14, the script exits with the old key already deleted and the new key never deployed.
- From that point, any instance that restarts or scales out and resolves `signing/$OLD_ID` has no key. Nothing in the script restores it.

**C2 is REFUTED.**
- Line 2 is `set -euo pipefail`. The command substitutions at lines 8 and 10 are plain assignments, not `local` or `export`, so a non-zero exit from `vault` aborts the script.
- A failure at line 12 also aborts. None of these can reach line 14.
- The author's evidence holds. A narrower, different suspicion (a command that succeeds but returns empty output) is listed as S1 below.

**C3 is REFUTED.**
- Line 12 sends stdout to `/dev/null`.
- Lines 11, 15 and 18 log only `$NEW_ID` and `$OLD_ID`, which are identifiers, never the value.
- No line echoes the value to the terminal. Stderr from line 12 is not redirected, but a successful write does not print the payload to stderr.
- A separate concern about line 12 is listed as S2 below.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | B | rotate_key.sh:14 before :17; line 2 | The old key is deleted before the new key is deployed, and there is no rollback. | The deploy fails (auth expired, rollout failure). `set -e` exits after the delete. The old key is gone and the new key is not live, so the next restart or scale-out has no signing key and webhooks stop. If instances read the key per request, signing fails for the whole rollout even when the deploy succeeds. | Order the steps as: create, deploy, verify that every instance is on `NEW_ID`, wait for the overlap window, then delete. Add a `trap` that never deletes on error. **Repro (in staging):** stub `deploy` to `exit 1`, run the script, and check that `secret/$SERVICE/signing/$OLD_ID` still exists. Expected: it exists. Observed: it is deleted. | a✓ b✓ c✓ d✓ |
| F2 | High | PROBABLE | A/B | rotate_key.sh:17 (`--restart rolling`); whole script | The script has no key-overlap window and no step that publishes the new key to customers. This drifts from the "no downtime" requirement. | During a rolling restart, old and new instances sign at the same time with different keys. A customer verifying with the single "current" key rejects every call from the instances on the other key. Nothing in the script tells customers about `NEW_ID`, so they cannot verify new signatures at all. | Rotate in phases: (1) publish the new key alongside the old one (dual-key verification, or multiple signatures per header). (2) Switch signing to the new key. (3) After the retry window passes, retire the old key. **Test:** during a staging rollout, send webhooks continuously and assert zero verification failures on the customer side. | a✓ b✗ c✓ d✓ |

NEEDS VALIDATION (no severity):
- **S1, lines 8, 10 and 14:** an empty `OLD_ID` or `NEW_ID` passes `set -u`. With an empty `OLD_ID`, line 14 deletes `secret/$SERVICE/signing/`, which may be the parent path. **Settled by:** whether `vault ... -field=key_id` exits non-zero when the field is missing or empty on this engine. Add `[[ -n $OLD_ID && -n $NEW_ID ]] || exit 1` regardless.
- **S2, line 12:** `vault write .../new/value read=true` is not a read. On a KV engine it would overwrite that path with `{read: "true"}` and possibly clobber the new key's value. **Settled by:** which secrets engine or plugin is mounted at `secret/` and what this call does on it.
- **S3, lines 8, 10 and 17:** the paths do not line up. The script reads `signing`, creates at `signing/new`, and deploys `signing/$NEW_ID`, and nothing updates the `signing` pointer to `NEW_ID`. A second run would read the already-deleted `OLD_ID`. **Settled by:** whether the engine advances the pointer and materializes `signing/<id>` on `generate=true`.

REFUTED:
- **C2:** `set -euo pipefail` at line 2 aborts on any failing `vault` command before line 14. The substitutions at lines 8 and 10 are not masked by `local` or `export`.
- **C3:** line 12 discards stdout, and the log lines 11, 15 and 18 write only key IDs. No line prints the secret value.

WHAT HOLDS UP:
- Strict mode (line 2).
- No secret value reaches the terminal or the log.
- Missing-argument handling: `$1` under `set -u` fails fast.
- The author conceded C1 and refuted C2 and C3 with exact line evidence.

UNVERIFIED CLAIMS: the script's own usage comment says it only needs the CLIs to be logged in. Its correctness actually depends on the vault engine semantics in S2 and S3 and on the deploy rollout behaviour. Confirm these by running it against a staging vault mount and a staging deploy target, and recording the resulting paths.

QUESTIONS FOR THE AUTHOR:
1. How do customers get the "current" key: a published endpoint, a dashboard, or an email? Can they hold two keys at once?
2. Does the service read the signing key from vault on each request or only at startup?
3. What engine is mounted at `secret/`, and what is line 12 meant to do?

DECISION-MAKER SUMMARY: Do not run this in production. F1 means a single failed deploy leaves payments webhooks with no signing key and no automatic recovery. F2 means even a successful run breaks customer verification during the rollout. The script needs a create, publish both keys, switch, then retire sequence, plus rollback, before anyone uses it.

OWNER SUMMARY: The key-rotation script removes the old signing key before the new one is in place. If anything goes wrong partway through, payment notifications to customers could stop working until someone intervenes. Even when it works, customers would see failed checks during the switchover, so the script needs to be reworked to keep both keys valid for a while before retiring the old one.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "rotate_key.sh", "status": "seen", "matters": true},
    {"item": "candidates.md", "status": "seen", "matters": true},
    {"item": "second_pass.md", "status": "seen", "matters": true},
    {"item": "README.md", "status": "seen", "matters": false},
    {"item": "vault secrets engine config at secret/", "status": "not_seen", "matters": true},
    {"item": "deploy CLI push/rollout semantics", "status": "not_seen", "matters": true},
    {"item": "service signing-key loading code", "status": "not_seen", "matters": true},
    {"item": "customer key-distribution mechanism", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "rotate_key.sh", "kind": "file"},
      {"unit": "candidates.md", "kind": "file"},
      {"unit": "second_pass.md", "kind": "file"},
      {"unit": "README.md", "kind": "file"},
      {"unit": "C1 delete-before-deploy", "kind": "claim"},
      {"unit": "C2 no error handling", "kind": "claim"},
      {"unit": "C3 secret printed/logged", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "vault engine at secret/", "reason": "not supplied; no tools"},
      {"unit": "deploy CLI", "reason": "not supplied; no tools"},
      {"unit": "service key loading", "reason": "not supplied"},
      {"unit": "customer key distribution", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "rotate_key.sh:14 (delete) precedes rotate_key.sh:17 (deploy); line 2 set -e",
     "scenario": "deploy push fails after vault delete; set -e exits with old key deleted and new key not live; next restart or scale-out has no signing key and payment webhooks stop. If instances read the key per request, signing fails during the rollout even on success.",
     "fix": "Order: create, deploy, verify all instances on NEW_ID, wait overlap window, then delete; add an error trap that never deletes on failure.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "In staging, stub deploy to exit 1 and run the script; expect secret/$SERVICE/signing/$OLD_ID to still exist, observe it deleted."},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "A",
     "location": "rotate_key.sh:17 (--restart rolling); whole script",
     "scenario": "During the rolling restart old and new instances sign with different keys; customers verifying with the single current key reject calls from the other set, and nothing publishes NEW_ID to customers.",
     "fix": "Phased rotation: publish new key alongside old (dual-key verification), switch signing, retire old key after the retry window.",
     "answers": {"a": true, "b": false, "c": true, "d": true},
     "reproduction": "Send continuous webhooks during a staging rollout; assert zero customer-side verification failures; observe failures for calls from instances on the non-current key."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "rotate_key.sh:8,10,14",
     "suspicion": "Empty OLD_ID/NEW_ID passes set -u; line 14 could delete secret/$SERVICE/signing/.",
     "unresolved_fact": "Whether vault -field=key_id exits non-zero on a missing or empty field for this engine."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "rotate_key.sh:12",
     "suspicion": "vault write ... read=true may overwrite the new key's value with {read: true} on a KV engine.",
     "unresolved_fact": "Which secrets engine is mounted at secret/ and what this write does there."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "rotate_key.sh:8,10,17",
     "suspicion": "Nothing updates the signing pointer to NEW_ID or materializes signing/$NEW_ID; a second run would read the deleted OLD_ID.",
     "unresolved_fact": "Whether generate=true on signing/new updates the pointer and creates signing/<id>."}
  ],
  "refuted": [
    {"id": "C2", "candidate": "A failed vault command does not stop the script and it continues to delete the old key.",
     "evidence": "set -euo pipefail at line 2; the substitutions at lines 8 and 10 are plain assignments (not local/export), so failures abort before line 14."},
    {"id": "C3", "candidate": "The new secret value is printed to the terminal and into rotation.log.",
     "evidence": "Line 12 redirects stdout to /dev/null; log lines 11, 15 and 18 write only key IDs; no line echoes the value."}
  ]
}
```