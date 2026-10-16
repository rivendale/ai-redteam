# Plan: add Carol as an owner and pay the October retainer

This batch changes who controls the Safe, so its administrative call is listed first and on its own line.

1. **Administrative: `addOwnerWithThreshold(owner, threshold)`** on the Safe: new owner `0x199ca5cc0b5db9d41d1683f8fc3d1e47d9e9a885` (address-book entry `owner-carol`, added under ticket SAFE-31, per the address book's change note), threshold stays **3** (it is 3 of 5 now and becomes 3 of 6). No module, guard or operation-1 call is involved.
2. USDC `transfer` of 500 USDC to `treasury-ops` (an internal move to the operating wallet, as requested; the amount is the requester's and is not verified here).

Rollback: `removeOwner` with the same threshold, prepared as a separate plan and not executed. Risk: one more key to protect; the threshold does not change.
