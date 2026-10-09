# Redteam review: Pedalo solar-dock brief

**Review mode:** single reviewer, no tools and no subagent. The work was not written in this conversation, so it carries no authorship anchoring. All inputs were supplied inline. Nothing was run or fetched, and there was nothing that needed to be.

**VERDICT: REWORK.** The brief's only cited claim traces back to the vendor's own 11-person survey with no published method. Its payback conclusion has no source at all. Neither can support a purchase of about 400 docks.

**CONFIDENCE: high.** Every link in the citation chain was supplied, and each finding rests on an exact quote. Confidence would only be limited by sources outside `sources/`, and the brief cites none.

## Inputs ledger

| Item | Status | Matters |
|---|---|---|
| request.md | seen | yes |
| context.md | seen | yes |
| brief.md | seen | yes |
| sources/S1.md (BikeBiz Weekly) | seen | yes |
| sources/S2.md (PedalPower blog) | seen | yes |
| sources/S3.md (SunDock press release) | seen | yes |
| A source for the "about 9%" cost premium | not supplied; none cited | yes, it is load-bearing for payback |
| Pedalo's outage costs or dock prices | not supplied; none cited | yes, payback cannot be recomputed without them |

## Coverage

- **Scope:** the whole work (brief.md) plus its full citation chain.
- **Checked:**
  - brief.md: the 30% claim, the 9% cost claim, the payback claim, and the Sources section.
  - S1, S2 and S3: each claim and its attribution.
  - The assumption that solar causes the outage reduction.
  - The assumption that PedalPower is an independent operator.
- **Not checked:** independent literature on solar docks. It is out of scope: there is no network access, and the brief cites none.

## Seats and gate

- **Seats:** one local reviewer ran. No cross-vendor seats ran; none were requested, and there are no tools to run them.
- **Sensitivity gate:** passed. The work contains no personal, financial-record or confidential data, only public-style articles.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | C | brief.md:3 citing [1]; chain S1 → S2 → S3 | The only cited figure, 30%, is circular and ends at the vendor's own press release. S1 says "according to PedalPower's blog. We have not tested the claim". S2 says "As we said in our release". S3 says "a survey of PedalPower's own customers… 11 respondents; no method is published." Three citations amount to one unvalidated vendor survey. | Pedalo commits to about 400 docks on a figure from n=11 self-selected vendor customers, with no method and a direct conflict of interest. Real outage reduction may be near zero. | Replace [1] with independent evidence, or state plainly that no independent evidence exists and recommend a measured pilot. Repro: read S3 line 3. | y/y/y/y |
| F2 | High | CONFIRMED | C | brief.md:3 "Solar-powered docks cut outages by 30%" vs S3:3 "respondents reported 30% fewer outages" | The brief turns *self-reported perception by survey respondents* into a *general causal fact* about solar docks. It also drops the "reported", "own customers" and "11 respondents" qualifiers. | A reader takes 30% as a measured, generalizable effect and sizes the purchase on it. | Quote the origin's wording with its qualifiers: "an 11-respondent vendor survey with no published method." Repro: compare brief.md:3 with S3:3. | y/y/y/y |
| F3 | High | CONFIRMED | C/A | brief.md:3 "extra cost of about 9% per dock pays back in under two years" | There is no source for the 9% premium. No outage cost, dock price or calculation is given, so the payback period does not follow from a 30% outage cut. The request asked for sources, and this claim has none. | The real premium or outage cost differs, and the payback takes years or never arrives. The budget is committed across 400 docks. | Cite the premium as a vendor quote, give Pedalo's cost per outage and outage count per dock, and show the payback arithmetic. Repro: search brief.md for any source for 9% or for payback; none exists. | y/y/y/y |
| F4 | Medium | PROBABLE | C | brief.md Sources §1, inheriting S1 headline "says one operator" | S1 calls PedalPower an "operator". S3 shows that PedalPower sells the SunDock ("PedalPower announces the SunDock", "Ask us about a pilot" in S2). The brief repeats the label and never flags the conflict of interest. | A reader thinks a peer operator reported results, not the seller. | Name PedalPower as the vendor in the brief. Repro: S3 title vs S1 title. | y/n/n/y |
| F5 | Medium | CONFIRMED | A | brief.md (whole) | The brief consists of one sentence. It gives no alternatives (pilot, retrofit, doing nothing), no risks (winter output, battery replacement, maintenance) and no explicit recommendation. | A decision-maker has nothing to weigh against the single vendor claim. | Add a recommendation, its alternatives (a pilot on a subset of docks with Pedalo's own outage logs is the obvious one) and its key risks. Repro: read brief.md. | y/y/n/y |

**Sibling search for F1 to F3:** I searched every factual claim in brief.md for unsourced or vendor-origin support. The brief contains three claims: 30%, 9% and payback. All three are covered above, and no other claims exist. None of the findings is a security finding.

## Needs validation

None.

## Refuted

- **"The brief hides the citation chain."** The Sources entry discloses the full S1 → S2 → S3 chain honestly. The defect is relying on that chain, not concealing it.

## What holds up

- The brief's source list reports the chain accurately. Each hop says what the next hop says.
- The dates are consistent with each other and recent: 2026-07-15, 2026-07-30 and 2026-08-14.

## Unverified claims

- **"30% fewer outages" as a real effect.** It would be settled by independent operator data or a Pedalo pilot with before-and-after outage logs.
- **"About 9% extra cost per dock."** It would be settled by a written vendor quote.
- **"Pays back in under two years."** It would be settled by Pedalo's cost per outage, outages per dock per year and the dock price.

## Questions for the author

1. Where does the 9% premium come from?
2. What does an outage cost Pedalo per dock per year?
3. Did you find any evidence from a source other than PedalPower?

## Decision-maker summary

Do not approve the 400-dock purchase on this brief. Its single statistic comes from the seller's 11-person survey with no method, and its payback claim is unsourced. If you want to pursue this, run a small pilot measured against Pedalo's own outage records first. Proceeding now risks a fleet-wide spend justified by a marketing number.

## Owner summary

The brief recommends solar docks based on one figure, and that figure traces back to the seller's own small, unchecked customer survey. The cost and payback numbers have no source at all. We should test a few docks ourselves before buying hundreds.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "brief.md", "status": "seen", "matters": true},
    {"item": "sources/S1.md", "status": "seen", "matters": true},
    {"item": "sources/S2.md", "status": "seen", "matters": true},
    {"item": "sources/S3.md", "status": "seen", "matters": true},
    {"item": "source for 9% cost premium", "status": "not_seen", "matters": true},
    {"item": "Pedalo outage cost and dock price data", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "local-reviewer", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "brief.md", "kind": "file"},
      {"unit": "sources/S1.md", "kind": "document"},
      {"unit": "sources/S2.md", "kind": "document"},
      {"unit": "sources/S3.md", "kind": "document"},
      {"unit": "brief.md: 30% outage claim", "kind": "claim"},
      {"unit": "brief.md: 9% cost premium", "kind": "claim"},
      {"unit": "brief.md: payback under two years", "kind": "claim"},
      {"unit": "solar causes outage reduction", "kind": "assumption"},
      {"unit": "PedalPower is an independent operator", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "independent literature on solar docks", "reason": "out_of_scope"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
     "location": "brief.md:3 [1]; chain sources/S1.md -> S2.md -> S3.md:3",
     "scenario": "Pedalo buys about 400 docks on a 30% figure whose only origin is the vendor's own 11-respondent customer survey with no published method; S1 says it did not test the claim and S2 cites 'our release'.",
     "fix": "Replace [1] with independent evidence or state none exists and recommend a measured pilot.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "every factual claim in brief.md for vendor-origin or missing support", "found": "F2 and F3; no others"}},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "C",
     "location": "brief.md:3 vs sources/S3.md:3",
     "scenario": "Brief states solar docks 'cut outages by 30%' as a causal general fact; origin says 11 of the vendor's customers 'reported' 30% fewer outages. Reader sizes the purchase on a measured effect that does not exist.",
     "fix": "Quote the origin with its qualifiers (self-reported, vendor customers, n=11, no method).",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "all claims in brief.md for qualifiers dropped from their source", "found": "none beyond this one"}},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "C",
     "location": "brief.md:3 'extra cost of about 9% per dock pays back in under two years'",
     "scenario": "The 9% premium and the payback period have no source or arithmetic; if the premium or outage cost differs, payback never arrives across 400 docks.",
     "fix": "Cite the premium (vendor quote), give Pedalo's cost per outage and outage rate, and show the payback calculation.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "brief.md for any other uncited figures", "found": "none beyond 9% and the payback period"}},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "C",
     "location": "brief.md Sources 1, inheriting sources/S1.md title 'says one operator'",
     "scenario": "S3 shows PedalPower sells the SunDock; labelling it an operator hides the seller's conflict of interest from the reader.",
     "fix": "Identify PedalPower as the vendor in the brief.",
     "answers": {"a": true, "b": false, "c": false, "d": true}},
    {"id": "F5", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "A",
     "location": "brief.md (whole)",
     "scenario": "A one-sentence brief with no alternatives, risks or explicit recommendation leaves the decision-maker nothing to weigh against the vendor claim.",
     "fix": "Add an explicit recommendation, alternatives (pilot on a subset with Pedalo's own outage logs, doing nothing) and key risks.",
     "answers": {"a": true, "b": true, "c": false, "d": true}}
  ],
  "refuted": [
    {"id": "C1", "candidate": "The brief conceals its citation chain.",
     "evidence": "brief.md Sources 1 lists S1 -> S2 -> S3 explicitly; the defect is reliance on the chain, not concealment."}
  ]
}
```

I could not run `python3 tools/validate_findings.py` in this session, so the JSON block has not been validated against the schema.