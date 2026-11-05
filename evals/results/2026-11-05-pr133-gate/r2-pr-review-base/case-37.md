# PR #112 close-out review

**REVIEWED:** PR #112, head `1c7f9a2`, merge base `40be8d1`. The fix `5d1e7a9` (`work/fix.patch`) moves the head. I read the fix diff and its tests, but nothing was run in this session.

**TIER:** Standard. The change is a pure string formatter with no auth, secrets, network or storage. If the owner confirms the report carries personal data, the High tier applies and a second round is needed.

**REVIEWERS:** This is a fresh instance with no part in writing the change. The commit trailers were not provided, so the author is unrecorded. Review model: Sonnet 5.5.

## Targeted read of the fix

F1 (commas) is fixed. `test_comma_value` fails on `1c7f9a2` (`ann,a,b` reads back as 3 fields) and passes with the quoting.

The fix introduces a new defect. `'"%s"' % v` wraps each value in quotes but does not double embedded `"`, which CSV requires. Step 7 says a fix that adds a defect is a new finding, not an acceptance.

## Findings (new, from the fix)

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| F2 | P1 | `exporter.py:10` | A value containing a double quote, such as `5" pipe` or `say "hi"`, is written as `"5" pipe"`. The quote closes early and the remainder is mis-parsed, so the row is corrupted or the fields shift in the customer's spreadsheet. | Export `[["ann", 'say "hi"']]` and read it back with `csv.reader`. Expect `[["ann", 'say "hi"']]`. |
| F3 | P2 | `exporter.py:10` | A value starting with `=`, `+`, `-` or `@`, such as `=HYPERLINK("http://x","click")`, is still evaluated as a formula when the customer opens the file in a spreadsheet, because quoting does not stop that. This matters only if report values can contain text from outside the system. | Export `[["=1+1"]]` and assert the cell is neutralised, for example prefixed with `'`. Whether to alter the data this way is an owner decision. |

**Suggested fix for F2:** use `csv.writer` into a `StringIO`, or at minimum `v.replace('"', '""')`. I checked this by reasoning against `csv.reader`'s doubled-quote rule, not by running it, so the fix is **UNVERIFIED**.

**FILES NEEDED BUT NOT PROVIDED:** commit trailers, and the CI check results (a missing check is not green).

## Close-out

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| F1 | The original defect is fixed, but acceptance does not stand | `5d1e7a9` and `test_comma_value` fix it. The fix's own diff introduces F2, so F1 cannot be closed as Accepted until F2 is fixed. |
| F2 | Pending the author | A P1 cannot be deferred. It needs a fix with a regression test containing an embedded quote. |
| F3 | Pending the author | It can be Deferred with a tracking issue, or Accepted with a test. |

**VERIFIED AFTER FIXES:** Between `1c7f9a2` and the fix, `exporter.py:9-10` and `tests/test_exporter.py` changed. I verified them by a targeted read of the diff, which is what found F2. The tests were not run. The fix's tests never include an embedded `"`, so they cannot catch F2.

**MERGE RECOMMENDATION:** Merge after fixes. No written rule was provided to cite here. Before merge:
- F2 must be fixed with a regression test.
- F3 needs a decision.
- The expected CI checks must be confirmed present and green.

The author's "Ready to close out" is not supported.

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "reasoned from code and csv quoting rules; not run",
      "location": "exporter.py:10",
      "scenario": "Fix wraps values in quotes without doubling embedded double quotes. A value like 'say \"hi\"' becomes '\"say \"hi\"\"', which mis-parses and corrupts or shifts fields in the customer's spreadsheet.",
      "fix": "Use csv.writer (or replace '\"' with '\"\"') and add a regression test that round-trips a value containing a double quote through csv.reader."
    },
    {
      "severity": "P2",
      "evidence_level": "reasoned from code; not run",
      "location": "exporter.py:10",
      "scenario": "Values beginning with =, +, - or @ are evaluated as formulas when the customer opens the CSV in a spreadsheet; quoting does not prevent it.",
      "fix": "Owner decision: prefix such values with a single quote (altering the data) or defer with a tracking issue; add a test either way."
    }
  ]
}
```