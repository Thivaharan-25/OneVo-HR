# Admin API Layer

## Overview

The Admin API Layer is a new controller namespace (`ONEVO.Admin.Api/`) added to the **existing OneVo backend**. It exposes platform-level operations under the `/admin/v1/*` path prefix, used exclusively by the Developer Console (`console.onevo.io`).

This is **not a new microservice**. No new service process, no new deployment unit — only a new namespace within the same backend process.

---

## What This Layer Is (and Is Not)

| Aspect | Detail |
|---|---|
| **Is** | A new controller namespace in the existing OneVo backend |
| **Is** | A thin orchestration layer — controllers call existing module interfaces |
| **Is** | Protected by a separate JWT issuer and policy |
| **Is NOT** | A separate microservice or deployment |
| **Is NOT** | A new data store — reads/writes existing module tables |
| **Is NOT** | A replacement for tenant-facing APIs |

---

## Namespace Structure

```
ONEVO.Admin.Api/
  Controllers/
    TenantsController.cs
    FeatureFlagsController.cs
    AgentVersionsController.cs
    AuditController.cs
    ConfigController.cs
    ApiKeysController.cs       ← Phase 2
```

Controllers in this namespace are thin. They do not contain business logic — they resolve existing module interfaces via DI and delegate all work to them.

---

## Dependency Injection Wiring

Controllers call the **same interfaces** used by tenant-facing code, injected via the standard DI container:

```csharp
public class TenantsController : ControllerBase
{
    private readonly ITenantService _tenantService;
    private readonly IModuleProvisioningService _provisioning;
    private readonly IImpersonationService _impersonation;

    public TenantsController(
        ITenantService tenantService,
        IModuleProvisioningService provisioning,
        IImpersonationService impersonation)
    {
        _tenantService = tenantService;
        _provisioning = provisioning;
        _impersonation = impersonation;
    }
}
```

No new service registrations are required for existing modules. Only Admin API-specific services (e.g., `IImpersonationService`) are new registrations.

---

## Authorization Policy: `PlatformAdmin`

All controllers and actions in `ONEVO.Admin.Api/` are decorated with:

```csharp
[Authorize(Policy = "PlatformAdmin")]
```

The `PlatformAdmin` policy is defined at startup and requires two conditions:

1. Token is a valid JWT signed by the **platform-admin issuer** (`iss: onevo-platform-admin`)
2. Token has not expired (TTL: **30 minutes**)

```csharp
services.AddAuthorization(options =>
{
    options.AddPolicy("PlatformAdmin", policy =>
        policy.RequireClaim("iss", "onevo-platform-admin"));
});
```

Any request without a valid platform-admin token receives `401 Unauthorized`.

---

## JWT Issuer Separation

The Admin API uses a **dedicated JWT issuer** to ensure complete isolation from tenant-facing traffic.

| Property | Platform Admin JWT | Tenant JWT |
|---|---|---|
| `iss` claim | `onevo-platform-admin` | `onevo-tenant` (or tenant-specific) |
| Accepted by Admin API | Yes | No — rejected at policy check |
| Accepted by tenant endpoints | No — wrong issuer | Yes |
| TTL | 30 minutes | Standard session TTL |

**Why issuer separation matters:** Tenant endpoints validate JWTs against the tenant issuer only. A platform-admin token cannot be replayed at a tenant endpoint, even if intercepted — the issuer mismatch causes immediate rejection. This prevents privilege escalation from the console into tenant data paths.

---

## Impersonation Policy: `ImpersonationOnly`

The `POST /admin/v1/tenants/{id}/impersonate` endpoint issues short-lived impersonation tokens. These tokens carry a distinct claim and are gated by a separate policy.

**Impersonation token properties:**

| Property | Value |
|---|---|
| `impersonation` claim | `true` |
| TTL | **15 minutes** |
| Policy | `ImpersonationOnly` |

```csharp
services.AddAuthorization(options =>
{
    options.AddPolicy("ImpersonationOnly", policy =>
        policy.RequireClaim("impersonation", "true"));
});
```

Impersonation tokens are issued by the Admin API and consumed by tenant-facing endpoints that explicitly allow impersonated access. The `ImpersonationOnly` policy is applied only to those specific tenant endpoints — it is **not** a general-access grant.

---

## Summary

- Single backend process, new controller namespace
- All business logic lives in existing module interfaces
- DI wires admin controllers to the same services as tenant controllers
- Hard JWT issuer boundary: platform-admin tokens cannot reach tenant endpoints
- Two authorization policies: `PlatformAdmin` (30 min TTL) and `ImpersonationOnly` (15 min TTL, `impersonation: true` claim)
