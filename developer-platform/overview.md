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

## Company And Tenant Model

In ONEVO, every company is a tenant. The Developer Platform provisions and manages companies as independent tenants with separate subscription, module entitlement, settings, branding, users, employees, and audit history.

Separate operating companies must not be modeled as legal entities inside one tenant. When companies need to work together, the Developer Platform manages an explicit [[modules/shared-platform/company-connections/overview|Company Connection]] between their tenants.

Owner email matching can make two tenants eligible for a connection, but it does not silently expose data. Cross-company access requires an active connection, scoped permission, module entitlement where applicable, and audit logging.

---

## Modules

Developer Platform modules follow the same KB shape as ONEVO product modules: each module folder contains `overview.md`, `end-to-end-logic.md`, and `testing.md`. User journeys live under `developer-platform/userflow/`.

| Module | Purpose |
|:---|:---|
| Dashboard | Cross-tenant operational summary and quick links |
| Tenant Console | Tenant lifecycle, provisioning, activation, status changes, and impersonation |
| Subscription Manager | Reusable plans, payment gateways, invoices, and commercial rules |
| Platform Access | Platform account invites, platform roles, platform permissions, and session revocation |
| Global Policies | Platform policy defaults and explicit tenant-impact propagation |
| Module Catalog Manager | ONEVO product module catalog: pricing, package inclusion, permission ownership, limits, and setup links |
| Role Template Manager | Module-filtered tenant role templates and tenant role materialization |
| Feature Flag Manager | Global flags and per-tenant overrides |
| Platform Health | Overall health status and dependency summary |
| Services Monitor | Detailed service/component health and safe service actions |
| Device Management | Cross-tenant agent/device visibility and approved agent commands |
| Infrastructure Operations | Infrastructure capacity and dependency summaries |
| Background Jobs | Scheduled/queued job observability and approved retries |
| Security Center | Security overview, risky activity, and session review |
| Audit Console | Cross-tenant read-only audit log viewer and exports |
| Compliance Center | Compliance exports and legal holds |
| Data Retention | Retention policy management and retention sweep observability |
| Platform Analytics | Cross-tenant operational and commercial analytics |
| Report Manager | Platform report catalog and exports |
| System Config | Global defaults editor and per-tenant settings override |
| App Catalog Manager | Global app catalog, `is_public` toggles, uncatalogued app bulk-approval |
| Desktop Agent Version Manager | Agent version catalog, deployment rings, force-update, and rollback |
| Platform API Key Manager | *(Phase 2)* Platform-level API key management |

Module Catalog Manager manages ONEVO product modules only. It does not manage Developer Platform sidebar sections or platform manager access; those are controlled by Platform Access.

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

## Implementation Reference

The backend implementation plan for subscription provisioning is at [[developer-platform/plans/subscription-provisioning-implementation-plan|Subscription Provisioning Implementation Plan]] — it documents the resolved architectural decisions, data model contracts, and phase-by-phase task breakdown for the backend team.

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
