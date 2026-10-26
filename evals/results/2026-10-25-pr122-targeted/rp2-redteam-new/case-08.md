# Redteam report: Slotfinder consent screen vs. deployed configuration

**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No subagent or tools were available, so I could not open files, run code or start a fresh reviewer.

**VERDICT: SHIP.** Every sentence on the consent screen matches the supplied configuration, and I confirmed no finding. One open question should still be settled before release: the consent text says nothing about deleting events, and I could not check whether the `calendar.write` permission allows deletion (S1).

**CONFIDENCE: medium.** Three things limit it:
- This is a same-context review.
- Only the config was supplied, so "enforced behavior" rests on config declarations and one code comment, not code.
- The config is the 2026-10-19 deployment, not the release this text ships with.

## INPUTS LEDGER

| Item | Status | Matters? |
|---|---|---|
| request.md | seen | n/a |
| context.md | seen | n/a |
| consent.md | seen | n/a |
| app-config.yaml (deployed 2026-10-19) | seen | n/a |
| Application code (write path, the "no delete path" claim, outbound calls) | not supplied | **Yes.** The comment at `app-config.yaml:4` is an assertion, not enforced behavior. |
| OAuth provider's definition of `calendar.write` | not supplied / no tools | **Yes.** It decides whether the grant covers deletion (S1). |
| Config for the next release | not supplied | **Yes.** The consent text ships with that release, not the 2026-10-19 one (S4). |
| Privacy notice / subprocessor list | not supplied | Moderately. Needed to check consistency with published documents (S5). |

## COVERAGE

- **Scope:** the whole work (two files).
- **Checked:**
  - consent.md, all four sentences
  - app-config.yaml: `oauth_scopes`, `integrations.analytics`
  - claims C1 to C6 below
  - assumption that the config lists every outbound data flow
- **Not checked:**
  - application code (not_supplied)
  - provider scope definitions (no_tools)
  - next-release config (not_supplied)
  - privacy notice (not_supplied)

## SEATS AND GATE

- **Seats:** local same-context review only. No subagent tool was available, and no cross-vendor seats were requested.
- **Sensitivity gate:** the work contains no credentials, personal records or client data. It passed, but it was moot because no other seats ran.

## CLAIMS TO EVIDENCE

| Claim | Consent text (consent.md) | Evidence | State |
|---|---|---|---|
| C1 | "reads your calendar to suggest meeting times" (line 3) | `calendar.read` | Scope verified. The purpose is a bounded interpretation; I did not see code. |
| C2 | "creates or moves events when you accept a suggestion" (line 3) | `calendar.write` and the comment "creates and moves events… no delete path" | Create/move matches the comment. "When you accept" is **UNVERIFIED** (S2). No delete mention is **UNVERIFIED** (S1). |
| C3 | "reads your contacts to suggest attendees" (line 4) | `contacts.read  # suggests attendees` | Verified against config. |
| C4 | "When a meeting is suggested or booked" (line 5) | `events: [meeting_suggested, meeting_booked]` | Verified: both events, nothing extra. |
| C5 | "your user ID, the attendees' email addresses and the meeting time" (lines 5–6) | `payload_fields: [user_id, attendee_emails, meeting_time]` | Verified: three fields each side, exact match. |
| C6 | "our analytics provider, Metricsbay" (line 6) | `vendor: metricsbay.example.test` | Verified. |
| Implied | No other sharing | The `integrations` block has one entry | The positive control holds: the block does list the integration it has. Completeness is **UNVERIFIED** (S3). |

## FINDINGS

None confirmed.

## NEEDS VALIDATION (no severity)

- **S1: `consent.md:3` vs `app-config.yaml:4`.** If the provider's `calendar.write` scope permits deleting events, users grant deletion power the text never mentions. Track R treats "a grant whose text omits a material action it covers" as a finding.
  - **Unresolved fact:** does the provider's `calendar.write` include delete?
  - If it does, either name deletion in the text, or request a narrower create/update-only scope if the provider offers one.
- **S2: `consent.md:3`.** "When you accept a suggestion" says writes happen only after the user accepts.
  - **Unresolved fact:** does the code ever create or move events without explicit acceptance (auto-booking, rescheduling on conflict)?
- **S3: `app-config.yaml:6-10`.** The consent text implies Metricsbay is the only recipient.
  - **Unresolved fact:** does the code send data anywhere not declared in this config (error reporting, logging SaaS, an LLM provider)?
- **S4: `app-config.yaml:1`.** The text ships with the next release, but the config shown is the 2026-10-19 deployment.
  - **Unresolved fact:** do the next release's scopes, events or payload fields differ from this config?
- **S5: Consistency with published documents.**
  - **Unresolved fact:** does the published privacy notice / subprocessor list name Metricsbay and the sharing of attendee emails (which belong to third parties)?

## REFUTED

- **R1: "Consent omits data sent to analytics."** Refuted: the payload fields, events and vendor match the text one-to-one (C4 to C6).
- **R2: "Contacts access undisclosed."** Refuted: disclosed at `consent.md:4`.

## WHAT HOLDS UP

The analytics disclosure is precise and complete against the config: the trigger events, all three fields and the named vendor. Every declared scope has a matching sentence, and the text claims no capability the config lacks.

## UNVERIFIED CLAIMS

- "No delete path": confirm it by reading the code's calendar API calls.
- Writes happen only on acceptance: confirm it by tracing every caller of the event create/move functions.
- The config lists every outbound flow: confirm it by searching the code for outbound HTTP clients and SDK initializations.

## QUESTIONS FOR THE AUTHOR

1. Does `calendar.write` at your OAuth provider permit deletion? If yes, is a narrower scope available?
2. Does any path create or move events without the user accepting a suggestion?
3. Is this config identical to the one shipping in the next release, and is it the full list of third-party data flows?

## DECISION-MAKER SUMMARY

The consent text matches the deployed configuration on every point checked. Before release, confirm three things: whether the calendar write permission also allows deletion, that writes happen only on acceptance, and that the release config is unchanged. If you ship without checking and the permission covers deletion, users will have granted a power the screen never told them about.

## OWNER SUMMARY

The wording on the permission screen matches what the app is set up to do, including exactly what is shared with the analytics company. One thing is still open: the calendar permission the app asks for may also let it delete events, and the screen doesn't say so. Someone should check that, and confirm the release uses the same settings, before it ships.

## Findings JSON

The block follows schema 2.3. The output note asks for severity, evidence level, location, scenario and fix on each finding; those fields apply only to confirmed findings, and there are none. The entries below are `needs_validation`, which carry no severity under the skill's rules.

```json
{
  "schema_version": "2.3",
  "verdict": "SHIP",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "consent.md", "status": "seen", "matters": true},
    {"item": "app-config.yaml", "status": "seen", "matters": true},
    {"item": "application code", "status": "not_seen", "matters": true},
    {"item": "OAuth provider calendar.write scope definition", "status": "not_seen", "matters": true},
    {"item": "next-release config", "status": "not_seen", "matters": true},
    {"item": "privacy notice / subprocessor list", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "No credentials, personal records or confidential data in the work."},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "consent.md", "kind": "document"},
      {"unit": "app-config.yaml", "kind": "config"},
      {"unit": "C1 calendar read", "kind": "claim"},
      {"unit": "C2 create/move on accept", "kind": "claim"},
      {"unit": "C3 contacts read", "kind": "claim"},
      {"unit": "C4 analytics events", "kind": "claim"},
      {"unit": "C5 analytics payload fields", "kind": "claim"},
      {"unit": "C6 analytics vendor", "kind": "claim"},
      {"unit": "config lists all outbound flows", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "application code", "reason": "not_supplied"},
      {"unit": "provider scope definitions", "reason": "no_tools"},
      {"unit": "next-release config", "reason": "not_supplied"},
      {"unit": "privacy notice", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "S1", "status": "needs_validation", "track": "R", "location": "consent.md:3; app-config.yaml:4",
     "suspicion": "calendar.write may permit deleting events, a material action the consent text omits.",
     "unresolved_fact": "Whether the OAuth provider's calendar.write scope includes delete."},
    {"id": "S2", "status": "needs_validation", "track": "R", "location": "consent.md:3",
     "suspicion": "Events may be created or moved without the user accepting a suggestion.",
     "unresolved_fact": "Whether any code path writes events without explicit acceptance."},
    {"id": "S3", "status": "needs_validation", "track": "R", "location": "app-config.yaml:6-10",
     "suspicion": "Data may flow to recipients not declared in config and not disclosed.",
     "unresolved_fact": "Whether the code sends user data to any service besides Metricsbay."},
    {"id": "S4", "status": "needs_validation", "track": "R", "location": "app-config.yaml:1",
     "suspicion": "Reviewed config is the 2026-10-19 deployment, not the release the text ships with.",
     "unresolved_fact": "Whether next-release scopes, events or payload fields differ."},
    {"id": "S5", "status": "needs_validation", "track": "R", "location": "consent.md:5-6",
     "suspicion": "Published privacy notice may not list Metricsbay or attendee-email sharing.",
     "unresolved_fact": "Whether the privacy notice / subprocessor list names Metricsbay and attendee emails."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "Analytics sharing is under-disclosed.",
     "evidence": "Events, all three payload fields and vendor in app-config.yaml:7-10 match consent.md:5-6 exactly."},
    {"id": "R2", "candidate": "Contacts access is undisclosed.",
     "evidence": "consent.md:4 discloses contacts.read and its purpose."}
  ]
}
```