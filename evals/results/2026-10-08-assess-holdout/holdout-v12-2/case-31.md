VERDICT: watch. The paper fits goal 3, but it only matters if our translations go through machine translation, and nothing in the context file says they do. Crowdin is our translation tool, and our five languages are not named.

WHAT IT IS: Paper 2609.07712, "Placeholder-safe machine translation for game strings". It is a preprint posted 2026-09-26. I read it from a saved snapshot captured 2026-10-08 (work/snapshot.md, work/meta.json), not live. The authors are not named in the snapshot. The linked repository is cited but was not read.

CLAIMS CHECKED:
- **Broken placeholders drop from 6.1% to 0.4% of strings** (load-bearing).
  - Evidence: an evaluation on 4 game string sets in 5 languages, with a 95% interval for the reduction of 5.1 to 6.3 points. That interval fits the 5.7-point drop.
  - Status: PROBABLE. It is a preprint with no peer review. The test sets are the authors' own, and the code was not read.
  - What would change it: a re-run of their evaluation script that disagrees, or results on strings like ours.
- **Translation quality is unchanged** (load-bearing).
  - Evidence: quality scores were "unchanged within the interval". The metric is not named in the snapshot.
  - Status: PROBABLE. It is an automatic score, and no human review is mentioned.
- **Code, strings and evaluation script are in a repository under Apache-2.0** (not load-bearing).
  - Status: UNVERIFIED. The repo was not read. Apache-2.0 would be acceptable under our license rules even for code we ship.
- **Generalizes to our languages** (not load-bearing).
  - Status: UNVERIFIED. The paper covers five languages and did not test right-to-left languages. Our five target languages are not in the context file.

FIT:
- **Goal:** Goal 3 (ship in five languages by the end of Q1), and only if machine translation is part of the pipeline.
- **Overlap:** Crowdin already handles translations. Whether we use its machine translation, and whether its own placeholder checks already catch these errors, is unknown. Check that before adding anything.
- **Burden:** Adopting the method would add a pre- and post-processing step around machine translation. Reading the paper costs nothing.
- **Cost:** Free paper. The code is stated to be Apache-2.0 (not checked), read 2026-10-08.
- **Risks:**
  - Right-to-left languages were not tested.
  - It is a preprint.
  - Using it would mean running unread code from the repo.
  - No player data is involved.

NEXT ACTION: The operator checks two things in Crowdin: whether our strings are machine-translated, and how many placeholder errors (such as {0} or %s) reach review today.
- **Done when:** both answers are written down.
- **What follows:** If we use machine translation and placeholder errors are common, re-assess the paper and hand it to `glean` to borrow the placeholder-protection method. Otherwise, close it.
- **Hand-off now:** none.

CONFIDENCE: medium. The paper is resolved from the snapshot, and the claims the verdict rests on are PROBABLE. Three things limit confidence: it is an unreviewed preprint, the repo was not read, and the context file does not say whether we use machine translation or which languages we target.

```json
{
  "schema_version": "assess-1",
  "verdict": "watch",
  "item": {"type": "paper", "identity": "2609.07712, 'Placeholder-safe machine translation for game strings', preprint posted 2026-09-26 (snapshot captured 2026-10-08)",
           "resolved": true},
  "claims": [
    {"claim": "a placeholder-protecting step reduces broken placeholders in machine output from 6.1% to 0.4% of strings", "evidence": "preprint evaluation on 4 game string sets in 5 languages, 95% interval for the reduction 5.1 to 6.3 points; own data, code not read", "status": "PROBABLE"},
    {"claim": "translation quality scores are unchanged", "evidence": "preprint states quality unchanged within the interval; metric not named, no human review mentioned", "status": "PROBABLE"},
    {"claim": "code, strings and evaluation script are in a linked repository under Apache-2.0", "evidence": "stated in the snapshot; repository not read", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "the result holds for our five target languages", "evidence": "paper tested five languages, no right-to-left; our languages are not named in the context file", "status": "UNVERIFIED", "load_bearing": false}
  ],
  "fit": {"goal": "ship the game in five languages by the end of Q1 (goal 3), only if machine translation is in the pipeline",
          "overlap": "Crowdin already handles translations; whether it uses machine translation or already checks placeholders is unknown",
          "burden": "none to read; adopting the method adds a pre/post-processing step around machine translation",
          "risks": ["preprint, not peer reviewed", "right-to-left languages not tested", "repository and its Apache-2.0 license not verified"],
          "cost": {"price": "free", "tier": "open access preprint", "limits": "none stated", "terms": "code stated as Apache-2.0, not verified",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Check in Crowdin whether our strings are machine-translated and how many placeholder errors reach review today",
                  "owner": "operator", "done_when": "both answers are written down; if machine translation is used and placeholder errors are common, re-assess and hand the paper to glean",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```