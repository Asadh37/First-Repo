# Production readiness backlog

These items are intentionally not represented as complete.

- [ ] Add approved authentication, secure sessions and server-side role enforcement on every protected route.
- [ ] Confirm system of record; implement and contract-test a read-only ILMS adapter first.
- [ ] Implement actual NCIP 2.0/SIP2 exchanges for the agreed profile, with correlation IDs, retries, timeouts, idempotency and dead-letter handling.
- [ ] Add real RFID tag encoding and vendor adapters for readers, gate, card, label printer and camera.
- [ ] Implement real alarm/footfall/CCTV and email/SMS/print providers, preferences, consent, retries and delivery evidence.
- [ ] Implement acquisitions, serials, barcode/spine-label printing, member self-service/OPAC, net cataloguing and virtual bookshelf.
- [ ] Add a dedicated search index, scheduled indexing and staleness monitoring.
- [ ] Implement fine payment/reversal and approved library policies.
- [ ] Build inventory expected-vs-observed baselines, misplaced-shelf logic and durable event queue.
- [ ] Add Alembic migrations, approved production DB engine and schema upgrade strategy.
- [ ] Harden uploads, validation, logging, rate limits and privacy controls.
- [ ] Add full dependency lock/SBOM/licence inventory and CI formatting, linting, static analysis, dependency and secret scans.
- [ ] Produce a signed Windows offline installer, activation, patch bundle, signature validation and rollback tooling.
- [ ] Add service monitoring, structured logs, backups, secret vault, alerts and retention policy.
- [ ] Execute and attach 20k performance/migration evidence, restore drill, offline update demo, security review and UAT sign-off.
- [ ] Complete authorised staging, privacy and institutional approvals before using production data.
