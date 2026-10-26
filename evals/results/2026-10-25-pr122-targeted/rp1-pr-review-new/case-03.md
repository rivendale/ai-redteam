# pr-review: rollout brief (Track A)

**Review report**

**REVIEWED:** This is not a pull request. Three files were supplied inline: `brief-2026-09-14.md`, `changelog.md` and `ownership.md`. There is no head SHA and no merge base, and the working directory is not a git repository. Step 1 (freeze the target) could not be met, so this review covers only the file contents shown above. If these files reach a PR, its head was not reviewed.

**TIER:** Low. The change is documentation only and does not touch auth, secrets, network exposure or data handling. The context also rates the stakes as low. One independent read is enough for this tier.

**REVIEWERS:**
- Reviewer: Claude (claude-opus-5-5), a fresh session with no part in writing these files. This session has no tools, so nothing was run or opened.
- Author: unknown, because there are no commits or `Co-Authored-By` trailers to read.
- Data: the files contain team names and dates only, with no personal or regulated data, so no Step 3 restriction applies.

**File classification (Step 5.6):**

| File | Kind | Basis |
|---|---|---|
| `brief-2026-09-14.md` | Dated record | Its own text says it "is not edited afterwards"; later changes go in changelog.md |
| `changelog.md` | Living document (append-only log of dated entries) | Where supersession of the brief is recorded |
| `ownership.md` | Living document (current register) | Has a "since" column and reflects the present state |

**Analysis**

- The brief says "Rollout owner: Team Cedar". The register shows Branch rollout moved to Team Birch on 2026-10-01.
- That move happened after the brief's date, so the brief was correct on 2026-09-14. Under Step 5.6 a dated record is never edited in place. Changing "Team Cedar" to "Team Birch" in the brief would be a defect, because the record would then misstate the position on its own date.
- The intended way to supersede the brief is a new dated entry in `changelog.md`. That entry is missing: the changelog has only the 2026-09-14 publication line.
- A branch manager reading the brief and then the changelog would find nothing contradicting "Team Cedar" and would send rollout questions to the wrong team.
- The other two lines need no update:
  - **Target** (40 offices by 2026-11-30): still in the future as of today (2026-10-25), and nothing in the inputs contradicts it.
  - **Blocker: none**: nothing in the inputs contradicts it.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `changelog.md:3` (no entry after the 2026-09-14 line) | Ownership of Branch rollout moved from Team Cedar to Team Birch on 2026-10-01 (`ownership.md`, Branch rollout row). No dated changelog entry records this, so the brief is never superseded on ownership. A branch manager reading brief plus changelog on 2026-10-25 concludes Cedar owns the rollout and escalates to the wrong team. Workaround: consult `ownership.md`. | Check that every ownership change in `ownership.md` dated after a brief's date has a matching dated changelog entry. This fails today (no 2026-10-01 entry) and passes once the entry is added. |
| 2 | P3 (guard against the wrong fix) | `brief-2026-09-14.md:6` | The request says "fix anything that is out of date". The obvious fix would be to edit the brief's owner line to Team Birch. That edits a dated record in place, which contradicts lines 3–4 of the brief, and makes it misstate the 2026-09-14 position. | Check that `brief-2026-09-14.md` is unchanged from its published version; any diff to a dated brief fails. |

**Suggested fix for #1** (append to `changelog.md`; leave the brief untouched):

```
- 2026-10-01: rollout ownership moved from Team Cedar to Team Birch (see ownership.md); supersedes the owner line in brief-2026-09-14.md.
```

How I checked the fix (Step 5.5): I compared it against its consumers. It is a dated entry in the format of the existing changelog line, and its date and teams match the `ownership.md` row. It is a docs change, so no runnable test applies. I have not applied it because this session has no tools.

**FILES NEEDED BUT NOT PROVIDED:**
- A git history or PR, needed to freeze SHAs and identify the author.
- Any source showing a rollout blocker or a target change after 2026-09-14. If one exists, it would need its own changelog entry.

---

**Close-out**

**ADJUDICATION:** Pending. A reviewer does not adjudicate its own findings. The author or owner needs to record Accepted, Deferred or Rejected for #1 and #2.

**VERIFIED AFTER FIXES:** Nothing has changed since the review.

**MERGE RECOMMENDATION:** Merge after fixes. Add the changelog entry and leave the brief as is.

Step 8 says: "Recommend merge only when all of these hold: every round the tier requires has run, and every finding has a written decision; every expected check is present and green; no unresolved blocker remains; no owner or architecture decision is pending." The single Low-tier read has run, but findings #1 and #2 have no written decisions yet. No checks are defined for these files.

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "confirmed from provided file contents (ownership.md Branch rollout row vs. changelog.md); not run, no SHAs available",
      "location": "changelog.md:3",
      "scenario": "Ownership moved Cedar -> Birch on 2026-10-01 but changelog has no dated entry, so the dated brief is never superseded; branch managers reading brief+changelog contact Team Cedar.",
      "fix": "Append '- 2026-10-01: rollout ownership moved from Team Cedar to Team Birch (see ownership.md); supersedes the owner line in brief-2026-09-14.md.' to changelog.md. Do not edit the brief."
    },
    {
      "severity": "P3",
      "evidence_level": "confirmed from brief's own text (lines 3-4) and skill Step 5.6",
      "location": "brief-2026-09-14.md:6",
      "scenario": "Acting on 'fix anything out of date' by editing the owner line in place would make the dated record misstate the 2026-09-14 position and violate its no-edit rule.",
      "fix": "Leave brief-2026-09-14.md unchanged; record the ownership change only as a new dated changelog entry."
    }
  ]
}
```