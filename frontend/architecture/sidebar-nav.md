# Sidebar Navigation Map

Canonical reference for ONEVO customer app navigation. Navigation components, permission gates, labels, and routes must reference this document. Do not hardcode role names.

## Application Split

ONEVO has two customer-facing applications plus the internal Developer Platform:

- Setup / Control Application
- Operations / Lifecycle Application
- Developer Platform

## Setup / Control Application Navigation

Purpose:

```text
Configure structure, access, policies, workflows, positions, and initial onboarding.
```

Primary sections:

| Section | Default Route | Visible When | Notes |
|---|---|---|---|
| Setup Home | `/` | `settings:read` OR `org:read` | Setup progress, missing configuration, warnings |
| Tenant Setup | `/tenant` | `settings:read` | Tenant profile, branding, defaults |
| Legal Entities | `/org/legal-entities` | `org:manage` | Single-company / multi-company setup |
| Departments | `/org/departments` | `org:manage` | Legal-entity-scoped departments |
| Teams | `/org/teams` | `org:manage` | Team setup |
| Positions | `/org/positions` | `org:manage` | Legal-entity-scoped positions, reporting structure, capacity |
| Roles & Permissions | `/access/roles` | `roles:manage` | Tenant roles, permission templates, position access templates |
| Policies | `/policies` | `settings:read` | Leave, attendance, overtime, monitoring/privacy policies |
| Workflows | `/workflows` | `workflows:manage` | Approval and escalation rules |
| Employee Import | `/people/import` | `employees:write` | CSV/Excel import and initial employee onboarding; PeopleHR is Phase 2 |
| Add-ons / Licenses | `/billing/requests` | `settings:billing` | Request add-ons, employee/license increases, device/agent limit increases |

## Operations / Lifecycle Application Navigation

Purpose:

```text
Run daily employee, manager, HR, workforce, and operational work.
```

Primary sections:

| Section | Default Route | Visible When | Notes |
|---|---|---|---|
| Home | `/` | Any authenticated user | Personal and operational overview |
| Inbox | `/inbox` | Any authenticated user | Approvals, tasks, mentions, exception alerts |
| My Profile | `/profile` | Any authenticated user | Own profile and self-service details |
| Leave | `/leave` | `leave:create` OR `leave:read` | Leave requests and approvals |
| Attendance | `/attendance` | `attendance:read-own` OR `attendance:read` | Attendance, overtime, corrections |
| People | `/people/employees` | `employees:read` | Employee profiles, transfer, promotion, offboarding |
| Workforce | `/workforce` | `workforce:view` | Monitoring review, exceptions, discrepancies |
| WorkSync | `/work` | `projects:read` OR `tasks:read` | Projects, tasks, time, chat when enabled |
| Reports | `/reports` | `reports:read` | Operational reports and exports |
| Compliance | `/compliance` | `settings:system` | Compliance exports and audit review |

## Tenant / Legal Entity Context

See [[frontend/architecture/topbar|Topbar Architecture]] for tenant/legal entity context behavior.

Rules:

- Single-company tenants may hide legal entity context and default to the only legal entity.
- Multi-company tenants show legal entity context only where relevant and permission-scoped.
- Legal entity switching must never bypass backend authorization.

## Permission Rules

- Navigation visibility is permission-key driven.
- Disabled modules must not appear.
- Backend entitlement checks remain authoritative.
- Frontend route guards must mirror backend permission and entitlement checks.
