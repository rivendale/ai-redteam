# PR Review: Rollout brief status record (Track A)

## Review report

**REVIEWED:** The work under review is three files supplied inline: `brief-2026-09-14.md`, `changelog.md` and `ownership.md`. There is no PR number, no head SHA and no merge base. These files are not in a git repository, and this session has no tools. **Step 1 is not satisfied.** This review covers the file contents exactly as quoted in the inputs. Whoever applies the fix should record the commit it lands on.

**TIER: Low.** The change is docs only: a dated status record and its changelog. It touches no auth, permissions, secrets, network exposure or data handling. The context gives the stakes as low; branch managers read the brief. One independent read is enough.

**REVIEWERS:** This session (Claude Opus 5.5, `claude-opus-5-5`) is the reviewer. It did not write these files and has no memory of authoring them. The author is unknown because no commit trailers are available. No data left this session.

**Scope check against the request.** The request says to "fix anything that is out of date". The brief says of itself that it "states the position on its date and is not edited afterwards. Later changes are recorded as new dated entries in changelog.md" (`brief-2026-09-14.md:3-4`). So the correct fix for an out-of-date fact is a new changelog entry. Rewriting the brief is wrong. If `brief-2026-09-14.md:6` were changed to "Team Birch", the record would claim that Birch owned the rollout on 2026-09-14, which is false. The ownership register says Birch has owned it only since 2026-10-01.

### FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `changelog.md:3` (missing entry after this line); stale fact at `brief-2026-09-14.md:6` | `ownership.md:5` records that branch rollout moved from Team Cedar to Team Birch on 2026-10-01. The changelog has no entry for this change, and its only entry is dated 2026-09-14. A branch manager who reads the brief and changelog on 2026-10-25 concludes that Team Cedar still owns the rollout, so escalations and questions go to the wrong team. The workaround is to cross-check the ownership register. | Write a consistency check: for every owner change in `ownership.md` dated after the brief's date, require a changelog entry on that date naming both the old and new owner. It fails today because 2026-10-01 has no entry, and it passes once the entry is added. A second check should confirm that `brief-2026-09-14.md` is byte-identical to its published version. |

**Proposed fix (not applied; no tools):** Append to `changelog.md`:

```markdown
- 2026-10-01: rollout owner changed from Team Cedar to Team Birch (see ownership.md).
```

Leave `brief-2026-09-14.md` unchanged.

**Not findings (no evidence of staleness):**
- **Target** (`brief-2026-09-14.md:7`, "40 branch offices by 2026-11-30"): no supplied file contradicts it, and the date is still in the future.
- **Blocker** (`brief-2026-09-14.md:8`, "none"): no supplied file contradicts it.

Either fact may have drifted since 2026-09-14, but nothing in the inputs shows that it has. I have not raised findings without evidence.

**FILES NEEDED BUT NOT PROVIDED:**
- The commit history or PR for these files, needed for the head and base SHAs and the author trailers.
- A current status source, such as a rollout tracker or blocker log, needed to confirm whether the target and the "Blocker: none" line are still accurate as of 2026-10-25.

## Close-out

A reviewer never adjudicates its own findings, so the author or the person closing the PR must fill this in.

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | *Pending (author)* | No test framework applies because this is docs only. The evidence that a fix is right would be the new changelog line, matching `ownership.md:5`, plus an unchanged diff of `brief-2026-09-14.md`. |

**VERIFIED AFTER FIXES:** None. No fix has been applied. When the fix lands, read its diff to confirm two things: only `changelog.md` changed, and the entry's date and team names match `ownership.md:5`.

**MERGE RECOMMENDATION: merge after fixes.** Finding 1 needs a written decision, ideally Accepted with the changelog entry above. Without a fix, branch managers are pointed at the wrong owner. Three items remain open:
1. No SHAs are recorded, because Step 1 could not be done.
2. No checks were shown, and a missing check is not a green check.
3. Without the status source listed above, the target and blocker lines remain unverified.

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "direct (ownership.md:5 contradicts brief-2026-09-14.md:6; changelog.md has no entry after 2026-09-14)",
      "location": "changelog.md:3 (missing entry); stale fact at brief-2026-09-14.md:6",
      "scenario": "Rollout ownership moved from Team Cedar to Team Birch on 2026-10-01, but the changelog has no entry for it. Branch managers reading the brief and changelog on 2026-10-25 send rollout questions and escalations to Team Cedar instead of Team Birch.",
      "fix": "Append '- 2026-10-01: rollout owner changed from Team Cedar to Team Birch (see ownership.md).' to changelog.md. Do not edit brief-2026-09-14.md: it is a dated record, and rewriting line 6 would falsely state Birch owned the rollout on 2026-09-14."
    }
  ]
}
```