VERDICT: try. The post serves goal 4, but our nightly `changelog.py` already does most of this job, so the only new part is grouping entries by change type. Borrow that idea into `changelog.py` for one weekly cycle instead of adopting the post's hook and script.

WHAT IT IS: Post "Changelogs from commit trailers, step by step", https://posts.example.test/changelog-from-trailers, posted 2026-09-17. The snapshot does not name an author. I read it from a saved snapshot captured 2026-10-08 (work/snapshot.md, work/meta.json), not live. The post gives no license for its code. The snapshot contains no text that tries to direct the reader.

CLAIMS CHECKED:
- "This explains building a changelog from commit trailers" (the sender's words). **CONFIRMED.** The post describes a trailer-based pipeline and includes the full script.
- "A 21-line script." **CONFIRMED.** The listing is 21 lines, counting blank lines. Not load-bearing.
- "Reads `git log` since the last tag." **CONFIRMED (load-bearing).** It uses `git describe --tags --abbrev=0` and then `git log {tag}..HEAD`. Because of `check=True`, it fails in a repo with no tags. It is also scoped to releases, not to a week.
- "Groups lines by trailer type and writes the markdown." **CONFIRMED (load-bearing), with gaps visible in the code:**
  - It prints only `added`, `changed`, `fixed` and `removed`. Any other trailer value is dropped silently.
  - Commits with no `Change:` trailer are skipped.
  - Only the first `Change:` line of each commit is used.
- "A commit-msg hook adds a `Change:` trailer from the first word of the subject (`Fix the retry` becomes `Change: fixed`)." **UNVERIFIED.** The post does not show the hook, so neither the word mapping nor what happens to subjects like "Update …" or "Bump …" can be checked. Not load-bearing.
- "…so nobody types one." **PROBABLE**, if the hook exists and each developer installs it. Not load-bearing.
- "On the sample repo it prints `## Changes since v0.3.0`, then `### Added` and `### Fixed`." **UNVERIFIED.** The sample repo is not in the snapshot. The output is consistent with the code. Not load-bearing.

FIT:
- **Goal:** Goal 4, "Ship a weekly changelog without manual work."
- **Overlap:** High. The nightly cron script `changelog.py` already builds a changelog draft from commit messages. The hook derives the trailer only from the subject's first word, so the trailer adds no information the subject doesn't already have. `changelog.py` can do the same grouping directly from subjects, with no hook and no trailers. What the post adds is the idea of grouping by change type.
- **Burden:**
  - Adopting the post as written means a commit-msg hook that every developer must install locally (git hooks are not cloned), plus a second changelog script beside `changelog.py`.
  - Borrowing only the grouping means one change to `changelog.py`.
- **Cost:** Free. No account or service is involved.
- **Risks:**
  - The code has no stated license, so reimplement the idea rather than vendoring the 21 lines.
  - The tag-based range does not match a weekly cadence and fails with no tags.
  - Unmapped change types are dropped silently.
  - No data leaves the machine.

NEXT ACTION:
- **Action:** Add first-word grouping (Added, Changed, Fixed, Removed, plus an "Other" bucket so nothing is dropped) to `changelog.py` over the last 7 days of commits, and compare one week's draft with the current output.
- **Owner:** Operator, or whoever maintains `changelog.py`.
- **Done when:** One weekly draft has been produced both ways, and the edits needed before shipping each have been compared.
- **Stop condition:** Stop if the grouped draft needs as much manual editing as the current one, or if `changelog.py` already groups by type.
- **Hand-off:** `harvest`, to borrow the grouping idea from the post.

CONFIDENCE: Medium. The post is resolved from a saved copy (2026-10-08, not live), and the claims the verdict rests on are confirmed from the code itself. Two things limit confidence: I cannot see what `changelog.py` already does, so the overlap may be total, and the hook the post relies on is not shown.

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "post",
           "identity": "\"Changelogs from commit trailers, step by step\", https://posts.example.test/changelog-from-trailers, posted 2026-09-17, author not named; read from snapshot captured 2026-10-08; no license stated for the code",
           "resolved": true},
  "claims": [
    {"claim": "the post explains building a changelog from commit trailers (sender)", "evidence": "snapshot describes the trailer pipeline and lists the full script", "status": "CONFIRMED", "load_bearing": false},
    {"claim": "the script is 21 lines", "evidence": "the listing in the snapshot is 21 lines including blanks", "status": "CONFIRMED", "load_bearing": false},
    {"claim": "the script reads git log since the last tag", "evidence": "code: git describe --tags --abbrev=0, then git log {tag}..HEAD; check=True means it fails with no tags", "status": "CONFIRMED"},
    {"claim": "the script groups lines by trailer type and writes markdown", "evidence": "code groups by the Change trailer value and prints only added/changed/fixed/removed; other values and commits without a trailer are dropped silently", "status": "CONFIRMED"},
    {"claim": "a commit-msg hook adds a Change: trailer from the subject's first word", "evidence": "described in the post; the hook code is not shown", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "so nobody types a trailer", "evidence": "follows if the hook exists and is installed by each developer; git hooks are not cloned", "status": "PROBABLE", "load_bearing": false},
    {"claim": "on the sample repo it prints Changes since v0.3.0 with Added and Fixed lists", "evidence": "sample repository is not in the snapshot; consistent with the code", "status": "UNVERIFIED", "load_bearing": false}
  ],
  "fit": {"goal": "ship a weekly changelog without manual work (goal 4)",
          "overlap": "changelog.py (nightly cron) already builds a changelog draft from commit messages; the trailer is derived only from the subject's first word, so changelog.py can group from subjects directly",
          "burden": "as written: a per-developer commit-msg hook plus a second changelog script; borrowed: one change to changelog.py",
          "risks": ["no license stated for the code: reimplement, do not vendor",
                    "range is since the last tag, not weekly, and fails with no tags",
                    "unmapped change types are silently dropped",
                    "no data leaves the machine"],
          "cost": {"price": "free", "tier": "n/a (blog post)", "limits": "none", "terms": "no license stated for the code",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Add first-word grouping (Added/Changed/Fixed/Removed plus Other) to changelog.py over the last 7 days of commits and compare one week's draft with the current output",
                  "owner": "operator (or the maintainer of changelog.py)",
                  "done_when": "one weekly draft has been produced both ways and the manual edits each needs are compared",
                  "stop_condition": "stop if the grouped draft needs as much manual editing as the current one, or if changelog.py already groups by type",
                  "handoff": "harvest"},
  "confidence": "medium",
  "context_file": "present"
}
```