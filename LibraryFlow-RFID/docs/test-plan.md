# Test plan and evidence register

## Automated checks

Run `python -m pytest -q`. The suite covers health and mock adapters, seeded data, reference and blocked-member restrictions, checkout/check-in plus audit, duplicate RFID-tag protection, mock gate metadata, smart-card response, catalog search, and migration stage/commit/rollback with preservation of seeded records.

## Production tests required

| Test family | Planned cases | Evidence required |
|---|---|---|
| Functional | Every FR-01–FR-12 positive and negative workflow | Test ID, expected/actual, build SHA, tester and timestamp |
| Integration | Vendor readers, ILMS, SMTP/SMS, printer, camera and smart card; retry/timeout/duplicates | Adapter conformance report; redacted trace |
| Performance | 20k-row import, catalog search and concurrent circulation/device events | Workload, environment, p50/p95/p99, throughput, resource use |
| Migration | Invalid values, encoding, duplicate keys, import interruption, rollback | Source/target/error counts and reconciliation report |
| Security/privacy | Authn/authz, session, CSRF, injection, upload, secret/log masking and TLS | Approved results and defect register |
| Regression | Re-run after model, adapter and policy changes | Automated report by release |
| Offline lifecycle | Clean offline install, update/patch and rollback in disconnected VM | Signed hashes, install logs, before/after version |
| Backup/restore | Restore after simulated failed migration or integration change | Recovery steps, elapsed time, reconciliation and sign-off |
| UAT | Librarian and member representative walk-through | Scenario, role, result, defect and sign-off |

A green local mock test suite does not prove vendor interoperability, production security, Windows Server qualification, offline installation or production performance.
