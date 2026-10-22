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
confirm it is rejected with 401 (the request is signed by us, see below, so the check does not depend on the provider still holding the old secret); (6) rename `WEBHOOK_SIGNING_SECRET_NEXT` to `WEBHOOK_SIGNING_SECRET`, redeploy, and review rejected-signature logs for the exposure window. In a suspected leak step (4) comes first,
before any new secret is created, accepting that the provider retries the webhooks that fail in the gap. Before the old value is removed (in a leak, the first thing done), the on-call engineer computes the signature of a fixed test body with it locally and saves that request; after the redeploy the saved request is replayed once through the service and once against each replica's pod address, and every replica must answer 401 (all replicas must also report the new revision before the step is closed). Reviewing rejected-signature logs cannot show a forged event that was accepted, so after a suspected leak the exposure window is also reconciled the other way: every event `payments-hook` accepted between the earliest possible leak time and the end of step (4) is compared with the provider's event history by event id, any accepted event that is not in the provider's history is treated as forged, and the orders it marked paid are held until each is re-confirmed against the provider's read-only payment lookup. The only consumer is `payments-hook`. Trigger: suspected leak, vendor notice, every 180 days.

## Not covered
The platform vendor's own breach response is outside our control; the inventory above assumes their copy may be read.
