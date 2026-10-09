VERDICT: adopt. It serves goal 2 at no cost. It is MIT, which our site-code rule allows. It sends visitors to the Mailchimp form we already use, so no new party is involved. The operator who maintains the Hugo site makes the change.

WHAT IT IS: example-org/signup-end, a GitHub repo. Release v1.0.2 is at commit `7be30d95a1c4f82e6b0d3a97c5e1f4082b6d9a13`.
- License: MIT.
- Health: 60 stars, last push 2026-09-15, not archived, default branch `main`.
- Source: read from the saved snapshot captured 2026-10-09 (work/snapshot.md and meta.json), not live. The snapshot is the README text only. The shortcode file itself was not in it.

CLAIMS CHECKED:
- **"A Hugo shortcode that renders a pitch box with a button linking to the form URL you give it."** Source: the README description. PROBABLE. The shortcode source was not in the snapshot to confirm. *The verdict rests on this.*
- **"Plain HTML and CSS; no scripts, no tracking, no cookies, no dependencies."** Source: the README says so. PROBABLE until the file is read at the pinned commit. *The verdict rests on this,* because tracking would send listener data to a new party.
- **License MIT.** Source: meta.json and the README agree. CONFIRMED. *The verdict rests on this.*
- **Sender: "it links to our existing mailchimp form."** The shortcode links to whatever URL you pass, and the README names a Mailchimp form as the example. CONFIRMED as a design choice: we pass our existing form's URL. *The verdict rests on this.*
- **Sender: "goal 2"**, meaning it will get more listeners to sign up. Nothing in the item measures this. UNVERIFIED. It is plausible, because the box puts the signup link where finished readers are. *The verdict rests on this,* but cheaply: if it does nothing, it costs nothing.

FIT:
- **Goal:** goal 2, grow the newsletter.
- **Overlap:** none. The Mailchimp form already exists, but nothing places a link to it at the end of each episode page. This complements the form rather than replacing it. It also sits inside the already-decided stack: Hugo and Mailchimp.
- **Burden:** copy one shortcode file into `layouts/shortcodes/`. Then add it to the episode template, or to each episode page. No account and no service. Upkeep is near zero.
- **Cost:** free and open source (MIT), no limits. Read 2026-10-09 from the snapshot.
- **Risks:**
  - The license is MIT, which is allowed for code that ships on the site.
  - The install path is a manual copy from a pinned commit. There is no `curl | bash`.
  - The README claims no scripts or tracking; this must be verified by reading the file.
  - There is no lock-in: it is one file we own after copying.
  - The project is small (60 stars) but active (last push 2026-09-15). Because we vendor the file, upstream health barely matters.

NEXT ACTION: The operator (site maintainer) does this:
1. Read the shortcode file at commit `7be30d95…` and confirm it has no `<script>`, no external resources and no tracking pixels.
2. Copy it into the Hugo site's `layouts/shortcodes/`.
3. Add `{{< signup-end url="<our Mailchimp form URL>" >}}` to the episode page template.

Done when the box appears on a published episode page on GitHub Pages and its button opens our Mailchimp form. Hand-off: none.

CONFIDENCE: medium. The context file is present and the item is resolved. Two things limit confidence:
- I worked from a saved README snapshot, and the shortcode source itself was not read, so the "no scripts, no tracking" claim is only PROBABLE.
- The effect on signups is unmeasured.

```json
{
  "schema_version": "assess-1",
  "verdict": "adopt",
  "item": {"type": "repo",
           "identity": "example-org/signup-end@7be30d95a1c4f82e6b0d3a97c5e1f4082b6d9a13 (MIT, v1.0.2, last push 2026-09-15, 60 stars, not archived; read from snapshot captured 2026-10-09)",
           "resolved": true},
  "claims": [
    {"claim": "Hugo shortcode that renders a pitch box with a button linking to the form URL you pass",
     "evidence": "README in snapshot; shortcode source not in snapshot", "status": "PROBABLE"},
    {"claim": "plain HTML and CSS; no scripts, no tracking, no cookies, no dependencies",
     "evidence": "README states it; file not read", "status": "PROBABLE"},
    {"claim": "license is MIT", "evidence": "meta.json and README agree", "status": "CONFIRMED"},
    {"claim": "sender: it links to our existing Mailchimp form",
     "evidence": "the url parameter takes any form URL; README names Mailchimp as the example", "status": "CONFIRMED"},
    {"claim": "sender: it serves goal 2 (more newsletter signups)",
     "evidence": "no measurement in the item; plausible placement argument only", "status": "UNVERIFIED"}
  ],
  "fit": {"goal": "grow the newsletter (goal 2)",
          "overlap": "none; complements the existing Mailchimp form, nothing already places a signup box at the end of episode pages",
          "burden": "copy one shortcode file and add one line to the episode template; no account or service",
          "risks": ["MIT, allowed for site code", "no-tracking claim to verify by reading the file at the pinned commit", "small project, but vendored so upstream health matters little"],
          "cost": {"price": "free", "tier": "open source", "limits": "none", "terms": "MIT",
                   "checked_at": "2026-10-09"}},
  "next_action": {"action": "Read the shortcode at commit 7be30d95 to confirm no scripts or external resources, copy it into layouts/shortcodes/, and add it with our Mailchimp form URL to the episode template",
                  "owner": "operator (site maintainer)",
                  "done_when": "a published episode page shows the box and its button opens our Mailchimp form",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```