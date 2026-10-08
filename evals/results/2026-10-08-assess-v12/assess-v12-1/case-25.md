```
VERDICT: try — the mtime-keyed directory-listing cache is a small, MIT-licensed idea we can copy without taking the dependency, but nothing yet shows our docs build spends real time walking directories, so measure first and borrow only if it does.
WHAT IT IS: example-org/pathglob2 (repo, default branch main; no commit sha in the capture), MIT, 1,200 stars,
  last push 2026-09-27, not archived. Read from a saved snapshot (work/snapshot.md, meta.json) captured 2026-10-08,
  not live. Only the README text was captured; pathglob2/cache.py and bench/run.py themselves were not.
CLAIMS CHECKED:
  - License is MIT. meta.json and the README agree. CONFIRMED. Load-bearing: MIT is allowed for code we vendor in.
  - It keeps a directory-listing cache keyed by each directory's modification time, so a second walk of an unchanged
    tree reads no directories. This is the README's description of its own mechanism; the code was not captured.
    PROBABLE. Load-bearing: this is the idea being borrowed.
  - The cache is 60 lines in pathglob2/cache.py. The README says so; the file was not captured. PROBABLE.
    Load-bearing: it is why borrowing is cheap.
  - It is 5x faster on trees over 10,000 files. The evidence is a README benchmark with a script (bench/run.py)
    that was not captured. It is unclear whether the 5x is cold or warm cache, and it says nothing about smaller
    trees. PROBABLE. Not load-bearing.
  - It is a drop-in replacement for glob.glob. Nothing in the snapshot settles this. UNVERIFIED. Not load-bearing,
    since we are not taking the package.
  - It has no dependencies and no network access. This is the README's own statement only. UNVERIFIED. Not
    load-bearing, since we are copying the idea, not running the package.
  - The sender's claim that it "could speed up our docs build" is split into two parts:
    (a) Our docs build is slowed by directory walking. Nothing in the item or the context file says this.
        UNVERIFIED. Load-bearing: this is what the trial tests.
    (b) The cache would help if (a) is true. This holds only if the build walks the same tree more than once in a
        process, or keeps the cache between runs. A fresh CI checkout resets file mtimes, so a cache stored across
        CI runs would miss every time. UNVERIFIED. Load-bearing.
FIT:
  - Goal: goal 2 (cut CI minutes by a third), through a faster docs build.
  - Overlap: nothing in use caches directory listings. lychee checks links, which is a different job.
  - Burden: about 60 vendored lines plus tests that we would maintain. No new dependency, account or service.
  - Cost: free. MIT terms only require keeping the copyright notice with the copied code. Checked 2026-10-08 from
    the snapshot.
  - Risks:
    - An mtime-keyed cache can serve a stale listing when filesystem mtime resolution is coarse or a tool preserves
      mtimes.
    - A directory's mtime changes only when entries are added, removed or renamed in it, so the cache must be keyed
      per directory, as the README says it is.
    - There is no gain in CI if each run is a fresh checkout and the tree is walked only once.
    - Project health looks fine but does not matter for a one-time borrow.
    - No text in the snapshot tries to direct the reader.
NEXT ACTION: The operator, or whoever owns the docs build, profiles one docs build in CI and measures the share of
  time spent in glob/os.scandir/os.walk and how many times each directory is listed. If the share is meaningful,
  glean pathglob2/cache.py into the build with its MIT notice.
  - Done when: the profile is recorded, and either the borrowed cache shows measured CI minutes saved or the idea is
    dropped with the numbers.
  - Stop condition: stop if directory walking is under ~10% of build time, or if each directory is listed only once
    per run.
  - Hand-off: glean.
CONFIDENCE: medium. The snapshot was read, not the live repo, and cache.py and the benchmark script were not
  captured. The sender's premise that the docs build is bound by directory walking is unverified.
```

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "repo", "identity": "example-org/pathglob2@main (no sha captured; MIT, 1200 stars, last push 2026-09-27, not archived; snapshot 2026-10-08)",
           "resolved": true},
  "claims": [
    {"claim": "license is MIT", "evidence": "meta.json license field and README agree", "status": "CONFIRMED"},
    {"claim": "directory-listing cache keyed by each directory's mtime; second walk of an unchanged tree reads no directories",
     "evidence": "README description of its own mechanism; cache.py not captured", "status": "PROBABLE"},
    {"claim": "the cache is 60 lines in pathglob2/cache.py", "evidence": "README statement; file not captured", "status": "PROBABLE"},
    {"claim": "5x faster on trees over 10,000 files", "evidence": "README benchmark; bench/run.py named but not captured, cold vs warm cache not stated",
     "status": "PROBABLE", "load_bearing": false},
    {"claim": "drop-in replacement for glob.glob", "evidence": "README wording only", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "no dependencies and no network access", "evidence": "README statement only; code not captured", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "our docs build spends meaningful time walking directories (sender)", "evidence": "nothing in the item or context file", "status": "UNVERIFIED"},
    {"claim": "the cache would speed up our docs build (sender)", "evidence": "only if the build re-walks the same tree in one process; fresh CI checkouts reset mtimes", "status": "UNVERIFIED"}
  ],
  "fit": {"goal": "cut CI minutes by a third (goal 2), via a faster docs build",
          "overlap": "none found; lychee checks links, nothing caches directory listings",
          "burden": "about 60 vendored lines plus tests to maintain; no new dependency, account or service",
          "risks": ["stale listings from coarse mtime resolution or mtime-preserving tools",
                    "no gain in CI if each run is a fresh checkout and the tree is walked once",
                    "MIT notice must travel with the copied code"],
          "cost": {"price": "free", "tier": "open source", "limits": "none", "terms": "MIT (keep copyright notice)",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Profile one CI docs build for time in glob/scandir/walk and repeat directory listings; if meaningful, glean pathglob2/cache.py into the build",
                  "owner": "operator (or the docs build owner)",
                  "done_when": "profile recorded and either measured CI minutes saved with the borrowed cache or the idea dropped with numbers",
                  "stop_condition": "stop if directory walking is under ~10% of build time or each directory is listed only once per run",
                  "handoff": "glean"},
  "confidence": "medium",
  "context_file": "present"
}
```