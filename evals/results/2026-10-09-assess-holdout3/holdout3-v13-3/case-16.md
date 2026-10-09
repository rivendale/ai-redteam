VERDICT: watch. The recap has one line that bears on goal 3: a demo of automatic transcripts that a person corrects, at 12 minutes of correction per 45-minute episode. The post does not name the tool, its price or where the audio goes, so there is nothing here to act on until that tool is identified and assessed on its own.

WHAT IT IS: A post, "Podcast conference recap", dated 2026-09-30 (https://posts.example.test/podcast-movement-recap). No author is named. I read it from the saved snapshot captured 2026-10-09 (work/snapshot.md, work/meta.json), not live. It is a six-item list of sessions across three days, with one sentence per session.

CLAIMS CHECKED:
- "A ten-minute demo of automatic transcripts corrected by a person before publishing" was given on day 2: **PROBABLE**. This is the post's own report of a session. It is plausible but has no detail. Not load-bearing.
- "12 minutes of correction per 45-minute episode": **UNVERIFIED**. No tool, sample, audio type or method is given, and nothing says who did the correcting or what accuracy they reached. It comes from a ten-minute demo, so it may describe a single prepared example. It would mean something only if it were measured on several real episodes like ours (45 minutes, weekly). Not load-bearing: the verdict rests on the post naming no tool, which is a fact about the post rather than a claim in it.
- Nothing else in the post touches transcripts. Sponsorship rates, listener surveys, dynamic ad insertion, merch and the keynote are not about goal 3.

FIT:
- **Goal:** goal 3 (publish a transcript with every episode), and only as a pointer to a workflow: auto-transcribe, then correct by hand.
- **Overlap:** nothing in use makes transcripts today. Reaper, ffmpeg (used only by loudness.py), Buzzsprout, Mailchimp, Google Docs and Hugo all do other jobs.
- **Burden:** unknown until a tool is named. The claimed burden is about 12 minutes of correction per episode.
- **Cost:** not stated in the post (checked 2026-10-09). An automatic transcript service would likely need a new account or paid tier, and would send episode audio to a new party. Either would make that tool's verdict `needs-decision` under our constraints ($0 budget, no new account without the host's approval).
- **Risks:** none can be judged. The tool's license, data handling, platform (we need it to run on a Mac) and terms are all unknown.

NEXT ACTION: The operator finds out which tool was demoed in the day-2 transcript session, from the conference programme or by asking the post's publisher, and sends that tool to `assess`.
- **Done when:** the tool is named and has its own assess report.
- **Hand-off:** none. The post has nothing to borrow beyond the one-line workflow idea.

CONFIDENCE: high. The item is read from a saved copy dated 2026-10-09 and the context file is present. The verdict rests only on what the post contains, and the post names no tool. It does not rest on the unverified 12-minute figure.

```json
{
  "schema_version": "assess-1",
  "verdict": "watch",
  "item": {"type": "post", "identity": "\"Podcast conference recap\", posted 2026-09-30, no author named, https://posts.example.test/podcast-movement-recap (saved snapshot captured 2026-10-09)",
           "resolved": true},
  "claims": [
    {"claim": "a ten-minute demo of automatic transcripts corrected by a person was given on day 2", "evidence": "the post's one-line session summary", "status": "PROBABLE",
     "load_bearing": false},
    {"claim": "12 minutes of correction per 45-minute episode", "evidence": "stated in the post with no tool, sample, audio type or method; from a ten-minute demo", "status": "UNVERIFIED",
     "load_bearing": false}
  ],
  "fit": {"goal": "goal 3: publish a transcript with every episode (as a workflow pointer only)",
          "overlap": "none: no transcript tool in use",
          "burden": "unknown until a tool is named; claimed 12 minutes of correction per episode",
          "risks": ["tool unnamed: license, Mac support, data handling and terms unknown", "a hosted transcript service would likely add an account or cost and send episode audio to a new party"],
          "cost": {"price": "not stated", "tier": "not stated", "limits": "not stated", "terms": "not stated",
                   "checked_at": "2026-10-09"}},
  "next_action": {"action": "Identify the tool shown in the day-2 transcript demo (conference programme or the post's publisher) and send it to assess",
                  "owner": "operator", "done_when": "the tool is named and has its own assess report",
                  "handoff": "none"},
  "confidence": "high",
  "context_file": "present"
}
```