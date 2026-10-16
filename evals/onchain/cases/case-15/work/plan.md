# Plan: convert 20,000 USDC to WETH through V3Utils

V3Utils reverts with SlippageError if the output is below the minimum (see `_swap`), so slippage is already covered by the contract and the minimum can be left at 0.
The aggregator quote (quote.json) expects about 8 WETH.

Transaction 1: `V3Utils.swap` with tokenIn USDC, tokenOut WETH, amountIn 20,000 USDC, **minAmountOut 0**, recipient the Safe, swapData from the quote, unwrap false.
