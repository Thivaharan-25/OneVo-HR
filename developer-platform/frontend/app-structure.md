# App Structure

## Canonical Navigation

The Developer Platform frontend uses a sidebar icon rail with a secondary panel for grouped modules. This navigation is separate from the tenant-facing ONEVO app navigation in `frontend/architecture/sidebar-nav.md`.

| Rail Area | Default Route | Has Panel | Panel Items |
|---|---|---:|---|
| Dashboard | `/` | No | None |
| Platform Management | `/platform/tenants` | Yes | Tenants, Subscriptions, Platform Users & Roles, Global Policies, Feature Management / Module Catalog, Role Templates, Feature Flags |
| System Operations | `/operations/platform-health` | Yes | Platform Health, Services Monitor, Device Management, Infrastructure, Background Jobs, Agent Versions |
| Security & Compliance | `/security/security-center` | Yes | Security Center, Audit Logs, Compliance Center, Data Retention |
| Analytics & Reports | `/analytics/platform` | Yes | Platform Analytics, Reports |
| Settings | `/settings/system` | Yes | System Settings, App Catalog, API Keys *(Phase 2)* |

Route visibility is controlled by platform permissions from Platform Access. Do not use tenant roles or ONEVO product module entitlements to show Developer Platform routes.

## Canonical Route Tree

```text
app/(console)/
|-- page.tsx
|-- platform/
|   |-- tenants/
|   |-- subscriptions/
|   |-- platform-users/
|   |-- platform-roles/
|   |-- global-policies/
|   |-- module-catalog/
|   |-- role-templates/
|   `-- feature-flags/
|-- operations/
|   |-- platform-health/
|   |-- services/
|   |-- devices/
|   |-- infrastructure/
|   |-- background-jobs/
|   `-- agent-versions/
|-- security/
|   |-- security-center/
|   |-- audit-logs/
|   |-- compliance/
|   `-- data-retention/
|-- analytics/
|   |-- platform/
|   `-- reports/
`-- settings/
    |-- system/
    |-- app-catalog/
    `-- api-keys/  # Phase 2
```

## Full Directory Tree

```
dev-console/
├── app/
│   ├── layout.tsx                     # Root layout with providers and dark ThemeProvider
│   ├── not-found.tsx
│   │
│   ├── (auth)/                        # Unauthenticated route group
│   │   └── login/
│   │       └── page.tsx               # Google OAuth login page (no password)
│   │
│   └── (console)/                     # Authenticated console route group
│       ├── layout.tsx                 # Console layout: sidebar + topbar
│       ├── page.tsx                   # Dashboard: tenant count, active flags, agent ring health
│       │
│       ├── tenants/
│       │   ├── page.tsx               # Tenant list: search, filter by plan/status
│       │   ├── new/
│       │   │   └── page.tsx           # Two-step tenant creation wizard, saveable draft
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
│       └── api-keys/                  # Phase 2 (not yet implemented)
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
│   │   └── ProvisioningWizard.tsx     # Two-step creation wizard plus Manage/Configure entry points
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
│   ├── api.ts                         # Typed API client for /admin/v1/* endpoints
│   ├── auth.ts                        # Google OAuth + platform JWT handling
│   └── types.ts                       # Shared TypeScript types
│
└── middleware.ts                      # Redirects unauthenticated users to /login
```

## Route Group Structure

### (auth) — Unauthenticated Routes
The `(auth)` route group contains all unauthenticated pages, primarily the login page. This group is **not protected** by middleware and is accessible to all visitors.

### (console) — Authenticated Routes
The `(console)` route group contains all authenticated admin console pages. The `middleware.ts` enforces that only users with a valid platform-admin JWT can access routes in this group. Unauthenticated requests are redirected to `/login`.

## lib/ Directory

The `lib/` folder contains shared utilities and configuration:

- **`api.ts`** — Typed HTTP client for making requests to the backend `/admin/v1/*` endpoints. Handles request/response serialization and error handling.
- **`auth.ts`** — Manages Google OAuth token exchange and platform JWT lifecycle (storage, validation, refresh if needed).
- **`types.ts`** — Shared TypeScript interfaces and types used across the frontend (Tenant, Flag, Agent, AuditLog, etc.).

## components/ Directory

Components are organized by domain:

- **`layout/`** — Reusable layout components (Sidebar, Topbar)
- **`tenants/`** — Tenant-related UI components (table, detail cards, creation wizard, Manage/Configure flow)
- **`feature-flags/`** — Feature flag management UI
- **`agents/`** — Agent version and ring assignment components
- **`shared/`** — Generic, reusable UI components (status badges, tables, dialogs)

## Phase 2 Note

The `api-keys/` section under `(console)/` is marked for Phase 2 implementation. The directory structure is defined, but the feature is not yet built. This will enable platform admins to manage API keys for programmatic access to the `/admin/v1/*` API.
