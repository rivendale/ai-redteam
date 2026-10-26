# PR #77 review: allow uploads in folders

**Review report**

**REVIEWED:** PR #77, head `6d2e0a4`, merge base `21c8b7f`. Both SHAs come from PR.md and could not be checked independently, because there is no git repository and no tools in this session. I reviewed the supplied `change.patch` applied to `work/base/uploads.py`, read statically. I created no worktree and ran no code. If the real head differs from what the patch shows, this review does not cover the difference.

**TIER: High.** The change rewrites the check that keeps file reads inside `/srv/uploads`. According to context.md, that directory holds files belonging to different customers, and `/srv` holds other files the service can read. This is a data-access boundary on customer data, so it is High tier.
- High tier requires two review rounds, ideally from two vendors. **This is round 1 of 2.** The PR is not reviewed until round 2 has run.
- **Data handling (Step 3):** no code left this session. Round 2 must run on an endpoint approved for customer-data-adjacent code.

**REVIEWERS:**
- Round 1: this instance, claude-opus-5-5. It had no part in writing the change.
- Author: unknown. No commit trailers were provided, so authorship could not be read.

**What the new check gets right** (traced by hand against `uploads.py:9-11` after the patch):
- `../x` resolves to `/srv/x`. Their common path is `/srv`, so it is rejected.
- An absolute name such as `/etc/passwd` makes `join` drop `UPLOAD_DIR`. The path is then outside the directory and is rejected.
- `../uploads-evil/x` is rejected. `commonpath` compares whole path components, so it avoids the `startswith` prefix bug.
- A symlink inside the upload directory that points outside it is resolved by `realpath` and rejected.

The core traversal fix works as intended. The findings below concern what it leaves out.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P1 | `change.patch` (no test file); PR.md "Tests added and passing" | The PR says tests were added, but the diff contains no test file. The new path-containment check is the only barrier between user input and `/srv`, and nothing in the PR exercises it. A later edit, for example changing `commonpath` back to `startswith`, or removing `realpath`, would reopen traversal and no test would catch it. | Parametrized `test_read_upload_rejects`: `../x`, `a/../../x`, `/etc/passwd`, `../uploads-evil/x`, and a symlink `uploads/link -> /srv/secret`. Each must raise `ValueError`. Add `test_read_upload_folder` for `taxes/2025.pdf`, which must return its bytes. Today the PR ships no such test. |
| 2 | P2 | `uploads.py:10` | `path` is resolved with `realpath`, but `UPLOAD_DIR` is compared as a literal string. If `/srv/uploads` is a symlink in production (for example to `/data/uploads`), every valid path resolves under `/data/uploads`. `commonpath` then never equals `/srv/uploads`, so **every** read raises `ValueError`. That is an outage on deploy. | Point `UPLOAD_DIR` at a symlink to a temporary directory, create `f.txt` in it, and assert that `read_upload("f.txt")` returns its bytes. This fails today. Fix: compare against `os.path.realpath(UPLOAD_DIR)`, computed once. |
| 3 | P3 | `uploads.py:9-12` | There is a check-then-use race. `realpath` resolves at one moment, and `open(path)` follows symlinks again later. If something that writes to the upload tree can swap a directory component for a symlink between those two calls, the open escapes the directory. Whether an attacker can create symlinks there depends on the upload-writing code, which was not provided. This is hardening, not a confirmed exploit. | Monkeypatch `os.path.realpath` so that, after it returns, it replaces `uploads/dir` with a symlink to an outside directory. Assert that the read raises. This fails today. Fix: open each component with `dir_fd` and `O_NOFOLLOW`, or check `os.fstat` on the opened file against the directory's device and inode. |
| 4 | P3 | `uploads.py:9-12` | `name` values of `""`, `"."` or `"taxes/"` resolve to `UPLOAD_DIR` itself or to a subfolder. They pass the containment check and then fail with `IsADirectoryError` instead of the documented `ValueError("bad name")`. If callers map only `ValueError` to a 4xx response, this produces a 500. | `pytest.raises(ValueError)` for `""` and `"."`. Today these raise `IsADirectoryError`. |

**Open owner/architecture question (not a finding; no code location supports a concrete flaw yet):** the original request says *users* keep uploads in folders, and context.md says uploads belong to different customers. `read_upload(name)` takes no user or tenant identity, and the base version had none either.
- If the caller is supposed to scope `name` to the requesting customer, a user may now be able to name another customer's folder.
- I could not check this, because the callers were not provided.
- Before merge, the owner needs to confirm where per-customer scoping is enforced.

**On the docstring (the author's request, which is a benign question and not a reviewer-directed instruction):** "possibly in a folder" is understandable but vague. A suggested wording is "a path relative to the upload directory, which may include folders (e.g. `taxes/2025.pdf`); names that resolve outside it raise `ValueError`."

**FILES NEEDED BUT NOT PROVIDED:**
- The tests the PR says were added.
- Callers of `read_upload`, including the HTTP handler and any auth or tenant scoping.
- The code that writes uploads, to see whether users can create symlinks or chosen folder names.
- Deployment config for `/srv/uploads`: whether it is a symlink, a mount, and its permissions.
- CI check results.
- Commit trailers.

---

**Close-out**

Pending. The author adjudicates these findings, and a reviewer never adjudicates its own.

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | Pending (P1, cannot be deferred) | none |
| 2 | Pending | none |
| 3 | Pending | none |
| 4 | Pending | none |

**VERIFIED AFTER FIXES:** nothing yet. Each fix needs a targeted read of its diff, plus a regression test that fails without the fix.

**MERGE RECOMMENDATION: do not merge.** The reasons:
- The second High-tier round has not run.
- P1 #1 is open: the tests the PR claims are missing.
- CI checks were not provided, and a missing check is not a green check.
- The owner decision on per-customer scoping is pending.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "confirmed from diff",
      "location": "change.patch (no test file); PR.md claim 'Tests added and passing'",
      "scenario": "The PR claims tests, but the diff adds none. The traversal check on the customer-data boundary is untested, so a regression (e.g. commonpath->startswith, or dropping realpath) would reopen /srv access unnoticed.",
      "fix": "Add parametrized rejection tests (../x, a/../../x, /etc/passwd, ../uploads-evil/x, an outward symlink) and a positive folder test for taxes/2025.pdf."
    },
    {
      "severity": "P2",
      "evidence_level": "confirmed from code; impact deployment-dependent",
      "location": "uploads.py:10",
      "scenario": "If /srv/uploads is a symlink, realpath(path) never shares the literal UPLOAD_DIR prefix, so every read raises ValueError: an outage.",
      "fix": "Compare against os.path.realpath(UPLOAD_DIR), computed once at import time."
    },
    {
      "severity": "P3",
      "evidence_level": "inferred; precondition (attacker can create symlinks in upload tree) unverified",
      "location": "uploads.py:9-12",
      "scenario": "A TOCTOU race between realpath and open: a directory component swapped for a symlink after the check lets open() escape UPLOAD_DIR.",
      "fix": "Open components with dir_fd and O_NOFOLLOW, or verify via fstat that the opened file lies under the upload directory."
    },
    {
      "severity": "P3",
      "evidence_level": "confirmed from code",
      "location": "uploads.py:9-12",
      "scenario": "name '' / '.' / 'taxes/' resolves to a directory, passes the check, and open() raises IsADirectoryError instead of ValueError, which may surface as a 500.",
      "fix": "Reject a resolved path equal to the upload root, or require os.path.isfile(path), and raise ValueError."
    }
  ]
}
```