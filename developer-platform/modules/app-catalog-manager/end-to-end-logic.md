# App Catalog Manager End-to-End Logic

## Add Catalog App

1. Operator opens Settings -> App Catalog.
2. Frontend calls `GET /admin/v1/app-catalog`.
3. Operator enters process name, display name, category, publisher, icon URL, public state, and default productivity classification.
4. Frontend calls `POST /admin/v1/app-catalog`.
5. Backend verifies `platform.app_catalog.manage`.
6. Backend creates `global_app_catalog` entry through Shared Platform interface.
7. Backend links matching `observed_applications` and audits the change.

## Bulk Approve Uncatalogued Apps

1. Frontend loads candidates from `GET /admin/v1/app-catalog/uncatalogued`.
2. Operator selects candidates and enters metadata.
3. Frontend calls `POST /admin/v1/app-catalog/bulk-approve`.
4. Backend creates catalog entries transactionally and links observations.

## APIs

| Method | Route | Purpose | Permission |
|---|---|---|---|
| GET | `/admin/v1/app-catalog` | List global app catalog | `platform.app_catalog.read` |
| POST | `/admin/v1/app-catalog` | Create app entry | `platform.app_catalog.manage` |
| PATCH | `/admin/v1/app-catalog/{id}` | Update metadata/public state | `platform.app_catalog.manage` |
| GET | `/admin/v1/app-catalog/uncatalogued` | Candidate processes | `platform.app_catalog.read` |
| POST | `/admin/v1/app-catalog/bulk-approve` | Bulk approve candidates | `platform.app_catalog.manage` |
