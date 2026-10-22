# Patch record: code-hosting server, critical advisory of 2026-10-21

Owner: platform engineer. Ticket PATCH-77.

## What was done
On 2026-10-21 the platform engineer ran the package update on the host. The package manager shows the code-hosting package at the fixed version (19.5.1)
as installed. The ticket was closed as **patched**.

## Exposure
The server is reachable only from the office network and the VPN.

## Inventory
| Component | Version |
|---|---|
| code host (installed package) | 19.5.1 |
| database | 16.4 |

## Follow-up
None. Credentials were not rotated because the server was never exposed to the internet.
