# Redteam report: `rotate_key.sh` confirm-or-refute round

**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No subagent and no tools were available, so nothing was executed. The script was reviewed by reading it, and bash semantics were reasoned from the language rules.

**VERDICT: REWORK.** The delete-before-deploy ordering (C1) is real. Fixing it still would not give no-downtime rotation, because the script has no overlap window: customers hold one key while a rolling restart has the fleet signing with two.

**CONFIDENCE: medium.** Limited by the same-context review, no execution, and missing inputs: how the service loads its key, how customers get keys, and the semantics of the vault engine and the deploy CLI.

**INPUTS LEDGER**
- **Seen:**
  - `request.md`
  - `context.md`
  - `README.md`
  - `candidates.md`
  - `second_pass.md`
  - `rotate_key.sh`
- **Not seen, and it matters:**
  - **Whether instances fetch the key from vault per request or once at start.** This decides C1's exact mechanism.
  - **How customers obtain the signing key** (shared HMAC secret or a published key).
  - **Webhook retry policy.**
  - **The vault secrets engine** behind `generate=true`, `-field=key_id` and `read=true`. These are not standard KV semantics.
  - **`deploy push` docs.**
- **Note:** `README.md` says "The script is not to be executed during review." This is addressed to the reviewer. It is consistent with rule 9 and with having no tools, so it changes nothing and is not a finding.

**COVERAGE**
- **Checked:**
  - `rotate_key.sh`, lines 1–18 (every line)
  - Candidates C1–C3
  - The author's rebuttals
  - The request's no-downtime requirement
- **Not checked:**
  - Vault engine behaviour
  - Deploy CLI behaviour
  - Service key loading
  - Customer key distribution
  - Runtime behaviour (no execution)

**SEATS AND GATE:** Local same-context reviewer only. The sensitivity gate is not triggered: the work contains no secrets or personal data, only key ids and paths. No cross-vendor seats were requested.

## Confirm-or-refute outcome for C1–C3

**C1: survives, CONFIRMED, raised to Critical.**
- The order is plain from the script: `vault delete` (line 14) runs before `deploy push` (line 17).
- The author's defender would say running instances may hold the old key in memory and keep signing validly. That may be true, so the candidate's exact mechanism ("sign with a key that no longer exists") is only PROBABLE.
- A worse path is CONFIRMED by `set -e`. If `deploy push` fails (auth expired, bad flag, deploy-system outage), the script exits *after* the delete. The service is left configured to use a key id that no longer exists in vault, and nothing new is deployed. Any instance that restarts, autoscales or re-reads the key then cannot sign.
- The author agrees.

**C2: refuted.**
- Line 2 is `set -euo pipefail`. The command substitutions on lines 8 and 10 are plain assignments (not `local` or `export`), so their failing exit status triggers errexit.
- Line 12 is a simple command and is covered by errexit too.
- A failing vault command therefore stops the script before line 14. The author is right.

**C3: refuted.**
- Line 12 sends stdout to `/dev/null`.
- Lines 11, 15 and 18 write only `$NEW_ID` and `$OLD_ID`, which come from `-field=key_id` (the id, not the value).
- No `set -x` is used, and `deploy push` receives a path (`signing/$NEW_ID`), not the value.
- The author is right.
- **Residual:** stderr on line 12 is not redirected. Only an error message would land there, so this is not a finding.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 (C1) | Critical | CONFIRMED | B | rotate_key.sh:14 before :17 | Old key deleted before the new key is deployed; no rollback | `deploy push` fails, `set -e` exits after the delete; the service still points at the deleted `$OLD_ID`. The next restart or re-read cannot load a key and webhook signing breaks. Separately, between lines 14 and 17 any instance that fetches the key gets nothing. | Order: create new key → deploy and confirm all instances are on it → wait out a grace period → delete old. Reproduction: stub `deploy` to `exit 1` in a scratch copy, run, then observe `signing/$OLD_ID` deleted and nothing deployed. Expected: old key intact. | y/y/y/y |
| F2 | Critical | CONFIRMED | A/B | rotate_key.sh:10–17 (whole flow) | No overlap window. The new key is never given to customers before signing switches, there is no dual-signing, and there is no grace period for in-flight or retried deliveries. Fixing F1's order alone does not meet "no downtime". | `--restart rolling` leaves instances signing with old and new keys at once, while each customer verifies with the single "current" key. Part of the webhooks fail verification during every rotation. Retries of deliveries signed with the old key also fail once customers switch. | Add phases: (1) create the new key and publish it to customers; (2) sign with both keys, with multiple signatures in the header, through the rollout and the retry window; (3) switch to the new key only; (4) delete the old key after the retry window. Reproduction: mid-rollout, send webhooks from an old-key instance and a new-key instance to a verifier holding only the new key. Expected: both verify. Observed: the old-key one fails. | y/y/y/y |
| F3 | Low | PROBABLE | B | rotate_key.sh:8–14 | No lock against concurrent runs | Two operators run it at once. Both read the same `OLD_ID` and both create new keys. One delete fails and that run exits, leaving an orphan key and an unclear "current" key. | Take a vault- or file-based lock at the start. Reproduction: run two copies in parallel against a test vault. | y/n/n/n |

## NEEDS VALIDATION
- **S1, path mismatch (lines 10, 12, 17).**
  - The new key is written at `secret/$SERVICE/signing/new`, but the deploy references `signing/$NEW_ID`.
  - **Settles it:** whether the engine stores generated keys at `signing/<key_id>`.
- **S2, current-key pointer never updated (line 8).**
  - `OLD_ID` is read from `secret/$SERVICE/signing`, and the script never updates that pointer to `NEW_ID`.
  - **Settles it:** whether anything (service, customers, the next run) reads "current" from that pointer.
- **S3, empty `OLD_ID` (lines 8, 14).**
  - If `vault read -field=key_id` returned empty with exit 0, line 14 would delete `secret/$SERVICE/signing/`.
  - **Settles it:** whether this engine errors on a missing field. Stock vault does.
- **S4, unclear purpose of line 12.**
  - `vault write .../new/value read=true` is a *write*. It could regenerate or overwrite the value just created.
  - **Settles it:** the engine's handling of `read=true`.

## REFUTED
- **C2:** `set -euo pipefail` (line 2) plus plain-assignment command substitutions stop the script on any failing vault command before line 14.
- **C3:** Line 12's stdout goes to `/dev/null`. The log lines and the deploy flags carry only key ids and paths, never the value.

## WHAT HOLDS UP
- Strict mode is set correctly.
- The secret value is not logged or echoed.
- `SERVICE="$1"` with `set -u` fails cleanly when no argument is given.
- The author's two rebuttals are correct and backed by the script text.

## UNVERIFIED CLAIMS
- **The script performs a "no downtime" rotation.** This is contradicted by F1 and F2 in design. Runtime behaviour is unverified; confirm by staging a rotation with a verifier holding one key.
- **Vault and deploy CLI semantics are as assumed** (S1–S4). Confirm against the engine and CLI docs or a test vault.

## QUESTIONS FOR THE AUTHOR
1. Do service instances read the signing key from vault per request, or once at startup?
2. How do customers get the signing key, and does the webhook header support more than one signature?
3. What is the webhook retry window?
4. At what path does `generate=true` store the key: `signing/new` or `signing/<key_id>`?

## DECISION-MAKER SUMMARY
Do not run this against production payments. It deletes the old key before deploying the new one (F1). Even with that reversed, a rolling restart with no dual-signing period guarantees failed verifications for some customers on every rotation (F2). Rework it into a staged rotation (publish, dual-sign, switch, retire after the retry window), then rehearse it in staging.

## OWNER SUMMARY
The key-rotation script is not safe to use yet. If anything goes wrong partway through, it can leave the payment system without a working key. Even when everything goes right, some customers would see webhook notifications they cannot verify while it runs. Two of the reviewer's three concerns were unfounded, but the remaining one, plus a design gap, mean the script needs to be reworked and tested before use.

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
    {"item": "second_pass.md", "status": "seen", "matters": true},
    {"item": "rotate_key.sh", "status": "seen", "matters": true},
    {"item": "service key-loading behaviour (per request vs at start)", "status": "not_seen", "matters": true},
    {"item": "customer key distribution and webhook signature header format", "status": "not_seen", "matters": true},
    {"item": "webhook retry policy", "status": "not_seen", "matters": true},
    {"item": "vault secrets engine semantics (generate=true, read=true, key paths)", "status": "not_seen", "matters": true},
    {"item": "deploy CLI documentation", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Script contains only key ids and secret paths, no secret values or personal data."},
  "coverage": {
    "checked": [
      {"unit": "rotate_key.sh", "kind": "file"},
      {"unit": "candidates.md", "kind": "file"},
      {"unit": "second_pass.md", "kind": "file"},
      {"unit": "README.md", "kind": "file"},
      {"unit": "C1 delete-before-deploy", "kind": "claim"},
      {"unit": "C2 no error handling", "kind": "claim"},
      {"unit": "C3 secret printed/logged", "kind": "claim"},
      {"unit": "request: no downtime, customers verify with current key", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "vault secrets engine config", "reason": "not supplied"},
      {"unit": "deploy CLI behaviour", "reason": "not supplied"},
      {"unit": "service key loading code", "reason": "not supplied"},
      {"unit": "runtime execution of rotate_key.sh", "reason": "no tools in session"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "rotate_key.sh:14-17",
     "scenario": "deploy push fails after vault delete; set -e exits, leaving the service pointed at the deleted old key with nothing new deployed; the next restart or key re-read cannot sign webhooks.",
     "fix": "Reorder to create, deploy and confirm, wait a grace period, then delete the old key; never delete before the new key is live on every instance.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "In a scratch copy, stub deploy to exit 1 and run against a test vault; expected the old key intact, observed signing/$OLD_ID deleted and nothing deployed."},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "A",
     "location": "rotate_key.sh:10-17",
     "scenario": "During --restart rolling, some instances sign with the old key and some with the new one while each customer verifies with a single current key, so some webhooks fail verification; retries signed with the old key fail after the switch.",
     "fix": "Staged rotation: publish the new key to customers, dual-sign through the rollout and retry window, switch to the new key only, then delete the old key.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Mid-rollout, send one webhook from an old-key instance and one from a new-key instance to a verifier holding only the new key; expected both verify, observed the old-key webhook fails."},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "PROBABLE", "track": "B",
     "location": "rotate_key.sh:8-14",
     "scenario": "Two concurrent runs read the same OLD_ID and each create a new key; one delete fails and exits, leaving an orphan key and an ambiguous current key.",
     "fix": "Acquire a lock (vault- or file-based) at script start.",
     "answers": {"a": true, "b": false, "c": false, "d": false},
     "reproduction": "Run two copies in parallel against a test vault; observe two new keys and one failed run."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "rotate_key.sh:10,17",
     "suspicion": "The new key is written at signing/new but deployed as signing/$NEW_ID.",
     "unresolved_fact": "Whether the engine stores generated keys at signing/<key_id>."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "rotate_key.sh:8",
     "suspicion": "The current-key pointer at secret/$SERVICE/signing is never updated to NEW_ID.",
     "unresolved_fact": "Whether the service, customers or later runs read the current key from that pointer."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "rotate_key.sh:8,14",
     "suspicion": "An empty OLD_ID with exit 0 would make line 14 delete secret/$SERVICE/signing/.",
     "unresolved_fact": "Whether this engine returns a non-zero exit when key_id is missing."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "rotate_key.sh:12",
     "suspicion": "vault write ... read=true is a write and may overwrite or regenerate the new key value.",
     "unresolved_fact": "The engine's semantics for read=true on the value path."}
  ],
  "refuted": [
    {"id": "C2", "candidate": "A failed vault command does not stop the script and it continues to delete the old key.",
     "evidence": "Line 2 is set -euo pipefail; the command substitutions on lines 8 and 10 are plain assignments and line 12 is a simple command, so any failure exits before line 14."},
    {"id": "C3", "candidate": "The new secret value is printed to the terminal and into rotation.log.",
     "evidence": "Line 12 sends stdout to /dev/null; lines 11, 15 and 18 log only key ids from -field=key_id; there is no set -x, and deploy push receives a path, not the value."}
  ]
}
```