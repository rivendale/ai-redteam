# Redteam report: Slotfinder consent screen versus deployed configuration

**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** This session has no tools and no subagent. Everything below comes from reading the two supplied files. Nothing was run, fetched or opened.

**VERDICT: REWORK.** The consent text makes one false promise ("never share") and leaves out two of the three access grants the app requests. Users would be granting write and contacts access, and agreeing to third-party data flows, that the text never mentions.

**CONFIDENCE: medium.** The contradictions are certain from the supplied text. Confidence is limited by:
- a same-context review with no tools;
- no app code, privacy notice, vendor contract or release build config;
- no knowledge of the jurisdiction.

## INPUTS LEDGER

| Item | Status | Matters? |
|---|---|---|
| request.md (original request) | seen | yes |
| context.md | seen | yes |
| work/app-config.yaml | seen | yes, it is the behavior baseline |
| work/consent.md | seen | yes, it is the surface under review |
| Application source (actual scope use, analytics call sites, delete path) | not seen | yes: confirms the config reflects runtime behavior |
| Config for the *next release* (the config supplied says "deployed 2026-10-19") | not seen | yes: the text ships with the next release, and the config may change |
| Published privacy notice / subprocessor list | not seen | yes, for consistency checks (Track R) |
| Contract or DPA with metricsbay.example.test | not seen | partly: it does not cure "never share", but it affects legal exposure |
| OAuth provider's own scope-consent screen | not seen | partly: the provider may list scopes, but that does not correct a false statement in the app's own text |
| Jurisdiction / applicable rules (e.g. GDPR, CCPA) | not supplied | yes, for required statements |

## COVERAGE

**Scope:** the whole work (both files), against the original request.

**Checked:**
- app-config.yaml: all lines (scopes 3–5, integration 7–10, header comment 1, line-4 comment).
- consent.md: lines 3–4.
- request.md and context.md.
- Claims C1–C4 and assumption A1 (below).

**Not checked:**
- App source: not supplied.
- Next-release config: not supplied.
- Privacy notice: not supplied.
- Vendor DPA: not supplied.
- Provider consent screen: not supplied.
- Applicable law: not supplied, no tools.

## SEATS AND GATE

- **Seats:** a single same-context reviewer. No subagent or cross-vendor seats were available, since there are no tools.
- **Sensitivity gate:** the work contains configuration and wording only. There is no personal data, credentials or client records, so the gate is not triggered.

## CLAIMS TO EVIDENCE

| Label | Location | Exact wording | Evidence against config | State |
|---|---|---|---|---|
| C1 | consent.md:3 | "Slotfinder reads your calendar" | `calendar.read` app-config.yaml:3 supports it; `calendar.write` :4 goes beyond "reads" | Verified observation: incomplete. Leads to F2 |
| C2 | consent.md:3 | "to suggest meeting times" | Purpose fits :3 and :5. But :4 "creates and moves events" and event `meeting_booked` :9 show booking, not only suggesting | Verified observation: incomplete. Leads to F2 |
| C3 | consent.md:4 | "We never share your data with anyone." | :7–10 send `user_id, attendee_emails, meeting_time` to `metricsbay.example.test` | Verified observation: false. Leads to F1 |
| C4 | consent.md (absent) | no mention of contacts | `contacts.read` :5 "suggests attendees" | Verified observation: omitted. Leads to F3 |
| C5 | app-config.yaml:4 comment | "the app has no delete path" | Author comment only; no code seen | UNVERIFIED. Leads to S2 |
| A1 | app-config.yaml:1 | the config is what runs and what will ship | Header comment only | UNVERIFIED. Leads to S1 |

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | R | consent.md:4 vs app-config.yaml:7–10 | "We never share your data with anyone" is false. The app sends user ID, attendee emails and meeting times to a third-party analytics vendor on every suggestion and booking. | A user grants access relying on "never share". Their identifier and schedule, and the email addresses of third parties who never saw any consent, go to metricsbay. This is a misrepresentation to customers and regulators, and a consent obtained on a false statement. | Remove the absolute claim. Disclose the analytics vendor, the fields sent and the purpose. Better still, drop or hash `attendee_emails` and pseudonymize `user_id` in the payload, then state exactly what is sent. Reconcile with the privacy notice and subprocessor list. | y/y/y/y |
| F2 | Critical | CONFIRMED | R | consent.md:3 vs app-config.yaml:4 | The text says the app *reads* the calendar to *suggest* times. The app requests write access and creates and moves events (bookings, event `meeting_booked` :9). | A user consents to a read-only assistant. The app then creates or moves events on their calendar, which is visible to attendees. The user never agreed to that power. | Disclose the write capability in plain words, e.g. "create and reschedule events on your calendar when you book a meeting." If write is not needed at grant time, request it incrementally. | y/y/y/y |
| F3 | Critical | CONFIRMED | R | consent.md (whole text) vs app-config.yaml:5 | Contacts access is requested but never mentioned. | A user grants access without knowing their address book is read. Contact data is collected beyond what the consent describes. Combined with F1, attendee emails drawn from it can reach the vendor. | Add a contacts line stating the purpose (attendee suggestions) and that contact emails are sent to analytics (or stop sending them). | y/y/y/y |

**Notes on the findings:**
- **Severity calibration.** Each finding meets a, b and c. Each is a distinct statement-versus-behavior gap at a different config location, so they are kept separate per the sibling rule.
- **Security flag.** All three are privacy, regulatory and consent findings, not trust-boundary security defects, so `security` is false.
- **Sibling search, F1.** I checked all `integrations:` entries; analytics is the only one present. I also checked all payload fields: all three are personal or schedule data, and `attendee_emails` is third-party data.
- **Sibling search, F2 and F3.** I checked every entry under `oauth_scopes`. Only `calendar.read` is disclosed; the other two are not.
- **Positive control.** The search found the one disclosed scope (`calendar.read`), so the reading method does catch disclosures when they exist.

## NEEDS VALIDATION

- **S1.** Is app-config.yaml (deployed 2026-10-19) the config that ships with the next release? Settle by comparing it with the release build's config or artifact.
- **S2.** Is "no delete path" (app-config.yaml:4) true? Separately, does the provider's `calendar.write` scope technically permit deletion? This matters if the consent text later reassures users about deletion. Settle by reading the app source and the provider scope documentation.
- **S3.** Does the runtime analytics call send exactly the listed `payload_fields`, or more? Settle by reading the analytics call sites or a captured payload in a test environment.
- **S4.** Which rules apply and what do they require? This covers required statements such as a revocation or withdraw-consent instruction, a privacy-notice link and a named data controller. Settle with the jurisdiction and a legal review.
- **S5.** Does the published privacy notice or subprocessor list already name metricsbay? If not, that list is also stale. Settle by reading the privacy notice.

## REFUTED

- **R1.** Candidate: "the stated purpose is false." Refuted. Suggesting meeting times is a real purpose (:3, :5). The problem is incompleteness (F2), not a false purpose.

## WHAT HOLDS UP

- The calendar-read disclosure and the meeting-suggestion purpose are accurate as far as they go.
- The config is clear enough to audit against. Its inline comments state the purpose of each scope, which makes an accurate rewrite straightforward.

## UNVERIFIED CLAIMS

- C5, "no delete path": confirm from the source (S2).
- A1, that the deployed config equals the release config: confirm from the build artifact (S1).

## QUESTIONS FOR THE AUTHOR

1. Will the analytics payload stay as configured? In particular, must `attendee_emails` be sent at all?
2. Is this config the one that ships with the next release?
3. Which jurisdictions does the app serve, and is there a signed DPA with metricsbay?

## DECISION-MAKER SUMMARY

Do not ship this consent text. It promises no data sharing while the app sends user and attendee data to an analytics vendor, and it hides write and contacts access. Shipping it would mean consent obtained on false statements, which carries regulatory and customer-trust exposure.

## OWNER SUMMARY

The permission screen tells people the app only reads their calendar and never shares their data. In reality, the app can also add and move calendar events, reads their contacts, and sends names, emails and meeting times to an outside analytics company. The screen needs to be rewritten to say all of this plainly, or the app needs to stop doing what the screen doesn't mention, before the release goes out.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "work/app-config.yaml", "status": "seen", "matters": true},
    {"item": "work/consent.md", "status": "seen", "matters": true},
    {"item": "application source", "status": "not_seen", "matters": true},
    {"item": "next-release config", "status": "not_seen", "matters": true},
    {"item": "privacy notice / subprocessor list", "status": "not_seen", "matters": true},
    {"item": "metricsbay DPA", "status": "not_seen", "matters": true},
    {"item": "OAuth provider consent screen", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "configuration and wording only; no personal data or credentials in the work"},
  "coverage": {
    "checked": [
      {"unit": "work/app-config.yaml", "kind": "config"},
      {"unit": "work/consent.md", "kind": "document"},
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "C1 reads calendar", "kind": "claim"},
      {"unit": "C2 suggest meeting times", "kind": "claim"},
      {"unit": "C3 never share", "kind": "claim"},
      {"unit": "C4 contacts disclosure", "kind": "claim"},
      {"unit": "A1 config equals shipped config", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "application source", "reason": "not_supplied"},
      {"unit": "next-release config", "reason": "not_supplied"},
      {"unit": "privacy notice", "reason": "not_supplied"},
      {"unit": "metricsbay DPA", "reason": "not_supplied"},
      {"unit": "applicable law text", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "R",
     "location": "consent.md:4 vs app-config.yaml:7-10",
     "scenario": "A user grants access relying on 'We never share your data with anyone'; the app sends user_id, attendee_emails and meeting_time to metricsbay.example.test on every meeting_suggested and meeting_booked event, including third parties' emails.",
     "fix": "Remove the absolute claim; disclose the analytics vendor, fields and purpose; preferably drop attendee_emails and pseudonymize user_id; reconcile with the privacy notice and subprocessor list.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "all integrations entries and all payload_fields in app-config.yaml", "found": "analytics is the only integration; all three fields are personal or schedule data"}},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "R",
     "location": "consent.md:3 vs app-config.yaml:4",
     "scenario": "A user consents to an app described as reading their calendar to suggest times; it holds calendar.write and creates and moves events visible to attendees.",
     "fix": "State the write capability plainly (create and reschedule events when booking), or request write access incrementally at booking time.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "every oauth_scopes entry against consent.md", "found": "calendar.write and contacts.read undisclosed; contacts.read is F3"}},
    {"id": "F3", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "R",
     "location": "consent.md (whole text) vs app-config.yaml:5",
     "scenario": "A user grants access without being told contacts are read; contact data is collected beyond what consent describes, and attendee emails can flow to analytics (F1).",
     "fix": "Disclose contacts access and its purpose (attendee suggestions) and whether contact emails reach analytics.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "every oauth_scopes entry against consent.md", "found": "calendar.write also undisclosed (F2)"}},
    {"id": "S1", "status": "needs_validation", "track": "R", "location": "app-config.yaml:1",
     "suspicion": "The supplied config (deployed 2026-10-19) may differ from the next release.",
     "unresolved_fact": "Whether the release build config matches app-config.yaml."},
    {"id": "S2", "status": "needs_validation", "track": "R", "location": "app-config.yaml:4",
     "suspicion": "'No delete path' is asserted only in a comment; calendar.write may technically permit deletion.",
     "unresolved_fact": "App source for delete calls, and provider documentation for calendar.write."},
    {"id": "S3", "status": "needs_validation", "track": "R", "location": "app-config.yaml:10",
     "suspicion": "The runtime analytics payload may include more than the listed fields.",
     "unresolved_fact": "The analytics call sites or a captured test payload."},
    {"id": "S4", "status": "needs_validation", "track": "R", "location": "consent.md",
     "suspicion": "Required consent statements (withdrawal, controller identity, notice link) may be missing.",
     "unresolved_fact": "The applicable jurisdiction and rule text."},
    {"id": "S5", "status": "needs_validation", "track": "R", "location": "privacy notice (not supplied)",
     "suspicion": "The subprocessor list may not name metricsbay.",
     "unresolved_fact": "The published privacy notice and subprocessor list."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "The stated purpose (suggest meeting times) is false.",
     "evidence": "app-config.yaml:3 and :5 support suggestion; the gap is incompleteness, captured in F2."}
  ]
}
```