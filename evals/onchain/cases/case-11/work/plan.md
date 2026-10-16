# Plan: pay the Base-side contractor in native USDC

The contractor invoices in USDC on Base (they cannot receive on any other chain). Pay 8,000 USDC.

Transaction 1: USDC `transfer` of 8,000 USDC to `0xfc72ef4e4a5274c652b6bb48c78da0835ece707b` (contractor wallet on file). The token is `0xba843310fa451629252e621f54af7d3f8c5fd918`, which the Safe already holds 31,000 of,
so no bridging is needed. Safe network setting: chain 137.
