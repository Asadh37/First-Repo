# Acceptance evidence register

This register distinguishes automated prototype evidence from evidence that must be collected in a real approved test environment. Do not mark a scenario passed just because a mock adapter returned a response.

| SOP scenario | Current prototype evidence | Evidence still required |
|---|---|---|
| AC-01 — Import ~20,000 records | XLSX staging, row validation, duplicate detection, explicit commit, reconciliation counts, rollback test on a small synthetic workbook | Run generated 20k workbook; record runtime, peak memory, source/valid/rejected/duplicate/created counts; verify existing records before/after; attach test log |
| AC-02 — RFID tagging | Existing accession validation and unique mock tag association | Record screen/API evidence for new and invalid accession, duplicate tag rejection, audit event |
| AC-03 — Circulation integration | Checkout/check-in test through mock ILMS boundary; renew endpoint exists | Capture checkout, renewal and check-in responses plus audit events; real protocol conformance is out of scope for mock demo |
| AC-04 — Restrictions | Tests cover reference-only and blocked member; fine threshold implemented | Add and run over-limit fine test and record expected rejection |
| AC-05 — Shelf inventory | Mock scan returns seen/untagged exceptions | Capture inventory report for a shelf with a known expected baseline, including missing and misplaced items; physical reader feedback is not implemented |
| AC-06 — Security gate | Mock gate event includes camera reference and queued notification object | Capture authorised and unauthorised examples; explain simulated camera URI and notification; no real alarm/CCTV/email claim |
| AC-07 — Smart card | Mock card lookup returns illustrative member role/permissions | Demonstrate invalid card and show role restrictions are not production identity integration |
| AC-08 — Reports | Dashboard aggregates and audit endpoint | Capture reports for circulation, members, fines and gate events; document missing filters/export as limitations |
| AC-09 — Offline install/update/rollback | Deployment plan only | Install/update/rollback on disconnected VM; include hashes, versions, logs and result; currently not delivered |
| AC-10 — Backup/restore | Backup/restore instructions only | Perform restore drill on disposable synthetic database and reconcile key table counts and audit records |

## Run evidence collection

1. Use only generated/synthetic records and a disposable database.
2. Record commit SHA, Python version, OS, test command, start/end time and tester.
3. Attach terminal logs and redacted screenshots to the submission package.
4. Record each failed step as a defect; do not replace failures with a narrative claim of success.
5. Keep institutional approvals, UAT signatures and production/vendor test evidence marked pending until actually obtained.
