VERDICT: adopt. It is an MIT-licensed, script-free Hugo shortcode that puts a link to the Mailchimp form we already have at the end of every episode page. That serves goal 2 with no new account, no cost and no new data recipient.

WHAT IT IS: example-org/signup-end, default branch main, release v1.0.2 at commit `7be30d95a1c4f82e6b0d3a97c5e1f4082b6d9a13`. License MIT. 60 stars, last push 2026-09-15, not archived. Read from a saved snapshot: README text in work/snapshot.md and repo metadata in work/meta.json, both captured 2026-10-09. The shortcode source file itself is not in the snapshot.

CLAIMS CHECKED:
- **License is MIT.** Evidence: meta.json (read live at capture) and the README. **CONFIRMED.** Load-bearing, because shortcodes on the show site must be MIT, Apache-2.0 or BSD.
- **It renders a box with a pitch and a button linking to a form URL you pass in, such as a Mailchimp form.** Evidence: the README's usage line `{{< signup-end url="..." >}}`. **PROBABLE.** The description is specific and consistent, but the source was not in the snapshot. Load-bearing.
- **"Plain HTML and CSS; no scripts, no tracking, no cookies, no dependencies."** Evidence: the README's own statement only. **PROBABLE.** It is plausible for a single shortcode, but the template has not been read. Load-bearing, because a tracker would send listener data to a new party.
- **Sender: "it links to our existing mailchimp form."** Evidence: the shortcode takes any URL, so it points wherever we tell it. **CONFIRMED** as a capability. Load-bearing.
- **Sender, by implication: it will grow sign-ups (goal 2).** Evidence: nothing in the item measures this. **UNVERIFIED.** Not load-bearing. The adopt rests on the box being cheap and safe, not on a promised lift.

FIT:
- **Goal:** goal 2, "Grow the newsletter: more listeners sign up". It puts the existing signup form in front of everyone who reaches an episode page.
- **Overlap:** none as a duplicate. Mailchimp stays the newsletter, as already decided, and this only links to its form. The context file says the form is "on the show site" but not whether it already appears on episode pages. If it does, this is a placement change, not a new capability.
- **Burden:** copy one file into `layouts/shortcodes/` of the Hugo site. Then add one line per episode page, or put it once in the episode template. No accounts and no services.
- **Cost:** free and open source, MIT, no tiers. Checked 2026-10-09 from the snapshot.
- **Risks:**
  - The license meets the site-code rule.
  - The install path is a pinned commit copied by hand after reading it, not `curl | bash`.
  - The no-scripts/no-tracking claim is from the README, so read the file before shipping it.
  - Health is small but active: 60 stars, pushed 2026-09-15.
  - No data leaves the site beyond the link to Mailchimp, which already receives sign-ups.
  - Lock-in is negligible: it is one file we own after copying.

NEXT ACTION: The operator (whoever maintains the Hugo site) copies the shortcode file from commit `7be30d95a1c4f82e6b0d3a97c5e1f4082b6d9a13`. They read it first to confirm it has no `<script>`, external requests or cookies, then add it to the episode template with our Mailchimp form URL.
- **Done when:** the box appears at the end of episode pages on the published GitHub Pages site and its button opens our Mailchimp form.
- **Hand-off:** none, because this is using a tool, not borrowing ideas.

CONFIDENCE: medium. The item is resolved from a dated snapshot and the context file is present. Two limits remain:
- The shortcode source was not in the snapshot, so "no scripts, no tracking" rests on the README.
- Whether the box actually raises sign-ups is unmeasured.

```json
{
  "schema_version": "assess-1",
  "verdict": "adopt",
  "item": {"type": "repo",
           "identity": "example-org/signup-end@7be30d95a1c4f82e6b0d3a97c5e1f4082b6d9a13 (v1.0.2, MIT, 60 stars, last push 2026-09-15, not archived, default branch main; snapshot captured 2026-10-09)",
           "resolved": true},
  "claims": [
    {"claim": "license is MIT", "evidence": "meta.json read live at capture and the README both say MIT", "status": "CONFIRMED"},
    {"claim": "renders an end-of-page box with a pitch and a button linking to a form URL passed as a parameter", "evidence": "README usage line {{< signup-end url=\"...\" >}}; shortcode source not in snapshot", "status": "PROBABLE"},
    {"claim": "plain HTML and CSS, no scripts, no tracking, no cookies, no dependencies", "evidence": "README statement only; template file not read", "status": "PROBABLE"},
    {"claim": "it links to our existing Mailchimp form (sender)", "evidence": "the url parameter takes any form URL, Mailchimp named as an example", "status": "CONFIRMED"},
    {"claim": "it will grow newsletter sign-ups (sender, implied by 'goal 2')", "evidence": "nothing in the item measures sign-up effect", "status": "UNVERIFIED", "load_bearing": false}
  ],
  "fit": {"goal": "goal 2: grow the newsletter (more listeners sign up)",
          "overlap": "Mailchimp form already on the show site; this only links to it and does not replace it",
          "burden": "copy one shortcode file into the Hugo site and add it to the episode template",
          "risks": ["MIT, meets the site-code license rule", "no-scripts/no-tracking claim is README-only until the file is read", "installed by copying from a pinned commit, not a moving branch", "small project: 60 stars, last push 2026-09-15"],
          "cost": {"price": "free", "tier": "open source", "limits": "none", "terms": "MIT",
                   "checked_at": "2026-10-09"}},
  "next_action": {"action": "Read the shortcode file at commit 7be30d95a1c4f82e6b0d3a97c5e1f4082b6d9a13, confirm it has no script, external request or cookie, copy it into layouts/shortcodes/ and add it to the episode template with our Mailchimp form URL",
                  "owner": "operator",
                  "done_when": "the box shows at the end of episode pages on the published site and its button opens our Mailchimp form",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```