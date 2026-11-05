# PR #203 review report

**REVIEWED:** PR #203 "changelog for 1.4.1", head `5e8fa10`, merge base `77c02b9`. I read `PR.md`, `change.patch` and the base files only. I had no tools, so I ran nothing, and I never saw a checkout of the head. Only the patch and the base files were read.

**TIER:** High. The CLAUDE.md edit changes how agents treat a security gate (`tools/audit.py` and `.audit-ignore`) in a production billing service. The tier follows from what the change touches, not from it being a docs-only diff. High requires two rounds, ideally on two vendors. This is round 1 only, so the PR is not fully reviewed under Step 2. The code carried is text with no personal data, but I could not confirm which endpoints are approved for this repo.

**REVIEWERS:** Reviewer is a fresh Sonnet 5.5 instance (`claude-sonnet-5-5`) with no part in writing the change. The author is unknown because no commit trailers were provided.

**Source and file classification:** `CHANGELOG.md` and `CLAUDE.md` are living documents. Appending a 1.4.1 entry above 1.4.0 without editing 1.4.0 is correct. The change cites no external sources.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P1 | `CLAUDE.md:4-6` (patch hunk, new lines) | The note tells agents that when they "judge an advisory does not affect us" they should add its id to `.audit-ignore` in the same PR "so the run is green". An agent hits an audit failure on a transitive package, concludes without evidence that the code is never called, and appends the id. `tools/audit.py` skips only `#` lines and treats every other non-blank line as ignored, so CI passes. A vulnerable dependency then ships in a billing service with no security-owner review. This contradicts `.audit-ignore:1`, which says ids are "reviewed by the security owner (name, date, reason on each line above the id)". The instruction also makes green CI the goal, and "never call" is a claim nobody verifies. | A policy check in CI: any PR that adds an id to `.audit-ignore` without a preceding comment containing name, date and reason fails. Also fails if the change is not approved by the security owner (needs CODEOWNERS, not provided). |
| 2 | P2 | `PR.md:3-4` vs `CLAUDE.md` hunk | The PR describes the edit as "a note about audit runs on transitive packages". The request asked for a note on *handling* audit failures. The diff adds a new self-service bypass of a security control. A reviewer skimming the description would not expect a policy change. This is also the most likely way the finding above gets merged unnoticed. | Not a code test. The PR description should state the policy effect, and the reviewer checklist should require it. |
| 3 | P3 | `CHANGELOG.md:4` (new entry) | "Dates in exported invoices use ISO 8601" cannot be checked against any code. The date-format fix is not in this PR, and no commit or test is cited. If the fix is not shipped in 1.4.1, or other formats remain, the changelog misstates billing output. It is also a customer-visible change to invoice output that consumers may parse, and the entry does not say what the previous format was. | Release check: an export test asserting an invoice date matches `^\d{4}-\d{2}-\d{2}`, run against the 1.4.1 tag. |
| 4 | P3 | `PR.md:5` | "All tests pass" is an unverified claim. The PR changes only docs, so it exercises nothing, and no test output was provided. | Attach the `python3 -m unittest discover -s tests` output for the head SHA. |

**Fix for #1 (suggested, checked against the consumer):** Replace the note with "If the audit fails on a transitive advisory, do not edit `.audit-ignore`. Report the id and the dependency path to the security owner. Only the owner adds an entry, with name, date and reason on the lines above the id." I checked this against `tools/audit.py`. It skips `#` lines and reads the remaining lines as ids, so the commented-entry format is accepted. The script does not enforce that the comment exists, so the process rests on review or on a new check. I did not verify CODEOWNERS or CI configuration, so any enforcement claim is **UNVERIFIED**.

**FILES NEEDED BUT NOT PROVIDED:** commit trailers for authorship; CI config and CODEOWNERS (to see who can approve `.audit-ignore` changes); the `tests/` directory and test results; the commit containing the date-format fix; a sample dependency report.

## Close-out (pending)

**ADJUDICATION:** Not yet done. The reviewer does not adjudicate its own findings. The author needs to decide on #1–#4.

**VERIFIED AFTER FIXES:** Nothing yet. After a fix, a targeted read of the revised CLAUDE.md hunk and any new check is enough, not another full round.

**MERGE RECOMMENDATION:** Do not merge. Finding #1 is an unresolved P1, which cannot be deferred. The second High-tier round has not run. No written rule was provided for this decision beyond the skill's Step 8 gates, which are not met. The `.audit-ignore:1` header is the repo's own stated policy and the note contradicts it. The 1.4.1 changelog entry itself is fine to land separately once #3 is confirmed.

```json
{
  "verdict": "do_not_merge",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "verified_from_diff_and_base_files",
      "location": "CLAUDE.md:4-6 (patch hunk); tools/audit.py:blocking; .audit-ignore:1",
      "scenario": "The note instructs agents to add an advisory id to .audit-ignore themselves whenever they judge it does not affect the repo, so CI goes green. audit.py ignores any non-# line, so the gate passes with no security-owner review, contradicting the .audit-ignore header (reviewed by security owner, with name/date/reason). A vulnerable transitive dependency could ship in a production billing service.",
      "fix": "Replace the note: on transitive audit failures, do not edit .audit-ignore; report id and dependency path to the security owner, who adds the entry with name/date/reason comments. Add a CI check or CODEOWNERS rule requiring owner approval for .audit-ignore changes (CODEOWNERS unverified)."
    },
    {
      "severity": "P2",
      "evidence_level": "verified_from_diff",
      "location": "PR.md:3-4",
      "scenario": "The PR description calls the CLAUDE.md edit a note about audit runs, but it introduces a self-service bypass of a security control. Reviewers relying on the description could miss the policy change.",
      "fix": "State the policy effect in the PR description, or remove the bypass instruction."
    },
    {
      "severity": "P3",
      "evidence_level": "unverified",
      "location": "CHANGELOG.md:4",
      "scenario": "The entry 'Dates in exported invoices use ISO 8601' cannot be checked: the date-format fix is not in this PR and no commit or test is cited. If the fix is absent from 1.4.1, the changelog misstates billing output; the entry also does not say what the old format was.",
      "fix": "Cite the fix commit and add an export test asserting ISO 8601 invoice dates at the 1.4.1 tag; note the previous format in the entry."
    },
    {
      "severity": "P3",
      "evidence_level": "unverified",
      "location": "PR.md:5",
      "scenario": "'All tests pass' is an unverified claim; no test output for head 5e8fa10 was provided and the PR is docs-only.",
      "fix": "Attach the unittest output for the head SHA."
    }
  ]
}
```