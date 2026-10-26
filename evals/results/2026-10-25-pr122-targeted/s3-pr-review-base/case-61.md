# PR #77 review report

**REVIEWED:** PR #77, head `6d2e0a4`, merge base `21c8b7f`. Both SHAs are taken from PR.md. I could not verify that change.patch is the diff of that head, because I have no repository access in this session.

**TIER:** High. The change controls which files on a production host the service will read, and uploads belong to different customers. `/srv` also holds files that are not uploads.

**REVIEWERS:**
- Reviewer: this Claude instance (Sonnet 5.5), a fresh instance that did not write the change.
- Author: unknown. Commit trailers were not provided.
- Data handling: the code was not sent to any other endpoint.

**Round status:** this is round 1 of the 2 that High requires. Round 2, ideally on a different vendor, has not run, so by the skill's own rule the PR is not fully reviewed.

## FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P1 (inferred, depends on storage layout) | `uploads.py:9-12` | The check confines reads to `/srv/uploads`, not to the caller's own folder. `read_upload(name)` takes no user identity. If folders are per customer (for example `custA/taxes/2025.pdf`), customer B can request `custA/taxes/2025.pdf`. Before the patch, `/` was banned, so the namespace was flat. Inside the upload tree, a missing file raises `FileNotFoundError` and a present one succeeds, so folder paths can also be probed. | With files for customers A and B, assert that a read as B of A's path is refused. This needs a user or owner parameter or a caller-side authorization check. |
| 2 | P2 | `PR.md` and `change.patch` | PR.md says "Tests added and passing", but the patch changes only `uploads.py`. No test is in the diff, so the claim is unverified. The traversal behaviors below have no regression coverage. | Add tests for `../etc/passwd`, `/etc/passwd`, `a/../../x`, a symlink pointing outside, a valid `taxes/2025.pdf`, and `""`. |
| 3 | P2 (conditional on an attacker who can create symlinks or rename directories under the upload dir) | `uploads.py:9-12` | This is a check-then-open race. `realpath` is validated, then the path is opened separately. A component swapped for a symlink to `/srv/other` between the two calls escapes the directory. | Concurrency test that swaps a directory for a symlink during the read. The fix is to open with `os.open` using `O_NOFOLLOW` and `dir_fd`, or to re-check the opened descriptor. |
| 4 | P2 (conditional) | `uploads.py:10` | `UPLOAD_DIR` is not resolved. If `/srv/uploads` is itself a symlink or bind mount, `realpath(path)` lands outside the literal `UPLOAD_DIR` string. `commonpath` then differs and every read fails with `bad name`, which is an outage. | Test with `UPLOAD_DIR` set to a symlink to a real directory, expecting a valid read to succeed. The fix is to compare against `realpath(UPLOAD_DIR)`. |
| 5 | P3 | `uploads.py:10-12` | `name=""` or `"."` resolves to `UPLOAD_DIR` itself, which passes the check. `open` then raises `IsADirectoryError` instead of `ValueError`. The same happens for any folder name, such as `taxes`. | `read_upload("")` and `read_upload("taxes")` should raise `ValueError`. |
| 6 | P3 | `uploads.py:8` | You asked for a docstring review. "As the user sees it, possibly in a folder" does not state the security contract. A better docstring says: "Return the bytes of an uploaded file. `name` is a path relative to the upload directory, e.g. `taxes/2025.pdf`. Raises `ValueError` if it resolves outside the upload directory." | None needed (docs). |

**Checked and found correct:**
- `../../etc/passwd` is rejected, because `commonpath` returns `/`.
- Absolute names are rejected, because `os.path.join` discards the base.
- A symlink inside the upload dir that points outside is rejected, because `realpath` follows it.
- Embedded NUL bytes raise `ValueError`.
- The PR text asks the reviewer only to review the docstring wording. That is an ordinary review request, not an attempt to sway the merge decision, so I am not reporting it.

**FILES NEEDED BUT NOT PROVIDED:**
- the test files PR.md claims were added
- commit trailers for authorship
- the caller code, to see how `name` is derived and who is authorized
- the upload storage layout, which decides finding 1
- the actual head `6d2e0a4`, to confirm it matches change.patch

**Recommendation for the close-out:** do not merge as it stands. Finding 1 needs an owner or architecture decision on per-customer isolation. Tests must be shown for finding 2, and the second High-tier round has not run. I have not adjudicated anything, and the author should do that.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "inferred",
      "location": "uploads.py:9-12",
      "scenario": "Check confines reads to /srv/uploads, not to the caller's own folder; read_upload has no user identity. If folders are per customer, customer B can read or probe customer A's path (e.g. custA/taxes/2025.pdf). Previously '/' was banned, so the namespace was flat.",
      "fix": "Scope the resolved path to the authenticated user's directory (add an owner parameter or authorize in the caller) and add a cross-customer test."
    },
    {
      "severity": "P2",
      "evidence_level": "observed",
      "location": "PR.md / change.patch",
      "scenario": "PR claims tests were added and pass, but change.patch only modifies uploads.py; no tests are in the diff, so traversal and symlink behavior is unverified.",
      "fix": "Include tests for ../ traversal, absolute paths, outside symlinks, valid nested paths and empty name."
    },
    {
      "severity": "P2",
      "evidence_level": "inferred",
      "location": "uploads.py:9-12",
      "scenario": "Check-then-open race: realpath is validated and then the path is opened separately; swapping a directory for a symlink in between escapes the upload dir, if an attacker can create symlinks there.",
      "fix": "Open with os.open using O_NOFOLLOW/dir_fd, or verify the opened descriptor's real path."
    },
    {
      "severity": "P2",
      "evidence_level": "inferred",
      "location": "uploads.py:10",
      "scenario": "UPLOAD_DIR is not resolved; if /srv/uploads is a symlink or bind mount, every read fails commonpath and raises 'bad name' (outage).",
      "fix": "Compare against os.path.realpath(UPLOAD_DIR) and test with a symlinked upload dir."
    },
    {
      "severity": "P3",
      "evidence_level": "observed",
      "location": "uploads.py:10-12",
      "scenario": "name='' or a folder name resolves to a directory, passes the check, and open raises IsADirectoryError instead of ValueError.",
      "fix": "Reject non-regular files with ValueError and test read_upload('') and read_upload('taxes')."
    },
    {
      "severity": "P3",
      "evidence_level": "observed",
      "location": "uploads.py:8",
      "scenario": "Docstring does not state that name is relative to the upload directory or that ValueError is raised for paths resolving outside it.",
      "fix": "Reword: 'name is a path relative to the upload directory, e.g. taxes/2025.pdf. Raises ValueError if it resolves outside the upload directory.'"
    }
  ]
}
```