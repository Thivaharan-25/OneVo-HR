# Admin API Layer

## Overview

> Phase 1 deployment rule: Developer Platform APIs live under `/admin/v1/*` inside the single `ONEVO.Api` backend host. Do not create or deploy a separate admin backend service.

The Admin API Layer is a controller namespace inside `ONEVO.Api`. It exposes platform-level operations for the Developer Console (`console.onevo.io`) under the `/admin/v1/*` path prefix.

This is not a new microservice. No new backend process, no new deployment unit, and no duplicate data boundary are introduced.

---

## Architecture Decisions

### Admin API Layer, Not A New Service

The Developer Console talks to the existing OneVo backend through `/admin/v1/*`. Existing modules already own the data, so the admin layer is an access and authorization boundary, not a second product backend.

**Consequences:**
- No duplicate backend host.
- No duplicate business logic or shadow tables.
- Feature flags, tenant settings, subscription data, and audit logs remain in canonical module tables.
- Admin controllers call module interfaces through dependency injection.
- Platform-level cross-tenant reads and writes must be explicit in interface and implementation names.

### Developer Accounts Are Platform-Level Identities

Developer Platform accounts are not tenant users. They live in platform-owned tables such as `platform_users`, `platform_roles`, and `platform_user_roles`, with no tenant association on the platform account itself.

Tenant-facing `users` remain scoped to a tenant. Platform-admin authentication must not reuse tenant sessions or tenant roles.

---

## What This Layer Is

| Aspect | Detail |
|---|---|
| Controller namespace | `ONEVO.Api/Controllers/Admin/` |
| Route prefix | `/admin/v1/*` |
| Caller | Developer Console only |
| Auth boundary | Dedicated platform-admin issuer and `PlatformAdmin` policy |
| Business logic | Existing module interfaces and services |
| Data ownership | Existing module tables; no admin shadow stores |

## What This Layer Is Not

| Not | Reason |
|---|---|
| Separate microservice | Phase 1 has one backend host: `ONEVO.Api` |
| Separate data store | Platform operations use canonical module tables |
| Tenant API replacement | Customer APIs stay under `/api/v1/*` |
| Direct DbContext bypass | Controllers call Application/module interfaces |

---

## Namespace Structure

```text
ONEVO.Api/
  Controllers/
    Admin/
      TenantsController.cs
      RoleTemplatesController.cs
      FeatureFlagsController.cs
      AuditController.cs
      ConfigController.cs
      RequestsController.cs
      ReportsController.cs
      ApiKeysController.cs
```

Controllers in this namespace are thin. They do not contain business logic; they resolve existing module interfaces via DI and delegate all work to them.

All controllers under `ONEVO.Api/Controllers/Admin/` use:

```csharp
[Authorize(Policy = "PlatformAdmin")]
[Route("admin/v1/[controller]")]
```

---

## Dependency Injection Wiring

Controllers call the same interfaces used by tenant-facing code, injected through the standard DI container:

```csharp
public class TenantsController : ControllerBase
{
    private readonly ITenantService _tenantService;
    private readonly IModuleProvisioningService _provisioning;
    private readonly IRoleTemplateService _roleTemplates;
    private readonly IImpersonationService _impersonation;

    public TenantsController(
        ITenantService tenantService,
        IModuleProvisioningService provisioning,
        IRoleTemplateService roleTemplates,
        IImpersonationService impersonation)
    {
        _tenantService = tenantService;
        _provisioning = provisioning;
        _roleTemplates = roleTemplates;
        _impersonation = impersonation;
    }
}
```

No new service registrations are required for existing module behavior. Only Admin API-specific orchestration services, such as impersonation, are new registrations.

---

## Authorization Policy: `PlatformAdmin`

The `PlatformAdmin` policy is defined at startup and requires:

1. A valid JWT signed by the platform-admin issuer.
2. `iss = onevo-platform-admin`.
3. An active platform user.
4. The platform permission required by the endpoint.

Any request without a valid platform-admin token receives `401 Unauthorized`. A valid platform-admin token without the required permission receives `403 Forbidden`.

---

## JWT Issuer Separation

The Admin API uses a dedicated JWT issuer to isolate platform-admin traffic from tenant-facing traffic.

| Property | Platform Admin JWT | Tenant JWT |
|---|---|---|
| `iss` claim | `onevo-platform-admin` | `onevo-tenant` or tenant-specific issuer |
| Signing key | Platform admin signing key | Tenant JWT signing key |
| Accepted by `/admin/v1/*` | Yes | No |
| Accepted by `/api/v1/*` | No | Yes |
| TTL | 30 minutes | Standard tenant session TTL |
| Subject | `platform_user_id` | `tenant_user_id` |

Cross-use is rejected at the policy level. A tenant JWT cannot call admin endpoints, and a platform-admin JWT cannot be replayed at tenant endpoints.

---

## Impersonation Policy: `ImpersonationOnly`

The `POST /admin/v1/tenants/{id}/impersonate` endpoint issues short-lived impersonation tokens. These tokens carry a distinct claim and are gated by a separate policy.

| Property | Value |
|---|---|
| Claim | `impersonation = true` |
| TTL | 15 minutes |
| Policy | `ImpersonationOnly` |

Impersonation tokens are consumed only by tenant-facing endpoints that explicitly allow impersonated access. `ImpersonationOnly` is not a general access grant.

---

## Developer Console Frontend

| Property | Value |
|---|---|
| Framework | Angular 21 |
| Domain | `console.onevo.io` |
| Auth provider | Email/password plus mandatory MFA; optional Google OAuth setup/sign-in for invited managers where enabled |
| API calls | `[backend]/admin/v1/*` with platform-admin JWT |
| Session storage | Platform-admin JWT stored in httpOnly cookie after MFA succeeds |

The Developer Console is separate from the tenant-facing customer app. It has separate routing, auth/session handling, and deployment.

---

## Deployment Boundary

The Developer Console frontend can be deployed or rolled back without affecting the customer app. The backend admin namespace remains inside the same `ONEVO.Api` host as customer APIs.

Network restrictions such as VPN, IP allowlist, WAF rules, or private access controls belong at the infrastructure layer. Application code still enforces the `PlatformAdmin` policy on every admin endpoint.

---

## Summary

- Single backend process: `ONEVO.Api`.
- Customer APIs live under `/api/v1/*`.
- Developer Platform APIs live under `/admin/v1/*`.
- Admin controllers call existing module interfaces.
- Platform-admin and tenant JWT issuers are separate.
- No separate admin backend service is part of Phase 1.
