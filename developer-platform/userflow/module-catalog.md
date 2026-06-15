# Module Catalog Userflow

## Actor

Module Catalog Manager or Platform Super Admin.

## Journey

### Create Module

1. Operator opens Platform Management -> Feature Management / Module Catalog.
2. Operator clicks **+ Add Module**.
3. Operator fills in the create form: module key, display name, pillar, pricing unit, sellable toggle, phase, AI capability flag, storage flag, setup service keys, commercial feature list, price brackets (required if sellable), permission ownership, default permissions, and active state.
4. In the **Permission Ownership** field, the permission picker loads seeded tenant-facing permission codes from the permission catalog. Permissions already owned by another module are shown greyed out and disabled; the operator cannot select them without first releasing them from the owning module. Unclaimed permissions are freely selectable.
5. Operator marks default permissions from the subset of permissions selected in step 4.
6. Operator submits. Backend validates: module key unique, price brackets present if sellable, no permission conflicts, default permissions are a subset of owned permissions, Phase 2 forces `is_active = false`.
7. Backend writes `module_catalog`, `module_features`, `module_permission_ownership`, and price history. Audit log entry created.

### Update Commercial Features

1. Operator opens a module detail page -> **Features** tab.
2. Operator adds, edits, deactivates, or marks default-included feature keys for the module.
3. Backend validates feature keys use `{module_key}.{feature_name}` and are unique.
4. Plans and custom contracts can include a subset of these features. Feature flags can only control runtime access after this commercial inclusion exists.

Adding a feature key to Module Catalog only makes that feature available for plan configuration, custom tenant commercial snapshots, permission mapping, and runtime flag mapping. It must not update existing subscription plans, update existing tenant subscriptions, or grant access to every tenant with the parent module.

### Update Permission Ownership

1. Operator opens a module detail page -> **Permissions** tab.
2. Permission picker loads pre-populated with this module's currently owned permissions checked. All seeded tenant-facing permissions are shown: permissions owned by other modules are visible but greyed out and disabled (tooltip: "Owned by `{module_name}` - release it there first"). Unclaimed permissions are selectable.
3. Operator checks or unchecks permission codes and marks which owned permissions are default permissions for future tenant Owner role materialization.
4. Operator saves. Backend rejects any permission already owned by another module (422 listing the conflicting module key). On success, `module_permission_ownership` is updated and any deselected permissions are automatically removed from the default permission set.
5. Backend invalidates affected tenant permission catalog caches.

### Update Pricing

1. Operator opens a module detail page -> **Pricing** tab.
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
- `GET /admin/v1/modules/catalog/{moduleKey}/features`
- `PUT /admin/v1/modules/catalog/{moduleKey}/features`
- `GET /admin/v1/modules/catalog/{moduleKey}/pricing`
- `PATCH /admin/v1/modules/catalog/{moduleKey}/pricing`
- `GET /admin/v1/modules/catalog/{moduleKey}/tenant-impact`

## Validation Rules

| Rule | Enforced on |
|---|---|
| Module key unique, lowercase, underscores only, max 80 chars | Create |
| Module key permanent after creation | Update |
| Sellable modules require at least one price bracket | Create + Update |
| Sellable modules require at least one commercial feature | Create + Update features |
| Commercial feature keys must use `{module_key}.{feature_name}` | Create + Update features |
| Phase 2 modules forced to `is_active = false` | Create |
| Permission codes cannot be owned by two modules simultaneously | Create + Update permissions |
| Default permissions must be a subset of permissions owned by the same module | Create + Update permissions |
| Deselecting an owned permission auto-removes it from the default permission set | Update permissions |

## Boundary

Module Catalog manages ONEVO product modules, commercial feature lists, and module-to-permission ownership. Permission codes themselves are seeded/version-controlled by the backend permission catalog. Developer Platform screen access is managed by Platform Users and Platform Roles. Tenant Runtime Overrides handle runtime rollout only; it does not define commercial inclusion or pricing.

Module Catalog defines the possible product surface. Subscription Plans define reusable commercial packages. Tenant subscription snapshots define what a specific tenant actually has. A tenant with a module entitlement does not automatically receive every feature key registered under that module.
