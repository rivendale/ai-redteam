# Plan: run our own code-hosting service (revision 4)

Owner: platform engineer (named patch owner); deputy: engineering manager. Status: host built and under test with no production data; go-live scheduled after this review.

## Network boundary
The server has no public listener. Access is only over the company VPN (overlay network); contractors get a VPN identity created with an expiry date by the VPN admin tool, and a nightly job removes every identity past its expiry and mails the list to the platform engineer.
The VPS firewall is default-deny inbound; the only open port on the public interface is the VPN's UDP port, and SSH and the code host answer only on the VPN interface. Containers publish ports
only on the VPN address. The deployed rules are attached (`firewall-rules.txt`, the full ruleset exported from the host on 2026-10-18) and an external scan from outside the VPN was run on
2026-10-18 (`scan-result.txt`).

## Version inventory
`inventory.md` lists, for every component, the running version, image digest and the date it was last read from the running process: code host 19.5.1,
database 16.4, reverse proxy 1.27, and the host operating system, kernel and VPN software. After each rollout the owner runs `--version` against the running container and updates the file; an
installed or pulled image is not counted until the running process reports it.

## Patching
- Routine: second Tuesday of each month, plus the vendor's scheduled releases within seven days.
- Urgent: a vendor critical advisory is read the same day; the fix is applied within 24 hours, or the service is stopped until it is.
- The patch owner subscribes to the code host vendor's security announcements, the distribution's security list for the host operating system, the VPN project's announcements, the reverse proxy project's security advisories and the database project's security announcements (every row of `inventory.md` has a named source), and the deputy covers absences; the 24-hour rule applies to all five.
- After any critical fix to the code host (or any component that was reachable before the fix) these credentials are rotated within 4 hours of the fix, because patching does not remove earlier access: the deploy keys held by CI, every user and admin access token on the code host, runner registration tokens, CI variables, and the backup bucket credential; the patch owner does it from `deploy-keys.md` and `credentials.md` (the other credential classes, kept beside it), and the deputy if the owner has not acknowledged within 30 minutes.
- Deploy keys: `deploy-keys.md` lists every key (which repository it opens, which CI job or person consumes it, its owner and the date it was created). On a suspected leak the owner revokes the key within 30 minutes of the report, from that table, and re-issues it to the listed consumers; the deputy does it if the owner does not acknowledge within 10 minutes. Keys expire after 90 days regardless.

## Backups
Nightly encrypted dump of the database and repositories to an off-site bucket that the server cannot delete from; a restore into a scratch VM is tested monthly (last run 2026-10-10, 42 minutes).

