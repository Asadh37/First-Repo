# LibraryFlow RFID

A white-and-navy RFID-enabled library management prototype aligned to the AISYS Candidate Software Development SOP. This folder contains the runnable prototype, mock RFID and ILMS adapters, spreadsheet migration workflow, automated tests, traceability matrix, architecture and operational guidance.

## Prototype boundary
All seeded records are synthetic. This application does not connect to a live ILMS or physical hardware. RFID readers, gates, smart cards, cameras, NCIP/SIP2, email, SMS and print services are mocked. The demo API has no authentication, so run on localhost only. This is not production-certified and does not include a tested offline installer.

## Quick start
Requires Python 3.11+.

    python -m venv .venv
    # Windows: .venv\\Scripts\\Activate.ps1
    # Linux/macOS: source .venv/bin/activate
    python -m pip install -r requirements.txt
    uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

Open http://127.0.0.1:8000 for the web console, /docs for interactive API docs, and /api/health for diagnostics. A local SQLite database is created and seeded on first run.

## Demo walkthrough
1. Search the catalog or add an item/member.
2. Check out ACC-1005 to STU-2026-001; ACC-1002 is reference-only and STU-2026-003 is blocked.
3. Run a simulated inventory scan for CS-01, tag ACC-1005, validate CARD-FAC-2026-001 or trigger a mock security-gate event.
4. Generate a synthetic 20,000-row workbook using `python scripts/generate_sample_migration.py`; upload the XLSX in Migration Center, inspect the staged counts, commit valid rows and optionally roll the demo batch back.
5. Inspect audit records and dashboard metrics.

## Test
    python -m pytest -q

## Project structure
- app/: FastAPI routes, SQLAlchemy models, seed data, mock adapter contracts, migration service and web UI.
- docs/: architecture, API contracts, database data dictionary, traceability, risk register, D0-D10 plan, deployment, user guide, test plan and production backlog.
- tests/: automated API tests.
- scripts/: synthetic 20k workbook generator and demo helper.
- sample_data/: sample import header template.

Detailed FR/NFR and AC mapping is in docs/requirements-traceability.md. Offline lifecycle validation, real NCIP/SIP2 exchanges, physical hardware integration, production authentication, security hardening, full SBOM and signed Windows installer remain explicit production backlog items. Do not use real patron data in this prototype.

## Licence
Candidate demonstration source. Review all dependency licences before redistribution; no vendor SDK or hardware driver is bundled.
