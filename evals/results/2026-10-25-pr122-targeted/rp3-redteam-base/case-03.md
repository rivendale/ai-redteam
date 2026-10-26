# Redteam review: rollout brief, changelog, ownership register

**VERDICT: SHIP WITH FIXES.** The brief is accurate for its own date, but the record set is out of date. The owner changed on 2026-10-01 and the changelog never recorded it. The fix belongs in `changelog.md`, not in the brief.

**CONFIDENCE: medium.** I had no tools and no subagent, so this is a single-reviewer pass over the pasted text only. I could not confirm whether the ownership register itself is authoritative.

**INPUTS LEDGER**
- Seen: `request.md`, `context.md`, `brief-2026-09-14.md`, `changelog.md`, `ownership.md`. All were pasted inline.
- Not seen: anything showing whether the 2026-11-30 target or the "Blocker: none" line still hold today (2026-10-25). This matters for completeness, not for the finding below.

**COVERAGE**
- Scope: the whole work, which is three files.
- Checked: each brief field (owner, target, blocker), the brief's editing policy, the changelog entries, and both ownership rows.
- Not checked: the current target and blocker status (`not_supplied`), and who changed the register and on what authority (`not_supplied`).

**SEATS AND GATE:** Same-reviewer pass only, with no fresh subagent available. The sensitivity gate passed: the files contain no personal or confidential data. No cross-vendor seats were used.

**CLAIMS TO EVIDENCE**

| Claim | Source | State |
|---|---|---|
| C1: "Rollout owner: Team Cedar" (brief, line 6) | Brief as of 2026-09-14; `ownership.md` agrees it was Cedar until 2026-10-01 | Verified for its date; superseded since 2026-10-01 → F1 |
| C2: "Target: 40 branch offices by 2026-11-30" | Brief only | UNVERIFIED for today → S2 |
| C3: "Blocker: none" | Brief only | UNVERIFIED for today → S2 |
| C4: The brief is not edited; later changes go to the changelog (brief, lines 3–4) | Brief | Stated policy, so it governs how F1 is fixed |
| C5: Branch rollout owner is Team Birch since 2026-10-01 | `ownership.md`, row 1 | Observed; authority UNVERIFIED → S1 |

**FINDINGS**

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | High | CONFIRMED | A | `changelog.md` (only entry is 2026-09-14); `ownership.md` row "Branch rollout" | The owner moved from Team Cedar to Team Birch on 2026-10-01. The brief's own policy says such changes are recorded as dated changelog entries, but no entry exists. | A branch manager reads the brief and the changelog and sees no change. They route rollout questions or escalations to Team Cedar, which has not owned the rollout for 24 days. | Add to `changelog.md`: `- 2026-10-01: rollout owner moved from Team Cedar to Team Birch (recorded 2026-10-25; see ownership.md).` Leave the brief unchanged. | a ✓ b ✓ c ✗ d ✓ |

- **Why High despite low stakes:** the rubric gives High when a, b and d hold, and this is exactly the "out of date" item the request asked about. The practical harm is misrouted questions, not data loss.
- **Siblings searched:** I checked the brief's other fields (target, blocker) against every supplied file. No source contradicts them, but none confirms them either (see S2). The Payroll export row is unrelated to the brief.
- **Security:** not a security finding.

**NEEDS VALIDATION**
- **S1:** The register is the only evidence of the owner change. Settle it by confirming that the register is the system of record for ownership, or by getting confirmation from Team Birch or Team Cedar.
- **S2:** The target and blocker may also have changed since 2026-09-14. Settle it by asking the current owner (Birch) for the target and blocker status as of today. If either changed, add another dated changelog entry.

**REFUTED**
- **"Edit the brief's owner line to Team Birch."** The brief was correct on its date. Its stated policy (lines 3–4) forbids editing it afterwards. Editing it would destroy the dated record and make the changelog contradict the history. So the brief is not wrong; the changelog is incomplete.

**WHAT HOLDS UP**
- The brief is internally consistent and correct as of 2026-09-14.
- Its "dated record plus changelog" design is sound.
- The register records the change with a date and the previous owner, which makes the gap easy to close.

**UNVERIFIED CLAIMS**
- C2 and C3 are unconfirmed for today; confirm them with the owning team.
- C5 is unconfirmed as authoritative; confirm it against the system of record.

**QUESTIONS FOR THE AUTHOR**
1. Is `ownership.md` the authoritative source for owners?
2. Have the target or blocker changed since 2026-09-14?

**DECISION-MAKER SUMMARY:** Add one changelog entry recording the 2026-10-01 handover to Team Birch, and do not edit the brief. Then confirm the target and blocker with Birch. If nothing is done, branch managers will keep contacting the wrong team.

**OWNER SUMMARY:** The rollout brief was right when it was written, but the team running the rollout changed on 1 October and the change log was never updated. Readers will still think the old team is in charge. Adding one line to the change log fixes this, and it is also worth checking that the deadline and "no blockers" status are still true.

I haven't edited any files. If you want, I can add the changelog line shown in F1.

```json
{
  "schema_version": "2.3",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "brief-2026-09-14.md", "status": "seen", "matters": true},
    {"item": "changelog.md", "status": "seen", "matters": true},
    {"item": "ownership.md", "status": "seen", "matters": true},
    {"item": "current target/blocker status source", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "brief-2026-09-14.md", "kind": "document"},
      {"unit": "changelog.md", "kind": "document"},
      {"unit": "ownership.md", "kind": "document"},
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "C1 rollout owner", "kind": "claim"},
      {"unit": "C4 dated-record policy", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "C2/C3 target and blocker as of 2026-10-25", "reason": "not_supplied"},
      {"unit": "authority of ownership.md", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {
      "id": "F1",
      "status": "confirmed",
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "track": "A",
      "location": "changelog.md (only entry 2026-09-14); ownership.md row 'Branch rollout'",
      "scenario": "Ownership moved from Team Cedar to Team Birch on 2026-10-01, but the changelog has no entry; branch managers reading brief + changelog route rollout questions to Team Cedar.",
      "fix": "Append to changelog.md: '- 2026-10-01: rollout owner moved from Team Cedar to Team Birch (recorded 2026-10-25; see ownership.md).' Do not edit the dated brief.",
      "answers": {"a": true, "b": true, "c": false, "d": true},
      "security": false,
      "siblings_searched": {
        "searched": "brief fields target and blocker against changelog.md and ownership.md",
        "found": "no contradicting source; their current status is unverified (needs validation)"
      }
    }
  ],
  "refuted": [
    {
      "id": "C1",
      "candidate": "Edit the brief's owner line to Team Birch.",
      "evidence": "brief-2026-09-14.md states it is a dated record not edited afterwards; it was correct on 2026-09-14."
    }
  ]
}
```