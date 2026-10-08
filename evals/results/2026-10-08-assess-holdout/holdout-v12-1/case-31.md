```
VERDICT: try. The paper targets a real risk for goal 3 (broken {0}/%s placeholders in machine-translated strings) and reports a large, interval-backed reduction, but whether it helps us depends on whether we machine-translate in Crowdin and how many placeholders break today, so the next step is a bounded look, not adoption.
WHAT IT IS: Paper 2609.07712, "Placeholder-safe machine translation for game strings", preprint (not peer reviewed), posted 2026-09-26. Read from the saved snapshot captured 2026-10-08 (work/snapshot.md, work/meta.json), not live. The linked repository was not read; its license and contents are only as the paper states them.
CLAIMS CHECKED:
  1. "A placeholder-protecting step cut broken placeholders in machine output from 6.1% to 0.4% of strings (95% interval for the reduction: 5.1 to 6.3 points)." Evidence: the authors' own evaluation on 4 game string sets in 5 languages, with an interval given. The numbers are internally consistent (the 5.7-point drop sits inside the interval). It has not been replicated, and the snapshot names neither the MT system nor the string sets. PROBABLE. The verdict rests on this claim.
  2. "Translation quality scores were unchanged within the interval." Evidence: a statement only. The snapshot gives no metric, scores or interval. UNVERIFIED. Not load-bearing, because the trial would check our own output.
  3. "Code, strings and evaluation script are in the linked repository (Apache-2.0)." Evidence: the paper says so. The repository was not read. UNVERIFIED. Not load-bearing; Apache-2.0 would be allowed even for shipped code.
  4. "Tested on five languages only; right-to-left not tested." Evidence: the paper's own limitations text. CONFIRMED as stated. Not load-bearing unless one of our five languages is RTL (Arabic, Hebrew), which the context file does not say.
FIT:
  - Goal: goal 3, ship in five languages by end of Q1. Broken placeholders are a common cause of runtime string bugs in localized builds.
  - Overlap: Crowdin already handles our translations. The context file does not say whether we use machine translation in Crowdin, or whether its QA checks already catch placeholder mismatches. If we use human translation only, or Crowdin already blocks mismatches, the gain is small.
  - Burden: reading a paper. Adopting the method would add a pre/post-processing step around MT (mask placeholders, translate, restore) and some upkeep.
  - Cost: paper free; code stated Apache-2.0 (checked 2026-10-08 from the snapshot). No new account or subscription implied.
  - Risks: preprint with no independent replication; RTL untested; quality claim unsupported in the text read; repository license and health unverified.
NEXT ACTION: Hand the paper and its repository to glean to extract the placeholder-protection step and map it onto our Crowdin flow, alongside a count of broken placeholders in one language of our current Crowdin output.
  - Owner: operator via glean.
  - Done when: a short note says how the step works, whether it fits our Crowdin workflow, and gives our current broken-placeholder rate.
  - Stop if: we do not machine-translate, or our current rate is already under about 0.5% of strings, or the repository's license is not Apache-2.0/MIT/BSD/zlib.
  - Hand-off: glean.
CONFIDENCE: medium. The item is resolved from a saved snapshot and the load-bearing claim is PROBABLE, but the fit depends on facts the context file does not record: whether we machine-translate, our target languages (RTL or not), and Crowdin's existing placeholder checks.
```

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "paper",
           "identity": "2609.07712, 'Placeholder-safe machine translation for game strings', preprint posted 2026-09-26 (read from snapshot captured 2026-10-08)",
           "resolved": true},
  "claims": [
    {"claim": "placeholder-protecting step cut broken placeholders in MT output from 6.1% to 0.4% of strings",
     "evidence": "authors' own evaluation on 4 game string sets in 5 languages, 95% interval for the reduction 5.1 to 6.3 points; not replicated, MT system not named in snapshot",
     "status": "PROBABLE"},
    {"claim": "translation quality scores unchanged",
     "evidence": "statement only; no metric, scores or interval in the snapshot",
     "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "code, strings and evaluation script are in a linked repository under Apache-2.0",
     "evidence": "the paper says so; repository not read",
     "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "only five languages tested; right-to-left languages not tested",
     "evidence": "the paper's own limitations text",
     "status": "CONFIRMED", "load_bearing": false}
  ],
  "fit": {"goal": "ship the game in five languages by end of Q1 (goal 3)",
          "overlap": "Crowdin already handles translations; unknown whether we use MT there or whether its QA already catches placeholder mismatches",
          "burden": "reading the paper; adopting would add a mask/translate/restore step around MT",
          "risks": ["preprint, no independent replication",
                    "right-to-left languages untested",
                    "quality claim unsupported by numbers in the snapshot",
                    "repository license and health not verified"],
          "cost": {"price": "free", "tier": "open paper; code stated Apache-2.0", "limits": "none stated",
                   "terms": "Apache-2.0 per the paper, unverified", "checked_at": "2026-10-08"}},
  "next_action": {"action": "Hand the paper and repository to glean to extract the placeholder-protection step and map it onto our Crowdin flow, with a count of broken placeholders in one language of our current Crowdin output",
                  "owner": "operator via glean",
                  "done_when": "a note describes the step, whether it fits our Crowdin workflow, and our current broken-placeholder rate",
                  "stop_condition": "stop if we do not machine-translate, our current rate is already under about 0.5% of strings, or the repository license is not Apache-2.0/MIT/BSD/zlib",
                  "handoff": "glean"},
  "confidence": "medium",
  "context_file": "present"
}
```