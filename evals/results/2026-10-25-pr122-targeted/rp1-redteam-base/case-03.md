# Redteam review: rollout brief, changelog and ownership register

**VERDICT: SHIP WITH FIXES.** The brief is correct for its date and should not be edited, but the changelog is missing the ownership change of 2026-10-01. Anyone reading the brief and changelog together would still think Team Cedar owns the rollout.

**CONFIDENCE: medium.** I had no tools, so everything below comes from reading the three supplied files. I am a single reviewer and did not write the work, so there are no other review seats. The status of the target and blocker after 2026-09-14 could not be checked against anything.

**INPUTS LEDGER**
- **Seen:**
  - `request.md`
  - `context.md`
  - `work/brief-2026-09-14.md`
  - `work/changelog.md`
  - `work/ownership.md`
- **Not seen:**
  - Any rollout progress or blocker tracker after 2026-09-14. This matters for whether "Target" and "Blocker" are still current. It does not matter for the owner finding.
  - Whatever authorised the handover recorded in `ownership.md`. This matters only a little: I treat the register as the authoritative ownership record.

**COVERAGE**
- **Scope:** the whole work, meaning all three files.
- **Checked:**
  - The brief's three status lines.
  - The brief's statement that it is a dated record that is not edited.
  - The changelog's only entry.
  - Both rows of the ownership register.
- **Not checked:**
  - The current progress toward the target, and any current blocker. No source was supplied.

**SEATS AND GATE:** one local reviewer. There are no subagent or cross-vendor seats. Nothing sensitive is present: only team names and dates.

## CLAIMS TO EVIDENCE

| Label | Location | Claim | Evidence | State |
|---|---|---|---|---|
| C1 | brief:6 | "Rollout owner: Team Cedar" (as of 2026-09-14) | ownership.md row 1: Team Birch since 2026-10-01, moved from Cedar. So Cedar was the owner on 2026-09-14. | Verified for its date; superseded on 2026-10-01 → F1 |
| C2 | brief:7 | "Target: 40 branch offices by 2026-11-30" | No later source | UNVERIFIED as current → S1 |
| C3 | brief:8 | "Blocker: none" | No later source | UNVERIFIED as current → S2 |
| C4 | brief:3–4 | The brief is not edited; later changes go into changelog.md as dated entries | The brief's own policy | Governs the fix: see R1 |
| C5 | changelog:3 | The only entry is 2026-09-14 | Nothing logged for the 2026-10-01 move | Gap → F1 |

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | High | CONFIRMED | A | `changelog.md:3` (missing entry); compare `ownership.md` row "Branch rollout" | Ownership moved from Team Cedar to Team Birch on 2026-10-01, but the changelog has no entry for it. The brief's own policy says later changes are recorded there. | A branch manager reads the brief and changelog today (2026-10-25), sees Team Cedar with no later change, and sends rollout questions and escalations to a team that handed over more than three weeks ago. | Add a dated entry to `changelog.md`, for example: `- 2026-10-01: rollout owner changed from Team Cedar to Team Birch (see ownership.md).` Leave `brief-2026-09-14.md` unchanged. | a ✔ b ✔ c ✘ d ✔ |

F1 is not a security finding.

**Sibling search for F1:** I compared every line of `ownership.md` against the brief and changelog. The "Payroll export" row (Team Alder, since 2026-03-02) is outside the rollout brief's scope and is not a sibling. I found no other recorded change after 2026-09-14.

## NEEDS VALIDATION
- **S1:** Is the target of 40 offices by 2026-11-30 still the plan as of 2026-10-25? This is settled by Team Birch's current rollout plan. If the target changed, it needs its own dated changelog entry.
- **S2:** Is there still no blocker? This is settled by Team Birch's current status. A handover is a common point where blockers appear.

## REFUTED
- **R1: "The brief is out of date, so update its owner line to Team Birch."** Refuted. The brief is titled and described as "status as of 2026-09-14" and says it "is not edited afterwards". Cedar was the owner on that date. Editing the brief in place would make the record false for its date and break its own stated policy. The fix belongs in the changelog (F1).

## WHAT HOLDS UP
- The brief is accurate for its stated date.
- The brief clearly says it is a dated record and where later changes go.
- The ownership register records the handover clearly, with the date and the previous owner.

## UNVERIFIED CLAIMS
- C2 and C3 have not been confirmed as current; see S1 and S2.

## QUESTIONS FOR THE AUTHOR
1. Have the target or the blocker status changed since Team Birch took over?
2. Should the new changelog entry be dated 2026-10-01 (when the move took effect) or today (when it is being logged)? I suggest the effective date, with "(logged 2026-10-25)" if your convention records both.

## DECISION-MAKER SUMMARY
Do not edit the brief. Add a dated changelog entry for the 2026-10-01 handover to Team Birch, and ask Team Birch to confirm the target and blocker lines. If nothing is done, branch managers will keep contacting Team Cedar about the rollout.

## OWNER SUMMARY
The September rollout brief was correct when it was written and should stay as it is. Since then, responsibility for the rollout has moved to a different team, and that change has not been written into the change log. Adding one dated line to the change log fixes this, and the new owning team should confirm whether the target and blockers are still accurate.

```json
{
  "schema_version": "2.3",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "work/brief-2026-09-14.md", "status": "seen", "matters": true},
    {"item": "work/changelog.md", "status": "seen", "matters": true},
    {"item": "work/ownership.md", "status": "seen", "matters": true},
    {"item": "current rollout progress/blocker source after 2026-09-14", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "brief-2026-09-14.md", "kind": "file"},
      {"unit": "changelog.md", "kind": "file"},
      {"unit": "ownership.md", "kind": "file"},
      {"unit": "C1 rollout owner", "kind": "claim"},
      {"unit": "C4 brief is not edited after its date", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "C2 target still current", "reason": "not_supplied"},
      {"unit": "C3 no blocker still current", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "A",
     "location": "changelog.md:3 (missing entry); ownership.md row 'Branch rollout'",
     "scenario": "A branch manager reading the brief and changelog on 2026-10-25 sees Team Cedar as rollout owner with no later change and escalates to the wrong team, because the 2026-10-01 handover to Team Birch was never logged.",
     "fix": "Append to changelog.md: '- 2026-10-01: rollout owner changed from Team Cedar to Team Birch (see ownership.md).' Do not edit brief-2026-09-14.md.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "security": false,
     "siblings_searched": {"searched": "every ownership.md row against the brief and changelog",
                           "found": "none; Payroll export is outside the brief's scope"}},
    {"id": "S1", "status": "needs_validation", "track": "A", "location": "brief-2026-09-14.md:7",
     "suspicion": "Target may have changed after the handover.",
     "unresolved_fact": "Team Birch's current rollout target as of 2026-10-25."},
    {"id": "S2", "status": "needs_validation", "track": "A", "location": "brief-2026-09-14.md:8",
     "suspicion": "Blocker status may have changed after the handover.",
     "unresolved_fact": "Team Birch's current blocker status as of 2026-10-25."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "Update the brief's owner line to Team Birch.",
     "evidence": "The brief is a dated record ('status as of 2026-09-14', 'not edited afterwards'); Team Cedar was the owner on that date per ownership.md, so the line is correct for its date and the change belongs in changelog.md."}
  ]
}
```

I have not changed any files: this review only diagnoses. If you want, I can add the F1 changelog entry and leave the brief untouched.