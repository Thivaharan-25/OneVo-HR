# App Catalog Userflow

## Actor

App catalog operator.

## Journey

1. Operator opens Settings -> App Catalog.
2. Console lists global app catalog entries.
3. Operator adds or updates app metadata.
4. Operator reviews uncatalogued app candidates.
5. Operator bulk-approves valid candidates.
6. Backend links observed applications and audits changes.

## APIs Used

- `GET /admin/v1/app-catalog`
- `POST /admin/v1/app-catalog`
- `PATCH /admin/v1/app-catalog/{id}`
- `GET /admin/v1/app-catalog/uncatalogued`
- `POST /admin/v1/app-catalog/bulk-approve`
