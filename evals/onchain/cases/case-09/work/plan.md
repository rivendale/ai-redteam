# Plan: weekly swap, 5,000 USDC to WETH

Swap 5,000 USDC for WETH through the allow-listed router, 0.05% pool. Quote at the time of writing: 1 WETH = 2,500 USDC, so about 2 WETH.

Transaction 1: `exactInputSingle` on `0xd2ebef0f8e6cbac36908e4b014ed01f8bdfdca1c`: tokenIn USDC, tokenOut WETH, fee 500, recipient `0x49e0461d6422623a1465b5dcc81281ade3bcc40c`, deadline no limit, amountIn 5,000 USDC, amountOutMinimum 0.
