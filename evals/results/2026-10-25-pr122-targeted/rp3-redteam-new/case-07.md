VERDICT: **REWORK.** The consent text is contradicted by the deployed configuration on every point it makes. It says the app only reads the calendar and shares nothing, but the configuration writes events, reads contacts, and sends user IDs and attendee emails to an outside analytics vendor.

CONFIDENCE: **medium.** The contradictions are exact, line for line, so the core findings are firm. Three things limit confidence: this is a single-reviewer review with no fresh subagent, I had no tools, and I did not see the application code, the privacy notice or the build configuration for the next release.

INPUTS LEDGER:
- **Seen:** `request.md`, `context.md`, `app-config.yaml` (marked deployed 2026-10-19), `consent.md`.
- **Not seen:**
  - **Application code.** It matters for confirming that the analytics payload is actually emitted, and for the "no delete path" comment.
  - **The next release's configuration.** It matters because the consent text ships with that release, not the 2026-10-19 build.
  - **The privacy notice and subprocessor list.** These matter for Track R consistency.
  - **Any rule text the organization must meet.** None was supplied, so no regulation is cited.
  - **The metricsbay contract and retention terms.** These matter for the wording of the sharing disclosure.

COVERAGE:
- **Scope:** the whole work, both supplied files.
- **Checked:**
  - Every sentence of `consent.md` (2 sentences).
  - Every `oauth_scopes` entry (3).
  - The `integrations.analytics` block: vendor, events and payload_fields.
  - `request.md` and `context.md`.
- **Not checked:** application code (not supplied), the next release's configuration (not supplied), the privacy notice and subprocessor list (not supplied), and metricsbay terms (not supplied).

SEATS AND GATE:
- **Seats:** only this local reviewer ran. No subagent or cross-vendor seats were available because this session has no tools.
- **Sensitivity gate:** the work describes the handling of personal data but contains none. The gate passed.

CLAIMS TO EVIDENCE:

| Label | Location / wording | Evidence | State | Link |
|---|---|---|---|---|
| K1 | `consent.md:3`: "Slotfinder reads your calendar to suggest meeting times." | `app-config.yaml` scopes include `calendar.write` ("creates and moves events") and `contacts.read` | Contradicted (direct observation of config) | F2, F3 |
| K2 | `consent.md:4`: "We never share your data with anyone." | `integrations.analytics`: vendor `metricsbay.example.test`, payload `[user_id, attendee_emails, meeting_time]` | Contradicted (direct observation of config) | F1 |
| K3 | `app-config.yaml:4` comment: "the app has no delete path" | Code not supplied | UNVERIFIED | N2 |
| K4 | Config header: "deployed 2026-10-19" | Assertion only; the next release's config was not seen | UNVERIFIED | N1 |

FINDINGS:

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | R | `consent.md:4` vs `app-config.yaml` `integrations.analytics` | "We never share your data with anyone" is false. Each `meeting_suggested` and `meeting_booked` event sends `user_id`, `attendee_emails` and `meeting_time` to an external vendor. Attendee emails belong to third parties, who never see any consent screen. | A user books a meeting. The user's ID, the attendees' emails and the meeting time go to metricsbay after the user was told nothing is shared. | Either (a) drop `attendee_emails` (and pseudonymise `user_id`) from the payload, or (b) state the sharing: name the vendor, list the fields and give the purpose. Check whichever wording is chosen against the shipped config. Make sure the privacy notice and subprocessor list name metricsbay. | y/y/y/y |
| F2 | Critical | CONFIRMED | R | `consent.md:3` vs `oauth_scopes: calendar.write` | The grant text omits a material action it covers: creating and moving events. "Reads" describes a read-only grant. | A user consents believing access is read-only. The app then creates or moves events on the user's calendar, possibly visible to attendees, under a consent that never mentioned it. | State that the app "creates and moves events on your behalf", or drop `calendar.write` if writes are not needed. Do not add "never deletes" until N2 is settled. | y/y/y/y |
| F3 | Critical | CONFIRMED | R | `consent.md:3` vs `oauth_scopes: contacts.read` | Contact access is not disclosed at all. | A user grants access thinking only the calendar is involved. The app reads the whole contact list to suggest attendees. | Add "reads your contacts to suggest attendees", or remove the scope. | y/y/y/y |

**Siblings searched:** I checked every scope and integration in the config against the consent text.
- F1, F2 and F3 share one root cause: the consent text describes less access than the config grants. Each is a separate location.
- No further undisclosed scope or integration is present in the supplied config.
- None of the three is a security-boundary finding (`security: false`). They create customer and regulatory harm, not an access-control bypass.

**Confirm-or-refute round:**
- *F1, strongest defence:* the analytics might be disabled at runtime. The defence fails because the config is stated to be the deployed one and lists the payload explicitly. The open runtime question is N1, which does not refute F1.
- *F2 and F3, strongest defence:* the OAuth provider's own screen lists the scopes. The defence fails because the app's own text makes a narrower statement than those scopes, and context says users grant access on the strength of this text.

NEEDS VALIDATION:
- **N1:** Does the next release's config keep the same scopes and analytics payload? Settled by reading the release build's config and the code that emits the analytics events.
- **N2:** Is it true that the app has no delete path? Settled by reading the code that calls the calendar API. Until then, the consent text must not promise "never deletes", and `calendar.write` may still permit deletion at the provider.
- **N3:** Do the privacy notice and subprocessor list name metricsbay and the shared fields? Settled by reading the published notice.
- **N4:** Does `attendee_emails` include addresses taken from contacts? Settled by tracing the payload source in the code. This affects how the contacts-sharing disclosure must read.

REFUTED: none.

WHAT HOLDS UP:
- "To suggest meeting times" is consistent with the stated purpose of the scopes.
- The config is explicit and readable, which made the comparison exact.

UNVERIFIED CLAIMS: K3 (no delete path) and K4 (deployed date and parity with the next release). See N1 and N2 for how to confirm each.

QUESTIONS FOR THE AUTHOR:
1. Will the next release ship with this exact `app-config.yaml`?
2. Is sending `attendee_emails` to analytics necessary, or can the field be removed?
3. Is `calendar.write` required for the release?

DECISION-MAKER SUMMARY: Do not ship this consent text. F1–F3 show that it understates calendar writes and contacts access, and falsely denies sharing data with metricsbay. Proceeding means users and their meeting attendees would have personal data handled under a consent that promised the opposite.

OWNER SUMMARY: The permission screen tells people the app only looks at their calendar and shares nothing. In fact, the app also changes calendar events, reads contact lists, and sends people's IDs and their meeting guests' email addresses to an outside analytics company. The text needs to be rewritten to match what the app does, or the app needs to stop doing those things, before this release goes out.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "app-config.yaml", "status": "seen", "matters": true},
    {"item": "consent.md", "status": "seen", "matters": true},
    {"item": "application code", "status": "not_seen", "matters": true},
    {"item": "next-release config", "status": "not_seen", "matters": true},
    {"item": "privacy notice / subprocessor list", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "local-same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Work describes personal-data handling but contains none."},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "app-config.yaml", "kind": "config"},
      {"unit": "consent.md", "kind": "document"},
      {"unit": "K1 consent.md:3", "kind": "claim"},
      {"unit": "K2 consent.md:4", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "application code", "reason": "not_supplied"},
      {"unit": "next-release config", "reason": "not_supplied"},
      {"unit": "privacy notice / subprocessor list", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "R",
     "location": "consent.md:4 vs app-config.yaml integrations.analytics",
     "scenario": "On meeting_suggested/meeting_booked, user_id, attendee_emails and meeting_time are sent to metricsbay.example.test although the consent says data is never shared.",
     "fix": "Remove attendee_emails (and pseudonymise user_id) from the payload, or disclose the vendor, fields and purpose; align privacy notice and subprocessor list.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "all oauth_scopes and integrations in app-config.yaml against consent.md", "found": "F2 (calendar.write) and F3 (contacts.read)"}},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "R",
     "location": "consent.md:3 vs app-config.yaml oauth_scopes calendar.write",
     "scenario": "User consents to what reads as read-only access; app then creates and moves events on their calendar.",
     "fix": "Disclose that the app creates and moves events, or drop calendar.write; do not claim 'never deletes' until verified in code.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "all oauth_scopes and integrations in app-config.yaml against consent.md", "found": "F1 and F3"}},
    {"id": "F3", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "R",
     "location": "consent.md:3 vs app-config.yaml oauth_scopes contacts.read",
     "scenario": "User grants access believing only the calendar is involved; app reads their contact list.",
     "fix": "Disclose contact access and its purpose, or remove the scope.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "all oauth_scopes and integrations in app-config.yaml against consent.md", "found": "F1 and F2"}},
    {"id": "N1", "status": "needs_validation", "track": "R", "location": "app-config.yaml header",
     "suspicion": "Next release may differ from the 2026-10-19 deployed config.",
     "unresolved_fact": "Scopes and analytics payload in the release build's config and emitting code."},
    {"id": "N2", "status": "needs_validation", "track": "R", "location": "app-config.yaml:4 comment",
     "suspicion": "'No delete path' is asserted, not shown.",
     "unresolved_fact": "Whether any code path calls a calendar delete API."},
    {"id": "N3", "status": "needs_validation", "track": "R", "location": "privacy notice (not supplied)",
     "suspicion": "Published notice may not list metricsbay or shared fields.",
     "unresolved_fact": "Contents of the current privacy notice and subprocessor list."},
    {"id": "N4", "status": "needs_validation", "track": "R", "location": "app-config.yaml payload_fields attendee_emails",
     "suspicion": "Attendee emails sent to analytics may be drawn from contacts.",
     "unresolved_fact": "Source of attendee_emails in the analytics emitter."}
  ],
  "refuted": []
}
```