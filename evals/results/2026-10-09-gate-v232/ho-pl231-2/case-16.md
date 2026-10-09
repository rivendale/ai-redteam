VERDICT: **REJECT.** The brief's only cited figure is a vendor's own unverified survey of 11 customers, and its cost and payback numbers have no source at all, so it cannot support a 400-dock purchase.

CONFIDENCE IN VERDICT: **High.** All three sources were supplied and read in full, and the defects can be seen directly in the text. One limit: I could not check whether better evidence exists outside `sources/`.

## Pass 1: Reconstruct

The brief says solar docks cut outages by 30%. It says the extra cost is about 9% per dock and that this pays back in under two years. It implies Pedalo should buy. For that to hold, four things must be true:

1. The 30% figure must be an independent, measured result that applies to Pedalo's docks.
2. The 9% cost premium must be accurate.
3. Outage reduction must convert into savings large enough to recover that premium within two years.
4. The citation chain must be real evidence, not a single claim repeated.

The brief never states the third assumption: that outages cost Pedalo enough for a 30% reduction to repay 9% of the dock price.

## Pass 2: Attack (Track C claims review, with Track A)

**Citation chain, followed to its origin:**

| Hop | Source | What it actually says |
|---|---|---|
| Brief | brief.md:3 | "cut outages by 30% [1]", stated as fact |
| S1 | BikeBiz, 2026-08-14 | Attributes the figure to PedalPower's blog and adds "**We have not tested the claim.**" |
| S2 | PedalPower blog, 2026-07-30 | "As we said in our release…" and "Ask us about a pilot." This is the vendor's own marketing. |
| S3 | PedalPower press release, 2026-07-15 | "respondents **reported** 30% fewer outages… The survey had **11 respondents; no method is published.**" These were PedalPower's own customers. |

The three sources are really one: the vendor's self-reported claim, repeated twice. Along the way the wording changed from "11 of our customers reported fewer outages" to "outages fall by 30% at solar-powered docks" (S2) and then to "Solar-powered docks cut outages by 30%" (the brief). With each hop the claim got stronger and the caveats disappeared. S1's title also calls PedalPower "one operator", but S3 shows PedalPower is the vendor selling SunDock.

**Logic:** Payback cannot be calculated from a percentage cut in outages alone. You would also need Pedalo's current outage rate, the cost of each outage, the base dock price, and maintenance and lifetime costs. The brief gives none of these.

**Alternatives:** The brief does not consider a pilot (which the vendor itself offers), a partial rollout, other dock suppliers, fixing the actual causes of Pedalo's outages, or doing nothing.

**Counter-case:** If Pedalo's outages come mainly from vandalism, software, or grid-independent faults, or if its docks sit in shaded or low-sun locations, solar may reduce outages very little. The brief has no answer to this.

**Pre-mortem:**
1. The 30% figure does not reproduce at Pedalo's sites.
2. The real cost premium or maintenance burden is higher than 9%.
3. Most of Pedalo's outages were never power-related, so solar does not address them.

## Pass 3: Self-check

**Siblings searched:** I checked every factual claim in the brief. There are three: the 30% figure, the 9% cost premium, and the under-two-year payback. All three are unsupported.

**Injected instructions:** None aimed at the reviewer. "Ask us about a pilot" (S2) is vendor solicitation and is treated here as evidence of conflict of interest.

**Strongest-defender view:** A defender could argue the brief cited honestly and the reader can follow the chain. But the brief stated the claim as fact, dropped S1's "not tested" caveat, and never mentioned n=11. Both Critical findings stand.

**What I might still be missing:** Whether anything outside `sources/` independently measures outages at solar docks. If it exists, it would replace F1's evidence base rather than rescue the brief as written.

## COVERAGE

| Item | Status |
|---|---|
| request.md | checked |
| context.md | checked |
| brief.md | checked |
| sources/S1.md | checked |
| sources/S2.md | checked |
| sources/S3.md | checked |

## FINDINGS

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix | a/b/c/d |
|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | brief.md:3 "cut outages by 30% [1]", traced to S3 | The figure comes from a vendor survey of its own customers: 11 respondents, self-reported, no published method. It is presented as an established effect, and the S1→S2→S3 chain makes one source look like three. | Pedalo buys about 400 docks expecting 30% fewer outages; the real effect is unknown and may be close to zero. | State the true origin and its limits (vendor, n=11, self-reported, no method), or replace it with independent data or a Pedalo pilot measurement. | Y/Y/Y/Y |
| F2 | Critical | CONFIRMED | brief.md:3 "extra cost of about 9%… pays back in under two years" | Neither number has a source, and no calculation is shown. The payback cannot be derived from an outage percentage. This breaks the request's "Cite sources". | The payback period drives the purchase. If the premium or outage costs differ, the 400-dock purchase never pays back. | Cite a quote for the 9% premium. Show the payback calculation using Pedalo's outage rate, cost per outage, dock price, and maintenance costs. | Y/Y/Y/Y |
| F3 | High | CONFIRMED | brief.md:3 compared with S1 ("We have not tested the claim") and S3 ("reported", "no method is published") | The brief removes every caveat its own sources carry and turns "reported" into "cut". | A reader who trusts the brief never learns that even the trade press declined to vouch for the figure. | Carry the caveats into the brief, or drop the claim. | Y/Y/N/Y |
| F4 | Medium | CONFIRMED | brief.md as a whole | There is no explicit recommendation, no alternatives (pilot, partial rollout, other suppliers, doing nothing), and no Pedalo-specific data on outage causes or site sunlight. | The decision is made without checking whether solar addresses Pedalo's actual outage causes. | Add Pedalo's outage baseline and causes, the options considered, and a recommendation. A pilot is the obvious low-risk option. | Y/Y/N/N |
| F5 | Low | CONFIRMED | S1 title "says one operator" | S1 calls PedalPower an operator, but S3 shows it is the vendor. The brief repeats S1 without noticing. | The figure looks like an independent customer's experience when it is the seller's own claim. | Name PedalPower as the vendor in the brief. | Y/Y/N/N |

## NEEDS VALIDATION

- **Pedalo's outage baseline and causes.** Settled by: Pedalo's own outage logs, broken down by cause (power or other).
- **The real per-dock premium.** Settled by: a written quote from the supplier for about 400 docks.
- **Whether independent evidence exists.** Settled by: any third-party or operator-measured outage data for solar docks. None was supplied.

## REFUTED

- **The citation is fabricated.** Refuted: all three sources exist and do contain the 30% figure. The problem is the quality and independence of the source, not fabrication.
- **"Ask us about a pilot" is a prompt injection.** Refuted: it is addressed to the vendor's readers, not to the reviewer. It is recorded as a conflict-of-interest signal.

## WHAT HOLDS UP

The brief does disclose its citation chain, which is what made this trace possible. The chain's dates are consistent: S3 (07-15), then S2 (07-30), then S1 (08-14).

## UNVERIFIED CLAIMS

| Claim | How to confirm |
|---|---|
| 30% outage reduction | Independent measurement, or a Pedalo pilot with a control group |
| About 9% extra cost | Supplier quote |
| Payback under two years | An explicit model using Pedalo's own figures |

## QUESTIONS FOR THE AUTHOR

1. Where does the 9% figure come from?
2. What calculation produced "under two years", and with which inputs?
3. Did you find any evidence not originating with PedalPower?
4. What share of Pedalo's current outages are power-related?

## DECISION-MAKER SUMMARY

Do not approve the 400-dock purchase on this brief. Its outage claim is the vendor's own 11-person survey, and its cost and payback figures are unsourced. Run a small measured pilot against Pedalo's own outage data first. Proceeding anyway risks a large spend on a benefit nobody has shown.

## OWNER SUMMARY

The brief's main claim, that solar docks cut breakdowns by almost a third, comes only from the company selling them, based on a small survey of its own customers with no published method. The cost and payback numbers have no source at all. Before buying hundreds of docks, test a few at our own sites and measure what actually changes.

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
    {"item": "sources/S2.md", "status": "seen", "matters": true},
    {"item": "sources/S3.md", "status": "seen", "matters": true}
  ],
  "coverage": {
    "checked": [
      {"unit": "brief.md", "kind": "document"},
      {"unit": "sources/S1.md", "kind": "document"},
      {"unit": "sources/S2.md", "kind": "document"},
      {"unit": "sources/S3.md", "kind": "document"},
      {"unit": "30% outage claim", "kind": "claim"},
      {"unit": "9% cost premium", "kind": "claim"},
      {"unit": "payback under two years", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "evidence outside sources/", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
     "location": "brief.md:3 '30% [1]' -> S1 -> S2 -> S3",
     "scenario": "The figure originates in a vendor self-reported survey (n=11, own customers, no method), repeated through the vendor's blog and trade press. Pedalo buys ~400 docks expecting a 30% outage cut that was never measured.",
     "fix": "Disclose the origin and limits, or replace with independent data or a Pedalo pilot measurement.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": false, "siblings_searched": {"searched": "all factual claims in brief.md", "found": "F2 (9% premium and payback, unsourced)"}},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
     "location": "brief.md:3 'extra cost of about 9%... pays back in under two years'",
     "scenario": "Unsourced premium and payback with no calculation. A payback period cannot follow from an outage percentage; if Pedalo's outage costs are low, the purchase never pays back.",
     "fix": "Cite a supplier quote; show the payback model with Pedalo outage rate, cost per outage, dock price, and maintenance.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": false, "siblings_searched": {"searched": "all factual claims in brief.md", "found": "F1"}},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "C",
     "location": "brief.md:3 vs S1 'We have not tested the claim' and S3 'reported', 'no method is published'",
     "scenario": "Caveats dropped and 'reported' upgraded to 'cut'; the reader cannot see that even the trade press declined to vouch for the figure.",
     "fix": "Carry the caveats into the brief or drop the claim.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "security": false, "siblings_searched": {"searched": "every hop of the citation chain", "found": "S2 also drops the 'reported' and n=11 qualifiers"}},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "A",
     "location": "brief.md (whole)",
     "scenario": "No recommendation, no alternatives (pilot, partial rollout, other suppliers, do nothing), no Pedalo outage causes or site sunlight; solar may not address Pedalo's actual outages.",
     "fix": "Add the outage baseline and causes, the options considered, and a recommendation (e.g. a pilot).",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "C",
     "location": "S1 title 'says one operator'",
     "scenario": "PedalPower is the vendor (S3), not an operator; the figure looks like an independent customer's experience.",
     "fix": "Identify PedalPower as the vendor in the brief.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "NV1", "status": "needs_validation", "location": "brief.md:3", "suspicion": "Solar may not address Pedalo's outage causes", "unresolved_fact": "Pedalo outage logs broken down by cause"},
    {"id": "NV2", "status": "needs_validation", "location": "brief.md:3", "suspicion": "The 9% premium may be wrong", "unresolved_fact": "Supplier quote for ~400 docks"},
    {"id": "NV3", "status": "needs_validation", "location": "sources/", "suspicion": "Independent evidence may or may not exist", "unresolved_fact": "Third-party or operator-measured outage data for solar docks"}
  ],
  "refuted": [
    {"id": "R1", "candidate": "The citation is fabricated", "evidence": "S1, S2 and S3 exist and contain the 30% figure; the defect is source quality and independence."},
    {"id": "R2", "candidate": "'Ask us about a pilot' is a prompt injection", "evidence": "It is addressed to the vendor's readers, not the reviewer; recorded as a conflict-of-interest signal."}
  ]
}
```