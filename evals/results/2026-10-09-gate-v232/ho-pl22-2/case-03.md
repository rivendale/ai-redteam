# Adversarial Diagnostic Review: `downloads.py`

## Pass 1: Reconstruct

The work adds three functions, `receipt`, `manual` and `station_map`. Each takes a file name from the request and returns the bytes of that file from `DOCS/<folder>`. The module docstring says "Names come from the request", so the author knew the input is untrusted. The author wrote a containment helper, `_inside`, for that reason, but used it in only one of the three functions.

For this to be correct, the following must be true:
- Every handler confines the name to its own folder, which matters because the context says the docs directory sits beside other server files.
- Something outside this file wires these functions to routes and turns exceptions into proper HTTP responses.
- It is acceptable that anyone who knows a receipt's file name can download it. This assumption is unstated.

## Pass 2: Attack (Track B, with a Track R note on receipts)

**Path traversal in `receipt` and `manual`.** These two functions call `os.path.join(DOCS, "<folder>", name)` with the raw name. Two attacks work:
- `name = "../../../etc/passwd"` resolves outside the docs tree.
- `name = "/etc/shadow"` works even more directly, because `os.path.join` throws away every earlier part when a later part is absolute. The result is plain `/etc/shadow`.

In both cases the file is opened and returned to the requester. Given the context, sibling server files such as config, keys or `.env` can be read with `"../<file>"`. I traced this from the code and from documented `os.path.join` behaviour. I could not execute it.

**`_inside` itself holds up.**
- Both the base and the target go through `realpath`, so `..` segments, absolute names and symlinks that point out of the folder are all resolved before the check.
- The prefix test is `startswith(base + os.sep)`, so a sibling folder with a similar name (`maps-private`) is not mistaken for `maps`.
- An empty name or `"."` resolves to `base`, which does not start with `base + os.sep`, so it is refused.
- A name containing a NUL byte makes `realpath`/`open` raise `ValueError`.
- The only residual gap is a time-of-check/time-of-use race. A symlink could be swapped between `realpath` and `open`, but that needs write access inside `DOCS/maps`. This is low risk.

**Receipts have no access control.** Example names like `2026-09-r1.pdf` look sequential and guessable. Nothing checks that the requester owns the receipt. Even with traversal fixed, rider A could fetch rider B's receipt, which may hold name, payment details or trip history. The request did not mention authorization, but receipts are personal data. Whether a caller enforces ownership is not visible here.

**Requirement fit.** The request asked for "download handlers to the rider site". What was delivered is three file-read functions. There is no routing, no `Content-Type`, no `Content-Disposition`, and no mapping of missing files to a 404. The wiring may live elsewhere. That is unverified.

**Failure handling.**
- `FileNotFoundError`, `IsADirectoryError`, `PermissionError` and `ValueError` all propagate to the caller unhandled.
- If the web layer renders them as a 500 or a debug page, the response leaks the absolute server path, because `open`'s error message includes it.
- In `station_map`, the response differs between a traversal attempt (`ValueError`) and a missing file (`FileNotFoundError`). This gives a weak oracle for whether a file exists.

**Operations.** `f.read()` loads the whole file into memory. That is fine for PDFs and PNGs at normal sizes, but large maps or many concurrent requests will hold whole files in memory. `DOCS` is read once at import time, which is acceptable.

**Tests.** None were supplied, so no test has ever gone red. Containment coverage for all three handlers is therefore unverified.

## Pass 3: Self-check

- The traversal finding is tied to exact lines and holds without assumptions.
- I downgraded the receipts authorization finding to PROBABLE because a caller might enforce ownership.
- The most serious thing I could still be missing is in the routing layer I cannot see. A framework may URL-decode `%2e%2e%2f` or `%2f` after its own path normalisation. That would not matter once `_inside` is applied everywhere, but it would matter for any other handler built the same way. It is also possible that `PEDALO_DOCS` is set to a path an attacker can influence. That is unlikely, but worth a check.

---

**VERDICT: REWORK.** Two of the three handlers let anyone read arbitrary server files, the receipts handler exposes other riders' receipts by name, and there are no tests to show any of it is fixed.

**CONFIDENCE IN VERDICT: High.** The traversal is visible in the code itself. Confidence is limited only by not seeing the routing and authentication layer.

## FINDINGS

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | `receipt`: `open(os.path.join(DOCS, "receipts", name), "rb")` | Untrusted name is joined without containment | `receipt("../../../etc/passwd")` or `receipt("/etc/shadow")` returns that file; `receipt("../<sibling server file>")` reads config or secrets beside docs | Use `_inside("receipts", name)`; add tests for `../x`, an absolute path, and a symlink out, each expecting refusal |
| 2 | Critical | CONFIRMED | `manual`: `open(os.path.join(DOCS, "manuals", name), "rb")` | Same traversal as #1 | `manual("/etc/passwd")` returns the system file | Use `_inside("manuals", name)`; add the same three tests |
| 3 | High | PROBABLE | `receipt` (no ownership check); docstring example `'2026-09-r1.pdf'` | Receipts are personal data, served to anyone who knows or guesses the name | A rider enumerates `2026-09-r1.pdf`, `r2`, and so on and downloads other riders' receipts | Check that the authenticated rider owns the receipt, for example by looking up the receipt by an ID scoped to that rider rather than taking a raw file name; add a test that rider A cannot fetch rider B's receipt |
| 4 | Medium | PROBABLE | All three handlers: exceptions propagate | No mapping of errors to 404/400; `open` errors include the absolute path | A missing file or traversal attempt yields a 500 or debug page showing `/srv/pedalo/docs/...`; `ValueError` vs `FileNotFoundError` reveals whether a file exists | Catch `ValueError` and `OSError` and return one uniform 404 without the path; test that both cases give the same response |
| 5 | Medium | UNVERIFIED | Whole file (no routing or headers) | Request asked for "download handlers"; delivered functions have no routes, `Content-Type` or `Content-Disposition` | Wired naively, PNGs or PDFs may be served with the wrong type, or uploaded HTML could be rendered inline | Show the route wiring; set an explicit content type per folder and `Content-Disposition: attachment`; consider an extension allowlist per folder |
| 6 | Low | PROBABLE | `_inside`: `realpath` then `open` | Time-of-check/time-of-use race on symlinks | Someone with write access to `DOCS/maps` swaps in a symlink after the check | Open with `O_NOFOLLOW` and/or verify with `os.fstat` after opening; acceptable to defer if `DOCS` is read-only to the app |
| 7 | Low | CONFIRMED | `return f.read()` in all three | Whole file is buffered in memory | Large maps under concurrent load raise memory use | Stream the file (the framework's file response, or chunked reads) |

## WHAT HOLDS UP

- **`_inside`** is a correct containment check, for the reasons given in Pass 2: it resolves `realpath` on both sides, compares with a trailing separator, and refuses the base folder itself.
- **`station_map`** is safe from traversal.
- **Configuration:** the `DOCS` location can be set through the `PEDALO_DOCS` environment variable and has a sensible default.

## UNVERIFIED CLAIMS

- **That the traversal actually runs end to end.** Running `receipt("/etc/passwd")` in a scratch copy would settle it.
- **That `_inside` blocks every attack.** No test exists. A mutation test would settle it: change the check to `startswith(base)` or remove it, and confirm that a traversal test goes red.
- **That routing, authentication and error mapping exist.** The calling code would settle it.
- **That receipt file names are not guessable.** A sample of real receipt names would settle it.

## QUESTIONS FOR THE AUTHOR

1. Why is `_inside` used only in `station_map`?
2. Who is allowed to download a given receipt, and where is that enforced?
3. Where are these functions wired to routes, and how are exceptions turned into responses?

## DECISION-MAKER SUMMARY

Do not deploy. Two of the three download handlers let anyone read arbitrary files on the server, including the server files that sit beside the docs directory. The fix is small: apply the existing `_inside` guard to all three handlers, add an ownership check for receipts, and add traversal tests. Proceeding as-is risks exposing secrets and riders' personal receipts.

## OWNER SUMMARY

The new download feature has a serious security hole: two of the three download types can be tricked into handing out any file on the server, not just the intended documents. Receipts can also be downloaded by people they do not belong to. The repair is small and well understood, but it should be made and tested before this goes live.

```json
{
  "verdict": "REWORK",
  "findings": [
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "downloads.py receipt(): open(os.path.join(DOCS, \"receipts\", name), \"rb\")",
      "scenario": "receipt(\"../../../etc/passwd\") or receipt(\"/etc/shadow\") (absolute part discards DOCS in os.path.join) returns arbitrary server files, including sibling files next to the docs directory",
      "fix": "Use _inside(\"receipts\", name); add tests for ../ traversal, absolute path and symlink-out expecting refusal"
    },
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "downloads.py manual(): open(os.path.join(DOCS, \"manuals\", name), \"rb\")",
      "scenario": "manual(\"/etc/passwd\") or manual(\"../../<server file>\") returns files outside the manuals folder",
      "fix": "Use _inside(\"manuals\", name); add the same traversal tests"
    },
    {
      "severity": "High",
      "evidence_level": "PROBABLE",
      "location": "downloads.py receipt(): no ownership check; guessable names like '2026-09-r1.pdf'",
      "scenario": "A rider enumerates sequential receipt names and downloads other riders' receipts (personal data)",
      "fix": "Require an authenticated rider and verify ownership, e.g. look up receipts by a rider-scoped ID; test that rider A cannot fetch rider B's receipt"
    },
    {
      "severity": "Medium",
      "evidence_level": "PROBABLE",
      "location": "downloads.py all handlers: exceptions propagate unhandled",
      "scenario": "Missing file or traversal attempt produces a 500/debug page exposing the absolute path; ValueError vs FileNotFoundError reveals whether a file exists",
      "fix": "Catch ValueError and OSError and return a uniform 404 without the path; test both cases give identical responses"
    },
    {
      "severity": "Medium",
      "evidence_level": "UNVERIFIED",
      "location": "downloads.py whole module: no routes, Content-Type or Content-Disposition",
      "scenario": "Request asked for download handlers; naive wiring may serve wrong content types or render HTML inline",
      "fix": "Show route wiring; set explicit content type per folder and Content-Disposition: attachment; consider per-folder extension allowlist"
    },
    {
      "severity": "Low",
      "evidence_level": "PROBABLE",
      "location": "downloads.py _inside(): realpath check followed by separate open()",
      "scenario": "Someone with write access inside DOCS/maps swaps a symlink between check and open (TOCTOU)",
      "fix": "Open with O_NOFOLLOW and/or verify with os.fstat after opening; or ensure DOCS is read-only to the app"
    },
    {
      "severity": "Low",
      "evidence_level": "CONFIRMED",
      "location": "downloads.py all handlers: return f.read()",
      "scenario": "Large files under concurrent load are fully buffered in memory",
      "fix": "Stream the file via the framework's file response or chunked reads"
    }
  ]
}
```