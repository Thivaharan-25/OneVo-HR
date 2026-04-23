# OneVo Developer Platform — System Design

## Architecture Decisions

### Decision 1: Admin API Layer, Not a New Service

The dev console does **not** get its own microservice. It talks to the existing OneVo backend via a dedicated `/admin/v1/*` controller namespace. This keeps the platform simple — the existing modules already own all the data. The admin layer is purely an access/authorization boundary, not a new data boundary.

**Consequences:**
- No new database schemas for core platform data
- No duplicate business logic — no parallel data structures or shadow copies
- Feature flags, tenant settings, agent version data, and audit logs all remain in their canonical tables
- The admin layer calls module interfaces via dependency injection — it does not reach into module internals
- All data reads and writes go through existing module interfaces (no direct table access)

---

### Decision 2: Developer Accounts Are Platform-Level Identities

The existing `users` table is scoped to tenants (it has a `tenant_id` column). Developer platform accounts have no tenant association and must not live there.

**New table:** `dev_platform_accounts`

| Column | Type | Notes |
|:---|:---|:---|
| `id` | UUID | Primary key |
| `email` | string | Must be `@onevo.io` domain |
| `google_sub` | string | Google OAuth subject identifier |
| `role` | enum | `super_admin`, `admin`, `viewer` |
| `created_at` | timestamp | |
| `last_login_at` | timestamp | |
| `is_active` | bool | Soft disable without deleting |

There is no `tenant_id` column. These accounts are platform-level.

---

## Backend Namespace: `ONEVO.Admin.Api/`

All admin controller code lives in a dedicated namespace within the existing backend project.

```
ONEVO.Backend/
├── ONEVO.Api/                  ← existing customer-facing controllers
│   └── Controllers/
├── ONEVO.Admin.Api/            ← new namespace (this work)
│   ├── Controllers/
│   │   ├── TenantsController.cs
│   │   ├── FeatureFlagsController.cs
│   │   ├── AgentVersionsController.cs
│   │   ├── AuditController.cs
│   │   └── SystemConfigController.cs
│   ├── Middleware/
│   │   └── PlatformAdminAuthMiddleware.cs
│   └── Policies/
│       └── PlatformAdminPolicy.cs
├── ONEVO.Modules/              ← existing modules (unchanged)
│   ├── SharedPlatform/
│   ├── Configuration/
│   ├── Auth/
│   ├── AgentGateway/
│   └── ...23 modules
```

All controllers in `ONEVO.Admin.Api/` are decorated with:

```csharp
[Authorize(Policy = "PlatformAdmin")]
[Route("admin/v1/[controller]")]
```

The `PlatformAdmin` policy validates:
1. Token issuer is `onevo-platform-admin`
2. Token audience matches the admin API audience
3. The `platform_role` claim is present and valid

---

## JWT Issuer Separation

Two completely independent JWT issuers exist in the backend:

| Property | Tenant Issuer | Admin Issuer |
|:---|:---|:---|
| `iss` claim | `onevo-tenant` | `onevo-platform-admin` |
| Signing key | Tenant JWT signing key | Platform admin signing key (separate secret) |
| Accepted at | `/api/v1/*` endpoints only | `/admin/v1/*` endpoints only |
| Token TTL | Configurable per tenant | 30 minutes (admin), 15 min (impersonation) |
| Subject | `tenant_user_id` | `dev_platform_account_id` |

**Cross-use is rejected at the policy level.** The `PlatformAdmin` policy explicitly checks `iss == "onevo-platform-admin"` and rejects any token that does not match — including a valid tenant JWT. The inverse applies at tenant endpoints.

---

## DI Wiring — Admin Layer to Existing Modules

Admin controllers call existing module interfaces via standard dependency injection. They do not instantiate module services directly or bypass module boundaries.

```
TenantsController
    └── ITenantManagementService       (SharedPlatform module)
    └── ISubscriptionService           (Configuration module)
    └── IImpersonationService          (Auth module — new method)

FeatureFlagsController
    └── IFeatureFlagService            (Configuration module)

AgentVersionsController
    └── IAgentVersionService           (AgentGateway module)

AuditController
    └── IAuditLogReader                (SharedPlatform module — read-only interface)

SystemConfigController
    └── IGlobalConfigService           (Configuration module)
```

No module gains a direct dependency on `ONEVO.Admin.Api/`. The dependency flows inward only (admin layer → modules, never modules → admin layer).

---

## Frontend: Dev Console Application

| Property | Value |
|:---|:---|
| Framework | Next.js (App Router) |
| Domain | `console.onevo.io` |
| Auth provider | Google OAuth via NextAuth.js |
| API calls | All go to `[backend]/admin/v1/*`, passing platform-admin JWT in `Authorization: Bearer` header |
| Session storage | Server-side session (NextAuth), platform-admin JWT stored in httpOnly cookie |

The dev console is a **completely separate Next.js project** from the main `app.onevo.io` frontend. It shares no code, no session infrastructure, and no deployment pipeline with the main product.

---

## Deployment Topology

```
                    ┌──────────────────────────────┐
                    │   VPN / IP Allowlist Layer    │
                    │  (infrastructure-level gate)  │
                    └──────────────┬───────────────┘
                                   │
                    ┌──────────────▼───────────────┐
                    │     console.onevo.io          │
                    │   Next.js — Dev Console       │
                    │   Deployed independently      │
                    └──────────────┬───────────────┘
                                   │ HTTPS + Admin JWT
                    ┌──────────────▼───────────────┐
                    │     OneVo Backend             │
                    │  /admin/v1/* namespace        │
                    │  ONEVO.Admin.Api controllers  │
                    └──────────────┬───────────────┘
                                   │ DI / module interfaces
                    ┌──────────────▼───────────────┐
                    │     Existing OneVo Modules    │
                    │  SharedPlatform · Config      │
                    │  Auth · AgentGateway · etc.   │
                    └──────────────────────────────┘
```

**Deployment independence:** The dev console can be deployed, rolled back, or taken offline without affecting the main product. The admin API namespace can be toggled off at the backend level (e.g., via a feature flag or build-time switch) without impacting any customer-facing endpoints.

**Network isolation:** The VPN/IP allowlist gate is applied at the infrastructure layer (load balancer or WAF rule), not in application code. This means even a catastrophic application bug cannot expose the console to the public internet.
