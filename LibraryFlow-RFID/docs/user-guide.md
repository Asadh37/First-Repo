# User guide

## Dashboard, catalog and members

The overview displays collection size, members, active loans, RFID coverage and gate alerts. All initial records are synthetic. Use Add new book or Add member to create local records; accession/member numbers must be unique. Search can match title, author, subject, accession or tag. Reference-only titles cannot be checked out.

## Circulation

Select Check out, Check in or Renew; enter accession and member IDs.

- Checkout rejects missing records, reference-only items, items already on loan, blocked members and fine balances above FINE_LIMIT.
- A successful checkout creates a 14-day loan and calls only the mock ILMS adapter.
- Renew adds 14 days and permits at most two renewals per loan.
- Check-in closes the loan; the demonstration policy adds ₹1 per overdue day.
- Actions are recorded in the audit table.

## RFID console

- Stock verification runs a simulated handheld scan for a shelf. In this prototype, tagged items on the recorded shelf appear as observed and untagged items are exceptions. This is not evidence of actual physical location.
- Security gate triggers an event for an existing accession. Unauthorised events record accession, create a mock:// camera reference and queue a mock email object. No camera is used or email sent.
- RFID tagging associates a unique tag with an existing accession.
- Smart-card example CARD-FAC-2026-001 returns an illustrative faculty role. This does not create a secured login session or protect other endpoints.

## Spreadsheet migration

Upload .xlsx with accession_no and title columns; author, isbn and shelf are optional. Stage first, inspect valid/rejected/duplicate counts, and explicitly choose Commit valid. A committed batch can be rolled back when its audit evidence exists, and rollback refuses records that have RFID tags or circulation history. Use a disposable demo DB for experiments.

The repository includes scripts/generate_sample_migration.py to create a synthetic 20,000-row workbook and sample_data/books_import_template.csv as a sample format reference; the current upload endpoint accepts XLSX only.

## Reports and troubleshooting

Download summary as local JSON. Audit data and health are available at /api/reports/audit and /api/health. The generated API reference is /docs. For demo DB corruption, stop the service and restore a known backup rather than editing the SQLite file manually.
