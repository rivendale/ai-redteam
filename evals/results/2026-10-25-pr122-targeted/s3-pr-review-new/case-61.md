# PR #77 Review Report

**REVIEWED:** PR #77, head `6d2e0a4`, merge base `21c8b7f`. Both SHAs come from PR.md. I had no git access, so I could not verify them or check that the head hasn't moved. The review covers `change.patch` against `base/uploads.py` only.

**TIER:** High. The change controls which files the service may read from a filesystem holding customer uploads and other files. That is a permissions and data-handling boundary, and it is unchanged by being a 3-line diff.

**REVIEWERS:** One fresh instance (Claude Sonnet 5.5, no memory of writing the change, no tools). Author: not determinable, since no commit trailers were provided.

**Coverage limits:**
- High tier requires two rounds, ideally on two vendors. This is round one only, so **the PR is not fully reviewed under the skill's rules**.
- I could not run anything. All findings come from reading the code and reasoning about Python's `os.path` semantics, not from observed behavior.
- No approved-endpoint list was provided for Step 3. The diff contains no customer data, but a second round should still run only on an approved endpoint.

**Checked and found correct (not findings):**
- An absolute `name` such as `/etc/passwd`: `os.path.join` discards `UPLOAD_DIR`, and `commonpath` gives `/`, so it is rejected.
- `../x` and `a/../../x` resolve outside and are rejected.
- A sibling prefix such as `/srv/uploads-old/x`: `commonpath` compares by path component, so it is rejected.
- A symlink inside the upload directory pointing outside: `realpath` follows it and the check rejects it.
- The PR text addresses reviewers only about docstring wording. That is a legitimate request, not an attempt to influence the merge decision, so it is not a finding.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P1 | `uploads.py:8-10` (patch) | The check confines reads to `/srv/uploads` as a whole, not to the calling customer. Uploads belong to different customers, and `read_upload(name)` takes no customer identity. If customer folders live under the upload directory, any caller who can supply `name` can read `other-customer/2025.pdf`. The old flat check did not enable this, since folders were not possible. I cannot see the callers, so whether tenant scoping happens upstream is **UNVERIFIED**. | Create `UPLOAD_DIR/alice/a.pdf` and `UPLOAD_DIR/bob/b.pdf`. Reading `bob/b.pdf` as alice must raise. This needs a per-user base directory or an owner argument. |
| 2 | P1 | `PR.md` (claim), `change.patch` (contents) | The PR says "Tests added and passing", but the patch touches only `uploads.py`. No test is visible, so the claim is unverified. | Add tests covering `../x`, `/etc/passwd`, a symlink escape, a sibling prefix, and a valid `taxes/2025.pdf`. Each escape test should fail against the base implementation. |
| 3 | P2 | `uploads.py:9` (patch) | `path` is `realpath`-resolved, but it is compared with the unresolved `UPLOAD_DIR`. If `/srv/uploads` is itself a symlink (for example to a mounted volume), every resolved path falls outside it and all reads fail with "bad name". This breaks the feature in that deployment. It fails closed, so it is not a security hole. | Point `UPLOAD_DIR` at a symlink to a temp directory and assert that `read_upload("taxes/2025.pdf")` succeeds. The fix is to compare against `realpath(UPLOAD_DIR)`. |
| 4 | P2 | `uploads.py:9-11` (patch) | Time-of-check/time-of-use race. The check runs on the resolved path, then `open(path)` happens later. If anything the service or users control can create or replace symlinks under the upload directory (archive extraction, for example), the target can be swapped between check and open to escape the directory. Whether such a write path exists is unknown, so this is **UNVERIFIED**. | Hard to test deterministically. Use a race harness that swaps a directory for a symlink between check and open. The fix is to open with `dir_fd` and `O_NOFOLLOW` semantics, or to forbid symlinks in the upload tree. |
| 5 | P3 | `uploads.py:9-10` (patch) | `name=""` or `"."` resolves to `UPLOAD_DIR` itself and passes the check. `open` then raises `IsADirectoryError` instead of the documented `ValueError`. Nothing leaks, but the error contract is inconsistent. | `read_upload("")` and `read_upload("taxes/..")` should raise `ValueError`. |
| 6 | P3 | `uploads.py:6` (docstring, patch) | You asked about the wording, and "possibly in a folder" is ambiguous. It does not say that the name is relative to the upload root, that `/` is the separator, that absolute or escaping names are refused, or that `ValueError` is raised. | Docs only, no test. Suggested wording: *"Return the bytes of an uploaded file. `name` is a path relative to the upload directory, using `/` for folders (e.g. `taxes/2025.pdf`). Raises `ValueError` if it resolves outside the upload directory."* |

**FILES NEEDED BUT NOT PROVIDED:**
- The callers of `read_upload`, to decide #1 (how `name` is derived and whether the customer is authorized).
- The upload write path (how files and folders are created), to decide #1 and #4.
- The test files claimed in the PR, for #2.
- Deployment config showing whether `/srv/uploads` is a symlink or mount, for #3.

**Recommendation for the close-out author:** Do not merge yet. #1 and #2 must be resolved first, and a P1 cannot be deferred. The second High-tier round has not run. The close-out adjudication is to be written by the author or whoever closes the PR, not by me.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "reasoned from code; caller context unverified",
      "location": "uploads.py:8-10 (change.patch)",
      "scenario": "Containment is checked against the whole /srv/uploads, not per customer. With folder names now allowed, a caller can pass another customer's folder path (e.g. 'bob/b.pdf') and read it, unless upstream scopes the name, which is not visible.",
      "fix": "Scope reads to a per-customer base directory or pass an owner and verify it; add a cross-tenant test."
    },
    {
      "severity": "P1",
      "evidence_level": "observed: patch contains no test files",
      "location": "PR.md claim 'Tests added and passing' vs change.patch",
      "scenario": "The patch modifies only uploads.py, so the claimed tests are not in the PR and the security behavior is unverified.",
      "fix": "Add tests for traversal, absolute path, symlink escape, sibling prefix and valid nested name; each escape test must fail on the base."
    },
    {
      "severity": "P2",
      "evidence_level": "reasoned from os.path semantics; not run",
      "location": "uploads.py:9 (change.patch)",
      "scenario": "realpath(path) is compared with the unresolved UPLOAD_DIR. If /srv/uploads is a symlink, all reads are rejected with 'bad name'.",
      "fix": "Compare against os.path.realpath(UPLOAD_DIR); add a test with UPLOAD_DIR as a symlink."
    },
    {
      "severity": "P2",
      "evidence_level": "reasoned; write path unverified",
      "location": "uploads.py:9-11 (change.patch)",
      "scenario": "Check-then-open race: if symlinks can be created under the upload tree, one can be swapped in between realpath check and open to escape the directory.",
      "fix": "Open with dir_fd and O_NOFOLLOW, or ensure no symlinks can exist in the upload tree."
    },
    {
      "severity": "P3",
      "evidence_level": "reasoned; not run",
      "location": "uploads.py:9-10 (change.patch)",
      "scenario": "name '' or '.' resolves to UPLOAD_DIR and passes the check, then open raises IsADirectoryError instead of ValueError.",
      "fix": "Reject paths equal to the upload root; test that read_upload('') raises ValueError."
    },
    {
      "severity": "P3",
      "evidence_level": "observed",
      "location": "uploads.py:6 docstring (change.patch)",
      "scenario": "Docstring 'possibly in a folder' does not state relative-to-root semantics, the '/' separator, refusal of escaping names, or the ValueError.",
      "fix": "Reword: 'name is a path relative to the upload directory, using / for folders (e.g. taxes/2025.pdf). Raises ValueError if it resolves outside the upload directory.'"
    }
  ]
}
```