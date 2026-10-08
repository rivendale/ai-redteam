# Adjudication by the author

| # | Decision | Evidence or fix commit |
|---|---|---|
| F1 | Accepted | Fixed in c04e6b8 (work/fix.patch): the check is now `used < limit`, and I removed the early return for 0 as dead code. `test_boundary` fails on the first commit and passes now. |

Ready to close out.
