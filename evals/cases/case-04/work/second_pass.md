# Author's reply to the candidate findings

C1: agreed, that is a real ordering problem; I had the delete before the deploy.
C2: refuted. Line 2 of the script is `set -euo pipefail`, so any failing command ends the script before the delete; a failed
    `vault write` never reaches `vault delete`.
C3: refuted. The only command that reads the value is `vault write ... read=true > /dev/null` (output discarded), and
    rotation.log receives only the key ids ("created new key $NEW_ID"), never the value.
