# Self-hosted exposure lens: failures registered first

Apply to self-hosted services, especially admin consoles and code-hosting surfaces.

1. An internet-reachable admin/code-hosting surface is accepted because it has a login page or TLS.
2. A claim of private-only reachability is accepted without the deployed ingress/firewall boundary.
3. The plan has no named patch owner, response cadence or urgent-advisory path.
4. A service has no inventory of running versions, images, embedded runtimes or last verification time.
5. The reviewer equates package installation with the running process receiving the fixed version.
6. A private service with enforced ingress and a complete patch plan receives blanket alarm findings.
7. Unknown inventory or missing access is reported as confirmed exploitation or automatically Critical.
8. A patch is treated as proof that earlier compromise or credential exposure has been removed.
9. Unconfirmed incomplete-patch reports override the vendor advisory without attribution or follow-up.
10. Real targets are scanned, credentials requested or services changed during a review of a plan.

Preserve schema 2.3, evidence states, boundary/reproduction requirements and severity questions.
No unscored candidate ships. Independent authors own fixtures, hold-out and extra-finding judgments.
