# Redteam review: "Evaluation: SecretSweep for our repositories"

> **Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No tools or subagent were available in this session, so I could not run anything, open links, or delegate to a fresh reviewer.

**VERDICT: REWORK.** The request was to evaluate Keyhole, the only tool on the shortlist, but the work evaluates and recommends a different tool, SecretSweep, so it does not answer the question asked.

**CONFIDENCE: high** on the main finding, which rests on exact quotes. It is lower on everything else because:
- this is a same-context review with no tools;
- the SecretSweep run outputs and Keyhole's full pricing terms were not supplied.

**INPUTS LEDGER:**

| Item | Status | Matters? |
|---|---|---|
| request.md | seen | – |
| context.md | seen | – |
| evaluation.md | seen | – |
| evidence/keyhole_docs.md (an extract) | seen | – |
| SecretSweep run logs, list of planted secrets, the five repositories | not seen | Low. The tool is off-target. |
| SecretSweep licence terms | not seen | Low. Same reason. |
| Keyhole full docs, pricing terms, definition of "committer", trial access | not seen | Yes, for the re-evaluation. |

**COVERAGE:**
- **Checked:** every section of evaluation.md (title, Recommendation, Method, Cost and effort, Risks); every claim in keyhole_docs.md; the request's two constraints (shortlist = Keyhole only; cap = $12 per committer per month); the 30-committer stake.
- **Not checked:** any actual scan results; the licence of either tool beyond the quoted text.

**SEATS AND GATE:**
- Sensitivity gate: passed. There is no personal, credential or confidential data; the secrets are described as fake and planted.
- Seats: same-context local review only. No subagent or cross-vendor seats were available, and none were requested.
- Prompt injection: no text in the work addresses the reviewer.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | D (fit) | evaluation.md title "Evaluation: SecretSweep…"; Recommendation "adopt SecretSweep" | The work evaluates a different tool than the request names. The request says to "Evaluate whether we should adopt Keyhole… Our shortlist is Keyhole only". The supplied Keyhole evidence is never cited. | A decision-maker reads "adopt" and either adopts an unevaluated, off-shortlist tool, or approves Keyhole spend on evidence about SecretSweep. Either way, the Keyhole question is never answered. | Redo the evaluation on Keyhole. Run the same planted-secret method on the same five repositories. Assess its stated differentiators: live-credential verification and pre-receive hooks. Cost it against the cap. If the author believes SecretSweep is better, present it as an explicit alternative and do not substitute it silently. Reproduction: search evaluation.md for "Keyhole"; it returns zero hits. Positive control: the same search in keyhole_docs.md returns hits. | a✓ b✓ c✓ d✓ |
| F2 | Medium | CONFIRMED | D / A | evaluation.md, Method: "planted 10 fake secrets… default rules… 9 of 10" | The method cannot support "adopt" for any tool. It uses n=10, measures no false-positive rate (the Risks section names false positives but never measures them), does not say whether git history was scanned, and makes no comparison against a baseline or alternative. | The method is reused unchanged for Keyhole and produces a similar 9/10. The team cannot tell whether the tool beats doing nothing or a free scanner, and an encoded-secret class goes undetected in production. | Expand the planted set across secret types and encodings (including base64, the known miss), plus secrets present only in history. Record false positives on unmodified repositories. Test Keyhole's live-verification claim with a revoked versus an active test credential. | a✓ b✓ c✗ d✗ |

## NEEDS VALIDATION

**S1.** Keyhole sits at exactly the budget ceiling.
- The arithmetic: $12 × 30 committers = $360/month = $4,320/year, which equals the pre-approved cap.
- The risk: no headroom at all if the vendor's "committer" count includes bots, former contributors or anyone active in a billing window, or if minimums or taxes apply.
- Settling fact: Keyhole's billing definition of "committer" and any minimum-seat or tax terms.

**S2.** "ran in 40 seconds on the largest repository" is not described in the Method section.
- Settling fact: the run log, including the repository's size and history depth.

**S3.** "$0 for open-source use" may not apply if our repositories or our use are commercial.
- Settling fact: SecretSweep's licence text. This is moot unless SecretSweep is formally added as an alternative.

## REFUTED

**C1.** "Keyhole exceeds the finance budget."
- Refuted by the vendor docs, which say "$12 per committer per month", against the request's "up to $12 per committer per month". That is within the cap, though only just (see S1).

## WHAT HOLDS UP

- The planted-secret method is a reasonable skeleton and can be reused for Keyhole once it is strengthened (F2).
- Reporting the one miss (base64) honestly is useful; it is the first test case to run against Keyhole.
- Naming false positives as a risk is correct, though they were not measured.

## UNVERIFIED CLAIMS

| Claim | How to confirm |
|---|---|
| 9 of 10 detections | Run log plus the planted-secret list |
| 40-second runtime | Timed CI log |
| About one hour to install in CI | A trial install |
| Keyhole "verifies live credentials against the issuing service" | A vendor trial with one revoked and one active test key |
| Keyhole "Supports pre-receive hooks" | A trial on our git host |

## QUESTIONS FOR THE AUTHOR

1. Was evaluating SecretSweep instead of Keyhole deliberate? If so, why was the shortlist not challenged openly?
2. Can you run the same test against a Keyhole trial?
3. How does Keyhole count billable committers?

## DECISION-MAKER SUMMARY

Do not act on this evaluation. It recommends SecretSweep, a tool not on the shortlist, and says nothing about Keyhole, the tool actually under consideration. Commission a Keyhole trial using a stronger version of the same test, and confirm the per-committer billing definition. At 30 committers the price lands exactly on the $12 cap.

## OWNER SUMMARY

This write-up reviewed the wrong product, so it cannot tell us whether to buy the scanner we were actually considering. The testing approach is a decent start and can be repeated on the right product with a few more test cases. The price fits the approved budget, but with no room to spare, so we should confirm how the vendor counts users before signing.

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
    {"item": "SecretSweep run logs and planted-secret list", "status": "not_seen", "matters": false},
    {"item": "Keyhole full pricing terms and committer definition", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "same-context-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "evaluation.md", "kind": "file"},
      {"unit": "evaluation.md#Recommendation", "kind": "section"},
      {"unit": "evaluation.md#Method", "kind": "section"},
      {"unit": "evaluation.md#Cost and effort", "kind": "section"},
      {"unit": "evaluation.md#Risks", "kind": "section"},
      {"unit": "evidence/keyhole_docs.md", "kind": "file"},
      {"unit": "Keyhole price within $12/committer/month cap", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "SecretSweep scan results", "reason": "not supplied; no tools"},
      {"unit": "Keyhole billing terms", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "D",
     "location": "evaluation.md: title and Recommendation ('adopt SecretSweep')",
     "scenario": "The request asks to evaluate Keyhole (sole shortlist item); the work evaluates and recommends SecretSweep and never mentions Keyhole, so a decision-maker either adopts an unevaluated off-shortlist tool or approves Keyhole on evidence about another product.",
     "fix": "Re-run the evaluation on Keyhole (same repos, planted secrets, live-verification and pre-receive tests, cost vs cap); present SecretSweep only as an explicit alternative.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Search evaluation.md for 'Keyhole': zero hits; the same search in keyhole_docs.md returns hits (positive control)."},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "D",
     "location": "evaluation.md#Method: '10 fake secrets ... default rules ... 9 of 10'",
     "scenario": "The method is reused for Keyhole: n=10, no false-positive measurement, no history scan and no baseline cannot distinguish tools, and the encoded-secret miss class reaches production undetected.",
     "fix": "Broaden planted secrets (types, encodings incl. base64, history-only), measure false positives on clean repos, test live verification with revoked vs active test keys.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "D", "location": "evidence/keyhole_docs.md: '$12 per committer per month'",
     "suspicion": "30 x $12 = $360/month equals the cap exactly; any broader committer count, minimums or tax exceeds it.",
     "unresolved_fact": "Keyhole's billing definition of a committer and any minimum-seat or tax terms."},
    {"id": "S2", "status": "needs_validation", "track": "C", "location": "evaluation.md#Recommendation: 'ran in 40 seconds'",
     "suspicion": "Runtime claim not supported by the Method section.",
     "unresolved_fact": "The timed run log and repository size."},
    {"id": "S3", "status": "needs_validation", "track": "C", "location": "evaluation.md: '$0 for open-source use'",
     "suspicion": "Zero-cost licence may not apply to our (possibly commercial) repositories.",
     "unresolved_fact": "SecretSweep licence text for commercial use."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Keyhole exceeds the pre-approved budget.",
     "evidence": "Vendor docs: '$12 per committer per month'; request: 'up to $12 per committer per month' - within the cap."}
  ]
}
```