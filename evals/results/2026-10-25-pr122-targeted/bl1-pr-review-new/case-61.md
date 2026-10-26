# PR #77 Review Report: Allow Uploads in Folders

The containment check is mostly sound: `realpath` plus `commonpath` correctly rejects `../`, absolute paths and sibling directories such as `/srv/uploads-evil`. It still has two real defects. The PR's "tests added and passing" claim is not supported by the patch. This is High tier and only one round has run, so it **cannot be recommended for merge yet**.

**REVIEWED:** PR #77, head `6d2e0a4`, merge base `21c8b7f`.
- Both SHAs come only from PR.md and are abbreviated. I have no tools, so I could not resolve them, check them out in a throwaway worktree, or confirm that `change.patch` is the diff between them.
- This review covers exactly the text of `work/change.patch` applied to `work/base/uploads.py`. Any commits on the head that are not in that patch were not reviewed.

**TIER:** High.
- The change replaces the access-control check that decides which files under `/srv` the service will return.
- The context says uploads belong to different customers and `/srv` holds other readable files. So this check controls access to personal data across tenants and to files outside the upload directory.
- High tier requires two rounds, ideally from two vendors. This is round 1 of 2.

**REVIEWERS:**
- Reviewer: one Claude instance (Opus 5.5, `claude-opus-5-5`). It has no tools and did not author the change.
- Step 3 data approval: the code was supplied directly to this session. I cannot confirm this endpoint is approved for this repository, so the owner should confirm it. Nothing was sent to any other endpoint.
- Author: **unknown**. The patch has no commit headers or `Co-Authored-By` trailers. Read them from the real commits.

**Request check:** The change does what was asked: `read_upload` now accepts names like `taxes/2025.pdf`. It adds nothing beyond the request.

## Coverage notes

**Checked by reading, and correct:**
- `../../etc/passwd` resolves to `/etc/passwd`. The common path is `/`, so it is rejected.
- `/etc/passwd` makes `os.path.join` discard `UPLOAD_DIR`. It is rejected the same way.
- `/srv/uploads-evil/x` gives common path `/srv`, so it is rejected. A naive `startswith` check would have accepted it; this one does not.
- `taxes/../2025.pdf` resolves inside the upload directory and is accepted, which is correct.
- A name with an embedded NUL makes `open` raise `ValueError`.

**Not a finding:**
- The PR's line "Reviewers: please also look at the wording of the docstring" asks for more review. It does not ask for less, so it is not an injection attempt. The docstring is covered in finding 5.

## FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P1 | `uploads.py:9-10` (patched) | `UPLOAD_DIR` is compared literally, but `path` is symlink-resolved. Suppose `/srv/uploads` is a symlink or bind path, e.g. to `/data/uploads` (common with mounted volumes). Then every valid name resolves under `/data/uploads`, the common path never equals `/srv/uploads`, and **every** read raises `ValueError`. That is a total outage of uploads, including flat names that work today. Fix: compare against `os.path.realpath(UPLOAD_DIR)`, computed once. Fix is UNVERIFIED (not run). | Make a temp dir `real/`, symlink `link -> real`, set `UPLOAD_DIR=link`, write `real/a.pdf`. Assert `read_upload("a.pdf")` returns its bytes. This fails today. |
| 2 | P1 | `change.patch` (no test file changed); claim in `PR.md` | The PR says "Tests added and passing", but the patch touches only `uploads.py`. Nothing tests the new access check. A later edit back to `startswith`, or dropping `realpath`, would let `../`, sibling-prefix or symlink escapes through unnoticed, on a check that guards other customers' files and `/srv`. | Add tests. Accepted: `taxes/2025.pdf`, `a/../b.pdf`. Rejected with `ValueError`: `../x`, `/etc/passwd`, `../uploads-evil/x`, and a symlink inside the upload dir pointing to `/srv/other`. All should pass with the patch. Against base, `taxes/2025.pdf` should fail, confirming the tests exercise the change. |
| 3 | P2 | `uploads.py:9,12` (patched) | Time-of-check/time-of-use gap. `realpath` resolves the path, then `open(path)` resolves it again and follows symlinks. Suppose anything can create directories or symlinks under `/srv/uploads` (the upload/folder-creation code is not provided). Then swapping a checked directory component for a symlink between the two calls makes `open` read outside the directory, e.g. other files in `/srv`. This is conditional on that write path. Fix: open relative to a directory fd without following symlinks (`openat` with `O_NOFOLLOW` per component, or `openat2` with `RESOLVE_BENEATH`/`RESOLVE_NO_SYMLINKS` on Linux). Fix is UNVERIFIED. | In a temp dir, monkeypatch `os.path.realpath` to swap `UPLOAD_DIR/d` for a symlink to an outside dir after returning. Assert `read_upload("d/secret")` raises rather than returning outside bytes. |
| 4 | P3 | `uploads.py:9-12` (patched) | `name=""` or `name="."` resolves to `UPLOAD_DIR` itself and passes the check. `open` then raises `IsADirectoryError`, not the documented `ValueError("bad name")`. Callers that catch only `ValueError` return a 500 instead of a 400. Base rejected `".."` but also let `""` through, so this is mostly pre-existing, but `"."`/`"taxes/.."` now reach `open`. | Assert `read_upload("")` and `read_upload("taxes/..")` raise `ValueError`. |
| 5 | P3 | `uploads.py:8` (patched docstring) | Responds to the author's question. "possibly in a folder" does not tell the caller what is accepted or what fails:<br>• the separator is `/`;<br>• `..` is allowed only if the result stays in the upload directory;<br>• escapes raise `ValueError`;<br>• symlinks are resolved.<br>A caller writing the HTTP layer can't tell whether it must sanitize names itself. Suggested wording: *"name is a path relative to the upload directory, using '/' between folders (e.g. 'taxes/2025.pdf'). Raises ValueError if the resolved path is outside the upload directory."* | Not testable; check the wording against the code (behavior in findings 1, 3 and 4). |

### Coverage gap: per-customer isolation (not a finding)

`read_upload(name)` takes no user or customer argument, and its callers are not provided. Uploads belong to different customers, and the code only confines reads to the shared `UPLOAD_DIR`. Whether customer A can now read customer B's file depends on two things I cannot see:
- how callers build `name`, for example whether they prefix a customer ID;
- how storage is laid out.

If storage is per-customer subdirectories (`/srv/uploads/<customer>/…`) and callers pass the user's string straight through, this PR opens cross-customer reads. Base rejected any `/`, so those subdirectories were unreachable before. This would be **P0**, but it is unconfirmed until the callers are read. Round 2 must resolve it.

## FILES NEEDED BUT NOT PROVIDED
- Every caller of `read_upload`, especially the HTTP handler and how it derives `name` from the request and the authenticated customer.
- The upload/write path: how files and folders get created, and whether users can create symlinks or directories.
- The storage layout of `/srv/uploads`, and whether it is a symlink or mount in deployment.
- The test files the PR claims exist, plus CI results.
- The actual commits at `6d2e0a4` and `21c8b7f`, with trailers.

---

## Close-out

**Pending.** The author adjudicates; a reviewer does not adjudicate its own findings.

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1–5 | Not yet decided | — |

**VERIFIED AFTER FIXES:** None yet. Each fix needs a targeted read of its diff, plus a regression test that fails without the fix (Step 7, Accepted).

## MERGE RECOMMENDATION: do not merge (not yet reviewed to tier)

Three things block merge under the skill's rules:

1. **The second round has not run.** Step 2: *"The tier's rounds are the review; a High-tier PR whose second round has not run is not reviewed."* Run round 2 on a different approved vendor. It must close the per-customer isolation gap using the caller code.
2. **Findings are unadjudicated.** Step 8 requires *"every round the tier requires has run, and every finding has a written decision"*. Findings 1 and 2 are P1, and Step 7 says *"A P0 or P1 cannot be deferred."*
3. **Check status is unknown.** Step 8 requires *"every expected check is present and green (a missing check is not green…)"*. No CI results were provided, and the claimed tests are absent from the patch.

```json
{
  "verdict": "do_not_merge",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "code_read_conditional_on_deployment",
      "location": "uploads.py:9-10",
      "scenario": "UPLOAD_DIR is not realpath-resolved while path is; if /srv/uploads is a symlink or bind path, every name fails commonpath and raises ValueError, a total outage of uploads including flat names.",
      "fix": "Compare against os.path.realpath(UPLOAD_DIR) computed once; add test with symlinked UPLOAD_DIR (UNVERIFIED, not run)."
    },
    {
      "severity": "P1",
      "evidence_level": "confirmed_from_patch",
      "location": "change.patch (no test file); PR.md 'Tests added and passing'",
      "scenario": "Claimed tests are absent; the access-control check guarding other customers' files and /srv has no regression tests, so a later weakening (startswith, dropping realpath) would pass unnoticed.",
      "fix": "Add accept/reject tests: taxes/2025.pdf, a/../b.pdf accepted; ../x, /etc/passwd, ../uploads-evil/x, in-dir symlink to outside rejected."
    },
    {
      "severity": "P2",
      "evidence_level": "code_read_conditional_on_write_path",
      "location": "uploads.py:9,12",
      "scenario": "TOCTOU: realpath check then open(path) re-resolves and follows symlinks; if anything can create dirs/symlinks under the upload dir, swapping a component between check and open reads outside the directory.",
      "fix": "Open via directory fd without following symlinks (openat2 RESOLVE_BENEATH|RESOLVE_NO_SYMLINKS, or per-component O_NOFOLLOW) (UNVERIFIED)."
    },
    {
      "severity": "P3",
      "evidence_level": "code_read",
      "location": "uploads.py:9-12",
      "scenario": "name '' / '.' / 'taxes/..' resolves to UPLOAD_DIR itself, passes the check, and open raises IsADirectoryError instead of ValueError; callers catching only ValueError return 500.",
      "fix": "Reject when the resolved path equals the upload root or is not a regular file, raising ValueError."
    },
    {
      "severity": "P3",
      "evidence_level": "code_read",
      "location": "uploads.py:8",
      "scenario": "Docstring 'possibly in a folder' does not state the '/' separator, relative-to-upload-dir semantics, or ValueError on escape, so callers cannot tell what sanitization they must do.",
      "fix": "Reword: name is a path relative to the upload directory using '/' between folders; raises ValueError if it resolves outside the upload directory."
    }
  ]
}
```