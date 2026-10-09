# Redteam report: evaluation of Keyhole

**Review mode:** I reviewed this myself with no tools and no subagent seat. I did not write the work. Nothing was run, opened or fetched. Everything below comes from the supplied text.

**VERDICT: REWORK.** The evaluation assesses a different product (SecretSweep), not the one the request asked about (Keyhole). It never uses the Keyhole documentation it was given, so it does not answer the question.

**CONFIDENCE: high** on the verdict, because the drift can be read directly from the text. **Medium** on the secondary findings, because I had no tools and did not see the repositories, the planted secrets, the scan output, or the full Keyhole or SecretSweep terms.

## Inputs ledger

**Seen:**
- `request.md` (original request)
- `context.md`
- `evaluation.md`
- `evidence/keyhole_docs.md` (marked as an extract)

**Not seen, and whether it matters:**

| Item | Matters? | Why |
|---|---|---|
| Full Keyhole pricing and terms | Yes | Needed for how "committer" is counted and for minimums. |
| SecretSweep licence | Yes | Needed for the "$0 for open-source use" condition. |
| The 5 test repositories and the 10 planted secrets | Yes | Needed for the detection claim. |
| Raw scan output and timing | Yes | Needed for "9 of 10" and "40 seconds". |
| Whether our repositories are open source or proprietary | Yes | Needed for the SecretSweep cost claim. |

## Coverage

**Checked:**
- `evaluation.md`: Recommendation, Method, Cost and effort, Risks
- `evidence/keyhole_docs.md`: all of it
- The original request against the work
- The budget arithmetic

**Not checked:**
- Any repository, scan, or licence text
- Keyhole's behaviour in practice

## Seats and gate

- **Sensitivity gate:** passed. The material has no personal data, credentials, or confidential records. The planted secrets are described as fake.
- **Seats:** only this single local reviewer ran. No subagent or cross-vendor seat was available in this session; none was refused.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | D | `evaluation.md` title and Recommendation: "Evaluation: SecretSweep … adopt SecretSweep" vs. `request.md`: "whether we should adopt Keyhole … Our shortlist is Keyhole only" | Drift. The request was a decision about Keyhole. The work evaluates and recommends SecretSweep and never mentions Keyhole. The supplied `keyhole_docs.md` is not used. | The decision-maker reads "Recommendation: adopt" next to a Keyhole request and approves Keyhole spend with no Keyhole evidence. Or they adopt an unshortlisted tool that finance did not approve and nobody scoped. Either way, the actual question stays unanswered. | Redo the evaluation for Keyhole: run the same planted-secret test against Keyhole, cost it for 30 committers, and assess its live-credential verification and pre-receive hooks. If SecretSweep is worth proposing, present it as an explicit cheaper alternative alongside the Keyhole result, not in place of it. **Reproduction:** search `evaluation.md` for "Keyhole" and get 0 hits. Positive control: the same search on `request.md` gets 1 hit. | a Y / b Y / c Y / d Y |
| F2 | Medium | CONFIRMED | D | Recommendation: "costs $0 for open-source use"; Cost: "No licence cost." | A conditional claim ("for open-source use") becomes unconditional ("No licence cost") two sections later. Nothing establishes that our repositories qualify. | If our repositories are proprietary, the real cost is unknown. Using an open-source-only licence commercially is a compliance exposure. | State whether our repositories are open source and quote the licence clause that covers our use. Price the commercial tier if one applies. | a Y / b Y / c N (unknown) / d N (unknown) |
| F3 | Medium | CONFIRMED | D | Method: "planted 10 fake secrets … default rules … 9 of 10"; the base64 miss is not listed under Risks | The method cannot support a recall claim. There are only 10 samples, the secret types are unknown, and the test secrets were planted by the evaluator. The one known blind spot (base64-encoded values) is dropped from Risks. False positives are named as a risk but never measured. | A team relies on "9 of 10" as coverage. Real credentials in encoded config, a common pattern in Kubernetes secrets and env files, pass undetected. | Use a larger, typed corpus: provider keys, private keys, tokens, plus encoded, split and historical-commit variants. Report misses by type. Measure false positives on the real repositories. Carry the base64 miss into Risks. Apply the same corpus to Keyhole. | a Y / b Y / c N / d Y |
| F4 | Medium | CONFIRMED | D | Whole document; no Need or Adoption section | Track D basics are missing. There is no statement of need: what incident, which repositories, push-time blocking or after-the-fact detection. There is no plan for how 30 committers would handle blocked pushes or allowlist upkeep. There is no signal for abandonment. The allowlist is offered as a fix without saying who maintains it. | The tool is installed. Allowlist upkeep falls on nobody. Findings pile up, alerts get muted within weeks, and the tool is effectively abandoned while appearing "adopted". | Add a need statement, an owner for triage and allowlist maintenance, the committer workflow on a block, and a 30-day adoption check (open findings triaged, alerts not muted). | a Y / b Y / c N / d Y |
| F5 | Low | CONFIRMED | D | "ran in 40 seconds on the largest repository" | There is no repository size, history depth, or runner spec, and no baseline. The figure cannot be compared to anything, including Keyhole. | Low. A misleading speed comparison is possible later. | Record repository size and commit count, whether full history was scanned, and the runner. Time Keyhole under the same conditions. | a N / b Y / c N / d N |

## Needs validation

- **S1, budget headroom.** 30 committers × $12 = **$360/month ($4,320/year)**. That sits exactly at the pre-approved ceiling with zero headroom. Unresolved fact: how Keyhole counts a "committer" (active in the period, or any contributor ever), and whether the count is expected to exceed 30. Either could push the cost over the approval.
- **S2, licence condition.** Whether our repositories are open source. This decides whether SecretSweep's "$0" applies at all (see F2).
- **S3, install estimate.** "Install in CI takes about an hour" is unsupported. Unresolved fact: whether it was actually installed in our CI, and with what result.

## Refuted

None.

## What holds up

- The planted-secret approach is a reasonable *shape* of test. Reusing it, at larger scale, against Keyhole is the fastest path to a real answer.
- The author reported the miss (base64) instead of hiding it.
- The Keyhole price fits the finance approval at today's committer count.

## Unverified claims

| Claim | How to confirm |
|---|---|
| 9 of 10 detections | Supply the corpus and the raw scan output. |
| 40 seconds | Supply the timing log and repository stats. |
| $0 / no licence cost | Quote the licence clause and confirm our repositories' status. |
| About one hour to install | Point to the CI change, as a PR or commit. |
| Keyhole "verifies live credentials" and "supports pre-receive hooks" | These are vendor assertions. Confirm in a Keyhole trial. |

## Questions for the author

1. Why was SecretSweep evaluated when the shortlist was Keyhole only? Was the scope deliberately changed, and by whom?
2. Are our repositories open source?
3. Do we need push-time blocking (pre-receive hooks), or is detection after the fact in CI enough?

## Decision-maker summary

Do not decide on Keyhole from this document. It evaluates a different, unshortlisted tool. Ask for the same test run against Keyhole, costed against the $360/month ceiling. Proceeding now means either buying Keyhole on no evidence or adopting an unapproved tool whose free licence may not apply to us.

## Owner summary

The write-up we received reviews a different secret-scanning product from the one we asked about, so it cannot tell us whether to buy Keyhole. The price Keyhole quotes fits the approved budget for our current team size, but nothing has been tested. The evaluation should be repeated for Keyhole, ideally with a larger test.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "evaluation.md", "status": "seen", "matters": true},
    {"item": "evidence/keyhole_docs.md (extract)", "status": "seen", "matters": true},
    {"item": "Full Keyhole pricing and terms (committer definition)", "status": "not_seen", "matters": true},
    {"item": "SecretSweep licence text", "status": "not_seen", "matters": true},
    {"item": "Test repositories, planted secrets, raw scan output", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "local-self-review", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "No personal data, credentials or confidential records; planted secrets described as fake."},
  "coverage": {
    "checked": [
      {"unit": "evaluation.md", "kind": "file"},
      {"unit": "evaluation.md#Recommendation", "kind": "section"},
      {"unit": "evaluation.md#Method", "kind": "section"},
      {"unit": "evaluation.md#Cost and effort", "kind": "section"},
      {"unit": "evaluation.md#Risks", "kind": "section"},
      {"unit": "evidence/keyhole_docs.md", "kind": "file"},
      {"unit": "30 x $12 = $360/month within pre-approval", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "Test repositories and scan output", "reason": "not supplied; no tools"},
      {"unit": "SecretSweep licence", "reason": "not supplied; no tools"},
      {"unit": "Keyhole behaviour in practice", "reason": "no trial run; no tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "D",
     "location": "evaluation.md: title and Recommendation vs request.md",
     "scenario": "The request asks whether to adopt Keyhole (shortlist: Keyhole only); the work evaluates and recommends SecretSweep and never mentions Keyhole, so a reader approves or rejects Keyhole with no Keyhole evidence, or adopts an unapproved tool.",
     "fix": "Redo the evaluation for Keyhole (same planted-secret test, 30-committer cost, live verification and pre-receive hooks); present SecretSweep only as an explicit alternative alongside it.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Search evaluation.md for 'Keyhole': 0 hits; same search on request.md: 1 hit (positive control)."},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "D",
     "location": "evaluation.md: Recommendation '$0 for open-source use'; Cost 'No licence cost.'",
     "scenario": "If our repositories are proprietary, the open-source-only $0 licence does not apply, cost is understated and commercial use may breach the licence.",
     "fix": "Confirm repository licensing status and quote the licence clause covering our use; price any commercial tier.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "D",
     "location": "evaluation.md: Method; Risks",
     "scenario": "Ten self-planted secrets with default rules cannot establish recall; the known base64 miss is dropped from Risks, so real encoded credentials in config pass undetected; false positives are never measured.",
     "fix": "Use a larger typed corpus with encoded and historical variants, report misses by type, measure false positives on real repositories, list the base64 gap under Risks, and apply the same test to Keyhole.",
     "answers": {"a": true, "b": true, "c": false, "d": true}},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "D",
     "location": "evaluation.md: whole document (no need or adoption section)",
     "scenario": "No need statement, owner, committer workflow or abandonment signal; allowlist upkeep falls on nobody, alerts get muted, and the tool is adopted in name only.",
     "fix": "Add the need, a triage and allowlist owner, the blocked-push workflow and a 30-day adoption check.",
     "answers": {"a": true, "b": true, "c": false, "d": true}},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "D",
     "location": "evaluation.md: Recommendation '40 seconds on the largest repository'",
     "scenario": "No repository size, history depth or runner spec is given, so the timing cannot be compared with Keyhole or anything else.",
     "fix": "Record repository size, commit count, full-history flag and runner; time Keyhole under the same conditions.",
     "answers": {"a": false, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "D", "location": "evidence/keyhole_docs.md: '$12 per committer per month'",
     "suspicion": "30 x $12 = $360/month sits exactly at the pre-approved ceiling with no headroom.",
     "unresolved_fact": "How Keyhole counts a committer, and the expected committer count over the contract term."},
    {"id": "S2", "status": "needs_validation", "track": "D", "location": "evaluation.md: Recommendation",
     "suspicion": "SecretSweep's $0 licence may not apply to our use.",
     "unresolved_fact": "Whether our repositories are open source."},
    {"id": "S3", "status": "needs_validation", "track": "D", "location": "evaluation.md: Cost and effort",
     "suspicion": "'About an hour' to install in CI is unsupported.",
     "unresolved_fact": "Whether it was actually installed in our CI, with a PR or commit to show it."}
  ],
  "refuted": []
}
```