# PR #203 review report

**REVIEWED:** PR #203 "changelog for 1.4.1", head `5e8fa10`, merge base `77c02b9` (short SHAs as given in PR.md; full SHAs not provided). I read the patch and base files only. I could not run anything or open any link, and this was not done in a worktree.

**TIER: High.** The CLAUDE.md change tells agents how to modify `.audit-ignore`, which is the allowlist for the security audit gate. That header says its entries are "reviewed by the security owner". This is a permissions and security-control change on a production billing service, so the docs-only size doesn't make it Low.
- **Only one round has run.** High needs two, ideally on two vendors, so the High-tier requirement is not met.
- **Data handling (Step 3).** The diff carries no personal or billing data, and no approved-endpoint list was provided. I'm assuming this session is an approved reviewer; the owner should confirm.

**REVIEWERS:** this instance (Sonnet 5.5, a fresh reviewer with no memory of writing the change). The author could not be determined because no commit trailers were provided.

## Findings

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P1 | `CLAUDE.md:4-6` | The new text tells an agent to add an advisory id to `.audit-ignore` whenever it "judges" the advisory doesn't affect us, in the same PR, "so the run is green". `tools/audit.py` suppresses any id listed there, with no check on who added it. An agent hits a critical advisory in a transitive package used on a billing path and misjudges reachability. It adds the id, CI goes green, and the advisory is silently suppressed. This bypasses the security-owner review that the `.audit-ignore` header requires (name, date and reason on each entry). The instruction also frames "make CI green" as the goal. | A CI check that fails any PR adding a line to `.audit-ignore` unless the line is preceded by a comment with name, date and reason, and the PR has a security-owner approval. A fixture PR that adds a bare id must fail. |
| 2 | P2 | `CLAUDE.md:4-5` | The note says the audit "often fails on advisories in transitive packages we never call". That is an unsupported claim, and `.audit-ignore` is empty in the base, so there is no record of such cases. It primes agents to treat failures as noise. | Doc review: cite the past failures, or remove the claim. |
| 3 | P2 | `CHANGELOG.md:3-4` | The entry claims "Dates in exported invoices use ISO 8601", but the PR contains no code change or test for the date-format fix. I can't confirm the fix is in 1.4.1 or that it behaves as stated. Invoice consumers that parse the old format would also be affected, and the entry gives no migration note. | Confirm the fix commit is in the 1.4.1 range. Add or point to a test asserting ISO 8601 invoice dates. |
| 4 | P3 | `PR.md` (description) | "All tests pass" is an assertion with no output. The PR is docs-only, so it says little. No CI check list was provided, and a missing check is not green. | Attach the CI run for `5e8fa10`. |

**Scope check against the request.** The changelog entry matches the request. The CLAUDE.md note goes beyond "a note on handling audit failures". It adds an authorization (agents may self-ignore advisories) that the request did not ask for.

**Suggested fix for #1 (UNVERIFIED).** Replace the instruction with "report the advisory id, the package and why you think it's unreachable to the security owner; do not edit `.audit-ignore`". Enforce this with a CODEOWNERS rule on `.audit-ignore`. I saw no CODEOWNERS or branch-protection config, so I haven't checked that the rule would apply. `audit.py` also doesn't enforce the name/date/reason format, because it skips `#` lines and accepts any id line.

**No reviewer-directed text** was found in the description, diff or files.

**FILES NEEDED BUT NOT PROVIDED:** commit trailers (authorship), CI check results, the commit or diff that implements the date-format fix, any CODEOWNERS or branch-protection config.

## Close-out (pending)

Adjudication has not been done. The author must adjudicate findings 1–4 before the PR is closed.

**MERGE RECOMMENDATION: do not merge as-is.** Finding 1 is an unresolved P1, which cannot be deferred. The High-tier second round has not run, and CI status is unknown. No written rule was provided to cite. After the CLAUDE.md note is rewritten, a targeted read of that diff and a second High-tier round would be needed. The changelog entry is fine once the fix commit is confirmed.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "confirmed by reading patch and tools/audit.py",
      "location": "CLAUDE.md:4-6",
      "scenario": "The note instructs agents to add advisory ids to .audit-ignore on their own judgment so CI goes green. audit.py suppresses any listed id with no ownership check, so a misjudged advisory in a transitive package on a billing service is silently suppressed, bypassing the security-owner review the .audit-ignore header requires.",
      "fix": "Replace with an instruction to report the advisory to the security owner and not edit .audit-ignore; enforce with CODEOWNERS and a CI check requiring name/date/reason on each entry (UNVERIFIED: no CODEOWNERS or branch-protection config seen)."
    },
    {
      "severity": "P2",
      "evidence_level": "inferred, no supporting record in the files provided",
      "location": "CLAUDE.md:4-5",
      "scenario": "The claim that the audit 'often fails on advisories in transitive packages we never call' is unsupported (.audit-ignore is empty in base) and encourages treating failures as noise.",
      "fix": "Cite past failures or remove the claim."
    },
    {
      "severity": "P2",
      "evidence_level": "unverified, fix commit not in the patch",
      "location": "CHANGELOG.md:3-4",
      "scenario": "The entry says invoice dates use ISO 8601 but the PR has no code or test for the date-format fix, so the claim cannot be confirmed. Downstream invoice consumers may be affected and no migration note is given.",
      "fix": "Confirm the fix commit is in the 1.4.1 range, reference its test, and add a note on the format change."
    },
    {
      "severity": "P3",
      "evidence_level": "unverified assertion",
      "location": "PR.md",
      "scenario": "'All tests pass' is stated without output and no CI check list was provided; a missing check is not green.",
      "fix": "Attach the CI run for head 5e8fa10."
    }
  ]
}
```