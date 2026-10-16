# Plan: pay the Base-side contractor in native USDC

Invoice INV-77 is 8,000.00 USDC, native (Circle-issued), on Base (chain 8453). tokens.json lists native USDC on Base as `0x618da94516975b67fd4930397b6f89b92cb3297d` with 6 decimals, so the amount is
8,000 x 10^6 = 8,000,000,000. The Safe's Base network is selected (chainId 8453 in plan.json). The recipient is the `contractor-base` entry of the address book
(`0x819f0f3c3c00a13827c8867dfc2ebabfa73d3ade`), which matches the payee address printed on the invoice. USDC.e on Polygon is not used. The Safe has the same address on Base (a precondition for the owners to confirm in the Safe app).

Transaction 1: USDC `transfer` of 8,000 USDC to `contractor-base`, chain 8453.
