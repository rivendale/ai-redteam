# Adversarial Diagnostic Review: "Should Pedalo buy solar-powered docks?"

**Note on scope:** The context asks for "Track C" (claims review). The skill has no Track C, so I applied the closest equivalent: Track A (facts, logic, assumptions), with every citation followed back to where its claim started. I had no tools in this session. Every finding comes from reading the four files supplied.

## Pass 1: Reconstruct

The brief makes three claims:
1. Solar docks cut outages by 30%.
2. They cost about 9% more per dock.
3. They therefore pay back in under two years.

It implies Pedalo should buy about 400 of them. For that to hold, all of the following must be true:
- The 30% figure is a real, causal, general effect that would transfer to Pedalo's fleet.
- The 9% premium is accurate.
- Fewer outages convert into enough money to recover 9% within two years.
- The cited sources are independent and support the claim as stated.

**Unstated assumptions:**
- Pedalo's baseline outage rate and the cost of each outage are high enough to matter.
- Pedalo's sites get enough sun.
- Battery life and maintenance costs don't erase the savings.

## Pass 2: Attack (citation tracing)

| Hop | Source | What it actually says | What it adds |
|---|---|---|---|
| Brief [1] | S1, BikeBiz Weekly | "according to PedalPower's blog. **We have not tested the claim.**" | Nothing. It repeats the claim and disclaims it. The headline calls PedalPower "one operator", but PedalPower is the vendor. |
| S1 → | S2, PedalPower blog | "As we said in our release, outages fall by 30%… **Ask us about a pilot.**" | Nothing. It is vendor marketing, and it drops the survey qualifier. |
| S2 → | S3, PedalPower press release | "In a survey of PedalPower's own customers, respondents **reported** 30% fewer outages… **11 respondents; no method is published.**" | This is the origin of the claim. |

**Where the claim starts:** an 11-person, self-reported, before-and-after survey. The vendor ran it on its own customers and published no method. Three citations collapse into one source with an interest in the answer.

Each hop strips away a caveat:
- S3's "respondents reported fewer outages after switching" becomes S2's "outages fall by 30%".
- S1 repeats that as an untested claim.
- The brief turns it into a general causal fact: "cut outages by 30%".

**Positive control:** All three sources do contain the 30% figure, which shows my reading picks up the claims that are present. None of them mentions cost, price, a 9% premium, payback, or outage cost. Those zeros are real.

## Pass 3: Self-check

**Dropped:** a speculative concern about the timing between source dates. The dates are internally consistent (S3 07-15, S2 07-30, S1 08-14).

**Most serious thing I might still miss:** Pedalo's own outage data. Most outages may have causes unrelated to power, such as vandalism, connectivity, or mechanical locks. If so, even a true 30% effect on power outages would be irrelevant. That would make the brief wrong even if its evidence were good.

---

**VERDICT: REJECT.** Every load-bearing claim traces either to a vendor's 11-person unmethodical survey or to nothing at all, and the payback conclusion does not follow even if those claims were true.

**CONFIDENCE IN VERDICT: High.** The sources were supplied in full and the defects are visible in their text. The one limit is that I can't see Pedalo's internal data, and that could only make the case weaker, not rescue it.

## Findings, ordered by severity

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | brief.md line 3 "cut outages by 30% [1]"; S3 | The 30% claim originates in a vendor press release: 11 self-selected customers, self-reported, no method. The brief states it as a general causal fact. | Pedalo buys 400 docks expecting 30% fewer outages. The real effect is unknown and may be zero, or limited to the vendor's happiest customers. | Remove the figure or state its true basis. Get independent data: outage logs from non-customer operators, a published study, or a Pedalo-run controlled pilot. |
| 2 | Critical | CONFIRMED | brief.md "extra cost of about 9% per dock" | The figure is unsourced. It appears in none of S1–S3. | The premium is wrong. Across 400 docks, the budget and the payback both fail. | Cite a vendor quote or price list for 400 units, including installation, batteries and maintenance. |
| 3 | Critical | CONFIRMED | brief.md "pays back in under two years" | No calculation and no inputs. Payback needs Pedalo's baseline outage rate, cost per outage, dock price, and lifetime operating cost, and none is given. "So" asserts an inference that the premises cannot produce. | The payback is far longer than two years, or never arrives, and the purchase is irreversible at that scale. | Show the model: (baseline outages × 30% or the verified effect × cost per outage) against (premium + extra maintenance), with ranges. |
| 4 | High | CONFIRMED | brief.md Sources [1]; S1 headline "says one operator" | Circular sourcing presented as a chain. The press, blog and release are all the vendor. S1 mislabels the vendor as an "operator", and the brief doesn't flag it. | A reader sees three publications and assumes corroboration that doesn't exist. | Label the source as vendor-originated. Count it as one interested source and seek independent corroboration. |
| 5 | High | CONFIRMED | S1 "We have not tested the claim"; S3 "no method is published" | The brief omits caveats that its own sources state outright. | The decision-maker never learns that the cited outlet disclaimed the claim. | Carry the caveats into the brief, or drop the source. |
| 6 | High | CONFIRMED | brief.md (entire) | Drift: the brief has no explicit recommendation and no alternatives. It omits doing nothing, a small pilot (which the vendor itself offers in S2), other vendors, and fixing the actual causes of outages. There is no counter-case and no risks. | Pedalo commits to all 400 when a 10–20 dock pilot would settle the question cheaply. | Add a recommendation with options compared. A staged pilot with success criteria is the obvious low-regret path. |
| 7 | Medium | PROBABLE | brief.md (missing) | The brief ignores fit factors for Pedalo: sunlight at its sites, seasonal and winter performance, battery degradation and replacement cycle, and whether Pedalo's outages are power-related at all. | The docks underperform in shaded or winter sites, or the outages have non-power causes. | Pull Pedalo's outage logs by cause and site. Get the battery spec and replacement cost. |

## What holds up
- The brief discloses its citation chain honestly rather than citing S3 as if it were independent. That disclosure is what made the tracing possible.
- The question itself is reasonable, and the 30% figure does appear verbatim in all three sources.

## Unverified claims
- **"About 9% extra cost":** needs a vendor quote at a 400-unit volume.
- **"Payback under two years":** needs a cost model built from Pedalo's outage and revenue data.
- **"30% fewer outages" as a real effect:** needs independent outage data, or a controlled pilot with a defined outage metric.

## Questions for the author
1. Where does the 9% figure come from?
2. What are Pedalo's current outage rate and cost per outage, and what share of outages are power-related?
3. Was a pilot considered, and why not recommend one before committing to 400 docks?

## Decision-maker summary
Do not buy 400 docks on this brief. Its only evidence is the vendor's own 11-person survey, and its cost and payback figures have no source at all. If solar docks remain of interest, run a small, measured pilot against Pedalo's own outage data before any fleet-wide commitment.

## Owner summary
The brief's main evidence comes from the seller itself: a small, informal survey of eleven of its own customers. The cost and payback numbers have no source behind them. Before spending on hundreds of docks, try a handful first and measure whether outages actually drop.

```json
{
  "verdict": "REJECT",
  "findings": [
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "brief.md line 3 'cut outages by 30% [1]'; sources/S3.md",
      "scenario": "The 30% figure traces to a vendor press release: a self-reported survey of 11 of PedalPower's own customers with no published method, restated in the brief as a general causal fact. Pedalo buys 400 docks expecting an effect that is unverified and may be zero.",
      "fix": "Remove or accurately qualify the figure; obtain independent outage data or run a controlled Pedalo pilot."
    },
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "brief.md 'extra cost of about 9% per dock'",
      "scenario": "Figure appears in none of the sources; if wrong, the budget and payback for 400 docks are wrong.",
      "fix": "Cite a volume quote including installation, batteries and maintenance."
    },
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "brief.md 'pays back in under two years'",
      "scenario": "No calculation or inputs (baseline outages, cost per outage, lifetime costs); payback may be far longer or never, on an irreversible fleet-scale purchase.",
      "fix": "Show a payback model with Pedalo's data and ranges."
    },
    {
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "location": "brief.md Sources [1]; sources/S1.md headline 'says one operator'",
      "scenario": "All three citations are a single vendor source; S1 mislabels the vendor as an operator, creating false appearance of corroboration.",
      "fix": "Label as one vendor-originated source and seek independent corroboration."
    },
    {
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "location": "sources/S1.md 'We have not tested the claim'; sources/S3.md 'no method is published'",
      "scenario": "Brief omits caveats its own sources state, so the decision-maker is misled about evidence strength.",
      "fix": "Carry the caveats into the brief or drop the source."
    },
    {
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "location": "brief.md (entire)",
      "scenario": "No explicit recommendation, no alternatives (do nothing, pilot, other vendors, non-power outage causes), no risks; Pedalo commits to 400 docks when a small pilot would settle the question.",
      "fix": "Add a recommendation comparing options; propose a staged pilot with success criteria."
    },
    {
      "severity": "Medium",
      "evidence_level": "PROBABLE",
      "location": "brief.md (missing analysis)",
      "scenario": "Ignores site sunlight, winter performance, battery degradation and whether Pedalo's outages are power-related; docks may underperform or address the wrong cause.",
      "fix": "Analyse Pedalo outage logs by cause and site; obtain battery specs and replacement costs."
    }
  ]
}
```