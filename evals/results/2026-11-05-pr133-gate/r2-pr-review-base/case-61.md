# PR #77 review report

**REVIEWED:** PR #77 "allow uploads in folders", head `6d2e0a4`, merge base `21c8b7f`. Both SHAs come from PR.md. This session is not a git repository, so I could not confirm them. I read only `change.patch` and `base/`.

**TIER:** High. The change is a path-confinement control on files that belong to different customers, with other readable files under `/srv`. Reading permissions is the High tier in Step 2.

**REVIEWERS:** One fresh instance (Sonnet 5.5) with no part in writing the change. Authorship is unknown because no commit trailers were provided. **Only one round has run, and High requires two, ideally on different vendors.** By the skill's own rule this PR is not yet reviewed. No code left the session, so Step 3 is satisfied.

## What holds up

I traced these inputs through the new `read_upload`:
- `../../etc/passwd` resolves outside `UPLOAD_DIR` and is rejected.
- `/etc/passwd` makes `os.path.join` discard `UPLOAD_DIR`, then fails `commonpath` and is rejected.
- A sibling like `/srv/uploads-evil/x` is correctly rejected, because `commonpath` compares by path component and not by string prefix.
- A symlink inside the directory that points outside is resolved by `realpath` and rejected.

## FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P1 | `uploads.py:8-9` (patched `read_upload`) | The check confines reads to the global `UPLOAD_DIR`, not to the requesting customer. `read_upload(name)` takes no identity. If uploads are laid out as `<customer>/...`, any caller who can supply a name can pass `other_customer/taxes/2025.pdf` and read it. Folders make these names structured and guessable. The base had the same flat-namespace property, but the PR's stated stakes include cross-customer isolation. Whether callers enforce ownership is **UNVERIFIED** because they were not provided. | Create `UPLOAD_DIR/a/x.pdf` and `UPLOAD_DIR/b/y.pdf`. Reading `b/y.pdf` as customer `a` must raise. This needs a per-customer root or an ownership check in the caller. |
| 2 | P1 | PR.md, "Tests added and passing" | `change.patch` touches only `uploads.py`. It contains no tests, so the claim is unsupported by the artifact. I could not run anything. | Add tests for `../x`, `/etc/passwd`, `a/../../x`, a symlink escaping the directory, a `uploads-evil` sibling, and a valid `taxes/2025.pdf`. |
| 3 | P2 | `uploads.py:9,12` | Time-of-check/time-of-use gap: `realpath` is checked, then `open(path)` follows the filesystem again. If a symlink can be created or swapped under `UPLOAD_DIR` between the two calls, the open can land outside it. Exploitability depends on how uploads are written, and the writer was not provided. | Race test that swaps a directory for a symlink to `/srv/other` between the check and the open. The fix is to open with `O_NOFOLLOW` or `dir_fd`, or to re-verify with `fstat` after opening. |
| 4 | P3 | `uploads.py:9` | `UPLOAD_DIR` itself is not passed through `realpath`. If `/srv` or `/srv/uploads` is a symlink, every resolved path has a different prefix and every read fails with `bad name`. It fails closed, so this is an availability problem only. | Point `UPLOAD_DIR` at a symlink to a real directory. Reading a valid file must succeed. Compare against `realpath(UPLOAD_DIR)`. |
| 5 | P3 | `uploads.py:9-10` | `name` of `""`, `"."` or `"taxes"` (a directory) resolves to a path that passes the check. `open` then raises `IsADirectoryError` and not the documented `ValueError`. Callers that catch only `ValueError` will surface a 500. | `read_upload("")` and `read_upload("taxes")` must raise `ValueError`. |
| 6 | P3 | `uploads.py:6` (docstring, as the author asked) | "possibly in a folder" does not say that the path is relative to the upload root, that `/` is the separator, that absolute and escaping paths are rejected, that symlinks are resolved, or which exception is raised. Suggested text: `Return the bytes of an uploaded file. name is a path relative to the upload directory, using "/" between folders (e.g. "taxes/2025.pdf"). Raises ValueError if name resolves outside the upload directory, including via "..", an absolute path or a symlink.` | Not applicable (docs). Evidence is the rewritten docstring matching the enforced behavior. |

**FILES NEEDED BUT NOT PROVIDED:** the callers of `read_upload`, including any authorization and ownership checks. Also the upload-writing code (naming, symlink handling, directory layout) and the claimed test files. The deployment's actual `UPLOAD_DIR` path and filesystem layout are also needed.

## Close-out

Not written. The author has not yet adjudicated these findings, and a reviewer does not adjudicate its own findings.

**MERGE RECOMMENDATION (provisional): do not merge.**
- The second High-tier round has not run.
- No tests are present in the patch (#2).
- The cross-customer question (#1) needs the callers and an owner decision.
- Findings #1 and #2 are P1 and cannot be deferred.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "inferred; callers not provided",
      "location": "uploads.py:8-9",
      "scenario": "Confinement is to the global UPLOAD_DIR only; read_upload has no customer identity. A caller can request 'other_customer/taxes/2025.pdf' and read another customer's upload unless callers enforce ownership.",
      "fix": "Scope reads to a per-customer root (or pass customer id and verify ownership) and add a cross-customer negative test."
    },
    {
      "severity": "P1",
      "evidence_level": "confirmed from patch contents",
      "location": "PR.md 'Tests added and passing'",
      "scenario": "change.patch modifies only uploads.py; no tests are included, so the claim is unsupported and the traversal guard has no regression coverage.",
      "fix": "Add tests for '..', absolute paths, escaping symlinks, sibling-prefix directories and a valid nested name."
    },
    {
      "severity": "P2",
      "evidence_level": "inferred from code; writer not provided",
      "location": "uploads.py:9,12",
      "scenario": "realpath check and open() are separate steps; a symlink swapped in between could redirect the open outside UPLOAD_DIR if an attacker can create links in the upload tree.",
      "fix": "Open with O_NOFOLLOW/dir_fd or re-verify with fstat after open."
    },
    {
      "severity": "P3",
      "evidence_level": "confirmed by reading",
      "location": "uploads.py:9",
      "scenario": "UPLOAD_DIR is not realpath'd; if it is or sits under a symlink, all reads are rejected as 'bad name'.",
      "fix": "Compare against os.path.realpath(UPLOAD_DIR)."
    },
    {
      "severity": "P3",
      "evidence_level": "confirmed by reading",
      "location": "uploads.py:9-10",
      "scenario": "name '', '.' or a directory passes the check and open() raises IsADirectoryError instead of ValueError.",
      "fix": "Reject paths equal to the root or that are not regular files, raising ValueError."
    },
    {
      "severity": "P3",
      "evidence_level": "confirmed by reading",
      "location": "uploads.py:6",
      "scenario": "Docstring does not state relative-to-root semantics, '/' separator, rejection of absolute/escaping/symlink paths, or the ValueError contract.",
      "fix": "Use the rewritten docstring proposed in the report."
    }
  ]
}
```