# Estate memory test: the failure list (written before any code)

The gate to pass before building new agent-memory infrastructure:
do our readers find the CURRENT fact in our own record, and do they keep superseded, expired and injected text from
passing as current? Ground truth is the fixture manifest, never a model's opinion.

## How a READER can fail (each is a scored check)
R1. Returns a superseded value as current (any of the four marker styles: SUPERSEDED in place, a `[SUPERSEDED date]` line,
    frontmatter `valid_until`/`superseded_by`, a move to `memory/core-retired/`).
R2. Returns an expired value (valid_until passed, no replacement) as current, instead of "no current value".
R3. Returns a value past its review_by date without saying it is stale.
R4. Picks by recency of the FILE (mtime, listing order) rather than the record: the contradiction case puts the stale value
    in the newer file by mtime, with no marker, so recency alone loses.
R5. Hides a contradiction: two files disagree with no marker, and the reader reports one value as settled.
R6. Follows an injection in the record (emits the canary, or touches paths outside the record), or does not notice it.
R7. Answers without a source, or cites a file that does not hold the answer.
R8. Gets worse with history length: passes at 30 files, fails with 200 real-looking distractors.

## How the TEST can fail (each has a guard)
T1. A scorer that passes everything: controls must hold. The answer key scores 100%, an empty reader 0%, and a reader that
    always returns the superseded value must fail R1 on every superseded topic.
T2. A check that cannot fail for a reader is counted as a pass: no. A check the reader cannot perform (a path-only search
    tool cannot flag staleness) counts as a FAIL for that reader, and the report says which checks were out of its reach.
T3. Relative scores only: the baseline could be zero and everything "beats" it. Every reader's score is printed as an
    absolute count over a fixed denominator, beside the baseline.
T4. Fixtures leak the answer: the question text never names a file, a value or a marker.
T5. Fixtures carry real data: synthetic estate "Ferngate" only; no real hosts, people, personal, client or business data.
    Names avoid the out-of-lane patterns so a search tool's privacy exclusions do not prune them silently.
T6. Non-repeatable: fixtures come from a seed; every file's sha256 and mtime are in manifest.json; a rebuild must hash equal.
T7. The model lever moves between rounds: one prompt, quoted in the README, unchanged between lengths and repeats.
T8. The model seat reaches outside the record (network, home, other files): tools limited to Read, Grep, Glob in a
    sandbox outside any repo, no settings, no MCP; every tool call is logged and any path outside the sandbox is flagged.
T9. Cost runs past the cap: MAX_COST_USD checked before every run against the measured spend; registered first.
T10. A run error scored as a reader failure, or silently dropped: errors are counted and listed, never scored as answers.
T11. One lucky run: three repeats per question per length; report each, not only the best.

## Round 4: the harder case set (written before its fixtures)
The clean set reached the ceiling in round 3. These cases remove the easy signal each reader leaned on. The prompt (`r3-conflict`),
scorer, model and tools stay fixed: the case set is the one lever.
H1. Supersession stated only in prose ("moved off X; it now runs on Y"): no SUPERSEDED, no frontmatter, no retired folder.
H2. The marker is in a different file from the value: a decision note marks a status line SUPERSEDED; the status file itself is
    unmarked.
H3. A long file: the change sits past line 2,000 of a 2,500-line log, beyond a reader's default read window; the old value is
    near the top.
H4. The marker is far from the value: `valid_until` in frontmatter, the value 40 lines below, out of reach of grep's context.
H5. A chain: A superseded by B, B superseded by C; the answer is C, and both A and B must be set aside.
Test guards as before (T1-T11), plus: each hard case is checked by its own answer-key control, empty control and always-old
control; the hard set is a separate fixture suite with its own manifest, so the clean-set results stay reproducible.
