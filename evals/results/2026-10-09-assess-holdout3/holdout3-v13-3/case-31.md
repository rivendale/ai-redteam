VERDICT: try. A randomized test found an end-of-article signup prompt beat a side-bar prompt (2.9% vs 1.7%), which serves goal 2. We can test this with the Mailchimp form and Hugo site we already have, with no new account, cost or data flow. The paper only tested text articles, so whether the result holds on our episode pages has to be checked here.

WHAT IT IS: Paper 2610.07719, "Where should a signup prompt go? A randomized test on 5 small sites". It is a preprint posted 2026-10-03. I worked from a saved snapshot captured 2026-10-09 (work/snapshot.md, work/meta.json) and did not resolve it live. The snapshot says code and an anonymized assignment table are in a linked MIT repository. That repository is not in the snapshot, and I did not read it.

CLAIMS CHECKED:
- **End-of-article placement gets more signups than a side bar (load-bearing): PROBABLE.**
  - Design: 9,000 visitors across 5 small content sites, randomly assigned 4,500 per arm.
  - Measure: signup rate. 2.9% vs 1.7%, a difference of 1.2 points, 95% interval 0.6 to 1.8.
  - The interval matches the stated numbers. I recomputed the standard error at about 0.32 points, giving roughly 0.58 to 1.82.
  - It is not CONFIRMED because I did not inspect the assignment table or code.
  - What would change the conclusion: the sites' results pointing in different directions (only the pooled figure is given), or a problem in the assignment table.
- **The result applies to podcast or audio pages (not load-bearing for a try; it is what the try tests): UNVERIFIED.**
  - The paper's own limitation says "text articles only; audio pages were not tested."
  - Our episode pages may differ: visitors may play the audio rather than scroll to the end.
- **Code and the anonymized assignment table are public under MIT (not load-bearing): UNVERIFIED.** The snapshot states it, but the repository is not included.
- **The sample was 5 small sites, all text articles (not load-bearing): CONFIRMED** as the paper's own stated limitation.

FIT:
- **Goal:** Goal 2, "Grow the newsletter: more listeners sign up."
- **Overlap:** The Mailchimp signup form already runs on the show site. The paper offers no new tool, only a placement choice.
  - The context file does not say where the form sits now. If it is already at the end of episode pages, there is nothing to change and this becomes a skip.
- **Burden:** One edit to the Hugo theme or the episode template to move the existing Mailchimp form, then a few weeks of reading signup counts.
- **Cost:** Free. The paper is open, and no new tier or service is needed. Checked 2026-10-09 from the snapshot.
- **Risks:**
  - No new third party, since Mailchimp is already approved and stays decided.
  - No license issue, because we edit our own theme and do not ship the paper's code.
  - Our traffic is likely far below 4,500 visitors per arm. A 1.2-point lift may not be distinguishable from noise in a before/after comparison.
  - The result may not transfer from text pages to audio pages.

NEXT ACTION:
- **Action:** Check where the Mailchimp form sits on episode pages. If it is in a side bar, move it to the end of each episode page's show notes. Then compare signups per page visitor for 8 weeks after the move against the 8 weeks before.
- **Owner:** operator (whoever maintains the Hugo site).
- **Done when:** The current placement is recorded, the form is moved (or found already at the end), and the two 8-week signup rates are written down side by side.
- **Stop condition:** Revert or stop if the form is already at the end of the page. Also stop if, after 8 weeks, the signup rate is not above the prior 8 weeks.
- **Hand-off:** none. This applies a finding with a tool we already use; it does not borrow code.

CONFIDENCE: medium.
- The item is a saved snapshot, not resolved live.
- The main claim is PROBABLE, not confirmed against the data.
- The finding was not tested on audio pages.
- The current form placement is unknown from the context file.

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "paper", "identity": "2610.07719, 'Where should a signup prompt go? A randomized test on 5 small sites', preprint posted 2026-10-03 (saved snapshot captured 2026-10-09)",
           "resolved": true},
  "claims": [
    {"claim": "a signup prompt at the end of the article gets more signups than one in a side bar", "evidence": "randomized test, 9,000 visitors on 5 sites, 4,500 per arm: 2.9% vs 1.7%, difference 1.2 points (95% interval 0.6 to 1.8); interval consistent with the stated rates; assignment table not inspected", "status": "PROBABLE"},
    {"claim": "the result holds on podcast or audio pages", "evidence": "the paper's own limitation: text articles only, audio pages not tested", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "code and anonymized assignment table are public under MIT", "evidence": "stated in the snapshot; linked repository not included in the snapshot", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "the sample was five small sites with text articles only", "evidence": "the paper's own stated limitation", "status": "CONFIRMED", "load_bearing": false}
  ],
  "fit": {"goal": "Grow the newsletter: more listeners sign up (goal 2)",
          "overlap": "the Mailchimp signup form already on the show site; only its placement would change, and its current placement is not stated",
          "burden": "one edit to the Hugo theme or episode template, then reading signup counts for 8 weeks",
          "risks": ["result untested on audio pages", "our traffic is likely too low to detect a 1.2-point lift with confidence", "no new third party: Mailchimp is already in use and decided"],
          "cost": {"price": "free", "tier": "open preprint; uses the existing Mailchimp form", "limits": "none", "terms": "linked code stated as MIT; not used",
                   "checked_at": "2026-10-09"}},
  "next_action": {"action": "Check where the Mailchimp form sits on episode pages; if in a side bar, move it to the end of the show notes and compare signups per page visitor for the 8 weeks after against the 8 weeks before",
                  "owner": "operator", "done_when": "current placement is recorded, the form is moved (or found already at the end), and the two 8-week signup rates are written down side by side",
                  "stop_condition": "stop if the form is already at the end of the page, or revert if after 8 weeks the signup rate is not above the prior 8 weeks", "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```