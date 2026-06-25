# Frontend App Structure

> **Stack:** Angular 21 standalone components. No NgModules, no SSR, no file-based routing. All routes are defined in `app.routes.ts`. Feature components live in `features/`. Loading states use Angular's `@defer` or `resource.isLoading()` signals.

> **Two applications total:** `customer-app` for tenant/company setup, People, Time Off, Time & Attendance, Work, Monitoring, Calendar, Inbox, and Settings operations, and `dev-console` for ONEVO internal platform operators. Customer app consumes `/api/v1/*`. Developer Platform consumes `/admin/v1/*`. Both apps share `@onevo/shared`.

---

## Application Boundaries

### Customer Application

Purpose:

```text
Run the full tenant experience in one shell: setup, People, Time Off, Time & Attendance, Work, Monitoring, Calendar, Inbox, Settings, and daily operations.
```

Contains:

- Tenant setup
- Single-company / multi-company mode
- Legal entity setup through the topbar company/legal-entity dropdown
- Department setup
- Position setup
- Reporting structure setup
- Grant system access from position setup
- Role and permission setup
- System settings assignment
- Time Off policy setup
- Attendance policy setup
- Overtime policy setup
- Monitoring/privacy policy setup
- Lightweight Phase 1 approval settings
- Employee import
- Initial employee onboarding
- Add-on / license increase request page

Rule:

```text
If it is tenant-customer work, it belongs in customer-app. Use feature-area routes and permissions to separate People, Time Off, Time & Attendance, Work, Monitoring, Calendar, Inbox, and Settings concerns inside the shell.
```

- Employee self-service
- Employee profile
- Time Off request
- Time Off approval
- Attendance
- Overtime
- Employee onboarding task completion
- Employee transfer
- Employee promotion
- Employee offboarding
- Monitoring review
- Exception/discrepancy review
- Work projects, work items, documents, members, settings, and worklogs when enabled. Planner, Goals/OKR, advanced roadmap, and chat are Phase 2.
- Operational reports
- Compliance exports and audit review

### Developer Platform

Purpose:

```text
ONEVO internal platform control only.
```

Contains:

- Tenant creation
- Tenant activation/suspension/cancellation
- Package/module entitlement activation
- Add-on approval/activation
- Employee/license count increase approval
- Device/agent limit increase approval
- Trial to active conversion
- Pricing override
- Billing/contract setup
- Platform feature rollout
- Agent version rollout

Rule:

```text
Customers request commercial changes in customer-app.
ONEVO approves and activates them in Developer Platform.
```

---

## Monorepo Workspace Structure

```text
onevo-frontend/
+-- angular.json
+-- tsconfig.json
+-- package.json
+-- projects/
|   +-- customer-app/
|   +-- dev-console/
|   +-- shared/
+-- e2e/
```

## Shared Library

`projects/shared` is imported by both applications as `@onevo/shared`.

Shared responsibilities:

- Authentication/session state
- Permission guards
- API base services and interceptors
- Tenant/legal entity context helpers
- Shared UI shell primitives
- Notification/inbox client
- Formatting, validation, and common models

## Routing Rule

Each app owns its own route map:

- `customer-app`: setup, configuration, legal entities, policies, roles/permissions, positions, imports, add-on requests, employee self-service, people lifecycle, Time Off, Time & Attendance, Work, Monitoring, Calendar, Inbox, Settings, reports.
- `dev-console`: ONEVO internal tenant provisioning, entitlement, billing, rollout, and platform support.

Do not split tenant-customer workflows into separate apps. Separate them by route group, navigation, permission, and entitlement inside `customer-app`.

## Permission Rule

Never hardcode role names in frontend navigation or routes. Visibility and access must be permission-key driven and entitlement-aware.

## Multi Company Rule

Customer apps must support:

```text
Tenant
+-- Legal Entity 1
+-- Legal Entity 2
+-- Legal Entity 3
```

Legal entity context is used for setup, department/position resolution, employee import, onboarding, transfer, reports, and scoped operational views.

Single-company tenants may hide the legal entity selector and default all legal-entity-scoped forms to the tenant's only legal entity.
