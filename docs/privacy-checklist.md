# Privacy checklist for reviewed work

Use with any track when the work touches personal information: names, contact details, financial or health records,
location, identifiers, or anything a person would not want repeated. Each item is a question with the failure it
catches.

## Where the data goes

1. **Does personal data reach a hosted model, and under what retention?** Read the retention from the provider's
   response header or settings on the review date, per key and per endpoint. Ask separately whether the data may be
   used for training: unlike a breach, which exposes a copy, training can make data part of a model that cannot be
   recalled. (A judgment, not a measured ranking; weigh it against your own threat model.)
2. **Is an unofficial relay or reseller in the path?** A relay sits between you and the provider and can see and
   log every prompt. A price far below the provider's own is a reason to ask how the relay pays for it, not proof of
   misuse.
3. **Is there a route for data that must never leave the machine?** Local models exist for this; see
   [rivendale/local-ai](https://github.com/rivendale/local-ai).
4. **Does standing configuration carry context across sessions?** Memory, project instructions and connected apps
   can leak one conversation's details into another. Keep standing context minimal.

## What is collected and kept

5. **Is each field needed?** Collect the minimum; a central store of identity data is a target.
6. **How long is it kept, and is deletion verified by the system, not by the name of a file?**
7. **Do logs, analytics, error reports or summaries repeat personal data?** "Counts and aggregates only" is a rule
   that can be checked; "we're careful" is not.

## How it is shown and shared

8. **Is redaction tested with a dummy value?** A redaction idiom can print the very value it hides.
9. **Is a secret described by where it is, never by what it is?**
10. **Does a published artifact (repository, page, report, screenshot) contain a person's details, a child's
    likeness, or a document someone shared in confidence?** Strip the story; keep the practice.

## Tools that cut both ways

11. **Reconnaissance tools (OSINT search across usernames, breaches, exposed services) are for auditing your own
    exposure.** Pointing them at other people is surveillance. Their output about you is itself sensitive.
12. **Before any second opinion from another vendor's model, check the work for personal data.** If present, use a
    zero-retention or local route, or no external review; the `redteam` skill's sensitivity gate does this.
