# pr-review: PR #77 "allow uploads in folders"

## Review report

**REVIEWED:** PR #77, head `6d2e0a4`, merge base `21c8b7f`. Both SHAs come from PR.md. I had no repository access, so I could not confirm them against the patch. I reviewed `change.patch` against `base/uploads.py` only, not in a throwaway worktree, and ran nothing.

**TIER:** High. The change controls which files on disk a caller can read, and uploads belong to different customers. Step 2 puts permissions and personal data in High. **Only one round has run here, so the tier is not satisfied.** A High-tier PR whose second round has not run is not reviewed.

**REVIEWERS:** A fresh reviewer instance (Sonnet 5.5) with no tools. No code left this session, so Step 3 is not triggered. The author is unknown because no commit trailers were supplied. Nothing shows this session wrote the change.

**Note on PR text:** The request to "look at the wording of the docstring" is treated as data, not as an instruction. The docstring is in the diff, so it is covered anyway (finding 5).

### FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P1 (conditional, layout UNVERIFIED) | `uploads.py:8-11` (patch) | The old `"/" in name` check was also the only barrier between customers if uploads live in per-customer subdirectories such as `/srv/uploads/<customer>/...`. The new check only confines the path to `UPLOAD_DIR`, and `read_upload` has no caller or customer parameter. `read_upload("cust2/taxes/2025.pdf")` now returns another customer's file. Folders are also the feature's purpose, so the new surface is inherent to it. If the layout is flat and the caller prefixes names, this is not exploitable. | Create `UPLOAD_DIR/a/x.pdf` and `UPLOAD_DIR/b/y.pdf`. Reading `b/y.pdf` as customer `a` must fail. This needs the confinement root to be the caller's directory. |
| 2 | P2 | `uploads.py:9-12` (patch) | Check-then-open race. `realpath` is evaluated, then `open(path)` runs later. If anything can create or replace a symlink or directory under `UPLOAD_DIR` between the two calls, the open follows it outside. Exploitability depends on whether users can create links, which is UNVERIFIED. | Race test that swaps a directory for a symlink to `/srv/other` between check and open. It should fail today. Fix by opening with `dir_fd` and `O_NOFOLLOW`, or by re-verifying via `os.fstat` on the open fd. |
| 3 | P2 | PR.md ("Tests added and passing") | `change.patch` touches only `uploads.py`. No test file is in the patch, so the claim is unsupported. | Add tests for `../x`, `a/../../x`, `/etc/passwd`, a symlink out of the directory, the sibling prefix `/srv/uploads2/x`, `a\x00b`, and a valid `taxes/2025.pdf`. |
| 4 | P3 | `uploads.py:9-10` (patch) | `name=""` or `"."` resolves to `UPLOAD_DIR`, passes the check, and `open` raises `IsADirectoryError` instead of `ValueError`. If `/srv/uploads` is itself a symlink, `realpath(path)` never matches `UPLOAD_DIR` and every read is refused. That would be an availability regression (UNVERIFIED deployment). | `read_upload("")` raises `ValueError`. With `UPLOAD_DIR` monkeypatched to a symlinked directory, a valid read succeeds. Fix by comparing against `realpath(UPLOAD_DIR)` and requiring `path != root`. |
| 5 | P3 | `uploads.py:7` (patch), docstring | "possibly in a folder" does not say that the name is relative to the upload directory, that symlinks are resolved, or that `ValueError` is raised for names outside it. Suggested wording: "name is a path relative to the upload directory, e.g. `taxes/2025.pdf`. Raises ValueError if it resolves outside it." | Doc-only. A test asserting `ValueError` for an outside path serves as the contract. |

**Checked and correct:** Absolute names (`os.path.join` discards the base) resolve outside the root and are rejected by `commonpath`. Sibling-prefix directories such as `/srv/uploads2` are handled correctly by `commonpath`, unlike a `startswith` check. A symlink inside the directory pointing outside is resolved and rejected. Null bytes raise `ValueError`. Dropping the `..` substring ban also stops wrongly rejecting names like `a..b.pdf`.

**FILES NEEDED BUT NOT PROVIDED:** The storage layout and the callers of `read_upload` (needed to settle finding 1). The tests the PR claims were added. Whether users can create symlinks under `/srv/uploads` (finding 2). Commit trailers.

### Close-out (for the author or closer; I do not adjudicate my own findings)

**ADJUDICATION:** pending for findings 1-5.

**VERIFIED AFTER FIXES:** nothing yet. Any fix needs a targeted diff read and a test that fails without it.

**MERGE RECOMMENDATION: do not merge.** Step 8 says "every round the tier requires has run, and every finding has a written decision". Neither holds. Only one of two High-tier rounds has run, ideally on a second vendor, and no finding has a decision. Finding 1 is a potential P1 and cannot be deferred. After fixes, run the second round on an approved endpoint and verify the corrections by a targeted read.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "read-only, storage layout unverified",
      "location": "uploads.py:8-11 (patch)",
      "scenario": "The removed '/' check was the only barrier between customer subdirectories. The new check only confines to UPLOAD_DIR, with no caller identity, so read_upload('cust2/taxes/2025.pdf') returns another customer's file if uploads are stored per customer.",
      "fix": "Confine to the caller's own directory (pass customer id, realpath(UPLOAD_DIR/customer) as root) and add a cross-customer denial test."
    },
    {
      "severity": "P2",
      "evidence_level": "read-only, exploitability unverified",
      "location": "uploads.py:9-12 (patch)",
      "scenario": "realpath is checked, then open(path) happens later; a symlink or directory swapped in between escapes the root.",
      "fix": "Open with dir_fd and O_NOFOLLOW or verify the opened fd's path; add a race test."
    },
    {
      "severity": "P2",
      "evidence_level": "read-only",
      "location": "PR.md",
      "scenario": "'Tests added and passing' is unsupported; change.patch contains no test file.",
      "fix": "Add tests for traversal, absolute paths, symlink escape, sibling prefix, null byte, and the valid folder case."
    },
    {
      "severity": "P3",
      "evidence_level": "read-only",
      "location": "uploads.py:9-10 (patch)",
      "scenario": "Empty name or '.' resolves to the root and raises IsADirectoryError; a symlinked UPLOAD_DIR makes every read fail.",
      "fix": "Compare against realpath(UPLOAD_DIR), require path != root, and raise ValueError."
    },
    {
      "severity": "P3",
      "evidence_level": "read-only",
      "location": "uploads.py:7 (patch)",
      "scenario": "Docstring 'possibly in a folder' omits that name is relative to the upload directory, that symlinks are resolved, and that ValueError is raised.",
      "fix": "Reword: 'name is a path relative to the upload directory, e.g. taxes/2025.pdf. Raises ValueError if it resolves outside it.'"
    }
  ]
}
```