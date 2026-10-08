VERDICT: skip. The post's evidence cannot support its conclusion: one run of one model, a one-point gap (about 2 of 200 tasks), and no measure of code quality at all. We already rely on pytest, so dropping tests would remove something that works on the strength of noise.

WHAT IT IS: a post by @devperf, "Empirically proven: AI-written tests don't improve code quality", posted 2026-10-01. It was read from a saved snapshot captured 2026-10-08 (work/snapshot.md, work/meta.json), not live. It has 5,200 likes, which is popularity, not evidence.

CLAIMS CHECKED:
- **The headline numbers (load-bearing): "On 200 benchmark tasks, agents that wrote tests passed the hidden suite 41% of the time and agents that did not passed 40%."**
  - Evidence: the post's own numbers. It names no benchmark and links no data or code.
  - Status: **PROBABLE** as a description of their run.
- **The study measured code quality (load-bearing): "AI-written tests don't improve code quality."**
  - Evidence: the post's own method line says "the hidden suite checks behaviour only." The only outcome was the pass rate on one-shot tasks.
  - The study did not measure maintainability, regressions over time, or anything else that tests usually protect.
  - Status: **REFUTED** by the item's own method.
- **"Empirically proven" (load-bearing):**
  - Evidence: the post's own method line: "one run per task, one model, no repeat." It has no variance, no significance test and no second model.
  - A 1-point gap on 200 tasks is about 2 tasks, which is within run-to-run noise.
  - Status: **REFUTED**. Its own method shows nothing was proven either way.
- **"Tests written by agents do not help" (the inference drawn from the 41% vs 40% fact):**
  - The data neither shows a benefit nor rules one out.
  - The study design also cannot see the main value of a test suite: catching later regressions across changes.
  - Status: **UNVERIFIED**. Not load-bearing.
- **"Skip them and save the tokens" (the post's advice, and the sender's "agents shouldn't bother writing tests"):**
  - Evidence: none beyond the above.
  - Status: **UNVERIFIED**. Not load-bearing.

FIT:
- **Goal:** none found. It does not serve any of goals 1–4. Cutting tests is not a stated route to goal 2 (CI minutes), and the post does not mention CI cost.
- **Overlap:** pytest is already in use. The post argues for removing a practice, not adding a tool.
- **Burden:** none to read. Acting on it would mean removing test-writing from agent workflows.
- **Cost:** free post (checked 2026-10-08).
- **Risks:** acting on it could lead to regressions that only a test suite would catch. There is no license, data or account risk.

NEXT ACTION:
- **Action:** reply to the sender that the post does not support its claim and that we keep writing tests. Give the reasons: one run, one model, a 1-point gap, and code quality never measured.
- **Owner:** operator.
- **Done when:** the reply is sent.
- **Hand-off:** none.

CONFIDENCE: high. The item was read in full from a dated saved copy, not live. The context file is present. Every load-bearing claim is PROBABLE or REFUTED from the post's own text.

```json
{
  "schema_version": "assess-1",
  "verdict": "skip",
  "item": {"type": "post", "identity": "@devperf, \"Empirically proven: AI-written tests don't improve code quality\", posted 2026-10-01 (saved snapshot captured 2026-10-08)",
           "resolved": true},
  "claims": [
    {"claim": "on 200 benchmark tasks, agents that wrote tests passed the hidden suite 41% vs 40% without", "evidence": "the post's own numbers; benchmark unnamed, no data or code linked", "status": "PROBABLE"},
    {"claim": "AI-written tests don't improve code quality (the study measured code quality)", "evidence": "the post's method line: the hidden suite checks behaviour only; only the one-shot pass rate was measured", "status": "REFUTED"},
    {"claim": "empirically proven", "evidence": "the post's method line: one run per task, one model, no repeat, no significance test; the 1-point gap is about 2 of 200 tasks", "status": "REFUTED"},
    {"claim": "tests written by agents do not help (inference from the 41% vs 40% result)", "evidence": "the data neither shows a benefit nor rules one out; regression value over time is not measured", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "agents should skip writing tests to save tokens (the post's advice and the sender's summary)", "evidence": "no evidence beyond the above", "status": "UNVERIFIED", "load_bearing": false}
  ],
  "fit": {"goal": "none found", "overlap": "pytest already in use; the post argues for removing a practice, not adding a tool",
          "burden": "none to read; acting on it would remove test-writing from agent workflows",
          "risks": ["regressions a test suite would catch if tests were dropped", "no license, data or account risk"],
          "cost": {"price": "free", "tier": "public post", "limits": "none", "terms": "public post",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Reply to the sender that the post does not support its claim (one run, one model, 1-point gap, code quality not measured) and that we keep writing tests",
                  "owner": "operator", "done_when": "the reply is sent", "handoff": "none"},
  "confidence": "high",
  "context_file": "present"
}
```