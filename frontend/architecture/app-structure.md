# Frontend App Structure

> **Stack:** Angular 21 standalone components. No NgModules, no SSR, no file-based routing. All routes are defined in `app.routes.ts`. Feature components live in `features/`. Loading states use Angular's `@defer` or `resource.isLoading()` signals.

> **Three applications total:** `setup-control-app` for tenant/company setup and configuration, `operations-lifecycle-app` for daily employee/manager/HR/workforce operations, and `dev-console` for ONEVO internal platform operators. Customer apps consume `/api/v1/*`. Developer Platform consumes `/admin/v1/*`. All apps share `@onevo/shared`.

---

## Application Boundaries

### Setup / Control Application

Purpose:

```text
Configure the tenant/company structure before daily operations start, and maintain that structure later.
```

Contains:

- Tenant setup
- Single-company / multi-company mode
- Legal entity setup
- Department setup
- Team setup
- Position setup
- Position setup
- Reporting structure setup
- Position access templates
- Role and permission setup
- System admin assignment
- Leave policy setup
- Attendance policy setup
- Overtime policy setup
- Monitoring/privacy policy setup
- Approval workflow setup
- Employee import
- Initial employee onboarding
- Add-on / license increase request page

Rule:

```text
If it configures structure, access, policies, workflows, positions, or initial onboarding, it belongs here.
```

### Operations / Lifecycle Application

Purpose:

```text
Run the configured system day to day.
```

Contains:

- Employee self-service
- Employee profile
- Leave request
- Leave approval
- Attendance
- Overtime
- Employee onboarding task completion
- Employee transfer
- Employee promotion
- Employee offboarding
- Manager/team views
- Workforce monitoring review
- Exception/discrepancy review
- WorkSync projects/tasks/time/chat, if enabled
- Operational reports
- Compliance exports and audit review

Rule:

```text
If it is daily employee, manager, HR, workforce, or operational work, it belongs here.
```

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
Customers request commercial changes in Setup / Control Application.
ONEVO approves and activates them in Developer Platform.
```

---

## Monorepo Workspace Structure

```text
onevo-frontend/
├── angular.json
├── tsconfig.json
├── package.json
├── projects/
│   ├── setup-control-app/
│   ├── operations-lifecycle-app/
│   ├── dev-console/
│   └── shared/
└── e2e/
```

## Shared Library

`projects/shared` is imported by all three applications as `@onevo/shared`.

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

- `setup-control-app`: setup, configuration, legal entities, policies, roles/permissions, positions, imports, add-on requests.
- `operations-lifecycle-app`: employee self-service, people lifecycle, leave, attendance, workforce, WorkSync, reports.
- `dev-console`: ONEVO internal tenant provisioning, entitlement, billing, rollout, and platform support.

Do not duplicate the same workflow across apps. If a workflow changes configuration, it belongs in Setup / Control Application. If it runs daily employee/manager/HR operations, it belongs in Operations / Lifecycle Application.

## Permission Rule

Never hardcode role names in frontend navigation or routes. Visibility and access must be permission-key driven and entitlement-aware.

## Multi Company Rule

Customer apps must support:

```text
Tenant
├── Legal Entity 1
├── Legal Entity 2
└── Legal Entity 3
```

Legal entity context is used for setup, department/position resolution, employee import, onboarding, transfer, reports, and scoped operational views.

Single-company tenants may hide the legal entity selector and default all legal-entity-scoped forms to the tenant's only legal entity.
