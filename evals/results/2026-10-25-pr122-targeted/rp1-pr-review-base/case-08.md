# pr-review: Slotfinder consent screen text vs. deployed behavior

## Review report

**REVIEWED:** Consent screen text (`consent.md`) checked against the deployed configuration (`app-config.yaml`, header dated 2026-10-19).
- **Head SHA:** not available. The inputs were pasted content with no PR number, no repository and no commit, so Step 1 could not be met. This review covers only the two files exactly as shown here. Any other version of them is unreviewed.
- **Merge base SHA:** not available.

**TIER:** High. The PR is regulated, customer-facing text. It covers OAuth permission grants (calendar write, contacts read) and sends personal data, including third parties' email addresses, to an outside analytics vendor.
- High requires two independent rounds, ideally from two vendors.
- **This report is round 1 only.** Until round 2 runs on an endpoint approved for this data, the PR is not reviewed under Step 2.

**REVIEWERS:**
- Round 1: this instance (claude-opus-5-5). It had no tools and no part in writing the change. The inputs contain only text and config, with no customer data, so Step 3's data concern is limited to the content shown here.
- Author: unknown. There are no commits, so there are no `Co-Authored-By` trailers to read.

### What matches

I compared each statement in the consent text with the config, line by line:

| Consent statement | Config | Match |
|---|---|---|
| "reads your calendar to suggest meeting times" | `calendar.read` | Yes |
| "creates or moves events when you accept a suggestion" | `calendar.write`, comment: "creates and moves events… no delete path" | Matches the comment. The grant itself is broader (finding 1). "Only when you accept" cannot be checked from config. |
| "reads your contacts to suggest attendees" | `contacts.read`, comment "suggests attendees" | Yes |
| "When a meeting is suggested or booked" | `events: [meeting_suggested, meeting_booked]` | Yes |
| "your user ID, the attendees' email addresses and the meeting time" | `payload_fields: [user_id, attendee_emails, meeting_time]` | Yes, exactly the same three fields |
| "our analytics provider, Metricsbay" | `vendor: metricsbay.example.test` | Name matches. The host is a reserved `.test` domain (finding 3). |

No scope, event or payload field in the config is missing from the consent text. The consent text also claims nothing the config does not show.

### FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `app-config.yaml:4`, `consent.md:3` | The consent text describes what the app *does* ("creates or moves"), not what the user *grants*. On common calendar providers, a write scope also allows deleting and editing any event. The only support for "the app has no delete path" is a YAML comment, and the application code was not provided. A user who agrees to "creates or moves" has actually given delete and edit authority. If a later change, a bug or a token compromise uses that authority, the consent text did not disclose it. Evidence level: inference. It depends on how the provider defines `calendar.write`, which is not in the inputs. | Add a static or integration test asserting that the calendar client never calls delete or update-other-fields endpoints. Add a check that fails if the requested scope grants more than create and move, or require the text to state the full grant. Either narrow the scope, if the provider offers a create-only scope, or say in the consent text that the permission technically allows editing and deleting but Slotfinder only creates and moves events. |
| 2 | P2 | `app-config.yaml:10`, `consent.md:5` | `attendee_emails` are sent to Metricsbay on `meeting_suggested`, before anyone books anything. The data belongs to third parties who never saw this screen and may not be Slotfinder users. The disclosure is accurate, but one user's consent cannot authorize sending other people's addresses to an analytics vendor. Under a regulated-text review, the screen implies a lawful basis it may not provide. The legal answer is an owner/legal decision, not a code defect (see Open decisions). | Add a test asserting the analytics payload for `meeting_suggested` contains no `attendee_emails`, or contains only hashed or pseudonymized values. The test should fail against today's config. Adopt it only if legal decides to minimize the data. |
| 3 | P3 | `app-config.yaml:8` | The file says it was "deployed 2026-10-19", but the vendor host is `metricsbay.example.test`, a reserved TLD that cannot resolve. One of two things is true. Either this is not the real deployed config, so the comparison above does not cover production. Or production analytics is pointed at nothing, and the consent text describes a send that does not happen. In both cases the consent text cannot be shown to match the deployed system. | Diff this file against the production config artifact. Assert that the production vendor host belongs to the entity named in the consent text. |

### FILES NEEDED BUT NOT PROVIDED

- The application code that calls the calendar API. I need it to verify "no delete path" and that writes happen only "when you accept a suggestion".
- The analytics client code. I need it to confirm that only the three configured fields are sent and that no other events fire.
- The OAuth provider's definitions of `calendar.write` and `contacts.read`, to establish exactly what the user grants.
- The production deployed config, or its artifact digest, to resolve finding 3.
- The consent text currently live. The config was deployed on 2026-10-19 but the text "ships with the next release". If attendee emails are already being sent under older text, users who consented before this release were not told.
- The PR or repository itself, with head and base SHAs and commit trailers.

### Open owner and legal decisions (these block merge under Step 8)

- **Third-party data.** Is there a lawful basis for sending attendees' email addresses to Metricsbay? This is finding 2.
- **Bundled consent.** Analytics sharing is part of the same consent as core calendar access, with no opt-out. Is that acceptable in the jurisdictions where Slotfinder ships?
- **Already-sent data.** If the 2026-10-19 config is live, does data already sent under the previous consent text need remediation?

## Close-out

A reviewer does not adjudicate its own findings, so this section is for the author or the person closing the PR.

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | pending | |
| 2 | pending | |
| 3 | pending | |

**VERIFIED AFTER FIXES:** Nothing yet. No fixes have been made.

**MERGE RECOMMENDATION: do not merge (not yet reviewed).**
- The PR is High tier and only round 1 has run.
- The target is not frozen to a SHA.
- Three owner/legal decisions are open.
- The code needed to verify the "no delete path" and "on accept" claims was not provided.

Apart from the scope-breadth gap, the consent text does match the config shown, field for field. Once the decisions are made and round 2 has run, this should close quickly.

```json
{
  "verdict": "do_not_merge",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "inference",
      "location": "app-config.yaml:4; consent.md:3",
      "scenario": "Consent text says the app 'creates or moves' events, but the granted calendar.write scope typically also permits editing and deleting any event. 'No delete path' rests on a YAML comment with no code provided, so users grant broader authority than the text discloses.",
      "fix": "Request a narrower create-only scope if the provider offers one, or state the full grant in the consent text. Add a test asserting the calendar client never calls delete or update endpoints."
    },
    {
      "severity": "P2",
      "evidence_level": "confirmed_from_config",
      "location": "app-config.yaml:10; consent.md:5",
      "scenario": "Attendees' email addresses (third parties who did not see or accept this screen) are sent to Metricsbay on every suggestion, before any booking. The disclosure is accurate, but the user's consent may not provide a lawful basis for third-party data.",
      "fix": "Owner/legal decision. If minimizing, drop or pseudonymize attendee_emails in the analytics payload, and add a test that fails while raw emails are present."
    },
    {
      "severity": "P3",
      "evidence_level": "confirmed_from_config",
      "location": "app-config.yaml:8",
      "scenario": "The 'deployed' config names vendor host metricsbay.example.test, a reserved non-resolving TLD. Either the reviewed config is not production, or analytics points nowhere. In both cases the match between consent text and deployed behavior is unestablished.",
      "fix": "Diff against the production config artifact and assert that the production vendor host belongs to the entity named in the consent text."
    }
  ]
}
```