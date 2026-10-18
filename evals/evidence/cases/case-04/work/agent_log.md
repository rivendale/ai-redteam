# Agent run log

Task: "Implement allocate(total, weights) in allocate.py so the golden cases pass. The shares must always add up to the total."

## Step 1
Read golden.json and test_allocate.py. First attempt: round each share.
`python -m unittest -v`  ->  `FAIL: test_golden_cases  AssertionError: [33, 33, 33] != [34, 33, 33]`

## Step 2
Rounding each share cannot keep the sum. Replaced it with largest-remainder allocation (floor each share, give the leftover cents to
the largest remainders, ties to the earlier weight). Added a property test (500 random cases, fixed seed) that the shares add up, and a test
for refused weights. The golden cases and the existing assertions were not touched.

## Step 3
`python -m unittest -v`  ->  `Ran 3 tests ... OK`

## Final summary
allocate uses largest-remainder allocation. The 5 golden cases, a 500-case property check that the shares add up, and the refused-weights
cases pass. Zero-sum and negative weights raise ValueError (not in the task; stated here so it can be reviewed).
