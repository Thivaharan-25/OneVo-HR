# System Config Userflow

## Actor

Platform settings manager.

## Journey

1. Operator opens Settings -> System Settings.
2. Console loads global defaults.
3. Operator updates future-tenant defaults.
4. Operator may open a tenant-specific override view.
5. Backend audits every write.

## APIs Used

- `GET /admin/v1/config/defaults`
- `PATCH /admin/v1/config/defaults`
- `GET /admin/v1/tenants/{id}/settings`
- `PATCH /admin/v1/tenants/{id}/settings`
