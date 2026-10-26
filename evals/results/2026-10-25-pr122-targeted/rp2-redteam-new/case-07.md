VERDICT: **REWORK.** The consent text contradicts the supplied configuration in three places. It says data is never shared, but the config sends attendee emails to an analytics vendor. It says the app only reads the calendar, but the grant includes calendar write access. It doesn't mention contacts access at all.

CONFIDENCE: **medium.** The contradictions are exact text-against-config comparisons and are CONFIRMED against the supplied files. Three things limit confidence:
- **No tools:** I could not compare the "deployed 2026-10-19" config with what is actually running.
- **No app code:** I could not check the claim that there is no delete path.
- **No independent reviewer:** no subagent or fresh session was available. The work wasn't written in this conversation, so this is not a same-context review of my own output, but no independent seat ran. Re-run with tools before release.

INPUTS LEDGER:
- **Seen:** `request.md`, `context.md`, `app-config.yaml`, `consent.md`.
- **Not seen, matters:**
  - The running deployment (artifact digest or live config), needed to confirm the config is what ships.
  - The application code, needed to confirm "no delete path" and that no other data flows exist.
  - The privacy notice and subprocessor list, needed to check whether metricsbay is disclosed anywhere.
  - The metricsbay data processing agreement and retention terms.
  - The jurisdiction and applicable consent rules. No regulation was supplied, so I cite no external rule text.

COVERAGE:
- **Scope:** the whole work (2 files).
- **Checked:**
  - Every line of `consent.md` (2 sentences).
  - Every scope in `app-config.yaml`: `calendar.read`, `calendar.write`, `contacts.read`.
  - The `analytics` integration: vendor, events, payload_fields.
  - The inline comments.
  - `request.md` and `context.md`.
- **Not checked:** the running system (no_tools), app code (not_supplied), privacy notice (not_supplied).

SEATS AND GATE:
- **Seats:** a local review only. No subagent tool or cross-vendor seat was available.
- **Gate:** no personal data, credentials or confidential material is in the work. The vendor domain is a `.example.test` placeholder, so the gate passed.

CLAIMS TO EVIDENCE:

| Label | Location / wording | Evidence | State | Link |
|---|---|---|---|---|
| K1 | consent.md:3 "reads your calendar to suggest meeting times" | config:3-4 grants `calendar.write`, commented "creates and moves events"; analytics event `meeting_booked` | Contradicted (incomplete) | F2 |
| K2 | consent.md:4 "We never share your data with anyone." | config:7-10 sends `user_id, attendee_emails, meeting_time` to `metricsbay.example.test` | Contradicted | F1 |
| K3 | (omitted) contacts access | config:5 `contacts.read` | Not disclosed | F3 |
| K4 | config:4 comment "the app has no delete path" | Author assertion; no code supplied | UNVERIFIED | S1 |
| K5 | config:1 "deployed 2026-10-19" | Header comment only | UNVERIFIED | S2 |

FINDINGS:

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and verification | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | R | consent.md:4 vs app-config.yaml:7-10 | The absolute promise "never share your data with anyone" is false. Booking and suggestion events send user_id, **attendee emails** and meeting times to a third-party analytics vendor. | A user grants access relying on "never share." On every `meeting_suggested` or `meeting_booked` event, their identifier and their attendees' emails reach metricsbay. The attendees are third parties who saw no consent screen at all. The published promise is broken on the normal path. | Either remove `attendee_emails` (and ideally `user_id`) from the payload, or replace the sentence with an accurate disclosure that names the analytics sharing and the fields. Check that the privacy notice and subprocessor list match. Verify against the deployed config. | y/y/y/y |
| F2 | Critical | CONFIRMED | R | consent.md:3 vs app-config.yaml:3-4 | The text describes read-only access. The grant also covers `calendar.write`, which per the config comment "creates and moves events on the user's behalf." This is a grant whose text omits a material action it covers. | A user believes Slotfinder only looks at their calendar. The app then books or moves a meeting, and attendees get invites or reschedules the user did not expect from what they approved. | Disclose write access plainly, for example "reads and can create or move events on your calendar." Alternatively, drop the write scope if booking is not needed. Verify that the scope list in the shipping build matches the text. | y/y/y/y |
| F3 | Critical | CONFIRMED | R | consent.md (absent) vs app-config.yaml:5 | `contacts.read` is requested, but the consent text never mentions contacts. | A user grants access without knowing their address book (third parties' personal data) is read to suggest attendees. | Add a contacts disclosure, for example "reads your contacts to suggest attendees," or remove the scope. | y/y/y/y |

Severity for all three: (a) a concrete scenario exists, (b) the contradiction is confirmed against the config text, (c) it creates customer and regulatory harm on a consent surface, and (d) it occurs on every normal use. All three are Track R consent findings, not security-boundary findings (`security: false`).

**Siblings searched (F1–F3):** every scope and integration in `app-config.yaml` against every sentence of `consent.md`.
- All 3 scopes and the 1 integration were checked.
- `calendar.read` is the only item the text covers.
- No other undisclosed item exists in the supplied files.
- Undisclosed flows in the unsupplied app code remain unchecked.

NEEDS VALIDATION:
- **S1 (delete path):** the claim that the app cannot delete events is unverified. Settle it with the app code and with whether the provider's `calendar.write` scope technically permits deletion. If the token can delete, the text should not imply otherwise even though the app doesn't do it.
- **S2 (deployed config):** whether the running deployment matches this file. Settle it with the artifact digest or live config compared to `app-config.yaml`.
- **S3 (other documents):** whether the privacy notice and subprocessor list already name metricsbay and attendee-email sharing. If they don't, the same root cause as F1 extends to them. Settle it by reading those documents.
- **S4 (vendor terms):** metricsbay's retention period and processing role. Settle it with the data processing agreement.

REFUTED:
- **Candidate:** "suggest meeting times" is itself false.
- **Why refuted:** suggestion is real (the `meeting_suggested` event). The defect is omission, which is covered by F2.

WHAT HOLDS UP:
- "Reads your calendar to suggest meeting times" is accurate as far as it goes: `calendar.read` exists and suggestion happens.
- The config is explicit enough to make the discrepancies easy to verify.

UNVERIFIED CLAIMS:
- "No delete path" (S1): confirm from the code.
- "Deployed 2026-10-19" (S2): confirm by digest.

QUESTIONS FOR THE AUTHOR:
1. Is `attendee_emails` needed in analytics at all? Removing it changes the F1 fix from a disclosure to a deletion.
2. Is booking (`calendar.write`) part of this release, or can the scope be dropped?
3. Which jurisdictions and consent rules apply, so specific required statements can be checked against rule text?

DECISION-MAKER SUMMARY: Do not ship this consent text. It promises no sharing while the app sends attendee emails to an analytics vendor, and it omits calendar write access and contacts access. Proceeding means users and their contacts are affected by data flows and actions they never agreed to, which creates direct regulatory and trust exposure.

OWNER SUMMARY: The permission screen tells people the app only reads their calendar and never shares their data. In fact it can create and move meetings, reads their contacts, and sends meeting details, including other people's email addresses, to an outside analytics company. The wording must be corrected, or those behaviors removed, before release.

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
    {"item": "running deployment / artifact digest", "status": "not_seen", "matters": true},
    {"item": "application code", "status": "not_seen", "matters": true},
    {"item": "privacy notice and subprocessor list", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "local-review", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "No personal data, credentials or confidential material in the work; vendor is a placeholder domain."},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "consent.md", "kind": "document"},
      {"unit": "app-config.yaml", "kind": "config"},
      {"unit": "app-config.yaml:oauth_scopes", "kind": "section"},
      {"unit": "app-config.yaml:integrations.analytics", "kind": "section"},
      {"unit": "K1 consent.md:3 reads calendar", "kind": "claim"},
      {"unit": "K2 consent.md:4 never share", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "running deployment", "reason": "no_tools"},
      {"unit": "application code", "reason": "not_supplied"},
      {"unit": "privacy notice and subprocessor list", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "R",
     "location": "consent.md:4 vs app-config.yaml:7-10",
     "scenario": "A user grants access relying on 'We never share your data with anyone'; each meeting_suggested/meeting_booked event sends user_id, attendee_emails and meeting_time to metricsbay.example.test, including emails of attendees who never consented.",
     "fix": "Remove attendee_emails (and user_id) from the analytics payload, or replace the sentence with an accurate disclosure naming the analytics vendor and fields; align privacy notice and subprocessor list.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "every scope and integration in app-config.yaml against every consent.md sentence", "found": "F2 and F3 (undisclosed scopes); no other integration"}},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "R",
     "location": "consent.md:3 vs app-config.yaml:3-4",
     "scenario": "A user approves what reads as read-only access; the app then creates or moves events on their calendar under the calendar.write scope, sending invites or reschedules the user did not expect.",
     "fix": "Disclose that the app can create and move calendar events, or drop calendar.write; verify the shipped scope list matches the text.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "every scope in app-config.yaml against consent.md", "found": "F3 (contacts.read undisclosed)"}},
    {"id": "F3", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "R",
     "location": "consent.md (no mention) vs app-config.yaml:5",
     "scenario": "A user grants access without being told their contacts are read; the app reads third parties' personal data to suggest attendees.",
     "fix": "Add a contacts disclosure ('reads your contacts to suggest attendees') or remove the contacts.read scope.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "every scope in app-config.yaml against consent.md", "found": "F2 (calendar.write undisclosed)"}},
    {"id": "S1", "status": "needs_validation", "track": "R", "location": "app-config.yaml:4 comment",
     "suspicion": "calendar.write may technically permit deletion even if the app has no delete path.",
     "unresolved_fact": "Application code and the provider's definition of the calendar.write scope."},
    {"id": "S2", "status": "needs_validation", "track": "R", "location": "app-config.yaml:1",
     "suspicion": "Supplied config may differ from what is running.",
     "unresolved_fact": "Artifact digest or live config of the deployment compared to this file."},
    {"id": "S3", "status": "needs_validation", "track": "R", "location": "privacy notice / subprocessor list (not supplied)",
     "suspicion": "Published documents may also omit metricsbay and attendee-email sharing.",
     "unresolved_fact": "Contents of the current privacy notice and subprocessor list."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "'suggest meeting times' is itself false.",
     "evidence": "The meeting_suggested event and calendar.read scope show suggestion occurs; the defect is omission, covered by F2."}
  ]
}
```