# Sidebar Navigation Map

Canonical reference for ONEVO customer app navigation. Navigation components, permission gates, labels, and routes must reference this document. Do not hardcode role names.

## Application Model

ONEVO has one customer-facing application plus the internal Developer Platform:

- Customer App
- Developer Platform

## Customer App Navigation

Purpose:

```text
Run employee self-service, manager work, HR operations, monitoring, work management, and tenant settings in one shell.
```

Primary sections:

| Section | Default Route | Visible When | Notes |
|---|---|---|---|
| Home | `/` | Any authenticated user | Personal and operational overview |
| People | `/people/employees` | `employees:read` | Employees, onboarding, offboarding, checklist templates, employee detail lifecycle actions |
| Time Off | `/time-off` | `time_off:create` OR `time_off:read` | Time off self-service, balances, requests, approvals, policy reminders; management policy/type/entitlement setup when permitted |
| Time & Attendance | `/time-attendance/attendance` | `attendance:read-own` OR `attendance:read` | Operational attendance, schedules, clock-in policy, overtime rules, and row-level corrections |
| Work | `/work` | `projects:read` OR `tasks:read` | Phase 1 projects, work items, documents, project members, project settings, worklogs |
| Calendar | `/calendar` | `calendar:read` | Visual calendar for events, holidays, schedules, Time Off, meetings, invitations, reminders, and conflicts |
| Inbox | `/inbox` | Any authenticated user | Approvals, requests, notifications, invitations, assignments, mentions, action items |
| Monitoring | `/monitoring` | `monitoring:view` | Monitoring review, live status, alerts, discrepancies |
| Settings | `/settings/general` | `settings:read` | General, branding, users, roles & permissions, notifications, billing, devices, audit log |

Do not add a separate customer-facing `Admin` top-level module. Tenant/system administration belongs under `Settings`.

## Tenant / Legal Entity Context

See [[frontend/architecture/topbar|Topbar Architecture]] for tenant/legal entity context behavior.

Rules:

- Single-company tenants may hide legal entity context and default to the only legal entity.
- Multi-company tenants show legal entity context only where relevant and permission-scoped.
- Company creation is started from the topbar tenant/company dropdown, not from the Org sub-sidebar.
- Company context is switched from the topbar tenant/company dropdown.
- Company-scoped General settings are edited from Settings > General after selecting a Company. Do not imply a separate entity-settings page.
- Company switching must never bypass backend authorization.

## Permission Rules

- Navigation visibility is permission-key driven.
- Disabled modules must not appear.
- Backend entitlement checks remain authoritative.
- Frontend route guards must mirror backend permission and entitlement checks.
