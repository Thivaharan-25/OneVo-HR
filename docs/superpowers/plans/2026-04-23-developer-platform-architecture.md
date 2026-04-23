# OneVo Developer Platform — Architecture Plan

**Date:** 2026-04-23
**Status:** Planning
**Supersedes:** Section 10 (`/platform-admin`) of `2026-04-21-unified-platform-architecture.md`

---

## 1. What This Is

A **separate, standalone web application** used exclusively by OneVo's internal engineering and operations team to maintain, control, and monitor the OneVo platform. Customers (tenants, employees, HR managers) never see it.

It is **not** a customer-facing developer portal (no customer API keys, no customer webhooks). Those are a Phase 2 concept. This is the internal control plane.

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

**Why separate app, not a `/platform-admin` route inside the main frontend:**
- Different auth model (developer Google SSO / email, not tenant JWT)
- Can be IP-restricted or VPN-gated without affecting customer traffic
- No risk of accidentally exposing admin surfaces to customers via permission bug
- Deployed and versioned independently

---

## 2. Core Architecture Decisions

### Decision 1: Admin API Layer, Not a New Service
The dev console talks to the **same OneVo backend** via a dedicated `/admin/v1/*` controller namespace. No new microservice. The existing modules already own the data — the admin layer exposes privileged operations on them with a separate JWT issuer.

New backend namespace: `ONEVO.Admin.Api/`
- Controllers live here, call module interfaces via DI
- Protected by `[Authorize(Policy = "PlatformAdmin")]`
- Separate JWT issuer (`iss: onevo-platform-admin`) — tokens from this issuer are rejected by all tenant-facing endpoints

### Decision 2: Developer Accounts Are Separate from Tenant Users
The existing `users` table is scoped to tenants. Developer platform accounts live in a new `dev_platform_accounts` table with no `tenant_id` — they're platform-level identities.

### Decision 3: Platform Does Not Duplicate Existing Logic
Feature flags, module toggles, tenant settings, agent commands all exist as tables in the current schema. The dev console reads and writes those tables through admin API endpoints. No parallel data structures.

---

## 3. Developer Platform Modules

### Module 1: Tenant Console
**Controls:** `tenants`, `users`, `tenant_settings`, `subscription_plans`

- List all tenants: name, plan tier, status, employee count, created date
- Per-tenant detail: subscription, feature access grants, last login, agent count
- Suspend / unsuspend tenant (sets `tenants.status`)
- Impersonation: generate short-lived "impersonate" JWT scoped to a tenant's super-admin role (for support debugging)
- **Subscription override** *(exception tool, not the primary path)*: manually set or change a tenant's plan, bypassing Stripe — used for enterprise deals closed by sales, trial extensions, test accounts, or fixing a Stripe sync error. The normal/primary path is customer self-signup → Stripe → plan auto-assigned.

#### Manual Customer Provisioning *(optional — use when needed)*
The dev team can fully provision a new customer account without the customer going through self-service signup. This is not required for every customer — it's available when the situation calls for it (enterprise onboarding, white-glove setup, internal test tenants).

Provisioning wizard (step-by-step, all steps completable in one session):

1. **Account setup** — company name, slug, country, industry, legal entity name, timezone
2. **Plan assignment** — pick subscription plan + set billing start date (Stripe charge optional at this stage)
3. **Module selection** — toggle which modules are active for this tenant (writes `module_registry`)
4. **Initial configuration** — set key tenant_settings: monitoring mode, leave policies defaults, transparency mode for desktop agent
5. **Admin user invite** — create the first super-admin user for the tenant and send invite email with set-password link
6. **Review & confirm** — summary of everything set, one-click confirm → tenant status set to `active`

At any step the wizard can be saved as a draft (`tenants.status = 'provisioning'`) and resumed later. A tenant in `provisioning` status is invisible to the main OneVo app until confirmed.

### Module 2: Feature Flag Manager
**Controls:** `feature_flags`, `feature_access_grants`, `module_registry` (SharedPlatform)

- Global flag list: all flags, default values, rollout percentage
- Per-flag: toggle globally or override per tenant
- Per-tenant flag override view: see every flag override for a given tenant
- Module enable/disable: turn modules on or off per tenant (writes `module_registry`)
- Audit trail: every flag change is logged with developer account + timestamp

### Module 3: Desktop Agent Version Manager
**Controls:** New `agent_version_releases`, `agent_deployment_rings`, `agent_deployment_ring_assignments` tables + `agent_commands` (AgentGateway)

- Version catalog: list all desktop agent releases, release notes, min OS version
- Mark a version as: `stable`, `beta`, `deprecated`, `recalled`
- Deployment rings:
  - Ring 0 — internal OneVo test tenants
  - Ring 1 — opted-in beta tenants
  - Ring 2 — all tenants (GA)
- Assign tenants to rings
- Force-update command: push `UPDATE_AGENT` command to all agents in a ring via AgentGateway
- Rollback: force-pin a tenant's agents to a previous version

### Module 4: Audit Console
**Controls:** `audit_logs` (Auth module — read-only)

- Cross-tenant audit log viewer with full filter set: tenant, user, action, resource, date range
- Export to CSV
- Cannot modify records (read-only)

### Module 5: System Config
**Controls:** `tenant_settings` defaults, `monitoring_feature_toggles` defaults, `integration_connections` global config

- Set global default values that new tenants inherit on creation
- Override individual tenant settings without tenant admin involvement (support escalations)
- View integration connection health across all tenants

### Module 6: Platform API Keys *(Phase 2)*
**Controls:** New `platform_api_keys` table

- Issue platform-level API keys for external system integrations (not tenant-specific)
- Set scopes, expiry, rate limits
- Revoke keys immediately
- View key usage logs

---

## 4. New Database Tables

These are the **only net-new tables** this platform requires. Everything else uses existing tables via admin API.

```
dev_platform_accounts
├── id               uuid PK
├── email            varchar(255) UNIQUE
├── full_name        varchar(255)
├── google_sub       varchar(255) — Google OAuth subject
├── role             varchar(30)  — 'super_admin' | 'admin' | 'viewer'
├── is_active        boolean
├── created_at       timestamptz
└── last_login_at    timestamptz

dev_platform_sessions
├── id               uuid PK
├── account_id       uuid FK → dev_platform_accounts
├── token_hash       varchar(64)
├── created_at       timestamptz
├── expires_at       timestamptz
└── ip_address       varchar(45)

agent_version_releases
├── id               uuid PK
├── version          varchar(20)  — semver e.g. '1.4.2'
├── release_channel  varchar(20)  — 'stable' | 'beta' | 'recalled'
├── min_os_version   varchar(20)
├── release_notes    text
├── download_url     varchar(500)
├── published_by_id  uuid FK → dev_platform_accounts
├── published_at     timestamptz
└── recalled_at      timestamptz (nullable)

agent_deployment_rings
├── id               uuid PK
├── ring_number      int          — 0, 1, 2
├── name             varchar(50)  — 'Internal' | 'Beta' | 'GA'
└── description      text

agent_deployment_ring_assignments
├── id               uuid PK
├── tenant_id        uuid FK → tenants
├── ring_id          uuid FK → agent_deployment_rings
├── assigned_by_id   uuid FK → dev_platform_accounts
└── assigned_at      timestamptz

-- Phase 2 only:
platform_api_keys
├── id               uuid PK
├── key_hash         varchar(64)
├── name             varchar(100)
├── scopes           text[]
├── created_by_id    uuid FK → dev_platform_accounts
├── expires_at       timestamptz (nullable)
├── revoked_at       timestamptz (nullable)
└── created_at       timestamptz
```

**Schema catalog impact:** +5 tables (Phase 1) / +6 tables (Phase 2). Schema catalog total moves from 170 → 175 (Phase 1) or 176 (Phase 2).

**Existing table change:** `tenants.status` enum must be updated to include `'provisioning'` alongside `'active'` and `'suspended'`. A tenant in `provisioning` status is excluded from all tenant-facing queries — only visible in the admin API.

---

## 5. Admin API Endpoints (New `/admin/v1/*` Namespace)

All endpoints require `Authorization: Bearer <platform-admin-jwt>`.

```
GET    /admin/v1/tenants                           → Tenant list
POST   /admin/v1/tenants                           → Create tenant (manual provisioning — step 1)
GET    /admin/v1/tenants/{id}                      → Tenant detail
PATCH  /admin/v1/tenants/{id}/status               → Suspend/unsuspend/activate
POST   /admin/v1/tenants/{id}/impersonate          → Issue impersonation token
PATCH  /admin/v1/tenants/{id}/subscription         → Override subscription tier (exception tool)
PUT    /admin/v1/tenants/{id}/modules              → Set active modules for tenant (provisioning step 3)
PATCH  /admin/v1/tenants/{id}/provision/confirm    → Finalise provisioning draft → set status active
POST   /admin/v1/tenants/{id}/invite-admin         → Create first super-admin + send invite email (provisioning step 5)

GET    /admin/v1/feature-flags                     → All flags + defaults
GET    /admin/v1/feature-flags/{flag}              → Flag detail + per-tenant overrides
PATCH  /admin/v1/feature-flags/{flag}              → Toggle global default
PUT    /admin/v1/tenants/{id}/feature-flags        → Set all overrides for a tenant
PATCH  /admin/v1/tenants/{id}/feature-flags/{flag} → Set single override

GET    /admin/v1/agent-versions                    → Version catalog
POST   /admin/v1/agent-versions                    → Publish new version
PATCH  /admin/v1/agent-versions/{id}/channel       → Change channel (stable/beta/recalled)
POST   /admin/v1/agent-versions/{id}/force-update  → Push UPDATE_AGENT command to ring
GET    /admin/v1/agent-rings                       → Ring list + tenant assignments
PUT    /admin/v1/tenants/{id}/agent-ring           → Assign tenant to ring

GET    /admin/v1/audit-logs                        → Cross-tenant audit log (filterable)

GET    /admin/v1/config/defaults                   → Global tenant setting defaults
PATCH  /admin/v1/config/defaults                   → Update defaults
GET    /admin/v1/tenants/{id}/settings             → Per-tenant settings
PATCH  /admin/v1/tenants/{id}/settings             → Override per-tenant settings

-- Phase 2:
GET    /admin/v1/api-keys                          → Platform API key list
POST   /admin/v1/api-keys                          → Issue new key
DELETE /admin/v1/api-keys/{id}                     → Revoke key
```

---

## 6. Frontend: Dev Console App Structure

**Tech:** Next.js 15 (App Router) · TypeScript · Tailwind · shadcn/ui
**Design:** Dark-theme admin aesthetic (slate/zinc palette) — distinct from main product
**Domain:** `console.onevo.io` (or internal dev URL during development)
**Auth:** Google OAuth 2.0 → exchange for platform-admin JWT

```
dev-console/                           ← Separate Next.js app (separate repo or monorepo workspace)
├── app/
│   ├── layout.tsx                     # Root: providers, dark ThemeProvider
│   ├── not-found.tsx
│   │
│   ├── (auth)/                        # Unauthenticated
│   │   └── login/
│   │       └── page.tsx               # Google OAuth login (no password)
│   │
│   └── (console)/                     # Authenticated — console layout
│       ├── layout.tsx                 # Sidebar + topbar
│       ├── page.tsx                   # Dashboard: tenant count, active flags, agent ring health
│       │
│       ├── tenants/
│       │   ├── page.tsx               # Tenant list: search, filter by plan/status
│       │   ├── new/
│       │   │   └── page.tsx           # Manual provisioning wizard (6-step, saveable draft)
│       │   └── [tenantId]/
│       │       ├── page.tsx           # Tenant detail: overview + quick actions
│       │       ├── provision/page.tsx # Resume/complete a provisioning draft
│       │       ├── flags/page.tsx     # Feature flag overrides for this tenant
│       │       ├── settings/page.tsx  # Tenant settings override
│       │       └── audit/page.tsx     # Audit log filtered to this tenant
│       │
│       ├── feature-flags/
│       │   ├── page.tsx               # All flags: name, default, override count
│       │   └── [flagId]/
│       │       └── page.tsx           # Flag detail: per-tenant overrides table
│       │
│       ├── agents/
│       │   ├── versions/
│       │   │   ├── page.tsx           # Version catalog: stable, beta, deprecated
│       │   │   └── [versionId]/page.tsx # Version detail + force-update to ring
│       │   └── rings/
│       │       └── page.tsx           # Ring assignments: drag tenant between rings
│       │
│       ├── audit/
│       │   └── page.tsx               # Cross-tenant audit log: filters + CSV export
│       │
│       ├── config/
│       │   └── page.tsx               # Global defaults editor
│       │
│       └── api-keys/                  # Phase 2
│           └── page.tsx               # API key management
│
├── components/
│   ├── layout/
│   │   ├── ConsoleSidebar.tsx         # Fixed sidebar with nav links + active states
│   │   └── ConsoleTopbar.tsx          # Account avatar, sign out, env badge
│   ├── tenants/
│   │   ├── TenantTable.tsx
│   │   ├── TenantDetailCard.tsx
│   │   ├── ImpersonateButton.tsx
│   │   └── ProvisioningWizard.tsx     # 6-step stepper, draft-safe, each step is own component
│   ├── feature-flags/
│   │   ├── FlagTable.tsx
│   │   └── TenantOverrideMatrix.tsx
│   ├── agents/
│   │   ├── VersionCatalog.tsx
│   │   ├── RingAssignmentBoard.tsx
│   │   └── ForceUpdateDialog.tsx
│   └── shared/
│       ├── StatusBadge.tsx
│       ├── AuditLogTable.tsx
│       └── ConfirmActionDialog.tsx
│
├── lib/
│   ├── api.ts                         # Typed API client for /admin/v1/*
│   ├── auth.ts                        # Google OAuth + platform JWT handling
│   └── types.ts                       # Shared TypeScript types
│
└── middleware.ts                      # Redirect unauthenticated to /login
```

---

## 7. User Flow: Key Paths

### 7.1 Developer Login
`/login` → Google OAuth → backend validates Google token + checks `dev_platform_accounts.is_active` → issues platform-admin JWT (30 min expiry) → redirect to `/`

### 7.2 Suspend a Tenant
Tenants list → click tenant → Tenant Detail → "Suspend" button → ConfirmActionDialog → `PATCH /admin/v1/tenants/{id}/status {status: "suspended"}` → toast confirmation → tenant row updates to red badge

### 7.3 Toggle Feature Flag for One Tenant
Tenants → [tenant] → Flags tab → find flag in table → toggle switch → optimistic update → `PATCH /admin/v1/tenants/{id}/feature-flags/{flag}` → persists to `feature_access_grants`

### 7.4 Publish Agent Version + Force-Update Ring 0
Agents → Versions → "Publish Version" → form (version, notes, download URL) → `POST /admin/v1/agent-versions` → version appears in catalog → "Force Update Ring 0" → ConfirmActionDialog → `POST /admin/v1/agent-versions/{id}/force-update {ring: 0}` → backend publishes `UPDATE_AGENT` commands to all agents in Ring 0 via AgentGateway

### 7.5 Impersonate Tenant Admin (Support)
Tenants → [tenant] → "Impersonate as Super Admin" → ConfirmActionDialog → `POST /admin/v1/tenants/{id}/impersonate` → receive short-lived tenant-scoped JWT (15 min, `impersonation: true` claim, not renewable) → opens main OneVo app in new tab with that JWT → audit log records the action

### 7.6 Manual Customer Provisioning (White-Glove Setup)
*Used when: enterprise deal, customer needs help, internal test tenant. Not required for every customer.*

Tenants → "Provision New Customer" → 6-step wizard:

1. **Account setup** — fill company name, slug, country, industry, timezone → `POST /admin/v1/tenants` → tenant created with `status: 'provisioning'` → wizard saves draft, can be closed and resumed
2. **Plan assignment** — pick subscription plan from dropdown → `PATCH /admin/v1/tenants/{id}/subscription` → marks whether Stripe billing is active or manually managed
3. **Module selection** — checklist of all available modules with phase labels → `PUT /admin/v1/tenants/{id}/modules` → writes `module_registry` for this tenant
4. **Initial config** — key settings form: monitoring transparency mode, leave policy defaults, working hours → `PATCH /admin/v1/tenants/{id}/settings`
5. **Invite admin** — enter customer's super-admin email + name → `POST /admin/v1/tenants/{id}/invite-admin` → creates `users` record, sends set-password email to customer
6. **Confirm** — summary screen showing all choices → "Activate Tenant" → `PATCH /admin/v1/tenants/{id}/provision/confirm` → `status` flips to `active` → tenant is now live and customer can log in

**Draft behaviour:** After step 1, the tenant exists in `status: 'provisioning'`. It's invisible to the main app. The wizard can be resumed from Tenants list (provisioning tenants shown with a yellow "In Progress" badge). Any step can be edited before confirming.

---

## 8. Security Model

| Concern | Approach |
|:---|:---|
| Authentication | Google OAuth only — no passwords |
| Authorization | Platform-admin JWT, separate issuer, rejected by all tenant endpoints |
| Role levels | `super_admin` (all), `admin` (no impersonate, no account mgmt), `viewer` (read-only) |
| Impersonation | Separate short-lived JWT, `impersonation: true` claim, 15 min TTL, non-renewable, always audit-logged |
| Network | IP allowlist or VPN required (configure at infrastructure layer) |
| Tenant API isolation | Admin JWT can never be used at tenant endpoints — validated at issuer claim |

---

## 9. Knowledge Base: Files to Create

```
developer-platform/
├── overview.md                        ← Purpose, users, connection model, what it is/isn't
├── system-design.md                   ← Full architecture diagram + admin API layer spec
├── auth.md                            ← Google OAuth, platform JWT, impersonation model, role levels
├── modules/
│   ├── tenant-console/overview.md
│   ├── feature-flag-manager/overview.md
│   ├── agent-version-manager/overview.md
│   ├── audit-console/overview.md
│   ├── system-config/overview.md
│   └── api-key-manager/overview.md   ← Phase 2
├── frontend/
│   ├── overview.md                    ← Stack, domain, design language, auth flow
│   └── app-structure.md              ← Full Next.js structure (as in Section 6 above)
├── backend/
│   ├── admin-api-layer.md            ← How /admin/v1/* is structured, JWT policy, DI wiring
│   └── api-contracts.md             ← All endpoints (as in Section 5 above)
├── database/
│   └── schema.md                    ← New tables (as in Section 4 above)
└── userflow/
    ├── overview.md                   ← Navigation map + access levels
    ├── tenant-management.md
    ├── provisioning-flow.md          ← Step-by-step manual provisioning wizard (7.6)
    ├── feature-flags.md
    └── agent-versions.md
```

**Total new files: 16**

---

## 10. Knowledge Base: Files to Correct/Update

| File | What to Change |
|:---|:---|
| `docs/vault-structure-guide.md` | Add `developer-platform/` as a new top-level vault section |
| `docs/superpowers/plans/2026-04-21-unified-platform-architecture.md` | Update Section 10 to say: "The `/platform-admin` concept has been promoted to a separate standalone app — see `developer-platform/overview.md`" |
| `database/schema-catalog.md` | Add developer platform tables (5 Phase 1 + 1 Phase 2). Update total: 170 → 175 |
| `backend/module-catalog.md` | Add `ONEVO.Admin.Api/` namespace entry + note the separate admin API layer |
| `frontend/architecture/app-structure.md` | Add note: "A second frontend app (dev-console) exists for platform administration — see `developer-platform/frontend/app-structure.md`" |
| `AI_CONTEXT/` read-me-first files | Add reference to developer platform so AI agents know a second frontend app exists |

**Total files to correct: 6**

---

## 11. Build Sequence

### Step 1 — Knowledge Base (this sprint)
Write all 16 new files listed in Section 9. Update 6 existing files listed in Section 10.

### Step 2 — Backend Admin API Layer
- Add `ONEVO.Admin.Api/` to the .NET solution
- Configure separate JWT issuer for `platform_admin` tokens
- Implement controllers for tenant console + feature flag manager first (highest value)
- Add new DB tables via EF migration

### Step 3 — Dev Console Frontend
- Bootstrap separate Next.js app
- Implement Google OAuth auth flow
- Build Tenant list + detail + suspend/impersonate (most critical path)
- Build Feature flag manager
- Build Agent version manager

### Step 4 — Remaining Modules
- Audit console, System Config
- Phase 2: Platform API keys

---

## 12. Out of Scope (for Now)

- **Customer-facing developer portal** (API keys for customers, webhook registration UI) — this is a separate future initiative
- **System health dashboard** — use Grafana as per existing tech stack decision
- **Log viewer** — use existing logging infrastructure (Seq/ELK)
- **CI/CD deployment controls** — handled by infrastructure pipeline, not this app
