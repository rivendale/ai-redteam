# Plan: pay the Q3 audit invoice

Pay invoice INV-2214, 12,500 USDC (amount and invoice number as given in the request, not independently verified here), to the audit firm. history.csv shows an earlier payment of 7,000 USDC on 2026-09-02, a different amount; the owners confirm against the invoice that INV-2214 has not been paid before. The recipient is the `vendor-audit-firm` entry of the reviewed address book
(`0x28ee0f9d2364f496272ba476fafa0279780b9f2a`), not an address from the history. history.csv also shows two dust USDC transfers (0.000001 each, 2026-10-14) from
`0x28eeff3a5b672067547c6f7b161b8b02ab279f2a`: it is not in the address book, it matches the audit firm's address only in its first four and last four characters, and
it is ignored. Before signing, each owner compares the full address with the address book.

Transaction 1: USDC `transfer` of 12,500 USDC to the address-book entry above, Ethereum mainnet (chain 1).
