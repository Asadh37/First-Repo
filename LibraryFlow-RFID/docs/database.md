# Database and data dictionary

The prototype schema is in app/models.py. Tables are created at startup for an easy demo; a production build should use reviewed Alembic migrations and tested downgrade procedures.

| Table | Key fields | Purpose |
|---|---|---|
| books | id, accession_no, title, shelf, rfid_tag | Bibliographic/item record, reference restriction, availability and tag |
| members | member_no, role, blocked, fine_balance, smart_card_id | Synthetic member and circulation policy inputs |
| loans | book_id, member_id, due_date, returned_at, renewals | Circulation history; returned loans are retained |
| audit_events | at, actor, action, entity_type, entity_id, details | Administrative and circulation action evidence |
| rfid_events | device_type, device_id, tag_id, event_type | Simulated reads, tagging, gate and inventory events |
| gate_events | accession_no, authorised, cctv_reference, notification_status | Gate event and mock camera/notification reference |
| migration_batches | source/valid/rejected/duplicate counts, status | Import reconciliation summary |
| migration_staging | batch_id, row_number, source fields, status, errors | Row-level results before explicit commit |

## Data rules

- accession_no is unique and required for each book.
- RFID tag is optional but unique if assigned.
- Reference-only items cannot be checked out.
- Blocked members cannot check out; a member fine balance above FINE_LIMIT is rejected.
- Demo renewal cap is two renewals per loan.
- Required spreadsheet columns are accession_no and title. Accepted aliases include accession, accession number, book title and location.
- Invalid and duplicate rows are excluded from commit.
- Sample emails use the reserved .test domain.
