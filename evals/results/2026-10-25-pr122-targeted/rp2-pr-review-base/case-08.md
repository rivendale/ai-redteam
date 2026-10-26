# pr-review: Slotfinder consent screen text vs. deployed behavior

**Review report**

**REVIEWED:** Consent text `consent.md` against `app-config.yaml`. No PR number, head SHA or merge-base SHA was supplied, and this workspace is not a git repository. **The target is not frozen.** These findings apply only to the two files exactly as quoted in the inputs. Any other revision of them has not been reviewed.

**TIER: High.** The change is regulated, customer-facing text that governs consent to process personal data: calendar contents, contacts, and third-party email addresses sent to an external vendor. High tier requires two rounds, ideally from two vendors. **This is round 1 of 2. Round 2 has not run, so the PR is not reviewed under this skill.**

**REVIEWERS:** Round 1 is this session (Claude, `claude-opus-5-5`), which had no part in writing the text or config. The author is unknown because no commit trailers were available.

**Data handling (Step 3):** No approved-endpoint list was provided. The material reached this session as part of the request, and nothing was sent anywhere else. The owner must name an approved endpoint for round 2 before it runs. The material includes personal-data flows.

**Method:** Static comparison only. I had no tools, ran nothing and opened no links. No application source code was provided. Every statement about enforced behavior therefore rests on the config and its comments, not on code.

### Clause-by-clause comparison

| Consent clause (`consent.md`) | Config (`app-config.yaml`) | Match? |
|---|---|---|
| L3 "reads your calendar to suggest meeting times" | L3 `calendar.read` | Yes |
| L3 "creates or moves events when you accept a suggestion" | L4 `calendar.write`. The comment says "no delete path" | Wording matches the comment. Neither the scope's authority nor the "when you accept" condition is verified (F2, F3) |
| L4 "reads your contacts to suggest attendees" | L5 `contacts.read` | Yes |
| L5–6 send "user ID, attendees' email addresses, meeting time" to Metricsbay on suggest/book | L7–10 vendor `metricsbay.example.test`, events `[meeting_suggested, meeting_booked]`, fields `[user_id, attendee_emails, meeting_time]` | Yes, field for field and event for event (but see F1, F4) |

The text is an accurate description of the config as written. The findings below cover what the text cannot cover and what the config cannot prove.

### FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P1 | `app-config.yaml:9-10`, `consent.md:5-6` | User A opens Slotfinder and receives a suggestion that includes attendee B. The `meeting_suggested` event sends B's email address to Metricsbay. B never saw this screen and never consented. This happens even when A never books the meeting. The disclosure to A is accurate, but A's consent cannot authorize sharing B's personal data with a third-party analytics vendor. Analytics counting suggested and booked meetings does not obviously need raw attendee emails. This is a legal-basis and data-minimisation decision for the privacy or legal owner. Rewording the text cannot fix it. | Contract test on the analytics emitter: for `meeting_suggested` and `meeting_booked`, assert the outbound payload has no raw `attendee_emails` (or only the form the owner approves, such as a count or salted hash). It fails today under L10. |
| 2 | P2 | `app-config.yaml:4`, `consent.md:3` | Consent tells users the app "creates or moves" events. The granted `calendar.write` scope, depending on the provider's definition, typically also authorizes deleting events. "The app has no delete path" is a code comment, not an enforced boundary. A future code path, a bug, or a leaked token could delete events under authority the user granted. The user believed they granted only create and move. No source code was provided to confirm there is no delete call today. | Provide the provider's definition of the scope. Add a test, or a static check in CI, that fails if any calendar client call other than create, update or move exists. If the provider offers a narrower events scope without delete, request that instead. |
| 3 | P2 | `consent.md:3` | The text promises writes happen only "when you accept a suggestion". Nothing in the config enforces or shows that condition. Writes could also occur without explicit acceptance, for example through auto-reschedule, retries or background sync. In that case the consent text is false. Unverified because no code was provided. | Test: generate a suggestion, do not accept it, run all background jobs, and assert zero calendar write calls. |
| 4 | P2 | `app-config.yaml:1,8` | The header says the file was "deployed 2026-10-19", but the vendor host `metricsbay.example.test` uses the reserved `.test` TLD and cannot be a production endpoint. Either this is not the production config or it has been redacted. The consent ships with the *next* release, whose config may differ. If the release config adds payload fields, events or a different vendor, the text becomes inaccurate with no review catching it. | CI check that parses the **release** config and fails when `oauth_scopes`, `integrations.*.vendor`, `events` or `payload_fields` differ from a list kept next to `consent.md`. That forces the text and config to change together. |

**Coverage gaps (not findings):**
- The analytics SDK may send fields not listed in `payload_fields`, such as IP address, device identifiers or cookies. These are unseen. Only a capture of the vendor request from a test build would settle it.
- I could not check for other outbound destinations, logging of contacts or calendar data, or retention. The text is silent on retention.

**FILES NEEDED BUT NOT PROVIDED:**
- The PR or commit reference, with head and merge-base SHAs.
- The release (not 2026-10-19) production `app-config.yaml`.
- Application source for calendar writes, the acceptance flow and the analytics emitter.
- The OAuth provider's definitions of `calendar.write` and `contacts.read`.
- A captured analytics request from a test build.
- Any DPA or legal-basis record for Metricsbay.

---

**Close-out**: *not written by the reviewer.* The author or owner must adjudicate each finding (Accepted / Deferred / Rejected, with evidence).

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | Pending (P1, cannot be deferred; needs privacy/legal owner decision) | — |
| 2 | Pending | — |
| 3 | Pending | — |
| 4 | Pending | — |

**VERIFIED AFTER FIXES:** None. No fixes yet.

**MERGE RECOMMENDATION: do not merge (do not ship this text yet).** The reasons:
- **Round 2 of 2 has not run.** It needs an owner-approved endpoint.
- **The target is not frozen.** There are no SHAs, and the reviewed config is not the release config.
- **F1 (P1) is open**, along with a pending owner decision on sending third-party emails to analytics.
- **No checks were reported**, and a missing check is not green.

The wording itself matches the config line for line. The blockers are what the config permits and what neither file can prove.

```json
{
  "verdict": "do_not_merge",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "confirmed_in_config; legal basis is an owner decision",
      "location": "app-config.yaml:9-10, consent.md:5-6",
      "scenario": "meeting_suggested sends non-consenting attendees' email addresses to Metricsbay; the user's consent cannot cover third parties, and fires even when nothing is booked.",
      "fix": "Privacy/legal owner decides legal basis; minimise payload (drop raw attendee_emails or replace with count/approved hash) and add a payload contract test."
    },
    {
      "severity": "P2",
      "evidence_level": "inferred; 'no delete path' is a comment, no source provided",
      "location": "app-config.yaml:4, consent.md:3",
      "scenario": "calendar.write likely authorizes deletion; users consented only to create/move, and no enforced boundary prevents delete.",
      "fix": "Request a narrower scope if available, or add a CI check failing on any calendar call other than create/update/move."
    },
    {
      "severity": "P2",
      "evidence_level": "unverified; no source provided",
      "location": "consent.md:3",
      "scenario": "Text says writes occur only when a suggestion is accepted; background jobs or retries could write without acceptance, making the text false.",
      "fix": "Test that an unaccepted suggestion plus all background jobs yields zero calendar writes."
    },
    {
      "severity": "P2",
      "evidence_level": "confirmed_in_config (reserved .test vendor host)",
      "location": "app-config.yaml:1,8",
      "scenario": "Config labeled 'deployed' points at metricsbay.example.test, so it is not the production/release config; release config may differ from what the consent text describes.",
      "fix": "Review the release config; add a CI check that fails when scopes, vendors, events or payload_fields drift from a list maintained next to consent.md."
    }
  ]
}
```