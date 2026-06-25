# Phase 1 Feature Permission Map

## Purpose

This document connects Phase 1 `module_key`, `feature_key`, owner permissions, dependency permissions, and management-coverage behavior.

It is intended to support Module Catalog seeding and permission ownership design without confusing module ownership with cross-module data dependencies.

## Core Model

| Layer | Meaning |
|---|---|
| `module_key` | Product module registered in Module Catalog. |
| `feature_key` | Commercial feature inside a module. Plans/custom contracts select these keys. |
| `owner_permissions` | Permissions that control actions inside the feature's owning module. |
| `dependency_permissions` | Permissions required only because the feature reads or writes another module's data. These permissions are not owned by the feature's module. |
| `management_coverage_applies` | Whether employee-data access must be resolved through Org Structure management coverage. |
| `notes` | Clarifies non-permission-controlled features, runtime-flag behavior, or wording inconsistencies. |

## Management Coverage Values

Management coverage is only for permissions that operate on employee-owned or employee-scoped data. Tenant-wide permissions such as `settings:admin`, `billing:manage`, `org:manage`, and `integrations:manage` do not need management coverage.

| Coverage level | Meaning | Use when |
|---|---|---|
| `Position` | Active employees assigned to the covered position. | Position-specific owner coverage. |
| `Department` | Active employees assigned inside the covered department. | Department owner coverage. |
| `Company-wide` | Active employees inside the active Company/legal entity. | Company-level HR, payroll, compliance, or executive ownership. |

Employee self-service views do not require management coverage. They are handled by own-record permissions such as `employees:read-own` and `time_off:read-own`.

## Important Rules

1. A permission does not turn on a feature key.
2. A feature key does not grant user access by itself.
3. Effective access requires active module entitlement, included feature key, runtime flag if applicable, owner permission, dependency permission where required, and management coverage where employee data is involved.
4. Dependency permissions must not be treated as permission ownership by the feature's module.
5. Foundation features can exist as feature keys for consistency, but they are always included and are not separately sellable in Phase 1.

## Known Wording Inconsistencies

| Area | Issue | Required interpretation |
|---|---|---|
| Time & Attendance | The module is named Time & Attendance, but many permissions still use `attendance:*`. | Treat `attendance:*` as the attendance/presence record permission namespace inside Time & Attendance. |
| `monitoring:view` vs `attendance:read` | Both appear around presence screens. | `attendance:read` controls historical attendance/presence record access. `monitoring:view` controls monitoring intelligence/live status/dashboard access. |
| Exception Engine | Full exception rules, exception alerts, and escalation chains are Phase 2. | Do not seed `exceptions.*` feature keys or `exceptions:*` permissions in the Phase 1 Module Catalog. Phase 1 monitoring-owned alerts use `monitoring:*` permissions and Notifications. |
| Roles | Phase 1 role management uses `roles:manage`. Granular role permissions are reserved for possible delegated administration later. | Seed and enforce `roles:manage` for Phase 1 role creation, editing, assignment, deletion, and permission management. |
| Automation / Workflow | Full Workflow Engine and Automation Center are Phase 2. | Phase 1 uses module-owned lightweight approval/request records, management coverage routing, and Notifications. Do not seed `workflow_engine.*` features or `workflows:*` permissions in the Phase 1 Module Catalog. |

## Phase 1 Feature To Permission Map

### Foundation Modules

| module | module_key | feature_key | owner_permissions | dependency_permissions | management_coverage_applies | notes |
|---|---|---|---|---|---|---|
| Auth & Security | `auth` | `auth.optional_google_oauth` | None | None | No | Optional invited-manager OAuth setup/sign-in capability; not controlled by tenant role permission. Operational runtime flag candidate only. |
| Auth & Security | `auth` | `auth.mfa_enforcement` | `users:manage` for admin reset/enforcement actions | `settings:admin` if changing tenant-wide auth policy | No | End users enabling their own MFA do not need a grantable permission. |
| Configuration | `configuration` | `configuration.tenant_settings` | `settings:read`, `settings:admin` | None | No | Foundation tenant setting capability. |
| Roles & Permissions | `roles` | `roles.permission_management` | `roles:manage` | `users:read` when selecting users for assignment | No | Phase 1 uses `roles:manage` as the aggregate role-management permission. |
| Notifications | `notifications` | `notifications.email_delivery` | `notifications:manage`, `settings:notifications` | None | No | Delivery itself is system behavior; permissions control template/channel configuration. |
| Notifications | `notifications` | `notifications.in_app_delivery` | `notifications:manage`, `settings:notifications` | None | No | Reading notifications is derived or authenticated-user behavior, not a normal feature owner permission. |
| Org Structure | `org` | `org.structure_management` | `org:read`, `org:manage` | `employees:read` when selecting or showing employees in the structure | Yes, only for employee lookup/detail dependency | `org:*` owns the structure; `employees:*` remains owned by Core HR. |

### HR Core Package

| module | module_key | feature_key | owner_permissions | dependency_permissions | management_coverage_applies | notes |
|---|---|---|---|---|---|---|
| Core HR | `core_hr` | `core_hr.employee_profiles` | `employees:read-own`, `employees:read`, `employees:write`, `employees:delete` | None | Yes for `employees:read`, `employees:write`, `employees:delete` | Own profile read is auto-grant. |
| Core HR | `core_hr` | `core_hr.employee_lifecycle` | `employees:read`, `employees:write` | `org:read` when showing department/job context | Yes | Lifecycle changes remain Core HR ownership. |
| Core HR | `core_hr` | `core_hr.onboarding` | `employees:write` | `users:manage` for auth invitation, `roles:manage` for assigning access, `org:read` for placement | Yes | Cross-module permissions are dependencies, not Core HR-owned permissions. |
| Core HR | `core_hr` | `core_hr.offboarding` | `employees:write` | `users:manage` for account suspension, `documents:manage` for document handoff, `payroll:write` for final payroll data | Yes | Dependencies apply only when the offboarding flow performs those actions. |
| Core HR | `core_hr` | `core_hr.dependents_contacts` | `employees:read-own`, `employees:write` | None | Yes for admin writes | Own dependent/contact management is self-scoped. |
| Core HR | `core_hr` | `core_hr.qualifications` | `employees:read-own`, `employees:write` | `skills:read`, `skills:write`, `skills:validate` when qualification data is handled through Skills | Yes | Boundary with Skills must be decided per screen/API. |
| Core HR | `core_hr` | `core_hr.compensation` | `employees:write` | `payroll:read`, `payroll:write` for salary/payroll-sensitive data | Yes | Compensation profile is Core HR; payroll amounts and payroll processing remain Payroll dependency. |
| Time Off | `time_off` | `time_off.requests` | `time_off:read-own`, `time_off:read`, `time_off:create` | `calendar:read` when showing calendar conflicts | Yes for `time_off:read`, `time_off:create` on behalf of others | Own Time Off read is auto-grant. |
| Time Off | `time_off` | `time_off.approvals` | `time_off:approve` | `employees:read` when showing employee context | Yes | Approval ownership is resolved through management coverage. |
| Time Off | `time_off` | `time_off.balances` | `time_off:read-own`, `time_off:read`, `time_off:manage` | None | Yes for `time_off:read` and `time_off:manage` over employee balances | Own balance read is auto-grant. |
| Time Off | `time_off` | `time_off.accrual_rules` | `time_off:manage` | None | No | Runtime flag candidate. |
| Time Off | `time_off` | `time_off.types` | `time_off:read`, `time_off:manage` | None | No | Time Off type setup is tenant-wide configuration inside Time Off. |
| Time Off | `time_off` | `time_off.calendar_integration` | `time_off:read`, `time_off:manage` | `calendar:read`, `calendar:admin` for calendar sync/configuration | Yes for Time Off records | Calendar permission is dependency. |
| Calendar | `calendar` | `calendar.company_calendar` | `calendar:read`, `calendar:write` | None | No | `calendar:read` is an auto-grant in the permissions reference. |
| Calendar | `calendar` | `calendar.holidays` | `calendar:read`, `calendar:admin` | None | No | Holiday administration uses `calendar:admin`. |
| Time & Attendance | `time_attendance` | `time_attendance.work_schedules` | `attendance:read`, `attendance:write` | `calendar:read` only when displaying schedule overlays in Calendar | Yes for attendance schedule records | Work schedule management belongs to Time & Attendance. Calendar can display schedule overlays only. |
| Calendar | `calendar` | `calendar.time_off_visibility` | `calendar:read` | `time_off:read` for Time Off record visibility | Yes for Time Off dependency | Calendar can display Time Off only through Time Off access rules. |
| Calendar | `calendar` | `calendar.event_sync` | `calendar:admin` | `settings:integrations` for tenant-wide external integration setup | No | External integration setup is dependency. |

### Intelligence Package

| module                | module_key     | feature_key                              | owner_permissions                                                          | dependency_permissions                                                                        | management_coverage_applies                                                        | notes                                                                                  |
| --------------------- | -------------- | ---------------------------------------- | -------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| Activity Monitoring   | `monitoring`   | `monitoring.activity_tracking`           | `monitoring:read`, `monitoring:view`                                        | `employees:read` for employee identity/context                                                | Yes for employee context                                                           | Monitoring data access must obey employee scope where employee-specific.               |
| Activity Monitoring   | `monitoring`   | `monitoring.app_usage`                   | `monitoring:read`, `monitoring:view`                                        | `employees:read` for employee context                                                         | Yes                                                                                | App usage is monitoring data, not Core HR data.                                        |
| Activity Monitoring   | `monitoring`   | `monitoring.website_usage`               | `monitoring:read`, `monitoring:view`                                        | `employees:read` for employee context                                                         | Yes                                                                                | Runtime flag candidate.                                                                |
| Activity Monitoring   | `monitoring`   | `monitoring.idle_detection`              | `monitoring:read`, `monitoring:view`, `monitoring:configure` for thresholds | `employees:read` for employee context                                                         | Yes                                                                                | Configuration uses `monitoring:configure`.                                             |
| Activity Monitoring   | `monitoring`   | `monitoring.screenshot_on_demand`        | `monitoring:read`, `monitoring:view`                                        | `agent:command` to request capture                                                            | Yes                                                                                | Runtime flag candidate.                                                                |
| Activity Monitoring   | `monitoring`   | `monitoring.app_allowlist`               | `monitoring:view-settings`, `monitoring:configure`                         | None                                                                                          | No                                                                                 | Runtime flag candidate.                                                                |
| Activity Monitoring   | `monitoring`   | `monitoring.productivity_classification` | `monitoring:configure`                                                     | `analytics:view` when surfaced in analytics dashboards                                        | No for config; depends on analytics screen for dashboard                           | Runtime flag candidate.                                                                |
| Activity Monitoring   | `monitoring`   | `monitoring.raw_data_processing`         | `monitoring:read`, `monitoring:view`                                        | None                                                                                          | Yes when employee-specific raw data is exposed                                     | Internal processing has no user action unless exposed through UI/API.                  |
| Time & Attendance    | `monitoring`    | `monitoring.presence_sessions`            | `attendance:read`, `attendance:read-own`, `monitoring:view` for live status | `employees:read` for employee context                                                         | Yes for `attendance:read`; live status scope must follow monitoring dashboard rules | Historical presence uses `attendance:read`; live endpoint uses `monitoring:view`.       |
| Time & Attendance    | `monitoring`    | `monitoring.break_tracking`               | `attendance:read`, `attendance:write`, `attendance:write-own`              | None                                                                                          | Yes for `attendance:read` and admin writes                                         | Own break start/end uses auto-grant-style own write behavior.                          |
| Time & Attendance    | `monitoring`    | `monitoring.overtime`                     | `attendance:write`, `attendance:approve`                                   | `payroll:read` when viewing payroll impact                                                    | Yes                                                                                | Runtime flag candidate.                                                                |
| Time & Attendance    | `monitoring`    | `monitoring.attendance_corrections`       | `attendance:write`, `attendance:approve`, `attendance:write-own`           | None                                                                                          | Yes                                                                                | Runtime flag candidate.                                                                |
| Time & Attendance    | `monitoring`    | `monitoring.device_sessions`              | `monitoring:view`                                                           | `agent:view-health` for agent/device health detail                                            | Yes when employee-specific                                                         | Device sessions are not presence sessions.                                             |
| Time & Attendance    | `monitoring`    | `monitoring.biometric_devices`            | `attendance:read`, `attendance:write`                                      | `settings:admin`, `agent:manage` for device-agent integration/configuration                   | Yes for employee enrollments                                                       | Runtime flag candidate.                                                                |
| Identity Verification | `verification` | `verification.identity_checks`           | `verification:view`                                                        | `employees:read` for employee context                                                         | Yes                                                                                | Verification results are employee-specific.                                            |
| Identity Verification | `verification` | `verification.face_match`                | `verification:view`, `verification:review`                                 | `employees:read` for employee context                                                         | Yes                                                                                | Runtime flag candidate.                                                                |
| Identity Verification | `verification` | `verification.verification_policies`     | `verification:configure`                                                   | `monitoring:configure` when tied to monitoring collection rules                               | No                                                                                 | Policy setup is tenant-wide.                                                           |
| Identity Verification | `verification` | `verification.manual_review`             | `verification:review`                                                      | None in Phase 1; escalation into Exception Engine is Phase 2                                 | Yes                                                                                | Runtime flag candidate.                                                                |
| Identity Verification | `verification` | `verification.photo_challenge`           | `verification:view`, `verification:review`, `verification:configure`       | `agent:command` if requesting photo via agent                                                 | Yes                                                                                | Runtime flag candidate.                                                                |
| Analytics             | `analytics`    | `analytics.daily_reports`                | `analytics:view`                                                           | Source-module permissions for drill-down rows                                                 | Depends on report content                                                          | Aggregate report view uses analytics permission; row drill-down follows source module. |
| Analytics             | `analytics`    | `analytics.monthly_reports`              | `analytics:view`                                                           | Source-module permissions for drill-down rows                                                 | Depends on report content                                                          | Aggregate report view uses analytics permission.                                       |
| Analytics             | `analytics`    | `analytics.monitoring_snapshots`          | `analytics:view`                                                           | `employees:read` for headcount detail                                                         | Yes for employee detail                                                            | Snapshot aggregates are analytics-owned.                                               |
| Analytics             | `analytics`    | `analytics.productivity_dashboard`       | `analytics:view`                                                           | `monitoring:read` or `monitoring:view` for underlying evidence drill-down                      | Depends on drill-down                                                              | Runtime flag candidate.                                                                |
| Analytics             | `analytics`    | `analytics.data_export`                  | `analytics:export`                                                         | Source-module export/read permissions for included data categories                            | Depends on exported data                                                           | Runtime flag candidate.                                                                |
| Analytics             | `analytics`    | `analytics.scheduled_reports`            | `reports:create`                                                           | `analytics:view` for source report visibility                                                 | Depends on scheduled report content                                                | Runtime flag candidate.                                                                |

### Work Management Package

| module | module_key | feature_key | owner_permissions | dependency_permissions | management_coverage_applies | notes |
|---|---|---|---|---|---|---|
| Work Management | `work_management` | `work_management.projects` | `projects:read`, `projects:write`, `projects:create` | None | No | Project access is not described as employee-record access in Phase 1 docs. |
| Work Management | `work_management` | `work_management.tasks` | `tasks:read`, `tasks:write`, `tasks:approve`, `tasks:delete` | `employees:read` when assigning tasks to employees | Yes where employee-data access is required | Management coverage applies where employee records are exposed. |
| Work Management | `work_management` | `work_management.sprints` | `sprints:read`, `sprints:manage` | `tasks:read`, `tasks:write` for sprint task management | No | Sprint task contents follow task permissions. |
| Work Management | `work_management` | `work_management.boards` | `sprints:read`, `sprints:manage`, `tasks:read`, `tasks:write` | None | No | Board actions are represented through sprint/task permissions. |
| Work Management | `work_management` | `work_management.okrs` | `okr:read`, `okr:write` | `employees:read` when assigning OKRs to employees | Yes for employee assignment/detail | OKR ownership remains Work Management. |
| Work Management | `work_management` | `work_management.roadmaps` | `roadmaps:read`, `roadmaps:write` | `projects:read` when roadmaps are project-linked | No | Roadmaps use their own permissions. |
| Work Management | `work_management` | `work_management.time_tracking` | `time:read`, `time:write`, `time:approve` | `tasks:read` when time is task-linked | Yes for employee time data | Management coverage applies where employee time data is exposed. |
| Work Management | `work_management` | `work_management.resource_planning` | `resources:read`, `resources:manage` | `employees:read`, `analytics:read` for capacity/availability data | Yes for employee resource data | Runtime flag candidate. |
| Work Management | `work_management` | `work_management.work_analytics` | `analytics:read`, `analytics:write`, `analytics:export` | `tasks:read`, `time:read`, `projects:read` for underlying work data | Depends on report content | Runtime flag candidate. |
| Work Management | `work_management` | `work_management.github_integration` | `integrations:read`, `integrations:manage` | `projects:read`, `tasks:write` for linked project/task automation | No | Runtime flag candidate. |
| Integrations | `integrations` | `integrations.microsoft_teams` | `integrations:read`, `integrations:manage` | `workspaces:manage` for workspace/member sync | No | Chat/message sync is Phase 2 with Chat. |
| Integrations | `integrations` | `integrations.github` | `integrations:read`, `integrations:manage` | `projects:read`, `tasks:write` for project/task sync | No | Runtime flag candidate. |
| Integrations | `integrations` | `integrations.google_workspace` | `integrations:read`, `integrations:manage` | `calendar:admin` for calendar sync | No | Not marked runtime flag candidate in registry. |
| Integrations | `integrations` | `integrations.webhooks` | `integrations:read`, `integrations:manage` | Resource-specific permission for events/actions exposed by webhook | Depends on webhook scope | Runtime flag candidate. |
| Integrations | `integrations` | `integrations.api_access` | `integrations:read`, `integrations:manage` | Resource-specific permissions represented in API scopes | Depends on API scope | Runtime flag candidate. |

## Validation Checklist For Module Catalog

When seeding or editing Module Catalog:

1. Create or update `module_catalog` with the `module_key`.
2. Seed `module_features` from the `feature_key` values in this document.
3. Seed `module_permission_ownership` only from `owner_permissions`.
4. Do not seed dependency permissions as owned by the feature's module.
5. For any feature marked as management-coverage scoped, require runtime employee-data access to resolve through Org Structure management coverage. Role/override flows must not carry a separate employee-data coverage policy.
6. If a feature is marked as not controlled by permission, do not add a fake permission just to make the table look complete.
7. If a feature is a runtime flag candidate, seed a matching `feature_flags` row only after the feature exists in `module_features`.
