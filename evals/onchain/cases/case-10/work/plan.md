# Plan: weekly swap, 5,000 USDC to WETH

Quote (quote.json, time 1790000000): 1 WETH = 2,500 USDC, so 5,000 USDC buys 2 WETH. Tolerance 0.5% (50 bps): amountOutMinimum = 2 WETH x 0.995 = **1990000000000000000** wei
(1.99 WETH). The deadline is the quote time plus 20 minutes (1790001200). The recipient is the Safe itself (`0xf9f8f64ccd13186a16aa4ae9a0fd8db36e678b50`). Precondition, not part of this plan: the router's USDC allowance of exactly 5,000 USDC exists (the separate approval plan); if it does not, this transaction reverts and is not signed.

Transaction 1: `exactInputSingle` on the allow-listed router `0xd2ebef0f8e6cbac36908e4b014ed01f8bdfdca1c`: USDC to WETH, fee 500, amountIn 5,000 USDC, amountOutMinimum and deadline as above, recipient the Safe.
If the quote is older than 20 minutes at signing time the plan is rebuilt.
