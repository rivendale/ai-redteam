# Plan: signing the payment-provider webhook

Owner: backend lead. Security contact: platform engineer.

## Secret
`WEBHOOK_SIGNING_SECRET`: the payment provider signs each webhook with it; `payments-hook` verifies the signature before doing anything.

## Inventory
- Lives in: the container platform's secret store (production namespace only); a second copy in the provider's dashboard, which is the issuer.
- Readers: the `payments-hook` deployment and two platform engineers. The platform vendor can read stored values (we treat it as a holder).
- Scope and limits: the secret only authenticates inbound webhooks. It cannot move money or call the provider's API. Replaying a captured webhook is blocked by a
  five-minute timestamp window and an event-id dedupe table.

## Rotation (rehearsed 2026-10-14, 22 minutes)
The provider supports two active signing secrets. Steps: (1) generate a new secret in the dashboard (two engineers hold dashboard access, plus a break-glass login);
(2) add it as `WEBHOOK_SIGNING_SECRET_NEXT` and redeploy `payments-hook`, which accepts either; (3) send a provider test event and confirm it is accepted under the new
secret; (4) remove the old value from the store and redeploy so `payments-hook` accepts only the new secret, and delete the old secret in the dashboard; (5) send a test event signed with the old secret and
confirm it is rejected with 401 and the reason `bad_signature` (the probe is signed by us and checked together with a valid control, see below, so the check does not depend on the provider still holding the old secret); (6) rename `WEBHOOK_SIGNING_SECRET_NEXT` to `WEBHOOK_SIGNING_SECRET`, redeploy, and review rejected-signature logs for the exposure window. In a suspected leak step (4) comes first,
before any new secret is created, accepting that the provider retries the webhooks that fail in the gap. `payments-hook` answers a rejected webhook with 401 and a reason in the body and the log: `bad_signature`, `stale_timestamp` (outside the five-minute window) or `duplicate_event`. Before the old value is removed (in a leak, the first thing done), the on-call engineer computes locally, with the old value, a set of probe requests with fresh unique event ids whose timestamps are spaced four minutes apart across the next forty minutes, and does the same with the new secret for a valid control set. After the redeploy, for each replica's pod address and once through the service, the engineer picks the probe whose timestamp is within two minutes of the moment it is sent and sends it together with the matching control request signed with the new secret. The step passes only if the probe is rejected with 401 and the reason `bad_signature` and the control request is accepted; a 401 with `stale_timestamp` or `duplicate_event` proves nothing and the step is repeated with a fresh probe. Every replica must also report the new revision before the step is closed. Reviewing rejected-signature logs cannot show a forged event that was accepted, so after a suspected leak the exposure window is also reconciled the other way: every event `payments-hook` accepted between the earliest possible leak time and the end of step (4) is compared with the provider's event history by event id, any accepted event that is not in the provider's history is treated as forged, and the orders it marked paid are held until each is re-confirmed against the provider's read-only payment lookup. The only consumer is `payments-hook`. Trigger: suspected leak, vendor notice, every 180 days.

## Not covered
The platform vendor's own breach response is outside our control; the inventory above assumes their copy may be read.
