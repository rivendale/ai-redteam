**VERDICT:** try. It is free, Apache-2.0, needs no account and claims no network access, but nothing shows it reads changelog.py's actual output, so run one bounded trial before adopting it.

**WHAT IT IS:** example-org/mdx-changelog. This comes from a saved snapshot captured 2026-10-08, not a live read, and no commit sha was recorded.
- License: Apache-2.0
- Popularity: 540 stars
- Activity: last push 2026-09-21, last release 0.9.3 on 2026-09-21, not archived
- Default branch: `main`
- Install: `pip install mdx-changelog==0.9.3`, a pinned release, but pre-1.0
- Contents: the snapshot is the README only. The source file was not captured.

**CLAIMS CHECKED:**
1. **"It formats the changelog.py output" (sender's claim): PROBABLE. The verdict rests on this.**
   - The README says the tool takes "one entry per line, like the output of a commit-message script."
   - Nothing shows changelog.py's actual format, so whether the two match is not established.
   - "Nicely" is a matter of taste and cannot be checked.
2. **"Groups entries and writes a markdown page with a date header": PROBABLE.** The README states this, but no sample output is shown.
3. **"One file, standard library only": PROBABLE.** The README states it, and the single pinned pip install is consistent with it. The source was not read. This claim is not load-bearing.
4. **"No network access, no telemetry": UNVERIFIED. The verdict rests on this.**
   - This is the README's self-description only. The code was not in the snapshot.
   - It matters because changelog drafts come from internal commit messages, and the constraints bar company data going to a new party.
5. **"Goal 4" (sender's link to our goals): PROBABLE.**
   - changelog.py already builds the draft.
   - This tool would only add formatting, which helps "without manual work" only if formatting is currently a manual step.

**FIT:**
- **Goal:** Goal 4, ship a weekly changelog without manual work. It covers the formatting step only.
- **Overlap:** changelog.py, the nightly cron job, already builds the draft from commits. This tool does not replace it; it would sit after it. Check whether changelog.py already formats its output.
- **Burden:** one pinned pip dependency and one extra step in the nightly cron job. No account and no service.
- **Cost:** free, open source, no limits stated. Read from the 2026-10-08 snapshot.
- **Risks:**
  - The license is fine even if we vendor it in.
  - The project is pre-1.0, so the output format may change. Keep the version pinned.
  - The no-network claim is unconfirmed until the one source file is read.
  - It has a single maintaining org, though the last push was recent.

**NEXT ACTION:**
- **Action:** The operator reads the package's one source file to confirm it is stdlib-only with no network calls. Then they run it once on last week's changelog.py draft and compare the result with what was published.
- **Owner:** operator.
- **Done when:** the source has been read and one week's formatted page has been compared with the manually published changelog.
- **Stop condition:** stop if the source makes any network call or needs non-stdlib imports, if it cannot parse changelog.py's output without a rewrite, or if the result still needs manual editing.
- **Hand-off:** none.

**CONFIDENCE:** medium. It is limited by three things:
- The item is a README-only snapshot rather than the source.
- The load-bearing no-network claim is UNVERIFIED.
- changelog.py's output format was not available to compare.

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "repo", "identity": "example-org/mdx-changelog (Apache-2.0, 540 stars, last push 2026-09-21, not archived, default branch main; release 0.9.3; snapshot 2026-10-08, sha not recorded)",
           "resolved": true},
  "claims": [
    {"claim": "formats the changelog.py output (sender)", "evidence": "README: input is one entry per line, 'like the output of a commit-message script'; changelog.py's actual format not shown", "status": "PROBABLE"},
    {"claim": "writes a grouped markdown page with a date header", "evidence": "README statement, no sample output", "status": "PROBABLE", "load_bearing": false},
    {"claim": "one file, standard library only", "evidence": "README statement; source not in snapshot", "status": "PROBABLE", "load_bearing": false},
    {"claim": "no network access, no telemetry", "evidence": "README self-description only; source not read", "status": "UNVERIFIED"},
    {"claim": "serves goal 4 (sender)", "evidence": "context: goal 4 is a weekly changelog without manual work; changelog.py already builds the draft, this adds formatting only", "status": "PROBABLE"}
  ],
  "fit": {"goal": "ship a weekly changelog without manual work (goal 4), formatting step only",
          "overlap": "changelog.py nightly cron already builds the draft; this would be a post-processing step, not a replacement",
          "burden": "one pinned pip dependency and one extra step in the nightly cron",
          "risks": ["Apache-2.0, allowed even if vendored", "pre-1.0, output may change; pin the version", "no-network claim unconfirmed until source is read"],
          "cost": {"price": "free", "tier": "open source", "limits": "none stated", "terms": "Apache-2.0",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Read the package's single source file for imports and network calls, then run it once on last week's changelog.py draft and compare with the published changelog",
                  "owner": "operator",
                  "done_when": "source read and one week's formatted output compared with the published changelog",
                  "stop_condition": "stop if it makes any network call, needs non-stdlib imports, cannot parse changelog.py output, or the result still needs manual edits",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```