VERDICT: try. The cache is MIT-licensed, short, and could be borrowed without adding a dependency, which matches goal 2 (CI minutes). But nothing shows our docs build spends real time walking directories, or walks the same tree twice in one CI run, so measure that before borrowing.

WHAT IT IS: example-org/pathglob2, default branch `main` (no commit sha captured), MIT, 1,200 stars, last push 2026-09-27, not archived. I read this from the saved snapshot (snapshot.md, meta.json) captured 2026-10-08, not live. `pathglob2/cache.py` is not in the snapshot, so I have not read the cache code itself, only the README's description of it.

CLAIMS CHECKED:
- **"License: MIT"**: meta.json (read live at capture) agrees. CONFIRMED. *Load-bearing*: MIT is on our list for code we vendor in.
- **The cache is keyed by each directory's modification time, so a second walk of an unchanged tree reads no directories**: this is the README's own description; the code is not in the snapshot. PROBABLE. *Load-bearing*: this is the idea we would borrow.
- **"The cache is 60 lines in `pathglob2/cache.py`"**: stated in the README, file not captured. PROBABLE. *Load-bearing*: a small size is what makes borrowing cheap.
- **"5x faster on trees over 10,000 files"**: a README benchmark with a script (bench/run.py), but no method, hardware or numbers. It also doesn't say whether the 5x is for the first walk or a second walk with the cache filled. PROBABLE as a measurement of something; what it measures is unclear. Not load-bearing.
- **(Sender) "could speed up our docs build"**: split into two parts.
  - "Our docs build walks large trees": UNVERIFIED. The context file doesn't describe the docs build.
  - "So the cache would speed it up": UNVERIFIED. The cache only helps on a *second* walk of an unchanged tree. Each CI run starts on a fresh runner with a fresh checkout, and git sets file times at checkout, so saving the cache between runs probably doesn't help. It pays off only if one build walks the same tree several times. *Load-bearing*: the trial below settles it.
- **"Drop-in replacement for `glob.glob`"**, **"No dependencies. No network access."**: README claims, not checked. PROBABLE/UNVERIFIED. Not load-bearing, since we are borrowing the idea, not the package.

FIT:
- **Goal:** goal 2, "Cut CI minutes by a third this quarter", but only if directory walks are a meaningful share of the docs build.
- **Overlap:** nothing we use caches directory listings. lychee checks links and doesn't affect build time here.
- **Burden:** about 60 lines of our own code to own, test and keep correct. No new service, account or dependency, which honors the sender's "no another dependency".
- **Cost:** free. MIT, open source, no tier. Checked 2026-10-08 from the snapshot.
- **Risks:**
  - The MIT notice must be kept if we copy code rather than reimplement it.
  - Directory mtime only changes when entries are added, removed or renamed, not when a file's contents change. Time resolution also varies by filesystem, so a change within the same tick can be missed. Our version needs a test for this.
  - The benefit may be zero in CI, where every run starts cold (see above).
  - Project health looks fine: active, not archived.

NEXT ACTION: Profile one docs build in CI and record (a) the share of wall time spent listing or globbing directories and (b) how many times the same tree is walked per run.
- **Owner:** operator, or whoever owns the docs build.
- **Done when:** both numbers are written down for one representative build.
- **Stop condition:** stop and skip if directory walking is under about 10% of build time, or if each tree is walked only once per run.
- **Hand-off:** if it passes, `glean` on `pathglob2/cache.py`, reading it and reimplementing (or copying with the MIT notice), not installing it.

CONFIDENCE: medium. The item is resolved from a dated snapshot and the context file is present. Limits:
- The cache code itself was not in the snapshot.
- The benchmark method is not given.
- The claim that the docs build would benefit has no evidence yet, and the trial is what tests it.

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "repo",
           "identity": "example-org/pathglob2@main (sha not captured; MIT, 1,200 stars, last push 2026-09-27, not archived; snapshot 2026-10-08)",
           "resolved": true},
  "claims": [
    {"claim": "License: MIT", "evidence": "meta.json license field read live at capture matches README", "status": "CONFIRMED"},
    {"claim": "cache keyed by directory mtime, so a second walk of an unchanged tree reads no directories", "evidence": "README description; pathglob2/cache.py not in snapshot", "status": "PROBABLE"},
    {"claim": "the cache is 60 lines in pathglob2/cache.py", "evidence": "README statement; file not captured", "status": "PROBABLE"},
    {"claim": "5x faster on trees over 10,000 files", "evidence": "README benchmark with bench/run.py; no method, hardware, or cold-vs-warm cache stated", "status": "PROBABLE", "load_bearing": false},
    {"claim": "(sender) our docs build walks large directory trees", "evidence": "context file does not describe the docs build", "status": "UNVERIFIED"},
    {"claim": "(sender) so the cache could speed up our docs build", "evidence": "the cache only helps on a repeat walk; CI runners start cold and git checkout resets mtimes; no profile of our build", "status": "UNVERIFIED"},
    {"claim": "drop-in replacement for glob.glob", "evidence": "README statement only", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "no dependencies and no network access", "evidence": "README statement; code not in snapshot", "status": "PROBABLE", "load_bearing": false}
  ],
  "fit": {"goal": "Cut CI minutes by a third this quarter (goal 2), only if directory walks are a real share of the docs build",
          "overlap": "none found; nothing in use caches directory listings",
          "burden": "about 60 lines of our own code to own and test; no new dependency, service or account",
          "risks": ["MIT notice must be kept if code is copied rather than reimplemented",
                    "directory mtime misses content-only changes and same-tick changes on coarse-timestamp filesystems; needs a staleness test",
                    "benefit may be zero in CI because each run starts with a cold cache and fresh checkout mtimes"],
          "cost": {"price": "free", "tier": "open source", "limits": "none", "terms": "MIT",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Profile one CI docs build: share of wall time spent listing/globbing directories, and how many times the same tree is walked per run",
                  "owner": "operator",
                  "done_when": "both numbers are recorded for one representative docs build",
                  "stop_condition": "stop and skip if directory walking is under about 10% of build time or each tree is walked only once per run",
                  "handoff": "glean"},
  "confidence": "medium",
  "context_file": "present"
}
```