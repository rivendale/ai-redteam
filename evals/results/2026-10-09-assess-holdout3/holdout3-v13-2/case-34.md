VERDICT: try. It is a free, MIT-licensed Hugo shortcode that adds a signup box at the end of each episode page and links to the Mailchimp form we already use, so it serves goal 2 with no new account, cost or third party. But its "no scripts, no tracking" claim comes only from its README, and nothing shows it raises signups, so it should be a bounded trial.

WHAT IT IS: example-org/signup-end, a GitHub repo. MIT, 60 stars, last push 2026-09-15, not archived, default branch `main`. Latest release is v1.0.2 (2026-09-15) at commit `7be30d95a1c4f82e6b0d3a97c5e1f4082b6d9a13`. This was read from a saved snapshot and meta.json captured on 2026-10-09, not live. The shortcode source file itself is not in the snapshot.

CLAIMS CHECKED:
- **License is MIT.** Evidence: meta.json (read live at capture) and the README agree. CONFIRMED. *Load-bearing*, because site code must be MIT, Apache-2.0 or BSD.
- **It renders a box with a pitch and a button linking to a URL you pass in, such as a Mailchimp form.** Evidence: README only. PROBABLE. *Load-bearing*: this is what lets it point at our existing Mailchimp form.
- **Plain HTML and CSS, with no scripts, tracking, cookies or dependencies.** Evidence: the README's own words. The file is not in the snapshot, so nothing settles this. UNVERIFIED. *Load-bearing*, because if it loads anything from a third party, listener data leaves to a new party.
- **The sender's claim that it serves goal 2 by linking to our existing Mailchimp form.** The fact part, that it can link to any form URL including ours, is PROBABLE per the README. The inference part, that a box at the end of each episode page will bring more signups, is UNVERIFIED: the item offers no data. That inference is what the trial measures.
- **The README asks you to install by copying the file from the release commit "after reading it".** This is an ordinary install note, not an attempt to direct the reader. It also matches what we would do anyway.

FIT:
- **Goal:** goal 2 (grow the newsletter).
- **Overlap:** Mailchimp and its signup form on the show site are already in use. This does not replace them. It adds one more place that links to that same form, so there is no conflict with the decision that Mailchimp stays our newsletter.
- **Burden:** copy one file into `layouts/shortcodes/`, then add one line to the episode template or each episode page. Nothing to run, and there is no new service.
- **Cost:** free, MIT (read 2026-10-09).
- **Risks:**
  - The license is allowed for site code.
  - Pinning to the release commit avoids pulling from a moving branch.
  - Its privacy claim is unverified until the file is read.
  - Project health is small but recent (60 stars, pushed 3 weeks before capture). Since we vendor one file, upstream health matters little.

NEXT ACTION: The operator reads the shortcode file at commit `7be30d9…`. If it is plain HTML and CSS only, they copy it into the Hugo site and add it to the episode template with our Mailchimp form URL.
- **Done when:** the box appears on episode pages for 4 weekly episodes, and Mailchimp signups for those 4 weeks are compared with the 4 weeks before.
- **Stop if** any of these happen:
  - the file contains a `<script>`, an external font, image or CSS URL, or any request other than the form link;
  - the license header is not MIT;
  - signups show no change after 4 episodes. In that case, remove the line.
- **Hand-off:** none. This is using the tool, not borrowing ideas.

CONFIDENCE: medium. The context file is present and the license is confirmed. Confidence is limited because the item was read from a saved snapshot, the "no scripts or tracking" claim the verdict rests on is unverified until the file is read, and the signup benefit is unproven.

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "repo",
           "identity": "example-org/signup-end@7be30d95a1c4f82e6b0d3a97c5e1f4082b6d9a13 (MIT, 60 stars, last push 2026-09-15, not archived, default branch main; from snapshot captured 2026-10-09)",
           "resolved": true},
  "claims": [
    {"claim": "license is MIT", "evidence": "meta.json read live at capture and README agree", "status": "CONFIRMED"},
    {"claim": "renders an end-of-page box with a button linking to a given form URL (e.g. Mailchimp)", "evidence": "README description only; shortcode file not in snapshot", "status": "PROBABLE"},
    {"claim": "plain HTML and CSS, no scripts, no tracking, no cookies, no dependencies", "evidence": "README's own words; source file not in snapshot", "status": "UNVERIFIED"},
    {"claim": "sender: it can link to our existing Mailchimp form", "evidence": "README: links to whatever form URL is passed", "status": "PROBABLE"},
    {"claim": "sender: an end-of-episode box will grow newsletter signups (goal 2)", "evidence": "none offered; this is what the trial measures", "status": "UNVERIFIED", "load_bearing": false}
  ],
  "fit": {"goal": "grow the newsletter (goal 2)",
          "overlap": "Mailchimp and its signup form already in use; this only adds another link to that same form, it does not replace anything",
          "burden": "copy one shortcode file into layouts/shortcodes and add one line to the episode template; no service, no account",
          "risks": ["MIT, allowed for site code", "no-scripts/no-tracking claim unverified until the file is read", "install pinned to a release commit, not a moving branch", "small project, but vendored as one file"],
          "cost": {"price": "free", "tier": "open source", "limits": "none", "terms": "MIT",
                   "checked_at": "2026-10-09"}},
  "next_action": {"action": "Read the shortcode file at commit 7be30d9; if it is plain HTML/CSS only, copy it into the Hugo site and add it to the episode template with our Mailchimp form URL",
                  "owner": "operator",
                  "done_when": "the box is live on 4 weekly episodes and Mailchimp signups for those 4 weeks are compared with the 4 weeks before",
                  "stop_condition": "stop if the file has any script, external resource or request other than the form link, or is not MIT; remove it if signups show no change after 4 episodes",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```