# OneVo Developer Platform - Overview

## What It Is


It is **not** customer-facing. Tenants, employees, and HR managers never interact with it. It is the internal operator console - think of it as the "back of house" for the entire OneVo SaaS platform.

---

## Who Uses It

| Role | Description |
|:---|:---|
| Platform operations | Provision tenants, manage subscriptions, run impersonation sessions |
| Viewer / read-only | Audit log access, system config review (no write access) |

All users must authenticate with **email/password plus MFA** before a Developer Platform session is created. Google OAuth may be enabled for invited platform managers as an optional account setup/sign-in method, but MFA remains required.

---

## Architecture Overview

```
+--------------------------------------------------+
| OneVo Dev Console                                |
| console.onevo.io - internal only                 |
| Separate Angular app, separate domain            |
+----------------+---------------------------------+
                 | HTTPS + Admin JWT
                 v
+--------------------------------------------------+
| OneVo Backend - Admin API Layer                  |
| /admin/v1/* endpoints                            |
| Separate JWT issuer: platform_admin claims       |
| Wraps existing modules - no new data stores      |
+----------------+---------------------------------+
                 | Module interfaces (internal DI)
                 v
+--------------------------------------------------+
| Existing OneVo Modules                           |
| SharedPlatform, Configuration, Auth              |
| AgentGateway, Infrastructure, all 23 modules     |
+--------------------------------------------------+
```

The dev console talks to the **same OneVo backend** via a dedicated `/admin/v1/*` controller namespace. There is no new microservice. The existing modules own the data - the admin layer exposes privileged operations on top of them with a separate JWT issuer.

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
| Tenant Management | Tenant lifecycle, demo/trial tenants, activation, status changes, and tenant audit history |
| Subscription Plans | Paid plan definitions, base package modules, optional module add-ons, resource-only add-ons, pricing brackets, and billing rules |
| Module Catalog | Master list of actual ONEVO product modules, feature keys, permission keys, and pricing/storage/AI reference values |
| Demo Profiles | Demo/trial workspace defaults, resource limits, module access levels, allowed upgrade plans, and allowed add-ons |
| Requests Center | Demo access requests and trial extension requests |
| Customer Support | Support ticket assignment, replies, internal notes, attachments, and closure |
| Platform Users | Platform manager invites, status, role assignment, MFA state, active sessions, and access history |
| Platform Roles | Custom platform roles, permission matrix, assigned users, and recoverable Super Admin protection |
| Template Management | Reusable tenant setup templates: role, configuration, position, Time Off policy, monitoring policy, app allowlist, onboarding, and data import templates |
| Security Center | Security overview, risky activity, and session review |
| Audit Console | Cross-tenant read-only audit log viewer and exports |
| Compliance Center | Compliance exports, legal holds, legal document versions, and legal/privacy acceptance tracking |
| Reports / Analytics | Cross-tenant operational, commercial, and report exports |
| System Config | Global system configuration for provider credentials, platform service keys, system settings, email, storage, and agent policy defaults |
| Operations | Phase 2 platform health, service/dependency status, alerts, resource utilization, and approved operational actions |
| App Catalog | Global app catalog, `is_public` toggles, and uncatalogued app bulk-approval |

Permission categories are part of the Platform Roles permission matrix, not a separate sidebar item.

Module Catalog manages ONEVO product modules only. It does not decide whether a module is a base package module or an optional add-on; that classification belongs to Subscription Plans. It does not manage Developer Platform sidebar access or platform manager permissions; those are controlled by Platform Roles.

---

## What It Is NOT

| Misconception | Reality |
|:---|:---|
| A customer developer portal | No - customers never access this. No customer API keys here. |
| A second backend service | No - the admin API layer lives inside the existing OneVo backend. |
| A `/platform-admin` route in the main frontend | No - it is a completely separate Angular application on a separate domain. |
| A duplicate of existing data stores | No - runtime overrides, settings, and tenant data live in the existing schema. The console reads/writes those through the admin API. |
| Phase 2 customer webhook/API infrastructure | No - customer-facing developer APIs are a Phase 2 concept, entirely separate. |

---

## Implementation Reference


---

## Why a Separate Application

Rather than adding an admin route inside the main customer-facing frontend, the dev console is deployed as a completely separate app. The reasons are:

1. **Different auth model** - Developer Platform email/password plus MFA and platform-admin JWT, not tenant JWT. The two systems must not share session infrastructure.
2. **Network isolation** - The console can be IP-restricted or VPN-gated without affecting customer traffic at all.
3. **No accidental surface exposure** - A permission bug in the main frontend cannot expose admin controls to customers.
4. **Independent deployment** - The console can be versioned, deployed, and rolled back independently of the main product release cycle.

---

## Connection Model

```
Internet / Customer Traffic
        |
        v
  app.onevo.io ------------------------------> OneVo Backend
  (main product)        tenant JWT             /api/v1/* endpoints

Internal / VPN only
        |
        v
  console.onevo.io --------------------------> OneVo Backend
  (dev console)         platform-admin JWT     /admin/v1/* endpoints
```

The two traffic paths hit the same backend but use **completely separate JWT issuers**. An admin JWT is rejected at tenant endpoints; a tenant JWT is rejected at admin endpoints. The isolation is enforced at the token level, not just at the network level.


