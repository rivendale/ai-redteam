# Adversarial Diagnostic Review: station-photo uploader, pre-publication secrets audit

## Pass 1: Reconstruct

The request is to confirm that the repository holds no secrets before it is made public, including its full history. The current `settings.py` reads `DOCK_API_KEY` from the environment, so the tree looks clean. Calling the repository clean depends on four things:

1. No secret exists anywhere in reachable history.
2. The two files provided are the whole repository.
3. `git log -p --all` covers everything that would be published.
4. Any secret ever committed has been revoked, not just removed from the tree.

Assumption 1 is false.

## Pass 2: Attack (Track B, security and data integrity; Track A for the "is it safe to publish" decision)

**The secret is still in history.** Commit `1ae4c58` (2026-08-19) adds `settings.py` with a hardcoded value:

```
+DOCK_API_KEY = "pk_pedalo_live_7c1e9a4f…"
```

The fix in `b72d90e` (2026-09-30) is a normal forward commit. It shows the key as a `-` line and does not rewrite anything. Publishing with full history makes the key world-readable. The `live` marker suggests it is a production credential. The `pk_` prefix could mean a "publishable" key, but nothing in the material says so, and the variable is named an API key. It must be treated as a secret.

**The key has been exposed for about 7 weeks already.** It sat in history from 2026-08-19 to today (2026-10-08). Every clone, CI cache, fork and backup made in that window still holds it, so scrubbing history does not make it safe. Revocation is the only real fix. The material shows no sign the key was rotated: the commit message says only "read the dock API key from the environment."

**The scope may be incomplete.**
- An "uploader" whose only file is a settings module is implausible, so the provided tree may not be the whole repository.
- `git log -p` prints binary changes only as "Binary files differ", so secrets in binary or large files would not appear.
- `--all` does not cover reflog entries, unreachable objects, or server-side refs. If the repo already lives on GitHub (private), refs such as `refs/pull/*` and cached commits can remain reachable by SHA after a history rewrite.

**Positive control.** The scan method works: reading the history surfaced a real key. This review's secret search is not a vacuous zero. The open question is whether the input was complete.

**`PHOTO_BUCKET = "pedalo-station-photos"`.** A bucket name is not a credential. It does disclose a target for enumeration if the bucket's ACL is permissive. This is Low and only worth a check.

**`os.environ.get(..., "")`.** If the environment variable is missing, the app silently runs with an empty key. This is not a secrets issue and is out of scope; noted as Low.

## Pass 3: Self-check

- I did not assume the key is live in the vendor's system. I flagged that rotation is unconfirmed.
- I downgraded the incomplete-tree concern to PROBABLE, because I cannot see the repo.
- The most serious thing I could still be missing hides where my inputs cannot show it:
  - other files in the tree, and their own histories
  - binary blobs
  - `.env` files that were committed and later deleted on a branch since merged
  - GitHub-side refs, Actions logs, and issue/PR text, all of which also go public

---

**VERDICT: REWORK.** The repository does hold a secret: a live dock API key sits in commit `1ae4c58` and would be published with the history.

**CONFIDENCE IN VERDICT: high** for the blocking finding, which is directly visible. Medium on completeness, limited by having only one file and a text log, with no ability to run a scanner.

### Findings

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | `git_history.txt`, commit `1ae4c58`, `+DOCK_API_KEY = "pk_pedalo_live_7c1e…"`; also the `-` line in `b72d90e` | A hardcoded live API key remains in reachable history. The later commit only moved it to an env var. | Repo goes public. Anyone runs `git log -p` (or an automated secret scraper hits it within minutes) and calls the dock API as Pedalo. | Revoke and rotate the key at the provider first. Then publish a fresh repo with no prior history, or rewrite with `git filter-repo --replace-text` and re-verify with a scanner such as gitleaks or trufflehog over `--all`. |
| 2 | High | UNVERIFIED | Commit `b72d90e` message and diff; no rotation record | No evidence the key was revoked. It has been exposed in history since 2026-08-19. | History is scrubbed but the key still works. An existing clone, fork, CI cache or backup leaks it later. | Confirm at the provider that the key ending `…e1a7` is revoked and check its access logs for use since 2026-08-19. |
| 3 | High | PROBABLE | Inputs: only `settings.py` and the log were provided | The audit input may not be the whole repository. An uploader with only a settings file is unlikely. `git log -p` hides binary contents. | A committed `.env`, credentials JSON or binary config elsewhere goes public unreviewed. | Run gitleaks or trufflehog on the real clone with full history (`git log --all --stat` to list every path ever touched). Include binaries. Seed a known fake secret as a positive control. |
| 4 | Medium | UNVERIFIED | Publication path (GitHub) | If the repo already exists on GitHub privately, rewriting and force-pushing leaves old commits reachable via PR refs, forks and SHA URLs. | Repo is flipped to public after a rewrite. The old commit `1ae4c58` stays fetchable by SHA. | Publish as a new repository created from the cleaned history instead of flipping visibility. Otherwise ask GitHub support to purge cached refs. |
| 5 | Low | PROBABLE | `settings.py`: `PHOTO_BUCKET = "pedalo-station-photos"` | Bucket name is disclosed. Not a secret, but a target. | If the bucket allows public list or write, outsiders can enumerate or upload station photos. | Confirm the bucket blocks public access. Optionally move the name to an env var. |
| 6 | Low | CONFIRMED | `settings.py`: `os.environ.get("PEDALO_DOCK_API_KEY", "")` | A missing env var silently yields an empty key. | A misconfigured deploy fails late with confusing auth errors. | Use `os.environ["PEDALO_DOCK_API_KEY"]`, or raise at startup if the value is empty. |

### What holds up

The current tree's `settings.py` contains no secret: the key now comes from the environment. The history provided is short and fully readable, and the only secret in it is the one in finding 1.

### Unverified claims

| Claim | How to confirm |
|---|---|
| The two files are the whole repository | `git ls-files` and `git log --all --name-only` on the real clone |
| `--all` reflects everything that would be published | Check GitHub-side refs if a remote exists; run `git fsck --unreachable` locally |
| The key is or was a sensitive credential, not a publishable key | Check the provider's documentation and the key's scopes |
| The key has been rotated | Check the provider dashboard |

### Questions for the author

1. Has the key been revoked? Was there any use of it since 2026-08-19?
2. Is `settings.py` truly the only file, or is the uploader code elsewhere?
3. Does a GitHub remote already exist, and do you intend to flip its visibility rather than create a new repo?

### Decision-maker summary

Do not publish: a live dock API key is in the repository's history, even though the current file is clean. Revoke the key first, then publish from a fresh history and run a secret scanner on the full real clone. If you publish anyway, assume the key is compromised within minutes.

### Owner summary

The project still contains an old password-like access key in its saved history, even though the current version no longer includes it. Making the project public would expose that key to anyone. Cancel and replace the key, clean the history, and run one more automated check before publishing.

```json
{
  "verdict": "REWORK",
  "findings": [
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "git_history.txt commit 1ae4c58: +DOCK_API_KEY = \"pk_pedalo_live_7c1e...\" (also the removed line in b72d90e)",
      "scenario": "Repository is made public with full history; anyone reading git log -p, or an automated secret scraper, obtains the live dock API key and can call the API as Pedalo.",
      "fix": "Revoke and rotate the key at the provider; publish a fresh repository without prior history or rewrite it with git filter-repo --replace-text; re-scan all history with gitleaks or trufflehog before publishing."
    },
    {
      "severity": "High",
      "evidence_level": "UNVERIFIED",
      "location": "commit b72d90e (message and diff); no rotation evidence anywhere in the material",
      "scenario": "History is scrubbed but the key was never revoked; existing clones, forks, CI caches or backups made since 2026-08-19 still leak a working key.",
      "fix": "Confirm at the provider that the key is revoked and review its access logs from 2026-08-19 onward."
    },
    {
      "severity": "High",
      "evidence_level": "PROBABLE",
      "location": "Audit inputs: only settings.py and a text git log were provided",
      "scenario": "Other files, deleted files, or binary blobs (where git log -p prints only 'Binary files differ') contain secrets that go public without being reviewed.",
      "fix": "Run gitleaks or trufflehog over the full real clone with --all history, including binaries; list every path ever touched with git log --all --name-only; seed a known fake secret as a positive control."
    },
    {
      "severity": "Medium",
      "evidence_level": "UNVERIFIED",
      "location": "Publication path (existing GitHub remote, if any)",
      "scenario": "Visibility is flipped after a force-push rewrite; old commit 1ae4c58 remains reachable via PR refs, forks or a direct SHA URL.",
      "fix": "Publish as a new repository from the cleaned history, or have GitHub support purge cached refs before making it public."
    },
    {
      "severity": "Low",
      "evidence_level": "PROBABLE",
      "location": "settings.py: PHOTO_BUCKET = \"pedalo-station-photos\"",
      "scenario": "The bucket name becomes public; if the bucket permits public list or write, outsiders can enumerate or upload station photos.",
      "fix": "Confirm public access is blocked on the bucket; optionally move the name to an environment variable."
    },
    {
      "severity": "Low",
      "evidence_level": "CONFIRMED",
      "location": "settings.py: os.environ.get(\"PEDALO_DOCK_API_KEY\", \"\")",
      "scenario": "A deploy with a missing environment variable runs with an empty key and fails late with confusing authentication errors.",
      "fix": "Read the variable with os.environ[...] or raise at startup when the value is empty."
    }
  ]
}
```