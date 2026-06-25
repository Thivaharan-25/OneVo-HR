# Security Role Creation

**Area:** Auth & Access  
**Trigger:** Admin clicks Create Role  
**Required Permission(s):** `roles:manage`

---

## Phase 1 Source of Truth

Roles & Permissions remains in the sidebar. Role create/edit/clone is a one-screen popup or drawer over the role list. Do not use a full-page creation flow and do not use a multi-step wizard.

Roles define **what the user can do**. Position-based access or explicit assignment defines **which employees the user can access**.

---

## Create/Edit Role UX

Fields on the same screen:

- Role name
- Description
- Permission browser grouped by module
- Selected permissions summary

Tenant roles created here must appear in later role dropdowns, including **Role granted** inside position setup.

---

## Permission Browser

Permissions are grouped by module. Employee-data permissions are selected as permission codes only; employee visibility is not configured on `role_permissions`.

Phase 1 alert permissions use:

- `monitoring:alerts:read`
- `monitoring:alerts:resolve`

Full Exception Engine rule management is Phase 2 and should not be a normal Phase 1 role-create focus.

---

## Save Behavior

1. Validate role name uniqueness.
2. Validate selected permissions are from enabled tenant modules/features.
3. Create/update `roles`.
4. Create/update `role_permissions`.
5. Invalidate affected permission caches.
6. Audit the change.

---

## Clone Role

Clone opens the same one-screen drawer/popup with copied permissions. Admin must provide a new role name before saving.

---

## Related

- [[Userflow/Auth-Access/permission-assignment|Permission Assignment]]
- [[Userflow/Auth-Access/access-policy|Management Coverage Reference]]
- [[Userflow/Org-Structure/position-setup|Position Setup]]
