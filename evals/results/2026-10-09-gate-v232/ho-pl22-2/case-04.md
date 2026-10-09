# Adversarial Diagnostic Review: `downloads.py` / `test_downloads.py`

*No tools were available in this session. Nothing below was executed. Findings come from tracing the code by hand, and evidence levels reflect that.*

## Pass 1: Reconstruct

The work adds three functions, `receipt`, `manual` and `station_map`. Each takes a caller-supplied file name and returns the file's bytes from `DOCS/receipts`, `DOCS/manuals` or `DOCS/maps`. Containment is enforced by `_inside`, which resolves both the folder and the requested path with `os.path.realpath` and then requires the result to start with `base + os.sep`.

For this to be correct and safe, the following must hold:

1. The realpath-plus-prefix check rejects every name that resolves outside the folder.
2. Every file in each folder may be served to whoever can reach the handler. **This is unstated, and it is false for receipts.**
3. A route layer, which is not shown, wires these functions to HTTP, sets content types, and maps exceptions to sensible responses.
4. `PEDALO_DOCS` is either set correctly or unset.
5. Nobody hostile can write into the docs folders between the check and the `open`.

## Pass 2: Attack (Track B)

**Path containment holds against the usual attacks.** I traced each of these by hand:

| Input | Result |
|---|---|
| `../secret.txt` | resolves to `DOCS/secret.txt`, refused |
| `/etc/passwd` | `os.path.join` discards `base`, resolves to `/etc/passwd`, refused |
| `../maps2/x` (sibling-prefix trick) | refused, because the check uses `base + os.sep` rather than `base` |
| symlink inside the folder pointing outside | `realpath` follows it, refused |
| `""` or `.` | resolves to `base`, which does not start with `base + "/"`, refused (`ValueError`) |
| NUL byte | `ValueError` from `realpath` or `open`, no bypass |
| `..%2f` | either the framework decodes it, and the check then applies, or it stays a literal nonexistent name |

The weak points are elsewhere: authorization, error handling, configuration, and how much the tests actually cover.

## Pass 3: Self-check

- I dropped a Windows case-sensitivity concern. Production is `/srv`, i.e. Linux.
- I dropped "reads the whole file into memory" as a standalone finding. It is only a problem if large files exist, so it is folded into the errors finding.
- I downgraded the TOCTOU symlink race to Low. It needs write access to the docs folders.
- **Where the most serious miss could hide:** the route layer I cannot see. It might pass the raw URL path, or a doubly-decoded value, into these functions, or expose them without authentication at all.

---

**VERDICT: SHIP WITH FIXES.** Path containment is sound for manuals and maps. However, `receipt()` serves any rider's receipt to anyone who can guess a file name, so it must not ship without an ownership check.

**CONFIDENCE IN VERDICT: medium.** The route and authentication layer was not provided, and no tests could be run.

### Findings

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED (no ownership check in the code); PROBABLE (exploitable) | `receipt(name)`, `downloads.py`; docstring example `'2026-09-r1.pdf'` | Receipts are per-rider personal and payment records, but the handler takes only a file name. It has no rider identity and no ownership check. The example naming (`YYYY-MM-rN`) is sequential and guessable. | A logged-in rider requests `receipt('2026-09-r2.pdf')`, `r3`, and so on, and downloads other riders' receipts (IDOR). Authenticating the route does not help, because the function cannot bind the file to the requester. | Change the signature to `receipt(rider_id, name)`. Look the receipt up from a record owned by `rider_id`, or store receipts under `receipts/<rider_id>/`, and refuse on mismatch. Use unguessable receipt IDs. Add a test: rider A requests rider B's receipt and gets a denial. |
| 2 | Medium | CONFIRMED (tests read) / PROBABLE (survival traced by hand, not run) | `test_traversal_is_refused_by_every_handler` | The only hostile input tested is `../secret.txt`. Several broken implementations would still pass. | (a) Mutating `base + os.sep` to `base` lets the sibling-prefix bypass through, and the test stays green. (b) Swapping `realpath` for `abspath` lets symlink escape through, and the test stays green. (c) Replacing the check with `if '..' in name` lets absolute paths through, and the test stays green. | Add cases for: absolute path; `../receipts2/x` with a sibling dir `receipts2`; a symlink inside `maps/` pointing to `secret.txt`; `""`; and a directory name. Run each mutation above in a scratch copy and confirm it turns red. |
| 3 | Medium | CONFIRMED (code) / UNVERIFIED (route mapping) | all three handlers, `open(...)` | No error handling. A missing file raises `FileNotFoundError`, a directory name raises `IsADirectoryError`, and traversal raises `ValueError`. All propagate raw. | If the route maps uncaught exceptions to 500 with a traceback, the response leaks absolute server paths (`/srv/pedalo/docs/...`). Probing `maps` vs `maps/x` also gives an existence oracle. | Catch these exceptions and return a uniform 404. Test that a nonexistent name, a directory name and a traversal attempt all produce the same not-found response. |
| 4 | Medium | PROBABLE | whole module vs request "Add three download handlers to the rider site" | The deliverable is plain functions that return bytes. There is no route registration, no `Content-Type`, and no `Content-Disposition: attachment`. "Handlers to the rider site" is only partly delivered. | When wired naively, a PNG or PDF is served with the wrong or a sniffed type. An HTML or SVG file placed in `maps/` would render inline on the rider site's origin, which is a stored-XSS vector. | Show the route wiring. Set the content type explicitly, send `attachment` and `X-Content-Type-Options: nosniff`, and restrict extensions per folder (`.pdf`, `.png`). |
| 5 | Low | PROBABLE | `DOCS = os.environ.get("PEDALO_DOCS", "/srv/pedalo/docs")` | If the variable is set but empty, `DOCS = ""`, so the folders resolve relative to the process working directory. | A deploy sets `PEDALO_DOCS=` and the app serves `./receipts` from wherever it was started, possibly an unexpected tree. | Use `os.environ.get(...) or default`, require an absolute path, and fail at startup if it is not one. |
| 6 | Low | PROBABLE | `_inside` then `open` | Check-then-open race: the path is resolved, then opened by name. | Someone with write access to a docs folder swaps a file for a symlink to `/etc/...` between the check and the open. | Open with `O_NOFOLLOW` or an `openat`-style directory fd, or verify `os.fstat` on the opened fd. This only matters if folders are writable at runtime, e.g. receipt generation. |
| 7 | Low | CONFIRMED | `test_downloads.py` `setUp` | The test sets the global `downloads.DOCS` and never restores it, and never deletes the temp dir. | Other test modules run in the same process inherit the temp `DOCS`, causing order-dependent results. | Use `addCleanup` to restore `DOCS` and remove `self.tmp`. |

### What holds up

- The containment check in `_inside` is correctly built. It applies `realpath` to both sides, which defeats symlinks and `..`. The `+ os.sep` defeats sibling-prefix names. Absolute names are refused.
- All three handlers route through the same helper, so there is no handler that skips the check.
- `DOCS` is read at call time, so the test override really takes effect.
- The existing traversal test does go red if the check is removed entirely (traced by hand, not run).

### Unverified claims

- **"2 tests in test_downloads.py pass."** Not run. Confirm with `python -m unittest test_downloads -v`.
- **Production config.** That `PEDALO_DOCS` is unset or absolute in production, and that the docs folders are read-only at runtime. Confirm from the deploy config and the folder permissions.
- **Route layer behaviour.** How names reach these functions (URL-decoded once?), whether authentication is applied, and how exceptions map to responses. Confirm by reading the route code.

### Questions for the author

1. How does the site know which rider is asking, and where is the receipt-to-rider ownership enforced? If the answer is "nowhere", the verdict becomes REWORK for receipts.
2. Are any of the three folders written to at runtime, for example receipts generated on purchase?
3. What does the route do with an uncaught `ValueError` or `FileNotFoundError`?

### Decision-maker summary

Manuals and maps can ship once errors are mapped to 404 and the traversal tests are broadened. Receipts must not ship until the handler checks that the requesting rider owns the file. If shipped as is, any rider who guesses a receipt file name can download other riders' payment records.

### Owner summary

The new download feature safely stops people from reaching files outside the intended folders. However, the receipts download does not check who is asking, so one rider could fetch another rider's receipts by guessing file names. That needs fixing before launch, along with a few smaller clean-ups to error messages and tests.

```json
{
  "verdict": "SHIP WITH FIXES",
  "findings": [
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED (no ownership check in code); PROBABLE (exploitable)",
      "location": "downloads.py receipt(name); docstring example '2026-09-r1.pdf'",
      "scenario": "A rider requests receipt('2026-09-r2.pdf'), 'r3', etc. and downloads other riders' receipts; the handler has no rider identity, so route-level authentication cannot bind the file to the requester (IDOR on personal/payment data).",
      "fix": "Take rider_id, resolve the receipt via a record owned by that rider or a receipts/<rider_id>/ subfolder, use unguessable IDs, and add a test that rider A cannot fetch rider B's receipt."
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED (tests read) / PROBABLE (mutation survival traced by hand, not run)",
      "location": "test_downloads.py test_traversal_is_refused_by_every_handler",
      "scenario": "Only '../secret.txt' is tested; mutating base+os.sep to base, realpath to abspath, or the check to \"'..' in name\" all leave the test green while reopening sibling-prefix, symlink, or absolute-path escapes.",
      "fix": "Add absolute-path, sibling-prefix (receipts2), symlink-escape, empty and directory-name cases; mutate in a scratch copy and confirm each goes red."
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED (code) / UNVERIFIED (route mapping)",
      "location": "downloads.py open(...) in all three handlers",
      "scenario": "Missing file, directory name or traversal raise FileNotFoundError/IsADirectoryError/ValueError uncaught; a 500 with traceback leaks /srv/pedalo/docs paths and gives an existence oracle.",
      "fix": "Catch these and return a uniform 404; test that missing, directory and traversal names get identical responses."
    },
    {
      "severity": "Medium",
      "evidence_level": "PROBABLE",
      "location": "downloads.py whole module vs request 'download handlers to the rider site'",
      "scenario": "Functions return raw bytes with no route, Content-Type or Content-Disposition; an HTML/SVG file in maps/ could render inline on the site origin (stored XSS), and PDFs/PNGs may be mis-served.",
      "fix": "Show route wiring; set explicit content type, Content-Disposition: attachment, X-Content-Type-Options: nosniff; allow-list extensions per folder."
    },
    {
      "severity": "Low",
      "evidence_level": "PROBABLE",
      "location": "downloads.py DOCS = os.environ.get('PEDALO_DOCS', '/srv/pedalo/docs')",
      "scenario": "PEDALO_DOCS set to empty string makes DOCS relative to the process working directory, serving files from an unintended tree.",
      "fix": "Use `os.environ.get(...) or default`, require an absolute path, fail at startup otherwise."
    },
    {
      "severity": "Low",
      "evidence_level": "PROBABLE",
      "location": "downloads.py _inside() followed by open()",
      "scenario": "If a docs folder is writable at runtime, a file can be swapped for an outward symlink between the realpath check and open (TOCTOU).",
      "fix": "Open relative to a directory fd with O_NOFOLLOW, or verify the opened fd, if folders are writable at runtime."
    },
    {
      "severity": "Low",
      "evidence_level": "CONFIRMED",
      "location": "test_downloads.py setUp",
      "scenario": "downloads.DOCS is overwritten globally and never restored and the temp dir is never removed, causing order-dependent results in other test modules.",
      "fix": "Use addCleanup to restore DOCS and remove the temp directory."
    }
  ]
}
```