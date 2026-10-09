# Adversarial Diagnostic Review: station-photo uploader secrets audit

## Pass 1: Reconstruct

The request is to confirm that the repository holds no secrets before it is made public with its full history. The current tree (`settings.py`) reads `DOCK_API_KEY` from the environment and contains no literal credential. A clean tree, however, is not enough. The claim "holds no secrets" is true only if every commit reachable from every published ref is free of secrets, and only if any secret ever committed is no longer valid. Load-bearing assumptions:

- `git_history.txt` is the complete, unedited output of `git log -p --all`.
- No other refs exist.
- No binary or non-diffable content hides material.
- Any historical credential has been revoked.

## Pass 2: Attack (Track B, secrets and history)

- **Current tree:** clean. The only value is the bucket name.
- **History:** commit `1ae4c58` (2026-08-19) adds `DOCK_API_KEY = "pk_pedalo_live_7c1e9a4f2b6d8035e1a7"`. Commit `b72d90e` removes it from the tree but not from history. Publishing with history publishes the key.
- **Rotation:** nothing in the material says the key was rotated. The fix commit message, "read the dock API key from the environment", covers moving the key, not revoking it. The `live` infix suggests a production key. The `pk_` prefix might mean a "publishable" key that is designed to be public, but nothing establishes that. The project's own fix treats it as a secret.
- **Positive control (rule 3):** the history excerpt does surface a literal secret. That shows the input can reveal secrets, so a clean result on the other lines means something. It does not prove the excerpt is complete.
- **Completeness of the excerpt:** real `git log` output includes `Author:` lines, and this paste has none. So the paste was edited or abridged, and its completeness is unverified. Author names and emails will also be published, which is a minor exposure but not a secret.
- **Scope oddity:** the repository is described as the uploader, yet the entire history touches only `settings.py`. Either the uploader code lives elsewhere, or the log does not cover the whole repository that will be published.
- **`PHOTO_BUCKET`:** the bucket name is not a secret. Publishing it does make the bucket a known target, so its access policy matters.
- **Default `""`:** the empty fallback fails silently, but that is not a secrets issue and is out of scope.

## Pass 3: Self-check

Every finding below cites a line in the provided material. I downgraded the "key is still valid" claim to PROBABLE because rotation could have happened outside git. The most serious problem I might still be missing would hide outside this log: in refs that the log does not show, in a remote such as an existing private GitHub repo or forks, in CI configuration, in files ignored by `.gitignore`, or in GitHub-side artifacts like issues, Actions logs and release assets. None of those are covered by `git log -p --all`.

---

**VERDICT: REWORK.** The repository is not safe to publish because its history contains a live-labelled API key. That key must be revoked first, and preferably also purged from history.

**CONFIDENCE IN VERDICT: high.** The leak is plainly visible in the history. What limits confidence is whether the history excerpt is complete and whether the key was already rotated.

## FINDINGS

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | `git_history.txt`, commit `1ae4c58`, line `+DOCK_API_KEY = "pk_pedalo_live_7c1e9a4f2b6d8035e1a7"` (removed again in `b72d90e`) | The production dock API key is in history. Removing it from the tree does not remove it from history. | The repo is made public. Within minutes, secret scanners and anyone who clones it can read the key from commit `1ae4c58` and call the dock API as Pedalo. | Revoke and rotate the key at the dock API provider **before** publishing, and check the provider's access logs for use since 2026-08-19. Then rewrite history (`git filter-repo --replace-text`) or publish a fresh squashed repository. Rewriting history without rotating the key is not a fix. |
| 2 | High | PROBABLE | Commit `b72d90e`, message "read the dock API key from the environment" | Nothing indicates the key was rotated when it was moved to the environment. The same value is probably still in use via `PEDALO_DOCK_API_KEY`. | The team rewrites history, believes the problem is solved, and the key keeps working. Any earlier exposure (clones, a private remote, CI logs) remains exploitable. | Confirm with the key owner that the value in `PEDALO_DOCK_API_KEY` differs from `…7c1e9a4f2b6d8035e1a7` and that the old key returns 401. |
| 3 | Medium | PROBABLE | `git_history.txt` as a whole: no `Author:` lines; only `settings.py` appears in the history of an "uploader" | The history excerpt looks edited or incomplete, so a clean result on the remaining lines cannot be trusted as covering the whole repository. | Another file, or a commit that was trimmed from the paste, holds a second credential and gets published. | Run a scanner against the actual repository: `gitleaks detect --log-opts="--all"` or `trufflehog git file://. --since-commit=` with no limit. Confirm `git for-each-ref` and `git stash list` show only `main`. Seed a known fake secret first as a positive control. |
| 4 | Medium | UNVERIFIED | Context: "made public" | Exposure beyond git has not been audited: an existing remote, forks, CI and Actions logs, issues and PRs, release artifacts. | The key was printed in a CI log or pushed to a private GitHub repo that is about to be flipped to public, so its PR diffs and cached views keep the secret even after the history rewrite. | Publish to a **new** repository from the cleaned history instead of flipping an existing one to public. Review CI logs for the key string. |
| 5 | Low | CONFIRMED | `settings.py`: `PHOTO_BUCKET = "pedalo-station-photos"` | The bucket name is not a secret, but publishing it invites probing. | The bucket allows public listing or writes, and attackers find it by name and abuse it. | Verify the bucket policy blocks public list and write access before publishing. |

## WHAT HOLDS UP

The current `settings.py` contains no literal secret and reads the key from the environment correctly. If the history excerpt is complete, the only secret-bearing line in it is the one in Finding 1.

## UNVERIFIED CLAIMS

- **That the history is complete.** Confirm by rerunning `git log -p --all` together with a scanner on the real repository.
- **That there are no other refs.** Confirm with `git for-each-ref`, `git stash list`, and `git reflog`.
- **That the key is a secret rather than a publishable key.** Confirm with the dock API provider's documentation for `pk_` keys.
- **Whether the key has already been rotated.** Confirm with the provider console.

## QUESTIONS FOR THE AUTHOR

1. Was `pk_pedalo_live_7c1e9a4f2b6d8035e1a7` revoked? If so, when?
2. Is `git_history.txt` the unedited, full output, and where is the uploader code itself?
3. Will this be published as a new repository, or will an existing private repository be made public?

## DECISION-MAKER SUMMARY

Do not publish yet. A live dock API key sits in the repository's history and becomes public with it. Revoke the key first, then publish from a history-cleaned copy into a new repository after a full scanner run. Proceeding as is hands anyone the ability to act on the dock API as Pedalo.

## OWNER SUMMARY

The current code is clean, but an older version of it contained a real access key, and publishing the project would expose that key to everyone. Before going public, the key needs to be cancelled and replaced, and the old version removed from the published copy. Once that is done and a full automated scan comes back clean, the project can be published.

```json
{
  "verdict": "REWORK",
  "findings": [
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "git_history.txt, commit 1ae4c58: +DOCK_API_KEY = \"pk_pedalo_live_7c1e9a4f2b6d8035e1a7\" (removed in b72d90e)",
      "scenario": "Repository is made public with full history; anyone or any secret scanner reads the live dock API key from commit 1ae4c58 and uses it against the dock API.",
      "fix": "Revoke and rotate the key at the provider before publishing and review its access logs since 2026-08-19; then purge it from history (git filter-repo --replace-text) or publish a fresh squashed repo. History rewrite alone is insufficient."
    },
    {
      "severity": "High",
      "evidence_level": "PROBABLE",
      "location": "git_history.txt, commit b72d90e message 'read the dock API key from the environment'",
      "scenario": "The key was moved to the environment but never rotated; after a history rewrite it still works and any prior exposure remains exploitable.",
      "fix": "Confirm PEDALO_DOCK_API_KEY holds a different value and that the old key is rejected (401) by the dock API."
    },
    {
      "severity": "Medium",
      "evidence_level": "PROBABLE",
      "location": "git_history.txt overall: no Author lines; only settings.py appears for an 'uploader' repo",
      "scenario": "The history paste is edited or incomplete; a second secret in an omitted file or commit is published.",
      "fix": "Run gitleaks or trufflehog over all refs of the real repo with a seeded fake secret as a positive control; confirm git for-each-ref and git stash list show only main."
    },
    {
      "severity": "Medium",
      "evidence_level": "UNVERIFIED",
      "location": "context.md: 'made public'",
      "scenario": "An existing private remote is flipped to public, or the key appears in CI logs or PR diffs, so it stays exposed despite a history rewrite.",
      "fix": "Publish to a new repository from cleaned history; search CI and Actions logs for the key string."
    },
    {
      "severity": "Low",
      "evidence_level": "CONFIRMED",
      "location": "settings.py: PHOTO_BUCKET = \"pedalo-station-photos\"",
      "scenario": "The bucket name becomes public; if the bucket allows public list or write, attackers find and abuse it.",
      "fix": "Verify the bucket policy blocks public list and write before publishing."
    }
  ]
}
```