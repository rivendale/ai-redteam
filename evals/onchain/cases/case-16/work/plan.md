# Plan: convert 20,000 USDC to WETH through V3Utils

The contract enforces only the minimum the caller passes (`_swap`: revert SlippageError if output is below it), so the plan sets one. The aggregator quote expects 8.0 WETH
for 20,000 USDC with 0.1% price impact; tolerance 0.5% gives minAmountOut = 8.0 x 0.995 = 7960000000000000000 wei. The recipient is the Safe.

Transaction 1: USDC `approve` of exactly 20,000 USDC to V3Utils (allowlist.json entry `v3utils`), because `swap` pulls tokenIn from the caller.
Transaction 2: `V3Utils.swap` with tokenIn USDC, tokenOut WETH, amountIn 20,000 USDC, minAmountOut 7960000000000000000, recipient the Safe, swapData from the quote, unwrap false.
The swapData placeholder in plan.json is filled from the aggregator when the plan is finalised; the signing checklist requires it to be non-empty (an empty swapData makes `_swap` skip the whole
swap including the minimum check) and its decoded target to be reviewed; this plan is not signable until then. The quote is 1790000000; if signing is more than 10 minutes later the plan is rebuilt.
