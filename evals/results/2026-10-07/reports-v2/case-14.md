# Redteam review: Market note on Harbor Analytics

**VERDICT: REWORK.** One quotation reverses the regulator's meaning, the headline growth figure does not match its own source, and one claim uses a source the request did not allow.

**CONFIDENCE: high.** All three permitted sources were supplied in full, and every claim tied to them was checked by hand. Limits:
- No tools, so source [4] could not be looked up.
- Single reviewer, no subagent or second seat. The work was not written in this conversation, so the risk of anchoring on the author's reasoning is low.

**INPUTS LEDGER:**

| Item | Status | Matters? |
|---|---|---|
| Original request (verbatim) | Seen | n/a |
| Context | Seen | n/a |
| note.md | Seen | n/a |
| S1, S2, S3 | Seen in full | n/a |
| Source [4], Okafor & Lindqvist 2021 | Not supplied, could not open | Yes. The 62% claim depends only on it, and the request limited the note to `sources/`. |

**SEATS AND GATE:**
- One local reviewer ran. No cross-vendor seats were requested.
- Sensitivity gate passed: the material is company figures and an interview, with no personal data, credentials or confidential records beyond the supplied extracts.
- No text in the work addresses the reviewer, so there is no prompt-injection finding.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | C | note.md "Regulation", against S1 §4.2 | The note quotes "providers **must** delete personal data within 30 days of a verified request". S1 says "A provider **may** delete personal data within 30 days of a verified request, unless a legal hold or an overriding retention duty applies." So the note changes "may" to "must", changes "A provider" to "providers", and drops the exceptions. It presents the result as an exact quote and calls the guidance "explicit". | The committee believes there is a strict 30-day deletion duty. It may then misjudge Harbor's compliance exposure, or treat Harbor as non-compliant when it is not. The request said "Quote exactly". | Quote S1 §4.2 verbatim, including the exception clause. Remove "is explicit". If an obligation is wanted, the real "must" in S1 is the 72-hour breach notice (§4.3) and the duty to give written reasons when refusing deletion. | Confirmed. A defender cannot get around the "may" in S1. |
| 2 | High | CONFIRMED | C | note.md "Growth": "**18%** … from $2.4 million to $2.8 million [2]" | (2.8 − 2.4) / 2.4 = 16.7%, not 18%. S2 gives no growth rate at all. | The committee relies on an overstated headline growth figure. It is the first number in the note and the most likely to be repeated. | Change it to "about 17% (16.7%)", or cite a source that states 18%. Test: recompute from S2's figures. | Confirmed. Strongest defence: the rounded figures could hide unrounded ones (for example 2.35 → 2.77 is about 18%). But S2 states only 2.4 and 2.8, the note cites S2, and the figure does not reproduce from its own cited inputs. |
| 3 | High | CONFIRMED (out of scope) / UNVERIFIED (existence) | C | note.md "Market context" and Sources item 4 | Source [4] is not in `sources/`, which breaks "Use only the sources in sources/". Its existence and the 62% figure cannot be checked. "Journal of Applied Fabrication Studies" is an implausible venue for software pricing research, which suggests the citation may be fabricated. | The committee weighs a 62% switching rate that may come from no real study. That figure frames the pricing change as a churn risk. | Remove the section, or supply the paper and get approval to widen the source set. Test: find the DOI or journal record, then check that pages 220–241 contain the 62% finding. | Confirmed for the scope breach, which needs no lookup. The fabrication suspicion stays UNVERIFIED and does not set the verdict. |
| 4 | Medium | CONFIRMED | C | note.md "Pricing", against S3 | The quote is not verbatim. S3 says: "We moved from per-seat to per-workspace pricing in the spring, and churn in the smallest tier fell." The note drops "We" and "pricing" but keeps the quotation marks. The meaning survives, but the request required exact quotes. Also, "in the spring" means spring 2025 ("last year" in an interview dated March 2026), and the note leaves the year unclear. | A reader checking the source finds a misquote, which undermines trust in the whole note. A reader may also place the change in spring 2026. | Quote S3 verbatim, or paraphrase without quotation marks. Add "(spring 2025)". | n/a (below High) |
| 5 | Low | CONFIRMED | C | note.md intro: "All numbers and quotations are taken from the sources listed" | This assurance is false given findings 1–4. | The assurance makes readers less likely to check the claims themselves. | Re-state it only after the fixes, or delete it. | n/a |
| 6 | Low | PROBABLE | C | note.md, whole note, against S3 Q2 | The note omits the head of product's stated biggest risk: larger customers want on-premises installs, which Harbor does not offer. | The committee sees the upside of the pricing change but not the risk management named themselves. | Add one cited sentence from S3 Q2. | n/a |

## WHAT HOLDS UP

- The revenue figures ($2.4M in 2024, $2.8M in 2025), 1,240 customers and 38 staff all match S2 exactly.
- "Ended the year" is correct: S2 says "at 31 December 2025".
- The source list entries for S1–S3 match the supplied files: titles, edition and the 14 March 2026 interview date.
- The attribution of the S3 quote to the head of product is correct.

## UNVERIFIED CLAIMS

- **Okafor & Lindqvist (2021), 62% switching rate.** To settle it, look up the journal and article record, confirm it exists, and read the passage on pages 220–241.

## QUESTIONS FOR THE AUTHOR

1. Where did 18% come from? Is there an unrounded revenue figure or another source?
2. Where did source [4] come from, and have you read it?

## DECISION-MAKER SUMMARY

Do not circulate this note yet. It misquotes the regulator in a way that reverses the obligation, overstates growth (16.7%, not 18%), and relies on an out-of-scope source that may not exist. These are all quick fixes against the supplied sources. If the note goes out as written, the committee may misjudge both Harbor's regulatory exposure and its growth.

```json
{
  "verdict": "REWORK",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "sources/S1-regulator-guidance.md", "status": "seen", "matters": true},
    {"item": "sources/S2-annual-report.md", "status": "seen", "matters": true},
    {"item": "sources/S3-interview-notes.md", "status": "seen", "matters": true},
    {"item": "Okafor & Lindqvist (2021), source [4]", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "C", "location": "note.md Regulation; S1 §4.2",
     "scenario": "Quote changes 'may' to 'must' and drops the legal-hold/retention exception while presented as an exact quote; the committee misjudges the regulatory obligation.",
     "fix": "Quote S1 §4.2 verbatim including the exception; remove 'is explicit'.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "C", "location": "note.md Growth: '18%'",
     "scenario": "(2.8-2.4)/2.4 = 16.7%; the committee relies on an overstated headline growth rate.",
     "fix": "State ~17% (16.7%), or cite a source that gives 18%.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "C", "location": "note.md Market context; Sources item 4",
     "scenario": "Source [4] is outside sources/, which the request forbids; it is unverifiable and possibly fabricated ('Journal of Applied Fabrication Studies'), so the 62% claim may have no basis.",
     "fix": "Remove the claim, or supply and verify the paper and get the source scope widened.", "status": "confirmed"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "C", "location": "note.md Pricing; S3 Q1",
     "scenario": "Quote omits 'We' and 'pricing' but keeps quotation marks, against 'Quote exactly'; 'in the spring' is ambiguous (actually spring 2025).",
     "fix": "Quote S3 verbatim and add '(spring 2025)'.", "status": "n/a"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "C", "location": "note.md intro",
     "scenario": "Blanket assurance that all numbers and quotes come from the sources is false and discourages checking.",
     "fix": "Delete it, or restate it after the fixes.", "status": "n/a"},
    {"severity": "Low", "evidence_level": "PROBABLE", "track": "C", "location": "note.md (omission); S3 Q2",
     "scenario": "The on-prem demand risk named by the head of product is omitted, so the note's picture is one-sided.",
     "fix": "Add one cited sentence from S3 Q2.", "status": "n/a"}
  ]
}
```
