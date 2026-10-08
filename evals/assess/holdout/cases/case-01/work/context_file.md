# Our context (SYNTHETIC: invented for an eval, not anyone's real stack)

## Goals
1. Get the Android release build under 10 minutes.
2. Cut crash-report noise so the top five crashes are the ones worth fixing.
3. Ship the game in five languages by the end of Q1.
4. Publish the monthly devlog with less hand work.

## Tools already in use
Unity 6 (C#), Jenkins on one self-hosted Mac mini, Firebase Crashlytics (crashes and analytics), Crowdin (translations), Git LFS, Notion, Figma,
ffmpeg for trailer encoding, and a Python script (devlog.py) that drafts the monthly devlog from merged pull requests.

## Constraints
- No new paid subscription or account without the operator's approval.
- No player data goes to a new third party without approval.
- Licenses: MIT, Apache-2.0, BSD or zlib only for code we ship in the game; GPL or AGPL only for tools we run and never ship.
- Builds run on macOS and Windows. Budget for new tools this quarter: $0 unless approved.

## Already decided
- We use Unity, not Godot or Unreal. Firebase stays our crash and analytics service; we run no backend of our own. Our code is on GitHub.
