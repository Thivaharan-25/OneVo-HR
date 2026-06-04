# Developer Platform Subscription Provisioning — Implementation Plan (v2)

> **Revision: 2026-05-11 — full rewrite.** Resolves all architectural flaws found in v1 review.
> **For agentic workers:** Phase 0 is a hard gate. Do not begin Phase 1 until every Phase 0 task is resolved or explicitly accepted as deferred technical debt with a written note.

---

## Goal

Cleanly implement the Developer Platform provisioning backend: subscription plan catalog, module catalog with configurable permissions, payment gateway config, tenant subscription snapshot, tenant module entitlements as the runtime access source of truth, invite-admin cleanup, and activation rules.

---

## Two-Step Backend Contract

The provisioning backend has exactly two core write steps to create a tenant:


| Step | Endpoint                                    | What it holds                                                                                                                 |
| ---- | ------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| 1    | `POST /admin/v1/tenants`                    | Account details, setup configuration selections (one-time charges), optional inline owner invite                              |
| 2    | `PATCH /admin/v1/tenants/{id}/subscription` | Plan selection, commercial model, billing terms, pricing, payment config — auto-syncs module entitlements in same transaction |


Additional provisioning endpoints (modules override, roles, settings, activation) follow after Step 2. The 7-step wizard in `provisioning-flow.md` is a UX concern. The backend enforces only these two required write steps before activation is possible.

**Correction to previous plan (`2026-05-10-module-entitlement-role-seeding`):** `SubscriptionInfoRequest` (containing `PlanId`, `BillingCycle`, `CommercialModel`) was added to `CreateTenantRequest` in that plan. This is wrong. `POST /admin/v1/tenants` must not require or accept plan selection. Those fields belong exclusively in `PATCH /admin/v1/tenants/{id}/subscription`. The `TenantConfigurationSetup` and `OwnerInvite` fields stay in `POST /admin/v1/tenants`.

---

## Resolved Decisions

These were listed as open in v1. All are now decided:

1. **Plan selection placement:** `plan_id` is required in `PATCH .../subscription`, not in `POST /admin/v1/tenants`. Tenant creation produces a bare `provisioning` draft.
2. **Module entitlement sync rule:** `PATCH .../subscription` upserts `TenantModuleEntitlement` records from the plan's `default_module_keys` in the same database transaction. `PUT .../modules` allows post-sync manual per-module override. The entitlement table is always the runtime source of truth. The subscription snapshot's `snapshot_module_keys` is a historical audit field only — it is never read for access checks.
3. **Full-license payment evidence:** Payment evidence fields (`payment_method`, `payment_reference`) are stored as nullable and are only required to be filled before activation when `license_payment_status = paid`. An operator may create a tenant, save commercial terms with `payment_status = pending`, and record evidence later via another `PATCH .../subscription` call before or after activation. Evidence fields are only relevant when `collection_mode = manual`; the frontend should conditionally show them, but the backend stores them as nullable regardless.
4. **Payment statuses and modes:**
  - `collection_mode: manual | gateway` — applies separately to subscription recurring, license one-time, and maintenance recurring
  - `payment_status: pending | paid | waived | failed` — applies separately to each payment type
  - `manual` mode enables `payment_method` (e.g., `manual_bank_transfer`, `manual_cheque`) and `payment_reference` fields
  - `gateway` mode requires a `gateway_id` FK to a configured payment gateway record
5. **Invite-admin idempotency:** `POST /admin/v1/tenants/{id}/invite-admin` checks for an existing active non-expired invite. If one exists, returns its metadata without re-sending. Caller must pass `"resend": true` to replace and resend. Endpoint is blocked after activation unless it becomes a general tenant-user invitation path.
6. **Activation status:** `tenant.status` transitions `provisioning -> pending_confirmation -> pending_payment -> active`. No trial is created during tenant creation. `tenant_subscription.status` carries `pending_confirmation | pending_payment | active | grace_period | suspended | cancelled` separately from tenant status.
7. **Module permissions (catalog-owned, seeded-code driven):** permission codes are seeded/version-controlled by the backend permission catalog. Module Catalog assigns those existing codes to modules through `module_permission_ownership`, with `is_default_permission` marking codes for future tenant Owner role materialization. When a module entitlement becomes access-granting, the tenant permission catalog is built from ownership rows for active modules.
8. **Payment gateways:** Phase 1 supports `stripe`, `paddle`, and `payhere`. Gateway is selected by the ONEVO operator per tenant subscription/commercial setup. Tenant owners do not choose the gateway. Config is stored as an encrypted JSON blob per provider. Admin API never returns secrets.

---

## Data Model Contracts

### TenantSubscription (commercial snapshot)


| Field                                      | Notes                                                                             |
| ------------------------------------------ | --------------------------------------------------------------------------------- |
| `plan_id`                                  | FK → `subscription_plans`                                                         |
| `commercial_model`                         | `subscription | full_license_maintenance`                                         |
| `billing_cycle`                            | `monthly | annual` — applies to subscription recurrence or maintenance recurrence |
| `calculated_price_monthly`                 | Sum from subscription plan employee-count pricing tier selected by confirmed employee count                   |
| `calculated_price_annual`                  | Calculated annual equivalent                                                      |
| `override_price_monthly`                   | Operator override; preserves calculated for audit                                 |
| `override_price_annual`                    | Operator override                                                                 |
| `ai_token_limit_per_month`                 | Positive for AI-enabled plans; null otherwise                                     |
| `snapshot_module_keys`                     | JSON array — historical audit only, never used for access checks                  |
| `contract_start_date`, `contract_end_date` | Contract window                                                                   |
| `unpaid_grace_days`                        | From plan at time of snapshot                                                     |
| `subscription_collection_mode`             | `manual | gateway`                                                                |
| `subscription_gateway_id`                  | FK → `payment_gateway_configs` when gateway mode                                  |
| `subscription_payment_status`              | `pending | paid | waived | failed`                                                |
| `license_amount`                           | Full-license only                                                                 |
| `license_currency`                         | Full-license only                                                                 |
| `license_collection_mode`                  | `manual | gateway` — full-license only                                            |
| `license_gateway_id`                       | FK → `payment_gateway_configs` when gateway — full-license only                   |
| `license_payment_status`                   | `pending | paid | waived | failed` — full-license only                            |
| `license_payment_method`                   | e.g. `manual_bank_transfer` — only when `license_collection_mode = manual`        |
| `license_payment_reference`                | Bank ref, cheque number, etc. — only when manual                                  |
| `license_payment_evidence_url`             | Optional even when manual                                                         |
| `license_paid_date`                        | Date of confirmed payment                                                         |
| `maintenance_collection_mode`              | `manual | gateway | waived` — full-license only                                   |
| `maintenance_gateway_id`                   | FK when gateway                                                                   |
| `maintenance_payment_status`               | `pending | paid | waived | failed`                                                |
| `maintenance_renewal_date`                 |                                                                                   |
| `discount`                                 |                                                                                   |
| `custom_contract_value`                    | Negotiated total                                                                  |
| `audit_reason`                             | Required for manual mode, override prices, discount, custom value                 |


### TenantModuleEntitlement (runtime access source of truth)


| Field                | Notes                                                                                                     |
| -------------------- | --------------------------------------------------------------------------------------------------------- |
| `module_key`         |                                                                                                           |
| `state`              | `available | quoted | purchased | subscription_included | maintenance_included | disabled`        |
| `source`             | `plan_sync` (auto-upserted from subscription patch) or `manual_override` (operator via PUT modules)       |
| `started_at`         | When entitlement began                                                                                    |
| `expires_at`         | End date; null = no expiry                                                                                |
| `price_override`     | Tenant-specific price for this module                                                                     |
| `currency`           |                                                                                                           |
| `is_access_granting` | Computed: state in {`purchased`, `subscription_included`, `maintenance_included`} AND not expired |


### PaymentGateway


| Field              | Notes                                                |
| ------------------ | ---------------------------------------------------- |
| `provider`         | `stripe`, `paddle`, or `payhere`                          |
| `name`             | Display name e.g. `Paddle UK`, `PayHere Sri Lanka`   |
| `country_codes`    | JSON array e.g. `["GB"]`, `["LK"]`                   |
| `environment`      | `sandbox | production`                               |
| `config_encrypted` | AES-256 JSON blob with all provider-specific secrets |
| `is_active`        |                                                      |


Paddle config blob keys: `api_key`, `client_token`, `seller_id`, `webhook_secret`.
PayHere config blob keys: `merchant_id`, `merchant_secret`, `webhook_secret`.
Admin API never returns any secret fields.

### ModulePermissionOwnership

| Field | Notes |
|---|---|
| `module_key` | FK to `module_catalog` |
| `permission_code` | FK to the seeded tenant-facing permission catalog |
| `is_default_permission` | Included in the tenant Owner role during future tenant activation |

These rows populate the tenant permission catalog when a module entitlement is access-granting. The `DefaultRoleSeeder` reads default permissions from `module_permission_ownership` for active modules. Permission codes themselves remain seeded/version-controlled and are not created by Module Catalog.

---

## Architecture Guardrails

- `POST /admin/v1/tenants` never creates or selects a subscription plan. It creates a bare provisioning draft.
- `PATCH .../subscription` is the only place `plan_id` is written. It always auto-syncs entitlement records in the same transaction.
- `PUT .../modules` overrides individual entitlement records after sync. It never re-derives from plan.
- `TenantModuleEntitlement` is always the runtime access source of truth. Never read `snapshot_module_keys` for access decisions.
- Changing module catalog base pricing does not rewrite existing tenant subscription snapshots.
- Changing plan catalog data does not silently update tenant snapshots.
- Payment secrets are never returned from any admin API response.
- `DefaultRoleSeeder` reads default permission ownership rows from `module_permission_ownership` for active modules.
- RBAC is downstream of entitlements: module entitlements decide what permissions can exist; roles decide who gets them.

---

## Phase 0: Architecture Cleanup (Hard Gate)

> Do not begin Phase 1 until all tasks below are resolved or individually accepted as deferred debt with a written note in this file.

### Task A: Fix Folder and Namespace Mismatch

**Target folder structure:**

```
ONEVO.Application/
└── Features/
    ├── Tenancy/
    │   ├── Commands/
    │   ├── Queries/
    │   ├── DTOs/
    │   │   ├── Requests/
    │   │   └── Responses/
    │   ├── Provisioning/
    │   └── Repositories/
    ├── SharedPlatform/
    │   ├── SubscriptionPlans/
    │   │   ├── Commands/
    │   │   ├── Queries/
    │   │   ├── DTOs/
    │   │   └── Repositories/
    │   ├── ModuleCatalog/
    │   │   ├── Commands/
    │   │   ├── Queries/
    │   │   ├── DTOs/
    │   │   └── Repositories/
    │   └── Billing/
    │       ├── Commands/
    │       ├── Queries/
    │       └── DTOs/
    └── Auth/
        ├── Commands/
        ├── Queries/
        ├── DTOs/
        └── Repositories/
```

**Files to inspect first:**

- `src/ONEVO.Application/Features/Tenancy/Commands/`*
- `src/ONEVO.Application/Features/Tenancy/DTOs/*`
- `src/ONEVO.Application/Features/Tenancy/Queries/*`
- `src/ONEVO.Application/Features/Auth/Commands/RefreshToken/*`
- Rename all `ONEVO.Application.Features.DevPlatform.*` namespaces in Tenancy files to `ONEVO.Application.Features.Tenancy.*`
- Move any Tenancy DTOs currently in `DevPlatform.DTOs` to `Features.Tenancy.DTOs`
- Fix `Commands/RefreshToken` namespace mismatch (`Commands.RefreshTokens` → `Commands.RefreshToken`)
- Update all controller, handler, validator, and test `using` statements
- Add or update an architecture test asserting `ONEVO.Application.Features.<Feature>` namespaces match physical folder paths
- Build after namespace cleanup before proceeding

### Task B: Split Mixed Type Files

**Known examples:**

- `src/ONEVO.Application/Features/Infrastructure/Interfaces/IUserService.cs`
- `src/ONEVO.Application/Features/SharedPlatform/Billing/TenantOneTimeChargeDto.cs`
- `src/ONEVO.Application/Features/Auth/Commands/AdminGoogleLogin/AdminGoogleLoginCommand.cs`
- `src/ONEVO.Application/Features/Infrastructure/Queries/GetCountryDefaults/GetCountryDefaultsQuery.cs`
- One public top-level type per file; tiny internal helper records may co-locate only when they have no other consumers
- Move `UserDto` out of `IUserService.cs`
- Rename or move `CreateUserCommand` from `IUserService.cs`; if it is not a MediatR request, do not call it `Command`
- Split billing request and response records into separate files
- Move command response DTOs to `DTOs/Responses/`
- Do not add new request/response records at the bottom of controller files

### Task C: Normalize Repository Contracts

**Known example:**

- `src/ONEVO.Application/Features/Auth/Repositories/AuthRepositoryInterfaces.cs`
- One repository interface per file — do not add to catch-all files
- New interfaces to create individually: `ISubscriptionPlanRepository.cs`, `IModuleCatalogRepository.cs`, `ITenantSubscriptionRepository.cs`, `ITenantModuleEntitlementRepository.cs`, `IPaymentGatewayRepository.cs`
- Keep interfaces in the feature that owns the aggregate
- Repository names must match aggregate ownership; no duplicate concepts across `DevPlatform`, `Tenancy`, and `SharedPlatform`

### Task D: Remove Web/Hosting Leakage From Application

**Files:**

- `src/ONEVO.Application/ONEVO.Application.csproj`
- `src/ONEVO.Application/Features/Auth/Commands/AdminLogin/AdminLoginCommandHandler.cs`
- Review why Application references `Microsoft.AspNetCore.App`
- Replace direct hosting/environment dependencies in handlers with an application-owned abstraction (`IApplicationEnvironment` or `IPlatformAdminCredentialProvider`)
- Implement the abstraction in Infrastructure or Api
- Remove `Microsoft.AspNetCore.App` from Application if no longer needed
- Add/keep architecture tests preventing Application from depending on ASP.NET Core hosting APIs

### Task E: Security Hygiene

**Files:**

- `src/ONEVO.Infrastructure/Encryption/NoOpEncryptionService.cs`
- `src/ONEVO.Infrastructure/DependencyInjection.cs`
- `src/ONEVO.Api/appsettings.json`
- `src/ONEVO.Api/appsettings.Development.json`
- Register `NoOpEncryptionService` only when `ASPNETCORE_ENVIRONMENT = Development`; make startup throw in Production/Staging when the real key is absent
- Move database passwords, API keys, SMTP credentials, JWT secrets, and dev admin passwords out of committed appsettings files
- Make startup validation fail loudly in non-development environments when unsafe crypto or missing secrets are detected

### Task F: Fix Tenant Create Contract to Remove SubscriptionInfoRequest

**Files:**

- `src/ONEVO.Application/Features/Tenancy/DTOs/Requests/CreateTenantRequest.cs`
- `src/ONEVO.Application/Features/Tenancy/Commands/CreateTenant/CreateTenantCommand.cs`
- `src/ONEVO.Application/Features/Tenancy/Commands/CreateTenant/CreateTenantCommandHandler.cs`
- `src/ONEVO.Api/Controllers/Admin/TenantsController.cs`

`SubscriptionInfoRequest` (with `PlanId`, `BillingCycle`, `CommercialModel`) was added to `CreateTenantRequest` in the `2026-05-10-module-entitlement-role-seeding` plan. This must be removed before Phase 1 begins.

- Remove `SubscriptionInfoRequest` record from `CreateTenantRequest.cs`
- Remove `SubscriptionInfo` record from `CreateTenantCommand.cs`
- Remove the `Subscription` parameter from `CreateTenantCommand`
- Remove subscription wiring from `TenantsController.Create`
- Remove subscription handling from `CreateTenantCommandHandler` — it no longer creates a `TenantSubscription` row; that happens exclusively in `PATCH .../subscription`
- Keep `TenantConfigurationSetup` and `OwnerInvite` in `CreateTenantRequest`
- Keep `TenantConfigurationSetup` and `OwnerInvite` handling in the handler
- Update validator: `CompanySizeRange` no longer needs to validate against plan pricing
- Update all affected unit tests to remove subscription fields from `CreateTenantCommand` calls
- Build and run tests after change

### Task G: Update Plan File Paths After Namespace Cleanup

- Replace every file path in Phases 1–5 with the exact resolved folder and namespace after Tasks A–E are done
- Confirm every file reference below resolves to a real file or is marked as "create new"

---

## Phase 1: Catalog Foundation APIs

### Task 1: Module Catalog with Configurable Permissions

**Purpose:** Implement module catalog CRUD plus `module_permission_ownership`. Permission codes stay seeded/version-controlled; Module Catalog owns the mapping from modules to permission codes and default Owner-role markers.

**Existing files:**

- `src/ONEVO.Domain/Features/SharedPlatform/Entities/ModuleCatalogItem.cs`
- `src/ONEVO.Domain/Services/ModulePricingCalculator.cs`
- `src/ONEVO.Infrastructure/Persistence/Configurations/SharedPlatform/ModuleCatalogItemConfiguration.cs`

**New files:**

- `src/ONEVO.Application/Features/SharedPlatform/ModuleCatalog/Repositories/IModuleCatalogRepository.cs`
- `src/ONEVO.Application/Features/SharedPlatform/ModuleCatalog/Commands/CreateModuleCatalogItem/CreateModuleCatalogItemCommand.cs`
- `src/ONEVO.Application/Features/SharedPlatform/ModuleCatalog/Commands/CreateModuleCatalogItem/CreateModuleCatalogItemCommandHandler.cs`
- `src/ONEVO.Application/Features/SharedPlatform/ModuleCatalog/Commands/CreateModuleCatalogItem/CreateModuleCatalogItemCommandValidator.cs`
- `src/ONEVO.Application/Features/SharedPlatform/ModuleCatalog/Commands/UpdateModuleCatalogItem/` (same structure)
- `src/ONEVO.Application/Features/SharedPlatform/ModuleCatalog/Queries/GetModuleCatalog/GetModuleCatalogQuery.cs`
- `src/ONEVO.Application/Features/SharedPlatform/ModuleCatalog/Queries/GetModuleCatalog/GetModuleCatalogQueryHandler.cs`
- `src/ONEVO.Application/Features/SharedPlatform/ModuleCatalog/DTOs/Requests/CreateModuleCatalogItemRequest.cs`
- `src/ONEVO.Application/Features/SharedPlatform/ModuleCatalog/DTOs/Requests/UpdateModuleCatalogItemRequest.cs`
- `src/ONEVO.Application/Features/SharedPlatform/ModuleCatalog/DTOs/Responses/ModuleCatalogItemDto.cs`
- `src/ONEVO.Infrastructure/Persistence/Repositories/SharedPlatform/EfModuleCatalogRepository.cs`

**Controller:** `src/ONEVO.Api/Controllers/Admin/ModuleCatalogController.cs`

- Add `module_permission_ownership` entity/table with `module_key`, `permission_code`, and `is_default_permission`
- Add `phase`, `pillar`, `pricing_unit`, `price_brackets` (JSON), `full_license_price`, `maintenance_rate`, `is_sellable`, `is_active` to entity if not present
- Implement `GET /admin/v1/modules/catalog` — list all modules, include pricing, sellable state, and permission ownership summary
- Implement `POST /admin/v1/modules/catalog` — create module with price brackets and permission ownership rows
- Implement `PATCH /admin/v1/modules/catalog/{moduleKey}` — update metadata, pricing, permissions, sellable/active state
- Validate employee-count pricing tier overlap, missing open-ended bracket, invalid currency, duplicate module keys
- Update `DefaultRoleSeeder` to read default permission rows from `module_permission_ownership` for each access-granting module.
- Update `IModuleEntitlementService` tenant permission catalog builder to use catalog data
- Ensure changing module base pricing never rewrites existing `TenantSubscription` snapshots
- Add unit tests for `ModulePricingCalculator` edge cases (missing bracket, open-ended fallback, empty module set)
- Add integration tests for list/create/update catalog APIs
- Add tests verifying `DefaultRoleSeeder` reads permissions from catalog, not constants

### Task 2: Subscription Plan APIs

**Existing files:**

- `src/ONEVO.Domain/Features/SharedPlatform/Entities/SubscriptionPlan.cs`
- `src/ONEVO.Infrastructure/Persistence/Configurations/SharedPlatform/SubscriptionPlanConfiguration.cs`
- `src/ONEVO.Application/Features/DevPlatform/Repositories/ISubscriptionPlanRepository.cs` (relocate to `SharedPlatform/SubscriptionPlans/Repositories/`)

**New files:** Follow the same pattern as Task 1 under `Features/SharedPlatform/SubscriptionPlans/`.

- Implement `GET /admin/v1/subscription-plans` — list with calculated/override prices, included modules, AI token limit, active state
- Implement `POST /admin/v1/subscription-plans` — create from module keys + employee-count pricing tiers; auto-calculate monthly/annual rates from the plan tier table; store calculated and override prices separately
- Implement `PATCH /admin/v1/subscription-plans/{id}` — update metadata, modules, pricing bands, active state, AI token limit and active state
- Validate: AI-enabled plans require positive `ai_token_limit_per_month`; non-AI plans store null
- Prevent deactivating a plan if active tenant subscriptions reference it (return a blocker response listing affected tenants)
- Add integration tests for list/create/update plan APIs
- Add unit tests for plan price calculation (multi-module sum, override preservation, employee-count tier lookup)

### Task 3: Payment Gateway Config APIs

**New files:**

- `src/ONEVO.Domain/Features/SharedPlatform/Entities/PaymentGateway.cs`
- `src/ONEVO.Infrastructure/Persistence/Configurations/SharedPlatform/PaymentGatewayConfiguration.cs`
- `src/ONEVO.Application/Features/SharedPlatform/Billing/Repositories/IPaymentGatewayRepository.cs`
- `src/ONEVO.Application/Features/SharedPlatform/Billing/Commands/CreatePaymentGateway/`
- `src/ONEVO.Application/Features/SharedPlatform/Billing/Commands/UpdatePaymentGateway/`
- `src/ONEVO.Application/Features/SharedPlatform/Billing/Queries/GetPaymentGateways/`
- `src/ONEVO.Application/Features/SharedPlatform/Billing/DTOs/Requests/CreatePaymentGatewayRequest.cs`
- `src/ONEVO.Application/Features/SharedPlatform/Billing/DTOs/Requests/UpdatePaymentGatewayRequest.cs`
- `src/ONEVO.Application/Features/SharedPlatform/Billing/DTOs/Responses/PaymentGatewayDto.cs`
- `src/ONEVO.Infrastructure/Persistence/Repositories/SharedPlatform/EfPaymentGatewayRepository.cs`

**Controller:** add to `src/ONEVO.Api/Controllers/Admin/PaymentGatewaysController.cs`

Gateway domain entity fields: `id`, `provider` (`stripe`, `paddle`, or `payhere`), `name`, `country_codes` (JSON), `environment` (`sandbox | production`), `config_encrypted` (AES-256 JSON blob), `is_active`, `created_at`, `updated_at`.

Stripe config blob: `secret_key`, `publishable_key`, `webhook_secret`.
Paddle config blob: `api_key`, `client_token`, `seller_id`, `webhook_secret`.
PayHere config blob: `merchant_id`, `merchant_secret`, `webhook_secret`.

- Implement `GET /admin/v1/payment-gateways` — list metadata only; never return secret fields
- Implement `POST /admin/v1/payment-gateways` — accept plaintext secrets in request body, encrypt with `IEncryptionService` before storing
- Implement `PATCH /admin/v1/payment-gateways/{id}` — update metadata or rotate secrets (re-encrypt on write)
- Validate `provider` is `stripe`, `paddle`, or `payhere`; validate required config keys per provider
- Response DTO must omit all encrypted/secret fields; include only `id`, `provider`, `name`, `country_codes`, `environment`, `is_active`
- Add unit tests for encryption roundtrip and missing-key validation per provider
- Add integration tests for list/create/update gateway APIs

---

## Phase 2: Fix Tenant Create Contract

### Task 4: Finalize `POST /admin/v1/tenants`

> Phase 0 Task F already removes `SubscriptionInfoRequest`. This task validates the resulting contract is complete and correct.

**Files:**

- `src/ONEVO.Application/Features/Tenancy/DTOs/Requests/CreateTenantRequest.cs`
- `src/ONEVO.Application/Features/Tenancy/Commands/CreateTenant/CreateTenantCommand.cs`
- `src/ONEVO.Application/Features/Tenancy/Commands/CreateTenant/CreateTenantCommandValidator.cs`
- `src/ONEVO.Application/Features/Tenancy/Commands/CreateTenant/CreateTenantCommandHandler.cs`
- `src/ONEVO.Api/Controllers/Admin/TenantsController.cs`

`POST /admin/v1/tenants` accepted body after cleanup:

```
company_name (required)
slug (required, unique)
industry_profile (required)
estimated_employee_count (optional profile estimate; not used as final invoice quantity)
legal_entity_name (required)
registration_number (optional)
country (required)
timezone (required)
currency (required)
tenant_configuration_setup.setup_options (optional string[]: position_template_setup | employee_invite | role_permission_configuration)
owner_invite (optional):
  email, first_name, last_name, completion_methods, allow_google_email_mismatch, allowed_email_domains
```

State written by handler: `tenants` row (`status = provisioning`), primary `legal_entities` row when activation/setup seeding runs, `tenant_settings` defaults, `TenantSetupSelection` rows per selected option, `TenantOneTimeCharge` rows per selected option, optional owner invite record + Owner role assignment. No `TenantSubscription` row is created.

- Confirm `SubscriptionInfoRequest` and `SubscriptionInfo` are fully removed (Phase 0 Task F prerequisite)
- Confirm `TenantConfigurationSetup` and `OwnerInvite` are present and correctly handled
- Validator: validate estimated employee count is positive when supplied; final invoice pricing waits for tenant-owner-confirmed employee count
- Validator: validate `setup_options` values are known setup keys, not module keys
- Owner invite: assign auto-seeded Owner role; do not accept operator-provided `role_id`
- Handler must not create any `TenantSubscription` row
- Add/update unit tests for the updated request contract
- Confirm build passes and all existing tenant creation tests pass

---

## Phase 3: Tenant Subscription Patch + Entitlement Auto-Sync

### Task 5: `PATCH /admin/v1/tenants/{id}/subscription`

This is the most complex endpoint. It must update the subscription snapshot and auto-sync entitlement records in a single transaction.

**New files:**

- `src/ONEVO.Application/Features/Tenancy/Commands/UpdateTenantSubscription/UpdateTenantSubscriptionCommand.cs`
- `src/ONEVO.Application/Features/Tenancy/Commands/UpdateTenantSubscription/UpdateTenantSubscriptionCommandHandler.cs`
- `src/ONEVO.Application/Features/Tenancy/Commands/UpdateTenantSubscription/UpdateTenantSubscriptionCommandValidator.cs`
- `src/ONEVO.Application/Features/Tenancy/DTOs/Requests/UpdateTenantSubscriptionRequest.cs`
- `src/ONEVO.Application/Features/Tenancy/DTOs/Responses/TenantSubscriptionDto.cs`
- `src/ONEVO.Application/Features/Tenancy/Repositories/ITenantSubscriptionRepository.cs`
- `src/ONEVO.Application/Features/Tenancy/Repositories/ITenantModuleEntitlementRepository.cs`
- `src/ONEVO.Infrastructure/Persistence/Repositories/EfTenantSubscriptionRepository.cs`
- `src/ONEVO.Infrastructure/Persistence/Repositories/EfTenantModuleEntitlementRepository.cs`

**Controller action:** add `UpdateSubscription` to `src/ONEVO.Api/Controllers/Admin/TenantsController.cs`

**Request body fields:**

Shared (all commercial models):

```
plan_id (required)
commercial_model: subscription | full_license_maintenance (required)
confirmed_employee_count (required during tenant-owner subscription confirmation for first invoice pricing tier and quantity)
selected_module_keys (required — drives auto-sync)
override_price_monthly (optional)
override_price_annual (optional)
ai_token_limit_per_month (required when plan is AI-enabled)
contract_start_date (optional)
contract_end_date (optional)
discount (optional)
custom_contract_value (optional)
audit_reason (required when: manual collection mode, price override, discount, custom_contract_value, post-activation change)
```

When `commercial_model = subscription`:

```
billing_cycle: monthly | annual (required)
subscription_collection_mode: manual | gateway (required)
subscription_gateway_id (required when gateway)
subscription_payment_status: pending | paid | waived | failed (required)
```

When `commercial_model = full_license_maintenance`:

```
license_amount (required)
license_currency (required)
license_collection_mode: manual | gateway (required)
license_gateway_id (required when gateway)
license_payment_status: pending | paid | waived | failed (required)
license_payment_method (optional; relevant when manual — e.g. manual_bank_transfer)
license_payment_reference (optional; relevant when manual)
license_payment_evidence_url (optional)
license_paid_date (optional)
maintenance_collection_mode: manual | gateway | waived (required)
maintenance_gateway_id (required when maintenance gateway)
maintenance_payment_status: pending | paid | waived | failed (required)
maintenance_renewal_date (required unless waived)
```

**Handler logic (all in one transaction):**

1. Validate plan exists and is active
2. Validate gateway refs exist and match provider
3. Calculate `calculated_price_monthly` and `calculated_price_annual` from the selected subscription plan employee-count tier using tenant-owner-confirmed employee count
4. Upsert `TenantSubscription` row with full snapshot
5. Set `snapshot_module_keys` = `selected_module_keys` (historical audit only)
6. Load plan's `default_module_keys` from `SubscriptionPlan`
7. For each key in `selected_module_keys` that exists in `default_module_keys`: upsert `TenantModuleEntitlement` with `state = subscription_included`, `source = plan_sync`
8. For any `TenantModuleEntitlement` with `source = plan_sync` that is no longer in `selected_module_keys`: set `state = disabled`
9. Do not touch entitlements where `source = manual_override`
10. Commit transaction

- Implement all above
- Validate `audit_reason` is present for all audit-required field changes
- Enforce commercial model-specific required fields
- Ensure `calculated_price_`* is always stored even when override is set
- Add tests: subscription monthly, subscription annual, full-license-maintenance, gateway vs manual, entitlement sync from plan, manual override entitlements are preserved, audit reason enforcement
- Add test: calling PATCH twice with changed module keys updates `plan_sync` entitlements correctly

---

## Phase 4: Tenant Module Entitlement Override

### Task 6: `PUT /admin/v1/tenants/{id}/modules`

This endpoint allows operators to override or extend individual entitlements after the auto-sync from Phase 3.

**New files:**

- `src/ONEVO.Application/Features/Tenancy/Commands/SetTenantModules/SetTenantModulesCommand.cs`
- `src/ONEVO.Application/Features/Tenancy/Commands/SetTenantModules/SetTenantModulesCommandHandler.cs`
- `src/ONEVO.Application/Features/Tenancy/Commands/SetTenantModules/SetTenantModulesCommandValidator.cs`
- `src/ONEVO.Application/Features/Tenancy/DTOs/Requests/SetTenantModulesRequest.cs`
- `src/ONEVO.Application/Features/Tenancy/DTOs/Responses/TenantModuleEntitlementDto.cs`

**Controller action:** add to `TenantsController`

Request body: array of module entitlement records, each with `module_key`, `state`, `started_at`, `expires_at`, `price_override`, `currency`.

Handler logic:

1. For each record in request: upsert `TenantModuleEntitlement` with `source = manual_override`
2. Recompute tenant permission catalog from all access-granting entitlements using `module_permission_ownership`
3. For any tenant role that has permissions outside the new module boundary: remove out-of-boundary permissions and record an audit event
4. Commit transaction

- Implement all above
- `is_access_granting` computed from state + expiry — implement as a computed property or DB check constraint
- Only access-granting states grant permissions: `purchased`, `subscription_included`, `maintenance_included`
- `available` and `quoted` are visible in console but do not appear in the permission catalog
- Add activation checklist blocker for zero access-granting modules at activation time
- Add tests: manual state override, expiry-based access revocation, permission boundary enforcement after module removal

---

## Phase 5: Invite-Admin Cleanup

### Task 7: Refactor `POST /admin/v1/tenants/{id}/invite-admin`

**Files:**

- `src/ONEVO.Application/Features/Tenancy/Commands/InviteTenantAdmin/InviteTenantAdminCommand.cs`
- `src/ONEVO.Application/Features/Tenancy/Commands/InviteTenantAdmin/InviteTenantAdminCommandHandler.cs`
- `src/ONEVO.Application/Features/Tenancy/Commands/InviteTenantAdmin/InviteTenantAdminCommandValidator.cs`
- `src/ONEVO.Application/Features/Tenancy/DTOs/Requests/InviteTenantAdminRequest.cs`
- Remove `role_id` from `InviteTenantAdminRequest`; endpoint always assigns the auto-seeded Owner role
- Idempotency: before creating a new invite, check for existing active non-expired invite for this tenant. If found, return its metadata with `"already_active": true` without resending
- Add `resend` boolean field to request body. When `resend: true`, replace active invite and send new email even if one already exists
- Block endpoint after `tenant.status = active` (return 409 with message explaining to use tenant-user invitation flow)
- Allow during `provisioning` status: initial invite, expired invite replacement, failed delivery correction
- Add tests: initial invite, duplicate call returns existing, resend flag replaces, post-activation block, both inline (from tenant create) and deferred invite paths result in same Owner role assignment

---

## Phase 6: Activation

### Task 8: `PATCH /admin/v1/tenants/{id}/provision/confirm`

Verify this endpoint exists. If not, implement it in this task.

**Files (verify or create):**

- `src/ONEVO.Application/Features/Tenancy/Commands/ConfirmTenantProvisioning/ConfirmTenantProvisioningCommand.cs`
- `src/ONEVO.Application/Features/Tenancy/Commands/ConfirmTenantProvisioning/ConfirmTenantProvisioningCommandHandler.cs`
- `src/ONEVO.Application/Features/Tenancy/Commands/ConfirmTenantProvisioning/ConfirmTenantProvisioningCommandValidator.cs`

Handler logic:

1. Run full activation checklist (see Task 9 blockers below)
2. If any blocker is present, return `422` with checklist response — do not activate
3. Set `tenant.status = active`
4. Set `tenant_subscription.status = pending_confirmation` until the tenant owner selects plan, billing cycle, and confirms employee count. After first invoice is paid or manually approved, set `tenant_subscription.status = active`.
6. Emit activation audit event
7. Commit

- Implement or verify endpoint exists
- Implement activation status logic (`pending_confirmation` -> `pending_payment` -> `active`) per resolved decision 6
- Ensure tenant becomes visible to the main OneVo app after status = active
- Ensure the invited admin can set their password before activation but cannot log in until status = active
- Add tests: activation succeeds with all prerequisites met, activation blocked per each individual missing prerequisite, pending confirmation set correctly, pending payment after first invoice generation, active after payment confirmation

### Task 9: Provisioning Summary + Activation Checklist

**Files:**

- `src/ONEVO.Application/Features/Tenancy/Queries/GetProvisioningSummary/GetProvisioningSummaryQuery.cs`
- `src/ONEVO.Application/Features/Tenancy/Queries/GetProvisioningSummary/GetProvisioningSummaryQueryHandler.cs`
- `src/ONEVO.Application/Features/Tenancy/Provisioning/ProvisioningReaders.cs`
- `src/ONEVO.Infrastructure/Tenancy/NotConfiguredYetReaders.cs`

**Activation blockers (all must be clear):**


| Blocker                                           | Check                                                                                                                 |
| ------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| Missing tenant details                            | `company_name`, `slug`, `country`, `timezone`, `currency` all present                                                 |
| No subscription snapshot                          | `TenantSubscription` row exists for this tenant                                                                       |
| No plan selected                                  | `plan_id` is set and plan is still active                                                                             |
| Invalid commercial model                          | `commercial_model` and required payment fields consistent                                                             |
| No access-granting modules                        | At least one `TenantModuleEntitlement` with `is_access_granting = true`                                               |
| Missing license evidence (optional at activation) | If `commercial_model = full_license_maintenance` and `license_payment_status = paid`, `license_paid_date` must be set |
| No Owner role                                     | At least one tenant role with Owner-level permissions exists                                                          |
| No owner invite                                   | Either inline invite in `CreateTenantCommand` or a `TenantAdminInvite` record exists for this tenant                  |
| Required settings missing                         | Module-required settings from `TenantSetupSelection` are configured                                                   |
| Role permission out of module boundary            | Zero roles have permissions outside the current module entitlement set                                                |


- Replace all `NotConfiguredYetReaders` for subscription/module/role/invite states with real DB-backed readers
- Return structured blockers response: each blocker with `code`, `message`, `is_blocking`
- Activation must fail with 422 and blockers list if any blocking item is unresolved
- Non-blocking warnings (e.g., license payment still `pending` for full-license) are returned in a `warnings` array but do not block activation
- Add stale-price warning: if `calculated_price_monthly` in snapshot diverges from current catalog calculation by more than 10%, include a non-blocking warning in summary
- Add tests per blocker: each blocker individually blocks activation; all clear allows activation

---

## Phase 7: Documentation

### Task 10: Align `OneVo-HR` Documentation

**Files:**

- `OneVo-HR/developer-platform/backend/api-contracts.md`
- `OneVo-HR/developer-platform/userflow/provisioning-flow.md`
- `OneVo-HR/developer-platform/userflow/tenant-management.md`
- `OneVo-HR/Userflow/Platform-Setup/tenant-provisioning.md`
- `OneVo-HR/Userflow/Platform-Setup/billing-subscription.md`
- `OneVo-HR/modules/shared-platform/subscriptions-billing/overview.md`
- `OneVo-HR/modules/shared-platform/subscriptions-billing/end-to-end-logic.md`
- State clearly that `POST /admin/v1/tenants` does NOT accept `plan_id`; it creates a bare provisioning draft
- State clearly that plan selection is `PATCH /admin/v1/tenants/{id}/subscription`
- State clearly that `PATCH .../subscription` auto-syncs module entitlements in the same transaction
- State clearly that `TenantModuleEntitlement` is the runtime access source of truth; `snapshot_module_keys` is historical audit only
- Document `payment_status` and `collection_mode` fields with allowed values; document that evidence fields are only relevant when `collection_mode = manual`
- Document `paddle` and `payhere` as Phase 1 gateway providers; document gateway config API
- Document `module_permission_ownership` and how it drives the permission catalog and Owner role seeding
- Update provisioning wizard UX steps to match the resolved 2-step backend contract:
  - Step 1: account details + setup configuration selections + optional owner invite → `POST /admin/v1/tenants`
  - Step 2: plan selection + commercial terms → `PATCH .../subscription`
  - Remaining steps: modules override, roles, settings, activation
- Document `POST /admin/v1/tenants/{id}/invite-admin` as deferred/resend only; Step 1 inline invite is the happy-path
- Remove all contradictions where docs describe subscription plan creation as part of tenant creation
- Add `GET/POST/PATCH /admin/v1/payment-gateways` to `api-contracts.md`

---

## Phase 8: Verification

### Task 11: Final Verification

- Run unit tests: tenancy, billing, module catalog, module pricing, DefaultRoleSeeder permissions-from-catalog
- Run integration tests covering:
  - Create module catalog item with permission ownership rows
  - Create subscription plan
  - Create payment gateways (Paddle, PayHere)
  - Create tenant — no plan fields in body, confirm no `TenantSubscription` row created
  - PATCH subscription monthly — confirm `TenantModuleEntitlement` rows auto-created with `plan_sync` source
  - PATCH subscription annual
  - PATCH subscription full-license-maintenance with manual payment
  - PATCH subscription full-license-maintenance with gateway payment
  - PUT modules — confirm `manual_override` source, plan_sync rows untouched
  - GET permissions catalog — returns only permissions from access-granting modules
  - Inline owner invite during tenant creation
  - Deferred invite via invite-admin endpoint
  - Resend invite with `resend: true`
  - Duplicate invite returns existing without resend
  - Activation blocked per each individual blocker
  - Successful activation sets `status = pending_confirmation`; subscription confirmation creates first invoice and moves to `pending_payment`; payment confirmation moves to `active`
  - `DefaultRoleSeeder` permissions match `module_permission_ownership` defaults for active modules
- Build `ONEVO.sln`
- Update API examples in docs after tests pass
- Confirm `DefaultRoleSeeder` reads `module_permission_ownership` rather than hardcoded permission constants
- Confirm no `NoOpEncryptionService` registered in non-development environments




