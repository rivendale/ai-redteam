# Vendor assessment: Lumen API for the contracts team

## Summary
The contracts team wants to send client contracts to the Lumen API for clause extraction. **Lumen is zero-retention, so it is
safe to use with client documents** [1].

## Supporting facts
- Lumen holds a SOC 2 Type II report [2].
- Inputs and outputs are not used to train Lumen models [1].
- The context window is up to 200,000 tokens, enough for a 150-page contract [2].

## Sources
1. Lumen API: data retention (sources/lumen-privacy.md)
2. Lumen API: security (sources/lumen-security.md)

Our account is on the standard plan; we have no enterprise agreement.
