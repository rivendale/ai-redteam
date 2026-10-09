VERDICT: **REWORK.** Two of the three handlers pass the request's file name straight into a filesystem path, so any caller can read any file the server process can read, including the server files next to the docs directory.

CONFIDENCE IN VERDICT: **High.** The traversal follows directly from the quoted code and standard `os.path.join` behaviour. Confidence is limited only by not knowing the web framework, which affects how names are decoded and how exceptions reach the client. I could not run anything in this session.

## Pass 1: Reconstruct

The work adds three functions to `downloads.py`: `receipt`, `manual` and `station_map`. Each takes a name and returns the bytes of a file under `DOCS/<folder>`. Its own docstring says "Names come from the request", so the author knew the input is attacker-controlled. A guard, `_inside`, resolves the path with `realpath` and refuses anything outside the folder.

For the work to be correct, these must hold:
- Every handler confines the name to its folder.
- Only the right person can fetch a given file. This matters most for receipts, which belong to individual riders. The request does not state it.
- The functions are actually wired as request handlers with sane error responses.
- `DOCS` is configured correctly in production.

## Pass 2: Attack (Track B)

**Traversal.** Tracing `receipt("../../../etc/passwd")`:
1. `os.path.join("/srv/pedalo/docs", "receipts", "../../../etc/passwd")` gives `/srv/pedalo/docs/receipts/../../../etc/passwd`.
2. `open` resolves that to `/etc/passwd`, and the function returns its contents.

`receipt("/etc/passwd")` is even simpler. When a later component is absolute, `os.path.join` discards every earlier component and returns `/etc/passwd` directly. `manual` has the same flaw. The context says the docs directory sits beside other server files, so `../../app/settings.py`, `.env` and keys are one hop away.

**The guard (`_inside`).**
- `base + os.sep` blocks the sibling-prefix trick (`maps-private/…`).
- `realpath` defeats `..`, absolute names, and symlinks inside `maps` that point outside.
- An empty name resolves to `base`, which fails the `startswith` check and is refused.
- A NUL byte makes Python raise `ValueError`.

The guard is sound. It is just only used once.

**Hostile inputs on `station_map`.**
- A directory name such as `.` gives `base`, which is refused. A name like `sub/` that resolves to a subdirectory hits `IsADirectoryError` and is not caught.
- A missing file raises `FileNotFoundError`, also not caught.
- A huge file is read entirely into memory.

## Findings

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | `receipt`: `open(os.path.join(DOCS, "receipts", name), "rb")` | The name is not confined. `..` segments and absolute names escape the folder. | A request with name `../../app/.env` or `/etc/passwd` returns that file. This exposes server secrets and lets an attacker read any rider's data on disk. | Use `_inside("receipts", name)`. Add tests asserting `ValueError` for `../x`, `/etc/passwd`, `..%2f`-decoded forms, and a symlink pointing outside. |
| 2 | Critical | CONFIRMED | `manual`: `open(os.path.join(DOCS, "manuals", name), "rb")` | Same flaw as #1. | `manual("../../../etc/shadow")` reads the file if the process has permission. Any server file under the service user's rights is readable. | Use `_inside("manuals", name)` and the same tests as #1. Better still, make `_inside` the only path builder so no handler can bypass it. |
| 3 | High | PROBABLE | `receipt` as a whole, and the example `2026-09-r1.pdf` | There is no check that the requester owns the receipt. Names look sequential and guessable. Even with #1 fixed, any user can fetch any rider's receipt by changing the name. | Someone loops `2026-09-r1.pdf … r9999.pdf` and downloads every rider's receipts, which contain personal and payment data. | Resolve receipts by authenticated rider ID, e.g. `DOCS/receipts/<rider_id>/<name>` or a lookup table. Return 404 for other riders' files. Ask whether auth is enforced upstream; see the questions below. |
| 4 | Medium | CONFIRMED | All three functions | The request asked for "download handlers", but these are bare functions. They have no routing, `Content-Type` or `Content-Disposition`, and no mapping of errors to 404 or 400. `ValueError`, `FileNotFoundError` and `IsADirectoryError` propagate. | A missing map or a traversal attempt produces a 500, possibly with a stack trace that reveals `/srv/pedalo/docs` and the code layout. | Wrap each in the site's handler layer. Map `ValueError` to 400 or 404, map `FileNotFoundError` and `IsADirectoryError` to 404, and set content headers. |
| 5 | Medium | CONFIRMED (absence) | No test files supplied | Nothing exercises the guard, and two handlers already bypass it. Rule 5 cannot be satisfied because there is no test to mutate. | A future refactor drops `_inside` from `station_map` and nothing fails. | Add traversal tests for every handler. Then check them by mutation: replace `_inside(...)` with a plain `os.path.join` and confirm the tests go red. |
| 6 | Low | PROBABLE | `_inside` followed by `open` | There is a time-of-check to time-of-use window. A path component can be swapped for a symlink between `realpath` and `open`. | This only matters if an attacker can write inside `docs/maps`. That is unlikely but possible if maps are uploaded. | Open with `O_NOFOLLOW` or `openat` relative to a directory file descriptor, or make the docs tree read-only to anything request-driven. |
| 7 | Low | CONFIRMED | `f.read()` in all three | The whole file is loaded into memory per request. | Large manuals or maps under concurrent load cause memory spikes. | Stream the file with the framework's file-response helper. |

## What holds up

- `_inside` is correctly built. It resolves both base and target with `realpath`, compares against `base + os.sep` (which defeats the sibling-prefix trick), and handles symlinks, absolute names and empty names.
- `station_map` is safe from traversal.
- Reading `DOCS` from the environment with a sane default is fine.

## Unverified claims

- **"Names come from the request".** I could not check how the framework decodes names: URL decoding, double-encoding, or whether `/` is allowed in a path parameter. Check by reading the route definitions. The fix in #1 and #2 makes this irrelevant to traversal.
- **Process permissions.** How much damage #1 and #2 cause depends on the service user's read access. Check with `id` and `ls -l` under the deploy user.
- **Authentication upstream.** I could not determine whether any authentication sits in front of these routes. Check the middleware and route decorators.

## Questions for the author

1. Is the receipt download restricted to the rider who owns it, and where is that enforced? If nothing enforces it, #3 becomes Critical.
2. Why do `receipt` and `manual` not use `_inside`? Was this an oversight, or is there a framework-level guard I cannot see?
3. Can anything write into `docs/` at runtime, for example uploaded maps? The answer sets the severity of #6.

## Decision-maker summary

Do not ship. The receipt and manual downloads let anyone read arbitrary server files. Route all three through the existing `_inside` guard, add per-rider authorisation for receipts, and add traversal tests before release. If this ships as is, assume server secrets and rider receipts are exposed from the first day.

## Owner summary

Two of the three new download links can be tricked into handing out any file on the server, including passwords and other riders' receipts. The station map download is already protected properly, and the same protection needs to be applied to the other two. Receipts also need a check that riders can only download their own.

```json
{
  "verdict": "REWORK",
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "location": "downloads.py receipt(): open(os.path.join(DOCS, \"receipts\", name), \"rb\")", "scenario": "name='../../app/.env' or '/etc/passwd' escapes the receipts folder (absolute name discards the base in os.path.join); the server file is returned", "fix": "Use _inside(\"receipts\", name); add tests asserting ValueError for ../ and absolute names and an outward symlink"},
    {"severity": "Critical", "evidence_level": "CONFIRMED", "location": "downloads.py manual(): open(os.path.join(DOCS, \"manuals\", name), \"rb\")", "scenario": "manual('../../../etc/shadow') or manual('/etc/passwd') reads arbitrary files readable by the service user", "fix": "Use _inside(\"manuals\", name); make _inside the only path builder; same traversal tests"},
    {"severity": "High", "evidence_level": "PROBABLE", "location": "downloads.py receipt(), example name '2026-09-r1.pdf'", "scenario": "No ownership check; sequential names let any user enumerate and download every rider's receipts", "fix": "Scope receipts to the authenticated rider (per-rider folder or lookup) and return 404 otherwise; test cross-rider access"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "all three functions", "scenario": "Not wired as handlers; ValueError/FileNotFoundError/IsADirectoryError propagate as 500s, possibly leaking paths in stack traces", "fix": "Wrap in the site's handler layer, map errors to 400/404, set Content-Type/Content-Disposition"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "no tests supplied", "scenario": "Nothing guards the traversal check; removing _inside from station_map would go unnoticed", "fix": "Add per-handler traversal tests; confirm by mutating _inside to a plain join and seeing them fail"},
    {"severity": "Low", "evidence_level": "PROBABLE", "location": "_inside() then open() in station_map", "scenario": "Symlink swapped in docs/maps between realpath check and open, if an attacker can write there", "fix": "Open with O_NOFOLLOW/openat on a directory fd, or keep docs read-only to request-driven code"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "location": "f.read() in all three", "scenario": "Large files read fully into memory per request cause memory spikes under load", "fix": "Stream via the framework's file-response helper"}
  ]
}
```