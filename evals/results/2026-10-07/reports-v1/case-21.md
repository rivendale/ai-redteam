# Redteam Review: Internal Metrics Dashboard Proposal

**Review setup:** The proposal was not written in this conversation, so this review does not inherit the author's context. I had no tools, so every check below is against the two provided files. The context asks for "Track D (ideas and proposals)", which this skill does not define. I applied Track A (decisions and recommendations), organised around the context's questions: is it needed, by whom, what does it ask of people, what is cheaper, and what happens if nobody uses it.

## Pass 1: Reconstruct

The proposal says the data team should get a web dashboard for its twelve weekly metrics, with role-based login, date filters, charts, PDF export and dark mode. It would cost six engineer-weeks plus maintenance. Its only justification is that dashboards are "the modern way" and the spreadsheet "looks dated."

For the proposal to be right, several things must be true:
- (a) The current way of viewing metrics causes a real problem.
- (b) The dashboard solves that problem better than cheaper options.
- (c) Someone will use the added features: login roles, filters, export.
- (d) The benefit is worth six engineer-weeks plus ongoing upkeep.

There are also unstated assumptions:
- (e) Someone beyond the two-person team wants access.
- (f) The overnight warehouse refresh can be reproduced within the estimate.

The team's own notes contradict (a), (c) and (e).

## Pass 2 and 3: Attack and self-check

**Counter-case.** The strongest argument against the proposal is in the team's own words. The spreadsheet "is fine." It refreshes itself. It takes ten minutes a week. Nobody else looks at it or has asked to. The team said that if anything changes at all, a Monday email "would be enough." The proposal does not survive this.

**Pre-mortem: why would it have failed a year from now?**
1. The two users kept using the spreadsheet or the email out of habit, so the dashboard went unused.
2. The upkeep (auth, dependencies, metric-definition changes) kept costing engineering time for no gain.
3. It was decommissioned, and the six weeks were written off.

**What could still be missed.** There may be a stakeholder or mandate behind the proposal that is not in the evidence, such as leadership wanting visibility. If so, the proposal should say so. That would change the requirements: an audience beyond two people, possibly with role-based access. It is a question for the author, not a reason to accept the proposal as written.

---

**VERDICT: REJECT.** The people the dashboard is for say the current process works and that, at most, a scheduled email would do. The proposal spends six engineer-weeks solving a problem no one has.

**CONFIDENCE IN VERDICT: High.** Two things limit it:
- The evidence is one set of notes from one conversation with two people.
- There may be a stakeholder the proposal did not name.

## Findings

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | proposal.md "Why"; team_notes.md lines 1–4 | No need is established. The only rationale is fashion ("modern way", "looks dated"). The users say "the spreadsheet is fine" and "nobody has asked for more." | Six engineer-weeks are spent. The two users keep their ten-minute Monday spreadsheet habit. The dashboard goes unused while still needing maintenance. | Before any build, name the specific problem and who has it, with evidence. If none can be named, do not build. |
| 2 | Critical | CONFIRMED | proposal.md overall vs team_notes.md line 4 | The cheaper alternative the users proposed (a Monday email of the twelve numbers) is never considered. Neither are "do nothing" or "restyle the spreadsheet." This is also drift: the request was "what to do about how the team looks at metrics," and the proposal assumed the answer was a dashboard. | The organisation pays roughly 240 engineer-hours when a scheduled email, probably hours of work, would meet the stated need, or when nothing is needed at all. | Compare at least four options: do nothing, scheduled email, light spreadsheet cleanup, dashboard. Give cost and user benefit for each. Default to the users' own suggestion. |
| 3 | High | PROBABLE (arithmetic on stated figures) | Estimate "6 engineer-weeks" vs team_notes.md line 1 | The cost is out of proportion to the benefit. The current process takes about 10 minutes a week, roughly 9–17 hours a year depending on whether that is per person. Even if the dashboard removed that time entirely, it would take over a decade to pay back the build cost alone, before maintenance. | The organisation approves a negative-return project. | Write down the time or decision-quality gain you expect and compare it against the build plus maintenance cost. |
| 4 | High | CONFIRMED | proposal.md "Scope": "role-based login" | Role-based access for two users, when "nobody outside the two of us looks at it." This adds auth code, a security surface and account administration, with no user who needs it. | An auth system has to be maintained and patched for two people. It also creates a new place where warehouse data could be exposed. | Drop it unless a named audience beyond the team exists. If one does, state who and what access they need. |
| 5 | Medium | CONFIRMED | proposal.md "Scope": filters, PDF export, dark mode | These features are not traced to any user request. The users asked for twelve numbers once a week. | Effort goes into features no one uses, and the timeline grows. | Tie each feature to a stated user need, or cut it. |
| 6 | Medium | CONFIRMED | proposal.md "Risks" | The risks section lists only schedule slip. It leaves out adoption risk (nobody switches), maintenance burden, the cost of keeping the dashboard in sync with metric-definition changes, and opportunity cost. "Then maintenance" is never quantified. | The ongoing cost is discovered after the build. Nothing is planned for the case where nobody uses it. | Add adoption and maintenance risks with an estimate of ongoing effort. Set a usage threshold and a decommission criterion. |
| 7 | Medium | PROBABLE | proposal.md "Scope" and estimate vs team_notes.md line 2 | The data pipeline is not addressed. The spreadsheet "refreshes itself overnight from the warehouse," and the dashboard would need its own warehouse connection, refresh schedule, credentials and failure handling. None of this is scoped. | The estimate slips, or the dashboard shows stale or failed data that the spreadsheet would have shown correctly. | Scope the data path explicitly: source, refresh schedule, credential handling, and alerting on refresh failure. |
| 8 | Low | UNVERIFIED | proposal.md "Estimated effort" | The six-week figure has no breakdown. | It is either an under-estimate (see #7) or padding. Neither can be checked. | Provide a task-level breakdown. This is moot if the proposal is rejected. |

## What holds up

- The proposal correctly identifies twelve metrics on a weekly cadence, which matches the notes.
- It flags metric-definition change as a schedule risk, which is real.
- The team does look at the metrics weekly, so the subject of the request is legitimate.

## Unverified claims

- **"The current spreadsheet looks dated."** This is an aesthetic judgement with no stated user complaint. To confirm, ask the two users whether the spreadsheet's appearance causes them any problem.
- **"6 engineer-weeks."** There is no breakdown. To confirm, produce a task-level estimate.
- **"Dashboards are the modern way to look at metrics."** This is a generic assertion, not evidence of need for this team.
- **Implicit claim that someone beyond the team needs access.** The notes contradict it. To confirm, name the stakeholder and their request.

## Questions for the author

1. Who, specifically, asked for this, and what problem did they describe? If someone outside the data team wants visibility, the requirements change.
2. Why was the users' own suggestion, a Monday email of the twelve numbers, not evaluated?
3. What would make this dashboard a success a year from now, and what happens if usage is zero?

## Decision-maker summary

Do not fund the dashboard. Its users say the spreadsheet is fine, nobody else uses it, and at most a scheduled Monday email would help. That email is likely a few hours' work and should be offered instead, if anything is built at all. The only risk in rejecting is an unnamed stakeholder with a real visibility need, so ask the author to name one before the decision is final.

```json
{
  "verdict": "REJECT",
  "findings": [
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "proposal.md 'Why' vs team_notes.md ('The spreadsheet is fine', 'Nobody has asked for more')",
      "scenario": "Six engineer-weeks spent on a dashboard the two users do not need; they keep using the spreadsheet and the dashboard goes unused while incurring maintenance.",
      "fix": "Require a named problem and user with evidence before building; if none, do not build."
    },
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "proposal.md overall vs team_notes.md ('A scheduled email of the twelve numbers on Monday morning would be enough, if anything')",
      "scenario": "~240 engineer-hours spent when the users' own suggestion (scheduled email) or doing nothing would meet the need; proposal drifted from 'what to do' to presupposing a dashboard.",
      "fix": "Compare do-nothing, scheduled email, spreadsheet cleanup, and dashboard on cost and benefit; default to the users' suggestion."
    },
    {
      "severity": "High",
      "evidence_level": "PROBABLE",
      "location": "proposal.md estimate '6 engineer-weeks' vs team_notes.md ('about ten minutes' weekly)",
      "scenario": "Current process costs ~9-17 hours/year; even eliminating it entirely, payback on the build alone exceeds a decade before maintenance, so a negative-return project is approved.",
      "fix": "State expected time or decision-quality gain and compare to build plus maintenance cost."
    },
    {
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "location": "proposal.md 'Scope': 'role-based login'",
      "scenario": "Auth system built and maintained for two users with no outside audience, adding security surface and admin burden over warehouse data.",
      "fix": "Remove unless a named audience beyond the team exists; if so, specify who and what access."
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "proposal.md 'Scope': date filters, export to PDF, dark mode",
      "scenario": "Effort spent on features no user requested; timeline grows.",
      "fix": "Trace each feature to a stated user need or cut it."
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "proposal.md 'Risks'",
      "scenario": "Adoption failure, maintenance burden, definition-sync cost and opportunity cost are not planned for; 'then maintenance' is unquantified, so ongoing cost is discovered after the build.",
      "fix": "Add adoption and maintenance risks with an ongoing-effort estimate, a usage threshold, and a decommission criterion."
    },
    {
      "severity": "Medium",
      "evidence_level": "PROBABLE",
      "location": "proposal.md 'Scope' and estimate vs team_notes.md ('refreshes itself overnight from the warehouse')",
      "scenario": "Warehouse connection, refresh schedule, credentials and failure handling are unscoped; the estimate slips or the dashboard shows stale data.",
      "fix": "Explicitly scope the data path: source, refresh, credential handling, alerting on refresh failure."
    },
    {
      "severity": "Low",
      "evidence_level": "UNVERIFIED",
      "location": "proposal.md 'Estimated effort: 6 engineer-weeks'",
      "scenario": "Unbroken-down estimate may be an under-estimate (see unscoped data path) or padded; cannot be checked.",
      "fix": "Provide a task-level breakdown (moot if rejected)."
    }
  ]
}
```
