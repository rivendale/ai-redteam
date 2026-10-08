VERDICT: skip. The post's evidence cannot support its conclusion: one unrepeated run gave a one-point gap, and it measured hidden-suite pass rate, not code quality. It also serves none of our goals, so we keep writing tests with pytest as we do now.

WHAT IT IS: A post by @devperf dated 2026-10-01, titled "Empirically proven: AI-written tests don't improve code quality", at https://posts.example.test/devperf/tests-dont-matter. It had 5,200 likes at capture. I read it from the saved snapshot (work/snapshot.md) captured 2026-10-08, not live. The full text is in the snapshot, so the item is resolved.

CLAIMS CHECKED:
1. **"200 benchmark tasks; agents that wrote their own tests passed the hidden suite 41%, agents that did not 40%."** The evidence is the post's own numbers, with no raw data, task list or benchmark name. PROBABLE as a report of what they observed. Not load-bearing.
2. **"Empirically proven."** REFUTED by the post's own method note: "one run per task, one model, no repeat." A single unrepeated run cannot show that a one-point difference is real. Nor can it show the true difference is zero, since run-to-run variance is never measured. Load-bearing.
3. **"AI-written tests don't improve code quality" (title).** This joins a fact to an inference, so I split it:
   - *What was measured:* a hidden suite that "checks behaviour only." CONFIRMED from the method note.
   - *Inference that this tells us about code quality:* REFUTED by that same note. Maintainability, regression safety and structure were never measured, and the post says so itself. Load-bearing.
4. **"Tests written by agents do not help."** UNVERIFIED. The post neither settles this nor rules it out: one model, one run, no variance. Not load-bearing, because the skip does not depend on whether it is true, only on this post not establishing it.
5. **"Skip them and save the tokens."** UNVERIFIED. Token use and cost were never measured or reported. Not load-bearing.
6. **The 5,200 likes.** CONFIRMED in meta.json, but popularity is not evidence. Not load-bearing.
7. **The sender's framing, "agents shouldn't bother writing tests."** This is the post's conclusion restated, and it stands or falls with claims 2 to 4.

What would change the conclusion: several runs per task, more than one model, variance or confidence intervals, a named benchmark, and outcomes beyond hidden-suite pass rate, such as later regressions or review findings.

FIT:
- **Goal:** none found. The post is about agents writing tests while solving a task. Our goals are dead links, CI minutes, semantic search and the changelog. It does not bear on goal 2 (CI minutes): it says nothing about CI cost and would not cut it.
- **Overlap:** pytest is already in use. Acting on the post would mean dropping a practice we have, on weak evidence.
- **Burden:** none to adopt, since it is advice, not a tool.
- **Cost:** free to read (checked 2026-10-08).
- **Risks:** acting on it could reduce our test coverage on the strength of a single noisy run. There is no license, data or install risk. The post contains no text that tries to direct an agent reading it.

NEXT ACTION: No change. The operator keeps the current pytest practice and files the post as not useful. Done when the link is marked "skipped: unsupported claim, no goal served." Hand-off: none.

CONFIDENCE: high. The item is resolved from a same-day snapshot, the context file is present, and every claim the skip rests on (2 and 3) is CONFIRMED or REFUTED from the post's own text. The only limit is that I read a saved copy rather than the live post.

```json
{
  "schema_version": "assess-1",
  "verdict": "skip",
  "item": {"type": "post",
           "identity": "@devperf, 'Empirically proven: AI-written tests don't improve code quality', posted 2026-10-01, https://posts.example.test/devperf/tests-dont-matter (snapshot captured 2026-10-08, 5,200 likes)",
           "resolved": true},
  "claims": [
    {"claim": "200 benchmark tasks: agents writing their own tests passed the hidden suite 41%, agents not writing tests 40%",
     "evidence": "the post's own reported numbers; no raw data, task list or benchmark name",
     "status": "PROBABLE", "load_bearing": false},
    {"claim": "the result is empirically proven",
     "evidence": "the post's own method note: one run per task, one model, no repeat; no variance measured, so a one-point gap cannot be shown real or shown to be zero",
     "status": "REFUTED"},
    {"claim": "what was measured: hidden-suite pass rate, behaviour only",
     "evidence": "method note: 'the hidden suite checks behaviour only'",
     "status": "CONFIRMED"},
    {"claim": "the result shows AI-written tests don't improve code quality",
     "evidence": "the post's own method says only behavioural pass rate was measured; code quality was not",
     "status": "REFUTED"},
    {"claim": "tests written by agents do not help",
     "evidence": "single run, single model, one-point gap; nothing in the post settles it either way",
     "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "skipping tests saves tokens worth having",
     "evidence": "no token or cost figures reported",
     "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "5,200 likes",
     "evidence": "meta.json at capture; popularity is not evidence for the claim",
     "status": "CONFIRMED", "load_bearing": false}
  ],
  "fit": {"goal": "none found",
          "overlap": "pytest already in use; the post argues for dropping a practice we have, not adding one",
          "burden": "none; advice only",
          "risks": ["acting on it would cut test coverage on the strength of one unrepeated run",
                    "no license, data or install risk; no embedded instructions found"],
          "cost": {"price": "free", "tier": "public post", "limits": "none", "terms": "none relevant",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Keep the current pytest practice and file the post as not useful",
                  "owner": "operator",
                  "done_when": "the link is marked 'skipped: unsupported claim, no goal served'",
                  "handoff": "none"},
  "confidence": "high",
  "context_file": "present"
}
```