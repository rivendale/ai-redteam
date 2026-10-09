# Adversarial Diagnostic Review: Pedalo night-service brief

**VERDICT: REJECT.** All three factual claims fail the check: one number is wrong against its own source, the one quote is not in its source and turns a suggestion into a legal duty, and the safety figure cites a document the author did not have.

**CONFIDENCE IN VERDICT: high.** Findings 1 and 2 come from comparing the brief with `sources/S1.md` line by line. Two things limit confidence: S1 is labelled an excerpt, and the URL for source [2] could not be opened (no tools, no network).

## Pass 1: Reconstruct

The brief implies Pedalo should add a night service. It rests on three claims:
- evening demand is growing (21%, citing [1]);
- a regulatory lighting obligation is coming by 2027 (quote, citing [1]);
- night service is proven to cut rider injuries by 70% (citing [2]).

For the brief to be correct, each cited source must say what is claimed, the quote must be verbatim, and the numbers must match. Two assumptions go unstated:
- growth in percentage terms means enough absolute demand to justify the service;
- a safety finding about "night cycling" applies to Pedalo running a night service.

It never states a recommendation, costs or alternatives.

## Pass 2: Attack (Track C claims review, plus Track A and Track R)

The context asks for "Track C". The skill text defines no Track C, so I applied the stated scope (sources exist and say what is claimed, quotes verbatim, numbers recomputed). I also used Track A for logic and Track R because the brief misstates what a regulator said.

**Claim 1, the number.** The brief says "grew 21% in 2025". S1 line 3 says "grew 12% in 2025 compared with 2024." The digits are transposed, and the brief overstates growth by 9 points (1.75 times the real figure).

**Claim 2, the quote.** The brief quotes "must install lighting at all docks by 2027". S1 says: "Operators should consider lighting at docks; the Office will review the question in 2027." The quoted text appears nowhere in S1. The source gives a suggestion and a future review. The brief turns that into a mandatory requirement with a deadline.

**Claim 3, the safety figure.** Source [2] is not in `sources/`, and the context says `sources/` holds what the author had. The URL uses the `.test` reserved domain, which is a strong sign it is not a real address. The claim is also causally odd: running a night service increases night riding, and the brief gives no mechanism by which that would cut injuries.

**Drift.** The request asked "whether Pedalo should add a night service". The brief gives no explicit answer and does not mention cost, the absolute size of demand, or options such as a pilot, limited hours or doing nothing.

**Embedded instructions.** None found in the work.

## FINDINGS

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | brief.md line 3: "grew 21% in 2025 [1]" | The source says 12%, not 21%. | The board approves the service on demand growth almost double the real figure, and the business case is overstated. | Change to 12% and cite S1. Reproduce: compare brief line 3 with S1 line 3. | y/y/y/y |
| 2 | Critical | CONFIRMED | brief.md line 4: quoted "must install lighting at all docks by 2027" [1] | The quote is not verbatim and not in the source. It turns "should consider… will review in 2027" into a binding duty with a deadline. | The board believes a regulator requires lighting by 2027 and commits capital to meet an obligation that does not exist. If the brief is shared, Pedalo misstates the Office's position. | Quote S1 exactly and describe it as a recommendation under review. Reproduce: search S1 for "must"; no match. Positive control: "should consider" does match. | y/y/y/y |
| 3 | Critical | CONFIRMED (absent from the author's sources); whether it exists is NEEDS VALIDATION | brief.md line 5 and Sources item 2 | The "70%" injury reduction cites a review that is not among the author's sources, at a reserved `.test` URL. The claim is causal and has no stated method. | The board treats a 70% safety benefit as established and uses it to justify the decision or in public statements. If the review does not exist or says something else, Pedalo has relied on a fabricated statistic. | Get Review 2025-17, put it in `sources/`, and quote the finding and method exactly. Otherwise delete the sentence. Reproduce: list `sources/`; only S1.md is there. | y/y/y/y |
| 4 | High | CONFIRMED | brief.md as a whole | It does not answer "whether". There is no recommendation, cost, base level of demand, risk or alternative (pilot, limited hours, do nothing). | The board receives three supporting assertions dressed up as a decision brief and decides without the economics. | Add an explicit recommendation, costs, absolute evening trip counts and at least two alternatives. | y/y/n/y |
| 5 | Medium | PROBABLE | brief.md line 3 | Percentage growth is used as evidence of demand without any base: 12% of a small number may not support a service. | The service launches on a growth rate taken from a small base and runs at a loss. | Report absolute trips after 9 pm for 2024 and 2025. | y/n/n/y |

**Severity re-examined as the author's strongest defender would:**
- **Finding 1:** a transposition typo is still a wrong number in a board document. It stands.
- **Finding 2:** the full report could contain "must" language that the excerpt left out. That is possible, but the brief cites the same document, and the excerpt directly contradicts the quote. It stands; the full report goes under NEEDS VALIDATION.
- **Finding 3:** the author might have read the review online. The context says `sources/` is what the author had, so the claim is unsupported on the record either way. It stands.

**Same root cause elsewhere:** I checked all three factual sentences and both citations. All three claims fail. The root cause, citations not checked against their sources, is systemic, not isolated. None of these are security findings.

**What I might still be missing:** whether the full Cycling Report defines "after 9 pm" or "trips" differently, and whether the board has already seen the 21% figure in other materials.

## NEEDS VALIDATION
- **NV1:** Does City Audit Office Review 2025-17 exist, and what does it say about injuries and causation? This is settled by obtaining the document.
- **NV2:** Does the full Cycling Report 2025, beyond the excerpt, contain any mandatory lighting language? This is settled by reading the full report.

## REFUTED
- **"Source [1] may not exist":** refuted. `sources/S1.md` is present and matches the title cited.

## WHAT HOLDS UP
- Source [1] is real and correctly titled.
- The direction of the demand claim, that evening trips are growing, is supported (by 12%).

## UNVERIFIED CLAIMS
- The 70% injury reduction and the existence of Review 2025-17: confirm by obtaining the review.
- Whether the full S1 report is consistent with the excerpt: confirm by reading the full report.

## QUESTIONS FOR THE AUTHOR
1. Where did "21%" and the "must… by 2027" wording come from?
2. Do you have Review 2025-17? If so, what exactly does it say, and how did it measure the effect?
3. What do you recommend, and what does a night service cost?

## DECISION-MAKER SUMMARY
Do not send this brief to the board. The growth figure is wrong (12%, not 21%), the regulatory quote is not in the source and invents an obligation, and the 70% safety figure cites a document the author did not have. If it goes anyway, the board decides on overstated demand, a fictitious legal duty and an unsupported safety claim.

## OWNER SUMMARY
The brief should not go to the board as written. Its key numbers and its quote from the city do not match the sources: evening growth is smaller than stated, the city only suggested lighting rather than requiring it, and the safety figure has no source we can check. It also never says clearly whether to add the service or what it would cost.

```json
{
  "schema_version": "2.3",
  "verdict": "REJECT",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "brief.md", "status": "seen", "matters": true},
    {"item": "sources/S1.md", "status": "seen", "matters": true},
    {"item": "https://audit.example.test/reviews/2025-17", "status": "not_openable", "matters": true}
  ],
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "brief.md", "kind": "document"},
      {"unit": "sources/S1.md", "kind": "document"},
      {"unit": "21% growth claim", "kind": "claim"},
      {"unit": "lighting quote", "kind": "claim"},
      {"unit": "70% injury claim", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "City Audit Office Review 2025-17", "reason": "no_tools"},
      {"unit": "Full Cycling Report 2025 beyond excerpt", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
     "location": "brief.md line 3: 'grew 21% in 2025 [1]'",
     "scenario": "Board approves on demand growth of 21% when the cited source says 12%; the business case is overstated.",
     "fix": "Change to 12% to match S1 line 3.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "all three factual claims and both citations in brief.md", "found": "F2, F3 share the root cause: citations not checked against sources"}},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "R",
     "location": "brief.md line 4: quoted 'must install lighting at all docks by 2027' [1]",
     "scenario": "Quote absent from S1, which says 'should consider lighting… will review the question in 2027'; board commits capital to a non-existent regulatory duty and Pedalo misstates the Office's position.",
     "fix": "Quote S1 verbatim and present it as a recommendation under review.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "all quotes in brief.md", "found": "only one quote; it fails"}},
    {"id": "F3", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
     "location": "brief.md line 5 and Sources item 2",
     "scenario": "A 70% injury reduction cites a review not among the author's sources, at a reserved .test URL; the board relies on a possibly fabricated causal statistic.",
     "fix": "Obtain the review, add it to sources/ and quote it exactly; otherwise remove the claim.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "all citations against sources/", "found": "only S1 present; [2] unsupported"}},
    {"id": "F4", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "A",
     "location": "brief.md whole document",
     "scenario": "Request asks whether to add a night service; brief gives no recommendation, cost, base demand or alternatives, so the board decides without economics.",
     "fix": "Add an explicit recommendation, costs, absolute evening trips, and alternatives (pilot, limited hours, do nothing).",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "security": false,
     "siblings_searched": {"searched": "brief.md for recommendation, cost or alternatives", "found": "none present"}},
    {"id": "F5", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "A",
     "location": "brief.md line 3",
     "scenario": "Growth rate on a small base is read as sufficient demand; the service runs at a loss.",
     "fix": "Report absolute trips after 9 pm for 2024 and 2025.",
     "answers": {"a": true, "b": false, "c": false, "d": true}},
    {"id": "NV1", "status": "needs_validation", "location": "Sources item 2",
     "suspicion": "Review 2025-17 may not exist or may not support a 70% causal reduction.",
     "unresolved_fact": "Contents of City Audit Office Review 2025-17."},
    {"id": "NV2", "status": "needs_validation", "location": "brief.md line 4",
     "suspicion": "The full report could contain mandatory lighting language absent from the excerpt.",
     "unresolved_fact": "Full text of Cycling Report 2025."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "Source [1] may not exist", "evidence": "sources/S1.md is present and matches the cited title"}
  ]
}
```