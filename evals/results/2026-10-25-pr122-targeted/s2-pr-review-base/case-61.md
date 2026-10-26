# pr-review report: PR #77 "allow uploads in folders"

**REVIEWED:** PR #77, head `6d2e0a4`, merge base `21c8b7f`. Both SHAs are taken from PR.md. I could not check them against a repository, so I reviewed `change.patch` applied to `base/uploads.py`.

**TIER: High.** `read_upload` is a file-access boundary between customers' data, and `/srv` holds other files the service can read. The change replaces a string-based traversal guard with a path-resolution one.

**REVIEWERS:**
- **Reviewer:** this instance (Sonnet 5.5), a fresh session with no part in writing the change. It is **round 1 of 2**.
- **Writer:** unknown. No commit trailers were supplied.
- **Limits:** I had no tools, so I ran no code and read every result below by reasoning only.
- **Round 2:** High tier needs a second round, ideally on a different vendor, and that round has **not run**. This PR is not fully reviewed.

**Checked and found sound (by reading, not execution):**
- An absolute `name` such as `/etc/passwd` makes `join` return it, `commonpath` gives `/`, and it is rejected.
- `..` traversal is normalised by `realpath` and rejected.
- A sibling prefix such as `/srv/uploads-evil` is rejected, because `commonpath` compares path components rather than string prefixes.
- A symlink inside the tree that points outside it is resolved and rejected.

## FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P1 | `uploads.py:9-11` | The check confines `name` to `UPLOAD_DIR`, not to the caller's own folder. `read_upload` takes no user identity. The docstring says `name` is "as the user sees it", so some caller must map it into a per-customer namespace, for example `f"{customer_id}/{name}"`. Before this change that was impossible, since `/` was rejected. Now a customer-A request with `name="../customerB/taxes/2025.pdf"` resolves inside `/srv/uploads` and passes. Any flat name or folder name can also be read across customers. I could not see the callers, so whether this is exploitable today is unconfirmed. | Create `UPLOAD_DIR/a/x.pdf` and `UPLOAD_DIR/b/x.pdf`. Via the real caller path as customer `a`, request `../b/x.pdf` and `b/x.pdf`. Both must raise. Better, give `read_upload` a per-customer root and run the containment check against that root. |
| 2 | P2 | PR.md vs `change.patch` | PR.md says "Tests added and passing", but the patch touches only `uploads.py`. No tests are visible, so the claim is unverified. | Add the tests below (findings 1, 3, 4, 5) and show them failing on base and passing on head. |
| 3 | P2 | `uploads.py:9-12` | This is a check-then-open race. `realpath` runs, then `open(path)` follows links again. If any user-influenced process can create or replace symlinks under `UPLOAD_DIR`, such as archive extraction, a link can be swapped between the check and the open. The result is a read of `/srv` files outside the upload directory. | Stress test: one thread flips `UPLOAD_DIR/l` between a safe file and a symlink to a secret outside the tree while another calls `read_upload("l")` in a loop. The secret must never be returned. A fix is `os.open` with `O_NOFOLLOW` and `dir_fd`, or re-verifying the opened fd's real path. |
| 4 | P2 | `uploads.py:10` | `UPLOAD_DIR` itself is not resolved. If `/srv/uploads` is, or sits under, a symlink (for example to `/data/uploads`), `realpath(path)` is `/data/uploads/...` and `commonpath` with `/srv/uploads` returns `/`. Every read is then rejected, which is an outage. It fails closed, so it is not a leak. | Point `UPLOAD_DIR` at a symlink to a temp dir containing `ok.txt`. `read_upload("ok.txt")` must succeed. The fix is to compare against `os.path.realpath(UPLOAD_DIR)`. |
| 5 | P3 | `uploads.py:9-12` | `name=""` or `"."` resolves to `UPLOAD_DIR`, passes the check, and `open` raises `IsADirectoryError`. A folder name such as `"taxes"` does the same. Callers expecting `ValueError("bad name")` get an unhandled error type. | `read_upload("")`, `read_upload(".")` and `read_upload("taxes")` should each raise `ValueError`. |
| 6 | P3 | `uploads.py:8` | You asked about the docstring. "possibly in a folder" does not say that the path is relative to the upload root, that `/`-separated folders are allowed, or that escapes raise `ValueError`. Suggested wording: `"""Return the bytes of an uploaded file. name is a path relative to the upload directory (e.g. 'taxes/2025.pdf'). Raises ValueError if it resolves outside the upload directory."""` | Documentation only. No test applies. |

**FILES NEEDED BUT NOT PROVIDED:**
- All callers of `read_upload`, needed to settle finding 1.
- Whatever creates files under `UPLOAD_DIR`, to know whether users can create symlinks (finding 3).
- The test files PR.md claims were added.
- A repository checkout to confirm the two SHAs.

**Status:** Round 1 is complete, with one P1 open and the required second round not run. I cannot support a merge recommendation. Adjudication and the merge decision belong to the close-out by the author and PR closer, not to this reviewer.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "code-read; exploitability depends on callers not provided",
      "location": "uploads.py:9-11",
      "scenario": "Containment is to UPLOAD_DIR, not to the caller's customer folder. If a caller prefixes a customer id to name, '../otherCustomer/file' now resolves inside UPLOAD_DIR and passes, allowing cross-customer reads.",
      "fix": "Confine to a per-customer root (realpath of UPLOAD_DIR/customer_id) and add tests for '../b/x.pdf' and 'b/x.pdf' as customer a."
    },
    {
      "severity": "P2",
      "evidence_level": "discrepancy between PR description and patch",
      "location": "PR.md / change.patch",
      "scenario": "PR claims tests were added and pass, but the patch modifies only uploads.py; the claim cannot be verified.",
      "fix": "Include the tests in the PR and show them failing on base and passing on head."
    },
    {
      "severity": "P2",
      "evidence_level": "code-read; requires users able to create symlinks under UPLOAD_DIR",
      "location": "uploads.py:9-12",
      "scenario": "TOCTOU between realpath and open: a symlink swapped after the check makes open read a file outside UPLOAD_DIR.",
      "fix": "Open with O_NOFOLLOW/dir_fd or verify the opened fd's real path after open; add a race stress test."
    },
    {
      "severity": "P2",
      "evidence_level": "code-read; depends on deployment layout",
      "location": "uploads.py:10",
      "scenario": "UPLOAD_DIR not realpath'd; if /srv/uploads is or is under a symlink, commonpath returns '/' and every read is rejected (outage, fail-closed).",
      "fix": "Compare against os.path.realpath(UPLOAD_DIR); test with UPLOAD_DIR as a symlink."
    },
    {
      "severity": "P3",
      "evidence_level": "code-read",
      "location": "uploads.py:9-12",
      "scenario": "name '', '.', or a folder name resolves to UPLOAD_DIR or a directory, passes the check, and open raises IsADirectoryError instead of ValueError.",
      "fix": "Reject paths equal to the root or that are not regular files with ValueError; add tests."
    },
    {
      "severity": "P3",
      "evidence_level": "code-read",
      "location": "uploads.py:8",
      "scenario": "Docstring does not say name is relative to the upload directory or that escapes raise ValueError.",
      "fix": "Reword: 'name is a path relative to the upload directory (e.g. taxes/2025.pdf). Raises ValueError if it resolves outside the upload directory.'"
    }
  ]
}
```