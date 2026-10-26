# Redteam review: Slotfinder consent screen vs. deployed config

**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No subagent and no tools were available, so I could not open files, run code or check the OAuth provider's scope definitions.

**VERDICT: SHIP.** Every sentence on the consent screen matches the supplied deployed config. One open question about whether the `calendar.write` grant covers deletion should be settled before release.

**CONFIDENCE: medium.** Three things limit it:
- This is a same-context review with no tools.
- The app code, the provider's scope definitions and the privacy notice were not supplied.
- The config is dated 2026-10-19, but the consent text ships with the *next* release, so the config may change before then.

**INPUTS LEDGER**

| Item | Status | Matters? |
|---|---|---|
| `request.md` | seen | yes |
| `context.md` | seen | yes |
| `app-config.yaml` | seen, as inline text | yes |
| `consent.md` | seen, as inline text | yes |
| App source code (the delete-path claim, the actual analytics payload, any other data leaving the app) | not supplied | **yes**: the config declares behavior; the code enforces it |
| OAuth provider's definition of `calendar.write` | not supplied | **yes**: decides whether the grant covers delete |
| Next-release config | not supplied | **yes**: the consent text ships with that release, not the 2026-10-19 one |
| Privacy notice and subprocessor list | not supplied | partly: needed to check that Metricsbay and attendee emails are listed |
| Metricsbay contract and retention terms | not supplied | low: the consent text makes no retention claim |

**COVERAGE.** Scope is the whole work: both files.
- **Checked:** `consent.md` sentences 1–3; `app-config.yaml` `oauth_scopes` (all three) and `integrations.analytics` (vendor, events, payload_fields).
- **Not checked:**
  - App code, scope semantics and the next-release config, because they were not supplied.
  - Privacy notice consistency, because it was not supplied.
  - The running deployment, because there were no tools. A config file is not proof of what is running.

**SEATS AND GATE.**
- Only the local same-context reviewer ran. No subagent was available, and no cross-vendor seats were requested.
- The sensitivity gate passed: there is no personal data or credentials, only a description that the app processes them.

**CLAIMS TO EVIDENCE**

| Label | Consent wording | Evidence | Status |
|---|---|---|---|
| K1 | "reads your calendar to suggest meeting times" | `oauth_scopes: calendar.read` | matches config |
| K2 | "creates or moves events when you accept a suggestion" | `calendar.write`, plus the comment "the app has no delete path" | matches the stated behavior; the delete-path claim and the scope's coverage are UNVERIFIED (see S1, S2) |
| K3 | "reads your contacts to suggest attendees" | `contacts.read  # suggests attendees` | matches config |
| K4 | sends "user ID, the attendees' email addresses and the meeting time" | `payload_fields: [user_id, attendee_emails, meeting_time]` | exact match (3 of 3 fields; none extra) |
| K5 | "When a meeting is suggested or booked" | `events: [meeting_suggested, meeting_booked]` | exact match (2 of 2 events) |
| K6 | "our analytics provider, Metricsbay" | `vendor: metricsbay.example.test` | matches |
| K7 | Implied: no other third party receives data | `integrations` lists only `analytics` | matches config; code not seen (see S3) |

**FINDINGS:** none confirmed.

**NEEDS VALIDATION** (no severity; these do not set the verdict)
- **S1 — `app-config.yaml:4` / `consent.md` line 1.** If the provider's `calendar.write` scope permits deleting events, the user grants a material action the text never mentions. The rule this would breach is "a grant whose text omits a material action it covers."
  - The config's own comment ("the app has no delete path") suggests the scope is broader than the app's use of it.
  - Unresolved fact: the provider's definition of `calendar.write`. If it covers delete, either request a narrower events-only scope, or say in the consent text that the grant allows deletion and that the app does not delete.
- **S2 — `app-config.yaml:4` comment.** "The app has no delete path" is an assertion with no supporting evidence.
  - Unresolved fact: whether the source code has any call that deletes events.
- **S3 — `app-config.yaml:6-9`.** The config declares the analytics payload, but the code may send more than it declares, or there may be other outbound calls.
  - Unresolved fact: the payload actually sent to Metricsbay and the full list of outbound integrations, taken from the code or captured traffic.
- **S4 — Release timing.** The consent text ships with the next release, but the config reviewed is the 2026-10-19 deployment.
  - Unresolved fact: whether the next-release config changes any scope, analytics field or vendor.
- **S5 — Privacy notice and subprocessor list.** Unresolved fact: whether Metricsbay is listed as a subprocessor and whether attendee emails are listed as a collected data category.

**REFUTED**
- **"The consent text hides that third parties' (attendees') emails are shared."** It states this explicitly ("the attendees' email addresses").
- **"The consent text omits write access."** It discloses creating and moving events.

**WHAT HOLDS UP**
- Each of the three scopes has a matching sentence that states its purpose.
- The analytics disclosure names the vendor, both trigger events and all three payload fields, with no omissions and no extras.
- The text claims no controls, retention periods or protections that the config fails to back up.

**UNVERIFIED CLAIMS**
- "The app has no delete path." Confirm by searching the code for event-delete calls.
- That the config reflects what is deployed and running. Confirm by checking the running version against the config.
- That the analytics payload is exactly the declared fields. Confirm by capturing traffic or reading the code.

**QUESTIONS FOR THE AUTHOR**
1. Does the provider's `calendar.write` scope allow deleting events, and is there a narrower scope that does not?
2. Does the next release change `oauth_scopes` or `integrations`?

**DECISION-MAKER SUMMARY.** The consent text accurately describes the deployed configuration and can ship. Before release, confirm whether the calendar write permission also allows deletion, and that the next release's configuration is unchanged. If the scope allows deletion and the text stays silent, users grant a power they were never told about.

**OWNER SUMMARY.** The wording users see matches what the app is set up to do, including what it shares with its analytics company. One thing to check: the calendar permission the app asks for may also allow deleting events, even though the app never deletes them. If so, either ask for a narrower permission or say so on the screen.

```json
{
  "schema_version": "2.3",
  "verdict": "SHIP",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "app-config.yaml", "status": "seen", "matters": true},
    {"item": "consent.md", "status": "seen", "matters": true},
    {"item": "application source code", "status": "not_seen", "matters": true},
    {"item": "OAuth provider scope definitions", "status": "not_seen", "matters": true},
    {"item": "next-release config", "status": "not_seen", "matters": true},
    {"item": "privacy notice / subprocessor list", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "same-context-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Work describes data processing but contains no personal data or credentials."},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "consent.md", "kind": "document"},
      {"unit": "app-config.yaml", "kind": "config"},
      {"unit": "app-config.yaml:oauth_scopes", "kind": "section"},
      {"unit": "app-config.yaml:integrations.analytics", "kind": "section"},
      {"unit": "K1-K7 consent claims", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "application source code", "reason": "not_supplied"},
      {"unit": "OAuth provider scope definitions", "reason": "not_supplied"},
      {"unit": "next-release config", "reason": "not_supplied"},
      {"unit": "privacy notice / subprocessor list", "reason": "not_supplied"},
      {"unit": "running deployment", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "S1", "status": "needs_validation", "track": "R", "location": "app-config.yaml:4; consent.md line 1",
     "suspicion": "calendar.write may permit event deletion, a material action the consent text omits.",
     "unresolved_fact": "The provider's definition of the calendar.write scope."},
    {"id": "S2", "status": "needs_validation", "track": "R", "location": "app-config.yaml:4 (comment)",
     "suspicion": "'The app has no delete path' is asserted, not shown.",
     "unresolved_fact": "Whether the source code contains any event-delete call."},
    {"id": "S3", "status": "needs_validation", "track": "R", "location": "app-config.yaml:6-9",
     "suspicion": "Code may send fields or call endpoints beyond the declared analytics payload.",
     "unresolved_fact": "Actual outbound payload and integrations, from code or captured traffic."},
    {"id": "S4", "status": "needs_validation", "track": "R", "location": "app-config.yaml:1 (deployed 2026-10-19)",
     "suspicion": "The consent text ships with the next release, but the reviewed config is the current deployment.",
     "unresolved_fact": "Whether the next-release config changes scopes, events, fields or vendor."},
    {"id": "S5", "status": "needs_validation", "track": "R", "location": "consent.md line 3",
     "suspicion": "Metricsbay and attendee emails may be missing from the privacy notice or subprocessor list.",
     "unresolved_fact": "Contents of the current privacy notice and subprocessor list."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Consent hides sharing of attendee emails.", "evidence": "consent.md line 3 names attendees' email addresses explicitly; matches payload_fields."},
    {"id": "C2", "candidate": "Consent omits write access.", "evidence": "consent.md line 1 discloses creating and moving events, matching calendar.write's stated use."}
  ]
}
```

There are no confirmed findings, so no entry carries severity, evidence level, scenario or fix. The `findings` array holds only `needs_validation` items, which have no severity by rule.