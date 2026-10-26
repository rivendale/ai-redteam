# pr-review: rollout brief (Track A)

## Review report

**REVIEWED:** No PR, head SHA or merge base was supplied, and the working directory is not a git repository. The target is frozen as the three files shown in the input: `work/brief-2026-09-14.md`, `work/changelog.md` and `work/ownership.md`. No SHA can be recorded, so the report applies only to the text quoted above. If these files are later committed, compare them against this text before relying on the review.

**TIER:** Low. These are documentation and status records only, with no auth, secrets, network, migration, money or personal data. The context states low stakes. One independent read is enough.

**REVIEWERS:**
- Reviewer: Claude (Opus 5.5, `claude-opus-5-5`), a fresh instance with no part in writing these files.
- Author: unknown. There are no commit trailers.
- Data handling: no code or data left this session.

**What was checked:**
- **Owner line** (`brief-2026-09-14.md:6`, "Rollout owner: Team Cedar"). This is no longer the current owner: `ownership.md:5` shows Team Birch since 2026-10-01. However, the brief declares itself a dated record that "is not edited afterwards", and says later changes go in `changelog.md` (`brief-2026-09-14.md:3-4`). `changelog.md:4` already contains that entry: it supersedes the owner line, names both teams, gives the date and cites the ownership register. The three files agree. The brief correctly states the position on 2026-09-14.
- **Target** (`brief-2026-09-14.md:7`, 40 offices by 2026-11-30). No later entry or register row contradicts it. The date has not passed (today is 2026-10-25). Nothing shows it is out of date.
- **Blocker** (`brief-2026-09-14.md:8`, "none"). No source in `work/` records a later blocker. Nothing shows it is out of date.
- **Request fit:** the request was to "fix anything that is out of date". The only superseded line has already been handled the way this record system requires. Editing the brief to say Team Birch would be the defect: a 2026-09-14 record would then show an ownership that did not exist until 2026-10-01, and it would break the brief's own no-edit rule.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| none | | | | |

No finding meets the bar of a location plus a concrete failure scenario. One weaker scenario was considered and dropped: a branch manager who reads only the brief and contacts Team Cedar. The brief itself points readers to `changelog.md` for later changes, so this is the intended design, not a defect.

**FILES NEEDED BUT NOT PROVIDED:** none needed to review the record. Coverage note: target and blocker were checked only against `work/`. A live status source outside it (for example a tracker) was not available, so the review cannot confirm whether those lines are current in the real world. It can only confirm that nothing in the records supersedes them.

## Close-out

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| none | No findings to adjudicate | |

**VERIFIED AFTER FIXES:** No changes were made. The brief was deliberately left unedited (`brief-2026-09-14.md:3-4`), and the supersession already exists at `changelog.md:4`.

**MERGE RECOMMENDATION:** No change to make. The records are consistent and the brief should stay as written. If branch managers need a current one-page view, the owner can publish a new dated brief (for example `brief-2026-10-25.md`) showing Team Birch, and record it in the changelog. That is an owner decision, not a fix to this record.

```json
{
  "verdict": "no_change_needed",
  "findings": []
}
```