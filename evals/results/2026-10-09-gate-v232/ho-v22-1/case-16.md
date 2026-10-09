VERDICT: **REWORK**. The brief's only evidence for buying 400 docks is a vendor's own 11-person survey with no published method, relayed through two re-tellings, and its payback claim has no source or inputs at all.

CONFIDENCE: **high** on the findings, because every cited source was supplied inline and the chain is short. Limits: a single reviewer with no tools and no subagent (independent of the author, but no second seat). Pedalo's own cost and outage data were not supplied.

INPUTS LEDGER:
- **Seen:** request.md, context.md, brief.md, sources/S1.md, sources/S2.md, sources/S3.md (all inline).
- **Not seen:** a source for the "about 9% per dock" premium (matters: it feeds the payback). Pedalo's outage rate, cost per outage, dock price and site conditions (matters: payback can't be computed without them). Any independent outage data on solar docks (matters: it is the only thing that could rescue the 30% figure).

COVERAGE:
- **Checked:** brief.md (both claims, the source list); the S1 → S2 → S3 chain, read to where the 30% starts; the 9% claim; the payback claim; fit to the request.
- **Not checked:** external sources (no network, none cited); the SunDock product spec or price (not supplied).

SEATS AND GATE: one local reviewer ran (no tools, no subagent). The material isn't sensitive: it's public articles and press releases. No cross-vendor seats, since the user didn't request them and none were available.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | C | brief.md line 3 "Solar-powered docks cut outages by 30% [1]"; origin in sources/S3.md | The brief states as measured fact what the origin calls a perception survey by the seller. S3: "In a survey of PedalPower's own customers, respondents reported 30% fewer outages after switching to SunDock. The survey had 11 respondents; no method is published." PedalPower makes the SunDock ("PedalPower announces the SunDock"). S2 is PedalPower citing itself ("As we said in our release"). S1 relays S2 and says "We have not tested the claim." Three documents, one interested origin. The brief also drops "reported", "11 respondents", "no method" and "own customers". | Pedalo commits to about 400 docks expecting a 30% outage cut. The figure is self-reported, n=11, selected by the vendor, with no baseline or control, so the real effect could be zero. The spend is then justified by nothing. | Restate the claim at its true strength: "the maker reports that 11 of its own customers said…". Name PedalPower as the SunDock vendor. Cite S3 as the origin. Get independent outage data or run a Pedalo pilot before relying on it. Reproduction: follow [1] → S1 → S2 → S3 and compare S3's sentence with the brief's. | a✓ b✓ c✓ d✓ |
| F2 | Critical | CONFIRMED | C/A | brief.md line 3 "the extra cost of about 9% per dock pays back in under two years" | The 9% premium has no citation; no source in sources/ mentions cost. The payback figure has no inputs: dock price, outage frequency and cost per outage are all absent. The "so" doesn't follow, because a percentage cut in outages implies no payback period without a cost of outage. The request said "Cite sources". | Decision-makers read "under two years" as a computed result. If Pedalo's outages are rare or cheap, payback may never come. | Cite the 9% premium. Show the arithmetic: premium per dock ÷ (baseline outages per dock-year × reduction × cost per outage). Use Pedalo's own figures, or delete the claim. Reproduction: try to recompute "<2 years" from the brief's contents; it cannot be done. | a✓ b✓ c✓ d✓ |
| F3 | Medium | CONFIRMED | A | brief.md (whole) | The request asks *whether* Pedalo should buy. The brief gives no explicit recommendation, no alternatives (pilot, partial rollout, grid upgrade, doing nothing), no risks (sunlight at Pedalo's sites, battery life, maintenance) and no Pedalo-specific facts. | A reader takes one sentence as a buy recommendation for a 400-unit purchase without weighing a cheap pilot. | Add a recommendation, the alternatives and their costs, the key risks, and what data would change the answer. The obvious first step is a small pilot that measures outages against current docks. | a✓ b✓ c✗ d✓ |

## NEEDS VALIDATION
- **S1:** whether any independent study of solar-dock outage rates exists. *Settled by:* a non-vendor dataset or study (none supplied; no network).
- **S2:** whether 9% is the real SunDock price premium for Pedalo's configuration. *Settled by:* a vendor quote or price list.

## REFUTED
- **R1:** "The brief misquotes its cited source." S1 says, word for word, "Solar-powered docks cut outages by 30%". The brief matches [1]. The distortion happens between S3 and S1, and the brief inherits it (covered by F1).
- **R2:** "The citation chain is broken or unopenable." All three links resolve to supplied files, and each points to the next as described in the brief's source list.

## WHAT HOLDS UP
The source list is transparent: it discloses the full S1 → S2 → S3 chain, which is what made the provenance traceable. The 30% figure is reproduced consistently across all three documents, and all sources are recent (July–August 2026).

## UNVERIFIED CLAIMS
- **"About 9% extra cost per dock":** confirm with a supplier quote.
- **"Pays back in under two years":** confirm by computing with Pedalo's outage logs and cost per outage.
- **"30% fewer outages" as a real-world effect:** confirm with independent data or a controlled Pedalo pilot.

## QUESTIONS FOR THE AUTHOR
1. Where does the 9% figure come from?
2. What outage rate and cost per outage did you assume for the payback?
3. Is there any evidence for the 30% figure that doesn't originate with PedalPower?

## DECISION-MAKER SUMMARY
The brief's sole evidence is the seller's own 11-respondent survey with no method, and its payback claim is unsourced and can't be computed. Don't approve the 400-dock purchase on this brief; commission a short pilot or independent data plus a payback calculation using Pedalo's figures. Proceeding anyway risks spending a 9% premium on 400 docks for a benefit that may not exist.

## OWNER SUMMARY
The case for solar docks rests on a claim that traces back to the company selling them, based on a tiny survey of its own customers with no explanation of how it was done. The promised two-year payback has no numbers behind it. Before buying, we should test a few docks ourselves and do the cost math with our own figures.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "brief.md", "status": "seen", "matters": true},
    {"item": "sources/S1.md", "status": "seen", "matters": true},
    {"item": "sources/S2.md", "status": "seen", "matters": true},
    {"item": "sources/S3.md", "status": "seen", "matters": true},
    {"item": "source for 9% per-dock cost premium", "status": "not_seen", "matters": true},
    {"item": "Pedalo outage rate, cost per outage, dock price", "status": "not_seen", "matters": true},
    {"item": "independent solar-dock outage data", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "local-reviewer-no-tools", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Public articles and press releases; no personal or confidential data."},
  "coverage": {
    "checked": [
      {"unit": "brief.md", "kind": "file"},
      {"unit": "brief.md: 30% outage claim", "kind": "claim"},
      {"unit": "brief.md: 9% cost premium", "kind": "claim"},
      {"unit": "brief.md: payback under two years", "kind": "claim"},
      {"unit": "sources/S1.md", "kind": "file"},
      {"unit": "sources/S2.md", "kind": "file"},
      {"unit": "sources/S3.md", "kind": "file"},
      {"unit": "fit to original request", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "external sources and SunDock pricing", "reason": "no network access; not supplied"},
      {"unit": "Pedalo operational data", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
     "location": "brief.md line 3; origin sources/S3.md",
     "scenario": "Pedalo buys about 400 docks expecting a 30% outage cut; the figure is the vendor's own self-reported survey of 11 customers with no method, relayed via PedalPower's blog and an outlet that did not test it, so the real effect may be zero.",
     "fix": "Restate at true strength, name PedalPower as the SunDock vendor, cite S3 as origin, and obtain independent data or run a Pedalo pilot before relying on it.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Follow [1] to S1, S2, S3; compare S3 ('respondents reported 30% fewer outages... 11 respondents; no method is published') with the brief's 'cut outages by 30%'."},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
     "location": "brief.md line 3: 'about 9% per dock pays back in under two years'",
     "scenario": "Decision-makers treat 'under two years' as computed; with no cited premium, outage frequency or outage cost, payback may never occur if Pedalo's outages are rare or cheap.",
     "fix": "Cite the 9% premium and show payback = premium per dock / (baseline outages per dock-year x reduction x cost per outage) using Pedalo data, or remove the claim.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Attempt to recompute the payback from the brief and sources; no cost or outage-cost inputs exist in any supplied file."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "A",
     "location": "brief.md (whole)",
     "scenario": "A one-sentence brief is read as a buy recommendation for 400 docks without weighing a pilot, alternatives or site-specific risks.",
     "fix": "Add an explicit recommendation, alternatives (pilot, partial rollout, do nothing), risks (sunlight, battery life, maintenance) and the data that would change the answer.",
     "answers": {"a": true, "b": true, "c": false, "d": true}},
    {"id": "S1", "status": "needs_validation", "track": "C", "location": "brief.md line 3",
     "suspicion": "No independent evidence supports a 30% outage reduction.",
     "unresolved_fact": "Whether any non-vendor study or dataset of solar-dock outage rates exists."},
    {"id": "S2", "status": "needs_validation", "track": "C", "location": "brief.md line 3",
     "suspicion": "The 9% premium may not reflect Pedalo's actual price.",
     "unresolved_fact": "A supplier quote for SunDock versus current docks at Pedalo's volume."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "The brief misquotes its cited source.",
     "evidence": "S1 says verbatim 'Solar-powered docks cut outages by 30%'; the distortion occurs between S3 and S1 and is covered by F1."},
    {"id": "R2", "candidate": "The citation chain is broken or unopenable.",
     "evidence": "S1, S2 and S3 are all supplied and each points to the next as the brief's source list states."}
  ]
}
```