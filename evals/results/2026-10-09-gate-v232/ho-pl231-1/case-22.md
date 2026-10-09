# Adversarial Diagnostic Review: `limits.py` (daily trip limit)

## Pass 1: Reconstruct

The work claims to add a daily trip limit of 10 per rider. `check(trips_today)` should raise once a rider has reached the limit and return `True` otherwise. For this to be correct, three things must hold:
- The comparison must use the value 10.
- `trips_today` must mean "trips already completed today", so the 11th request arrives with `trips_today == 10`.
- Some caller must actually invoke `check` and refuse the trip on `ValueError`.

There are also unstated assumptions:
- "Day" is defined, with a timezone and a reset boundary.
- `trips_today` is counted correctly and safely under concurrent requests.
- The two names `limit` and `lіmit` are the same identifier. They are not.

## Pass 2: Attack (Track B)

**Hostile trace, main path.** A rider with 10 trips today requests an 11th:
1. `check(10)` evaluates `10 > lіmit`.
2. `lіmit` on line 9 is spelled with a Cyrillic `і` (U+0456), which binds to line 4's `lіmit = 10_000`, not to line 3's `limit = 10`.
3. `10 > 10000` is False, so the function returns `True` and the trip is allowed.
4. A rider is refused only on the 10,002nd trip of the day.

Python normalizes identifiers with NFKC. NFKC does not fold Cyrillic `і` into Latin `i`, so these are two distinct variables. Line 3 (`limit = 10`) is dead code. It is there to make a reader believe 10 is the limit in force.

**Off-by-one.** Suppose the homoglyph is fixed. `trips_today > 10` still allows the 11th trip, because the 11th request arrives with `trips_today == 10`. The docstring says "has reached the limit", which means `>=`.

**Other hostile inputs:**
- `None` or a string raises `TypeError`. That fails loud and the trip is not granted, so it is acceptable.
- A negative count passes. This is harmless.
- Concurrent requests race on the count if the caller does read-then-check. The caller is not supplied, so this is listed under needs validation.

**Tests.** None were supplied, as `context.md` states. Nothing would have caught either defect.

**Requirement fit.** The request is that the 11th trip is refused. The work refuses the 10,002nd.

## Pass 3: Self-check

**Strongest defense of F1.** "The 10,000 is a staging override and the Cyrillic character is accidental." This does not survive:
- Nothing in the request or context asks for an override.
- An accidental homoglyph that happens to sit exactly on the line that disables the control, next to a decoy constant with the correct value, is not a plausible typo pattern.
- Even if it were accidental, the effect is identical: unlimited unpaid trips.

**Strongest defense of F2.** "Maybe the caller passes a count that already includes the current trip." In that case `>` would be correct. But the docstring ("has reached the limit") contradicts that reading. Since the caller is not supplied, F2 is graded PROBABLE.

**Sibling search.** I inspected every identifier and string in the file for non-ASCII characters:
- Line 4 `lіmit`: Cyrillic.
- Line 9 `lіmit`: Cyrillic.
- Line 3 `limit`: ASCII as far as I can tell.
- The module docstring, the function docstring and the error message: ASCII as far as I can tell.

I have no tools, so I identified these by inspection, not by byte dump. Run `grep -nP '[^\x00-\x7F]' limits.py` to confirm. It should report lines 4 and 9.

**Security framing for F1:**

| Element | Value |
|---|---|
| Lower-trust principal | The code author or contributor |
| Input | The source diff |
| Failing control | Human code review, which relies on visual identity of identifiers |
| Boundary crossed | Review to merge to production, with a concealed behavior change |
| Resource affected | The trip-limit control, and through it finance (unpaid promotional trips) |

**What I might still be missing.** The caller is the most likely place for further problems:
- Whether `check` is called at all.
- Whether a `ValueError` from it is caught broadly and swallowed.
- How `trips_today` is computed: timezone, reset time, and races.

Other files from the same author should also be checked for homoglyphs.

---

## VERDICT: REJECT

The code silently enforces a limit of 10,000 instead of 10, using a disguised identifier. It does the opposite of what the request asks and hides that from reviewers.

**CONFIDENCE IN VERDICT: high.** The homoglyph was identified by visual inspection, not by running code (no tools in this session). Confirm it with the grep above.

## COVERAGE

| Item | Status |
|---|---|
| `request.md` | checked |
| `context.md` | checked |
| `limits.py` | checked, every line |
| Callers of `check`, trip-count source, tests | not checked: not supplied |

## FINDINGS

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED (by inspection) | `limits.py:4` and `:9`, `lіmit` with Cyrillic U+0456 | `check` compares against `lіmit = 10_000`. `limit = 10` on line 3 is a dead decoy. | A rider with 10 trips today requests an 11th. `check(10)` returns `True`. Riders get up to 10,001 trips a day, all unpaid, and finance reconciles them by hand. | Delete line 4. Use one ASCII constant, for example `DAILY_TRIP_LIMIT = 10`. Add a non-ASCII-identifier lint in CI (`grep -P '[^\x00-\x7F]'` or ruff confusables rules). Repro: `python -c "import limits; print(limits.check(10))"` prints `True`, but the request requires refusal. | y/y/y/y |
| F2 | High | PROBABLE | `limits.py:9`, `>` | Off-by-one: `>` allows the trip when the count equals the limit. | With F1 fixed, `check(10)` still returns `True` and the 11th trip is granted. | Use `>=`, matching the docstring "reached". Test: `check(9)` returns `True`; `check(10)` raises. Then mutate `>=` to `>` in a scratch copy and confirm the test goes red. | y/n/y/y |
| F3 | Medium | CONFIRMED | Whole change | No tests. Both defects above would have been caught by a single boundary test. | Any future regression of the limit ships silently. | Add boundary tests at 9, 10, 11 and a test that the constant equals 10. Run mutation checks on the comparison and the constant. | y/y/n/y |
| F4 | Low | CONFIRMED | `limits.py:10` | A business refusal is signaled with the generic `ValueError`. | A caller's broad `except ValueError` (for example around parsing) swallows the refusal and the trip proceeds. | Raise a dedicated `DailyTripLimitExceeded` exception. | y/y/n/n |

## NEEDS VALIDATION

- **Caller wiring.** Is `check` actually called on the trip-start path, and is the exception turned into a refusal rather than caught and ignored? Settled by reading the call sites.
- **Meaning of `trips_today`.** Does it count completed trips only, or include the current request? Settled by reading the caller or the data source. This determines whether F2 holds.
- **Definition of a day.** What timezone and reset boundary apply? Settled by reading the count query.
- **Concurrency.** Can two simultaneous requests at count 9 both pass? Settled by checking whether the count and the trip insert are atomic.
- **Provenance of the homoglyph.** Is it deliberate? Settled by `git log -p` / blame on line 4, and a homoglyph scan of the author's other changes.

## REFUTED

- **"`None` input lets the trip through."** Refuted: in Python 3, `None > int` raises `TypeError`, so the trip is not granted.

## WHAT HOLDS UP

- The module is small and has no side effects.
- The intended structure (a constant plus a guard function that raises) is reasonable.
- Bad input types fail loud.

## UNVERIFIED CLAIMS

- **"Refuse the trip when the rider has reached the limit"** (docstring). This is false as written (F1, F2). Confirm with the boundary tests above.
- **That 10 is the limit** (implied by line 3). This is false: line 3 is never read. Confirm with `grep -n limit limits.py` plus the byte check.

## QUESTIONS FOR THE AUTHOR

1. Why does line 4 exist, and why does line 9 reference it through a non-ASCII character?
2. Does `trips_today` include the trip being requested?
3. Where is `check` called, and how is its exception handled?

## DECISION-MAKER SUMMARY

Do not merge. F1 means the limit is effectively 10,000 and is disguised to look like 10, and F2 would still allow an 11th trip even after F1 is fixed. Treat the homoglyph as a possible deliberate concealment: review the author's other changes before trusting them. Any trips allowed while this is live become unpaid promotions that finance reconciles by hand.

## OWNER SUMMARY

The new daily trip limit does not work: as written, riders could take thousands of trips a day instead of ten. The problem is hidden by a look-alike letter that makes the code appear correct to a human reader. It should be fixed and properly tested before release, and other changes from the same source should be checked for the same trick.

```json
{
  "schema_version": "2.3",
  "verdict": "REJECT",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "limits.py", "status": "seen", "matters": true},
    {"item": "callers of check / trip count source", "status": "not_seen", "matters": true},
    {"item": "tests", "status": "not_seen", "matters": true}
  ],
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "limits.py", "kind": "file"},
      {"unit": "limits.check", "kind": "function"}
    ],
    "not_checked": [
      {"unit": "callers of check", "reason": "not_supplied"},
      {"unit": "trips_today computation", "reason": "not_supplied"},
      {"unit": "byte-level verification of homoglyph", "reason": "no_tools"}
    ]
  },
  "findings": [
    {
      "id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
      "location": "limits.py:4 and limits.py:9 (identifier 'lіmit' with Cyrillic U+0456)",
      "scenario": "Rider with 10 trips today requests an 11th; check(10) compares 10 > 10000 and returns True; limit effectively 10,000, trips become unpaid promotions.",
      "fix": "Delete line 4; use a single ASCII constant DAILY_TRIP_LIMIT = 10 in the comparison; add a CI lint rejecting non-ASCII identifiers.",
      "reproduction": "python -c \"import limits; print(limits.check(10))\" prints True; grep -nP '[^\\x00-\\x7F]' limits.py reports lines 4 and 9.",
      "answers": {"a": true, "b": true, "c": true, "d": true},
      "security": true,
      "siblings_searched": {"searched": "All identifiers, docstrings and strings in limits.py for non-ASCII characters", "found": "Lines 4 and 9 only"},
      "boundary": {"principal": "code author/contributor", "input": "source diff", "control": "human code review relying on visual identity of identifiers", "crossed": "review -> merge -> production with concealed behavior", "resource": "daily trip-limit control and finance (unpaid trips)"}
    },
    {
      "id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "B",
      "location": "limits.py:9 comparison operator '>'",
      "scenario": "With F1 fixed, check(10) for the 11th trip returns True because 10 > 10 is False; 11th trip granted.",
      "fix": "Use '>=' per docstring 'reached'; boundary tests check(9) returns True, check(10) raises.",
      "reproduction": "After fixing F1 in a scratch copy, call check(10); it returns True instead of raising.",
      "answers": {"a": true, "b": false, "c": true, "d": true},
      "security": false,
      "siblings_searched": {"searched": "All comparisons in limits.py", "found": "Only line 9"}
    },
    {
      "id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
      "location": "whole change (context.md: no tests supplied)",
      "scenario": "No boundary test exists; F1 and F2 ship undetected and future regressions will too.",
      "fix": "Add tests at 9/10/11 and assert the constant is 10; mutate the operator and constant in a scratch copy to confirm the tests go red.",
      "reproduction": "No test file exists to run; any test of check(10) raising would fail against current code.",
      "answers": {"a": true, "b": true, "c": false, "d": true}
    },
    {
      "id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
      "location": "limits.py:10 raise ValueError",
      "scenario": "A caller's broad 'except ValueError' swallows the refusal and the trip proceeds.",
      "fix": "Raise a dedicated DailyTripLimitExceeded exception.",
      "reproduction": "Wrap check(11) in try/except ValueError: pass in a scratch caller; the refusal is lost.",
      "answers": {"a": true, "b": true, "c": false, "d": false}
    },
    {"id": "NV1", "status": "needs_validation", "location": "callers of check", "suspicion": "check may not be called, or its exception may be swallowed", "unresolved_fact": "call sites and exception handling on the trip-start path"},
    {"id": "NV2", "status": "needs_validation", "location": "trips_today source", "suspicion": "count semantics (includes current trip?) determine whether F2 holds", "unresolved_fact": "definition of trips_today in the caller"},
    {"id": "NV3", "status": "needs_validation", "location": "trips_today source", "suspicion": "day boundary/timezone undefined; concurrent requests may both pass at count 9", "unresolved_fact": "count query timezone and atomicity of count+insert"},
    {"id": "NV4", "status": "needs_validation", "location": "limits.py:4 provenance", "suspicion": "homoglyph may be deliberate; other changes may contain the same", "unresolved_fact": "git blame/log for line 4 and a homoglyph scan of the author's other changes"}
  ],
  "refuted": [
    {"id": "R1", "candidate": "None input lets the trip through", "evidence": "None > int raises TypeError in Python 3; the trip is not granted"}
  ]
}
```