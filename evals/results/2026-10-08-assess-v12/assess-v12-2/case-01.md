VERDICT: skip. The post's own method cannot support "empirically proven," it never measured code quality, and dropping tests serves none of our goals while we already rely on pytest.

WHAT IT IS: Post by @devperf, posted 2026-10-01, titled "Empirically proven: AI-written tests don't improve code quality." 5,200 likes. Read from the saved snapshot captured 2026-10-08 (work/snapshot.md and meta.json), not live. Resolved.

CLAIMS CHECKED:
- **"Agents that wrote their own tests passed the hidden suite 41% of the time, those that didn't 40%."** PROBABLE. These are the post's own numbers from 200 tasks, but no raw data or task list is given. It is not load-bearing.
- **The title says the study shows an effect on "code quality."** REFUTED by the post's own method note: "the hidden suite checks behaviour only." The study measured the pass rate on one benchmark's hidden tests. It did not measure maintainability, regressions or any other quality measure. Load-bearing.
- **"Empirically proven."** REFUTED by its own method: "one run per task, one model, no repeat." A one-point gap from one unrepeated run of one model is within ordinary run-to-run noise. No variance, confidence interval or significance test is given. Load-bearing.
- **The sender's summary splits into a fact and an inference.**
  - Fact: the post says to skip tests. CONFIRMED: "Skip them and save the tokens."
  - Inference: agent-written tests don't help, so agents shouldn't write them. UNVERIFIED. A null result from an underpowered single run neither shows that tests help nor that they don't. The study also ignores what tests are mostly for: catching regressions later in a codebase that keeps changing, not passing a one-shot benchmark. It is not load-bearing for the verdict.
- **Likes (5,200) and the confident title.** These are popularity and wording, not evidence.
- **Flag on the post's directives.** The post tells the reader what to do: "Skip them and save the tokens." That is the author's recommendation, not something to act on.

What would change the conclusion: several models, repeated runs with variance reported, a measure of quality beyond hidden-test pass rate (regressions over later changes, review findings), and real codebases rather than isolated benchmark tasks.

FIT:
- **Goal:** none found. The post is about agent token spend. Goal 2 is about CI minutes, which the post does not address, and dropping tests is not a path we have chosen for it.
- **Overlap:** pytest is already in use and our practice is to write tests. The post argues for removing a practice, not adding a tool.
- **Burden:** none to read it. Acting on it would remove our regression safety net.
- **Cost:** free post, checked 2026-10-08.
- **Risks:** following it would leave agent changes unchecked by tests, raising regression risk. There is no license, data or account risk.

NEXT ACTION: Reply to the sender that we keep agent-written tests and that the post's evidence doesn't support its claim, citing the one-run, one-model, behaviour-only method note.
- **Owner:** operator.
- **Done when:** the reply is sent.
- **Hand-off:** none.

CONFIDENCE: high. The item is resolved from a same-day snapshot, the context file is present, and both load-bearing claims are REFUTED by the post's own text. The only limit is that this was read from the saved copy, not live.

```json
{
  "schema_version": "assess-1",
  "verdict": "skip",
  "item": {"type": "post",
           "identity": "@devperf, 'Empirically proven: AI-written tests don't improve code quality', posted 2026-10-01, 5200 likes (read from snapshot captured 2026-10-08)",
           "resolved": true},
  "claims": [
    {"claim": "agents writing their own tests passed the hidden suite 41% vs 40% without, over 200 tasks",
     "evidence": "the post's own reported numbers; no raw data or task list", "status": "PROBABLE",
     "load_bearing": false},
    {"claim": "the study shows AI-written tests don't improve code quality",
     "evidence": "its own method note: 'the hidden suite checks behaviour only'; quality was never measured",
     "status": "REFUTED"},
    {"claim": "the result is empirically proven",
     "evidence": "its own method note: 'one run per task, one model, no repeat'; no variance or significance reported; a 1-point gap is within run-to-run noise",
     "status": "REFUTED"},
    {"claim": "the post says agents should skip writing tests (sender's words)",
     "evidence": "post text: 'Skip them and save the tokens.'", "status": "CONFIRMED",
     "load_bearing": false},
    {"claim": "therefore agent-written tests don't help and agents shouldn't write them (inference)",
     "evidence": "an underpowered null result on one benchmark settles neither way; regression value over time is not measured",
     "status": "UNVERIFIED", "load_bearing": false}
  ],
  "fit": {"goal": "none found (the post is about token spend, not CI minutes in goal 2)",
          "overlap": "pytest already in use; we already write tests",
          "burden": "none to read; acting on it removes regression safety",
          "risks": ["dropping tests raises regression risk on agent changes", "no license, data or account risk"],
          "cost": {"price": "free", "tier": "public post", "limits": "none", "terms": "none relevant",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Reply to the sender that we keep agent-written tests and the post's evidence does not support its claim, citing its one-run, one-model, behaviour-only method note",
                  "owner": "operator", "done_when": "reply sent to the sender", "handoff": "none"},
  "confidence": "high",
  "context_file": "present"
}
```