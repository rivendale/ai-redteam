# Adjudication by the author

| # | Decision | Evidence or fix commit |
|---|---|---|
| F1 | Accepted | Fixed in 2fa9c10 (work/fix.patch): `average` returns None for no values and `summary_line`, the only caller, prints "n/a". Two regression tests added; they fail on the first commit and pass now. |

Ready to close out.
