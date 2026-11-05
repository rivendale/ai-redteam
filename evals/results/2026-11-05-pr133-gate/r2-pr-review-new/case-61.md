# PR #77 review report

**REVIEWED:** PR #77 "allow uploads in folders". Head `6d2e0a4`, merge base `21c8b7f`. Both SHAs are taken from PR.md. I had only the pasted files, with no checkout, so I could not confirm that `change.patch` is the content of that head.
**TIER:** High. The change is a path-containment check on file reads, which is access control. It can expose other customers' data and the other files under `/srv`.
**REVIEWERS:** This instance (Claude Sonnet 5.5), one round, with no tools: nothing was run and no links were opened. Author unknown, because no commit trailers were supplied. This session did not write the change. **The required second High-tier round (ideally another vendor) has not run, and I could not check which endpoints are approved for this data.** Per Step 2 the PR is therefore not fully reviewed.

**Instruction files / injection check:** I saw no instruction files and no text aimed at the reviewer. The request to look at the docstring wording is an ordinary review request, not an override, and is covered by finding 5.

**What I checked and found sound (by reading only)**
- `commonpath` compares whole path components, so a sibling like `/srv/uploads-evil` is rejected.
- An absolute `name` makes `os.path.join` discard `UPLOAD_DIR`, the result is outside it, and it is rejected.
- `..` segments and symlinks that resolve outside `UPLOAD_DIR` are rejected after `realpath`, so these fail closed.
- Opening `path` (the resolved path) rather than the raw join is the right choice.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P1 (UNVERIFIED, callers not provided) | `uploads.py:9-10` | The boundary is the whole `UPLOAD_DIR`, not the requesting customer. Once nested names are allowed, if uploads are laid out per customer (`custA/…`, `custB/…`) or the caller passes a user-controlled `name`, customer A calls `read_upload("custB/taxes/2025.pdf")` and gets B's file. The old flat check never allowed folders, so this exposure is new. If the caller prefixes or scopes the name, the finding drops. | Call with owner A and `name="custB/x.pdf"` where the file exists. Expect a rejection, and check the caller's scoping. |
| 2 | P2 | PR.md vs `change.patch` | PR.md says "Tests added and passing", but the patch changes only `uploads.py`. No test file is in the diff, so the claim is unsupported. | Add tests for `../x`, `a/../../x`, `/etc/passwd`, a sibling prefix dir, a symlink out, a symlink inside, and a valid `taxes/2025.pdf`. |
| 3 | P3 | `uploads.py:9-12` | `name=""` or `"."` resolves to `UPLOAD_DIR` itself and passes the check. `open` then raises `IsADirectoryError`, not the documented `ValueError`. | `read_upload("")` and `read_upload(".")` should raise `ValueError`. |
| 4 | P3 | `uploads.py:9-12` | The check and the `open` are separate steps (TOCTOU). Anyone who can create or swap symlinks under `UPLOAD_DIR` between them can redirect the read. This needs write access to that tree, and I don't know whether uploads can create symlinks. Also, if `/srv/uploads` is itself a symlink, `realpath(path)` never matches the unresolved `UPLOAD_DIR` and every read is rejected. That is fail-closed but a deployment hazard. | Test with `UPLOAD_DIR` as a symlink (should work, so resolve `UPLOAD_DIR` too). Consider `os.open` with `O_NOFOLLOW` or `openat`-style handling. |
| 5 | P3 | `uploads.py:8` (docstring) | The docstring wording is unclear. "possibly in a folder" doesn't say the name is relative to the upload root, uses `/` separators, may not escape the root, or that `ValueError` (bad name) and `FileNotFoundError` can be raised. | Docs only, so no test. Suggested text: "`name` is a path relative to the upload directory, using `/` for folders (e.g. `taxes/2025.pdf`). Raises `ValueError` if it resolves outside the upload directory." |

**FILES NEEDED BUT NOT PROVIDED:** the callers of `read_upload` (how `name` is derived and whether it is scoped per customer), the upload-writing code (whether symlinks or directories can be created), the actual directory layout under `/srv/uploads`, the test files, and CI check status.

**Close-out (not yet written):** the author must adjudicate findings 1-5 per Step 7. I do not adjudicate my own findings.

**MERGE RECOMMENDATION: do not merge.** Reasons:
1. The required second High-tier round has not run.
2. No tests are in the diff.
3. Finding 1 (customer isolation) is unresolved and needs the callers.
4. No check status was provided.

The containment logic itself looks correct. Merge after finding 1 is resolved or rejected with evidence, finding 2 is fixed, and the second round is done. No written rule was supplied that settles the recommendation, so none is cited.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "inferred (callers and directory layout not provided)",
      "location": "uploads.py:9-10",
      "scenario": "Containment is to the whole UPLOAD_DIR, not the requesting customer. With nested names allowed, a user-controlled name such as 'custB/taxes/2025.pdf' reads another customer's upload unless the caller scopes it.",
      "fix": "Scope resolution to the caller's own directory (join under UPLOAD_DIR/<customer_id> and check containment against that), or confirm and test that callers enforce ownership."
    },
    {
      "severity": "P2",
      "evidence_level": "observed in the supplied files",
      "location": "PR.md / change.patch",
      "scenario": "PR claims tests added and passing, but the patch touches only uploads.py, so the claim is unsupported and the traversal, symlink and sibling-prefix cases are unproven.",
      "fix": "Add regression tests for ../, absolute paths, sibling-prefix dirs, symlinks out and within, empty name, and a valid nested name."
    },
    {
      "severity": "P3",
      "evidence_level": "reasoned from code",
      "location": "uploads.py:9-12",
      "scenario": "name='' or '.' resolves to UPLOAD_DIR, passes commonpath, and open() raises IsADirectoryError instead of ValueError.",
      "fix": "Reject path == UPLOAD_DIR, or require os.path.isfile(path), and raise ValueError."
    },
    {
      "severity": "P3",
      "evidence_level": "reasoned from code, not run",
      "location": "uploads.py:9-12",
      "scenario": "TOCTOU between realpath check and open lets a symlink swap redirect the read if an attacker can write under UPLOAD_DIR. A symlinked UPLOAD_DIR makes every read fail closed because the unresolved root is compared with a resolved path.",
      "fix": "Resolve UPLOAD_DIR with realpath before comparing; open with O_NOFOLLOW or dir_fd-based opens if symlink creation is possible."
    },
    {
      "severity": "P3",
      "evidence_level": "observed in the supplied files",
      "location": "uploads.py:8",
      "scenario": "Docstring does not say name is relative to the upload root, uses '/' separators, or which exceptions are raised.",
      "fix": "Document: name is a path relative to the upload directory using '/' for folders; raises ValueError if it resolves outside, FileNotFoundError if missing."
    }
  ]
}
```