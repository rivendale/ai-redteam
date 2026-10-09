# Adversarial Diagnostic Review: Pedalo download handlers

## Pass 1: Reconstruct

The work adds three functions, `receipt`, `manual` and `station_map`. Each takes a caller-supplied name, resolves it under `DOCS/<folder>` through `_inside`, and returns the file's bytes. `_inside` takes the `realpath` of both the folder and the joined path, and refuses any result that does not start with `base + os.sep`. For the work to be correct, four things must hold:

- `realpath` fully resolves `..`, absolute names and symlinks before the check.
- Nothing can change the filesystem between the check and `open`.
- Every file in each folder may go to anyone who asks for it.
- Some unseen web layer turns these functions into HTTP handlers and maps the exceptions to 4xx responses.

The last two assumptions are unstated. The third is the one most likely to be false, because receipts belong to individual riders.

## Pass 2: Attack (Track B)

I could not run anything. Everything below comes from tracing the code by hand.

**The path containment logic holds.** I traced these inputs:

| Input | Resolves to | Result |
|---|---|---|
| `../secret.txt` | `DOCS/secret.txt` | not under `base/`, refused |
| `/etc/passwd` | `os.path.join` drops `base`, gives `/etc/passwd` | refused |
| `..` | `DOCS` | refused |
| `""` | `base` itself, which fails `startswith(base + sep)` | refused |
| `../receipts_old/x` (sibling with the same prefix) | outside `base/` | refused, because the check includes the separator |
| symlink inside the folder pointing outside | `realpath` follows it | refused |
| `a/../../maps/x` | outside `base/` | refused |
| URL-encoded `..%2f` | the literal file name `..%2f`, which stays inside the folder | harmless here, as long as the framework decodes only once before calling |

**Tests.** I mentally removed the check: `receipt("../secret.txt")` then opens `DOCS/secret.txt`, returns `b"top secret"`, and the test goes red. So the traversal test does guard the main mutation, and `test_normal_names_work` acts as the positive control. Two weaker replacement checks would still pass both tests:
- `startswith(base)` without the separator.
- `if ".." in name: raise`, which would let `/etc/passwd` through.

## Pass 3: Self-check

I dropped a finding about TOCTOU symlink swapping and downgraded it to a note. It requires an attacker who can already write into the docs folder, and nothing in the material shows that. A finding about whole-file reads into memory is real but minor; I kept it as Low.

The most serious problem I might still be missing would sit in the layer I cannot see: how the web framework passes `name`, and whether it authenticates the rider. Findings 1 and 2 hinge on that layer.

---

**VERDICT: SHIP WITH FIXES.** The path-traversal defence is sound and its test genuinely fails when the check is removed. However, the receipt handler serves any rider's receipt to anyone who knows or guesses its name, and the "handlers" are not actually wired into the site.

**CONFIDENCE IN VERDICT: medium.** It is limited because I could not see the routing and auth layer, and I could not run the tests.

## Findings

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | High | PROBABLE | `receipt(name)`, docstring "A rider's receipt, e.g. receipt('2026-09-r1.pdf')" | There is no ownership or authentication check. Receipts are per-rider personal data, but any caller can fetch any receipt by name. | Names follow a guessable `YYYY-MM-rN.pdf` pattern. A logged-in or anonymous user loops over `2026-09-r1` through `r9999`. That exposes other riders' payment records. A `FileNotFoundError` vs success response also tells the attacker which receipts exist. | Resolve the receipt from the authenticated rider's identity, for example `receipts/<rider_id>/<name>`, or check ownership in a database before reading. Add a test that rider A cannot fetch rider B's receipt. If an auth layer already does this, point to it. |
| 2 | Medium | CONFIRMED (absence), UNVERIFIED (wiring elsewhere) | `downloads.py` as a whole | The request asked for "download handlers to the rider site". The work delivers plain functions with no route, no Content-Type or Content-Disposition, and no HTTP status mapping. | Wired naively, `ValueError` and `FileNotFoundError` become 500 responses, possibly with tracebacks that reveal `/srv/pedalo/docs` paths. A PNG map may be served as `application/octet-stream` or inline. | Show the route code. Map `ValueError` and `FileNotFoundError`/`IsADirectoryError` to 404. Set the content type by extension and `Content-Disposition: attachment`. |
| 3 | Medium | CONFIRMED | `test_traversal_is_refused_by_every_handler` | Only `../secret.txt` is tested, so regressions to weaker checks would pass. | Someone "simplifies" the guard to `if ".." in name` or `startswith(base)`. Both tests stay green, but `receipt("/etc/passwd")` or `receipt("../receipts_old/x")` now leaks files beside docs, which the context says hold other server files. | Add refused cases for an absolute path (`/etc/passwd` or the absolute tmp `secret.txt`), a sibling-prefix folder (`receipts_old/x`), a symlink inside the folder pointing outside, `..`, and `""`. |
| 4 | Low | CONFIRMED | `_inside` then `open` in each handler | Errors are not classified. A directory name raises `IsADirectoryError`, a missing file raises `FileNotFoundError`, and a name with a null byte raises `ValueError` from `realpath` or `open`. All of these escape to the caller. | `manual("subdir")` raises an unhandled `IsADirectoryError`, and the caller cannot tell "refused" apart from "not found". | Raise a single `NotFound` for all of these, or document which exceptions callers must handle. |
| 5 | Low | CONFIRMED | `f.read()` in all three handlers | The whole file is read into memory. | Large manuals or maps under concurrent downloads drive up memory use. | Stream the file, or use the framework's send-file feature, for example `FileResponse`. |
| 6 | Low | CONFIRMED | `test_downloads.py` `setUp` | File handles are opened without being closed, the tempdir is never removed, and `downloads.DOCS` is never restored. | Tests produce ResourceWarnings, and state leaks into other test modules. | Use `with open`, `addCleanup(shutil.rmtree, ...)`, and restore `DOCS` in a cleanup. |

## What holds up

- **`_inside`'s containment check.** Using `realpath` on both sides plus the `base + os.sep` prefix correctly refuses `..`, absolute paths, sibling-prefix folders, symlink escapes and empty names.
- **Late binding of `DOCS`.** It is read at call time, so the test override works.
- **The traversal test.** It is a real test: removing the check turns it red, and the normal-names test serves as its positive control.

## Unverified claims

- **"2 tests in test_downloads.py pass."** I could not run them, though by trace they should pass. To confirm, run `python -m unittest test_downloads -v`.
- **That an auth layer protects receipts.** Nothing in the material shows one. To confirm, show the route and middleware for the receipt endpoint.
- **That the framework decodes the URL once before passing `name`.** To confirm, request `..%252fsecret.txt` against staging and check it returns 404.

## Questions for the author

1. Is the receipt endpoint behind authentication, and does anything check that the receipt belongs to the requesting rider? If yes, and it is shown, finding 1 drops and the verdict moves toward SHIP.
2. Where is the route code that turns these functions into HTTP handlers, and how does it map exceptions?

## Decision-maker summary

Manuals and maps can ship once the missing-file and refused-name errors map to 404 and the extra traversal tests are added. The receipt handler should not go live until it checks that the receipt belongs to the logged-in rider. If it ships as is, anyone can download other riders' receipts by guessing sequential file names.

## Owner summary

The new download feature correctly stops people from reaching files outside the intended folders. However, the receipts download does not check who is asking, so one rider could fetch another rider's receipt by guessing its name. Fix that and tidy up the error handling before launch; manuals and maps are otherwise fine.

```json
{
  "verdict": "SHIP WITH FIXES",
  "findings": [
    {
      "severity": "High",
      "evidence_level": "PROBABLE",
      "location": "downloads.py receipt(name), docstring 'A rider's receipt, e.g. receipt('2026-09-r1.pdf')'",
      "scenario": "No ownership/auth check; names follow a guessable YYYY-MM-rN.pdf pattern, so any caller can enumerate and download other riders' receipts (personal data); success vs FileNotFoundError also reveals which receipts exist.",
      "fix": "Derive the path from the authenticated rider (e.g. receipts/<rider_id>/<name>) or verify ownership before reading; add a test that rider A cannot fetch rider B's receipt."
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "downloads.py (whole module)",
      "scenario": "Request asked for site download handlers; work delivers bare functions with no routing, content type, or status mapping. Naive wiring turns ValueError/FileNotFoundError into 500s that may leak server paths.",
      "fix": "Provide route code; map ValueError, FileNotFoundError, IsADirectoryError to 404; set Content-Type by extension and Content-Disposition: attachment."
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "test_downloads.py test_traversal_is_refused_by_every_handler",
      "scenario": "Only '../secret.txt' is tested; regressing the guard to `'..' in name` or startswith(base) without os.sep keeps tests green while allowing '/etc/passwd' or '../receipts_old/x'.",
      "fix": "Add refusal cases for absolute paths, sibling-prefix folder, symlink inside folder pointing outside, '..' and ''."
    },
    {
      "severity": "Low",
      "evidence_level": "CONFIRMED",
      "location": "downloads.py _inside and open() in each handler",
      "scenario": "Directory names raise IsADirectoryError, missing files FileNotFoundError, null bytes ValueError; all escape unclassified, so callers cannot tell refused from not found.",
      "fix": "Raise a single NotFound exception for all, or document the exceptions callers must handle."
    },
    {
      "severity": "Low",
      "evidence_level": "CONFIRMED",
      "location": "downloads.py f.read() in all handlers",
      "scenario": "Whole file read into memory; large files under concurrent downloads increase memory use.",
      "fix": "Stream the file or use the framework's send-file response."
    },
    {
      "severity": "Low",
      "evidence_level": "CONFIRMED",
      "location": "test_downloads.py setUp",
      "scenario": "Unclosed file handles, tempdir never removed, downloads.DOCS never restored; ResourceWarnings and state leaking across test modules.",
      "fix": "Use `with open`, addCleanup(shutil.rmtree, self.tmp), and restore DOCS in cleanup."
    }
  ]
}
```