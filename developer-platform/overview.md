# OneVo Developer Platform — Overview

## What It Is

The OneVo Developer Platform is a **separate, standalone internal web application** at `console.onevo.io`. It is the control plane used exclusively by OneVo's internal engineering and operations team to maintain, configure, and monitor the OneVo platform.

It is **not** customer-facing. Tenants, employees, and HR managers never interact with it. It is the internal operator console — think of it as the "back of house" for the entire OneVo SaaS platform.

---

## Who Uses It

| Role | Description |
|:---|:---|
| Engineering team | Deploy agent versions, manage feature flags, debug tenant issues |
| Platform operations | Provision tenants, manage subscriptions, run impersonation sessions |
| Viewer / read-only | Audit log access, system config review (no write access) |

All users must authenticate via **Google OAuth** using an approved `@onevo.io` email. No password login.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────┐
│           OneVo Dev Console                     │
│      (console.onevo.io — internal only)         │
│   Separate Next.js app, separate domain         │
└────────────────┬────────────────────────────────┘
                 │  HTTPS + Admin JWT
                 ▼
┌─────────────────────────────────────────────────┐
│        OneVo Backend — Admin API Layer          │
│   /admin/v1/* endpoints (new namespace)         │
│   Separate JWT issuer: platform_admin claims    │
│   Wraps existing modules — no new data stores   │
└────────────────┬────────────────────────────────┘
                 │  Module interfaces (internal DI)
                 ▼
┌─────────────────────────────────────────────────┐
│           Existing OneVo Modules                │
│  SharedPlatform · Configuration · Auth          │
│  AgentGateway · Infrastructure · all 23 modules │
└─────────────────────────────────────────────────┘
```

The dev console talks to the **same OneVo backend** via a dedicated `/admin/v1/*` controller namespace. There is no new microservice. The existing modules own the data — the admin layer exposes privileged operations on top of them with a separate JWT issuer.

---

## Modules

| Module | Purpose |
|:---|:---|
| Tenant Console | Manage tenants, subscriptions, impersonation, provisioning wizard |
| Feature Flag Manager | Global flags, per-tenant overrides, module enable/disable |
| Desktop Agent Version Manager | Version catalog, deployment rings, force-update |
| Audit Console | Cross-tenant read-only audit log viewer |
| System Config | Global defaults editor, per-tenant settings override |
| Platform API Keys | *(Phase 2)* Platform-level API key management |

---

## What It Is NOT

| Misconception | Reality |
|:---|:---|
| A customer developer portal | No — customers never access this. No customer API keys here. |
| A second backend service | No — the admin API layer lives inside the existing OneVo backend. |
| A `/platform-admin` route in the main frontend | No — it is a completely separate Next.js application on a separate domain. |
| A duplicate of existing data stores | No — feature flags, settings, and tenant data live in the existing schema. The console reads/writes those through the admin API. |
| Phase 2 customer webhook/API infrastructure | No — customer-facing developer APIs are a Phase 2 concept, entirely separate. |

---

## Why a Separate Application

Rather than adding an admin route inside the main customer-facing frontend, the dev console is deployed as a completely separate app. The reasons are:

1. **Different auth model** — Developer Google SSO, not tenant JWT. The two systems must not share session infrastructure.
2. **Network isolation** — The console can be IP-restricted or VPN-gated without affecting customer traffic at all.
3. **No accidental surface exposure** — A permission bug in the main frontend cannot expose admin controls to customers.
4. **Independent deployment** — The console can be versioned, deployed, and rolled back independently of the main product release cycle.

---

## Connection Model

```
Internet / Customer Traffic
        │
        ▼
  app.onevo.io  ──────────────────────────────► OneVo Backend
  (main product)        tenant JWT              /api/v1/* endpoints

Internal / VPN only
        │
        ▼
  console.onevo.io ───────────────────────────► OneVo Backend
  (dev console)         platform-admin JWT      /admin/v1/* endpoints
```

The two traffic paths hit the same backend but use **completely separate JWT issuers**. An admin JWT is rejected at tenant endpoints; a tenant JWT is rejected at admin endpoints. The isolation is enforced at the token level, not just at the network level.
