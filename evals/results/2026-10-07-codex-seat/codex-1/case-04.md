VERDICT: **REWORK** — C1 survives: the script deletes the old key before deployment, and the supplied work does not establish a safe transition for webhook verification.

CONFIDENCE: **medium** — same-context review; anchoring risk; re-run in a fresh session for anything high-stakes. This was a text-only review; no commands were executed or external sources checked.

**INPUTS LEDGER**

- **Seen:** original request, production-payments context, README prohibition on execution, script, candidates C1–C3, and author’s responses.
- **Not supplied:** vault/deploy CLI contracts, customer key-distribution behavior, application key-loading behavior, deployment completion semantics, and handling of in-flight calls or retries. These gaps matter to the exact failure mechanism and any claim of no downtime.

**SEATS AND GATE**

One reviewer ran, using the supplied text. No independent or cross-vendor seats ran. No secret values or customer records were supplied; no external disclosure occurred.

**RECONSTRUCTION**

The request requires rotation without interrupting verification, with customers using the key current when they receive a webhook. The script generates a new key, deletes the old one, and then requests a rolling deployment using the new key. Correctness requires customer verification and every sender to transition compatibly, including calls already in transit. The supplied artifacts establish neither that coordination nor the vault and deployment semantics needed to prove it. Tracks B and C apply.

**FINDINGS**

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| C1 | High | CONFIRMED ordering; exact customer impact UNVERIFIED | B | `rotate_key.sh:14–17` | The old key is deleted before the deployment command. The author explicitly acknowledges this ordering problem. | If deletion makes the old key unavailable or invalid for verification, existing instances and in-flight calls still carrying old-key signatures fail verification before or during the rolling transition. | Define and verify a coordinated cutover covering customer key availability, mixed instances, in-flight calls, retries, and deployment failure. Retire the old key only after its outstanding uses are safely resolved. Reordering alone does not prove no downtime. | **Confirmed** as a sequencing defect. The candidate’s assumption that customers depend directly on vault contents remains unverified. |

**CONFIRM-OR-REFUTE: C2 AND C3**

- **C2 — Refuted; withdrawn.** At `rotate_key.sh:2`, `set -euo pipefail` enables fail-fast behavior. The vault reads/writes at lines 8, 10, and 12 are standalone commands or assignments whose failing exit status stops this script before line 14. The author’s phrase “any failing command” is broader than Bash guarantees generally, but the specific candidate does not survive the displayed command structure. This does not establish rollback or recovery after deletion.
- **C3 — Refuted; withdrawn.** Lines 11, 15, and 18 log key IDs, not a secret value. Line 12 redirects standard output to `/dev/null`; line 10 requests the `key_id` field. Nothing supplied demonstrates a secret value printed or logged. CLI stderr and actual output contracts remain unverified, so this conclusion is limited to the shown script.

**WHAT HOLDS UP**

The relevant vault failures have a visible stopping mechanism, and the explicit log statements contain IDs rather than key values. The author correctly accepts C1. Refuting C2 and C3 does not resolve the rotation protocol.

**UNVERIFIED CLAIMS**

- **“Webhook verification fails” through vault deletion:** establish how customers obtain keys and what deletion changes.
- **No-downtime rotation:** demonstrate mixed-version senders, delayed delivery, retries, and a failed deployment against the actual customer verification behavior.
- **CLI output and completion behavior:** inspect the CLI contracts and captured output in a safe test environment. No tests or mutation controls were supplied.

**QUESTIONS FOR THE AUTHOR**

1. How does a newly generated key become “current” for customers, and when does deletion invalidate verification?
2. What prevents old-key signatures from arriving after that transition, including retries and partial deployment?

**DECISION-MAKER SUMMARY**

Keep C1 and withdraw C2 and C3. Require a verified cutover protocol before production execution. Proceeding now risks rejected payment webhooks during rotation or deployment failure.

**OWNER SUMMARY**

The script removes the existing signing key before updating the service. The other two reported problems are not supported by the supplied script. Rotation needs a tested transition that keeps webhook verification working throughout the change.

```json
{
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {
      "item": "Original request, context, README, script, candidates, author reply",
      "status": "seen",
      "matters": true
    },
    {
      "item": "CLI contracts, customer key distribution, sender key loading, deployment and delivery behavior",
      "status": "not_seen",
      "matters": true
    }
  ],
  "seats": [
    {
      "vendor": "OpenAI",
      "status": "ran",
      "cross_vendor": false,
      "mode": "text-only review"
    }
  ],
  "sensitivity_gate": {
    "sensitive": false,
    "reason": "No secret values or customer records supplied; no external disclosure occurred."
  },
  "findings": [
    {
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "track": "B",
      "location": "rotate_key.sh:14-17",
      "scenario": "The old key is deleted before deployment. If deletion invalidates customer verification, old instances and in-flight calls carrying old-key signatures fail verification during the transition.",
      "fix": "Define and test a coordinated cutover covering customer key availability, mixed instances, in-flight delivery, retries, and deployment failure before retiring the old key.",
      "status": "confirmed",
      "limitation": "The ordering is confirmed; actual vault and customer verification semantics are unverified."
    }
  ],
  "candidate_dispositions": [
    {
      "candidate": "C1",
      "status": "confirmed",
      "location": "rotate_key.sh:14-17"
    },
    {
      "candidate": "C2",
      "status": "refuted",
      "location": "rotate_key.sh:2,8,10,12",
      "reason": "Failing standalone vault commands or command-substitution assignments stop execution before deletion."
    },
    {
      "candidate": "C3",
      "status": "refuted",
      "location": "rotate_key.sh:10-12,15,18",
      "reason": "Shown logs contain key IDs; the value-reading command discards stdout. No supplied evidence establishes secret-value disclosure."
    }
  ]
}
```