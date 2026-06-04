# Role Template Management Userflow

## Actor

Platform operator with role-template permissions.

## Global Template Journey

1. Operator opens Developer Platform -> Templates -> Template Manager -> Role Templates.
2. Console loads available product-module permissions and existing templates.
3. Operator creates or edits a template.
4. Backend validates permission ownership.
5. Template is versioned and audit-logged.

## Tenant Apply Journey

1. Operator opens Tenant Console -> Manage/Configure -> Roles.
2. Console loads tenant-filtered permission catalog.
3. Operator applies a template or creates tenant-specific role.
4. Backend validates permissions against tenant entitlements.
5. Auth module materializes tenant roles.

## APIs Used

- `GET /admin/v1/role-templates`
- `POST /admin/v1/role-templates`
- `PATCH /admin/v1/role-templates/{id}`
- `GET /admin/v1/tenants/{id}/permissions/catalog`
- `GET /admin/v1/tenants/{id}/roles`
- `POST /admin/v1/tenants/{id}/roles`
- `POST /admin/v1/tenants/{id}/role-templates/{templateId}/apply`
- `PUT /admin/v1/tenants/{id}/roles/{roleId}/permissions`
