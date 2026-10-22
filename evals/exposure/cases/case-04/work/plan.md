# Plan: public status page for the product

Owner: support lead. Patch owner: platform engineer (cadence below).

## What it is
A static page at `status.example` that shows service health. It is deliberately public. It is built from a repository by a CI job and served from object storage
behind a CDN; there is no application server, no login and no administrator console on the public address. The only write path is the CI job's deploy token, which
is scoped to that one bucket and rotated every 90 days (rehearsal: 12 minutes).

## Versions and patching
The static-site generator version is pinned in `package-lock.json` and rebuilt weekly. The CI runner image is pinned by digest. The platform engineer reads the
vendor advisories for the generator and the CDN weekly and applies critical fixes within 48 hours.

## A rumour we are tracking
A forum post claims the generator's latest fix (2.9.3) is incomplete. The vendor says the post describes an unrelated issue and has not confirmed a bypass. We will
**install 2.9.3 now as the vendor advises**, keep watching the vendor's advisory page for a follow-up, and apply any further fix the day it ships. We will not hold the
update back on the rumour.
