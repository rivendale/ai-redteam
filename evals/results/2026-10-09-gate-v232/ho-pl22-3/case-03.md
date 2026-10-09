# Adversarial Diagnostic Review: `downloads.py`

## Pass 1: Reconstruct

The work adds three functions, `receipt`, `manual` and `station_map`. Each takes a file name from the request and returns the bytes of that file from `DOCS/<folder>`. It defines a containment helper, `_inside`, whose docstring promises to refuse names that resolve outside the folder.

For the work to be correct, these must hold:
- **Containment in all three handlers.** Every handler must confine untrusted names to its own folder. The context says the docs directory sits beside other server files, so escaping it exposes those files.
- **Receipt ownership.** Receipts belong to individual riders, so something must stop one rider from fetching another rider's receipt. This assumption is unstated in the work.
- **Error handling.** Callers must handle the errors these functions raise.
- **Configuration.** `PEDALO_DOCS` must point at a directory that holds only downloadable content.

## Pass 2: Attack (Track B, with Track R for receipt data)

**Main trace for `station_map`.** `_inside("maps", name)` resolves the base folder with `realpath`, resolves the joined name with `realpath`, and requires the result to start with `base + os.sep`.

Hostile inputs I traced:
- `../../etc/passwd` resolves outside `maps` and is refused.
- `/etc/passwd` is refused. `os.path.join` discards the base when given an absolute component, but the result still fails the prefix check.
- A symlink inside `maps` that points elsewhere is refused, because `realpath` follows it before the check.
- `""` or `.` resolves to `base` itself, which does not start with `base + "/"`, so it is refused.
- `maps-evil/x` is refused, because the separator in the check prevents sibling-prefix confusion.

`station_map` holds.

**`receipt` and `manual`** bypass `_inside` entirely and pass the raw name to `os.path.join`:
- `receipt("../../../etc/passwd")` reads `/srv/pedalo/etc/passwd` and continues upward until it reaches a real file.
- `receipt("/etc/shadow")` makes `os.path.join` return `/etc/shadow` directly.
- `manual("../../app/config.py")` or `manual("../../.env")` reads neighbouring server files, which the context explicitly warns sit beside the docs directory.

The author wrote the guard, then applied it to one of three handlers. The file therefore *looks* defended, which makes the gap harder to spot in a casual review.

## Findings

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED (by `os.path.join` semantics; not executed, no tools) | `receipt()`: `open(os.path.join(DOCS, "receipts", name), "rb")` | No containment check. Path traversal and absolute paths both work. | Request `name=../../../etc/passwd` or `name=/srv/pedalo/app/.env` and the server returns that file's bytes. Server secrets and source are exposed. | Use `open(_inside("receipts", name), "rb")`. Add tests asserting `ValueError` for `../x`, `/etc/passwd`, `""`, and a symlink pointing out of the folder. |
| 2 | Critical | CONFIRMED (same reasoning) | `manual()`: `open(os.path.join(DOCS, "manuals", name), "rb")` | Same traversal hole as #1. | `name=../../../etc/passwd` returns that file. Because manuals are public, this endpoint is probably unauthenticated, so anyone on the internet can read server files. | Use `_inside("manuals", name)`, with the same tests as #1. |
| 3 | Critical | PROBABLE (caller not shown) | `receipt()`; request text "takes a file name from the request" | There is no ownership check. Any requester who knows or guesses a name (the docstring shows the pattern `2026-09-r1.pdf`) gets that rider's receipt. Containment alone does not fix this. | Rider A enumerates `2026-09-r1.pdf`, `r2`, `r3`, and so on, and downloads other riders' receipts. Those contain personal and payment data, creating privacy and regulatory exposure. | Look up receipts by the authenticated rider's ID plus a receipt ID checked against their account, rather than by a client-supplied file name. Add a test in which rider A requests rider B's receipt and gets 403 or 404. |
| 4 | Medium | CONFIRMED | `receipt`/`manual`/`station_map`: `f.read()` | Each call reads the whole file into memory. | A large map PNG or PDF combined with concurrent requests causes memory spikes. Repeated requests become a cheap denial-of-service lever. | Stream the file with the framework's file response (for example `send_file` or `FileResponse`) or read in chunks, and cap the size. |
| 5 | Low | PROBABLE | All three handlers; `_inside` | Errors are raised but not mapped. A missing file raises `FileNotFoundError`, whose message contains the full server path. A directory name such as `subdir` raises `IsADirectoryError`. A traversal attempt raises `ValueError`. | If the caller returns exception text or a debug page, the response leaks `/srv/pedalo/docs/...` and the internal layout. Unhandled exceptions become 500 errors. | Have callers map `ValueError`, `FileNotFoundError` and `IsADirectoryError` to a uniform 404 without the path. Test that the response bodies contain no filesystem paths. |
| 6 | Low | PROBABLE | `_inside` then `open` | There is a time-of-check to time-of-use gap: the path is checked, then reopened. | Someone with write access to `maps` swaps a component for a symlink between the check and the open. This needs local write access, so the risk is low. | Open the resolved path with `O_NOFOLLOW`, or verify the path after opening with `os.path.realpath(f"/proc/self/fd/{fd}")`. Alternatively, make sure the docs directories are not writable by untrusted parties. |
| 7 | Low | UNVERIFIED | `DOCS = os.environ.get(...)` | The root comes from configuration with no validation. | If `PEDALO_DOCS` is misconfigured as `/srv/pedalo` or `/`, then `_inside` "contains" requests to a much broader tree. | Assert at startup that `DOCS` exists and is the expected directory. Log the resolved path. |

## What holds up

`_inside` is correctly written for Linux:
- It resolves symlinks on both the base and the target.
- It uses `base + os.sep`, which avoids the classic `startswith` sibling-prefix bug.
- It handles absolute names, empty names and `.`.

`station_map` is safe against traversal as written. The scope matches the request: three handlers, nothing extra.

## Unverified claims

- **The `_inside` docstring claim** ("refusing any name that resolves outside"). I confirmed it by reading the code but did not run it. To confirm it, run the hostile-input tests above against a temporary `DOCS` tree.
- **Tests.** There are none, so no test has ever been shown to fail. To settle this, write the traversal tests, then temporarily remove the `_inside` call from `station_map` in a scratch copy and confirm the tests go red.
- **How the caller wires these handlers.** Authentication, URL decoding and error mapping all depend on the caller. To settle this, review the route definitions.

## Questions for the author

1. Why does only `station_map` use `_inside`? Was this an oversight, or a deliberate choice I am missing?
2. How is a receipt download tied to the logged-in rider? Who supplies the file name, and can a rider name another rider's receipt?
3. Are these handlers behind authentication, and how are their exceptions turned into HTTP responses?

## Decision-maker summary

Do not ship as-is: two of the three handlers let anyone read arbitrary server files, and receipts appear to have no ownership check. Applying the existing `_inside` guard to `receipt` and `manual` is a two-line fix, but the receipt access model needs a deliberate design and a test. If you proceed anyway, expect exposure of server secrets and riders' personal receipt data.

## Owner summary

Two of the three new download features can be tricked into handing out any file on the server, including private configuration, and receipts may be downloadable by people they don't belong to. The fix for the first problem is small and already half-written, but the second needs a clear rule about who may download which receipt. This should not go live until both are fixed and tested.

```json
{
  "verdict": "REWORK",
  "findings": [
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "downloads.py receipt(): open(os.path.join(DOCS, \"receipts\", name), \"rb\")",
      "scenario": "name='../../../etc/passwd' or an absolute name '/etc/shadow' (os.path.join discards the base) returns arbitrary server files, including neighbouring server files beside the docs directory.",
      "fix": "Use open(_inside(\"receipts\", name), \"rb\"); add tests asserting ValueError for '../x', '/etc/passwd', '', and an outward symlink."
    },
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "downloads.py manual(): open(os.path.join(DOCS, \"manuals\", name), \"rb\")",
      "scenario": "name='../../../etc/passwd' reads arbitrary files; manuals are likely public, so this is an unauthenticated arbitrary file read.",
      "fix": "Use _inside(\"manuals\", name); same traversal tests as receipt."
    },
    {
      "severity": "Critical",
      "evidence_level": "PROBABLE",
      "location": "downloads.py receipt(); request: 'takes a file name from the request'",
      "scenario": "Rider A guesses names following the docstring pattern (2026-09-r1.pdf, r2, ...) and downloads other riders' receipts containing personal and payment data.",
      "fix": "Resolve receipts from the authenticated rider ID plus a receipt ID checked against their account; test that a cross-rider request returns 403/404."
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "downloads.py all handlers: f.read()",
      "scenario": "Large maps or PDFs under concurrent requests load fully into memory, causing memory spikes and an easy DoS lever.",
      "fix": "Stream via the framework's file response or read in chunks; cap the file size."
    },
    {
      "severity": "Low",
      "evidence_level": "PROBABLE",
      "location": "downloads.py all handlers and _inside: unhandled ValueError/FileNotFoundError/IsADirectoryError",
      "scenario": "A missing file raises FileNotFoundError with the full server path; if the caller echoes exception text, the internal layout leaks, and unhandled errors become 500s.",
      "fix": "Map these exceptions to a uniform 404 without the path; test that response bodies contain no filesystem paths."
    },
    {
      "severity": "Low",
      "evidence_level": "PROBABLE",
      "location": "downloads.py _inside() followed by open() in station_map",
      "scenario": "Time-of-check to time-of-use: someone with write access to maps swaps a path component for a symlink between the check and the open.",
      "fix": "Open with O_NOFOLLOW or verify the real path of the opened fd; ensure the docs directories are not writable by untrusted parties."
    },
    {
      "severity": "Low",
      "evidence_level": "UNVERIFIED",
      "location": "downloads.py DOCS = os.environ.get(\"PEDALO_DOCS\", \"/srv/pedalo/docs\")",
      "scenario": "PEDALO_DOCS misconfigured to a broad root such as /srv/pedalo or / widens what _inside treats as contained.",
      "fix": "Validate DOCS at startup and log the resolved path."
    }
  ]
}
```