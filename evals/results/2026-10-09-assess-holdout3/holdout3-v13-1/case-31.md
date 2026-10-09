VERDICT: try. A randomized test points to placing the signup prompt at the end of the content, which serves goal 2. The change uses the Mailchimp form we already have. The paper did not test audio pages, so we should check whether the result holds on our episode pages before keeping the change.

WHAT IT IS: Paper 2610.07719, "Where should a signup prompt go? A randomized test on 5 small sites". It is a preprint posted 2026-10-03. I read it from the saved snapshot captured 2026-10-09 (work/snapshot.md, work/meta.json), not live. The authors are not named in the snapshot. The paper links a repository (MIT) with code and an anonymized assignment table. I did not read that repository.

CLAIMS CHECKED:
- **Placement effect (rests on this): PROBABLE.** The claim is that a prompt at the end of an article gets more signups than one in a side bar.
  - Design: randomized assignment of 9,000 visitors across 5 small content sites. 2.9% signed up with the end-of-article prompt (n = 4,500) and 1.7% with the side-bar prompt (n = 4,500). The gap is 1.2 points, with a 95% interval of 0.6 to 1.8.
  - What was measured: the signup rate per visitor, not whether those subscribers stayed.
  - Why not CONFIRMED: it is an unreviewed preprint covering only 5 sites, and I did not check the data.
  - What would change the conclusion: a site-level breakdown showing one site drives the effect, or a failed replication.
- **The reported numbers are internally consistent (does not rest on this): CONFIRMED.** I recomputed the interval from the reported rates and group sizes and got about 0.58 to 1.82. That matches the stated 0.6 to 1.8.
- **The effect carries over to a podcast site's episode pages (rests on this): UNVERIFIED.** The paper's own limitation says "text articles only; audio pages were not tested". Our pages have a player plus show notes.
- **The code and assignment table are public under MIT (does not rest on this): UNVERIFIED.** The paper says so, but I did not read the repository.

FIT:
- **Goal:** goal 2, "Grow the newsletter: more listeners sign up".
- **Overlap:** the Mailchimp signup form already runs on the show site. This only changes where it sits. The context file does not say where it sits now. If it is already at the end of the episode pages, there is nothing to try.
- **Burden:** a one-time edit to the Hugo theme partial or episode template. No new service and no daily steps.
- **Cost:** free. The paper is open, and the change uses Mailchimp and Hugo, which we already have. There is no new account, subscription or data recipient.
- **Risks:** low.
  - Nothing ships from the paper's repository, so its license does not matter here.
  - Our measurement will be weak. The site lists no analytics, so we can count Mailchimp signups from the site form but not signups per visitor.
  - Adding an analytics service or an A/B tool to fix that would send visitor data to a new party or add an account. That would be needs-decision, so it is not part of this trial.

NEXT ACTION:
- **Action:** first check where the Mailchimp form sits on the episode pages. If it is in a side bar or header, move it to the end of each episode's show notes in the Hugo template. Then compare weekly signups from the site form in Mailchimp over the next 8 weeks against the 8 weeks before the change.
- **Owner:** operator (whoever maintains the Hugo site).
- **Done when:** the form is at the end of the episode pages and the before/after signup counts are written down with the dates of both periods.
- **Stop condition:**
  - Stop before changing anything if the form is already at the end of the episode pages.
  - Revert after 8 weeks if signups from the site form are not higher than in the prior 8 weeks.
- **Hand-off:** none. We are applying a placement finding with tools we already use, not borrowing code or text from the paper.

CONFIDENCE: medium. The item is resolved from a dated snapshot and the context file is present. The verdict rests on a PROBABLE placement effect and on an UNVERIFIED carry-over to audio episode pages that the paper itself says it did not test. Our own before/after count will also be noisy without traffic data.

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "paper",
           "identity": "2610.07719, 'Where should a signup prompt go? A randomized test on 5 small sites', preprint posted 2026-10-03 (read from snapshot captured 2026-10-09; authors not shown)",
           "resolved": true},
  "claims": [
    {"claim": "a signup prompt at the end of an article gets more signups than one in a side bar (2.9% vs 1.7%, +1.2 points, 95% CI 0.6 to 1.8)",
     "evidence": "randomized test, 9,000 visitors on 5 small text sites, n = 4,500 per arm; unreviewed preprint; data not checked",
     "status": "PROBABLE"},
    {"claim": "the reported rates, group sizes and interval are internally consistent",
     "evidence": "recomputed 95% interval from the stated rates and n: about 0.58 to 1.82, matching 0.6 to 1.8",
     "status": "CONFIRMED", "load_bearing": false},
    {"claim": "the placement effect carries over to a podcast site's episode pages",
     "evidence": "the paper's own limitation: text articles only, audio pages were not tested",
     "status": "UNVERIFIED"},
    {"claim": "code and anonymized assignment table are public under MIT",
     "evidence": "stated in the paper; linked repository not read",
     "status": "UNVERIFIED", "load_bearing": false}
  ],
  "fit": {"goal": "goal 2: grow the newsletter, more listeners sign up",
          "overlap": "Mailchimp signup form already on the show site; this changes only its placement (current placement not stated in the context file)",
          "burden": "one edit to the Hugo theme partial or episode template",
          "risks": ["paper tested text articles only, not audio pages",
                    "no site analytics, so only raw signup counts can be compared",
                    "adding analytics or an A/B tool would send visitor data to a new party: out of scope here"],
          "cost": {"price": "free", "tier": "open preprint; uses existing Mailchimp and Hugo", "limits": "none",
                   "terms": "no new account, subscription or data recipient", "checked_at": "2026-10-09"}},
  "next_action": {"action": "Check where the Mailchimp form sits on episode pages; if not at the end, move it to the end of the show notes in the Hugo template and compare weekly site-form signups in Mailchimp for 8 weeks against the prior 8 weeks",
                  "owner": "operator",
                  "done_when": "form sits at the end of episode pages and before/after signup counts are recorded with dates",
                  "stop_condition": "stop before changing anything if the form is already at the end; revert after 8 weeks if site-form signups are not higher than the prior 8 weeks",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```