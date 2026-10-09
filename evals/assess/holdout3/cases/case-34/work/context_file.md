# Our context (SYNTHETIC: invented for an eval, not anyone's real stack)

## Goals
1. Cut editing time to under 2 hours per episode.
2. Grow the newsletter: more listeners sign up.
3. Publish a transcript with every episode.
4. Keep loudness consistent from one episode to the next.

## Tools already in use
Reaper (editing) on a Mac mini, ffmpeg, Buzzsprout (hosting and the RSS feed), Mailchimp (the newsletter and the signup form on the show site), Google Docs (show notes),
a static site built with Hugo and published on GitHub Pages, a shared password manager, and loudness.py: a script that normalizes each finished episode to -16 LUFS with ffmpeg's
loudnorm and appends the measured loudness before and after to loudness.log. Every cut, including every silence and filler word, is made by hand in Reaper; nothing automates cutting, and ffmpeg is used only by loudness.py.
The show gets about 3,000 downloads per episode and publishes weekly (45 minutes).

## Constraints
- No new paid subscription or account without the host's approval.
- No listener or subscriber data goes to a new third party without approval.
- Code that ships on the show site (theme and shortcodes) must be MIT, Apache-2.0 or BSD; GPL or AGPL only for tools we run on our own machines.
- The machines are Macs. Budget for new tools this quarter: $0 unless approved.

## Already decided
- Buzzsprout stays our host and Mailchimp stays our newsletter. We edit in Reaper. The show stays audio only.
