# Decision memo: move the nightly batch to Stepwise (managed workflow service)

**Recommendation:** move the nightly batch from cron on a VM to Stepwise this quarter.

## Why
- The VM costs **$400 per month** (instance, disk, backups) and needs patching and a person on call for stuck jobs.
- Stepwise bills **$0.06 per workflow run**. Our batch is about **3,000 runs per month**, so the bill is **$180 per month**,
  a saving of $220 per month ($2,640 per year).
- Stepwise retries failed steps on its own and keeps a run history for 90 days, which removes our hand-written retry code.

## Alternatives considered
1. Stay on cron and add the retry helper (cost: two days of work, no change to the $400).
2. Move to Stepwise (this memo).
3. Run the batch as a scheduled container job on the existing cluster (cost: about $60 per month of extra node capacity).

## Plan
1. Week 1: port the three batch scripts into Stepwise definitions.
2. Week 2: run both systems in parallel and compare outputs.
3. Week 3: cut over. **Decommission the VM the same day**, so we stop paying for it.

## Risks
- Vendor outage. Stepwise publishes 99.9% availability.
