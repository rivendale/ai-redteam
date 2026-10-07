# Redteam review: "Evaluation: SecretSweep for our repositories"

> Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes. No tools were available, so nothing was run, opened or fetched.

**VERDICT: REWORK.** The evaluation answers a different question from the one asked. The request was whether to adopt Keyhole; the work evaluates and recommends SecretSweep, a tool not on the shortlist, and never assesses Keyhole.

**CONFIDENCE: high** on the drift finding, which is tied to exact quotes. **Medium** on the rest, because:
- this is a same-context review with no independent seat;
- no tools were available, so the SecretSweep test results and licence terms could not be checked;
- the Keyhole documentation is a short extract.

**INPUTS LEDGER**

| Item | Status | Matters? |
|---|---|---|
| `request.md` (original request) | seen | yes. It is the yardstick. |
| `context.md` | seen | yes |
| `evaluation.md` (work under review) | seen | yes |
| `evidence/keyhole_docs.md` | seen (extract only) | yes. It is the only Keyhole evidence. It covers price, live verification and pre-receive hooks. Detection rate, false positives, data handling and contract terms are absent. |
| The five test repositories, the 10 planted secrets, SecretSweep run logs | not seen | yes. The 9/10 and 40 s figures are unverifiable without them. |
| SecretSweep licence text ("$0 for open-source use") | not seen | yes. Whether our repositories count as open-source use decides the cost claim. |
| Full Keyhole docs: verification data flow, retention, SLA | not seen | yes, for any Keyhole decision |

**SEATS AND GATE**
- No subagent or cross-vendor seats were available in this session. One local reviewer ran.
- Sensitivity gate: no personal, financial, credential or confidential material was found. Planted secrets are described as fake. The gate passed, but no external seats ran anyway.
- No embedded instructions addressed to the reviewer were found.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | D (Fit), A | `evaluation.md` title and **Recommendation** line; vs `request.md` "Evaluate whether we should adopt Keyhole… Our shortlist is Keyhole only" | The work evaluates and recommends SecretSweep. Keyhole is never named, tested or assessed. This is total drift from the request. | A decision-maker reads "adopt SecretSweep" as the outcome of the Keyhole evaluation. Either a non-shortlisted tool is adopted with no procurement review, or the Keyhole question stays unanswered while it looks settled. | Redo the evaluation on Keyhole. If the author believes SecretSweep is better, present it as an explicit challenge to the shortlist, with a head-to-head comparison against Keyhole. | confirmed. Strongest defence: "the author found a free alternative, which is useful." That justifies a side note, not replacing the asked question. |
| 2 | High | CONFIRMED | D (Fit), A (Missing info) | `evidence/keyhole_docs.md` vs `evaluation.md` (no reference to it) | The supplied Keyhole evidence is ignored: live-credential verification, pre-receive hooks, $12/committer/month. The work never weighs these differentiators. Pre-receive blocking stops a secret before it lands; a CI scan only flags it after push. | Without the comparison, the team may pick a CI-only scanner. A committed secret then reaches the remote and history before detection, which forces rotation and a history rewrite that pre-receive would have avoided. | Assess each Keyhole capability against our needs. In the planted-secret test, measure whether pushes containing secrets are blocked. | confirmed |
| 3 | High | PROBABLE | D (Cheaper alternative / Cost), C | `evaluation.md` "costs $0 for open-source use"; "No licence cost" | "Open-source use" is a licence condition. Nothing shows our repositories qualify. "No licence cost" restates the condition as fact. | Our repositories are private or commercial, so the free tier does not apply. The cost case then reverses after adoption, or the team is in licence breach. | Quote the SecretSweep licence clause and state whether our repositories qualify. Get the commercial price if not. | confirmed as a gap. The licence was not seen, so this is PROBABLE, not CONFIRMED. |
| 4 | Medium | CONFIRMED (method as described) | A (Logic), B (Tests) | `evaluation.md` **Method** | The test has several weaknesses: 10 author-planted secrets is a tiny sample; there is no false-positive rate; only default rules were used; and git history scanning is not mentioned. It also shows a known blind spot (base64-encoded value) without assessing how common that pattern is in our configs. | Production secrets in encoded or unusual formats are missed. A high false-positive rate leads developers to ignore or bypass alerts within weeks. | Run the same planted set (plus encoded variants) through Keyhole and any challenger. Measure the false-positive count on a real repository with history. | n/a |
| 5 | Medium | PROBABLE | D (Burden, Adoption) | `evaluation.md` **Risks** "fixable with an allowlist" | The work dismisses false positives without measuring them, and does not say who maintains the allowlist or how. | The allowlist grows unmaintained, or broad allowlist entries hide real secrets in fixtures. | Measure the false-positive count. Name an allowlist owner and a review process. | n/a |
| 6 | Low | CONFIRMED (arithmetic) | C (Numbers) | `request.md` budget; `keyhole_docs.md` price; `context.md` 30 committers | Keyhole at $12 × 30 = $360/month ($4,320/year) is exactly at the pre-approved cap, with no headroom. The work does not mention this. | Committer growth, or price changes at renewal, push the cost over the approval and need a new finance sign-off. | Note the zero headroom in the Keyhole evaluation. Ask the vendor about volume pricing or price locks. | n/a |

**Pass 3 check**
- The verdict is consistent with the findings: an open Critical rules out SHIP and SHIP WITH FIXES.
- I chose REWORK over REJECT because the method (planted-secret test, timing, CI install estimate) can be reused for Keyhole.
- What is most likely still missed: Keyhole's live-credential verification sends found credentials to issuing services. That data flow, along with what Keyhole itself stores, needs the privacy checklist applied to the full vendor docs. Neither the work nor the extract addresses it.

## WHAT HOLDS UP
- Planting known secrets and counting detections is a sound basic method.
- Reporting the miss (the base64-encoded value) honestly is good practice.
- The CI install time and runtime are the right kinds of operational evidence, though they are unverified.

## UNVERIFIED CLAIMS
- **"9 of 10"**: settle it with the planted-secret list and the SecretSweep run output.
- **"40 seconds on the largest repository"**: settle it with the run log and the repository size, including whether history was scanned.
- **"$0 for open-source use" / "No licence cost"**: settle it with the licence clause and our repositories' status.
- **"Install in CI takes about an hour"**: settle it with an actual install record.
- **Keyhole's "verifies live credentials"** (vendor claim): settle it with full docs or a trial, including what is sent where.

## QUESTIONS FOR THE AUTHOR
1. Why was Keyhole, the only shortlisted tool, not evaluated? Was the shortlist changed, and by whom?
2. Do our repositories qualify as "open-source use" under SecretSweep's licence?
3. Do we need push-time blocking (pre-receive), or is post-push CI detection acceptable for us?

## DECISION-MAKER SUMMARY
This document does not answer the question asked: it recommends SecretSweep and never evaluates Keyhole, so do not treat it as a Keyhole decision. Have the same test run on Keyhole, and include SecretSweep only as an explicit head-to-head challenger if its licence actually covers our repositories. Proceeding now risks adopting an off-shortlist tool on an unverified "free" claim, while the approved option sits exactly at budget and remains unassessed.

```json
{
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "evaluation.md", "status": "seen", "matters": true},
    {"item": "evidence/keyhole_docs.md", "status": "seen_extract_only", "matters": true},
    {"item": "test repositories, planted secrets, SecretSweep run logs", "status": "not_seen", "matters": true},
    {"item": "SecretSweep licence text", "status": "not_seen", "matters": true},
    {"item": "full Keyhole docs (verification data flow, retention)", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "local-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "no personal, financial, credential or confidential material; planted secrets are fake"},
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "D", "location": "evaluation.md title and Recommendation line vs request.md",
      "scenario": "Work evaluates and recommends SecretSweep while the request and shortlist are Keyhole only; a non-shortlisted tool is adopted or the Keyhole question is left unanswered while appearing settled.",
      "fix": "Redo the evaluation on Keyhole; present SecretSweep only as an explicit head-to-head challenge to the shortlist.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "D", "location": "evidence/keyhole_docs.md (unreferenced by evaluation.md)",
      "scenario": "Keyhole's live verification and pre-receive blocking are never weighed; a CI-only scanner lets secrets reach the remote and history before detection.",
      "fix": "Assess each Keyhole capability against needs; test whether pushes with secrets are blocked.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "PROBABLE", "track": "D", "location": "evaluation.md 'costs $0 for open-source use' / 'No licence cost'",
      "scenario": "Our repositories are not open-source use, so the free tier does not apply; the cost case reverses or the team is in licence breach.",
      "fix": "Quote the licence clause and confirm eligibility; obtain the commercial price otherwise.", "status": "confirmed"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "A", "location": "evaluation.md Method",
      "scenario": "10 author-planted secrets, default rules, no false-positive rate, no history scan; encoded or unusual secrets are missed in production and alert fatigue sets in.",
      "fix": "Run the same planted set plus encoded variants through Keyhole and any challenger; measure false positives on a real repository with history.", "status": "n/a"},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "D", "location": "evaluation.md Risks 'fixable with an allowlist'",
      "scenario": "The allowlist grows unowned or overly broad, hiding real secrets in fixtures.",
      "fix": "Measure the false-positive count; name an allowlist owner and a review process.", "status": "n/a"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "C", "location": "request.md budget; keyhole_docs.md price; context.md 30 committers",
      "scenario": "$12 x 30 = $360/month sits exactly at the approved cap; any committer growth or price change exceeds approval.",
      "fix": "Note the zero headroom; ask the vendor about volume pricing or a price lock.", "status": "n/a"}
  ]
}
```
