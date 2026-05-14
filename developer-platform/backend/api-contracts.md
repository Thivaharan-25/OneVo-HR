# Admin API Contracts

All endpoints are under the `/admin/v1/` prefix and require:

```
Authorization: Bearer <platform-admin-jwt>
```

Platform-admin JWTs are issued with issuer `onevo-platform-admin` and have a 30-minute TTL. Tenant-issued tokens are rejected by all endpoints in this namespace.

---

## Tenant Console

Manages tenant lifecycle: creation, status, subscription, module assignment, post-creation Manage/Configure, activation, and impersonation.

| Method | Path | Description |
|---|---|---|
| `GET` | `/admin/v1/subscription-plans` | List reusable subscription/commercial plans for tenant creation, including selected packages/modules, company-size range, calculated/override prices, and AI token limits |
| `POST` | `/admin/v1/subscription-plans` | Create a reusable subscription/commercial plan from selected packages/modules and company-size bracket pricing |
| `PATCH` | `/admin/v1/subscription-plans/{id}` | Update reusable plan metadata, included modules, company-size price band, active state, calculated/override prices, and AI token limits |
| `GET` | `/admin/v1/modules/catalog` | List reusable module catalog, sellable state, company-size bracket pricing, and module-owned permissions |
| `POST` | `/admin/v1/modules/catalog` | Create a reusable module catalog item with price brackets, full-license price, maintenance rate, module limits, and permission ownership |
| `PATCH` | `/admin/v1/modules/catalog/{moduleKey}` | Update reusable module metadata, sellable state, price brackets, full-license price, maintenance rate, module limits, and permission ownership |
| `GET` | `/admin/v1/payment-gateways` | List safe Stripe/PayHere gateway config metadata |
| `POST` | `/admin/v1/payment-gateways` | Create Stripe or PayHere gateway config with encrypted secrets |
| `PATCH` | `/admin/v1/payment-gateways/{id}` | Update gateway metadata or rotate encrypted secrets |
| `GET` | `/admin/v1/tenants/validate` | Validate tenant slug, company name, domain, and primary contact fields |
| `GET` | `/admin/v1/tenants` | List all tenants |
| `POST` | `/admin/v1/tenants` | Create tenant draft through creation wizard Step 1 |
| `GET` | `/admin/v1/tenants/{id}` | Get tenant detail |
| `PATCH` | `/admin/v1/tenants/{id}` | Edit draft tenant details before activation |
| `PATCH` | `/admin/v1/tenants/{id}/status` | Suspend, unsuspend, or activate a tenant |
| `POST` | `/admin/v1/tenants/{id}/impersonate` | Issue an impersonation token (15 min TTL, `impersonation: true`) |
| `PATCH` | `/admin/v1/tenants/{id}/subscription` | Assign or override subscription/commercial terms (creation wizard Step 2; exception tool after activation) |
| `PUT` | `/admin/v1/tenants/{id}/modules` | Set tenant module entitlements and sales state during Manage/Configure |
| `PATCH` | `/admin/v1/tenants/{id}/provision/confirm` | Finalise provisioning draft -> set status active |
| `GET` | `/admin/v1/tenants/{id}/permissions/catalog` | Return universal permissions plus permissions exposed by enabled tenant modules during Manage/Configure |
| `GET` | `/admin/v1/role-templates` | List global/default role templates during Manage/Configure |
| `POST` | `/admin/v1/role-templates` | Create operator-managed role template from a module-filtered permission set |
| `PATCH` | `/admin/v1/role-templates/{id}` | Edit reusable non-system role template and version the change |
| `GET` | `/admin/v1/tenants/{id}/roles` | List materialized tenant roles during Manage/Configure |
| `POST` | `/admin/v1/tenants/{id}/roles` | Create tenant-specific role during Manage/Configure |
| `POST` | `/admin/v1/tenants/{id}/role-templates/{templateId}/apply` | Materialize a role template into tenant-scoped roles during Manage/Configure |
| `PUT` | `/admin/v1/tenants/{id}/roles/{roleId}/permissions` | Adjust a tenant role using only permissions in the tenant catalog |
| `GET` | `/admin/v1/setup-services` | List global/free, paid, and module-specific setup services |
| `POST` | `/admin/v1/setup-services` | Create a setup service definition and optional module binding |
| `PUT` | `/admin/v1/tenants/{id}/setup-services` | Select and track setup services required for the tenant |
| `GET` | `/admin/v1/configuration-templates` | List reusable configuration, role, org, job-family, leave, onboarding, app-allowlist, monitoring, and data-import templates |
| `POST` | `/admin/v1/configuration-templates` | Create a reusable configuration/template record |
| `POST` | `/admin/v1/tenants/{id}/configuration-templates/{templateId}/apply` | Apply a reusable template as tenant-specific configuration |
| `POST` | `/admin/v1/tenants/{id}/invite-admin` | Create first super-admin and send invite email only by explicit Manage/Configure invite action |
| `GET` | `/admin/v1/tenants/{id}/provisioning-summary` | Return review data, missing steps, warnings, and activation blockers |

Commercial terms track the tenant's commercial model (`subscription` or `full_license_maintenance`), billing cycle/currency, contract dates, payment collection mode, gateway references, manual billing evidence, payment exception/grace dates, full-license payment evidence, maintenance status/renewal date, discount, Work Management storage limits, AI token limits, and any custom contract value. Plans are reusable catalog records; operators do not create a new plan per tenant unless product intentionally creates a reusable custom plan. Module entitlements are resolved from the active subscription/commercial plan, plan allowed modules, tenant module grants, and tenant feature grants; RBAC permissions are filtered after entitlement resolution.

Payment collection rules:

- Normal subscription tenants use gateway collection for recurring SaaS fees (`subscription_collection_mode = gateway`), unless a reviewed manual exception is recorded.
- Full-license tenants may record the one-time license sale manually (`license_payment_mode = manual`) with license amount, paid date, and reference.
- Full-license maintenance/support is separate from the one-time license and normally uses gateway collection (`maintenance_collection_mode = gateway`) for recurring maintenance fees.
- Manual collection modes require an audit reason and should be treated as exceptions.
- The primary Phase 1 gateway providers are `stripe` and `payhere`. Gateway secrets are stored in encrypted gateway config records or environment variables and are never returned by admin APIs.

Reusable package/module default prices are managed through `module_catalog.price_brackets`; reusable plan prices are calculated from selected packages/modules and company-size range, with optional plan-level overrides. Tenant-specific negotiated pricing is managed through `/admin/v1/tenants/{id}/subscription` and `/admin/v1/tenants/{id}/modules`. Updating a catalog base price must not silently rewrite existing tenant commercial records.

Plan price calculation contract:

- Company-size range values come from the same dropdown used by tenant creation.
- `POST/PATCH /admin/v1/subscription-plans` accepts selected module keys and company-size range, returns calculated monthly/annual prices, and stores optional override monthly/annual prices separately.
- Example: `core_hr` at `$3.50` plus `work_management` at `$4.00` for `51-200` employees returns `$7.50` per employee.
- AI-enabled plans must include a positive `ai_token_limit_per_month`; non-AI plans leave it null.
- Work Management plans with storage-backed features must include a positive storage limit or selected plan default; non-Work Management plans leave it null.
- `/admin/v1/tenants/{id}/subscription` stores a tenant subscription snapshot of selected packages/modules, company-size range, calculated prices, monthly/annual/full-license/maintenance override prices, AI token limit, storage limit, manual billing evidence references, and payment exception/grace dates.

Module permission ownership contract:

- Each permission belongs to exactly one module.
- Module Catalog APIs must show the owning module for every assigned permission.
- A permission already assigned to one module cannot be assigned to another module unless it is explicitly removed from the original module first.
- Tenant permission catalogs and role-template APIs use module ownership plus tenant entitlements to decide what permissions can be shown or assigned.

Module sales states are commercial states. `available` and `quoted` do not grant tenant-facing access. `purchased`, `trial`, `subscription_included`, and `maintenance_included` can grant access while the entitlement is valid.

Role templates are reusable blueprints. Applying a template creates normal tenant-scoped Auth roles. Operators may also create tenant-specific roles directly during Manage/Configure without saving them as reusable templates. Role creation does not require job levels; job levels only matter later for hierarchy scope and workflow routing.

---

## Feature Flag Manager

Controls global feature flag defaults and per-tenant overrides.

| Method | Path | Description |
|---|---|---|
| `GET` | `/admin/v1/feature-flags` | List all flags with their global defaults |
| `GET` | `/admin/v1/feature-flags/{flag}` | Get flag detail including per-tenant overrides |
| `PATCH` | `/admin/v1/feature-flags/{flag}` | Toggle global default for a flag |
| `PUT` | `/admin/v1/tenants/{id}/feature-flags` | Set all feature flag overrides for a tenant (replaces existing) |
| `PATCH` | `/admin/v1/tenants/{id}/feature-flags/{flag}` | Set a single feature flag override for a tenant |

---

## Agent Version Manager

Manages desktop agent versions, release channels, update rings, and force-update commands.

| Method | Path | Description |
|---|---|---|
| `GET` | `/admin/v1/agent-versions` | List version catalog |
| `POST` | `/admin/v1/agent-versions` | Publish a new agent version |
| `PATCH` | `/admin/v1/agent-versions/{id}/channel` | Change version channel (`stable` / `beta` / `recalled`) |
| `POST` | `/admin/v1/agent-versions/{id}/force-update` | Push `UPDATE_AGENT` command to all agents on this version in a ring |
| `GET` | `/admin/v1/agent-rings` | List rings and their tenant assignments |
| `PUT` | `/admin/v1/tenants/{id}/agent-ring` | Assign tenant to an update ring |

---

## Audit Console

Cross-tenant audit log access for platform administrators.

| Method | Path | Description |
|---|---|---|
| `GET` | `/admin/v1/audit-logs` | Query cross-tenant audit log (supports filtering by tenant, date, action type) |

---

## System Config

Manages global tenant setting defaults and per-tenant overrides.

| Method | Path | Description |
|---|---|---|
| `GET` | `/admin/v1/config/defaults` | Get global tenant setting defaults |
| `PATCH` | `/admin/v1/config/defaults` | Update global tenant setting defaults |
| `GET` | `/admin/v1/tenants/{id}/settings` | Get per-tenant settings |
| `PATCH` | `/admin/v1/tenants/{id}/settings` | Override per-tenant settings |

---

## Platform API Keys — Phase 2

> These endpoints are planned for Phase 2 and are not available in Phase 1.

Manages long-lived API keys for programmatic access to the Admin API (CI/CD, external tooling).

| Method | Path | Description |
|---|---|---|
| `GET` | `/admin/v1/api-keys` | List all active platform API keys |
| `POST` | `/admin/v1/api-keys` | Issue a new platform API key |
| `DELETE` | `/admin/v1/api-keys/{id}` | Revoke a platform API key |
