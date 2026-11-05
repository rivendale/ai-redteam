# PR #77 review report: allow uploads in folders

**REVIEWED:** PR #77, head `6d2e0a4`, merge base `21c8b7f`. Both SHAs come from PR.md. I could not verify them or check out the head, because I have no tools and only the supplied files. Line numbers are my count of the patched `uploads.py`.

**TIER: High.** `read_upload` is a file-access boundary. The uploads belong to different customers, and `/srv` holds other files the service can read. Only one round has run (this one), so under Step 2 this PR is **not yet reviewed**. A second round, ideally on a different vendor, is still required.

**REVIEWERS:** This session (Sonnet 5.5, single round, no tools), with no memory of writing the change. Authorship is unknown because no commit trailers were supplied. Step 3: the supplied code carries no customer data, so there is no data-routing constraint on this round. The second round should run only on an approved endpoint.

**Handling of PR text:** The PR asks reviewers to look at the docstring wording. That falls within normal review of the diff and does not try to steer the merge decision, so I treated it as a P3 finding (#6) and not as an instruction.

## What holds up (read from the code)
- **Absolute names:** `os.path.join(UPLOAD_DIR, "/etc/passwd")` gives `/etc/passwd`. `realpath` and `commonpath` then reject it.
- **Sibling-prefix directories:** `/srv/uploads-evil/x` is rejected, because `commonpath` is used and not `startswith`.
- **`..` escapes:** these are rejected after normalization.
- **Symlinks that already exist:** `realpath` resolves them before the check, so a link pointing out of the directory is rejected.

## FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P1 (evidence: inferred; callers not provided) | `uploads.py:7-13` | The only check is containment in the shared `UPLOAD_DIR`, and `read_upload` takes no user or tenant argument. Before, flat names forced a single namespace. Now `read_upload("customerB/taxes/2025.pdf")` or `"mine/../customerB/taxes/2025.pdf"` passes the guard whenever customer data sits in subfolders of one directory. Any caller that passes user input straight through exposes other customers' files. If an upstream layer already prefixes or authorizes names per customer, this is mitigated, but I could not see it. | With files at `UPLOAD_DIR/a/x.pdf` and `UPLOAD_DIR/b/x.pdf`, a read scoped to customer `a` of `b/x.pdf` and of `a/../b/x.pdf` must fail. This needs a per-customer root parameter or an enforced prefix. |
| 2 | P2 (verified by reading) | `uploads.py:9-12` | Time-of-check/time-of-use race. `realpath` runs at line 9, but `open(path)` at line 12 follows symlinks again. If anyone can create or replace entries under the upload tree (archive extraction, a sync tool, another process), they can swap a checked regular file for a symlink to `/srv/<other>` between the check and the open. | Concurrency test: a thread flips `uploads/x` between a file and a symlink to an outside file while `read_upload("x")` loops. It must never return outside bytes. The fix is `os.open` with `dir_fd` and `O_NOFOLLOW` per component, or opening first and verifying the fd's real path. |
| 3 | P2 (verified: the patch touches only `uploads.py`) | `change.patch` | The PR says "Tests added and passing", but no test file is in the patch. The claim is unverified. Nothing shows that absolute paths, symlinks, `..`, or a sibling-prefix directory such as `/srv/uploads-evil` are exercised. | Add a test file covering: `taxes/2025.pdf` succeeds; `../x`, `/etc/passwd`, `a/../../x`, a symlink out of the tree, and `uploads-evil/x` each raise `ValueError`. |
| 4 | P3 (verified by reading) | `uploads.py:10` | If `/srv/uploads` is itself a symlink or has a symlinked parent, `realpath(path)` is under the target while `UPLOAD_DIR` is not. Every read is rejected, which fails closed but is an outage on such hosts. | With `UPLOAD_DIR` patched to a symlink to a real directory, `read_upload("a.pdf")` should succeed. The fix is `realpath(UPLOAD_DIR)` in the comparison. |
| 5 | P3 (verified by reading) | `uploads.py:9-12` | `name=""` or `"."` resolves to `UPLOAD_DIR`, which passes the guard. `open` then raises `IsADirectoryError` and not `ValueError`. Callers that catch only `ValueError` for bad names get an unhandled exception, and the error text discloses that the path exists. | `read_upload("")`, `read_upload(".")` and `read_upload("taxes")` (a directory) must raise `ValueError`. |
| 6 | P3 (verified by reading) | `uploads.py:8` | Docstring wording, as the author requested. "Possibly in a folder" is vague. It does not say that `/` is the separator, that names are relative to the upload root, that `..` is allowed only when it stays inside the root, that symlinks are resolved, or that `ValueError` is raised for anything outside. | None needed. Suggested wording: "Return the bytes of an uploaded file. `name` is a path relative to the upload root, using `/` to separate folders (e.g. `taxes/2025.pdf`). Raises `ValueError` if the resolved path is outside the upload root." |

## FILES NEEDED BUT NOT PROVIDED
- The test files the PR claims were added.
- Callers of `read_upload`, and any per-customer authorization or naming layer, which decide whether #1 is real.
- How files and symlinks get into the upload tree, which decides whether #2 is exploitable.
- Check results (CI), and the commit trailers for authorship.

## Status
The path-escape guard itself is sound for static layouts. The PR is not ready to merge, for these reasons:
- The required second High-tier round has not run.
- The claimed tests are not visible.
- Finding #1 needs an answer about customer isolation before this change can ship.

Under Step 7, the author adjudicates the findings and the close-out is written by whoever closes the PR. I have not adjudicated them.

```json
{
  "verdict": "do_not_merge_yet",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "inferred",
      "location": "uploads.py:7-13",
      "scenario": "Containment is checked only against the shared UPLOAD_DIR and read_upload has no tenant argument. With subfolders now allowed, read_upload('customerB/taxes/2025.pdf') or 'mine/../customerB/taxes/2025.pdf' passes the guard, so one customer can read another's files unless an unseen upstream layer enforces per-customer prefixes.",
      "fix": "Pass a per-customer root or enforced prefix into read_upload and check containment against that root; add cross-tenant read tests including '..' hops."
    },
    {
      "severity": "P2",
      "evidence_level": "verified_by_reading",
      "location": "uploads.py:9-12",
      "scenario": "TOCTOU: realpath is computed at line 9 but open() at line 12 follows symlinks again. Anyone who can swap a path component for a symlink between the two calls can read files outside the upload tree.",
      "fix": "Open with os.open using dir_fd and O_NOFOLLOW per component, or open first and verify the fd's real path; add a concurrent symlink-swap test."
    },
    {
      "severity": "P2",
      "evidence_level": "verified_by_reading",
      "location": "change.patch",
      "scenario": "PR claims tests were added and pass, but the patch modifies only uploads.py. No coverage of absolute paths, '..', symlinks, or sibling-prefix directories is visible.",
      "fix": "Add tests: valid nested path succeeds; '../x', '/etc/passwd', 'a/../../x', outbound symlink, and '/srv/uploads-evil/x' all raise ValueError."
    },
    {
      "severity": "P3",
      "evidence_level": "verified_by_reading",
      "location": "uploads.py:10",
      "scenario": "If UPLOAD_DIR is or sits under a symlink, realpath(path) never matches the unresolved UPLOAD_DIR in commonpath, so every read is rejected (fail closed, but an outage).",
      "fix": "Compare against os.path.realpath(UPLOAD_DIR); test with UPLOAD_DIR patched to a symlink."
    },
    {
      "severity": "P3",
      "evidence_level": "verified_by_reading",
      "location": "uploads.py:9-12",
      "scenario": "name '' or '.' (or an existing directory name) resolves to UPLOAD_DIR, passes the guard, and open raises IsADirectoryError instead of ValueError, so callers catching only ValueError crash and the error discloses the path exists.",
      "fix": "Reject paths equal to the root or non-regular files with ValueError; test '', '.', and a directory name."
    },
    {
      "severity": "P3",
      "evidence_level": "verified_by_reading",
      "location": "uploads.py:8",
      "scenario": "Docstring says 'possibly in a folder' without stating that names are relative to the upload root, '/' separates folders, symlinks are resolved, or that ValueError is raised for paths outside the root.",
      "fix": "Reword: 'Return the bytes of an uploaded file. name is a path relative to the upload root, using / between folders (e.g. taxes/2025.pdf). Raises ValueError if the resolved path is outside the upload root.'"
    }
  ]
}
```