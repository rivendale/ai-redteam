# Redteam review: internal metrics dashboard proposal

**Review conditions:** One reviewer, no tools, no subagent. The proposal was not written in this conversation, so I have no authorship anchoring. Anything that needs running code or opening sources is marked UNVERIFIED.

**VERDICT: REJECT.** The data team's own notes say the spreadsheet works, takes ten minutes a week, nobody else uses it, and a Monday email would be enough. The proposal asks for six engineer-weeks plus maintenance and justifies it only by fashion.

**CONFIDENCE: medium.** Every finding rests on direct quotes from the two supplied files. It is limited by:
- the evidence being one conversation with two people,
- no view of the spreadsheet or the metric definitions,
- not knowing whether someone outside the team asked for this proposal.

**INPUTS LEDGER**

Seen:
- request.md
- context.md
- evidence/team_notes.md
- proposal.md

Not seen:
- **Who commissioned the proposal and why.** This matters: if a stakeholder outside the team wants a dashboard, the need changes.
- **The spreadsheet itself and the twelve metric definitions.** These matter somewhat for the "definitions may change" risk.
- **Any effort breakdown behind "6 engineer-weeks".** This matters for cost, though not for the verdict.

**COVERAGE**
- Scope: the whole proposal.
- Checked:
  - proposal.md: Proposal, Why, Scope and Risks sections
  - team_notes.md: all four notes
  - request.md
  - context.md
- Not checked:
  - the spreadsheet and warehouse refresh (not supplied)
  - the effort estimate's basis (not supplied)

**SEATS AND GATE**
- Seats: the local reviewer only. No cross-vendor seats; none were requested and no tools are available.
- Sensitivity gate: passed. There is no personal, financial or confidential data. The team notes hold no names.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | High | CONFIRMED | D | proposal.md "Why"; team_notes.md lines 1–3 | Need not established. The only rationale is "Dashboards are the modern way… the spreadsheet looks dated". The team says "The spreadsheet is fine", "about ten minutes" a week, and "Nobody has asked for more." The proposal answers "how do we build a dashboard", not the request "what to do about how the team looks at its metrics". | Six engineer-weeks are spent replacing a ten-minute weekly task that its only two users call fine. They are then committed to maintaining it. | State a need with evidence from the users, or withdraw. Rewrite the proposal against the team's stated position. | a✓ b✓ c✗ d✓ |
| F2 | High | CONFIRMED | D | proposal.md (no alternatives section); team_notes.md line 4 | The cheapest option is ignored. The team named it: "A scheduled email of the twelve numbers on Monday morning would be enough, if anything." Doing nothing is also viable, since the sheet "refreshes itself overnight". Neither is compared. | The decision-maker approves six weeks without seeing that a roughly one-day scheduled email, or no change at all, meets the stated need. | Add an alternatives section that costs (1) do nothing, (2) a scheduled Monday email of the twelve numbers, and (3) the dashboard. Recommend the cheapest option that meets the need. | a✓ b✓ c✗ d✓ |
| F3 | High | CONFIRMED | D | proposal.md "Scope" | The scope is built for an audience that does not exist. It includes role-based login, date filters, PDF export and dark mode, but "Nobody outside the two of us looks at it." Login adds a new account and step for two people who now just open a spreadsheet. | The team must log in to a new tool to see numbers they already have. They keep using the spreadsheet, the dashboard goes unused, and maintenance continues anyway. | If any build survives F1 and F2, cut the scope to what the two users ask for. Drop roles, PDF export and dark mode unless a named user requests them. | a✓ b✓ c✗ d✓ |
| F4 | Medium | CONFIRMED | D | proposal.md "Proposal" ("then maintenance") | Maintenance is unquantified, although the context names it as part of the stakes. Auth, roles and a web front end all carry ongoing cost: patches, access reviews, warehouse schema changes. | The sponsor approves on "6 weeks" and inherits an unbudgeted, permanent maintenance load. | Estimate yearly maintenance and name an owner. Include it in the alternatives comparison. | a✓ b✓ c✗ d✗ |
| F5 | Medium | CONFIRMED | D | proposal.md (whole; no success or adoption criteria) | There is no adoption measure and no criterion for retiring the dashboard. Nothing defines who uses it in week one or what would show it was abandoned. | The dashboard ships, the team stays on the spreadsheet, and nobody notices or decommissions it. | Define first-week users, a usage signal (for example, Monday logins), and a retire-if-unused rule. | a✓ b✓ c✗ d✗ |
| F6 | Low | CONFIRMED | D | proposal.md "Risks" | The Risks section lists only schedule slip from metric-definition changes. It omits the largest risk: non-adoption by the only two users. | The decision-maker sees a risk list that understates the main reason this fails. | Add non-adoption and maintenance burden as risks. | a✓ b✓ c✗ d✗ |

**Siblings and boundaries (F1–F3).**
- Root cause: the proposal ignores what the users said they need.
- Search: I checked every proposal section against each team note.
- Result: the same disregard appears in Why (F1), the missing alternatives (F2), Scope (F3) and Risks (F6), each recorded separately.
- None of these is a security finding, so no trust boundary is crossed.

## NEEDS VALIDATION
- **S1, a stakeholder outside the team.** Someone outside the team may want visibility, for example leadership. To settle it: who commissioned this proposal, and did any named person outside the team ask to see these metrics? The notes say nobody has.
- **S2, how representative the notes are.** The notes come from one conversation and record no dissent. To settle it: do both team members agree with the notes as written?
- **S3, stability of the metric definitions.** To settle it: how often the twelve definitions changed over the past year. This affects the cost of any option that hard-codes them, the email included.

## REFUTED
- **"The spreadsheet requires manual effort that a dashboard would remove."** Refuted by team_notes.md: "It refreshes itself overnight from the warehouse."
- **"Login is needed because the metrics are sensitive."** Nothing supplied suggests the metrics are sensitive, and only two people view them. This is not a finding, though it remains a question if roles are kept.

## WHAT HOLDS UP
- The proposal is clear about scope and effort, so its cost is visible.
- The one risk it names (definition churn) is real.

## UNVERIFIED CLAIMS
- **"Dashboards are the modern way to look at metrics."** This is an assertion with no source, and it is irrelevant to this team's need.
- **"6 engineer-weeks."** There is no breakdown. To confirm it, ask for a task-level estimate.

## QUESTIONS FOR THE AUTHOR
1. Who, outside the two-person team, asked for a dashboard?
2. Why was the team's own suggestion of a scheduled email not costed?

## DECISION-MAKER SUMMARY
Do not fund the six-week dashboard. Ask for a revised proposal that costs doing nothing and the team's own suggestion, a Monday scheduled email, against any build. If you proceed anyway, the likely outcome is six weeks of engineering plus ongoing maintenance on a tool its two users did not ask for and may never open.

## OWNER SUMMARY
The data team says its current spreadsheet works well and takes about ten minutes a week. The only improvement it mentioned is an automatic Monday email of the numbers. A six-week dashboard project is not justified by anything the team said, so the cheaper options should be compared before any money is spent.

```json
{
  "schema_version": "2.3",
  "verdict": "REJECT",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "evidence/team_notes.md", "status": "seen", "matters": true},
    {"item": "proposal.md", "status": "seen", "matters": true},
    {"item": "who commissioned the proposal", "status": "not_seen", "matters": true},
    {"item": "the spreadsheet and metric definitions", "status": "not_seen", "matters": false},
    {"item": "effort estimate breakdown", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "evidence/team_notes.md", "kind": "document"},
      {"unit": "proposal.md", "kind": "document"},
      {"unit": "proposal.md:Why", "kind": "section"},
      {"unit": "proposal.md:Scope", "kind": "section"},
      {"unit": "proposal.md:Risks", "kind": "section"},
      {"unit": "Dashboards are the modern way to look at metrics", "kind": "claim"},
      {"unit": "6 engineer-weeks", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "the spreadsheet and warehouse refresh", "reason": "not_supplied"},
      {"unit": "effort estimate breakdown", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "D",
     "location": "proposal.md 'Why'; evidence/team_notes.md lines 1-3",
     "scenario": "Six engineer-weeks are spent replacing a ten-minute weekly task that its only two users call fine ('The spreadsheet is fine'; 'Nobody has asked for more'); the proposal answers how to build a dashboard, not what the team needs.",
     "fix": "State a user need with evidence or withdraw; rewrite the proposal against the team's stated position.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "security": false,
     "siblings_searched": {"searched": "every proposal section against each team note", "found": "same root cause in missing alternatives (F2), Scope (F3) and Risks (F6)"}},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "D",
     "location": "proposal.md (no alternatives section); evidence/team_notes.md line 4",
     "scenario": "The decision-maker approves six weeks without seeing that the team's own suggestion, a scheduled Monday email of the twelve numbers, or doing nothing meets the stated need.",
     "fix": "Add an alternatives section costing do-nothing, a scheduled Monday email, and the dashboard; recommend the cheapest that meets the need.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "security": false,
     "siblings_searched": {"searched": "every proposal section against each team note", "found": "same root cause in Why (F1), Scope (F3) and Risks (F6)"}},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "D",
     "location": "proposal.md 'Scope'",
     "scenario": "Role-based login, filters, PDF export and dark mode are built for an audience that does not exist ('Nobody outside the two of us looks at it'); the two users face a new login, keep using the spreadsheet, and the dashboard goes unused while still needing maintenance.",
     "fix": "If any build survives, cut scope to what the two users request; drop roles, PDF export and dark mode unless a named user asks.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "security": false,
     "siblings_searched": {"searched": "every proposal section against each team note", "found": "same root cause in Why (F1), missing alternatives (F2) and Risks (F6)"}},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "D",
     "location": "proposal.md 'Proposal' ('then maintenance')",
     "scenario": "The sponsor approves on '6 weeks' and inherits an unbudgeted, permanent maintenance load for auth, roles and a web front end.",
     "fix": "Estimate yearly maintenance, name an owner, and include it in the alternatives comparison.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F5", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "D",
     "location": "proposal.md (whole; no success or adoption criteria)",
     "scenario": "The dashboard ships, the team stays on the spreadsheet, and nobody notices or decommissions it.",
     "fix": "Define first-week users, a usage signal such as Monday logins, and a retire-if-unused rule.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F6", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "D",
     "location": "proposal.md 'Risks'",
     "scenario": "The risk list names only schedule slip and omits non-adoption by the only two users, so the decision-maker underrates the main failure mode.",
     "fix": "Add non-adoption and maintenance burden to Risks.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "D", "location": "proposal.md (author and sponsor not stated)",
     "suspicion": "A stakeholder outside the team may want visibility, which would change the need.",
     "unresolved_fact": "Who commissioned the proposal, and whether any named person outside the team asked to see these metrics."},
    {"id": "S2", "status": "needs_validation", "track": "D", "location": "evidence/team_notes.md",
     "suspicion": "The notes come from one conversation and may not represent both members.",
     "unresolved_fact": "Whether both team members agree with the notes as written."},
    {"id": "S3", "status": "needs_validation", "track": "D", "location": "proposal.md 'Risks'",
     "suspicion": "Metric-definition churn may raise the cost of any option, the email included.",
     "unresolved_fact": "How often the twelve metric definitions changed over the past year."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "The spreadsheet requires manual effort a dashboard would remove.",
     "evidence": "team_notes.md: 'It refreshes itself overnight from the warehouse.'"},
    {"id": "C2", "candidate": "Login is needed because the metrics are sensitive.",
     "evidence": "Nothing supplied indicates sensitivity, and only two people view the metrics."}
  ]
}
```