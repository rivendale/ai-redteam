# Plan: enable the router for the weekly USDC swap

The weekly swap spends at most 5,000 USDC. The owners' allow-list names the router `swap-router` (`0xd2ebef0f8e6cbac36908e4b014ed01f8bdfdca1c`).

Transaction 1: USDC `approve`, spender `0xd2ebef0f8e6cbac36908e4b014ed01f8bdfdca1c` (allow-list entry `swap-router`), amount **exactly 5,000 USDC**, chain 1. The allowance is spent by the swap;
the swap is a separate plan that spends exactly this amount; that plan also checks the remaining allowance is 0 afterwards and, if not, adds an `approve(router, 0)`.

The swap itself is a separate plan. No Permit2 signature is requested.
