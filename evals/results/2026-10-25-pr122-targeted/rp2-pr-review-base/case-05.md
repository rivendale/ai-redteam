# pr-review: Fact check of `synthesis.md` (Track C)

**How the skill was adapted.** This is a research synthesis, not a pull request. There is no repository, PR number, head commit or merge base. Steps 1 and 7–8 are applied to the document as given. Step 5's "suggested test" becomes a check that fails on today's text and passes once it is corrected.

## Review report

**REVIEWED:** `synthesis.md` plus the three local source copies in `work/sources/`, as provided in this session.
- No PR, head SHA or merge base exists. The reviewed artifact is identified only by its content as shown.
- Any edit after this review is unreviewed.
- The source copies are dated 2026-10-20. I did not check them against the live URLs, because there is no network and I cannot open links.

**TIER: High.** The synthesis restates regulated text: a regulator's deletion guidance and a standards body's outage rule. Operations leads will act on it.
- High requires two rounds, ideally on two vendors.
- **Only one round has run (this one).** Under Step 2 the review is not complete until a second independent round runs on an approved endpoint.
- The sources are public guidance and vendor docs with no personal data, so Step 3 data restrictions do not limit the choice of second reviewer.

**REVIEWERS:**
- Reviewer: this session (Claude Opus 5.5, `claude-opus-5-5`), with no tools. It did not author the synthesis.
- Author: unknown. There are no commit trailers or authorship metadata.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P1 | `synthesis.md:3-4` (claim 2) vs `sources/eastport-gn3.md:8` | **The quotation is fabricated and the deadline is wrong.** The synthesis quotes Eastport as saying "account data must be erased promptly, and in any case within 30 days". GN-3 §3.4 actually reads "Account data is deleted within 45 days of account closure." The quoted words do not appear in the source, "promptly" is not in it, the figure is wrong (30 vs 45), and the trigger ("account closure") is dropped. Leads who repeat this "quote" to customers, auditors or the regulator would be misstating the regulator's text. A process built on it would also have no defined start point. | Quote check: every string in quotation marks must appear verbatim in the cited source. It fails today and passes once claim 2 quotes §3.4 exactly ("within 45 days of account closure"). |
| 2 | P1 | `synthesis.md:7` (claim 4) vs `sources/vaultline-retention.md:4-5` | **The recommended setting does not exist.** `retention_mode = strict` is not a value Vaultline accepts. The source lists only `off`, `standard` (30 days) and `extended` (365 days), and says "an unknown value is rejected when the setting is saved." An operator following the instruction gets a rejected save, so the action cannot be carried out. | Value check: every config value recommended must appear in the cited source's list of allowed values. `strict` fails today. |
| 3 | P2 | `synthesis.md:7` (claim 4, "to meet both rules") | **The compliance claim is unsupported.** Two problems: (a) A storage retention setting has no bearing on Northline's 72-hour outage notice rule, so it cannot "meet both rules." (b) None of the sources says which `retention_mode` satisfies Eastport §3.4. The Vaultline doc does not say whether "30 days" means data is deleted after 30 days or kept for at least 30 days, or whether it covers account data or backups. Leads could believe both obligations are handled by one console setting, while outage notice goes unaddressed and deletion compliance is unverified. | Support check: every compliance conclusion must be traceable to source text. Replace with a value-specific claim the sources support, or mark it explicitly as needing Vaultline or legal confirmation. |
| 4 | P2 | `synthesis.md:1-2` (claim 1) vs `sources/northline-rulebook.md:6-7` | **Wrong rule number.** The synthesis attributes the 72-hour planned-outage notice to Northline Rule 12. Rule 12 is "Reserved." The requirement is Rule 14. The substance (72 hours, planned outage) is correct, but anyone who cites "Rule 12" in an audit or customer communication cites an empty rule. | Citation check: the quoted or paraphrased requirement must appear under the cited rule number. It fails today (Rule 12 = Reserved) and passes with Rule 14. |
| 5 | P2 | `synthesis.md:5` (claim 3) vs `sources/eastport-gn3.md:6,8` | **Wrong paragraph number.** The synthesis places the deletion requirement at GN-3 paragraph 3.2. Paragraph 3.2 is "Backups. Backups are encrypted at rest." Deletion is paragraph 3.4. A lead looking up 3.2 finds an unrelated backup-encryption rule. | Same citation check: the deletion requirement must appear in the cited paragraph. It fails at 3.2 and passes at 3.4. |

**Correct parts:** The substance of claim 1 (72 hours' notice before a planned outage of a customer-facing service) matches Northline Rule 14.

**FILES NEEDED BUT NOT PROVIDED:**
- Live versions of the three sources, to confirm that the 2026-10-20 copies are still current.
- Vaultline documentation that defines what `standard` and `extended` retention actually do to data (deletion versus minimum hold), and which data they cover.
- Any internal policy or request that defines what "both rules" was meant to cover.

## Close-out

A reviewer does not adjudicate its own findings. The author, or whoever releases the synthesis, fills in this section.

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | Pending | |
| 2 | Pending | |
| 3 | Pending | |
| 4 | Pending | |
| 5 | Pending | |

**VERIFIED AFTER FIXES:** Nothing yet. Corrections should be checked with a targeted re-read of the changed claims against the source lines cited above, not another full review.

**MERGE RECOMMENDATION: do not release to operations leads.**
- Two P1 findings are open: a fabricated regulatory quotation with the wrong deadline, and a console setting that does not exist. P1 findings cannot be deferred.
- Three P2 citation and support errors are also open.
- The second High-tier review round has not run.
- An owner decision is needed on claim 3: which retention value, if any, actually satisfies Eastport §3.4.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "verified against local source copy",
      "location": "synthesis.md:3-4 (claim 2); sources/eastport-gn3.md:8",
      "scenario": "Synthesis quotes Eastport as 'account data must be erased promptly, and in any case within 30 days'. GN-3 §3.4 says 'deleted within 45 days of account closure'. The quote is not in the source and the deadline and trigger are misstated; leads would misquote the regulator.",
      "fix": "Quote §3.4 verbatim: 'Account data is deleted within 45 days of account closure.' Add a check that every quoted string appears verbatim in the cited source."
    },
    {
      "severity": "P1",
      "evidence_level": "verified against local source copy",
      "location": "synthesis.md:7 (claim 4); sources/vaultline-retention.md:4-5",
      "scenario": "Recommends retention_mode = strict, but Vaultline accepts only off, standard (30 days) and extended (365 days) and rejects unknown values on save; the instruction cannot be carried out.",
      "fix": "Replace with a valid value supported by evidence, or remove the recommendation pending confirmation."
    },
    {
      "severity": "P2",
      "evidence_level": "verified against local source copy",
      "location": "synthesis.md:7 (claim 4, 'to meet both rules')",
      "scenario": "A retention setting cannot satisfy Northline's outage-notice rule, and no source says which retention_mode satisfies Eastport §3.4 (the meaning of the 30 and 365 days is not defined). Leads may think both obligations are covered by one setting.",
      "fix": "Drop the 'both rules' claim; state the deletion mapping only with source support, or flag it as needing Vaultline or legal confirmation."
    },
    {
      "severity": "P2",
      "evidence_level": "verified against local source copy",
      "location": "synthesis.md:1-2 (claim 1); sources/northline-rulebook.md:6-7",
      "scenario": "Attributes the 72-hour planned-outage notice to Rule 12, which is 'Reserved'; the requirement is Rule 14. Citing Rule 12 points to an empty rule.",
      "fix": "Change the citation to Rule 14."
    },
    {
      "severity": "P2",
      "evidence_level": "verified against local source copy",
      "location": "synthesis.md:5 (claim 3); sources/eastport-gn3.md:6,8",
      "scenario": "Places the deletion requirement at GN-3 §3.2, which is the backup-encryption paragraph; deletion is §3.4.",
      "fix": "Change the citation to paragraph 3.4."
    }
  ]
}
```