# Redteam review: station-photo uploader secrets audit

**Review conditions:** same-context review with no tools and no subagent, so anchoring is a risk. Re-run it in a fresh session with repository access before publishing. Nothing below was executed. All evidence comes from the supplied text.

**VERDICT: REWORK.** A live-looking API key is in the repository history. Publishing the history as it stands exposes the key to the world, even though the current tree is clean.

**CONFIDENCE: medium.** It is limited by the review conditions above and by two unknowns: whether the supplied `git log -p --all` output is complete and unedited (it has no Author lines, so it was at least trimmed), and whether a GitHub remote already holds extra refs.

**INPUTS LEDGER**
- **Seen:**
  - `request.md` and `context.md`.
  - `work/settings.py`, the current tree.
  - `work/git_history.txt`: 2 commits, `1ae4c58` and `b72d90e`, both touching only `settings.py`.
- **Not seen:**
  - The repository itself. I could not run `git log`, `git rev-list --all --objects` or a secret scanner. **Matters:** I cannot confirm the excerpt is the full history.
  - Any existing GitHub remote and its refs (`refs/pull/*`, forks, caches). **Matters:** these survive a local history rewrite.
  - The key issuer's documentation on what the `pk_` prefix means. **Matters only for severity framing**, not for the fix.
  - The uploader code. Per the history, no other file was ever committed, so this gap matters only if the excerpt is incomplete.

**COVERAGE**
- **Scope:** the whole repository: current tree plus full history as supplied.
- **Checked:**
  - Every line of both commits' diffs.
  - Every line of the current `settings.py`.
  - `request.md` and `context.md`.
- **Positive control for the "no other secrets" scan:** the same visual scan does find the `pk_pedalo_live_…` string in both diffs. So the scan can match, and its silence elsewhere means something.
- **Not checked:**
  - Commit author names and emails (lines absent from the excerpt).
  - Binary files (not shown by `git log -p`).
  - Unreachable objects and reflog (no tools).

**SEATS AND GATE**
- Same-context reviewer only.
- **Sensitivity gate:** the work contains a credential, so cross-vendor seats are refused. The key must not be sent to an external reviewer.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | B | `settings.py` blob in commit `1ae4c58`, line 2: `DOCK_API_KEY = "pk_pedalo_live_7c1e9a4f2b6d8035e1a7"`. The same blob is rendered as the removed line in `b72d90e`'s diff. | Commit `b72d90e` moved the key to the environment, but the hardcoded live key stays in history. The current tree is clean; the repository is not. | The repo is made public with full history. Anyone running `git log -p`, browsing commit `1ae4c58` on GitHub, or running an automated secret scraper gets the live Pedalo dock API key and can call the dock API as the uploader. The key has also sat in the repo since 2026-08-19, so anyone with existing access may already have it. | **1.** Revoke and rotate the key with the issuer *first*. This is the only fix that works if the key has already leaked. **2.** Then purge it from history, for example with `git filter-repo --replace-text` or by publishing a fresh repo whose first commit is the current tree. **3.** Re-scan the result with gitleaks or trufflehog across all refs. **Reproduction:** in a clone, run `git log -p --all -S 'pk_pedalo_live_7c1e9a4f2b6d8035e1a7'`. Expected: no commits. Observed (per the supplied history): `1ae4c58` and `b72d90e`. | a✔ b✔ c✔ d✔ |

**F1 details**
- **Security finding:** yes.
- **Boundary:**
  - Principal: any anonymous internet user once the repo is public.
  - Input: read access to repository history.
  - Control that fails: the secret was removed only from the tip, not from history.
  - Boundary crossed: public to authenticated Pedalo dock API.
  - Resource affected: whatever the dock API key authorizes.
- **Sibling search:** I searched both commits and the current tree for other credential-shaped strings (`key`, `token`, `secret`, `password`, long hex or base64, URLs with userinfo). None found. `PHOTO_BUCKET = "pedalo-station-photos"` is a resource name, not a credential.
- **Why one finding, not two:** the two diff locations are one stored object, the `settings.py` blob of `1ae4c58`. The `b72d90e` diff only re-renders it, and removing that blob clears both.

## NEEDS VALIDATION

- **S1: completeness of the history.** It is unknown whether the excerpt is the unedited, complete output of `git log -p --all`. It has no Author lines, so it was trimmed. Settle it by running `git rev-list --all --objects` and a scanner over the real repository.
- **S2: an existing GitHub remote.** It is unknown whether the repo already exists on GitHub, privately or otherwise, with pull requests or forks. If it does, `refs/pull/*` and cached commit views keep `1ae4c58` reachable after a force-push. That would need GitHub Support to purge, or creating a new repository instead.
- **S3: the bucket's access policy.** It is unknown whether the `pedalo-station-photos` bucket allows public write or list. Publishing its name is harmless only if it does not.

## REFUTED

- **C1: "The current tree still leaks the key."** Refuted. Current `settings.py` line 4 reads the key from `PEDALO_DOCK_API_KEY` with an empty default. No literal key is present.
- **C2: "`pk_` means a publishable, non-secret key, so there is no finding."** Not accepted as a defense:
  - The prefix is `_live_`.
  - The author's own commit message and docstring ("Secrets come from the environment") treat it as a secret.
  - No issuer documentation was supplied to show otherwise.
  - The question is listed for the author below, but the finding holds unless they show the key is public by design.

## WHAT HOLDS UP

- The current `settings.py` contains no secret.
- Moving the key to an environment variable is the right pattern.
- Nothing else in the history looks like a credential.

## UNVERIFIED CLAIMS

- **"One branch, no tags, no stashes, no other refs."** Confirm with `git for-each-ref` and `git stash list`.
- **That the key is live and still valid.** Confirm with the issuer, then revoke it regardless.

## QUESTIONS FOR THE AUTHOR

1. Has the key been revoked and rotated yet?
2. Does a GitHub repository for this project already exist, with pull requests or forks?
3. Is the supplied log complete and unedited?

## DECISION-MAKER SUMMARY

Do not publish yet. Commit `1ae4c58` contains the live dock API key, and publishing the full history exposes it even though the latest code is clean. Revoke the key, purge it from history (or publish a fresh single-commit repo), and re-scan. Publishing as is hands working API credentials to anyone on the internet.

## OWNER SUMMARY

The current code is clean, but an older saved version of it still contains a working password for the dock system, and making the project public would reveal that old version too. Before publishing, cancel that password and issue a new one, then remove the old version from the project's record or start the public copy fresh. After that, a final automated check for leaked passwords should come back clean before release.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "work/settings.py", "status": "seen", "matters": true},
    {"item": "work/git_history.txt", "status": "seen", "matters": true},
    {"item": "the repository itself (to verify history completeness)", "status": "not_seen", "matters": true},
    {"item": "existing GitHub remote and its refs", "status": "not_seen", "matters": true},
    {"item": "key issuer documentation for the pk_ prefix", "status": "not_seen", "matters": false}
  ],
  "seats": [
    {"vendor": "same-context", "status": "ran", "cross_vendor": false},
    {"vendor": "cross-vendor", "status": "refused", "cross_vendor": true}
  ],
  "sensitivity_gate": {"sensitive": true, "reason": "The work contains a live API credential; it must not be sent to external reviewers."},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "work/settings.py", "kind": "file"},
      {"unit": "work/git_history.txt", "kind": "file"},
      {"unit": "commit 1ae4c58 diff", "kind": "data"},
      {"unit": "commit b72d90e diff", "kind": "data"}
    ],
    "not_checked": [
      {"unit": "commit author names and emails", "reason": "not_supplied"},
      {"unit": "binary objects, unreachable objects, reflog", "reason": "no_tools"},
      {"unit": "GitHub remote refs (refs/pull/*, forks)", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "settings.py line 2 in commit 1ae4c58 (also rendered as the removed line in b72d90e)",
     "scenario": "Once the repository is public with full history, anyone browsing commit 1ae4c58 or scraping it obtains the live Pedalo dock API key pk_pedalo_live_... and can call the dock API as the uploader; the key has also been readable by repo holders since 2026-08-19.",
     "fix": "Revoke and rotate the key with the issuer first; then purge it from history (git filter-repo --replace-text, or publish a fresh repo whose first commit is the current tree) and re-scan all refs with gitleaks or trufflehog.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "In a clone run: git log -p --all -S 'pk_pedalo_live_7c1e9a4f2b6d8035e1a7'. Expected: no commits. Observed per supplied history: 1ae4c58 and b72d90e.",
     "security": true,
     "boundary": {"principal": "any anonymous internet user after publication", "input": "read access to repository history",
                  "control": "the secret was removed only from the tip, not from history", "crossed": "public to authenticated dock API",
                  "resource": "the Pedalo dock API and whatever the key authorizes"},
     "siblings_searched": {"searched": "both commits' diffs and the current settings.py for key, token, secret, password, long hex/base64 strings and URLs with credentials",
                           "found": "no other credential; PHOTO_BUCKET is a resource name; the b72d90e occurrence is the same blob as 1ae4c58, not a separate stored copy"}},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "work/git_history.txt",
     "suspicion": "The excerpt may be trimmed or incomplete (no Author lines), hiding other secrets.",
     "unresolved_fact": "Output of git rev-list --all --objects plus a secret scanner over the real repository."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "GitHub remote (if any)",
     "suspicion": "Existing pull requests or forks keep 1ae4c58 reachable after a force-push.",
     "unresolved_fact": "Whether a GitHub repository with PRs or forks already exists for this project."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "settings.py:5 PHOTO_BUCKET",
     "suspicion": "Publishing the bucket name matters if the bucket allows public write or list.",
     "unresolved_fact": "The access policy of the pedalo-station-photos bucket."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "The current tree still leaks the key.", "evidence": "Current settings.py line 4 reads os.environ.get(\"PEDALO_DOCK_API_KEY\", \"\"); no literal key."},
    {"id": "C2", "candidate": "pk_ marks a publishable non-secret key, so there is no finding.", "evidence": "The key is marked _live_ and the author's commit message and docstring treat it as a secret; no issuer documentation shows it is public by design."}
  ]
}
```