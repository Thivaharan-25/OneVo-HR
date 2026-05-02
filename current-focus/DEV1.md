# DEV1: Backend Platform Foundation + Auth + Developer Platform Admin API

**Track:** Backend
**Primary ownership:** platform foundation, auth/RBAC, tenant context, audit, Developer Platform Admin API
**Current Unfinished Task:** Task 1 - Backend foundation
**Blocked By:** none

---

## ADE Instructions

When Dev 1 asks to continue, start with the first unchecked item in **Current Unfinished Task**. Read references only as needed, implement, test, and update this file.

---

## Task 1: Backend Foundation

**Goal:** create the backend baseline every other backend module can depend on.

### Acceptance Criteria

- [ ] Solution structure exists for API, application, domain, infrastructure, tests, and admin API host.
- [ ] Shared kernel includes base entity, auditable entity, result type, domain event base, tenant context abstraction, and time provider abstraction.
- [ ] API project exposes health checks and OpenAPI.
- [ ] Database context is configured for PostgreSQL and snake_case naming.
- [ ] Migrations can be created and applied locally.
- [ ] Request pipeline includes correlation ID, exception mapping, tenant resolution, and structured logging.
- [ ] Baseline test project validates API boot, admin API boot, and database context boot.

### References

- [[backend/clean-architecture-overview|Clean Architecture Overview]]
- [[backend/shared-kernel|Shared Kernel]]
- [[backend/api-conventions|API Conventions]]
- [[database/migration-patterns|Migration Patterns]]
- [[backend/module-catalog|Backend Module Catalog]]

### Verification

```bash
dotnet build ONEVO.sln
dotnet test ONEVO.sln
```

---

## Task 2: Tenant Auth + RBAC

**Goal:** implement secure tenant-facing user authentication and permission checks for protected `/api/v1/*` APIs.

### Acceptance Criteria

- [ ] User login issues short-lived tenant access token and backend-managed refresh token.
- [ ] Refresh token rotation persists replaced-by chain.
- [ ] MFA setup and verification endpoints exist.
- [ ] Password reset flow exists.
- [ ] Forced password change flow exists using `must_change_password`, `password_set_by_admin`, and `temporary_password_expires_at`.
- [ ] Permission keys are seeded.
- [ ] API authorization supports tenant-level roles and explicit permissions.
- [ ] Tenant JWT issuer is rejected by `/admin/v1/*`.
- [ ] Integration tests cover login, refresh, forced password change, forbidden access, and admin issuer rejection.

### References

- [[modules/auth/overview|Auth]]
- [[security/auth-architecture|Auth Architecture]]
- [[security/auth-flow|Auth Flow]]
- [[Userflow/Auth-Access/permissions-reference|Permissions Reference]]

### Verification

```bash
dotnet test ONEVO.sln --filter Auth
```

---

## Task 3: Tenant + Entitlement Foundation

**Goal:** provide server-side module gates used by web app, IDE extension, and Developer Platform provisioning.

### Acceptance Criteria

- [ ] Tenant provisioning creates baseline tenant, legal entity, admin user, and subscription record.
- [ ] Module entitlement service resolves active modules from subscription, feature grants, and module registry.
- [ ] Permissions service can return effective permissions for a user and tenant.
- [ ] Entitlement DTO supports web and IDE consumers.
- [ ] Developer Platform provisioning can set tenant modules through the same entitlement/module registry.
- [ ] Tests cover active module resolution, permission inheritance, and module assignment.

### References

- [[modules/infrastructure/overview|Infrastructure]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[modules/shared-platform/overview|Shared Platform]]
- [[database/schemas/shared-platform|Shared Platform Schema]]
- [[developer-platform/modules/feature-flag-manager/overview|Feature Flag Manager]]

### Verification

```bash
dotnet test ONEVO.sln --filter Entitlement
```

---

## Task 4: Audit Foundation

**Goal:** create a shared audit service used by auth, Developer Platform, agent, and IDE tag flows.

### Acceptance Criteria

- [ ] Audit log entity supports tenant, actor, action, resource type, resource ID, IP, user agent, and metadata.
- [ ] Audit writer is injectable from all modules.
- [ ] Cross-tenant audit reader exists for Developer Platform Audit Console.
- [ ] Auth events write audit records.
- [ ] Permission denial writes audit records.
- [ ] Developer Platform audit queries are themselves audit-logged with query parameters.
- [ ] Tests cover audit persistence, metadata serialization, tenant-scoped read, and cross-tenant admin read.

### References

- [[security/compliance|Compliance]]
- [[security/data-classification|Data Classification]]
- [[developer-platform/modules/audit-console/overview|Audit Console]]

### Verification

```bash
dotnet test ONEVO.sln --filter Audit
```

---

## Task 5: Shared Platform Core + Workflow Engine

**Goal:** build the cross-cutting platform services that other modules depend on, including the workflow/approval engine.

### Backend Module Location

- Feature: `Features/SharedPlatform`
- API: `/api/v1/sso/*`, `/api/v1/subscriptions/*`, `/api/v1/feature-flags`, `/api/v1/workflows/*`
- Consumed by: Leave, Workforce Presence, WorkSync Collaboration, Notifications, Developer Platform

### Acceptance Criteria

- [ ] SSO provider configuration exists for Google only in Phase 1, with encrypted client credentials.
- [ ] Subscription plan catalog exists with plan features and tenant subscription state.
- [ ] Stripe-facing subscription and invoice records are represented behind module interfaces.
- [ ] Feature flag service resolves tenant flags and module gates.
- [ ] Tenant branding records exist for custom domain, logo, and colors.
- [ ] Notification templates and notification channel configuration exist.
- [ ] Workflow definitions, workflow steps, workflow instances, workflow step instances, and approval actions are mapped.
- [ ] Workflow engine can start an instance for any `resource_type` + `resource_id`.
- [ ] Workflow engine resolves approvers by reporting manager, department head, role, or specific user.
- [ ] Workflow engine supports approve, reject, delegate, request info, condition steps, SLA deadline, and timeout action.
- [ ] Workflow engine publishes `WorkflowStepCompleted` and `WorkflowCompleted` events.
- [ ] Leave approval can use the workflow engine rather than a hard-coded approval path.
- [ ] Overtime approval can use the workflow engine rather than a hard-coded approval path.
- [ ] Workflow status endpoint exists for resource lookup.
- [ ] Tests cover workflow start, approver resolution, approve, reject, delegate, SLA timeout, event publish, leave workflow integration, and tenant isolation.

### References

- [[modules/shared-platform/overview|Shared Platform]]
- [[modules/shared-platform/workflow-engine/overview|Workflow Engine]]
- [[modules/shared-platform/sso-authentication/overview|SSO Authentication]]
- [[modules/shared-platform/subscriptions-billing/overview|Subscriptions Billing]]
- [[modules/shared-platform/notification-infrastructure/overview|Notification Infrastructure]]
- [[modules/shared-platform/compliance-governance/overview|Compliance Governance]]
- [[backend/domain-events|Domain Events]]

### Verification

```bash
dotnet test ONEVO.sln --filter SharedPlatform
dotnet test ONEVO.sln --filter Workflow
```

---

## Task 6: Configuration + Monitoring Policy Foundation

**Goal:** build tenant settings, monitoring toggles, employee overrides, retention, integrations, and app allowlist policy source of truth.

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

- [[modules/configuration/overview|Configuration]]
- [[modules/configuration/app-allowlist/overview|App Allowlist]]
- [[modules/configuration/employee-overrides/overview|Employee Overrides]]
- [[modules/configuration/integrations/overview|Integrations]]
- [[modules/configuration/retention-policies/overview|Retention Policies]]
- [[Userflow/Configuration/monitoring-toggles|Monitoring Toggles]]
- [[Userflow/Configuration/app-allowlist-setup|App Allowlist Setup]]

### Verification

```bash
dotnet test ONEVO.sln --filter Configuration
dotnet test ONEVO.sln --filter AppAllowlist
```

---

## Task 7: Developer Platform Admin API Foundation

**Goal:** implement the platform-admin backend boundary used by the internal Developer Platform console.

### Backend Module Location

- Feature: `Features/DevPlatform`
- Host: `ONEVO.Admin.Api`
- Endpoint prefix: `/admin/v1/*`
- Auth boundary: platform-admin JWT issuer only; tenant JWTs must be rejected
- DbContext: unified `ApplicationDbContext`; DevPlatform entities have no `TenantId` and must be excluded from tenant query filters

### Acceptance Criteria

- [ ] `ONEVO.Admin.Api` host exists inside `ONEVO.sln`.
- [ ] `ONEVO.Admin.Api` has its own `Program.cs`, controller namespace, auth policy registration, OpenAPI group, health check, and environment config.
- [ ] Admin controllers are routed under `/admin/v1/*`.
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
- [ ] Platform roles are enforced: `super_admin`, `admin`, `viewer`.
- [ ] Admin session records store token hash, account ID, created timestamp, expiry timestamp, and IP address.
- [ ] `last_login_at` updates after successful login.
- [ ] Tests cover Google callback success, inactive account rejection, non-`@onevo.io` rejection, issuer separation, role claim mapping, and session persistence.

### References

- [[modules/dev-platform/overview|Dev Platform Feature]]
- [[developer-platform/overview|Developer Platform Overview]]
- [[developer-platform/auth|Developer Platform Auth]]
- [[developer-platform/system-design|Developer Platform System Design]]
- [[developer-platform/backend/admin-api-layer|Admin API Layer]]
- [[developer-platform/backend/api-contracts|Admin API Contracts]]
- [[developer-platform/database/schema|Developer Platform Schema]]
- [[backend/module-catalog|Backend Module Catalog]]

### Verification

```bash
dotnet test ONEVO.sln --filter DevPlatform
dotnet test ONEVO.sln --filter AdminApi
```

---

## Task 8: Developer Platform Tenant Console Backend

**Goal:** implement the admin tenant lifecycle APIs used by `console.onevo.io`.

### Backend Module References

- Admin host: `ONEVO.Admin.Api`
- Tenant data: `Features/SharedPlatform`, `Features/InfrastructureModule`, `Features/Auth`
- DevPlatform auth/session: `Features/DevPlatform`

### Acceptance Criteria

- [ ] `GET /admin/v1/tenants` returns all tenants, including `provisioning` and `suspended` statuses, with search/filter support.
- [ ] Tenant list includes company name, slug, plan tier, status, employee count, created date, agent count, and last login summary.
- [ ] `POST /admin/v1/tenants` creates a draft tenant in `provisioning` status from account setup data.
- [ ] `GET /admin/v1/tenants/{id}` returns overview, plan, billing dates, status, users summary, agent summary, flags summary, settings summary, and audit summary links.
- [ ] `PATCH /admin/v1/tenants/{id}/status` supports suspend, unsuspend, and activate with role checks.
- [ ] `PATCH /admin/v1/tenants/{id}/subscription` supports exception subscription override with required reason and audit log.
- [ ] `PUT /admin/v1/tenants/{id}/modules` sets active module grants for provisioning and post-provisioning changes.
- [ ] `PATCH /admin/v1/tenants/{id}/settings` writes tenant setting overrides through the Configuration module interface.
- [ ] `POST /admin/v1/tenants/{id}/invite-admin` creates the first tenant super-admin invite.
- [ ] `PATCH /admin/v1/tenants/{id}/provision/confirm` activates a provisioning tenant only after required steps are complete.
- [ ] `POST /admin/v1/tenants/{id}/impersonate` is `super_admin` only, creates a 15-minute non-renewable impersonation token, and always writes an audit log.
- [ ] Provisioning tenants are invisible to tenant-facing `/api/v1/*` queries.
- [ ] Tests cover tenant draft creation, provisioning resume data, activation guard, suspend/unsuspend, subscription override audit, module assignment, invite admin, and impersonation role enforcement.

### References

- [[developer-platform/modules/tenant-console/overview|Tenant Console]]
- [[developer-platform/userflow/tenant-management|Tenant Management Flows]]
- [[developer-platform/userflow/provisioning-flow|Manual Customer Provisioning Flow]]
- [[developer-platform/backend/api-contracts|Admin API Contracts]]
- [[modules/shared-platform/overview|Shared Platform]]
- [[modules/infrastructure/overview|Infrastructure]]
- [[modules/auth/overview|Auth]]

### Verification

```bash
dotnet test ONEVO.sln --filter TenantConsole
dotnet test ONEVO.sln --filter Provisioning
dotnet test ONEVO.sln --filter Impersonation
```

---

## Task 9: Developer Platform Operations Backend

**Goal:** implement feature flag, audit, system config, and app catalog admin APIs.

### Backend Module References

- Feature flags/module grants: `Features/SharedPlatform` and `Features/Configuration`
- Audit reader: shared audit foundation from Task 4
- App catalog: SharedPlatform public catalog interface plus Configuration observed-app reader
- Admin host: `ONEVO.Admin.Api`

### Acceptance Criteria

- [ ] `GET /admin/v1/feature-flags` returns all flags, global defaults, rollout values, and override counts.
- [ ] `GET /admin/v1/feature-flags/{flag}` returns flag detail and per-tenant overrides.
- [ ] `PATCH /admin/v1/feature-flags/{flag}` updates global default or rollout configuration with audit log.
- [ ] `PUT /admin/v1/tenants/{id}/feature-flags` replaces a tenant's flag overrides.
- [ ] `PATCH /admin/v1/tenants/{id}/feature-flags/{flag}` sets or clears one tenant override.
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

- [[developer-platform/modules/feature-flag-manager/overview|Feature Flag Manager]]
- [[developer-platform/userflow/feature-flags|Feature Flag Flows]]
- [[developer-platform/modules/audit-console/overview|Audit Console]]
- [[developer-platform/modules/system-config/overview|System Config]]
- [[developer-platform/modules/app-catalog-manager/overview|App Catalog Manager]]
- [[modules/shared-platform/overview|Shared Platform]]
- [[modules/configuration/overview|Configuration]]
- [[security/compliance|Compliance]]

### Verification

```bash
dotnet test ONEVO.sln --filter FeatureFlags
dotnet test ONEVO.sln --filter Audit
dotnet test ONEVO.sln --filter SystemConfig
dotnet test ONEVO.sln --filter AppCatalog
```
