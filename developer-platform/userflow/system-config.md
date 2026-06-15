# System Config Userflow

## Actor

Platform settings manager.

## Journey

1. Operator opens Settings -> System Config.
2. Console loads global defaults.
3. Operator updates future-tenant defaults.
4. Operator may open a tenant-specific override view.
5. Backend audits every write.

## APIs Used

- `GET /admin/v1/system-config/global-defaults`
- `PATCH /admin/v1/system-config/global-defaults`
- `GET /admin/v1/tenants/{id}/settings-override`
- `PATCH /admin/v1/tenants/{id}/settings-override`
