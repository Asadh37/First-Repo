# API contracts (prototype)

The generated OpenAPI schema is at /openapi.json; interactive docs are at /docs.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | /api/health | App version, status and adapter health |
| GET/POST | /api/books | Search/list and create a catalog item |
| GET/POST | /api/members | Search/list and create a member |
| POST | /api/circulation/checkout | Check out with policy validation |
| POST | /api/circulation/checkin | Return an active loan and record demo fine |
| POST | /api/circulation/renew | Renew within the demo cap |
| GET | /api/circulation/loans | Recent loan history |
| POST | /api/rfid/tag | Validate an accession and associate a unique mock tag |
| POST | /api/rfid/inventory?shelf=CS-01 | Run mock shelf inventory |
| POST | /api/rfid/gate-event | Record mock gate passage/removal |
| POST | /api/rfid/smart-card-login | Validate a demo card; returns illustrative role, not secure session |
| GET | /api/rfid/devices | Adapter health |
| GET | /api/dashboard | Dashboard aggregates |
| GET | /api/reports/audit?limit=100 | Recent audit events |
| POST | /api/migration/stage | Stage and validate multipart XLSX |
| GET | /api/migration/batches | Migration batch summary |
| GET | /api/migration/batches/{id} | Row-by-row staged results |
| POST | /api/migration/batches/{id}/commit | Insert valid staged records; no updates to existing rows |
| POST | /api/migration/batches/{id}/rollback | Attempt safe rollback using this batch's commit audit record |

All endpoints are for a local candidate prototype. Add authentication and server-side authorization before network deployment.
