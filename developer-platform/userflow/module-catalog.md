# Module Catalog Userflow

## Actor

Module Catalog Manager or Platform Super Admin.

## Journey

1. Operator opens Platform Management -> Feature Management / Module Catalog.
2. Console lists ONEVO product modules.
3. Operator creates or updates product module metadata, package, phase, pricing, limits, and permission ownership.
4. Backend validates module key, price brackets, and permission ownership.
5. Backend writes catalog changes and price history.
6. Operator previews tenant impact before deactivating or changing major module behavior.

## APIs Used

- `GET /admin/v1/modules/catalog`
- `POST /admin/v1/modules/catalog`
- `GET /admin/v1/modules/catalog/{moduleKey}`
- `PATCH /admin/v1/modules/catalog/{moduleKey}`
- `GET /admin/v1/modules/catalog/{moduleKey}/permissions`
- `PUT /admin/v1/modules/catalog/{moduleKey}/permissions`
- `GET /admin/v1/modules/catalog/{moduleKey}/pricing`
- `PATCH /admin/v1/modules/catalog/{moduleKey}/pricing`
- `GET /admin/v1/modules/catalog/{moduleKey}/tenant-impact`

## Boundary

Module Catalog manages ONEVO product modules only. Developer Platform screen access is managed by Platform Access.
