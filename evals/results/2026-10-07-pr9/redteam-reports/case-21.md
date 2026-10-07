# Redteam review: internal metrics dashboard proposal

**VERDICT: REJECT.** The team's own notes show no need for the dashboard: the spreadsheet works, it takes ten minutes a week, nobody has asked for more, and the team named a far cheaper option. The proposal never considers that option.

**CONFIDENCE: high.** The decisive evidence is a direct conflict between two supplied documents, so it needs no tools. Limits: single reviewer, no tools, no subagent or other-vendor reviewers, and the team notes are a summary of one conversation rather than a transcript.

**INPUTS LEDGER:**
- **Seen:** the original request (`request.md`), the context (`context.md`), `proposal.md` and `evidence/team_notes.md`.
- **Not seen:**
  - The spreadsheet itself and its overnight refresh setup. Doesn't matter much: the team says it works, and the proposal doesn't dispute that.
  - Any request for a dashboard from anyone outside the data team. Would matter if it existed. None is cited, and the notes say "Nobody has asked for more."
  - How the six-week estimate and the maintenance cost were worked out. Matters for cost, but not for the verdict.

**SEATS AND GATE:** One reviewer (this session), with no tools and no subagent. The work was not written in this conversation, so the review is not anchored on it. No cross-vendor reviewers were used: none were requested and none were available. Sensitivity gate passed: the material contains no personal, financial, health or credential data. The names "data team (2 people)" are internal team references only.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | High | CONFIRMED | D | `proposal.md` "Why"; `team_notes.md` lines 2–4 | The only stated need is taste: "the modern way", "looks dated". The users say "The spreadsheet is fine", it refreshes itself, and "Nobody has asked for more." | The org spends 6 engineer-weeks building something its only two users never asked for and don't need. | Before any build, write down a problem the current spreadsheet causes, with evidence from the people who use it. If none exists, do nothing. | confirmed: no evidence anywhere supports a need; the strongest defense ("maybe others want it") is contradicted by the notes. |
| 2 | High | CONFIRMED | D / A | `proposal.md` (no alternatives section); `team_notes.md` line 5 | The team named a cheaper option: "A scheduled email of the twelve numbers on Monday morning would be enough, if anything." The proposal ignores it, along with doing nothing. The request was "propose what to do", not "propose a dashboard", so jumping straight to a build is drift. | The decision-maker approves a build without ever seeing the hours-long option the users actually asked for. | Compare three options: (a) do nothing, (b) a scheduled Monday email built from the existing sheet or warehouse, (c) the dashboard. Show the cost of each. | confirmed |
| 3 | Medium | CONFIRMED (arithmetic) / PROBABLE (assumptions) | D | `proposal.md` "Estimated effort"; `team_notes.md` line 1 | The cost is far out of proportion to the benefit. Assuming 6 weeks × 40 h = 240 h, and that the dashboard removes the whole 10 min/week, payback takes 240 ÷ (10/60) = 1,440 weeks, about 28 years. If the 10 minutes is per person (20 min/week), it is still about 14 years. Both figures exclude maintenance. | The dashboard never pays back, and the maintenance load lands on an engineer indefinitely. | Put a payback estimate in the proposal. Kill it if the payback is longer than the expected life of the tool. | — |
| 4 | Medium | CONFIRMED | D | `proposal.md` "Scope" | Scope includes features nobody asked for. Role-based login, PDF export and dark mode for a tool used by two people who share everything. Login also adds a burden: new accounts and credentials to manage. | The work grows, the schedule slips, and access control is maintained for an audience of two. | Remove every feature not traced to a stated user need. If anything gets built, it should have no login beyond existing single sign-on and no extras. | — |
| 5 | Medium | PROBABLE | D | `proposal.md` (no adoption or success section) | There is no adoption plan and no way to tell if the tool has been abandoned. The users' stated preference ("an email… if anything") suggests they would keep using the spreadsheet or the email. | Six months on, the dashboard has no logins while the spreadsheet is still the working tool. Now two sources of the same numbers can disagree. | Define what success looks like (for example, weekly use by both users within 2 weeks) and a date to shut the tool down if usage falls short. | — |
| 6 | Low | CONFIRMED | D / B | `proposal.md` "Risks"; "then maintenance" | The risk section lists only schedule slip. It leaves out maintenance cost (not quantified), duplicated metric definitions between the sheet and the dashboard, and the opportunity cost of the engineer. | Hidden ongoing cost, and conflicting numbers between the two tools. | List maintenance in hours per month, name a single source of truth, and state the opportunity cost. | — |

## WHAT HOLDS UP
- The scope is concrete: twelve named metrics.
- The effort estimate is stated, not hidden.
- Changing metric definitions is a real schedule risk.

## UNVERIFIED CLAIMS
- **"6 engineer-weeks"**: no breakdown is given. A task-level estimate would confirm it.
- **"The current spreadsheet looks dated" as a problem**: this is opinion, and no user complaint is cited. Asking the two users would settle it, and their notes already say it's fine.
- **The team notes themselves**: they are a summary, not a transcript. Confirming with both team members would settle this.

## QUESTIONS FOR THE AUTHOR
1. Who, besides the two-person data team, needs these metrics, and where is that need recorded?
2. Why was the scheduled-email option, suggested by the team itself, not costed or compared?
3. What specific failure of the current spreadsheet would the dashboard fix?

## DECISION-MAKER SUMMARY
Don't fund the six-week dashboard: its only users say the current spreadsheet works and that a Monday email would be the most they'd want. If anything is done, set up the scheduled email, which costs hours rather than weeks. Proceeding anyway likely means about 240 engineer-hours plus ongoing maintenance on a tool that never pays back and may go unused.

## OWNER SUMMARY
The two people who use these weekly numbers say their current spreadsheet works well and takes about ten minutes a week. The plan to spend six weeks of an engineer's time on a new dashboard isn't backed by any real need. The sensible choice is to leave things as they are, or at most send the numbers by email every Monday.

```json
{
  "verdict": "REJECT",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "proposal.md", "status": "seen", "matters": true},
    {"item": "evidence/team_notes.md", "status": "seen", "matters": true},
    {"item": "current spreadsheet and refresh job", "status": "not_seen", "matters": false},
    {"item": "estimate breakdown for 6 engineer-weeks", "status": "not_seen", "matters": false},
    {"item": "any stakeholder request for a dashboard", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-single-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "No personal, financial, health, credential or confidential client data in the work."},
  "findings": [
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "D", "location": "proposal.md 'Why'; team_notes.md lines 2-4",
     "scenario": "Only stated need is aesthetic; users say the spreadsheet is fine and nobody asked for more, so 6 engineer-weeks are spent on an unneeded tool.",
     "fix": "Require a documented user problem before any build; if none, do nothing.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "D", "location": "proposal.md (no alternatives); team_notes.md line 5",
     "scenario": "Team-suggested scheduled Monday email and do-nothing are never considered; decision-maker approves the costliest option without seeing the cheap one (drift from 'propose what to do').",
     "fix": "Compare do nothing / scheduled email / dashboard with costs.", "status": "confirmed"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "D", "location": "proposal.md 'Estimated effort'; team_notes.md line 1",
     "scenario": "240 h build vs at most 10-20 min/week saved gives a payback of about 14-28 years before maintenance.",
     "fix": "Add a payback calculation; reject if longer than the tool's life.", "status": "n/a"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "D", "location": "proposal.md 'Scope'",
     "scenario": "Role-based login, PDF export and dark mode for two users inflate scope and add account burden.",
     "fix": "Cut every feature not traced to a stated user need.", "status": "n/a"},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "D", "location": "proposal.md (no adoption section)",
     "scenario": "Users keep using the spreadsheet or email; the dashboard is abandoned and the two sources diverge.",
     "fix": "Define a success metric and a sunset date.", "status": "n/a"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "D", "location": "proposal.md 'Risks'",
     "scenario": "Unquantified maintenance and duplicated metric definitions create hidden cost and conflicting numbers.",
     "fix": "Quantify maintenance, name a single source of truth, state the opportunity cost.", "status": "n/a"}
  ]
}
```
