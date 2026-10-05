# Deployment, backup, update and rollback guide

## Local evaluation

1. Install Python 3.11 or newer.
2. Open a terminal in the LibraryFlow-RFID folder.
3. Create an environment: `py -3.11 -m venv .venv` (Windows) or `python3 -m venv .venv`.
4. Activate: `.venv\\Scripts\\activate` on Windows, or `source .venv/bin/activate` on Linux/macOS.
5. Install: `python -m pip install -r requirements.txt`.
6. Start: `uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`.
7. Browse to `http://127.0.0.1:8000`; API docs are at `/docs`; health is at `/api/health`.

The default database is `sqlite:///./libraryflow.db` and synthetic sample records are created on first start. Keep the bind address at localhost; authentication is not implemented.

## Offline setup planning

On an approved connected staging machine, prepare a controlled wheelhouse for the approved Python version and platform:

```powershell
python -m pip download --only-binary=:all: --dest wheelhouse -r requirements.txt
python -m pip install --no-index --find-links wheelhouse -r requirements.txt
```

Review package licences and hashes, transfer the bundle according to local media controls, and install in a clean disconnected test VM. The prototype is not itself a signed installer or tested update package.

## Configuration

- DATABASE_URL: connection string; default local SQLite.
- FINE_LIMIT: circulation fine threshold; default 100.00.
- APP_ENV: environment label.
- SESSION_SECRET: placeholder only; does not secure routes because app sessions/authentication are not implemented.

Never commit secrets, personal data, certificates or production connection strings.

## Local SQLite backup/restore

Stop the app before a consistent file-level copy. Example PowerShell command:

```powershell
Copy-Item .\\libraryflow.db .\\backups\\libraryflow-YYYYMMDD-HHMM.db
```

Restore with the service stopped: move the failed DB aside, copy the selected backup into the configured DB path, restart, then reconcile book/member/loan counts and audit rows. Record the operator, timestamp, backup source and results. For production, use institution-approved DB-native backup and point-in-time recovery procedures.

## Update and rollback gates

1. Build from an immutable commit in a clean environment.
2. Run tests, dependency scanning, SBOM/licence checks and migration dry-runs.
3. Produce an organisation-signed offline package with hashes and signature validation.
4. Back up database/configuration and record the current version.
5. Test in staging and run AC-01 to AC-10 where possible.
6. Apply during an approved maintenance window and reconcile results.
7. On failure stop services, restore compatible app/config and DB backup, and verify.

**Not delivered/validated:** signed installer, update agent, signing-key lifecycle, automatic DB downgrade, Windows service wrapper, Windows Server qualification, offline install and rollback drill.
