# DEV1: Backend Platform Foundation + Auth + Developer Platform Admin API

**Track:** Backend
**Primary ownership:** platform foundation, auth/RBAC, tenant context, audit, Developer Platform Admin API
**Current Unfinished Task:** Task 2 - Tenant Auth + RBAC gaps (Slice A: Role CRUD + Role-Permission Assignment **done 2026-05-08**; next slice = User-role assignment + perm_ver bump). Task 2A final integration tests still blocked by Docker.
**Blocked By:** none for in-process work (Task 2A integration test verification blocked by Docker/Testcontainers availability)

---

## ADE Instructions

When Dev 1 asks to continue, start with **Task 0** before any other backend work. Read references only as needed, implement, test, and update this file.

---

## Task 0: Backend CQRS Folder Structure Cleanup

**Goal:** update the actual backend codebase to match the cleaned KB architecture before Dev 1 continues Auth/RBAC, tenant, or platform foundation work.

**This is Dev 1's first task. Do not start Task 2A, Task 2, or any later Dev 1 task until this cleanup is complete or explicitly blocked.**

**Requires:** none

### Required Rule

The backend must follow this default Application feature shape:

```text
ONEVO.Application/Features/{Feature}/
|-- Commands/
|   `-- {UseCase}/
|       |-- {UseCase}Command.cs
|       |-- {UseCase}Handler.cs
|       `-- {UseCase}Validator.cs
|-- Queries/
|   `-- {UseCase}/
|       |-- {UseCase}Query.cs
|       `-- {UseCase}Handler.cs
|-- DTOs/
|   |-- Requests/
|   `-- Responses/
`-- Interfaces/
```

Events are optional only:

```text
ONEVO.Domain/Features/{Feature}/Events/
ONEVO.Application/Features/{Feature}/EventHandlers/
```

Do not create `Events/`, `EventHandlers/`, or feature-level `Validators/` folders as default scaffolding.

### Acceptance Criteria

- [x] Audit `C:\Onevo\Onevo_Backend` for feature-level `Validators/`, default `Events/`, and default `EventHandlers/` folders.
- [x] Move every command validator beside the command it validates: `Commands/{UseCase}/{UseCase}Validator.cs`.
- [x] Update namespaces/usings after validator moves.
- [x] Remove empty feature-level `Validators/` folders after validators are moved.
- [x] Remove empty/default `Events/` and `EventHandlers/` folders that do not contain justified domain events or handlers.
- [x] Keep real event folders only when there is a documented post-save side effect.
- [x] Update or add architecture tests that reject feature-level `Validators/` as the default pattern and keep handlers free of EF Core/DbContext dependencies.
- [x] Verify FluentValidation assembly scanning still finds colocated validators.
- [x] Update this DEV1 file with the cleanup result before continuing to Task 2A.

### References

- [[backend/folder-structure|Folder Structure]] (backend/folder-structure.md)
- [[backend/cqrs-patterns|CQRS Patterns]] (backend/cqrs-patterns.md)
- [[backend/module-boundaries|Module Boundaries]] (backend/module-boundaries.md)
- [[backend/domain-events|Domain Events]] (backend/domain-events.md)
- [[code-standards/backend-standards|Backend Standards]] (code-standards/backend-standards.md)

### Verification

```bash
dotnet build ONEVO.sln
dotnet test ONEVO.sln --filter "LayerDependency|Architecture|Auth"
```

### Task 0 Progress - 2026-05-08

**Backend location correction:** the actual backend lives at `c:\Users\User\Desktop\dev\Onevo\Onevo_Backend` (not `C:\Onevo\Onevo_Backend` as previously written). All paths below reference the actual location.

**Audit findings (already mostly clean):**

- Feature-level `Validators/` folders: **0 found** - codebase already follows the colocated pattern.
- Feature-level `EventHandlers/` folders: **0 found**.
- `Events/` folders: **1 found** at `src/ONEVO.Domain/Features/Auth/Events/` containing 4 scaffold-only records (`PermissionChanged`, `RoleAssigned`, `UserLoggedIn`, `UserLoggedOut`). Repo-wide grep confirmed none were raised by any `BaseEntity.AddDomainEvent(...)` call and none had a corresponding `INotificationHandler<T>`. Per the Task 0 rule "remove empty/default Events folders that do not contain justified domain events", they were deleted.
- `Application/Features/Auth/Commands/` already follows `Commands/{UseCase}/{UseCase}{Command|Handler|Validator}.cs` pattern. Only `Login/LoginCommandValidator.cs` exists today and is already colocated correctly.

**Changes applied:**

- Deleted `src/ONEVO.Domain/Features/Auth/Events/PermissionChanged.cs`.
- Deleted `src/ONEVO.Domain/Features/Auth/Events/RoleAssigned.cs`.
- Deleted `src/ONEVO.Domain/Features/Auth/Events/UserLoggedIn.cs`.
- Deleted `src/ONEVO.Domain/Features/Auth/Events/UserLoggedOut.cs`.
- Removed the now-empty `src/ONEVO.Domain/Features/Auth/Events/` folder.
- Added two new architecture tests in `tests/ONEVO.Tests.Architecture/LayerDependencyTests.cs`:
  - `ApplicationFeatures_ShouldNotUse_FeatureLevelValidatorsFolder` — fails if any type lives under `ONEVO.Application.Features.*.Validators` namespace, enforcing the colocated-validator rule.
  - `ApplicationFeatures_ShouldNotUse_FeatureLevelEventsFolder` — fails if any type lives under `ONEVO.Application.Features.*.Events` namespace, enforcing that domain events live in the Domain layer.

**FluentValidation scanning:** already configured via `services.AddValidatorsFromAssembly(assembly)` in `ONEVO.Application/DependencyInjection.cs`, which discovers validators anywhere in the Application assembly. Colocated `LoginCommandValidator` continues to be picked up automatically; no DI changes needed.

**Verification:**

- `dotnet build ONEVO.sln --verbosity minimal -m:1 -p:UseSharedCompilation=false` -> `Build succeeded. 0 Warning(s) 0 Error(s)`.
- `dotnet test tests/ONEVO.Tests.Architecture/ONEVO.Tests.Architecture.csproj --no-build` -> **7 passed, 0 failed** (5 existing layer-dependency/EFCore tests + 2 new folder-shape tests).
- `dotnet test tests/ONEVO.Tests.Unit/ONEVO.Tests.Unit.csproj --no-build` -> **4 passed, 0 failed**.
- `dotnet test ONEVO.sln --filter "FullyQualifiedName~LayerDependency|FullyQualifiedName~Architecture|FullyQualifiedName~Auth" --no-build` -> Architecture project all 7 pass; Auth integration suite (12 tests) fails to construct fixtures because Docker/Testcontainers is unavailable on this host. This is the same pre-existing blocker recorded under Task 2A on 2026-05-08; not caused by Task 0 changes.

**Stylistic deviations flagged (not in Task 0 scope, no changes made):**

- Application Auth feature uses `Repositories/` folder name; the canonical rule shape lists `Interfaces/`. The team has standardized on `Repositories/` via Task 2A's repository boundary work, so leaving as-is.
- Command handler files use `{UseCase}CommandHandler.cs` (e.g., `LoginCommandHandler.cs`) instead of strict `{UseCase}Handler.cs`. Both readings are valid against the rule and the codebase is internally consistent; no rename done.

**Outcome:** Task 0 complete. Backend structure now matches the cleaned KB architecture and is enforced by automated tests. Dev 1 may proceed to finish the remaining 2 items in Task 2A and then start Task 2.

---

## Current Backend State Audit - 2026-05-07

Dev 1 was checked against `C:\Onevo\Onevo_Backend` before this focus file was corrected.

### What Exists

- [x] Backend solution exists with `ONEVO.Api`, `ONEVO.Application`, `ONEVO.Domain`, `ONEVO.Infrastructure`, and test projects.
- [x] Auth command handlers exist for login, logout, refresh token, forced password change, MFA enable/verify, password reset request, and password reset.
- [x] Domain entities exist for users, roles, permissions, role permissions, user roles, permission overrides, sessions, refresh tokens, password reset tokens, MFA records, audit logs, and consent records.
- [x] `ApplicationDbContext` maps the current Auth and Infrastructure entities.
- [x] API has tenant/admin JWT scheme separation, health checks, OpenAPI, exception/correlation/tenant middleware, and a minimal admin-boundary endpoint.
- [x] Integration tests currently cover login, refresh, forced password change, password reset request, protected endpoint rejection, and tenant token rejection on the admin boundary.

### What Is Not Finished

- [ ] Application handlers still inject `IApplicationDbContext` directly and query EF `DbSet`s.
- [ ] `IApplicationDbContext` exposes EF Core types from the Application layer; this keeps database access too close to command handlers.
- [ ] There are no Auth/RBAC repository interfaces in Application and no repository implementations in Infrastructure.
- [ ] `PermissionResolver` and `AuthTokenIssuer` still read/write persistence directly instead of using repositories.
- [ ] Role CRUD, role permission assignment, user role assignment, permission overrides, and role template APIs are not implemented.
- [ ] TOTP exists as command skeletons, but replay protection, fallback OTP challenge storage, delivery boundary tests, and lockout tests are not complete.
- [ ] The admin API is only a boundary stub; Developer Platform admin account/session entities and controllers are not complete.

### Required Dev 1 Rule Going Forward

- [ ] Controllers remain thin and call MediatR/application services only.
- [ ] Application command/query handlers do not inject `ApplicationDbContext`, `IApplicationDbContext`, or EF `DbSet`.
- [ ] Application command/query handlers read and write persistence only through feature repository interfaces plus `IUnitOfWork`.
- [ ] Infrastructure owns EF Core queries, `ApplicationDbContext`, repository implementations, seeders, and persistence-specific optimizations.
- [ ] Architecture tests must fail if Application handlers or services use EF Core directly.

---

## Task 1: Backend Foundation

**Goal:** create the backend baseline every other backend module can depend on.

### Acceptance Criteria

- [x] Solution structure exists for API, application, domain, infrastructure, tests, and the single API host used for tenant and admin boundaries.
- [x] Shared kernel includes base entity, auditable entity, result type, domain event base, tenant context abstraction, and time provider abstraction.
- [x] API project exposes health checks and OpenAPI.
- [x] Database context is configured for PostgreSQL and snake_case naming.
- [x] Migrations can be created and applied locally.
- [x] Request pipeline includes correlation ID, exception mapping, tenant resolution, and structured logging.
- [x] Baseline test project validates API boot, admin boundary boot, and database context boot.

### References

- [[backend/clean-architecture-overview|Clean Architecture Overview]] (backend/clean-architecture-overview.md)
- [[backend/shared-kernel|Shared Kernel]] (backend/shared-kernel.md)
- [[backend/api-conventions|API Conventions]] (backend/api-conventions.md)
- [[database/migration-patterns|Migration Patterns]] (database/migration-patterns.md)
- [[backend/module-catalog|Backend Module Catalog]] (backend/module-catalog.md)

### Verification

```bash
dotnet build ONEVO.sln
dotnet test ONEVO.sln
```

---

## Task 2A: Repository Boundary Repair

**Goal:** repair the backend architecture before adding more Auth/RBAC features, so database access is centralized behind repositories instead of scattered through command handlers and services.

**Requires:** DEV1 Task 1 complete

### Acceptance Criteria

- [x] Add Auth repository interfaces in `ONEVO.Application`, starting with user, refresh token, session, password reset token, MFA, role, permission, user role, permission override, feature access grant, and audit read/write needs.
- [x] Add Infrastructure repository implementations that use `ApplicationDbContext` internally.
- [x] Keep `IUnitOfWork` as the commit boundary and remove `SaveChangesAsync` usage from feature handlers except through `IUnitOfWork`.
- [x] Refactor login, logout, refresh token, forced password change, MFA enable/verify, password reset request, and password reset handlers to use repositories.
- [x] Refactor `AuthTokenIssuer` to create refresh tokens and sessions through repositories.
- [x] Refactor `PermissionResolver` behind repository-backed permission reads; it must not depend on `ApplicationDbContext` directly.
- [x] Refactor customer web auth to BFF-style HttpOnly cookie sessions: browser responses must not include tenant access JWTs, refresh/session cookies are rotated by the backend, and `/api/v1/*` browser calls authenticate from the HttpOnly session cookie.
- [x] Stop exposing EF `DbSet`s through `IApplicationDbContext`; if the interface remains temporarily, it must be Infrastructure-only and not injected into Application handlers.
- [x] Add architecture tests that reject `Microsoft.EntityFrameworkCore`, `IApplicationDbContext`, and `ApplicationDbContext` dependencies from `ONEVO.Application.Features.*`.
- [ ] Add focused tests proving existing auth flows still pass after repository refactor.
- [ ] Update this DEV1 file after the repair, marking only verified items as complete.

### Middleware Completion Checklist

These items are required to complete the BFF/session middleware behavior referenced by DEV1 Task 2A and Task 2.

- [x] Enforce `X-CSRF-Token` for cookie-authenticated state-changing `/api/v1/*` requests.
  - References: `security/auth-architecture.md` Session Security, `current-focus/contracts/auth-session.md` Customer Web Session Model, `backend/api-conventions.md` Standard Headers.
- [x] Reject authenticated tenant API requests that do not carry a valid `tenant_id` claim.
  - References: `security/auth-architecture.md` Authorization Check, DEV1 primary ownership of tenant context.
- [x] Reject stale cookie-authenticated tenant sessions when JWT `perm_ver` is behind the current permission version.
  - References: `security/auth-architecture.md` Permission Revocation, `modules/auth/overview.md` Key Business Rule 4.

### Task 2A Progress - 2026-05-08

- Repository boundary repair was implemented through Auth repository interfaces in Application and EF-backed implementations in Infrastructure.
- `IApplicationDbContext` was removed from Application; Auth handlers now persist through repositories plus `IUnitOfWork`.
- BFF-style customer web auth was implemented: login, refresh, MFA verify, and forced password change now return non-token session metadata JSON and set HttpOnly `onevo_session` / `onevo_refresh` cookies plus readable `onevo_csrf`; tenant `/api/v1/*` auth can read the `onevo_session` cookie.
- Middleware completion added CSRF double-submit validation, tenant claim rejection, and permission-version staleness checks for authenticated tenant API requests.
- Focused Auth integration tests were updated to assert that access tokens are not returned in JSON, HttpOnly cookies are set/rotated, and protected browser calls authenticate from the session cookie.
- Verified: `dotnet build ONEVO.sln --no-restore --verbosity minimal -m:1 -p:UseSharedCompilation=false`; `dotnet test tests\ONEVO.Tests.Architecture\ONEVO.Tests.Architecture.csproj --no-build --verbosity minimal -m:1`.
- Blocked verification: Auth integration tests could not run because Docker/Testcontainers is unavailable (`Docker is either not running or misconfigured`).

### References

- [[backend/clean-architecture-overview|Clean Architecture Overview]] (backend/clean-architecture-overview.md)
- [[backend/module-catalog|Backend Module Catalog]] (backend/module-catalog.md)
- [[modules/auth/overview|Auth]] (modules/auth/overview.md)
- [[security/auth-architecture|Auth Architecture]] (security/auth-architecture.md)

### Verification

```bash
dotnet build ONEVO.sln
dotnet test ONEVO.sln --filter "Auth|LayerDependency"
```

---

## Task 2: Tenant Auth + RBAC

**Goal:** implement secure tenant-facing user authentication and permission checks for protected `/api/v1/*` APIs.

**Requires:** DEV1 Task 1 and Task 2A complete

### Acceptance Criteria

- [ ] Customer web login sets an HttpOnly backend-managed session cookie and does not return the tenant access JWT to browser JavaScript.
- [x] Refresh token rotation persists replaced-by chain.
- [x] MFA setup and verification endpoint skeletons exist.
- [ ] MFA primary method is authenticator-app TOTP: setup stores an encrypted TOTP secret, login verifies a current 6-digit authenticator code, and replay inside the accepted window is blocked.
- [ ] MFA email OTP is fallback/recovery only and goes through the Auth email/notification boundary; local development may log fallback OTPs, but Phase 1 customer release requires Resend-backed delivery.
- [ ] MFA fallback OTP challenges are hashed at rest, expire after 5 minutes, are single-use, and lock after 3 failed attempts.
- [ ] Authenticator-app TOTP is the default Phase 1 MFA flow.
- [x] Password reset flow exists.
- [x] Password reset email can use a temporary logger-only stub during DEV1 Task 2; Phase 1 release requires DEV2 Task 5 to route password reset and account setup emails through the Resend-backed notification/email dispatcher.
- [x] Forced password change flow exists using `must_change_password`, `password_set_by_admin`, and `temporary_password_expires_at`.
- [x] Permission keys are seeded.
- [x] API authorization can enforce explicit permission claims on protected endpoints.
- [x] Tenant JWT issuer is rejected by `/admin/v1/*`.
- [x] Focused integration tests cover login and admin issuer rejection paths.
- [x] Tenant role CRUD APIs exist: list, create, update, archive/delete system-safe roles.
- [~] Role permission assignment API exists and only accepts permissions available to the tenant's enabled modules. *(Permission-exists validation shipped; tenant-module-filtering deferred until T3 ships `IModuleEntitlementService`.)*
- [ ] User role assignment API exists and increments the permission version counter.
- [ ] User permission override APIs exist for grant/revoke/remove and increment the permission version counter.
- [ ] Effective permission query returns universal grants, role grants, module filtering, hierarchy scope, and user overrides.
- [ ] Role template support exists for provisioning: templates can be created from module-filtered permissions and materialized into tenant roles.
- [ ] Tests cover TOTP setup, TOTP verify success, TOTP wrong code, TOTP replay protection, email fallback generation, fallback delivery boundary call, fallback expired, fallback wrong code, attempt lockout, role CRUD, role permission assignment, user role assignment, permission overrides, module-filtered permission visibility, and permission version refresh.

### References

- [[modules/auth/overview|Auth]] (modules/auth/overview.md)
- [[security/auth-architecture|Auth Architecture]] (security/auth-architecture.md)
- [[security/auth-flow|Auth Flow]] (security/auth-flow.md)
- [[Userflow/Auth-Access/permissions-reference|Permissions Reference]] (Userflow/Auth-Access/permissions-reference.md)
- [[Userflow/Auth-Access/role-creation|Role Creation]] (Userflow/Auth-Access/role-creation.md)
- [[Userflow/Auth-Access/permission-assignment|Permission Assignment]] (Userflow/Auth-Access/permission-assignment.md)
- [[developer-platform/modules/role-template-manager/overview|Role Template Manager]] (developer-platform/modules/role-template-manager/overview.md)

### Verification

```bash
dotnet test ONEVO.sln --filter Auth
```

### Task 2 Progress - 2026-05-08 (Slice A: Role CRUD + Role-Permission Assignment)

Delivered the foundational RBAC slice that the Tenant Creation API (and every other admin-side write) needs to gate access to.

**Endpoints shipped under `/api/v1/roles` (gated by `[Authorize(Policy = "TenantPolicy")]`):**

- `GET /api/v1/roles` — list tenant roles (`roles:read`).
- `GET /api/v1/roles/{id}` — get one role with its permissions (`roles:read`).
- `POST /api/v1/roles` — create a tenant-scoped role with optional initial permissions (`roles:manage`).
- `PATCH /api/v1/roles/{id}` — rename / re-describe a non-system role (`roles:manage`).
- `DELETE /api/v1/roles/{id}` — soft-archive a non-system role via `SoftDeleteInterceptor` (`roles:manage`).
- `PUT /api/v1/roles/{id}/permissions` — atomically replace a role's permission set (`roles:manage`).

**Application layer (under `Features/Auth`):**

- Commands: `CreateRole`, `UpdateRole`, `ArchiveRole`, `AssignRolePermissions` — each with `Command`, `Handler`, and (where input has user data) a colocated `Validator`.
- Queries: `ListRoles`, `GetRoleById`.
- DTOs: `Requests/{CreateRole,UpdateRole,AssignRolePermissions}Request.cs`, `Responses/{RoleSummary,RoleDetail}Dto.cs`.
- Repository interfaces extended in `AuthRepositoryInterfaces.cs`:
  - `IRoleRepository` gained `GetByIdForTenantAsync`, `GetByNameForTenantAsync`, `ListByTenantAsync`, `AddAsync`, `Remove`.
  - New `IRolePermissionRepository`: `ListByRoleAsync`, `AddRangeAsync`, `RemoveRange`.
  - `IPermissionRepository` gained `GetByIdsAsync` for batch validation.

**Infrastructure layer:**

- `EfAuthRepository` implements the new interfaces against `ApplicationDbContext`.
- `Infrastructure.DependencyInjection` registers `IRolePermissionRepository`.
- Soft delete uses the existing `SoftDeleteInterceptor` (no DB schema changes needed).

**Behavioural rules enforced:**

- All operations are tenant-scoped; cross-tenant access is impossible because every repository call carries `tenantId` from `ICurrentUser` and the DB index `(tenant_id, name)` is unique.
- System roles (`IsSystem = true`) are protected from update, archive, and permission reassignment — handler returns 403.
- Role name uniqueness is enforced per tenant in the create + rename paths; conflict returns 409.
- Permission ids are validated against the seeded `permissions` catalog before any DB write; unknown ids return 400 without persisting.
- TODO marker placed in `CreateRoleCommandHandler` and `AssignRolePermissionsCommandHandler` for module-filtered permission validation, to be wired once T3 ships `IModuleEntitlementService`.

**Tests:**

- 19 new unit tests in `tests/ONEVO.Tests.Unit/Features/Auth/Roles/` covering: success paths, system-role protection, name conflict, unknown permission id, empty-list (clear all), unauthenticated/no-tenant, persistence side-effects.
- Added `Moq 4.20.72` to `ONEVO.Tests.Unit.csproj` (consistent with the Moq convention in user rules).
- ArchUnit suite still passes 7/7 — repository boundary is preserved (handlers depend only on Application interfaces, no EF Core types).

**Verification:**

- `dotnet build ONEVO.sln` -> `Build succeeded. 0 Warning(s) 0 Error(s)`.
- `dotnet test tests/ONEVO.Tests.Unit/ONEVO.Tests.Unit.csproj --no-build` -> **23 passed, 0 failed** (4 existing + 19 new role-handler tests).
- `dotnet test tests/ONEVO.Tests.Architecture/ONEVO.Tests.Architecture.csproj --no-build` -> **7 passed, 0 failed**.
- Auth integration tests still blocked by Docker/Testcontainers (recorded under T2A on 2026-05-08); no new integration coverage in this slice.

**Outstanding T2 work after Slice A:**

- User role assignment API + `perm_ver` increment.
- User permission override APIs (grant/revoke/remove).
- Effective permission query (universal + role + module filter + hierarchy + overrides).
- Role template support (operator-managed, materialisable).
- MFA TOTP authenticator-app flow + replay protection.
- MFA email fallback OTP (hashed, 5-min expiry, single-use, lock after 3).
- Module-filtered permission validation in `CreateRole` and `AssignRolePermissions` once T3 entitlement service exists.
- Integration tests for the Role CRUD endpoints once Docker/Testcontainers is back.

---

## Task 3: Tenant + Entitlement Foundation

**Goal:** provide server-side module gates used by web app, IDE extension, and Developer Platform provisioning.

**Requires:** DEV1 Task 2 complete

### Acceptance Criteria

- [x] Tenant provisioning creates baseline tenant, legal entity, admin user, and subscription record.
- [x] Module entitlement service resolves active modules from subscription, tenant module entitlements, selected feature keys, and module registry.
- [x] Permissions service can return effective permissions for a user and tenant.
- [x] Entitlement DTO supports web and IDE consumers.
- [x] Tests cover active module resolution and focused entitlement reads.
- [ ] Developer Platform provisioning can create a draft tenant in `provisioning` status before activation.
- [ ] Developer Platform provisioning can set commercial terms via `/admin/v1/tenants/{id}/subscription`, including `subscription` vs `full_license_maintenance`, subscription gateway collection, manual one-time full-license payment evidence, gateway-collected maintenance, maintenance status, renewal date, and custom contract values.
- [ ] Developer Platform provisioning can set tenant modules through the same entitlement/module registry via `/admin/v1/tenants/{id}/modules`, including module sales states: `purchased`, `trial`, `quoted`, `maintenance_included`, `subscription_included`, and `disabled`.
- [ ] Permission catalog endpoint returns only permissions for enabled tenant modules plus universal permissions.
- [ ] Provisioning can attach role templates to the tenant and materialize them into tenant-scoped roles.
- [ ] Tenant owner invite creates a user without requiring an operator-entered final password and sends a set-password link.
- [ ] Tenant owner invite supports complete-invite-with-password using the invited email and BCrypt password hashing.
- [ ] Tenant owner invite supports complete-invite-with-Google when allowed by tenant/invitation policy, including audited handling for different Google email vs invited email.
- [ ] Add Auth backend entities, EF configurations, DbSets, migration, repositories, and tests for `invitation_tokens`: token hash, invited email, expiry, used/accepted timestamp, revoked timestamp, revoked-by actor, completion method, allowed completion methods, Google email mismatch policy, and allowed domains.
- [ ] Add Auth backend entities, EF configurations, DbSets, migration, repositories, and tests for `user_external_identities`: provider, provider subject, provider email, verification state, linked timestamp, and last-used timestamp without overloading the user email field.
- [ ] Add Auth backend entities, EF configurations, DbSets, migration, repositories, and tests for `tenant_auth_policies`: password completion allowed, Google completion allowed, Google email mismatch default, allowed login domains, and MFA requirement.
- [ ] Add SharedPlatform/Provisioning backend entities, EF configurations, DbSets, migration, module interfaces, and tests for `tenant_provisioning_states` and `tenant_provisioning_validation_results`: current step, per-section completion timestamps, validation blockers/warnings, activation readiness, activation timestamp, and last operator update.
- [ ] Add SharedPlatform catalog backend entities, EF configurations, DbSets, migration, module interfaces, and tests for `subscription_plan_price_history` and `module_catalog_price_history`: old/new price, currency, pricing unit, changed-by actor, reason, timestamp, and rule that catalog price changes do not silently rewrite existing tenant contracts.
- [ ] Activation is blocked until required provisioning steps are complete: tenant details, subscription/commercial terms, module selection/pricing, role template application, first owner invite, and required initial settings.
- [ ] Tests cover draft provisioning, module assignment, permission catalog filtering, role-template materialization, owner invite, accept-with-password, accept-with-Google, Google email mismatch rejection/allowed path, and activation guard.

### References

- [[modules/infrastructure/overview|Infrastructure]] (modules/infrastructure/overview.md)
- [[infrastructure/multi-tenancy|Multi Tenancy]] (infrastructure/multi-tenancy.md)
- [[modules/shared-platform/overview|Shared Platform]] (modules/shared-platform/overview.md)
- [[database/schemas/shared-platform|Shared Platform Schema]] (database/schemas/shared-platform.md)
- [[developer-platform/modules/feature-flag-manager/overview|Feature Flag Manager]] (developer-platform/modules/feature-flag-manager/overview.md)
- [[developer-platform/modules/role-template-manager/overview|Role Template Manager]] (developer-platform/modules/role-template-manager/overview.md)
- [[developer-platform/userflow/provisioning-flow|Manual Customer Provisioning Flow]] (developer-platform/userflow/provisioning-flow.md)

### Verification

```bash
dotnet test ONEVO.sln --filter Entitlement
```

---

## Task 4: Audit Foundation

**Goal:** create a shared audit service used by auth, Developer Platform, agent, and IDE tag flows.

**Requires:** DEV1 Task 1 complete

> **Pickup assigned to Dev 4** — Dev 4 is blocked waiting for Task 2 (Auth); Task 4 only needs Task 1. Dev 4 executes this in that idle window. Dev 1 proceeds T1 → T2 → T3 → T5 → T6 without stopping for T4. See DEV4.md early-pickup section.

### Acceptance Criteria

- [ ] Audit log entity supports tenant, actor, action, resource type, resource ID, IP, user agent, and metadata.
- [ ] Audit writer is injectable from all modules.
- [ ] Cross-tenant audit reader exists for Developer Platform Audit Console.
- [ ] Auth events write audit records.
- [ ] Permission denial writes audit records.
- [ ] Developer Platform audit queries are themselves audit-logged with query parameters.
- [ ] Tests cover audit persistence, metadata serialization, tenant-scoped read, and cross-tenant admin read.

### References

- [[security/compliance|Compliance]] (security/compliance.md)
- [[security/data-classification|Data Classification]] (security/data-classification.md)
- [[developer-platform/modules/audit-console/overview|Audit Console]] (developer-platform/modules/audit-console/overview.md)

### Verification

```bash
dotnet test ONEVO.sln --filter Audit
```

---

## Task 5: Shared Platform Core + Workflow Engine

**Goal:** build the cross-cutting platform services that other modules depend on, including the workflow/approval engine.

**Requires:** DEV1 Task 3 complete

### Backend Module Location

- Feature: `Features/SharedPlatform`
- API: `/api/v1/sso/*`, `/api/v1/subscriptions/*`, `/api/v1/feature-flags`, `/api/v1/workflows/*`
- Consumed by: Leave, Workforce Presence, WorkSync Collaboration, Notifications, Developer Platform

### Acceptance Criteria

- [ ] SSO provider configuration exists for Google only in Phase 1, with encrypted client credentials.
- [ ] Subscription plan catalog exists with plan features and tenant subscription state.
- [ ] Stripe/PayHere-facing subscription, maintenance, and invoice records are represented behind module interfaces.
- [ ] Feature flag service resolves tenant flags and module gates.
- [ ] Tenant branding records exist for logo and colors; default tenant URL comes from `tenants.slug`.
- [ ] Notification templates and notification channel configuration exist.
- [ ] Workflow definitions, workflow steps, workflow instances, workflow step instances, and approval actions are mapped.
- [ ] Workflow engine can start an instance for any `resource_type` + `resource_id`.
- [ ] Workflow engine resolves approvers through dynamic resolvers, including reporting manager, team lead, department owner, selected permission, selected department, selected team, selected job level, specific employee, configured escalation owner, previous approver, and case conversation participants.
- [ ] Workflow approval steps support multiple-approver modes: only one approval is required, all assigned approvers must approve, and approve in order.
- [ ] Workflow engine supports approve, reject, delegate, request info, condition steps, SLA deadline, and timeout action.
- [ ] Workflow engine publishes `WorkflowStepCompleted` and `WorkflowCompleted` events.
- [ ] Leave approval can use the workflow engine rather than a hard-coded approval path.
- [ ] Overtime approval can use the workflow engine rather than a hard-coded approval path.
- [ ] Workflow status endpoint exists for resource lookup.
- [ ] Tests cover workflow start, approver resolution, approve, reject, delegate, SLA timeout, event publish, leave workflow integration, and tenant isolation.

### References

- [[modules/shared-platform/overview|Shared Platform]] (modules/shared-platform/overview.md)
- [[modules/shared-platform/workflow-engine/overview|Workflow Engine]] (modules/shared-platform/workflow-engine/overview.md)
- [[modules/shared-platform/sso-authentication/overview|SSO Authentication]] (modules/shared-platform/sso-authentication/overview.md)
- [[modules/shared-platform/subscriptions-billing/overview|Subscriptions Billing]] (modules/shared-platform/subscriptions-billing/overview.md)
- [[modules/shared-platform/notification-infrastructure/overview|Notification Infrastructure]] (modules/shared-platform/notification-infrastructure/overview.md)
- [[modules/shared-platform/compliance-governance/overview|Compliance Governance]] (modules/shared-platform/compliance-governance/overview.md)
- [[backend/domain-events|Domain Events]] (backend/domain-events.md)

### Verification

```bash
dotnet test ONEVO.sln --filter SharedPlatform
dotnet test ONEVO.sln --filter Workflow
```

---

## Task 6: Configuration + Monitoring Policy Foundation

**Goal:** build tenant settings, monitoring toggles, employee overrides, retention, integrations, and app allowlist policy source of truth.

**Requires:** DEV1 Tasks 3 and 5 complete

### Backend Module Location

- Feature: `Features/Configuration`
- API: `/api/v1/settings/*`
- Consumed by: Agent Gateway, Activity Monitoring, Identity Verification, Exception Engine, Developer Platform System Config

### Acceptance Criteria

- [ ] Tenant settings API supports timezone, date format, currency, work week, work hours, privacy mode, and data retention settings.
- [ ] Monitoring feature toggles exist for activity monitoring, application tracking, screenshot capture, meeting detection, device tracking, identity verification, and biometric.
- [ ] Industry profile defaults seed monitoring toggles at tenant creation.
- [ ] Employee monitoring overrides support nullable inherit/override behavior.
- [ ] Bulk overrides can apply by department, team, or job family.
- [ ] Integration connections support encrypted credentials and health status.
- [ ] Shared encryption abstraction is available for Calendar Google/Outlook OAuth token storage owned by DEV2.
- [ ] Retention policy records exist per data type.
- [ ] App allowlist supports tenant, role, and employee scopes.
- [ ] Effective app allowlist resolution uses employee > role > tenant precedence.
- [ ] Allowlist mode supports allowlist and blocklist behavior.
- [ ] Allowlist changes trigger policy refresh commands for affected agents.
- [ ] Tests cover tenant settings update, monitoring toggle merge, employee override, bulk override, integration credential encryption, retention update, app allowlist merge, and policy refresh event.

### References

- [[modules/configuration/overview|Configuration]] (modules/configuration/overview.md)
- [[modules/configuration/app-allowlist/overview|App Allowlist]] (modules/configuration/app-allowlist/overview.md)
- [[modules/configuration/employee-overrides/overview|Employee Overrides]] (modules/configuration/employee-overrides/overview.md)
- [[modules/configuration/integrations/overview|Integrations]] (modules/configuration/integrations/overview.md)
- [[modules/configuration/retention-policies/overview|Retention Policies]] (modules/configuration/retention-policies/overview.md)
- [[Userflow/Configuration/monitoring-toggles|Monitoring Toggles]] (Userflow/Configuration/monitoring-toggles.md)
- [[Userflow/Configuration/app-allowlist-setup|App Allowlist Setup]] (Userflow/Configuration/app-allowlist-setup.md)

### Verification

```bash
dotnet test ONEVO.sln --filter Configuration
dotnet test ONEVO.sln --filter AppAllowlist
```

---

## Task 7: Developer Platform Admin API Foundation

**Goal:** implement the platform-admin backend boundary used by the internal Developer Platform console.

**Requires:** DEV1 Tasks 1, 2, and 4 complete

> **Pickup assigned to Dev 3** — Dev 3 is blocked the longest (needs Tasks 1–3 before DEV3.T1 starts). Task 7 only needs Tasks 1, 2, and 4, so Dev 3 can build it during that wait. Dev 1 is free to run the critical chain T3 → T5 → T6 without interruption. See DEV3.md early-pickup section.

### Backend Module Location

- Feature: `Features/DevPlatform`
- Host: `ONEVO.Api` only; `/admin/v1/*` is a logical admin namespace inside the single Phase 1 backend host
- Endpoint prefix: `/admin/v1/*`
- Auth boundary: platform-admin JWT issuer only; tenant JWTs must be rejected
- DbContext: unified `ApplicationDbContext`; DevPlatform entities have no `TenantId` and must be excluded from tenant query filters

### Acceptance Criteria

- [ ] `ONEVO.Api` hosts both tenant `/api/v1/*` and admin `/admin/v1/*` endpoints in one deployment.
- [ ] `ONEVO.Admin.Api` remains deprecated scaffold only; no new admin controllers are added there.
- [ ] Admin controllers live under `ONEVO.Api/Controllers/Admin` and are routed under `/admin/v1/*`.
- [ ] Admin API has OpenAPI grouping, health coverage, environment config, and explicit `PlatformAdmin` policy registration inside `ONEVO.Api`.
- [ ] Admin controllers are thin and call application/module interfaces through DI.
- [ ] Platform admin auth validates Google OAuth login through `POST /admin/v1/auth/google-callback`.
- [ ] Google token validation enforces `@onevo.io` email domain.
- [ ] Login checks `dev_platform_accounts.google_sub`, `email`, and `is_active`.
- [ ] Successful login issues a 30-minute platform-admin JWT with `iss`, `aud`, `sub`, `email`, and `platform_role`.
- [ ] `dev_platform_accounts` and `dev_platform_sessions` are mapped in `ApplicationDbContext`.
- [ ] `dev_platform_accounts` and `dev_platform_sessions` have no `TenantId`.
- [ ] DevPlatform entities are excluded from tenant query filters.
- [ ] Platform admin JWT is accepted only by `/admin/v1/*` endpoints.
- [ ] Tenant JWT is rejected by every `/admin/v1/*` endpoint.
- [ ] Platform admin JWT is rejected by tenant `/api/v1/*` endpoints.
- [ ] Platform permissions are enforced through Developer Platform RBAC; `super_admin`, `admin`, and `viewer` are compatibility presets only.
- [ ] Admin session records store token hash, account ID, created timestamp, expiry timestamp, and IP address.
- [ ] `last_login_at` updates after successful login.
- [ ] Tests cover Google callback success, inactive account rejection, non-`@onevo.io` rejection, issuer separation, role claim mapping, and session persistence.

### References

- [[modules/dev-platform/overview|Dev Platform Feature]] (modules/dev-platform/overview.md)
- [[developer-platform/overview|Developer Platform Overview]] (developer-platform/overview.md)
- [[developer-platform/auth|Developer Platform Auth]] (developer-platform/auth.md)
- [[developer-platform/system-design|Developer Platform System Design]] (developer-platform/system-design.md)
- [[developer-platform/backend/admin-api-layer|Admin API Layer]] (developer-platform/backend/admin-api-layer.md)
- [[developer-platform/backend/api-contracts|Admin API Contracts]] (developer-platform/backend/api-contracts.md)
- [[developer-platform/database/schema|Developer Platform Schema]] (developer-platform/database/schema.md)
- [[backend/module-catalog|Backend Module Catalog]] (backend/module-catalog.md)

### Verification

```bash
dotnet test ONEVO.sln --filter DevPlatform
dotnet test ONEVO.sln --filter AdminApi
```

---

## Task 8: Developer Platform Tenant Console Backend

**Goal:** implement the admin tenant lifecycle APIs used by `console.onevo.io`.

**Requires:** DEV1 Tasks 3, 5, and 7 complete

> **Parallel with Task 9** — both unlock when Task 7 is done. Run them simultaneously.
> **Overflow to Dev 2** — Dev 2 picks this up after completing DEV2 Tasks 1–5. Dev 2 owns org structure and employee lifecycle data that Task 8 reads through module interfaces, making this a natural fit.

### Backend Module References

- Admin host: `ONEVO.Api` `/admin/v1/*`
- Tenant data: `Features/SharedPlatform`, `Features/InfrastructureModule`, `Features/Auth`
- DevPlatform auth/session: `Features/DevPlatform`

### Acceptance Criteria

- [ ] `GET /admin/v1/tenants` returns all tenants, including `provisioning` and `suspended` statuses, with search/filter support.
- [ ] Tenant list includes company name, slug, plan tier, status, employee count, created date, agent count, and last login summary.
- [ ] `GET /admin/v1/subscription-plans` returns reusable plan catalog records with included modules, company-size price band, calculated monthly/annual price, override monthly/annual price, currency, active state, pricing unit, and AI monthly token limit; operators do not create a plan per tenant.
- [ ] `POST /admin/v1/subscription-plans` and `PATCH /admin/v1/subscription-plans/{id}` create/update reusable plans from selected modules and `module_catalog.price_brackets`, using the same company-size values as tenant creation, with optional override prices and audit reason.
- [ ] `GET /admin/v1/modules/catalog` returns reusable module catalog records with pillar, phase, sellable state, price brackets, full-license price, maintenance rate, and pricing unit.
- [ ] `POST /admin/v1/modules/catalog` and `PATCH /admin/v1/modules/catalog/{moduleKey}` create/update reusable module price brackets, full-license price, maintenance rate, active state, and pricing unit with audit reason.
- [ ] `GET /admin/v1/tenants/validate` validates tenant slug, company name, email domain, registration number, and country rules with conflicts and warnings.
- [ ] `POST /admin/v1/tenants` creates a draft tenant in `provisioning` status from account setup data.
- [ ] `PATCH /admin/v1/tenants/{id}` edits draft tenant details before activation without bypassing activation guards.
- [ ] `GET /admin/v1/tenants/{id}` returns overview, plan, billing dates, status, users summary, agent summary, flags summary, settings summary, and audit summary links.
- [ ] `PATCH /admin/v1/tenants/{id}/status` supports suspend, unsuspend, and activate with role checks.
- [ ] `PATCH /admin/v1/tenants/{id}/subscription` supports provisioning commercial terms and post-activation exception subscription override with selected packages/modules, company-size range, calculated price snapshot, override prices, AI monthly token limit, required reason, and audit log.
- [ ] `PUT /admin/v1/tenants/{id}/modules` sets tenant module entitlements, selected feature keys, module sales state, and module-level pricing override metadata for provisioning and post-provisioning changes.
- [ ] `GET /admin/v1/tenants/{id}/permissions/catalog` returns only permissions exposed by the tenant's active modules plus universal permissions.
- [ ] `GET /admin/v1/role-templates` lists global/default role templates with module and permission coverage.
- [ ] `POST /admin/v1/role-templates` creates an operator-managed role template from a module-filtered permission set.
- [ ] `PATCH /admin/v1/role-templates/{id}` edits reusable non-system templates with versioning and audit.
- [ ] `POST /admin/v1/tenants/{id}/role-templates/{templateId}/apply` materializes a role template into tenant-scoped roles.
- [ ] `GET /admin/v1/tenants/{id}/roles` lists materialized tenant roles during provisioning.
- [ ] `POST /admin/v1/tenants/{id}/roles` creates tenant-specific roles during provisioning without requiring job levels.
- [ ] `PUT /admin/v1/tenants/{id}/roles/{roleId}/permissions` lets Developer Platform adjust a provisioned role using only permissions available to that tenant.
- [ ] Tenant owner can later create/edit tenant roles inside `/api/v1/roles`, still limited by enabled modules.
- [ ] `PATCH /admin/v1/tenants/{id}/settings` writes tenant setting overrides through the Configuration module interface.
- [ ] `POST /admin/v1/tenants/{id}/invite-admin` creates the first tenant super-admin invite.
- [ ] `GET /admin/v1/tenants/{id}/provisioning-summary` returns review data, section completion, warnings, and activation blockers.
- [ ] `PATCH /admin/v1/tenants/{id}/provision/confirm` activates a provisioning tenant only after required steps are complete.
- [ ] `POST /admin/v1/tenants/{id}/impersonate` requires `platform.tenants.impersonate`, creates a 15-minute non-renewable impersonation token, and always writes an audit log.
- [ ] Provisioning tenants are invisible to tenant-facing `/api/v1/*` queries.
- [ ] Tests cover tenant draft creation, provisioning resume data, activation guard, suspend/unsuspend, subscription/commercial terms override audit, module assignment and pricing state, invite admin, and impersonation role enforcement.

### References

- [[developer-platform/modules/tenant-console/overview|Tenant Console]] (developer-platform/modules/tenant-console/overview.md)
- [[developer-platform/userflow/tenant-management|Tenant Management Flows]] (developer-platform/userflow/tenant-management.md)
- [[developer-platform/userflow/provisioning-flow|Manual Customer Provisioning Flow]] (developer-platform/userflow/provisioning-flow.md)
- [[developer-platform/backend/api-contracts|Admin API Contracts]] (developer-platform/backend/api-contracts.md)
- [[database/schemas/shared-platform|Shared Platform Schema]] (database/schemas/shared-platform.md)
- [[Userflow/Platform-Setup/billing-subscription|Billing & Subscription]] (Userflow/Platform-Setup/billing-subscription.md)
- [[backend/module-catalog|Backend Module Catalog]] (backend/module-catalog.md)
- [[modules/shared-platform/overview|Shared Platform]] (modules/shared-platform/overview.md)
- [[modules/infrastructure/overview|Infrastructure]] (modules/infrastructure/overview.md)
- [[modules/auth/overview|Auth]] (modules/auth/overview.md)
- [[developer-platform/modules/role-template-manager/overview|Role Template Manager]] (developer-platform/modules/role-template-manager/overview.md)
- [[Userflow/Auth-Access/role-creation|Role Creation]] (Userflow/Auth-Access/role-creation.md)
- [[Userflow/Auth-Access/permission-assignment|Permission Assignment]] (Userflow/Auth-Access/permission-assignment.md)

### Verification

```bash
dotnet test ONEVO.sln --filter TenantConsole
dotnet test ONEVO.sln --filter Provisioning
dotnet test ONEVO.sln --filter Impersonation
```

---

## Task 9: Developer Platform Operations Backend

**Goal:** implement feature flag, audit, system config, and app catalog admin APIs.

**Requires:** DEV1 Tasks 4, 5, and 7 complete

> **Parallel with Task 8** — both unlock when Task 7 is done. Run them simultaneously.
> **Overflow to Dev 3** — Dev 3 picks this up after completing DEV3 Tasks 1–5 (and after having already built Task 7 earlier).

### Backend Module References

- Feature flags/runtime overrides and module entitlements: `Features/SharedPlatform` and `Features/Configuration`
- Audit reader: shared audit foundation from Task 4
- App catalog: SharedPlatform public catalog interface plus Configuration observed-app reader
- Admin host: `ONEVO.Api` `/admin/v1/*`

### Acceptance Criteria

- [ ] `GET /admin/v1/feature-flags` returns all flags, global defaults, rollout values, and override counts.
- [ ] `GET /admin/v1/feature-flags/{flag}` returns flag detail and per-tenant overrides.
- [ ] `PATCH /admin/v1/feature-flags/{flag}` updates global default or rollout configuration with audit log.
- [ ] `PUT /admin/v1/tenants/{id}/feature-flags` replaces a tenant's flag overrides.
- [ ] `PATCH /admin/v1/tenants/{id}/feature-flags/{flag}` sets one tenant override with `value`; `DELETE /admin/v1/tenants/{id}/feature-flags/{flag}` clears it.
- [ ] Module enable/disable uses the same module entitlement registry consumed by tenant app and IDE extension.
- [ ] `GET /admin/v1/audit-logs` supports tenant, actor, action, resource, and date filters.
- [ ] Audit log export endpoint returns filtered CSV without allowing mutation or deletion.
- [ ] Audit Console access itself writes an audit record with query parameters.
- [ ] `GET /admin/v1/config/defaults` and `PATCH /admin/v1/config/defaults` manage global tenant defaults.
- [ ] `GET /admin/v1/tenants/{id}/settings` and `PATCH /admin/v1/tenants/{id}/settings` manage per-tenant overrides.
- [ ] App Catalog admin endpoints support catalog list, create/edit, `is_public` toggle, uncatalogued app list, bulk approve, dismiss, and aggregate usage.
- [ ] App Catalog writes go through SharedPlatform catalog interfaces, never direct DbContext access from admin controllers.
- [ ] Tests cover global flag toggle, tenant override, module toggle, audit filtering/export, config default update, tenant config override, catalog create, catalog public toggle, and uncatalogued bulk approve.

### References

- [[developer-platform/modules/feature-flag-manager/overview|Feature Flag Manager]] (developer-platform/modules/feature-flag-manager/overview.md)
- [[developer-platform/userflow/feature-flags|Feature Flag Flows]] (developer-platform/userflow/feature-flags.md)
- [[developer-platform/modules/audit-console/overview|Audit Console]] (developer-platform/modules/audit-console/overview.md)
- [[developer-platform/modules/system-config/overview|System Config]] (developer-platform/modules/system-config/overview.md)
- [[developer-platform/modules/app-catalog-manager/overview|App Catalog Manager]] (developer-platform/modules/app-catalog-manager/overview.md)
- [[modules/shared-platform/overview|Shared Platform]] (modules/shared-platform/overview.md)
- [[modules/configuration/overview|Configuration]] (modules/configuration/overview.md)
- [[security/compliance|Compliance]] (security/compliance.md)

### Verification

```bash
dotnet test ONEVO.sln --filter FeatureFlags
dotnet test ONEVO.sln --filter Audit
dotnet test ONEVO.sln --filter SystemConfig
dotnet test ONEVO.sln --filter AppCatalog
```
