# pr-review report: PR #77 "allow uploads in folders"

**REVIEWED:** PR #77, head `6d2e0a4`, merge base `21c8b7f`. These SHAs are taken from PR.md. I had no repository, so I could not confirm them, and I read only `change.patch` and `base/uploads.py`.

**TIER:** High. The change is the path-confinement check that decides which files on disk the service reads. The context says uploads belong to different customers and `/srv` holds other readable files, so this is a permissions and personal-data boundary.

**REVIEWERS:** This is one round by a fresh instance (Sonnet 5.5) with no part in writing the change. The author is unknown because no commit trailers were supplied. No code left this session, and I did not run anything.
- **Second round not run.** High tier requires two rounds, ideally on two vendors, and only one has run. By Step 2 the PR is not fully reviewed.
- **Approved endpoint needed.** The second round has to go to an endpoint approved for customer-data code. I have no list of approved endpoints.

**What I checked (traced by reading, not executed):**
- `name="../x"` and `name="/etc/passwd"` are rejected. `join` discards `UPLOAD_DIR` for an absolute name, and `commonpath` then yields `/`.
- A sibling directory such as `/srv/uploads-evil` is rejected. `commonpath` compares path components, not string prefixes.
- A symlink inside the upload directory that points outside is rejected, because the check runs on `realpath`.
- The old `".." in name` check also blocked legitimate names like `a..b.pdf`. That is now fixed.

## FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P1 | `uploads.py:10` | The check confines reads to the whole `/srv/uploads` tree, not to the requesting customer's folder. `read_upload(name)` takes no user identity. If uploads are laid out as `<customer>/<file>`, which folders invite, then `read_upload("customerB/taxes/2025.pdf")` from customer A passes the check and returns B's file. The old flat code had the same gap, but folders now make the layout predictable. The caller was not provided, so whether scoping happens upstream is unverified. | Create `/uploads/a/f.pdf` and `/uploads/b/f.pdf`. Assert a read as user A of `b/f.pdf` raises, either through a `user` parameter or through the caller's prefix enforcement. |
| 2 | P1 | `change.patch` (no test file), `PR.md` | The PR says "Tests added and passing", but the patch touches only `uploads.py`. No test is visible, and none of the traversal, absolute-path or symlink behavior is evidenced. | A new test file covering `../x`, `/etc/passwd`, `a/../../x`, a symlink escape, a sibling prefix (`/srv/uploads-evil`), `""`, a NUL byte, and the happy path `taxes/2025.pdf`. |
| 3 | P3 | `uploads.py:8` (docstring, which the author asked about) | The docstring does not say that `name` is relative to the upload directory. It also does not say that a `ValueError` is raised for escaping paths, or that `FileNotFoundError` or `IsADirectoryError` can occur. `name=""` resolves to `UPLOAD_DIR`, passes the check, and fails in `open` with `IsADirectoryError` instead of `ValueError`. | Assert `read_upload("")` and `read_upload("taxes")` (a directory) raise a consistent, documented error. |
| 4 | P3 | `uploads.py:4,10` | `UPLOAD_DIR` is not passed through `realpath`. If `/srv` or `/srv/uploads` is itself a symlink, every resolved path differs from `UPLOAD_DIR`, and every read fails with "bad name". It fails closed, but it is an outage. | Monkeypatch `UPLOAD_DIR` to a symlinked directory and assert a valid read succeeds. |
| 5 | P3 | `uploads.py:9-12` | There is a time gap between `realpath` and `open`. If any process other than the service can write inside the upload tree, for example archive extraction that creates symlinks, a path component could be swapped to a symlink in that gap. The patch reduces this by opening the resolved path, but does not remove it. Exploitability is unverified. | Hard to test deterministically. Prefer `os.open(..., dir_fd=...)` with no-follow flags, or confirm the upload tree is writable only by the service. |

**Suggested docstring:**
> Return the bytes of an uploaded file. `name` is a path relative to the upload directory and may include folders (e.g. `taxes/2025.pdf`). Raises `ValueError` if the resolved path is outside the upload directory.

No text in the PR addresses the reviewer other than the docstring wording request, which is benign. The patch cites no sources, adds no dependencies, and adds no consent text.

**FILES NEEDED BUT NOT PROVIDED:**
- The callers of `read_upload`, needed for finding 1.
- Any test files in the PR.
- The deployment layout of `/srv/uploads`: symlinks, per-customer folders, and who can write there.
- Commit trailers.

## Merge status
This is not a close-out, since the author has not adjudicated yet. Under Step 8, merge is recommended only when "every round the tier requires has run, and every finding has a written decision". The second High-tier round has not run, and findings 1 and 2 are P1, which cannot be deferred. The current status is **do not merge** until findings 1 and 2 are resolved and the second round is done.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "depends on unseen caller code",
      "location": "uploads.py:10",
      "scenario": "Confinement is to the whole /srv/uploads tree, not the requesting customer's folder. read_upload takes no user identity, so with a per-customer folder layout, read_upload('customerB/taxes/2025.pdf') by customer A passes the check and returns B's file.",
      "fix": "Scope reads to the caller's own folder (pass the user or prefix and confine to realpath(UPLOAD_DIR/user)), or show the caller enforces it, and add a cross-customer test."
    },
    {
      "severity": "P1",
      "evidence_level": "confirmed by reading the patch",
      "location": "change.patch (no test file); PR.md",
      "scenario": "PR claims tests were added and pass, but the patch modifies only uploads.py. No traversal, absolute-path, symlink or sibling-prefix tests are visible.",
      "fix": "Add the tests to the PR and show them failing against the old check and passing against the new one."
    },
    {
      "severity": "P3",
      "evidence_level": "confirmed by reading",
      "location": "uploads.py:8",
      "scenario": "The docstring omits that name is relative to the upload dir and omits the error behavior. An empty name or a directory resolves to UPLOAD_DIR, passes the check, and raises IsADirectoryError instead of ValueError.",
      "fix": "Use the suggested docstring and reject empty or directory targets with a consistent ValueError."
    },
    {
      "severity": "P3",
      "evidence_level": "depends on deployment",
      "location": "uploads.py:4,10",
      "scenario": "UPLOAD_DIR is not realpath-normalised. If /srv or /srv/uploads is a symlink, every read is rejected as 'bad name' (fails closed but is an outage).",
      "fix": "Compare against os.path.realpath(UPLOAD_DIR)."
    },
    {
      "severity": "P3",
      "evidence_level": "unverified",
      "location": "uploads.py:9-12",
      "scenario": "A time gap between realpath and open lets a path component be swapped to a symlink if another process can write in the upload tree.",
      "fix": "Open with dir_fd and no-follow semantics, or ensure only the service can write to the upload tree."
    }
  ]
}
```