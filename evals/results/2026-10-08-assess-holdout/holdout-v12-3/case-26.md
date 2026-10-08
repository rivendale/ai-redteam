```
VERDICT: needs-decision (money). The technique fits goal 3, but using it means paying for calls to a model that is not in our tool list; it likely also needs a new account. I lean to try, with a bounded pilot on our own strings, once the operator approves the spend and the account.

WHAT IT IS: Post "Glossary-first pre-translation, step by step", https://posts.example.test/glossary-pre-translation,
  posted 2026-09-21. No author is named in the snapshot. Read from the saved snapshot captured 2026-10-08
  (work/snapshot.md, work/meta.json), not live. The post does not name which model it calls.

CLAIMS CHECKED:
  1. "Glossary terms used correctly in 779 of 800 (97%)". PROBABLE, load-bearing.
     - The arithmetic holds (779/800 = 97.4%).
     - Design: the author's own single run, 800 strings, Spanish and German only, one bilingual reviewer.
     - Measured: only whether glossary terms were used verbatim. Overall translation quality, fluency and
       string-length fit were not measured.
     - The model is unnamed, so the result may not transfer.
     - What would change it: a run on our strings and our other three target languages showing lower glossary
       adherence, or reviewers rejecting the non-glossary text.
  2. "The prompt text and the 800 strings are in the post". UNVERIFIED, not load-bearing.
     The snapshot states it, but the prompt and the strings are not in the captured content.
  3. "About 25 lines of Python call the model and write the result back to a CSV". UNVERIFIED, not load-bearing.
     The code is not in the snapshot.
  4. Sender: "we could borrow the technique for goal 3". PROBABLE, load-bearing.
     It matches goal 3 (five languages by end of Q1), but the post covers only 2 of our 5 languages.

FIT:
  Goal: goal 3, ship the game in five languages by end of Q1.
  Overlap: Crowdin already handles our translations. Whether Crowdin's own glossary and machine pre-translation
    features already do this job is not settled by this item, so check that before building anything.
  Burden: a small script plus a CSV round-trip into Crowdin, a glossary we keep current, and a human review pass
    per language.
  Cost: the post is free. The model calls are not free and have no named provider, so the price is unknown
    (as of 2026-10-08). Our budget is $0 unless approved, and any new model account needs approval.
  Risks:
    - Game strings would go to a model provider. They are not player data, so that rule is not triggered, but
      the provider is still a new party.
    - The model is unnamed, so results may not transfer.
    - Untested on 3 of our 5 languages.
    - No license is stated for the prompt or code.

NEXT ACTION: The operator decides whether to approve a model API account and a capped spend for a pilot. A
  sensible pilot would take about 200 of our strings in one language the post did not test, with a bilingual
  review. If Crowdin's built-in glossary MT already covers this, decline and use that instead.
  Owner: operator. Done-when: the operator records yes or no, with a spend cap if yes.
  Hand-off: none. If approved, a later step hands the post to `harvest` to capture the prompt structure.

CONFIDENCE: medium. The item is resolved from a saved snapshot and the context file is present. Confidence is
  limited because:
  - the model is unnamed;
  - the prompt and code are not in the snapshot;
  - the evidence is one self-reported run on 2 of our 5 languages;
  - the Crowdin overlap is unchecked.
```

```json
{
  "schema_version": "assess-1",
  "verdict": "needs-decision",
  "needs_decision_reason": "money",
  "item": {"type": "post",
           "identity": "\"Glossary-first pre-translation, step by step\", https://posts.example.test/glossary-pre-translation, posted 2026-09-21, author not named; read from snapshot captured 2026-10-08",
           "resolved": true},
  "claims": [
    {"claim": "glossary terms used correctly in 779 of 800 strings (97%)",
     "evidence": "author's single self-run, Spanish and German, one bilingual reviewer; measured glossary-term adherence only, not overall quality; model unnamed",
     "status": "PROBABLE"},
    {"claim": "the prompt text and the 800 strings are in the post",
     "evidence": "stated in the snapshot, but neither appears in the captured content",
     "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "about 25 lines of Python call the model and write results to a CSV",
     "evidence": "stated only; code not in snapshot",
     "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "sender: we could borrow the technique for goal 3",
     "evidence": "matches goal 3 (five languages by end of Q1); post tested only 2 of our 5 languages",
     "status": "PROBABLE"}
  ],
  "fit": {"goal": "ship the game in five languages by the end of Q1 (goal 3)",
          "overlap": "Crowdin already handles translations; whether its own glossary/MT pre-translation covers this is unchecked",
          "burden": "a small script, a CSV round-trip into Crowdin, glossary upkeep, per-language human review",
          "risks": ["paid model calls against a $0 budget", "likely a new model-provider account", "game strings (not player data) sent to a new provider", "model unnamed, results may not transfer", "untested on 3 of 5 target languages", "no license stated for prompt or code"],
          "cost": {"price": "post free; model API price unknown (no provider named)", "tier": "unknown",
                   "limits": "unknown", "terms": "no license stated in snapshot",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Operator decides whether to approve a model API account and a capped spend for a ~200-string pilot in one untested language, after checking whether Crowdin's built-in glossary MT already covers this",
                  "owner": "operator",
                  "done_when": "operator records yes or no, with a spend cap if yes",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```