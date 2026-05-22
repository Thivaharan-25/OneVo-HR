# Module Catalog Userflow

## Actor

Module Catalog Manager or Platform Super Admin.

## Journey

### Create Module

1. Operator opens Platform Management → Feature Management / Module Catalog.
2. Operator clicks **+ Add Module**.
3. Operator fills in the create form: module key, display name, pillar, pricing unit, sellable toggle, phase, AI capability flag, storage flag, setup service keys, price brackets (required if sellable), permission ownership, default permissions, and active state.
4. In the **Permission Ownership** field, the permission picker loads all platform permissions. Permissions already owned by another module are shown greyed out and disabled — operator cannot select them without first releasing them from the owning module. Unclaimed permissions are freely selectable.
5. Operator selects `default_permission_codes` from the subset of permissions they have already selected in step 4.
6. Operator submits. Backend validates: module key unique, price brackets present if sellable, no permission conflicts, default permissions are a subset of owned permissions, Phase 2 forces `is_active = false`.
7. Backend writes `module_catalog` row and price history. Audit log entry created.

### Update Permission Ownership

1. Operator opens a module detail page → **Permissions** tab.
2. Permission picker loads pre-populated with this module's currently owned permissions checked. All platform permissions are shown — permissions owned by other modules are visible but greyed out and disabled (tooltip: "Owned by `{module_name}` — release it there first"). Unclaimed permissions are selectable.
3. Operator checks or unchecks permission codes.
4. Operator saves. Backend rejects any permission already owned by another module (422 listing the conflicting module key). On success, `permission_codes_json` is updated and any deselected permissions are automatically removed from `default_permission_codes`.
5. Backend invalidates affected tenant permission catalog caches.

### Update Pricing

1. Operator opens a module detail page → **Pricing** tab.
2. Operator updates price brackets or rates.
3. Backend writes updated brackets and a `module_catalog_price_history` entry. Existing tenant subscription snapshots are not repriced.

### Preview Tenant Impact

1. Before deactivating a module or making a significant pricing or permission change, operator navigates to the **Tenant Impact** tab on the module detail page.
2. Backend returns the list of tenants and plans that would be affected.
3. Operator reviews and confirms before proceeding.

## APIs Used

- `GET /admin/v1/modules/catalog`
- `POST /admin/v1/modules/catalog`
- `GET /admin/v1/modules/catalog/{moduleKey}`
- `PATCH /admin/v1/modules/catalog/{moduleKey}`
- `GET /admin/v1/modules/catalog/{moduleKey}/permissions`
- `GET /admin/v1/modules/catalog/{moduleKey}/permissions/available`
- `PUT /admin/v1/modules/catalog/{moduleKey}/permissions`
- `GET /admin/v1/modules/catalog/{moduleKey}/pricing`
- `PATCH /admin/v1/modules/catalog/{moduleKey}/pricing`
- `GET /admin/v1/modules/catalog/{moduleKey}/tenant-impact`

## Validation Rules

| Rule | Enforced on |
|---|---|
| Module key unique, lowercase, underscores only, max 80 chars | Create |
| Module key permanent after creation | Update |
| Sellable modules require at least one price bracket | Create + Update |
| Phase 2 modules forced to `is_active = false` | Create |
| Permission codes cannot be owned by two modules simultaneously | Create + Update permissions |
| `default_permission_codes` must be a subset of `permission_codes_json` | Create + Update permissions |
| Deselecting an owned permission auto-removes it from `default_permission_codes` | Update permissions |

## Boundary

Module Catalog manages ONEVO product modules only. Developer Platform screen access is managed by Platform Access.
