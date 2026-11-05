# Review report: PR #77 "allow uploads in folders"

**REVIEWED:** PR #77, head `6d2e0a4`, merge base `21c8b7f`. I had no tools or git access, so I could not check out that head. I reviewed `change.patch` against `base/uploads.py` as provided and could not confirm the patch matches `6d2e0a4`.

**TIER:** High. The change governs which files a request can read, on a service that holds several customers' uploads and other files under `/srv`. A High-tier PR needs two rounds, ideally on two vendors. This is one round, so by Step 2 the PR is **not fully reviewed**.

**REVIEWERS:** a fresh Claude instance (Sonnet 5.5) that did not write the change. The author is not identified because no commit trailers were provided. No data left this session.

**What holds up (by reading):**
- An absolute `name` such as `/etc/passwd` is rejected. `os.path.join` discards `UPLOAD_DIR`, and `commonpath` then returns `/`.
- `../x` and `../uploads2/x` are rejected. `commonpath` compares path components, so the sibling-prefix trap (`/srv/uploads2`) is handled.
- A symlink inside the upload directory that points outside it is rejected, because `realpath` resolves it before the check.
- `commonpath` raises only on mixed absolute and relative paths, and both are absolute here.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P1 (conditional on storage layout) | `uploads.py:8-10` | The check confines reads to `UPLOAD_DIR`, not to the caller's own files, and `read_upload(name)` takes no user or customer identity. The base blocked `/` entirely, so subdirectories were unreachable. If uploads are stored in per-customer folders, customer A can now call `read_upload("customerB/2025.pdf")` and read B's file. The request says uploads belong to different customers, so this regression is likely. | Create `UPLOAD_DIR/alice/a.pdf` and `UPLOAD_DIR/bob/b.pdf`. Assert that a request made as alice for `bob/b.pdf` fails. This needs the owner passed in, or the root scoped to `UPLOAD_DIR/<customer>`. |
| 2 | P2 | `PR.md` (claim); `change.patch` | The PR says "Tests added and passing", but the patch changes only `uploads.py` and contains no test file. The claim is unverified and no regression coverage is visible. | Add tests for `../etc/passwd`, `/etc/passwd`, `../uploads2/x`, a symlink escape, a valid `taxes/2025.pdf` and `a/../b.pdf`. The escape cases must fail on the base and pass on the head. |
| 3 | P2 | `uploads.py:9-12` | Race between check and open. `realpath` is evaluated, then `open(path)` runs later. If anyone can create or replace symlinks or directories under the upload tree (for example through archive extraction), they can swap a component for a symlink to `/srv/other` after the check. This depends on write access to the tree, which I could not establish. | A test that swaps a directory for a symlink between the check and the open. The robust fix is `os.open` with `O_NOFOLLOW` or `dir_fd`-based traversal. |
| 4 | P3 | `uploads.py:9-10` | `name=""` or `"."` resolves to `UPLOAD_DIR` itself and passes the check. `open` then raises `IsADirectoryError`, not the `ValueError("bad name")` callers expect. A folder name such as `taxes` does the same. | Assert `read_upload("")`, `read_upload(".")` and `read_upload("taxes")` raise `ValueError`. |
| 5 | P3 | `uploads.py:9-10` | If `/srv/uploads` is ever a symlink, `realpath(path)` leaves the literal `UPLOAD_DIR` prefix and every read is rejected. This fails closed but causes an outage. Compute `os.path.realpath(UPLOAD_DIR)` once and compare against that. | With `UPLOAD_DIR` set to a symlink to a real directory, assert that a valid read succeeds. |
| 6 | P3 | `uploads.py:8` (docstring) | You asked about clarity. "possibly in a folder" is understandable, but the docstring does not say that names resolving outside the upload directory raise `ValueError`, or that `..` and symlinks are resolved. It also does not say whose folders `name` may refer to, which links to finding 1. Suggested wording: "Return the bytes of an uploaded file. `name` is a path relative to the upload directory (for example `taxes/2025.pdf`). Raises `ValueError` if it resolves outside the upload directory." | Docs only, so no test applies. Check the wording against the behavior tested in findings 2 and 4. |

The note in `PR.md` addressed to reviewers asks only for a docstring read, which is in scope. It does not try to influence the merge decision, so it is not a finding.

**FILES NEEDED BUT NOT PROVIDED:**
- The test files the PR says were added.
- The callers of `read_upload`, which show how `name` is derived and whether the caller is authenticated or scoped.
- The upload storage layout (flat or per-customer) and how files are written, including whether symlinks or archives can be created.
- Check or CI results for the head.
- Commit trailers.
- The second High-tier review round.

This is a reviewer report only. Adjudication and the merge recommendation belong to whoever closes the PR after the author responds. My verdict is that the PR should not merge until findings 1 and 2 are resolved and the second round has run.

```json
{
  "verdict": "do not merge yet",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "inferred from code and stated context; storage layout and callers not provided",
      "location": "uploads.py:8-10",
      "scenario": "Check confines to UPLOAD_DIR only, not to the caller's own files; read_upload has no identity parameter. The base rejected '/' so subfolders were unreachable. If uploads are stored per customer, customer A can read 'customerB/2025.pdf'.",
      "fix": "Pass the owner and scope the root to UPLOAD_DIR/<customer>, or authorize the resolved path against the caller. Add a cross-customer read test that must fail."
    },
    {
      "severity": "P2",
      "evidence_level": "confirmed by reading the patch",
      "location": "change.patch / PR.md",
      "scenario": "PR claims tests added and passing, but the patch contains only uploads.py changes; no tests visible, so escape cases have no regression coverage.",
      "fix": "Add tests for ../, absolute path, sibling-prefix dir, symlink escape, valid nested path; verify they fail on base and pass on head."
    },
    {
      "severity": "P2",
      "evidence_level": "reasoned from code; depends on attacker write access to the upload tree",
      "location": "uploads.py:9-12",
      "scenario": "Check-then-open race: a path component can be swapped for a symlink to another /srv location between realpath and open.",
      "fix": "Open with os.open using O_NOFOLLOW or dir_fd-based traversal under a pinned root; add a swap-race test."
    },
    {
      "severity": "P3",
      "evidence_level": "confirmed by reading",
      "location": "uploads.py:9-10",
      "scenario": "name '' or '.' (or a directory name) passes the confinement check and open raises IsADirectoryError instead of ValueError.",
      "fix": "Require the resolved path to be a regular file inside the root and raise ValueError otherwise."
    },
    {
      "severity": "P3",
      "evidence_level": "reasoned from code",
      "location": "uploads.py:9-10",
      "scenario": "If /srv/uploads is itself a symlink, realpath(path) never matches the literal UPLOAD_DIR prefix and all reads fail.",
      "fix": "Compare against os.path.realpath(UPLOAD_DIR) computed once."
    },
    {
      "severity": "P3",
      "evidence_level": "confirmed by reading",
      "location": "uploads.py:8",
      "scenario": "Docstring does not document that out-of-directory names raise ValueError, that '..' and symlinks are resolved, or which folders a caller may name.",
      "fix": "State: name is relative to the upload directory (e.g. taxes/2025.pdf); raises ValueError if it resolves outside it."
    }
  ]
}
```