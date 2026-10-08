```
VERDICT: needs-decision, because the technique only works by sending our strings to a language model. Nothing in our context file says we have a model account, and the budget is $0, so using it needs a new paid service and probably a new account. My lean is to try it on a small batch if the operator approves a model, because goal 3 is real and the post's result is specific, but that choice is the operator's.

WHAT IT IS: Post "Glossary-first pre-translation, step by step", posted 2026-09-21. The snapshot does not name an author.
  I read it from the saved snapshot captured 2026-10-08 (work/snapshot.md, work/meta.json), not live.
  The post does not name which model it calls or what that model costs.

CLAIMS CHECKED:
  1. "A bilingual reviewer found glossary terms used correctly in 779 of 800 (97%), Spanish and German."
     Evidence: the authors' own run, on 800 strings in 2 languages, checked by one reviewer.
     The arithmetic holds (779/800 = 97.4%).
     What it measured: glossary-term correctness only. It did not measure overall translation quality, fluency, or string length.
     There is no baseline without the glossary table and no second reviewer. It is unclear whether the 800 counts strings or term uses.
     What would change the conclusion: a lower hit rate on our own glossary or on our other three languages.
     -> PROBABLE (load-bearing)
  2. Sender: "we could borrow the technique for goal 3." I split this into two parts:
     a. Goal 3 is shipping in five languages by end of Q1. -> CONFIRMED by the context file (load-bearing)
     b. The technique would help goal 3. It fits pre-translation ahead of human review, but the post only shows 2 of our 5 languages. -> PROBABLE (load-bearing)
  3. "The prompt text and the 800 strings are in the post." The captured snapshot does not contain them.
     It may be truncated, so this is not refuted. -> UNVERIFIED (not load-bearing; the prompt structure is described well enough to rebuild)
  4. "About 25 lines of Python call the model and write the result back to a CSV." The code is not in the snapshot. -> UNVERIFIED (not load-bearing)
  No text in the snapshot tries to direct the reader.

FIT:
  Goal: goal 3 (five languages by end of Q1).
  Overlap: Crowdin is already our translation tool. This would feed pre-translations into it, not replace it. Whether Crowdin already offers glossary-aware machine pre-translation is not settled by this item; check that before adding anything new.
  Burden: one small script, a model API key, and a CSV round-trip into Crowdin each time we pre-translate. Bilingual review is still needed.
  Cost: unknown. The post names no model or price. Our budget for new tools is $0 unless approved.
  Risks: game strings go to a model provider. This is not player data, but it is a new third party. Possible lock-in to one provider's API. The post states no license, so rewrite the prompt rather than copying it verbatim.

NEXT ACTION: The operator decides whether to approve a model API for translation work (provider, spend cap, account) or to use any machine-translation option Crowdin already includes.
  Owner: operator.
  Done when: one model or option is approved or the idea is declined.
  If approved, the follow-on is a trial: pre-translate about 100 strings in each of our five languages using our Crowdin glossary, and have a reviewer count glossary-term hits. Stop if term accuracy is under 90% in any language, or if review time is no better than translating from scratch.
  Hand-off: none.

CONFIDENCE: medium. The snapshot is readable and the context file is present, but the post does not name the model or its cost, its result covers only 2 of our 5 languages with one reviewer, and Crowdin's existing capabilities are not settled by this item.
```

```json
{
  "schema_version": "assess-1",
  "verdict": "needs-decision",
  "needs_decision_reason": "money",
  "item": {"type": "post",
           "identity": "post 'Glossary-first pre-translation, step by step', posted 2026-09-21, author not named, https://posts.example.test/glossary-pre-translation, read from snapshot captured 2026-10-08",
           "resolved": true},
  "claims": [
    {"claim": "glossary terms used correctly in 779 of 800 (97%) in Spanish and German",
     "evidence": "authors' own run on 800 strings, one bilingual reviewer, no baseline; measures glossary-term use only",
     "status": "PROBABLE"},
    {"claim": "goal 3 is shipping the game in five languages by end of Q1",
     "evidence": "context_file.md goals list",
     "status": "CONFIRMED"},
    {"claim": "the technique would help goal 3",
     "evidence": "method fits pre-translation before review, but only 2 of our 5 languages tested",
     "status": "PROBABLE"},
    {"claim": "the prompt text and the 800 strings are in the post",
     "evidence": "not present in the captured snapshot; may be truncated",
     "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "about 25 lines of Python call the model and write results to a CSV",
     "evidence": "code not present in the snapshot",
     "status": "UNVERIFIED", "load_bearing": false}
  ],
  "fit": {"goal": "goal 3: ship the game in five languages by end of Q1",
          "overlap": "Crowdin already handles translations; this would feed pre-translations into it; whether Crowdin already offers glossary-aware machine pre-translation is not settled by this item",
          "burden": "one small script, a model API key, a CSV round-trip into Crowdin per batch, bilingual review still required",
          "risks": ["game strings sent to a new model provider (not player data, but a new third party)",
                    "provider lock-in",
                    "post states no license; rewrite the prompt rather than copy it",
                    "result covers only 2 of 5 languages, one reviewer"],
          "cost": {"price": "unknown: the post names no model or price", "tier": "unknown",
                   "limits": "unknown", "terms": "no license stated for the prompt or code; $0 budget unless approved",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Operator decides whether to approve a model API (provider, spend cap, account) or use a machine-translation option Crowdin already includes; if approved, trial on ~100 strings per language with our glossary",
                  "owner": "operator",
                  "done_when": "a model or option is approved or the idea is declined",
                  "stop_condition": "for the follow-on trial: stop if glossary-term accuracy is under 90% in any language or review time is no better than translating from scratch",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```