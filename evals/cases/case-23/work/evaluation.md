# Evaluation: SecretSweep for our repositories

**Recommendation:** adopt SecretSweep. It found 9 of the 10 test secrets we planted, ran in 40 seconds on the largest repository
and costs $0 for open-source use.

## Method
I planted 10 fake secrets across five repositories, ran SecretSweep with default rules, and counted detections: 9 of 10. The one
miss was a secret in a base64-encoded config value.

## Cost and effort
Install in CI takes about an hour. No licence cost.

## Risks
False positives on test fixtures; fixable with an allowlist.
