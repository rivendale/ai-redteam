# Adversarial Diagnostic Review: "Should Pedalo buy solar-powered docks?"

**Scope note:** The context asks for "Track C". The skill has no Track C. I treated the request as a claims review: I followed each citation back to where the claim starts. That falls under Track A (Facts, Logic). I reviewed only the four supplied files. Quoted findings are CONFIRMED against those files.

## Pass 1: Reconstruct

The brief makes three claims:
- Solar-powered docks cut outages by 30%.
- They cost about 9% more per dock.
- They therefore pay back in under two years.

It implies Pedalo should buy about 400 of them. For that to be correct, all of the following must hold:
- The 30% figure is a real, causal, generalizable reduction that applies to Pedalo's fleet.
- The 9% premium is accurate.
- Avoided outages are worth enough per dock-year to recover that premium within 24 months.
- No cheaper alternative achieves the same result.

Unstated assumptions:
- Pedalo's outages are mostly power-related, so solar could fix them.
- Pedalo's sites get enough sun.
- The three sources are independent of each other.

## Pass 2: Attack (Track A, claims-chain focus)

**Citation chain traced:**
- **Brief [1] → S1 (BikeBiz):** "according to PedalPower's blog. We have not tested the claim."
- **S1 → S2 (PedalPower blog):** "As we said in our release, outages fall by 30%… Ask us about a pilot."
- **S2 → S3 (press release, "PedalPower announces the SunDock"):** "In a survey of PedalPower's own customers, respondents reported 30% fewer outages after switching to SunDock. The survey had 11 respondents; no method is published."

The origin of the claim is a vendor's self-run survey of 11 of its own customers, with no published method. The two later sources only repeat it. One of them, S1, explicitly says it did not test it.

**How each step changed the claim:**
- "Respondents reported 30% fewer outages after switching" (S3) became "outages fall by 30% at solar-powered docks" (S2). That turned self-reported, uncontrolled before/after data into a general fact.
- S1 attributes the claim to "one operator". PedalPower is the vendor that sells SunDock, not an independent operator.
- The brief drops every caveat and asserts it as a causal fact: "cut outages by 30%".

**Counter-case:** There is no independent evidence that solar docks reduce outages at all. The respondents were existing customers selected by the vendor. That group is likely to suffer from survivorship and satisfaction bias. "After switching" comparisons also pick up confounds such as new hardware replacing old, which would cut outages regardless of power source. The opposite conclusion is equally consistent with the material: the premium buys nothing measurable. The brief does not survive this.

**Pre-mortem (one year later, the purchase failed):**
1. Pedalo's outages were mostly comms, mechanical, or vandalism failures, so solar did not touch them.
2. The 30% figure did not replicate outside the vendor's hand-picked respondents.
3. Payback slipped because the 9% premium excluded installation, panel maintenance, or shaded sites.

**Alternatives never considered:**
- A pilot. The vendor itself offers one ("Ask us about a pilot").
- A partial rollout at sun-exposed or high-outage sites.
- Fixing the actual top causes of outages.
- Doing nothing.

**Bias:** The brief anchors on a vendor's marketing number and presents it as a finding. Its confidence ("pays back in under two years") is not earned by any evidence in the material.

## Pass 3: Self-check

Every finding below is tied to a quoted line. I did not assume the 9% figure is wrong, only that it is unsourced. The most serious problem I might still be missing is whether Pedalo has its own outage data that would independently support or refute the case. That would live outside this material, and the brief does not mention it.

---

**VERDICT: REJECT.** The brief's only evidence traces to a vendor's 11-person self-survey with no method, laundered through two repeaters into a causal fact. Its payback conclusion has no calculation or source behind it.

**CONFIDENCE IN VERDICT: high.** The chain is fully traceable within the supplied files. The only limit is that Pedalo's own outage and cost data was not provided.

## Findings

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | brief.md "cut outages by 30% [1]"; origin S3 | The sole evidence is a vendor survey of 11 of its own customers with "no method is published". It is presented as an established causal effect. | Pedalo commits to about 400 docks on a figure that may not exist outside the vendor's sample. The premium is spent with no outage reduction. | Remove the claim as stated. Get independent data (third-party study, other operators' records) or run a controlled pilot that compares solar and grid docks at matched Pedalo sites. |
| 2 | Critical | CONFIRMED | brief.md Sources [1]; S1→S2→S3 | Circular sourcing. All three sources are one claim from one interested party (PedalPower). S1 says "We have not tested the claim." The brief lists them as if they corroborate each other. | A reader sees a press outlet cited and assumes independent verification that never happened. | Cite S3 as the origin and describe it accurately (vendor, n=11, self-reported, no method). Disclose that S1 and S2 add no evidence. |
| 3 | Critical | CONFIRMED | brief.md "the extra cost of about 9% per dock pays back in under two years" | The 9% premium has no source. The payback has no calculation: no dock price, no outage cost, no outage baseline, no install or maintenance costs. "So" asserts a conclusion that does not follow from the cited premise. | The real premium or the per-outage cost differs, and payback stretches to many years or never arrives. | Show the arithmetic: premium per dock (sourced quote) ÷ (Pedalo's baseline outages per dock-year × share that is power-related × reduction × cost per outage). Test sensitivity at 0%, 10% and 30% reduction. |
| 4 | High | CONFIRMED | S1 headline "says one operator"; brief reuse | PedalPower is the vendor that announces SunDock (S3), not an independent operator. The framing understates the conflict of interest. | A decision-maker gives the number operator-level credibility it does not have. | State plainly that the source is the manufacturer's own marketing. |
| 5 | High | CONFIRMED | S3 "respondents reported… after switching" vs. brief "cut" | Self-reported, uncontrolled before/after data was upgraded to a causal claim. Confounds such as new hardware, survey selection and recall bias are ignored. | The outage drop came from replacing aging docks, which any new dock would achieve. Pedalo pays a premium for the solar feature alone. | Compare solar docks against new non-solar docks, not against old ones. |
| 6 | High | PROBABLE | brief.md (whole) | The work drifted from the request. It asked for a brief on *whether* to buy. The work is one sentence asserting yes, with no alternatives (pilot, partial rollout, do nothing), no risks, and nothing on site suitability or what causes Pedalo's outages. | Leadership approves a fleet-wide, hard-to-reverse purchase without seeing the cheaper option of piloting first. | Add options, risks, site and sun suitability, Pedalo's outage-cause breakdown, and a recommendation scaled to the evidence (e.g. a pilot). |
| 7 | Medium | CONFIRMED | brief.md Sources | Caveats in the sources were dropped: "We have not tested the claim" (S1), "11 respondents; no method is published" (S3). | A reader who never opens the sources gets a materially more confident picture than the sources support. | Carry the caveats into the brief text next to the claim. |

## What holds up

- The citation trail is transparent. The brief names all three hops, which is what made this trace possible.
- The dates are internally consistent: press release 2026-07-15, blog 2026-07-30, article 2026-08-14.
- The 30% figure is quoted consistently across all three sources. It was not distorted numerically, only in its meaning.

## Unverified claims

- **"About 9% extra cost per dock":** no source. Confirm with a written vendor quote for 400 units, including installation.
- **"Pays back in under two years":** confirm with the calculation in Finding 3, using Pedalo's own outage logs and cost per outage.
- **That solar addresses Pedalo's outage causes:** confirm with Pedalo's outage root-cause data.
- **That the 30% generalizes:** confirm with independent studies or a pilot. The vendor's survey method and raw data would at least let the 30% be assessed.

## Questions for the author

1. Where does the 9% figure come from, and what does it include?
2. What share of Pedalo's current outages are power-related, and what does an outage cost Pedalo?
3. Did you find any source on solar docks that does not trace back to PedalPower?
4. Was a pilot considered, and why was it not recommended?

## Decision-maker summary

Do not approve the 400-dock purchase on this brief. Its only evidence is the manufacturer's own survey of 11 customers, repeated by two outlets that did not check it, and its payback figure has no calculation. If you want to pursue this, run a matched pilot at a few sites against Pedalo's own outage data. The risk of proceeding anyway is paying a fleet-wide premium for a benefit that may not exist.

## Owner summary

The case for buying solar docks rests on a single claim from the company that sells them, based on a small survey of its own customers with no published method. The cost-saving promise in the brief is not backed by any numbers. A small trial at a few locations would show whether the docks actually help before committing to a large purchase.

```json
{
  "verdict": "REJECT",
  "findings": [
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "brief.md 'Solar-powered docks cut outages by 30% [1]'; origin sources/S3.md",
      "scenario": "The sole evidence is a vendor's self-reported survey of 11 of its own customers with no published method; Pedalo buys ~400 docks on a figure that may not hold outside that sample and pays the premium for no outage reduction.",
      "fix": "Remove or restate the claim accurately; obtain independent data or run a controlled pilot comparing solar and grid docks at matched Pedalo sites."
    },
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "brief.md Sources [1]; chain S1 -> S2 -> S3",
      "scenario": "Circular sourcing: all three sources are one PedalPower claim, and S1 states 'We have not tested the claim'; readers assume the press citation means independent verification.",
      "fix": "Cite S3 as the origin, describe it as vendor marketing (n=11, self-reported, no method), and disclose that S1 and S2 add no evidence."
    },
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "brief.md 'the extra cost of about 9% per dock pays back in under two years'",
      "scenario": "The 9% premium is unsourced and the payback has no calculation (no dock price, outage baseline, or cost per outage); actual payback may be many years or never.",
      "fix": "Source the premium from a written quote and show the payback arithmetic using Pedalo's outage data, with sensitivity at 0%, 10% and 30% reduction."
    },
    {
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "location": "sources/S1.md headline 'says one operator'",
      "scenario": "PedalPower is the vendor announcing SunDock (S3), not an independent operator; the decision-maker gives the number operator-level credibility.",
      "fix": "State in the brief that the source is the manufacturer's own marketing."
    },
    {
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "location": "sources/S3.md 'respondents reported... after switching' vs brief.md 'cut outages'",
      "scenario": "Uncontrolled self-reported before/after data is presented as causal; the drop may come from replacing old hardware, so Pedalo pays a premium for the solar feature alone.",
      "fix": "Compare solar docks against new non-solar docks in a pilot rather than against old docks."
    },
    {
      "severity": "High",
      "evidence_level": "PROBABLE",
      "location": "brief.md (entire document)",
      "scenario": "The request asked whether to buy; the brief is one sentence asserting yes with no alternatives, risks, or site analysis, so leadership approves an irreversible fleet-wide purchase without seeing the pilot option.",
      "fix": "Add options (pilot, partial rollout, do nothing), risks, site suitability, and Pedalo's outage-cause breakdown, and scale the recommendation to the evidence."
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "brief.md Sources; caveats in S1 and S3",
      "scenario": "Source caveats ('We have not tested the claim'; '11 respondents; no method is published') are dropped, so readers who do not open the sources get an overconfident picture.",
      "fix": "Carry the caveats into the brief text next to the claim."
    }
  ]
}
```