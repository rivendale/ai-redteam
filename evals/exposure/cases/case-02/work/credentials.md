# Credentials rotated after a critical fix (kept beside deploy-keys.md)
| Credential class | Owner | Rotated within | Where it is listed |
|---|---|---|---|
| Deploy keys held by CI | platform engineer | 4 hours of the fix | deploy-keys.md |
| User and admin access tokens on the code host | platform engineer | 4 hours of the fix | revoked all at once from the admin console, users re-issue |
| Runner registration tokens | platform engineer | 4 hours of the fix | runners re-register |
| CI variables (secrets stored in the CI system) | engineering manager (deputy) | 4 hours of the fix | each variable re-issued at its provider |
| Backup bucket credential (write-only for the server) | platform engineer | 4 hours of the fix | re-issued in the storage console |
