# Redteam review: Lumen API vendor assessment

**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No tools or subagent were available in this session. I checked each claim against the two source files supplied inline. I could not open the live vendor pages.

**VERDICT: REJECT.** The headline conclusion ("Lumen is zero-retention, so it is safe to use with client documents") is the opposite of what its own cited source says for this account's plan. Relying on it would send client-confidential contracts to a vendor that keeps them for 30 days.

**CONFIDENCE: high** on the central finding, because it is a direct quote mismatch against the supplied source. Limits: same-context review, no tools, and the live pages, plan terms and SOC 2 report were not seen.

**INPUTS LEDGER**

| Item | Status | Matters? |
|---|---|---|
| request.md, context.md | seen | yes |
| assessment.md | seen | yes |
| sources/lumen-privacy.md (retrieved 5 Oct 2026) | seen | yes, it is the load-bearing source |
| sources/lumen-security.md (retrieved 5 Oct 2026) | seen | yes |
| Live Lumen pages as of today (7 Oct 2026) | not openable | low; the snapshots are 2 days old, but they should be re-read before any decision |
| Our Lumen account agreement / plan terms | not seen | yes; the assessment asserts "standard plan; no enterprise agreement", and that fact decides whether ZDR applies |
| SOC 2 Type II report (scope, exceptions) | not seen | moderate; "holds a report" says nothing about scope or exceptions |
| Client contracts' confidentiality / third-party-processing clauses | not seen | yes for the decision, though outside the Track C scope |

**SEATS AND GATE:** One seat ran: same-context Claude, no tools. No cross-vendor seats were used, none were requested, and the depth is standard. Sensitivity gate: the work under review contains vendor pages and an internal assessment, not client documents, so it is not sensitive in itself. The decision does concern client-confidential material.

## Pass 1: Reconstruct

The work claims Lumen is zero-retention and therefore safe for client contracts. It supports this with three further claims: SOC 2 Type II, no training on inputs, and a 200k-token context sufficient for 150 pages. It recommends, implicitly, that the contracts team proceed.

For it to be correct, these must hold:
- (a) Zero retention applies to *our* account.
- (b) The cited pages say what is claimed.
- (c) "Zero-retention plus SOC 2 plus no training" is enough for "safe" with client-confidential documents.

Track C is primary. Track A is used briefly for the "safe" inference.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | C | assessment.md, Summary: "Lumen is zero-retention, so it is safe to use with client documents [1]" vs. sources/lumen-privacy.md, Retention | Source [1] says the reverse. "Inputs and outputs sent to the Lumen API are retained for 30 days for abuse monitoring and are then deleted. Zero data retention (ZDR) is available only to accounts on an enterprise agreement that includes the signed ZDR addendum." The assessment itself states "Our account is on the standard plan; we have no enterprise agreement." ZDR therefore does not apply to us, and the citation misrepresents its source. | The team sends client contracts on the standard plan. Each one is held by Lumen for 30 days and may be accessed for abuse monitoring. This could breach client confidentiality terms, and it cannot be undone once sent (per context.md). | Withdraw the conclusion. State the actual term: 30-day retention on our plan; ZDR requires an enterprise agreement plus a signed ZDR addendum. Do not send client documents unless that addendum is executed, or unless 30-day retention is separately cleared against client obligations. | confirmed. Strongest defense: "zero-retention" might refer to training, not storage. It fails, because the source uses "retained" and "Zero data retention (ZDR)" explicitly as a storage term and separates training into its own paragraph. |
| 2 | Medium | CONFIRMED (unsourced) / PROBABLE (substance) | C | assessment.md, Supporting facts: "enough for a 150-page contract [2]" | sources/lumen-security.md states only "a context window of up to 200,000 tokens". It says nothing about pages or contracts, so the 150-page claim is the author's inference attributed to the vendor. This breaks the request's "Base every claim on Lumen's own pages". Rough arithmetic: 150 pages × ~500–700 words ≈ 75k–105k words ≈ 100k–140k tokens. That probably fits for plain text but is tight for dense, scanned or OCR'd text. It also ignores room for the prompt and extracted output if the window is shared. | A long or dense contract exceeds the window. Extraction silently truncates, or the call fails, and clauses near the end are missed. | Drop the page claim or mark it as the author's estimate. Test by tokenizing two or three real (non-client or redacted) long contracts with Lumen's tokenizer, and check whether the 200k limit includes output. | n/a (not High) |
| 3 | Medium | PROBABLE | A/C | assessment.md, Summary: "so it is safe" | Even if ZDR applied, "safe for client documents" does not follow from retention, SOC 2 and training terms alone. The assessment never mentions the 30-day abuse-monitoring access, client contract terms on third-party processors, or data residency. None of the cited pages support "safe". | Clients whose contracts restrict subprocessors or require consent are breached even under ZDR. | Replace "safe" with the specific properties verified. Add a check of client confidentiality clauses and of who at Lumen can access retained data for abuse monitoring. | n/a |
| 4 | Low | CONFIRMED | C | assessment.md: "Lumen holds a SOC 2 Type II report [2]" | The claim matches the source, but it omits the period ("ending 30 June 2026"). The report's scope and exceptions were not reviewed. | Readers treat the claim as assurance that the API and the abuse-monitoring data store are in scope, when that is unknown. | Cite the period. Obtain the report and confirm scope, exceptions and the bridge letter. | n/a |

### Pass 3 self-check
- Finding 1 is the only High or Critical. It survives the strongest defense and is confirmed.
- Most serious possible miss: the assessment's statement "Our account is on the standard plan" is unverified here. If the team actually holds an enterprise agreement with a signed ZDR addendum, Finding 1's impact changes. The claim would still be mis-cited, because the source only offers ZDR conditionally.

## WHAT HOLDS UP
- **Training:** "Inputs and outputs are not used to train Lumen models [1]" matches the source verbatim in substance: "not used to train Lumen models on any plan." The "any plan" wording means it applies to our standard plan.
- **SOC 2:** The claim matches [2], with the caveat in Finding 4.
- **Context window:** "up to 200,000 tokens" matches [2].
- **Citation mapping:** Each citation number points at the right file. The problem is what [1] is claimed to say, not which file it points to.

## UNVERIFIED CLAIMS
- **"Our account is on the standard plan; we have no enterprise agreement."** Confirm from the Lumen account console or the signed order form.
- **Whether the live pages still match the 5 Oct snapshots.** Re-read both pages on the decision date.
- **"Enough for a 150-page contract."** Tokenize real long contracts to settle it.
- **SOC 2 scope.** Obtain and read the report.

## QUESTIONS FOR THE AUTHOR
1. Is there any enterprise agreement or signed ZDR addendum with Lumen, or a plan to obtain one?
2. Have the relevant client contracts been checked for restrictions on sending documents to third-party processors?

## DECISION-MAKER SUMMARY
The assessment's key claim is false for our account. Lumen keeps API inputs for 30 days on the standard plan, and zero retention requires an enterprise agreement with a signed ZDR addendum that we do not have. Do not send client contracts until that addendum is in place or 30-day retention is cleared against client obligations. Proceeding anyway risks a confidentiality breach that cannot be reversed.

## OWNER SUMMARY
The report says the service deletes our documents immediately, but the vendor's own page says it keeps them for 30 days on our current plan. Immediate deletion is only offered under a separate enterprise contract that we have not signed. Client contracts should not be sent to this service until that is resolved.

```json
{
  "verdict": "REJECT",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "assessment.md", "status": "seen", "matters": true},
    {"item": "sources/lumen-privacy.md", "status": "seen", "matters": true},
    {"item": "sources/lumen-security.md", "status": "seen", "matters": true},
    {"item": "live Lumen pages as of 2026-10-07", "status": "not_openable", "matters": false},
    {"item": "Lumen account agreement / plan terms", "status": "not_seen", "matters": true},
    {"item": "SOC 2 Type II report", "status": "not_seen", "matters": true},
    {"item": "client contract confidentiality clauses", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Work under review contains vendor pages and an internal assessment, no client documents; the decision concerns client-confidential material."},
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
     "location": "assessment.md Summary vs sources/lumen-privacy.md Retention",
     "scenario": "Assessment claims Lumen is zero-retention citing [1]; [1] says inputs/outputs are retained 30 days for abuse monitoring and ZDR requires an enterprise agreement with a signed ZDR addendum, which the account does not have. Client contracts sent on the standard plan are retained 30 days; irreversible.",
     "fix": "Withdraw the conclusion; state 30-day retention on the standard plan; do not send client documents unless a ZDR addendum is executed or 30-day retention is cleared against client obligations.",
     "status": "confirmed"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "C",
     "location": "assessment.md Supporting facts: 'enough for a 150-page contract [2]'",
     "scenario": "Source states only 'up to 200,000 tokens'; the page-count claim is unsourced, violating 'base every claim on Lumen's pages'. Dense or OCR'd 150-page contracts plus prompt and output may exceed the window, truncating clauses.",
     "fix": "Remove or mark as an estimate; tokenize real long contracts and confirm whether the limit includes output.",
     "status": "n/a"},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "A",
     "location": "assessment.md Summary: 'so it is safe'",
     "scenario": "'Safe' does not follow from the cited properties; client subprocessor/consent clauses and abuse-monitoring access are unaddressed, so a breach is possible even under ZDR.",
     "fix": "Replace 'safe' with the specific verified properties; check client confidentiality clauses and Lumen's abuse-monitoring access.",
     "status": "n/a"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "C",
     "location": "assessment.md Supporting facts: 'SOC 2 Type II report [2]'",
     "scenario": "Claim omits the period (ending 30 June 2026); scope and exceptions unreviewed, so readers may over-trust it.",
     "fix": "Cite the period; obtain the report and confirm scope and exceptions.",
     "status": "n/a"}
  ]
}
```