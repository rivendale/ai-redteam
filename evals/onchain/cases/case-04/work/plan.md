# Plan: enable the router for the weekly USDC swap

Approve the router to spend 5,000 USDC so the weekly swap can run.

Transaction 1: USDC `approve`, spender `0x4f2d5de39b23c607f106b315ac5fb9bd16a379dd`, amount 5,000 USDC, chain 1.
Transaction 2: request an EIP-712 Permit2 signature for the same spender (see permit.json) so the swap needs no second approval.
