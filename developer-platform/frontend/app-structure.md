# App Structure

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
- **`tenants/`** — Tenant-related UI components (table, detail cards, provisioning wizard)
- **`feature-flags/`** — Feature flag management UI
- **`agents/`** — Agent version and ring assignment components
- **`shared/`** — Generic, reusable UI components (status badges, tables, dialogs)

## Phase 2 Note

The `api-keys/` section under `(console)/` is marked for Phase 2 implementation. The directory structure is defined, but the feature is not yet built. This will enable platform admins to manage API keys for programmatic access to the `/admin/v1/*` API.
