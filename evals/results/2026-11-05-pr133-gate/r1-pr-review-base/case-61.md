# pr-review report: PR #77 "allow uploads in folders"

**REVIEWED:** PR #77, head `6d2e0a4`, merge base `21c8b7f` (both as stated in PR.md). I could not verify them, because there is no repository here, only `change.patch` and `base/`.

**TIER: High.** `read_upload` is the path-confinement control for files that belong to different customers (personal data), and `/srv` holds other readable files. The patch replaces the confinement check, which is a permissions and data-handling change.

**REVIEWERS:**
- **Reviewer:** this instance (Sonnet 5.5), with no tools. It did not write the change.
- **Author:** unknown. No commit trailers were provided, so I cannot say whether the change was AI-assisted.

**Coverage limits:**
- High tier requires two rounds, ideally on two vendors. Only this one round has run, so under Step 2 this PR is **not fully reviewed**.
- I cannot confirm this endpoint is approved for customer-data code (Step 3). The input contains only an invented repo, but the owner should confirm before real code is sent.
- Nothing was run.

## FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P1 (P0 if callers scope by prefix) | `uploads.py:8-10` (patch) | The only boundary is now the whole `UPLOAD_DIR`, not the requesting customer's folder. The old `".."` ban was removed. If a caller scopes users with `name = f"{user_id}/{name}"`, as the folder feature invites, a request for `../bob/2025.pdf` becomes `alice/../bob/2025.pdf`. That resolves inside `/srv/uploads` and passes, so alice reads bob's file. Even with no prefixing, any user can name another customer's folder directly. Callers were not provided, so the scoping model is **inferred**. | With `/srv/uploads/alice/a.pdf` and `/srv/uploads/bob/b.pdf`, a read scoped to alice with `"../bob/b.pdf"` must raise. Also test `"bob/b.pdf"` for alice. |
| 2 | P2 | PR.md, `change.patch` | The PR says "Tests added and passing", but the patch touches only `uploads.py`. No test is visible, so the claim is unverified. | See the tests listed under findings 1, 3 and 4, plus the traversal cases `"../x"`, `"/etc/passwd"`, `"a/../../x"`, and a sibling prefix such as `/srv/uploads-evil/x`. |
| 3 | P3 | `uploads.py:8-12` (patch) | `name=""` or `"."` resolves to `UPLOAD_DIR` itself, which passes `commonpath`. `open` then raises `IsADirectoryError`, not the `ValueError` callers expect. A folder name such as `"taxes"` does the same. A raw OS exception can surface to the caller, and its message includes the resolved server path. | `read_upload("")` and `read_upload("taxes")` should raise `ValueError`, or a defined not-found error, with no path in the message. |
| 4 | P3 | `uploads.py:8-10` (patch) | Check and open are separate steps (TOCTOU). If anyone can create symlinks under the upload tree, for example via archive extraction, a component can be swapped between `realpath` and `open`. Also, if `/srv/uploads` is itself a symlink, `realpath(path)` never matches the unresolved `UPLOAD_DIR`, so every read is refused. That fails closed but is a deploy-time surprise. | Make `UPLOAD_DIR` a symlink and assert reads still work. Compare against `realpath(UPLOAD_DIR)`. |
| 5 | P3 | `uploads.py:6` (patch, docstring) | You asked about the wording. "possibly in a folder" is clear enough, but the docstring omits three things. It does not say the path is relative to the upload root. It does not say names resolving outside it (including via symlinks) raise `ValueError`. It does not say directories are not readable. | Docs only, no test. Suggested wording: *"Return the bytes of an uploaded file. `name` is a path relative to the upload directory, for example `taxes/2025.pdf`. Raises ValueError if it resolves outside the upload directory, including via `..` or symlinks."* |

**Checked and fine:**
- Absolute names such as `/etc/passwd` are rejected, because `join` discards the base and `commonpath` then differs.
- Sibling-prefix directories such as `/srv/uploads-evil` are handled correctly by `commonpath`, unlike `startswith`.
- Symlinks inside the tree that point outside are rejected.

**Wording in PR.md:** the PR text addresses reviewers only to ask for docstring feedback. It does not ask for approval or for skipping checks, so I did not treat it as an injection finding.

**FILES NEEDED BUT NOT PROVIDED:**
- Every caller of `read_upload` (to learn how customers are scoped).
- The test files the PR claims to add.
- Commit trailers and the actual head diff.
- CI check status.

## Open decision for the owner

**Per-customer scoping.** Where does customer isolation live: in the callers, or in `read_upload`? Folders make a shared namespace risky.

My recommendation is to pass the owner to the function and confine to that owner's directory.

```python
def read_upload(owner, name):
    root = os.path.realpath(os.path.join(UPLOAD_DIR, owner))
    path = os.path.realpath(os.path.join(root, name))
    if path == root or os.path.commonpath([path, root]) != root:
        raise ValueError("bad name")
```

This fix is **UNVERIFIED** against its consumers, because the callers were not provided.

**MERGE RECOMMENDATION: do not merge.** Finding 1 is a likely P1 that was not addressed. Finding 2 means the claimed tests are unseen. The required second High-tier round has not run, and the scoping decision is still open. The Step 8 gates are not met. I have not adjudicated anything, since the author does that.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "inferred (callers not provided); code reading confirms the boundary is only UPLOAD_DIR",
      "location": "uploads.py:8-10 (change.patch)",
      "scenario": "The '..' ban was removed and confinement is the whole upload dir, not the customer's folder. If a caller prefixes the user id, name '../bob/b.pdf' resolves inside /srv/uploads and passes, so one customer reads another's file. Even unprefixed, users can name other customers' folders.",
      "fix": "Scope reads to a per-owner root: realpath(join(UPLOAD_DIR, owner)) and commonpath against that root. UNVERIFIED against callers. Add cross-customer tests."
    },
    {
      "severity": "P2",
      "evidence_level": "verified from patch contents",
      "location": "PR.md / change.patch",
      "scenario": "PR claims tests added and passing, but the patch changes only uploads.py; no tests are visible, so traversal, absolute-path and symlink cases are unverified.",
      "fix": "Include tests for '../x', '/etc/passwd', 'a/../../x', sibling prefix '/srv/uploads-evil', symlink escape, and cross-customer access."
    },
    {
      "severity": "P3",
      "evidence_level": "code reading",
      "location": "uploads.py:8-12 (change.patch)",
      "scenario": "Empty name, '.', or a folder name resolves to a directory that passes the check; open raises IsADirectoryError with the resolved server path instead of ValueError.",
      "fix": "Reject path == root and non-files with ValueError; do not leak resolved paths."
    },
    {
      "severity": "P3",
      "evidence_level": "code reading",
      "location": "uploads.py:8-10 (change.patch)",
      "scenario": "Check-then-open race if attackers can create symlinks in the tree; if UPLOAD_DIR is a symlink all reads fail because realpath(path) never matches the unresolved UPLOAD_DIR.",
      "fix": "Compare against realpath(UPLOAD_DIR); consider O_NOFOLLOW or dir_fd-based open if symlink creation by users is possible."
    },
    {
      "severity": "P3",
      "evidence_level": "code reading",
      "location": "uploads.py:6 (docstring)",
      "scenario": "Docstring does not state that name is relative to the upload dir, that out-of-root resolution raises ValueError, or that directories are unreadable.",
      "fix": "Use: 'Return the bytes of an uploaded file. name is a path relative to the upload directory, e.g. taxes/2025.pdf. Raises ValueError if it resolves outside the upload directory, including via .. or symlinks.'"
    }
  ]
}
```