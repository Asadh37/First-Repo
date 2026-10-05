# Requirements Traceability Matrix

Status: **P** prototype implemented; **S** partially represented/design boundary; **R** production work remaining. A UI control does not claim an OEM/device protocol is certified.

| Requirement | SOP intent | Prototype evidence | Status / next evidence |
|---|---|---|---|
| FR-01 | Acquisition, cataloguing, serials, circulation, OPAC, barcode/spine labels, reports | Catalog create/search, circulation and reports | S — acquisition, serials, barcode and spine-label print templates remain |
| FR-02 | Web UI, full-text search/indexing, net cataloguing, virtual bookshelf | Staff console and query-time catalog search | S — dedicated index/re-index and virtual bookshelf remain |
| FR-03 | RFID devices via middleware; NCIP 2.0 and SIP2 boundary | Device-neutral mock adapters and documented ILMS seam | S — real exchanges require authorised ILMS contract and conformance tests |
| FR-04 | Checkout, check-in, renew, due enquiry, card personalisation, restrictions, member blocking, fine limits and role rights | Circulation endpoints, renewal cap, reference/blocked/fine checks, mock card role output | S — production authentication/authorization and card personalisation remain |
| FR-05 | Validate records before tagging, associate RFID tag and monitor | Existing accession check, unique tag association, RFID events | P for mock tagging; monitoring and retag approval remain |
| FR-06 | Stock verification, shelf management, misplaced/missing, bulk read and confirmation | Mock shelf scan and tagged/untagged exceptions | S — physical read feedback and richer expected-vs-observed logic require hardware |
| FR-07 | Unauthorised gate, offline security bit, accession, alarm/footfall/CCTV/email | Gate event, mock camera URI and queued email object | S — actual alarm, footfall, offline security policy, CCTV capture and email need verified integrations |
| FR-08 | Usage stats and reports for items, members, circulation, operators/clients, fines and gate events | Dashboard aggregates and audit endpoint | S — exports, filters and operator/client breakdown remain |
| FR-09 | Configurable per-user email/SMS/print adapters | Provider-neutral notification mock | S — preferences, retries and delivery proof remain |
| FR-10 | Import ~20k spreadsheet rows with validation, duplicates, error logs, reconciliation and rollback | XLSX staging, invalid/duplicate detection, explicit commit, counts, audit-backed rollback | P for core workflow; benchmark 20k and restore evidence remain |
| FR-11 | User/role management, configuration, audit, version and health | Demo roles, audit events, version and health endpoint | S — real identity lifecycle and enforcement remain |
| FR-12 | Offline activation, updates, upgrades, patches and rollback package | Local setup and offline deployment design | R — signed installer/update package and offline rollback demo remain |
| NFR-01 | Do not corrupt existing library records | Separate prototype DB; importer inserts only; rollback tracks its own inserted accession list | S — backup/restore evidence and read-only live ILMS contract required |
| NFR-02 | Privacy/security, least privilege, secrets, audit and encrypted transport | Synthetic seed, env example, input validation, audit history | S — authentication, route-level authorization, CSRF, TLS and security assessment required |
| NFR-03 | Windows 11 clients and Windows Server 2022+ isolated-site deployment | Python ASGI app and topology guide | R — Windows qualification and isolated install test remain |
| NFR-04 | Pinned and licensed dependencies | Exact top-level dependency versions in requirements.txt | S — full transitive lock and SBOM/licence inventory remain |
| NFR-05 | Functional, integration, performance, migration, security, regression and UAT evidence | pytest API suite and migration helper | S — load/security/UAT artefacts remain |
| NFR-06 | Modular adapters, external config, logs, versioned migrations, build and rollback | Layered modules, env config, audit model | S — Alembic history, structured logging and release procedure remain |
| NFR-07 | Diagnostics, health checks, logs and runbooks | /api/health and audit endpoint | S — service diagnostics and incident runbooks remain |
| NFR-08 | Architecture, device/interface details, API, versions and operational documentation | Documentation package and generated OpenAPI | S — site-specific IP/interface details require the actual environment |
| NFR-09 | D0 to D10 delivery and production backlog | Milestone plan and backlog | P for planning only; execution evidence still needs capturing |

## Acceptance scenario traceability

| Scenario | Demonstration | Evidence |
|---|---|---|
| AC-01 | Stage an XLSX with valid, missing-key and duplicate rows; inspect report; commit; reconcile counts; rollback | /api/migration/* and migration end-to-end test |
| AC-02 | Create/find a catalog record, validate it and associate a unique mock RFID tag | Catalog UI, /api/rfid/tag, audit table |
| AC-03 | Checkout, renew and check-in through the simulated protocol boundary | Circulation endpoints and audit trail |
| AC-04 | Attempt reference-item, blocked-member and over-limit-fine checkout | Expected 409/403 responses and policy tests |
| AC-05 | Run handheld mock inventory and inspect exception/confirmation data | /api/rfid/inventory |
| AC-06 | Trigger gate alert and inspect accession, mock CCTV and queued notification | /api/rfid/gate-event |
| AC-07 | Validate CARD-FAC-2026-001 and inspect illustrative role response | /api/rfid/smart-card-login |
| AC-08 | View dashboard and filterable audit endpoint | /api/dashboard, /api/reports/audit |
| AC-09 | Install offline, apply offline update and rollback in a disconnected VM | Not completed; production gate |
| AC-10 | Restore after simulated failed migration/change and reconcile data | Runbook exists; restore drill evidence remains |
