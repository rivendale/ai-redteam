VERDICT: try. The script does the last step of goal 3 (publish a transcript with every episode) on our Hugo site, for free and entirely on our own machine. But nothing we use today makes the `.srt` it needs, so a trial on one episode should show whether that gap can be filled without a new account or tool.

WHAT IT IS: A post, "Turn a subtitle file into a transcript page", dated 2026-09-25. No author is named. I read it from a saved snapshot captured 2026-10-09 (`work/snapshot.md`, `work/meta.json`), not live. It contains the full script, 13 lines of Python. The post states no license.

CLAIMS CHECKED:
- **"A 13-line Python script"** (the post). CONFIRMED. The script as shown is 13 lines, counting its one blank line. Not load-bearing.
- **"Reads an .srt on stdin and prints a Hugo page: front matter, then one paragraph per subtitle with its start time in bold"** (the post). CONFIRMED by reading the code; I did not run it.
  - It reads `sys.stdin` and splits on blank lines.
  - It skips blocks with fewer than 3 lines.
  - It prints `---\ntitle: Transcript\n---`, then one `**HH:MM:SS** text` paragraph per cue.
  - Caveats:
    - Milliseconds are dropped.
    - Every page gets the same title, "Transcript".
    - Multi-line cues are joined with spaces.
    - Cue text is not escaped, so `*`, `_`, `#` or `{{<` in the text would be read as Markdown or shortcodes.
  - Load-bearing.
- **"Turns a subtitle file into a transcript page for hugo"** (the sender). CONFIRMED by the same reading. Load-bearing.
- **"Most transcription tools can write an .srt subtitle file"** (the post). UNVERIFIED. The post names no tools and gives no evidence. Not load-bearing.
- **The usage path `content/episodes/42/transcript.md` fits our site** (implied by the post). UNVERIFIED. It depends on our Hugo content layout, which the context file does not describe. Not load-bearing.

FIT:
- **Goal:** Goal 3, "Publish a transcript with every episode", but only the formatting step. The script needs an `.srt`. Nothing in use (Reaper, ffmpeg via loudness.py, Buzzsprout, Mailchimp, Google Docs, Hugo) is listed as producing transcripts or subtitles. That missing source is the larger part of the goal.
- **Overlap:** None found. Nothing in use turns subtitles or transcripts into site pages.
- **Burden:**
  - One small local script.
  - One command per episode.
  - Possibly a per-episode title fix, since the title is fixed.
  - The real ongoing burden is getting an `.srt` for every episode, which is not covered here.
- **Cost:** Free, read 2026-10-09 from the snapshot. No account or service is needed for the script itself.
- **Risks:**
  - **No license stated.** The script runs on our machines and only its output ships, so the site-code license rule does not bite. Still, copying unlicensed code is unclear, and a 13-line script is easy to rewrite from the idea.
  - **Unescaped cue text** could break or alter the rendered page.
  - **Page shape:** one paragraph per cue gives a long, choppy page for a 45-minute episode.
  - **Data and dependencies:** no data leaves the machine, and there are no dependencies beyond the Python standard library.
  - **Transcription source:** getting the `.srt` may later need a new tool or account. That would need the host's approval.

NEXT ACTION:
- **Action:** Hand the post to `harvest` to bring the idea in as our own local script (rewritten, since the post has no license). Then run it on one episode's `.srt` and build the page with Hugo.
- **Owner:** operator.
- **Done when:** One episode's transcript page builds and reads correctly on the local Hugo site.
- **Stop condition:** Stop if getting an `.srt` for that episode needs a new paid tool, a new account, or sending audio to a new third party. That becomes a needs-decision for the host. Also stop if the page needs more fixing than writing the formatter from scratch would take.
- **Hand-off:** `harvest`.

CONFIDENCE: high. The item is resolved from a dated snapshot, the claims the verdict rests on are confirmed by reading the code, and the context file is present. Two things limit the trial's value rather than the verdict:
- The code's behavior was read, not run.
- Where the `.srt` will come from is unknown.

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "post",
           "identity": "\"Turn a subtitle file into a transcript page\", posted 2026-09-25, no author named, no license stated; saved snapshot captured 2026-10-09",
           "resolved": true},
  "claims": [
    {"claim": "a 13-line Python script", "evidence": "the script as shown is 13 lines including one blank line",
     "status": "CONFIRMED", "load_bearing": false},
    {"claim": "reads an .srt on stdin and prints a Hugo page: front matter, then one paragraph per subtitle with its start time in bold",
     "evidence": "read the script: reads sys.stdin, splits cues on blank lines, prints '---\\ntitle: Transcript\\n---' then '**HH:MM:SS** text' per cue (milliseconds dropped, fixed title, cue text not escaped)",
     "status": "CONFIRMED"},
    {"claim": "turns a subtitle file into a transcript page for hugo (sender)",
     "evidence": "same reading of the script; output is a Markdown page with YAML front matter",
     "status": "CONFIRMED"},
    {"claim": "most transcription tools can write an .srt subtitle file",
     "evidence": "stated without naming tools or giving evidence", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "the output path content/episodes/42/transcript.md fits our site",
     "evidence": "depends on our Hugo content layout, which the context file does not describe",
     "status": "UNVERIFIED", "load_bearing": false}
  ],
  "fit": {"goal": "goal 3, publish a transcript with every episode (the page step only; the .srt source is not covered)",
          "overlap": "none found: nothing in use makes transcript pages or .srt files",
          "burden": "one local script and one command per episode, plus a per-episode title fix; getting an .srt each week is not covered",
          "risks": ["no license stated in the post; runs locally so the site-code license rule does not apply, but rewrite rather than copy",
                    "cue text is not escaped, so Markdown or Hugo shortcode syntax in subtitles can alter the page",
                    "one paragraph per cue makes a choppy page for a 45-minute episode",
                    "the .srt source may need a new tool or account later, which needs the host's approval",
                    "no data leaves the machine; standard library only"],
          "cost": {"price": "free", "tier": "none (code in a post)", "limits": "none",
                   "terms": "no license stated", "checked_at": "2026-10-09"}},
  "next_action": {"action": "Hand the post to harvest to bring the idea in as our own local script, then run it on one episode's .srt and build the page with Hugo",
                  "owner": "operator",
                  "done_when": "one episode's transcript page builds and reads correctly on the local Hugo site",
                  "stop_condition": "stop if getting the .srt needs a new paid tool, a new account or sending audio to a new third party (a needs-decision for the host), or if the page needs more fixing than writing the formatter from scratch",
                  "handoff": "harvest"},
  "confidence": "high",
  "context_file": "present"
}
```