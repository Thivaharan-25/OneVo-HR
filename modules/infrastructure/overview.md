# Module: Infrastructure

**Namespace:** `ONEVO.Modules.Infrastructure`
**Phase:** 1 — Build
**Pillar:** 1 — HR Management
**Owner:** Dev 1 (Week 1)
**Tables:** 4
**Task File:** [[current-focus/DEV1-infrastructure-setup|DEV1: Infrastructure]]

---

## Purpose

Foundational module managing tenants, users (authentication identity), file uploads, and country reference data. All other modules depend on Infrastructure for multi-tenancy and user context.

---

## Dependencies

| Direction | Module | Interface | Purpose |
|:----------|:-------|:----------|:--------|
| **Depends on** | [[backend/shared-kernel\|Shared Kernel]] | `BaseEntity`, `BaseRepository`, `ITenantContext` | Foundation |
| **Consumed by** | All modules | `ITenantContext`, `IFileService`, `IUserService` | Multi-tenancy, files, users |

---

## Public Interface

```csharp
public interface ITenantService
{
    Task<Result<TenantDto>> ProvisionTenantAsync(CreateTenantCommand command, CancellationToken ct);
    Task<Result<TenantDto>> GetTenantAsync(Guid tenantId, CancellationToken ct);
    Task<Result<TenantDto>> UpdateTenantAsync(Guid tenantId, UpdateTenantCommand command, CancellationToken ct);
}

public interface IUserService
{
    Task<Result<UserDto>> CreateUserAsync(CreateUserCommand command, CancellationToken ct);
    Task<Result<UserDto>> GetUserByIdAsync(Guid userId, CancellationToken ct);
}

public interface IFileService
{
    Task<Result<FileRecordDto>> UploadFileAsync(Stream file, string fileName, string contentType, CancellationToken ct);
    Task<Result<Stream>> DownloadFileAsync(Guid fileId, CancellationToken ct);
}
```

---

## Database Tables (4)

### `tenants`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `name` | `varchar(200)` | Company name |
| `slug` | `varchar(100)` | URL-safe identifier, UNIQUE |
| `industry_profile` | `varchar(30)` | `office_it`, `manufacturing`, `retail`, `healthcare`, `custom` — **sets monitoring defaults at signup** |
| `status` | `varchar(20)` | `trial`, `active`, `suspended`, `cancelled` |
| `subscription_plan_id` | `uuid` | FK → subscription_plans |
| `settings_json` | `jsonb` | Tenant-level settings |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

**Note:** `industry_profile` is new — used by [[modules/configuration/overview|Configuration]] to set default monitoring feature toggles when a tenant signs up.

### `users`

Authentication identity. Linked 1:1 to `employees` (HR identity) via `user_id` on employees table.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `email` | `varchar(255)` | UNIQUE per tenant |
| `password_hash` | `varchar(255)` | bcrypt |
| `is_active` | `boolean` | |
| `email_verified` | `boolean` | |
| `last_login_at` | `timestamptz` | |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

### `file_records`

Metadata for all uploaded files (documents, avatars, screenshots, verification photos).

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `file_name` | `varchar(255)` | |
| `content_type` | `varchar(100)` | MIME type |
| `size_bytes` | `bigint` | |
| `storage_path` | `varchar(500)` | Blob storage path |
| `uploaded_by_id` | `uuid` | FK → users |
| `created_at` | `timestamptz` | |

### `countries`

Reference data — NOT tenant-scoped (global).

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `name` | `varchar(100)` | |
| `code` | `varchar(3)` | ISO 3166-1 alpha-3 |
| `phone_code` | `varchar(10)` | |
| `currency_code` | `varchar(3)` | |

---

## Code Location (Clean Architecture)

Domain entities:
  ONEVO.Domain/Features/InfrastructureModule/Entities/
  ONEVO.Domain/Features/InfrastructureModule/Events/

Application (CQRS):
  ONEVO.Application/Features/InfrastructureModule/Commands/
  ONEVO.Application/Features/InfrastructureModule/Queries/
  ONEVO.Application/Features/InfrastructureModule/DTOs/Requests/
  ONEVO.Application/Features/InfrastructureModule/DTOs/Responses/
  ONEVO.Application/Features/InfrastructureModule/Validators/
  ONEVO.Application/Features/InfrastructureModule/EventHandlers/

Infrastructure:
  ONEVO.Infrastructure/Persistence/Configurations/InfrastructureModule/

API endpoints:
  ONEVO.Api/Controllers/InfrastructureModule/InfrastructureModuleController.cs

---

## Domain Events (intra-module — MediatR)

> These events are published and consumed within this module only. They never leave the module.

| Event | Published When | Handler |
|:------|:---------------|:--------|
| _(none)_ | — | — |

## Integration Events (cross-module — RabbitMQ)

### Publishes

| Event | Routing Key | Published When | Consumers |
|:------|:-----------|:---------------|:----------|
| `TenantCreated` | `infrastructure.tenant.created` | New tenant provisioned | [[modules/configuration/overview\|Configuration]] (seed monitoring defaults), [[modules/org-structure/overview\|Org Structure]] (seed default department) |
| `TenantActivated` | `infrastructure.tenant.activated` | Tenant moves from trial to active | [[modules/shared-platform/overview\|Shared Platform]] |
| `TenantDeactivated` | `infrastructure.tenant.deactivated` | Tenant suspended or cancelled | [[modules/shared-platform/overview\|Shared Platform]] |
| `UserCreated` | `infrastructure.user.created` | New user record created | Downstream modules that need user context |
| `UserStatusChanged` | `infrastructure.user.status` | User activated or deactivated | [[modules/auth/overview\|Auth]] (update login access) |

### Consumes

| Event | Routing Key | Source Module | Action Taken |
|:------|:-----------|:-------------|:-------------|
| _(none)_ | — | — | — |

---

## Key Business Rules

1. **Tenant provisioning flow:** Signup → seed default data (roles, permissions, monitoring toggles based on `industry_profile`) → activate.
2. **Users ≠ Employees.** `users` is the login identity. `employees` is the HR identity in [[modules/core-hr/overview|Core Hr]]. They are 1:1 linked via `user_id` on the employees table. When working with HR features, always query through `employees`.
3. **Files are stored in blob storage** (Railway/S3). Only metadata lives in `file_records`.
4. **Countries table has no `tenant_id`** — it's global reference data.

---

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| POST | `/api/v1/tenants` | Public (signup) | Provision new tenant |
| GET | `/api/v1/tenants/current` | Authenticated | Get current tenant |
| PUT | `/api/v1/tenants/current` | `settings:admin` | Update tenant settings |
| GET | `/api/v1/users` | `users:read` | List users |
| POST | `/api/v1/users` | `users:manage` | Create user |
| PUT | `/api/v1/users/{id}` | `users:manage` | Update user |
| POST | `/api/v1/files/upload` | Authenticated | Upload file |
| GET | `/api/v1/files/{id}` | Authenticated | Download file |
| GET | `/api/v1/countries` | Authenticated | List countries |

## Features

- [[modules/infrastructure/tenant-management/overview|Tenant Management]] — Tenant provisioning, industry profile, subscription linking
- [[modules/infrastructure/user-management/overview|User Management]] — Authentication identity (login), linked 1:1 to employees
- [[modules/infrastructure/file-management/overview|File Management]] — File upload/download metadata; blobs in external storage
- [[modules/infrastructure/reference-data/overview|Reference Data]] — Global countries table (ISO codes, currency, phone codes)

---

## Related

- [[infrastructure/multi-tenancy|Multi Tenancy]] — Source of truth for `tenants` table and `ITenantContext`
- [[backend/shared-kernel|Shared Kernel]] — `BaseEntity`, `BaseRepository`, `ITenantContext` foundation
- [[security/data-classification|Data Classification]] — Files stored in blob storage; `password_hash` is bcrypt
- [[database/migration-patterns|Migration Patterns]] — Countries table is global (no `tenant_id`)
- [[current-focus/DEV1-infrastructure-setup|DEV1: Infrastructure]] — Implementation task file

See also: [[backend/module-catalog|Module Catalog]], [[modules/auth/overview|Auth]], [[modules/core-hr/overview|Core Hr]], [[modules/configuration/overview|Configuration]]
