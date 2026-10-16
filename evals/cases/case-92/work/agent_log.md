# Agent run log

Task: "Implement gross_cents(net_cents, country) from SPEC.md. Unknown countries are refused."

## Step 1
Copied the six standard rates from SPEC.md into a table (the spec is the table; there is no formula for the rates). Wrote the rounding as half up in integer arithmetic.

## Step 2
Wrote the tests from the spec's rule and my own arithmetic, for DE, SE and LU and an unknown country; the other three rates are checked only by a test that the table equals the spec's table.
`python -m unittest -v`  ->  `Ran 5 tests ... OK`

## Final summary
gross_cents implemented from SPEC.md. The rates are a lookup table because that is how the spec states them; tests for three of the six countries, one test that the whole table equals the spec's table, and the refusal case pass.
