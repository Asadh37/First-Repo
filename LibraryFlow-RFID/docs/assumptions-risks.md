# Assumptions, clarification log and risk register

## Assumptions

1. No ILMS schema, production credentials, live database or source spreadsheet was supplied; the prototype uses an independent local DB and synthetic data.
2. XLSX is the initial migration format; required columns are accession_no and title.
3. Physical device SDKs and ILMS endpoints are unavailable; RFID, camera, notification and NCIP/SIP2 seams are mocks.
4. Fine is demonstrated as ₹1 per overdue day; FINE_LIMIT is configurable. Actual library policy must be confirmed.
5. Single-library scope and local database are assumed; branch and patron-account requirements need confirmation.

## Clarification questions

- Which ILMS vendor/version, supported NCIP/SIP2 profiles and endpoints apply? Is integration read-only or allowed to mutate circulation?
- Which system is source-of-truth for bibliographic, item, patron, circulation, fine and RFID fields?
- Which reader/gate/card/camera models, firmware, SDKs, tag encoding and offline security-bit semantics are required?
- What are the actual spreadsheet headers, encodings, null rules and duplicate-resolution policy?
- Which member types, loan/renewal rules, fine cap and notification preferences apply?
- Which Windows Server, DB engine, identity provider, certificate authority and offline update process are approved?
- Which reports and UAT sign-off stakeholders are required?

## Risks

| Risk | Severity | Mitigation / gate |
|---|---|---|
| Live ILMS records could be corrupted | Critical | Separate DB, reviewed contract, backup, read-only discovery phase and authorised sandbox |
| Mocks mistaken for certified protocol support | High | Clearly labelled docs/UI; actual profile/conformance tests required |
| Demo endpoints are unauthenticated | High | Localhost only; production auth, route roles and network security required |
| Migration source mapping or duplicates are wrong | High | Stage, validate, dry-run, reconcile, backup and rehearse rollback |
| Gate events repeat or disappear offline | High | Production IDs, durable queue, dedupe, retry and sync state machine |
| Offline bundle misses dependencies | Medium | Build wheelhouse and test clean disconnected installation |
| Backup copy is inconsistent while DB is running | Medium | Stop service or use DB-native backup; verify restore with count reconciliation |
