VERDICT: try. The paper targets a real risk for goal 3 (broken `{0}` or `%s` placeholders in machine-translated strings). First check whether our own Crowdin output actually has this problem before borrowing anything.

WHAT IT IS: Paper, preprint id 2609.07712, "Placeholder-safe machine translation for game strings", posted 2026-09-26. It was read from a saved snapshot captured 2026-10-08 (work/snapshot.md and work/meta.json), not live. The snapshot holds only abstract-level text: no authors, no method section, and no repository URL. The linked repository was not read.

CLAIMS CHECKED:
- **Claim:** "A placeholder-protecting step cut broken placeholders from 6.1% to 0.4% of strings, on 4 string sets in 5 languages."
  - **Evidence:** A before/after comparison on the authors' own sets, with a 95% interval of 5.1 to 6.3 points for the reduction.
  - **Status:** PROBABLE. The 5.7-point drop sits inside the interval. However, the interval's upper bound (6.3) is larger than the 6.1% baseline, so its top end is impossible. That points to a rough approximation, and the method is not in the snapshot. The size of the effect is plausible, but its precision is overstated.
  - **Load-bearing:** yes.
- **Claim:** "Translation quality scores were unchanged within the interval."
  - **Evidence:** None shown. The metric, the scores and the interval are not given.
  - **Status:** PROBABLE at best, since the abstract asserts it without data.
  - **Load-bearing:** yes. A fix that hurts translation quality would not be worth borrowing.
- **Claim:** "Code, strings and evaluation script are in the linked repository (Apache-2.0)."
  - **Status:** UNVERIFIED. The repository was not read and no URL is in the snapshot.
  - **Load-bearing:** no. Apache-2.0 would be allowed even for shipped code.
- **Claim:** "Five languages only; right-to-left languages were not tested."
  - **Status:** CONFIRMED as a limitation the paper states.
  - **Load-bearing:** no for now. It becomes load-bearing if any of our five languages is right-to-left, and the context file does not name them.

FIT:
- **Goal:** Goal 3, "Ship the game in five languages by the end of Q1". Broken placeholders cause crashes or garbled UI text in localized builds.
- **Overlap:** Crowdin already handles our translations. The context file does not say whether we use machine translation inside Crowdin, or whether Crowdin's own checks already catch placeholder mismatches. That gap needs answering first.
- **Burden:**
  - Measuring the problem costs nothing new.
  - Adopting the method would mean a pre- or post-processing step around machine translation, owned by us.
- **Cost:** The paper is free (checked 2026-10-08). No account or subscription is involved.
- **Risks:**
  - No player data is involved.
  - Results come from the authors' own sets, and right-to-left languages are untested.
  - The interval reporting is sloppy.
  - The repository's license and health are unread.

NEXT ACTION:
- **Action:** Export the current Crowdin translations for our target languages and count strings whose placeholders do not match the source (`{0}`, `%s` and so on).
- **Owner:** operator.
- **Done when:** We have a broken-placeholder rate per language, and we know whether any target language is right-to-left.
- **Stop condition:** Stop if the rate is under 1% or Crowdin's existing checks already flag these strings. In that case the paper adds nothing for us.
- **Hand-off:** If the rate is higher, hand the paper and its repository to `glean` (rivendale/opensource) to borrow the protection step.

CONFIDENCE: medium. The snapshot is abstract-only and the repository is unread. The quality claim has no data behind it. The context file does not say whether we use machine translation in Crowdin or which five languages we ship.

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "paper", "identity": "preprint 2609.07712, 'Placeholder-safe machine translation for game strings', posted 2026-09-26 (saved snapshot of 2026-10-08, abstract-level text only)",
           "resolved": true},
  "claims": [
    {"claim": "placeholder-protecting step cuts broken placeholders from 6.1% to 0.4% of strings on 4 sets in 5 languages", "evidence": "abstract figures with a 95% interval of 5.1 to 6.3 points; the interval's upper bound exceeds the 6.1% baseline, so it is loosely computed; method not in snapshot", "status": "PROBABLE"},
    {"claim": "translation quality scores unchanged within the interval", "evidence": "asserted in the abstract; no metric or scores shown", "status": "PROBABLE"},
    {"claim": "code, strings and evaluation script are in a linked Apache-2.0 repository", "evidence": "stated in the abstract; repository not read and no URL in snapshot", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "only five languages tested; right-to-left languages not tested", "evidence": "the paper's own stated limitation", "status": "CONFIRMED", "load_bearing": false}
  ],
  "fit": {"goal": "goal 3: ship the game in five languages by the end of Q1", "overlap": "Crowdin already handles translations; unknown whether we use its machine translation or whether its checks already catch placeholder mismatches",
          "burden": "measurement needs nothing new; adopting would add a pre/post-processing step around machine translation",
          "risks": ["results only on the authors' own sets", "right-to-left languages untested", "interval reported loosely", "repository license and health not read"],
          "cost": {"price": "free", "tier": "open preprint", "limits": "none", "terms": "repo stated Apache-2.0, not verified",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Export current Crowdin translations for the target languages and count strings whose placeholders do not match the source",
                  "owner": "operator", "done_when": "a broken-placeholder rate per language is known, and whether any target language is right-to-left",
                  "stop_condition": "stop if the rate is under 1% or Crowdin's existing checks already flag these strings", "handoff": "glean"},
  "confidence": "medium",
  "context_file": "present"
}
```