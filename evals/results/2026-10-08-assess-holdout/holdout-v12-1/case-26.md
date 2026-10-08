VERDICT: needs-decision. The technique fits goal 3, but using it means calling a language model that is not in our stack. That needs a new API account and paid usage (money first, then account), and it sends our game strings to a new party. My lean is a small bounded `try` if the operator approves the spend.

WHAT IT IS: Post "Glossary-first pre-translation, step by step", posted 2026-09-21, from https://posts.example.test/glossary-pre-translation. I read a saved snapshot captured 2026-10-08 (work/snapshot.md, work/meta.json), not the live page. The snapshot names no author and no model.

CLAIMS CHECKED:
- **"Glossary terms used correctly in 779 of 800 strings (97%)" (load-bearing): PROBABLE.**
  - Evidence: the authors ran it on 800 strings in Spanish and German, checked by one bilingual reviewer. The arithmetic holds (97.4%).
  - Limits: it is a self-reported single run, with one reviewer and no second rater. It names no model and has no baseline, such as the same strings without the glossary table.
  - It measures only whether glossary terms were used correctly. It does not measure overall translation quality, fluency or string-length fit.
  - It covers 2 languages, and we need 5.
  - What would change the conclusion: a much lower glossary hit rate in our other three languages, or with the model we would use, or on our short UI strings.
- **"The prompt text and the 800 strings are in the post" (not load-bearing): UNVERIFIED.** The post says so, but neither appears in the captured snapshot.
- **"About 25 lines of Python call the model and write the result back to a CSV" (not load-bearing): UNVERIFIED.** The code is not in the snapshot.
- **Sender: "we could borrow the technique for goal 3" (load-bearing): PROBABLE.**
  - The method is fully described in the snapshot: a glossary table, then the strings, then a "use the table verbatim" rule.
  - It is cheap to reproduce.
  - The 97% result supports it only for glossary consistency in two languages.

FIT:
- **Goal:** Goal 3, ship in five languages by the end of Q1. It would speed up pre-translation and keep game terms consistent.
- **Overlap:** We already use Crowdin for translations. Pre-translated output would need to go into Crowdin for review, not replace it. The context does not say whether we already use a glossary or machine pre-translation inside Crowdin, so check that before adding a separate pipeline.
- **Burden:**
  - A small script: export strings, prompt the model, write a CSV, import into Crowdin.
  - Glossary upkeep.
  - Human review per language remains.
- **Cost:**
  - The post itself is free.
  - Running it needs a model API, which is not in our tool list. That means a new account and per-token usage.
  - Budget this quarter is $0 unless approved. No price could be read because the post names no model.
- **Risks:**
  - Game strings go to a model provider. They are not player data, so the player-data rule does not apply, but it is still a new party.
  - Results in our three other languages are unknown.
  - The script is not in the snapshot, so we would write our own. Licensing is not an issue because it is a tool we run and never ship.

NEXT ACTION: The operator decides whether to approve a model API account and a small usage budget for a bounded trial.
- Before deciding, check whether our Crowdin setup already offers glossary-enforced pre-translation, which would make a new provider unnecessary.
- Done when the decision (yes or no, and any cap) is recorded.
- If yes, the follow-up is a trial on about 200 strings per target language, comparing glossary hit rate and reviewer edits against our current Crowdin flow. Stop if glossary accuracy falls below about 95% or reviewers save no time.
- Hand-off: none for now. Harvesting the post's prompt is the step after approval.

CONFIDENCE: medium.
- The context file is present, and the item is resolved from a dated snapshot rather than live.
- The load-bearing result is a self-reported single-reviewer run in 2 of our 5 languages, with no model named.
- The prompt and data the post points to are missing from the snapshot.

```json
{
  "schema_version": "assess-1",
  "verdict": "needs-decision",
  "needs_decision_reason": "money",
  "item": {"type": "post",
           "identity": "post 'Glossary-first pre-translation, step by step', posted 2026-09-21, https://posts.example.test/glossary-pre-translation (snapshot captured 2026-10-08; no author or model named)",
           "resolved": true},
  "claims": [
    {"claim": "glossary terms used correctly in 779 of 800 strings (97%)",
     "evidence": "authors' own run, Spanish and German, one bilingual reviewer; no model named, no baseline, measures glossary use only",
     "status": "PROBABLE"},
    {"claim": "the prompt text and the 800 strings are in the post",
     "evidence": "stated in the post, but not present in the captured snapshot",
     "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "about 25 lines of Python call the model and write results to a CSV",
     "evidence": "stated in the post; code not in the snapshot",
     "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "sender: we could borrow the technique for goal 3",
     "evidence": "method fully described in the snapshot (glossary table, strings, verbatim rule); results cover 2 of our 5 languages",
     "status": "PROBABLE"}
  ],
  "fit": {"goal": "ship the game in five languages by the end of Q1 (goal 3)",
          "overlap": "Crowdin already handles translations; output would feed Crowdin review, and Crowdin's own glossary or pre-translation features should be checked first",
          "burden": "a small export/prompt/import script, glossary upkeep, human review per language",
          "risks": ["requires a model API not in our stack: new account and paid usage against a $0 budget",
                    "game strings sent to a new party (not player data)",
                    "results unproven for our other three languages and on short UI strings",
                    "prompt and code not in the snapshot; we would write our own"],
          "cost": {"price": "post free; model API usage unpriced (no model named)",
                   "tier": "unknown",
                   "limits": "unknown",
                   "terms": "unknown; depends on the chosen model provider",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Operator decides whether to approve a model API account and a small usage budget for a ~200-strings-per-language trial, after checking whether Crowdin already offers glossary-enforced pre-translation",
                  "owner": "operator",
                  "done_when": "the yes/no decision and any spending cap are recorded",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```