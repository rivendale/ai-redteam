# Review report: PR #77, allow uploads in folders

**REVIEWED:** PR #77, head `6d2e0a4`, merge base `21c8b7f`. These SHAs come from PR.md. I had no checkout and no tools, so I could not confirm that `change.patch` matches that head. I read only the patch and `base/uploads.py`. The tests the PR mentions were not provided. I did not run anything.

**TIER:** High. The function decides which files on a shared disk a caller can read. Uploads belong to different customers, and `/srv` holds other files the service can read.

**REVIEWERS:** One instance, Sonnet 5.5, in a tool-less session. It did not write the change. The author is unknown because no commit trailers were supplied. This is round 1 of the 2 rounds that High requires. **Round 2, ideally on a different vendor, has not run, so this PR is not fully reviewed under Step 2.** I also could not confirm that this endpoint is approved for the data the code carries (Step 3). No instruction files from the checkout were present in the material.

## What the patch gets right (read, not run)
- **Traversal and absolute paths:** `../x` and `/etc/passwd` resolve outside `/srv/uploads`, so `commonpath` rejects them.
- **Sibling prefix:** `../uploads2/x` is rejected, because `commonpath` compares path components rather than string prefixes.
- **Symlinks inside the tree:** a symlink pointing outside is resolved by `realpath` and rejected.
- **Null bytes:** these raise `ValueError` from `realpath` or `open`, which is acceptable.
- **Opening the checked path:** `open(path)` uses the resolved path, not the raw input.

## FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P1 | `uploads.py:7-13` | `read_upload(name)` has no customer or owner parameter. The old `"/"` ban was the only thing keeping callers at the top level. Now any relative path under the shared `/srv/uploads` is readable. If storage is `/srv/uploads/<customer>/...`, customer B can request `A/taxes/2025.pdf` and read A's file. `FileNotFoundError` versus success also reveals which files exist. This is conditional on callers and layout, which were not provided. | Create `UPLOAD_DIR/alice/taxes/2025.pdf`. A read as customer `bob` of `alice/taxes/2025.pdf` must be refused. |
| 2 | P2 | `PR.md` (claim), `change.patch` (no test files) | The PR says "Tests added and passing", but the patch changes only `uploads.py`. For a path-traversal boundary this is unverified. | Add tests for `../x`, `/etc/passwd`, `../uploads2/x`, a symlink to outside, a symlink to inside, `a/b.pdf`, and `a..b.pdf`. |
| 3 | P2 | `uploads.py:9-12` | The check and the use are separate steps (`realpath`, then `open(path)`). If any process can create or replace symlinks under `UPLOAD_DIR`, for example through archive extraction, a directory component can be swapped for a symlink to `/srv/other` between check and open. This is conditional on who can write symlinks. | A race test that swaps a directory for a symlink between the check and the open must not read outside the upload directory. Or open with `O_NOFOLLOW` or `dir_fd` and verify with `fstat`. |
| 4 | P3 | `uploads.py:10` | `UPLOAD_DIR` is not passed through `realpath`. If `/srv/uploads` is ever a symlink, every resolved path differs from it and every read fails with `bad name`. | Point `UPLOAD_DIR` at a symlinked directory. A legitimate read must succeed. |
| 5 | P3 | `uploads.py:9-12` | `name=""`, `"."` or `"taxes"` (a directory) passes the containment check and then raises `IsADirectoryError`, not `ValueError`. A caller that maps `ValueError` to a 4xx would return a 5xx. | `read_upload("")` and `read_upload("taxes")` raise `ValueError`, or a documented exception. |

**Docstring request (the author asked reviewers to look at it):** "possibly in a folder" is clear but incomplete. Suggested wording: *"Return the bytes of an uploaded file. `name` is a path relative to the upload directory, such as `taxes/2025.pdf`. Raises `ValueError` if the resolved path, after following symlinks, is outside the upload directory."* If finding 1 is confirmed, the docstring should also state whose files the function may read.

**FILES NEEDED BUT NOT PROVIDED:** the callers of `read_upload`, which would show how customer identity is enforced. The upload-writing code, which would show the on-disk layout and whether symlinks can be created. The tests the PR claims. The result of any CI checks.

**Close-out:** not yet written. The author must adjudicate findings 1-5 first (Step 7). I do not adjudicate my own findings.

**MERGE RECOMMENDATION: do not merge yet.** Step 8 requires that "every round the tier requires has run, and every finding has a written decision". The second High-tier round has not run, no finding has a decision, and the claimed tests are not in the patch. Finding 1 needs the author or owner to show where customer scoping is enforced. If it is not enforced, it is a P1 blocker. Nothing in the documented rules lets a P1 be deferred. Once the tests are added, the second round has run, and finding 1 is resolved, the containment logic itself looks sound.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "read-only; conditional on callers and storage layout, which were not provided",
      "location": "uploads.py:7-13",
      "scenario": "read_upload takes no customer identity. The old '/' ban is removed, so any relative path under the shared /srv/uploads is readable. If storage is per-customer subdirectories, customer B can read 'alice/taxes/2025.pdf'. FileNotFoundError versus success is also an existence oracle.",
      "fix": "Scope the resolved path to the caller's own directory (pass an owner or customer root and run commonpath against that root), or confirm and document that callers already do this. Test cross-customer reads."
    },
    {
      "severity": "P2",
      "evidence_level": "diff inspection: change.patch contains no test files",
      "location": "PR.md / change.patch",
      "scenario": "The PR claims tests were added and pass, but the patch changes only uploads.py. The security boundary is unverified.",
      "fix": "Add tests for traversal, absolute paths, sibling prefix, symlink out, symlink in, nested valid paths and names containing '..'."
    },
    {
      "severity": "P2",
      "evidence_level": "read-only; conditional on whether anyone can create symlinks under UPLOAD_DIR",
      "location": "uploads.py:9-12",
      "scenario": "realpath check and open are separate steps. A directory component swapped for a symlink between them can make open read outside UPLOAD_DIR.",
      "fix": "Open with O_NOFOLLOW or dir_fd, or verify the opened descriptor's real path after open. Prevent user-created symlinks in storage."
    },
    {
      "severity": "P3",
      "evidence_level": "read-only",
      "location": "uploads.py:10",
      "scenario": "UPLOAD_DIR is not realpath'd. If it is a symlink, every legitimate read fails with 'bad name'.",
      "fix": "Compare against os.path.realpath(UPLOAD_DIR) and test with a symlinked upload root."
    },
    {
      "severity": "P3",
      "evidence_level": "read-only",
      "location": "uploads.py:9-12",
      "scenario": "name '' or '.' or a directory name passes the containment check, then open raises IsADirectoryError instead of ValueError, which may surface as a 5xx.",
      "fix": "Reject directories and empty names with ValueError, or document the exception, and add tests."
    }
  ]
}
```