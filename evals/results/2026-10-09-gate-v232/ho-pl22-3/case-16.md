# Adversarial Diagnostic Review: "Should Pedalo buy solar-powered docks?"

**Scope note:** The context asks for "Track C (claims review)". The skill defines Tracks A, B and R, not C. I applied **Track A** (decisions and analysis) and followed every citation back to its origin, as the context instructs. Track R does not apply because this is an internal brief, not customer-facing wording. Only the material provided was examined: `brief.md` and `sources/S1–S3.md`.

## Pass 1: Reconstruct

The brief claims that solar-powered docks reduce outages by 30% and that the roughly 9% extra cost per dock pays back in under two years. It implies, without saying so outright, that Pedalo should buy them, at a scale of about 400 docks. For that to be correct, all of the following must be true:

- (a) The 30% figure is a real, measured, causal effect.
- (b) The figure applies to solar docks in general and to Pedalo's own conditions.
- (c) The 9% cost premium is accurate.
- (d) Fewer outages save enough money to recover that premium within two years.

Several assumptions are unstated. Pedalo's baseline outage rate and the cost of each outage are similar to the surveyed customers'. "Outage" means the same thing in both places. The source of the figure is independent of the seller.

## Pass 2: Attack (Track A, citation chain traced)

**How the 30% figure travels:**
- **S1** (BikeBiz, 2026-08-14) says "Solar-powered docks cut outages by 30%, according to PedalPower's blog. **We have not tested the claim.**"
- **S2** (PedalPower blog, 2026-07-30) says "As we said in our release, outages fall by 30% at solar-powered docks. **Ask us about a pilot.**"
- **S3** (PedalPower press release, 2026-07-15) is where the number starts: "In a survey of PedalPower's **own customers**, respondents **reported** 30% fewer outages after switching to **SunDock**. The survey had **11 respondents; no method is published.**"

So the one number in the brief comes from a self-reported survey of 11 of the vendor's own customers, with no published method. It passed through the vendor's own blog and then a trade article that explicitly says it did not check the claim. Along the way, the claim grew in three ways:
- "respondents reported" became "outages fall"
- "SunDock" became "solar-powered docks" in general
- "after switching" became a causal "cut"

**Positive control for absence checks:** I searched all three sources for "30%" and found it in each, which shows the search works. The same check for any cost, "9%", price, "payback", "two years" or any outage cost finds **nothing in any source**.

**Logic:** Even if the 30% figure were true, payback cannot be calculated from the information given. It requires the baseline outage rate, the cost per outage (lost rides, repair callouts), the dock price, and the premium. None of these appear anywhere.

**Counter-case:** A vendor sample of 11 happy customers is exactly what selection bias produces. Customers who switched and were satisfied are the ones who answer a survey. Outages may also have fallen for other reasons, such as new hardware or the season. The strongest opposite conclusion is: "We have no evidence about solar docks yet; run a small pilot measured against our own outage logs." The brief does not survive this, because it contains no independent evidence.

**Pre-mortem (one year on, the purchase failed):**
1. The real reduction in outages was small or zero at Pedalo's sites, because of shading, winter daylight, or a different definition of "outage".
2. The 9% premium was wrong, or there were installation and battery-replacement costs nobody counted.
3. The two-year payback was never modelled, so the 400 docks never earned back their cost.

**Alternatives never considered:** doing nothing, a 10–20 dock pilot, competing products, fixing the actual causes of Pedalo's current outages, or a partial rollout at the docks with the most outages.

**Incentives:** The only underlying source is the vendor, which is openly selling ("Ask us about a pilot"). The S1 headline calls PedalPower "one operator", but S3 shows PedalPower *announces and sells* SunDock. The brief does not mention this conflict of interest.

## Pass 3: Self-check

I dropped a possible finding about the brief's length, because "brief" was requested; I mention it only as part of the missing analysis in finding 6. I downgraded the "operator vs vendor" point to PROBABLE, since PedalPower could be both. The most serious thing I might still be missing is whether Pedalo has internal outage or cost data that the author used but did not cite. If it exists, the payback figure might be recoverable, but as written it is unsupported.

---

**VERDICT: REJECT.** The brief's only evidence is the seller's own unverified survey of 11 customers, passed through two more write-ups, and its cost and payback figures have no source at all. It cannot support buying 400 docks.

**CONFIDENCE IN VERDICT: High.** All three sources were provided and read in full. The only limit is that I cannot rule out uncited internal Pedalo data behind the 9% and two-year figures.

### FINDINGS

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | brief.md line 3, "cut outages by 30% [1]"; origin S3 | The figure comes from a vendor survey of its own customers: 11 respondents, self-reported, no method. The brief states it as established fact. | Pedalo buys 400 docks expecting 30% fewer outages; the real effect at its sites is small or zero. | Cite S3 directly with its limits stated. Require independent data or a measured Pedalo pilot before deciding. |
| 2 | Critical | CONFIRMED | brief.md line 3, "extra cost of about 9% per dock pays back in under two years" | No source contains any cost, premium, price or payback figure. I checked all three; "30%" was found in each as a positive control. | The purchase is approved on a payback figure nobody calculated; the real cost or payback is worse. | Source the 9% premium (quote or price list). Build a payback model from the baseline outage rate, cost per outage, and dock price and premium. |
| 3 | High | CONFIRMED | Citation [1], chain S1 → S2 → S3 | Three citations are one source, the vendor. S1 says "We have not tested the claim"; S2 only repeats "our release". This looks like corroboration but adds no independent evidence. | A reader sees a trade publication and assumes independent confirmation. | Count sources by origin, not by link. State "single vendor source". |
| 4 | High | CONFIRMED | S3 → S2 → brief | The claim grew at each step: "respondents reported" became "outages fall", "SunDock" became "solar-powered docks", and "after switching" became a causal "cut". | Pedalo generalises a result from one product to any solar dock it buys, and treats correlation as cause. | Quote S3's exact wording and limit the claim to SunDock and self-report. |
| 5 | High | CONFIRMED | brief.md as a whole; S2 "Ask us about a pilot"; S3 | The brief does not disclose that the only source is the seller. | The decision-maker under-weights an obvious conflict of interest. | Add a source-independence and conflict note. |
| 6 | Medium | CONFIRMED | brief.md as a whole | The request was for a brief on *whether* to buy. The work gives one sentence with no alternatives (pilot, do nothing, other vendors), no Pedalo baseline data, no risks (climate, maintenance, battery life), and no explicit recommendation. | The decision is made without considering cheaper or reversible options. | Add options including a pilot, plus risks and an explicit recommendation with conditions. |
| 7 | Medium | CONFIRMED | S3 "30% fewer outages" | "Outage" is undefined and there is no baseline rate. A 30% *relative* drop from an unknown baseline cannot be turned into savings. | A 30% drop from a low baseline saves almost nothing. | Get the outage definition and absolute rates. Compare with Pedalo's own logs. |
| 8 | Low | PROBABLE | S1 headline "says one operator" | PedalPower is described as an operator, but S3 shows it is the SunDock vendor. | A reader mistakes vendor marketing for an operator's field experience. | Describe PedalPower as the vendor in the brief. |

### WHAT HOLDS UP
- The brief's source list describes the citation chain accurately (S1 cites S2, which cites S3), so a reader *can* trace it.
- The dates are consistent: the release is dated 07-15, the blog 07-30, the article 08-14.
- The 30% number is quoted consistently at every step. It is the meaning that drifted, not the number.

### UNVERIFIED CLAIMS
- **"Extra cost of about 9% per dock":** confirm with a vendor quote or price list for about 400 units.
- **"Pays back in under two years":** confirm with a model using Pedalo's outage rate, cost per outage, and maintenance and battery costs.
- **The 30% reduction itself:** confirm with the survey data and method from PedalPower, independent studies, or a Pedalo pilot with before-and-after outage logs.
- **Whether PedalPower is an operator or only a vendor:** confirm from company information.

### QUESTIONS FOR THE AUTHOR
1. Where do the 9% premium and the two-year payback come from? Is there an uncited calculation or quote?
2. Is there any source for the outage reduction that does not trace back to PedalPower?
3. What are Pedalo's current outage rate and cost per outage?

### DECISION-MAKER SUMMARY
Do not approve the 400-dock purchase on this brief. Its only evidence is the vendor's own unverified 11-person survey, and its cost and payback figures have no source. Commission a small measured pilot and a proper payback model first. Proceeding now risks a large spend on an effect and a return that nobody has shown.

### OWNER SUMMARY
The brief recommending solar docks rests on a single claim that traces back to the company selling them, based on an informal survey of eleven of its own customers. The cost and payback numbers in the brief do not appear in any of its sources. Before buying around 400 docks, test a small number on our own network and check the real costs.

```json
{
  "verdict": "REJECT",
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "location": "brief.md line 3 '30% [1]'; origin sources/S3.md", "scenario": "Figure is a self-reported vendor survey of 11 own customers with no method; Pedalo buys 400 docks expecting 30% fewer outages and sees little or none.", "fix": "Cite S3 directly with its limits; require independent data or a measured Pedalo pilot before deciding."},
    {"severity": "Critical", "evidence_level": "CONFIRMED", "location": "brief.md line 3 '9% per dock pays back in under two years'", "scenario": "No source contains any cost or payback figure (positive control: '30%' found in all three); purchase approved on an uncalculated return.", "fix": "Source the premium from a quote; build a payback model from baseline outages, cost per outage, dock price and premium."},
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "Citation [1], chain S1->S2->S3", "scenario": "Three links are one vendor source; S1 states it did not test the claim; reader mistakes repetition for corroboration.", "fix": "Count sources by origin; label as single vendor source."},
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "S3 -> S2 -> brief.md wording", "scenario": "'Respondents reported... after switching to SunDock' became 'solar-powered docks cut outages'; Pedalo generalises one product's self-report to a causal effect for any solar dock.", "fix": "Quote S3 exactly and scope the claim to SunDock self-reports."},
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "brief.md; S2 'Ask us about a pilot'; S3", "scenario": "Vendor conflict of interest undisclosed; decision-maker under-weights marketing as evidence.", "fix": "Add a source-independence and conflict-of-interest note."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "brief.md whole", "scenario": "No alternatives (pilot, do nothing, other vendors), risks or explicit recommendation; an irreversible large purchase is made without considering a cheaper reversible path.", "fix": "Add options, risks and a conditional recommendation, e.g. pilot first."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "S3 '30% fewer outages'", "scenario": "Outage undefined and baseline unknown; a 30% relative drop from a low baseline yields negligible savings.", "fix": "Obtain the outage definition and absolute rates; compare with Pedalo's logs."},
    {"severity": "Low", "evidence_level": "PROBABLE", "location": "S1 headline 'says one operator'", "scenario": "PedalPower is the SunDock vendor per S3; readers take vendor marketing as operator field experience.", "fix": "Describe PedalPower as the vendor in the brief."}
  ]
}
```