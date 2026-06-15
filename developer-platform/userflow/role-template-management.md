# Role Template Management Userflow

## Actor

Platform operator with role-template permissions.

## Global Template Journey

1. Operator navigates to **Platform Management → Templates** (`/platform/templates`).
2. Selects the **Role** filter chip to view existing role templates. Console loads available role templates.
3. To create: click **"+ New Template"** → Type Picker modal → select **Role** → creation form loads with permission picker grouped by module.
4. To edit: click an existing template card → click **Edit** (or **Clone** for system templates).
5. Operator creates or edits the template.
6. Backend validates permission ownership.
7. Template is versioned and audit-logged.

## Tenant Apply Journey

1. Operator opens Tenant Management -> Manage/Configure -> Roles.
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
