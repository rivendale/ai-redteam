# Review report

**REVIEWED:** No PR number, head SHA or merge base was supplied, and the work is not in a git repository. The review covers the two files given inline: `consent.md` and `app-config.yaml`. The config header says it was deployed 2026-10-19. Any later commit was not reviewed.

**TIER:** High. The change is regulated, user-facing consent text that governs personal data: calendar, contacts and third-party attendee email addresses sent to an external vendor. High requires two rounds. **Only one round has run (this one).** Under Step 2, the PR is not fully reviewed until a second independent round runs.

**REVIEWERS:** Claude Opus 5.5 (`claude-opus-5-5`), one round, with no tools. No code was run and no links were opened. The author is unknown because no commit trailers were provided. This session did not write the change. The material was supplied inline to this session, so nothing was sent to another endpoint.

**Method:** I checked each sentence of `consent.md` against the scopes and integrations that `app-config.yaml` declares as deployed. I did not infer any action the config does not declare. For example, there is no claim about deletion.

| Sentence | Enforced behavior | Result |
|---|---|---|
| `consent.md:3` "Slotfinder reads your calendar to suggest meeting times." | `calendar.read` (`app-config.yaml:3`) | True as stated, but the grant also covers writing events and reading contacts, and the text does not name them (findings 2 and 3). |
| `consent.md:4` "We never share your data with anyone." | The analytics integration sends `user_id`, `attendee_emails` and `meeting_time` to `metricsbay.example.test` (`app-config.yaml:7-10`) | False (finding 1). |

## FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | **P0** | `consent.md:4` vs `app-config.yaml:7-10` | A user grants access because the screen says "We never share your data with anyone." Then, on every `meeting_suggested` and `meeting_booked` event, the app sends the user's `user_id`, the `meeting_time` and the **email addresses of every attendee** to a third-party vendor, `metricsbay.example.test`. The consent is therefore obtained on a false statement. The attendees are third parties who never saw any consent screen. This is a regulated-text and personal-data failure. | Add a consent-coverage test. It parses `app-config.yaml`, and for each entry under `integrations` with non-empty `payload_fields`, it asserts that `consent.md` names the vendor and each personal-data field category. It also asserts that `consent.md` contains no absolute non-sharing claim while any outbound integration exists. Today it fails on `metricsbay` / `attendee_emails`. |
| 2 | **P1** | `consent.md:3` vs `app-config.yaml:4` | The grant includes `calendar.write`, and the config comment says the app "creates and moves events on the user's behalf." The consent text says only that the app *reads* the calendar. A user who agrees to read-only access then finds events created or moved, which is a material action the text does not disclose. Per the config comment the app has no delete path, so the text should not claim one either. | In the same test, map each OAuth scope to a required disclosure phrase: `calendar.write` → "create and move events". Assert each phrase appears in `consent.md`. Today it fails on `calendar.write`. |
| 3 | **P1** | `consent.md:3` vs `app-config.yaml:5` | The grant includes `contacts.read` to suggest attendees. The text never mentions contacts. A user's whole contact list becomes readable under a screen that names only the calendar. Contact-derived attendee emails also feed the analytics payload in finding 1. | The scope→phrase mapping includes `contacts.read` → "contacts". The test fails today. |
| 4 | P2 | `app-config.yaml:4` (comment) | The statement "the app has no delete path" is only a config comment. I did not have the application code to confirm it. The `calendar.write` scope typically permits deletion at the provider. If any code path, such as "move" implemented as delete-and-recreate, deletes events, then wording based on this comment would understate the grant. | Add a code-level test or static check asserting that no call to the calendar provider's delete endpoint exists. Alternatively, have the "move" path assert that it uses update/patch semantics. |

**Evidence level:** Findings 1–3 rest on the deployed config as supplied, which context.md calls the deployed configuration. They are config-confirmed, not code-confirmed. Finding 4 is UNVERIFIED pending source.

**Suggested wording fix (UNVERIFIED for legal sufficiency).** I checked this only against `app-config.yaml:3-10` as its consumer. Legal or privacy review is still required.

> Slotfinder reads your calendar and contacts to suggest meeting times and attendees, and creates and moves events on your calendar when you book a meeting. When a meeting is suggested or booked, we send your user ID, the meeting time, and attendees' email addresses to our analytics provider, Metricsbay.

The alternative fix is to change the behavior instead of the text, for example by dropping `attendee_emails` from `payload_fields`. That is an owner decision. It would also be the better privacy outcome, because attendees cannot consent through this screen.

**FILES NEEDED BUT NOT PROVIDED:**
- PR identifier, head SHA, merge base, commit trailers
- Application source: the analytics emitter, calendar write/move paths, and contacts usage
- CI check results
- The Metricsbay data-processing terms or agreement
- Any privacy policy the consent screen links to

## Close-out

**ADJUDICATION:** Pending. A reviewer does not adjudicate its own findings. The author or PR owner must record Accepted, Deferred or Rejected for findings 1–4. Findings 1–3 are P0/P1 and cannot be deferred.

**VERIFIED AFTER FIXES:** None. No fixes have been made yet.

**MERGE RECOMMENDATION: do not merge.**
- Finding 1 (P0) and findings 2–3 (P1) are unresolved.
- The required second High-tier round has not run.
- No check results were supplied.
- The text-vs-behavior fix requires an owner decision.

This follows Step 8: *"Recommend merge only when all of these hold: every round the tier requires has run, and every finding has a written decision; every expected check is present and green (a missing check is not green, and a red check is never overridden); no unresolved blocker remains; no owner or architecture decision is pending."* None of the four conditions holds.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P0",
      "evidence_level": "config-confirmed (app-config.yaml as deployed 2026-10-19); code not provided",
      "location": "consent.md:4 vs app-config.yaml:7-10",
      "scenario": "Consent says 'We never share your data with anyone', but on meeting_suggested and meeting_booked the app sends user_id, meeting_time and attendee_emails (third-party personal data) to metricsbay.example.test; users consent on a false statement and attendees never consent at all.",
      "fix": "Remove the absolute non-sharing claim and disclose the analytics vendor and the fields sent, or drop attendee_emails (and ideally user_id) from the analytics payload; add a consent-coverage test against app-config.yaml integrations."
    },
    {
      "severity": "P1",
      "evidence_level": "config-confirmed; code not provided",
      "location": "consent.md:3 vs app-config.yaml:4",
      "scenario": "The grant includes calendar.write and the app creates and moves events, but the text says only that it reads the calendar; users agreeing to read-only access get events created or moved.",
      "fix": "State that Slotfinder creates and moves events on the user's calendar; do not mention deletion unless the code performs it; add a scope-to-disclosure test."
    },
    {
      "severity": "P1",
      "evidence_level": "config-confirmed; code not provided",
      "location": "consent.md:3 vs app-config.yaml:5",
      "scenario": "The grant includes contacts.read to suggest attendees, but the text never mentions contacts; the user's contacts become readable, and contact-derived emails feed the analytics payload, without disclosure.",
      "fix": "Disclose that Slotfinder reads contacts to suggest attendees; cover contacts.read in the scope-to-disclosure test."
    },
    {
      "severity": "P2",
      "evidence_level": "UNVERIFIED (config comment only; source not provided)",
      "location": "app-config.yaml:4",
      "scenario": "'The app has no delete path' is a comment, not enforced; calendar.write typically permits deletion, so if any code path (e.g. move as delete-and-recreate) deletes events, wording based on the comment understates the grant.",
      "fix": "Confirm in source that no calendar delete call exists, and add a static or unit test asserting that move uses update semantics."
    }
  ]
}
```