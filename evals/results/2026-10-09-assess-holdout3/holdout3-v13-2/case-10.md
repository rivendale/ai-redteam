**VERDICT:** skip. It serves none of our four goals, and its GPL-3.0 license breaks our rule that code shipping on the show site must be MIT, Apache-2.0 or BSD.

**WHAT IT IS:** example-org/chapter-player, a Hugo shortcode repo.
- License GPL-3.0, 300 stars, last push 2026-09-14, not archived, default branch `main`.
- Read from the saved snapshot captured 2026-10-09 (`work/snapshot.md` and `work/meta.json`), not live. No commit SHA was captured.

**CLAIMS CHECKED:**
- **The license is GPL-3.0** (sender's link, item's own text). CONFIRMED. Both `meta.json` and the snapshot say GPL-3.0. *The verdict rests on this.*
- **"Anything that includes this shortcode must itself be released under the GPL"** (the item's own terms). CONFIRMED as the stated term. Shipping it would put our Hugo theme and site under GPL obligations, which our constraints do not allow for site code. *The verdict rests on this.*
- **It adds a play button with the chapter list to episode pages** (sender's words). PROBABLE. The snapshot describes exactly this, but it holds no source or demo to confirm it works. Not load-bearing.
- **It is plain HTML and a small script, with no tracking and no dependencies.** UNVERIFIED. This is README wording only; the snapshot contains no source to read. Not load-bearing.
- **The project is maintained** (last release 2026-09-14). CONFIRMED by `meta.json` `last_push` 2026-09-14 and not archived. Not load-bearing.

**FIT:**
- **Goal:** none found. Our goals are:
  1. Editing under 2 hours per episode.
  2. Newsletter signups.
  3. A transcript with every episode.
  4. Consistent loudness.
  
  A chapter player on episode pages does none of these.
- **Overlap:** none found in the context file. Buzzsprout hosts the audio, but the context does not say whether its player is embedded on the site.
- **Burden:** small. It is one shortcode added to the Hugo site and episode templates, plus writing chapter lists per episode, which adds editing work against goal 1.
- **Cost:** free, open source, read 2026-10-09.
- **Risks:**
  - The license conflicts with the site-code rule (GPL is allowed only for tools run on our own machines).
  - The "no tracking" claim is unverified.

**NEXT ACTION:** The operator tells the sender it is not being added: it serves no current goal, and its GPL-3.0 license is not allowed for code shipped on the site.
- Done when: the sender has the answer.
- Hand-off: none.
- If chapters on episode pages later become a goal, look for an MIT, Apache-2.0 or BSD alternative.

**CONFIDENCE:** high. The item is resolved from a dated snapshot, the claims the verdict rests on are CONFIRMED, and a context file is present. It is read from a saved copy, not live.

```json
{
  "schema_version": "assess-1",
  "verdict": "skip",
  "item": {"type": "repo",
           "identity": "example-org/chapter-player@main (GPL-3.0, 300 stars, last push 2026-09-14, not archived; saved snapshot captured 2026-10-09, no commit sha captured)",
           "resolved": true},
  "claims": [
    {"claim": "licensed GPL-3.0", "evidence": "meta.json license field and snapshot text both say GPL-3.0",
     "status": "CONFIRMED"},
    {"claim": "anything that includes this shortcode must itself be released under the GPL",
     "evidence": "the item's own stated license terms in the snapshot", "status": "CONFIRMED"},
    {"claim": "adds a play button with the chapter list to episode pages",
     "evidence": "snapshot description only; no source or demo in the snapshot", "status": "PROBABLE",
     "load_bearing": false},
    {"claim": "plain HTML and a small script, no tracking, no dependencies",
     "evidence": "README wording only; no source in the snapshot to read", "status": "UNVERIFIED",
     "load_bearing": false},
    {"claim": "maintained, last release 2026-09-14",
     "evidence": "meta.json last_push 2026-09-14, archived false", "status": "CONFIRMED",
     "load_bearing": false}
  ],
  "fit": {"goal": "none found (goals are editing time, newsletter signups, transcripts, loudness)",
          "overlap": "none found in the context file",
          "burden": "one shortcode in the Hugo site plus writing chapter lists per episode",
          "risks": ["GPL-3.0 conflicts with the rule that site code must be MIT, Apache-2.0 or BSD",
                    "no-tracking claim unverified"],
          "cost": {"price": "free", "tier": "open source", "limits": "none stated",
                   "terms": "GPL-3.0; including works must be released under the GPL",
                   "checked_at": "2026-10-09"}},
  "next_action": {"action": "Tell the sender it is not being added: it serves no current goal and its GPL-3.0 license is not allowed for code shipped on the site",
                  "owner": "operator", "done_when": "the sender has the answer",
                  "handoff": "none"},
  "confidence": "high",
  "context_file": "present"
}
```