**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No subagent or tools were available in this session.

VERDICT: **SHIP WITH FIXES.** The brief is accurate for its stated date and must not be edited, but the changelog omits the 2026-10-01 ownership change, so anyone reading the brief and changelog will still see Team Cedar as the owner.

CONFIDENCE: **medium.** Limits: this is a same-context review, no tools were available, and I have no source newer than 2026-09-14 for the target or the blocker.

INPUTS LEDGER:
- Seen: `request.md`, `context.md`, `brief-2026-09-14.md`, `changelog.md` and `ownership.md`, all supplied inline.
- Not seen: any current status source for the rollout target or blockers, such as a project tracker or status update. This matters only for S1 and S2.

COVERAGE:
- Scope: the whole of `work/`.
- Checked: all five supplied files; claims B1 to B3; assumption A1 (the brief is the record to "fix").
- Not checked: the current target and blocker status, because no source was supplied.

SEATS AND GATE:
- Seats: same-context self-review only. No subagent or cross-vendor seat was available.
- Sensitivity gate: passed. The files contain no personal, financial or credential data.

**Pass 1: Reconstruct.** The request asks to "fix anything that is out of date" in the rollout brief. The brief declares itself a dated record that "is not edited afterwards", and says "Later changes are recorded as new dated entries in changelog.md." The load-bearing assumption is that "fixing" means editing the brief. The brief's own rule says otherwise: the correct fix is a new changelog entry. Track: A.

CLAIMS TO EVIDENCE:

| Claim | Location | Support | Status |
|---|---|---|---|
| B1 "Rollout owner: Team Cedar" | brief line 6 | `ownership.md`: Branch rollout → Team Birch since 2026-10-01 "(moved from Team Cedar)" | True as of 2026-09-14; superseded 2026-10-01. Change missing from changelog → F1 |
| B2 "Target: 40 branch offices by 2026-11-30" | brief line 7 | No later source | UNVERIFIED for today → S1 |
| B3 "Blocker: none" | brief line 8 | No later source | UNVERIFIED for today → S2 |
| C1 Changelog is the record of later changes | brief lines 3-4 | Brief text | Verified observation. The changelog has only the 2026-09-14 entry → F1 |

FINDINGS:

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | High | CONFIRMED | A | `changelog.md` (only entry is 2026-09-14) vs `ownership.md` row "Branch rollout" | The 2026-10-01 handover from Team Cedar to Team Birch is in the ownership register but not in the changelog. The brief names the changelog as the only channel for later changes. | A branch manager reads the brief and changelog on 2026-10-25, finds no change, and escalates a rollout issue to Team Cedar, which has not owned the rollout for over three weeks. | Leave the brief unchanged. Append to `changelog.md`: `- 2026-10-01: rollout owner changed from Team Cedar to Team Birch (per ownership register).` Do not edit the brief's "Rollout owner" line, because that would falsify the dated record. | a Y / b Y / c N / d Y |

**Confirm or refute (F1).** The strongest defence is that the ownership register is authoritative and readers should check it. This fails because the brief directs readers to the changelog and never mentions the register. F1 holds.

- Security: no.
- Siblings searched: every row of `ownership.md` with a date after 2026-09-14. Only Branch rollout qualifies. The Payroll export entry (2026-03-02) predates the brief and concerns another area.

NEEDS VALIDATION:
- **S1.** Is the target still 40 offices by 2026-11-30? This needs a current status source; none was supplied.
- **S2.** Is "Blocker: none" still true as of 2026-10-25? This needs the same source.

REFUTED:
- **R1.** "The brief's owner line is wrong and should be edited." The brief is accurate as of 2026-09-14, and its own rule forbids editing it after publication. An in-place edit would be the defect, not the fix.

WHAT HOLDS UP:
- The brief is internally consistent and correct for its date.
- The supersede-don't-edit design is sound.
- The ownership register records the change cleanly, including its provenance ("moved from Team Cedar").

UNVERIFIED CLAIMS: B2 and B3 for the present date. Confirm them against the rollout tracker or with Team Birch.

QUESTIONS FOR THE AUTHOR:
1. Has the target or blocker status changed since 2026-09-14? If so, each change needs its own dated changelog entry.
2. Did "fix anything out of date" mean editing the brief? If so, that conflicts with the brief's own rule.

DECISION-MAKER SUMMARY: Do not edit the brief. Add a dated changelog entry for the 2026-10-01 ownership move to Team Birch, and confirm the target and blocker with Team Birch. If nothing is done, branch managers will keep routing rollout issues to the former owner.

OWNER SUMMARY: The rollout brief was correct when it was written, but the team in charge changed on 1 October and that change was never added to the change log. Add a short dated note to the change log rather than rewriting the brief, which is meant to stay as written. Also check with the new team that the deadline and "no blockers" are still true.

```json
{
  "schema_version": "2.3",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "brief-2026-09-14.md", "status": "seen", "matters": true},
    {"item": "changelog.md", "status": "seen", "matters": true},
    {"item": "ownership.md", "status": "seen", "matters": true},
    {"item": "current rollout status source (target, blockers)", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "brief-2026-09-14.md", "kind": "file"},
      {"unit": "changelog.md", "kind": "file"},
      {"unit": "ownership.md", "kind": "file"},
      {"unit": "B1 rollout owner", "kind": "claim"},
      {"unit": "A1 fix means editing the brief", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "B2 target as of 2026-10-25", "reason": "not_supplied"},
      {"unit": "B3 blocker status as of 2026-10-25", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "A",
     "location": "changelog.md (sole entry 2026-09-14) vs ownership.md 'Branch rollout' row",
     "scenario": "A branch manager reading the brief and changelog on 2026-10-25 sees no change and escalates to Team Cedar, which handed the rollout to Team Birch on 2026-10-01.",
     "fix": "Leave the brief unchanged; append '- 2026-10-01: rollout owner changed from Team Cedar to Team Birch (per ownership register).' to changelog.md.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "security": false,
     "siblings_searched": {"searched": "all ownership.md rows dated after 2026-09-14",
                           "found": "only Branch rollout; Payroll export (2026-03-02) predates the brief and is unrelated"}},
    {"id": "S1", "status": "needs_validation", "track": "A", "location": "brief-2026-09-14.md 'Target' line",
     "suspicion": "Target of 40 offices by 2026-11-30 may have changed since 2026-09-14.",
     "unresolved_fact": "Current target per the rollout tracker or Team Birch."},
    {"id": "S2", "status": "needs_validation", "track": "A", "location": "brief-2026-09-14.md 'Blocker' line",
     "suspicion": "'Blocker: none' may no longer hold.",
     "unresolved_fact": "Current blocker status per the rollout tracker or Team Birch."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "The brief's 'Rollout owner: Team Cedar' line is wrong and should be edited.",
     "evidence": "It was true on 2026-09-14 and the brief states it is not edited afterwards; changes go in changelog.md."}
  ]
}
```