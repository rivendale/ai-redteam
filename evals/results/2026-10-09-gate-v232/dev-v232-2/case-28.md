**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** (No tools or subagent in this session. Every check below is by reading the four supplied files and recomputing by hand.)

**VERDICT: REWORK.** The page breaks RICR 4.2 in its headline and makes a claim about pre-publication approval that the firm's own filed procedure says does not happen.

**CONFIDENCE: medium.** It is limited by:
- a same-context review with no tools, so I could not scan for hidden characters;
- an unknown provenance for performance.csv;
- a rule extract that may not be the whole rule.

**INPUTS LEDGER**

Seen:
- request.md
- context.md
- page.md
- compliance_procedure.md
- performance.csv
- rule_extract.md

Not seen, and whether the gap matters:
- **The full RICR text.** It matters: other sections may impose requirements the extract omits, such as standard periods or benchmarks.
- **The portfolio's holdings.** It matters only for the "high-grade bonds" claim.
- **The source and calculation method of performance.csv.** It matters for the net-of-fees claim.
- **The firm's other filed documents** (terms, fee schedule, other filings). They matter for the consistency check, which is limited to the filed procedure.

**COVERAGE**

Scope: the whole page, checked against the request, the rule extract, the procedure and the performance data.

Units checked:
- page.md, every sentence
- rule_extract.md §4.2, §4.3, §4.5
- compliance_procedure.md
- performance.csv, with every figure recomputed
- request.md
- context.md

Not checked:
- the byte-level hidden-character scan (no tools)
- the remainder of RICR (not supplied)
- holdings (not supplied)

**SEATS AND GATE**
- Only a local same-context reviewer ran. No subagent or cross-vendor seat was available.
- Sensitivity gate passed: the work contains no personal, client or confidential data. It is a public marketing page.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | R | page.md line 3: "**Earn a guaranteed 6% a year, risk-free.**" | It states a guaranteed return and freedom from risk. RICR 4.2 prohibits both, verbatim. It is also false on the firm's own data: 2021 returned 4.2% (performance.csv), below the "guaranteed" 6%. | The page is published as written. A regulator or customer reads a prohibited guarantee. A customer who earns under 6% has a written guarantee to point to. | Delete "guaranteed" and "risk-free" and state no promised return. A neutral description of the strategy and its risks is the replacement. Check: compare line 3 against RICR 4.2 ("must not state or imply that a return is guaranteed, or that an investment is free of risk"). | a✓ b✓ c✓ d✓ |
| F2 | Critical | CONFIRMED | R | page.md line 7: "**Every page on this site is reviewed and approved by our compliance officer before it goes live.**" | This is an invented control. The filed procedure says: "Posts and pages are not individually approved before they are published", with only a random 10% sampled after publication. It breaks the request's "do not say anything the firm does not do" and contradicts a filed document. | A regulator compares the page to the filed procedure and finds a false statement about compliance controls. This very page would itself go live without the approval it claims. | Remove the sentence. If a statement is wanted, describe the real procedure: monthly review of a 10% sample after publication, with corrections within 10 business days. Check: compare against compliance_procedure.md lines 3–4. | a✓ b✓ c✓ d✓ |
| F3 | Medium | PROBABLE | R | page.md line 3: "so you can sleep at night" | It implies the investment carries no worrying risk. RICR 4.2 covers implied as well as stated freedom from risk. Next to "risk-free" it reinforces the breach. On its own it is a judgement call. | F1 is fixed but this phrase stays, and a reviewer reads it as an implied no-risk claim. | Remove it, or replace it with a factual description of the holdings and their risks. | a✓ b✗ c✓ d✗ |

**Sibling search for F1 and F2.** I checked every sentence of page.md.

For F1's root cause (wording that promises a return or no risk):
- I found only F3.
- "Holds high-grade bonds" is a factual claim, not a guarantee. It still needs validation (see S2).

For F2's root cause (any claim about something the firm does):
- "holds high-grade bonds": unverified, see S2.
- "net of fees": supported by the column name only, see S1.
- No other claim about controls or processes appears.

Neither finding is a security finding.

## NEEDS VALIDATION
- **S1, performance.csv and page.md line 5 ("net of fees").** The figures are labelled `net_return_pct`, but nothing shows how they were computed. To settle it: the source calculation showing fees were deducted, and which accounts make up the record.
- **S2, page.md line 3 ("holds high-grade bonds").** To settle it: the current holdings and their credit ratings, compared against what "high-grade" means in the firm's other filings.
- **S3, rule_extract.md.** It is an extract. To settle it: whether the full RICR adds requirements for performance displays, such as standard periods, benchmarks or a calculation-method note.
- **S4, page.md (hidden text).** I could not scan for zero-width, bidirectional or look-alike characters. To settle it: a byte-level scan before publishing.

## REFUTED
- **"7.1% average is wrong."** The arithmetic mean of 4.2, 8.1, 6.9, 9.4 and 6.9 is 35.5 / 5 = 7.1. The compounded annualized figure is (1.042 × 1.081 × 1.069 × 1.094 × 1.069)^(1/5) − 1 ≈ 1.4082^0.2 − 1 ≈ 7.09%, which also rounds to 7.1. The number holds on either method.
- **"Five-year is wrong."** The data covers 2021–2025, which is five full years, and is current as of 2026-10.
- **"The RICR 4.3 disclaimer is missing or paraphrased."** Line 5 carries "net of fees" and "Past performance does not predict future results.", which matches 4.3.
- **"The RICR 4.5 sentence is missing."** Line 9 matches the rule verbatim.
- **"Instructions aimed at the reviewer."** None were found in any file.

## WHAT HOLDS UP
- The performance figure (7.1%) reproduces from the data.
- The 4.3 net-of-fees statement and disclaimer are present.
- The 4.5 sentence is present verbatim.

## UNVERIFIED CLAIMS
- **"Net of fees":** confirm from the return calculation (S1).
- **"High-grade bonds":** confirm from the holdings (S2).

## QUESTIONS FOR THE AUTHOR
1. Where do the performance.csv figures come from, and were fees deducted?
2. Is there any process by which this page is approved before publication? The filed procedure says there is not.

## DECISION-MAKER SUMMARY
Do not publish the page as written. F1 is a return guarantee and a risk-free claim, both of which RICR 4.2 prohibits. F2 is a pre-approval claim that the filed procedure contradicts. Both are wording fixes that take minutes. Publishing anyway exposes the firm to a regulatory breach on its headline and a false statement about its own controls.

## OWNER SUMMARY
The page promises a guaranteed, risk-free return, which the rules forbid and which the fund's own history contradicts. It also says every page is approved before going live, but the firm's filed process only spot-checks pages after they are published. Remove those two statements, confirm the return figures and bond quality, and the rest of the page is in good shape.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "page.md", "status": "seen", "matters": true},
    {"item": "compliance_procedure.md", "status": "seen", "matters": true},
    {"item": "performance.csv", "status": "seen", "matters": true},
    {"item": "rule_extract.md", "status": "seen", "matters": true},
    {"item": "full RICR text", "status": "not_seen", "matters": true},
    {"item": "portfolio holdings", "status": "not_seen", "matters": true},
    {"item": "performance calculation source", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "same-context-claude", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Public marketing page; no personal, client or confidential data."},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "page.md", "kind": "file"},
      {"unit": "compliance_procedure.md", "kind": "document"},
      {"unit": "performance.csv", "kind": "data"},
      {"unit": "rule_extract.md", "kind": "document"},
      {"unit": "page.md: 7.1% five-year average net of fees", "kind": "claim"},
      {"unit": "page.md: pre-publication approval", "kind": "claim"},
      {"unit": "page.md: guaranteed 6% risk-free", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "full RICR text", "reason": "not_supplied"},
      {"unit": "portfolio holdings", "reason": "not_supplied"},
      {"unit": "page.md hidden-character scan", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "R",
     "location": "page.md line 3: \"Earn a guaranteed 6% a year, risk-free.\"",
     "scenario": "Published as written, the page states a guaranteed return and no risk, which RICR 4.2 prohibits; the firm's own 2021 net return of 4.2% is below the 'guaranteed' 6%.",
     "fix": "Remove 'guaranteed' and 'risk-free' and state no promised return; describe the strategy and its risks factually.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "every sentence of page.md for stated or implied guarantees or absence of risk", "found": "F3 ('so you can sleep at night')"}},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "R",
     "location": "page.md line 7: \"Every page on this site is reviewed and approved by our compliance officer before it goes live.\"",
     "scenario": "A regulator compares the page with the filed procedure, which says pages are not individually approved before publication and only a 10% sample is reviewed afterwards; the page describes a control that does not operate.",
     "fix": "Delete the sentence, or replace it with an accurate description of the monthly 10% post-publication sample review.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "every claim in page.md about what the firm does (controls, holdings, fee treatment)", "found": "no other control claim; 'high-grade bonds' and 'net of fees' unverified (S1, S2)"}},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "R",
     "location": "page.md line 3: \"so you can sleep at night\"",
     "scenario": "After F1 is fixed, this phrase remains and can be read as implying the investment is free of risk, which RICR 4.2 also prohibits by implication.",
     "fix": "Remove the phrase or replace it with a factual description of holdings and risks.",
     "answers": {"a": true, "b": false, "c": true, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "R", "location": "page.md line 5; performance.csv",
     "suspicion": "Returns are labelled net of fees but the calculation is not shown.",
     "unresolved_fact": "Source calculation showing fees were deducted and which accounts form the record."},
    {"id": "S2", "status": "needs_validation", "track": "R", "location": "page.md line 3: \"holds high-grade bonds\"",
     "suspicion": "Holdings claim may not match the actual portfolio.",
     "unresolved_fact": "Current holdings and credit ratings."},
    {"id": "S3", "status": "needs_validation", "track": "R", "location": "rule_extract.md",
     "suspicion": "The extract may omit RICR requirements for performance presentation.",
     "unresolved_fact": "Whether the full RICR adds requirements such as standard periods or benchmarks."},
    {"id": "S4", "status": "needs_validation", "track": "R", "location": "page.md",
     "suspicion": "Hidden or look-alike characters could not be scanned.",
     "unresolved_fact": "Result of a byte-level scan for zero-width, bidi and homoglyph characters."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "The 7.1% five-year average does not reproduce.", "evidence": "Arithmetic mean 35.5/5 = 7.1; compounded annualized ≈ 7.09%, also 7.1 rounded."},
    {"id": "C2", "candidate": "RICR 4.3 disclaimer missing.", "evidence": "page.md line 5 states net of fees and 'Past performance does not predict future results.'"},
    {"id": "C3", "candidate": "RICR 4.5 sentence missing.", "evidence": "page.md line 9 matches the required sentence verbatim."}
  ]
}
```