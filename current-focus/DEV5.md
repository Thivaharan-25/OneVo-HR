# DEV5: Frontend App Foundation + Developer Platform Console

**Track:** Frontend
**Primary ownership:** main Vite app foundation, auth UI, shared frontend architecture, standalone Developer Platform console
**Current Unfinished Task:** Task 1 - Vite app foundation
**Blocked By:** none for scaffold; DEV1 auth contracts for live auth

---

## ADE Instructions

When Dev 5 asks to continue, start with the first unchecked item in **Current Unfinished Task**. If backend APIs are not ready, use MSW mocks matching the documented contract.

---

## Task 1: Vite App Foundation

**Goal:** create the main customer-facing frontend foundation all app screens use.

### Acceptance Criteria

- [ ] Vite + React + TypeScript app runs locally.
- [ ] React Router route tree exists for auth, dashboard, HR, workforce, admin, and error pages.
- [ ] Provider stack includes query client, auth state, theme, toast, and permission context.
- [ ] App shell includes sidebar, topbar, command palette placeholder, and responsive content area.
- [ ] Shared layout supports loading, empty, error, and forbidden states.
- [ ] Baseline tests render app shell and protected route behavior.

### References

- [[frontend/architecture/app-structure|Frontend App Structure]] (frontend/architecture/app-structure.md)
- [[frontend/architecture/routing|Routing]] (frontend/architecture/routing.md)
- [[frontend/design-system/components/shell-layout|Shell Layout]] (frontend/design-system/components/shell-layout.md)
- [[frontend/design-system/README|Design System]] (frontend/design-system/README.md)

### Verification

```bash
npm run lint
npm run test
npm run build
```

---

## Task 2: Main App API Client + State Layer

**Goal:** implement reusable API and state patterns for all main app frontend members.

**Requires:** DEV5 Task 1 complete

### Acceptance Criteria

- [ ] API client attaches access token, tenant header, and correlation ID.
- [ ] API client maps validation, auth, forbidden, not found, rate limit, and server errors.
- [ ] TanStack Query defaults are configured.
- [ ] Cursor pagination helper exists.
- [ ] Zustand stores exist for auth, shell, theme, and active tenant/workspace.
- [ ] MSW is configured for local contract mocks.
- [ ] Tests cover API error mapping and auth header behavior.

### References

- [[frontend/data-layer/api-integration|API Integration]] (frontend/data-layer/api-integration.md)
- [[frontend/data-layer/state-management|State Management]] (frontend/data-layer/state-management.md)
- [[frontend/data-layer/caching-strategy|Caching Strategy]] (frontend/data-layer/caching-strategy.md)

### Verification

```bash
npm run test -- api
npm run build
```

---

> **Parallel group** — Tasks 3 and 4 both require Tasks 1 and 2 and are independent of each other. Run them simultaneously.

## Task 3: Main App Auth Screens

**Goal:** provide the customer-facing user login and session UI.

**Requires:** DEV5 Tasks 1-2 complete - Contract: `current-focus/contracts/auth-session.md`

### Acceptance Criteria

- [ ] Login screen exists.
- [ ] MFA verification screen exists.
- [ ] Password reset request and reset screens exist.
- [ ] Forced password change screen exists.
- [ ] Protected routes redirect unauthenticated users.
- [ ] Forbidden page displays when user lacks permission.
- [ ] Tests cover login success, login error, forced password change, and route guard.

### References

- [[Userflow/Auth-Access/login-flow|Login Flow]] (Userflow/Auth-Access/login-flow.md)
- [[Userflow/Auth-Access/mfa-setup|MFA Setup]] (Userflow/Auth-Access/mfa-setup.md)
- [[Userflow/Auth-Access/password-reset|Password Reset]] (Userflow/Auth-Access/password-reset.md)
- [[frontend/cross-cutting/authentication|Frontend Authentication]] (frontend/cross-cutting/authentication.md)

### Verification

```bash
npm run test -- auth
npm run build
```

---

## Task 4: Main App Shared Components

**Goal:** provide stable components used by Dev 6 and Dev 7 feature screens.

**Requires:** DEV5 Tasks 1-2 complete

### Acceptance Criteria

- [ ] Data table wrapper supports loading, empty, sorting, filtering, and cursor paging.
- [ ] Form field primitives work with React Hook Form and Zod.
- [ ] Status badge supports success, warning, danger, neutral, pending, and offline states.
- [ ] Permission gate component hides or disables UI based on permissions.
- [ ] Confirm dialog and destructive action patterns exist.
- [ ] Tests cover table, permission gate, and form validation behavior.

### References

- [[frontend/design-system/components/component-catalog|Component Catalog]] (frontend/design-system/components/component-catalog.md)
- [[frontend/design-system/patterns/table-patterns|Table Patterns]] (frontend/design-system/patterns/table-patterns.md)
- [[frontend/design-system/patterns/form-patterns|Form Patterns]] (frontend/design-system/patterns/form-patterns.md)
- [[frontend/cross-cutting/authorization|Authorization]] (frontend/cross-cutting/authorization.md)

### Verification

```bash
npm run test -- components
npm run build
```

---

## Task 5: Developer Platform Console Foundation

**Goal:** build the standalone internal Developer Platform frontend foundation at `console.onevo.io`.

**Requires:** DEV5 Task 1 complete - Contract: `current-focus/contracts/admin-api.md`

### Frontend App Location

- App type: separate Next.js 15 App Router application
- Domain: `console.onevo.io`
- API prefix: `/admin/v1/*`
- Auth: Google OAuth exchanged for platform-admin JWT
- Visual language: dark internal admin console, separate from customer-facing OneVo app

### Acceptance Criteria

- [ ] Standalone Next.js console app exists separately from the main Vite app.
- [ ] Directory structure follows [[developer-platform/frontend/app-structure|Developer Platform App Structure]] (developer-platform/frontend/app-structure.md).
- [ ] Login page starts Google OAuth flow.
- [ ] OAuth callback exchanges Google identity for platform-admin session through `/admin/v1/auth/google-callback`.
- [ ] Auth middleware protects all console routes except login/callback.
- [ ] Platform-admin session uses httpOnly cookie/session handling and never reuses tenant app auth state.
- [ ] Admin API client targets `/admin/v1/*`, attaches platform-admin JWT, and rejects tenant-token shaped sessions.
- [ ] Console layout has fixed sidebar, topbar, environment badge, account menu, role-aware nav, and tenant search.
- [ ] Dashboard shows tenant count, active flags, agent ring health, provisioning drafts, and recent audit entries.
- [ ] Shared components exist for status badge, audit table, confirm action dialog, destructive confirmation, filter bar, empty state, and loading skeleton.
- [ ] Tests cover login redirect, protected route, role-aware nav, API client auth header, and dashboard loading/error states.

### References

- [[developer-platform/overview|Developer Platform Overview]] (developer-platform/overview.md)
- [[developer-platform/frontend/overview|Developer Platform Frontend Overview]] (developer-platform/frontend/overview.md)
- [[developer-platform/frontend/app-structure|Developer Platform App Structure]] (developer-platform/frontend/app-structure.md)
- [[developer-platform/auth|Developer Platform Auth]] (developer-platform/auth.md)
- [[developer-platform/system-design|Developer Platform System Design]] (developer-platform/system-design.md)
- [[developer-platform/backend/api-contracts|Admin API Contracts]] (developer-platform/backend/api-contracts.md)
- [[developer-platform/userflow/overview|Developer Platform Userflows]] (developer-platform/userflow/overview.md)

### Verification

```bash
npm run lint
npm run test
npm run build
```

---

> **Parallel group** — Tasks 6 and 7 both require Task 5 and are independent of each other. Run them simultaneously.

## Task 6: Developer Platform Tenant Console UI

**Goal:** build tenant lifecycle and provisioning workflows for internal operators.

**Requires:** DEV5 Task 5 complete  
**Live integration:** DEV1 Tasks 7-8 (use MSW until ready)

### Acceptance Criteria

- [ ] `/tenants` renders tenant list with company, slug, plan, status, employee count, created date, agent count, and last login.
- [ ] Tenant list supports search, status filter, plan filter, and provisioning draft visibility.
- [ ] `/tenants/[tenantId]` renders Overview, Flags, Settings, Users, and Audit tabs.
- [ ] Suspend flow requires `super_admin`, confirm dialog, slug confirmation, API call, toast, and status update.
- [ ] Unsuspend flow requires `super_admin`, confirm dialog, API call, toast, and status update.
- [ ] Subscription override flow requires `super_admin`, new plan, billing start date, reason, and visible manual override state.
- [ ] Impersonation flow requires `super_admin`, warning confirmation, opens main app in a new tab, and surfaces token expiry.
- [ ] `/tenants/new` implements six-step provisioning wizard: account setup, plan assignment, module selection, initial configuration, admin invite, review/confirm.
- [ ] Provisioning wizard is draft-safe after Step 1 and can resume from a `provisioning` tenant.
- [ ] Step 3 module selection writes the same module grants consumed by main app and IDE extension.
- [ ] Step 6 activation flips tenant from provisioning to active and updates the tenant list badge.
- [ ] Tests cover tenant list filters, tenant detail tabs, suspend role gate, subscription override validation, impersonation role gate, provisioning draft resume, and activation.

### References

- [[developer-platform/modules/tenant-console/overview|Tenant Console]] (developer-platform/modules/tenant-console/overview.md)
- [[developer-platform/userflow/tenant-management|Tenant Management Flows]] (developer-platform/userflow/tenant-management.md)
- [[developer-platform/userflow/provisioning-flow|Manual Customer Provisioning Flow]] (developer-platform/userflow/provisioning-flow.md)
- [[developer-platform/backend/api-contracts|Admin API Contracts]] (developer-platform/backend/api-contracts.md)

### Verification

```bash
npm run test -- tenants
npm run test -- provisioning
npm run build
```

---

## Task 7: Developer Platform Operations UI

**Goal:** build feature flags, agent versions/rings, audit, system config, and app catalog screens.

**Requires:** DEV5 Task 5 complete  
**Live integration:** DEV1 Task 9, DEV4 Task 8 (use MSW until ready)

### Acceptance Criteria

- [ ] `/feature-flags` renders flag list with key, description, global default, rollout percentage, and override count.
- [ ] `/feature-flags/[flagId]` renders flag detail with per-tenant override table.
- [ ] Global flag toggle uses confirm dialog and optimistic update with rollback on error.
- [ ] Tenant flag override UI supports set, clear, and inherit-default states.
- [ ] `/agents/versions` renders version catalog with version, status, release notes, minimum OS, publisher, published date, and recalled date.
- [ ] Publish Version form validates semver uniqueness, channel, minimum OS, release notes, and HTTPS download URL.
- [ ] Version detail supports channel change, recall, force-update ring, and rollback workflows with correct role gates.
- [ ] `/agents/rings` renders Ring 0, Ring 1, and Ring 2 with tenant assignments and reassignment workflow.
- [ ] `/audit` renders cross-tenant audit log filters for tenant, user, action, resource, and date range, plus CSV export.
- [ ] `/config` renders global defaults, tenant override search, monitoring toggle defaults, and integration health read-only section.
- [ ] App Catalog screen renders global catalog, public/private toggle, metadata editor, uncatalogued apps, bulk approve, dismiss, and aggregate usage.
- [ ] Tests cover flag toggle, tenant override, version publish, force-update role gate, ring reassignment, audit filters/export, config update, catalog toggle, and uncatalogued bulk approve.

### References

- [[developer-platform/modules/feature-flag-manager/overview|Feature Flag Manager]] (developer-platform/modules/feature-flag-manager/overview.md)
- [[developer-platform/userflow/feature-flags|Feature Flag Flows]] (developer-platform/userflow/feature-flags.md)
- [[developer-platform/modules/agent-version-manager/overview|Agent Version Manager]] (developer-platform/modules/agent-version-manager/overview.md)
- [[developer-platform/userflow/agent-versions|Agent Version and Ring Management Flows]] (developer-platform/userflow/agent-versions.md)
- [[developer-platform/modules/audit-console/overview|Audit Console]] (developer-platform/modules/audit-console/overview.md)
- [[developer-platform/modules/system-config/overview|System Config]] (developer-platform/modules/system-config/overview.md)
- [[developer-platform/modules/app-catalog-manager/overview|App Catalog Manager]] (developer-platform/modules/app-catalog-manager/overview.md)

### Verification

```bash
npm run test -- feature-flags
npm run test -- agent-versions
npm run test -- audit
npm run test -- config
npm run test -- app-catalog
npm run build
```

---

## Open Backend Contracts

- [x] Auth response shape -> `current-focus/contracts/auth-session.md`
- [x] Permission payload shape -> `current-focus/contracts/auth-session.md`
- [x] Platform-admin JWT exchange response -> `current-focus/contracts/admin-api.md`
- [x] `/admin/v1/*` DTOs from DEV1 and DEV4 -> `current-focus/contracts/admin-api.md`


