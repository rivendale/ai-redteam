# PR #77 Review Report

**REVIEWED:** PR #77 "allow uploads in folders". Head `6d2e0a4`, merge base `21c8b7f`. Both SHAs are taken from PR.md. I had no git access, so I could not confirm that `change.patch` matches the head. I reviewed `change.patch` against `base/uploads.py` only.

**TIER:** High. The change is the path-confinement check for file reads. It touches permissions and data handling, uploads belong to different customers, and `/srv` holds other readable files.

**REVIEWERS:** This is a single round by a fresh Claude Sonnet 5.5 instance with no part in writing the change. No commit trailers were supplied, so the author is unknown. No data was sent outside this session.
**The second High-tier round has not run, so under Step 2 this PR is not fully reviewed.**

## What the patch gets right
- Absolute names like `/etc/passwd` are rejected. `os.path.join` discards `UPLOAD_DIR`, and `commonpath` then returns `/`.
- `../x` and symlinks pointing outside the directory are rejected, because `realpath` resolves them before the check.
- A sibling directory like `/srv/uploads-old/x` is rejected, because `commonpath` compares whole path components rather than string prefixes.
- A null byte in the name raises `ValueError`, so the code fails closed.

## FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P1 | `uploads.py:8-10` (patched) | The check confines reads to the whole `UPLOAD_DIR`, not to the caller's own folder. The old `".." in name` guard is gone. If uploads are stored per customer (`/srv/uploads/alice/...`) and the caller prefixes or trusts a user-supplied name, then `alice/../bob/taxes/2025.pdf` or simply `bob/taxes/2025.pdf` resolves inside `UPLOAD_DIR` and passes. Alice reads Bob's file. `read_upload(name)` has no identity parameter, so it cannot enforce isolation. Evidence level: inferred, because callers and storage layout were not provided. | With `alice/a.pdf` and `bob/b.pdf` present, a read scoped to alice must raise for `../bob/b.pdf`, `alice/../bob/b.pdf` and `bob/b.pdf`. It must succeed for `taxes/2025.pdf` under alice's folder. |
| 2 | P2 | `change.patch` (whole) | PR.md says "Tests added and passing", but the patch touches only `uploads.py`. No test is visible and none could be run. The security property (traversal rejection) has no seen coverage. | Add a test file covering `../x`, `/etc/passwd`, a symlink out, `a/../../x`, a sibling-prefix directory, and a valid `taxes/2025.pdf`. |
| 3 | P3 | `uploads.py:8-9` | `name=""` or `"."` resolves to `UPLOAD_DIR` itself and passes the check. `open` then raises `IsADirectoryError` instead of `ValueError("bad name")`, which leaks a different error type to callers. Likewise any name that resolves to a directory. | `read_upload("")` and `read_upload("taxes")` (a directory) must raise `ValueError`. |
| 4 | P3 | `uploads.py:8-11` | Check-then-use race: `realpath` is checked, then `open(path)` happens later. If anything other than the service can create or swap symlinks under `UPLOAD_DIR` (archive extraction, shared mounts), a component can be swapped after the check. Evidence level: theoretical, depends on who can write the directory. | Hard to test deterministically. Prefer `os.open` with `dir_fd` and `O_NOFOLLOW`, or re-verify the opened fd's path. Add a stress test that swaps a symlink during reads. |
| 5 | P3 | `uploads.py:4` (unchanged constant, used at `:8`) | If `/srv/uploads` is itself a symlink, `realpath(path)` never has the literal `UPLOAD_DIR` as its prefix, so every read is rejected (fails closed, but breaks the feature). Evidence level: conditional on deployment. | Point `UPLOAD_DIR` at a symlinked dir in a test. A valid file must still be readable if `UPLOAD_DIR` is canonicalized with `realpath` at load time. |
| 6 | P3 | `uploads.py:7` (docstring) | You asked for a docstring review. "possibly in a folder" does not say that the name is relative to the upload root, that absolute paths and `..` escapes are rejected, or which customer's folder it is scoped to. | Not applicable. Suggested wording: "Return the bytes of the upload at `name`, a path relative to the upload root (for example `taxes/2025.pdf`). Raises `ValueError` if the resolved path leaves the root." |

The request in PR.md to look at the docstring is an ordinary author request. It does not try to influence the merge decision, so it is not a finding.

**FILES NEEDED BUT NOT PROVIDED:**
- The callers of `read_upload`, which show how `name` is built and whether a customer prefix is applied.
- The upload-writing code and the storage layout (per-customer or flat).
- The tests PR.md claims were added.
- Commit metadata (trailers, SHAs).

## Close-out (pending)
**ADJUDICATION:** Not done. The author or PR closer must give a decision for each of findings 1–6. I do not adjudicate my own findings.

**VERIFIED AFTER FIXES:** Nothing yet.

**MERGE RECOMMENDATION: Do not merge.**
- Finding 1 is a P1, and a P1 cannot be deferred.
- The tests are unseen.
- The second High-tier round has not run.
- The missing callers and storage layout prevent confirming or ruling out cross-customer access.

Fix finding 1 by scoping `read_upload` to a per-customer root (for example `read_upload(customer_id, name)`, confined to `UPLOAD_DIR/<customer_id>`). Add the tests, then run the second round on an approved second endpoint.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "inferred",
      "location": "uploads.py:8-10 (patched)",
      "scenario": "Confinement is to the whole UPLOAD_DIR, not the caller's customer folder, and the old '..' guard is removed. With per-customer folders, a name such as 'alice/../bob/taxes/2025.pdf' or 'bob/taxes/2025.pdf' resolves inside UPLOAD_DIR and passes, so one customer can read another's upload. read_upload has no identity parameter. Callers and layout were not provided.",
      "fix": "Scope reads to a per-customer root (read_upload(customer_id, name) confined to UPLOAD_DIR/<customer_id>) and test cross-customer traversal attempts."
    },
    {
      "severity": "P2",
      "evidence_level": "read",
      "location": "change.patch (whole)",
      "scenario": "PR claims tests were added and pass, but the patch contains only uploads.py; no test is visible or runnable, so traversal rejection is uncovered.",
      "fix": "Add tests for '../x', absolute paths, symlink escape, 'a/../../x', sibling-prefix dir, and valid 'taxes/2025.pdf'."
    },
    {
      "severity": "P3",
      "evidence_level": "read",
      "location": "uploads.py:8-9",
      "scenario": "name '' or '.' (or any directory) resolves to UPLOAD_DIR and passes the check; open raises IsADirectoryError instead of ValueError('bad name').",
      "fix": "Reject paths that equal UPLOAD_DIR or are not regular files; test read_upload('') and a directory name."
    },
    {
      "severity": "P3",
      "evidence_level": "theoretical",
      "location": "uploads.py:8-11",
      "scenario": "Check-then-use race between realpath and open: if another actor can create or swap symlinks under UPLOAD_DIR, a path component can be swapped after the check.",
      "fix": "Open with os.open using dir_fd and O_NOFOLLOW, or verify the opened fd's resolved path."
    },
    {
      "severity": "P3",
      "evidence_level": "conditional",
      "location": "uploads.py:4",
      "scenario": "If /srv/uploads is itself a symlink, realpath(path) never has the literal UPLOAD_DIR prefix and every read is rejected (fails closed).",
      "fix": "Canonicalize UPLOAD_DIR with os.path.realpath at load time; test with a symlinked upload dir."
    },
    {
      "severity": "P3",
      "evidence_level": "read",
      "location": "uploads.py:7",
      "scenario": "Docstring 'possibly in a folder' does not state that name is relative to the upload root, that '..' and absolute escapes raise ValueError, or the per-customer scope.",
      "fix": "Reword: 'Return the bytes of the upload at name, a path relative to the upload root (e.g. taxes/2025.pdf). Raises ValueError if the resolved path leaves the root.'"
    }
  ]
}
```