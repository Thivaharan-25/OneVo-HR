# Phase 1 Feature Permission Map

## Purpose

This document connects Phase 1 `module_key`, `feature_key`, owner permissions, dependency permissions, and access-policy behavior.

It is intended to support Module Catalog seeding and permission ownership design without confusing module ownership with cross-module data dependencies.

## Core Model

| Layer | Meaning |
|---|---|
| `module_key` | Product module registered in Module Catalog. |
| `feature_key` | Commercial feature inside a module. Plans/custom contracts select these keys. |
| `owner_permissions` | Permissions that control actions inside the feature's owning module. |
| `dependency_permissions` | Permissions required only because the feature reads or writes another module's data. These permissions are not owned by the feature's module. |
| `access_policy_applies` | Whether employee-data scope must be resolved with access policy, such as `self`, `direct_reports`, `reporting_tree`, or `organization`. |
| `notes` | Clarifies non-permission-controlled features, runtime-flag behavior, or wording inconsistencies. |

## Access Policy Values

Access policy is only for permissions that operate on employee-owned or employee-scoped data. Tenant-wide permissions such as `settings:admin`, `billing:manage`, `org:manage`, and `integrations:manage` do not need an access policy.

| Access policy | Meaning | Use when |
|---|---|---|
| `self` | Own employee record only. | Employee self-service views and default fallback when no broader policy is assigned. |
| `direct_reports` | Employees who report directly to the current employee. | Line-manager approval or direct team visibility. |
| `reporting_tree` | All employees below the current employee in the reporting hierarchy. | Manager-of-managers visibility. |
| `department` | Active employees in the same department. | Department-level HR or operational support. |
| `department_tree` | Active employees in the department and its child departments. | Department heads with nested department ownership. |
| `org_unit_tree` | Active employees under the user's org unit. | Regional/business-unit hierarchy when org units are modeled separately from departments. |
| `organization` | All active employees in the tenant. | HR, payroll, compliance, or executive access. |

`department_tree` and `org_unit_tree` should only be used when the tenant org model has those hierarchy concepts populated. If the implementation only has position-derived reporting hierarchy and flat departments, use `direct_reports`, `reporting_tree`, `department`, or `organization` until department/org-unit hierarchy tables exist.

## Important Rules

1. A permission does not turn on a feature key.
2. A feature key does not grant user access by itself.
3. Effective access requires active module entitlement, included feature key, runtime flag if applicable, owner permission, dependency permission where required, and access-policy scope where employee data is involved.
4. Dependency permissions must not be treated as permission ownership by the feature's module.
5. Foundation features can exist as feature keys for consistency, but they are always included and are not separately sellable in Phase 1.

## Known Wording Inconsistencies

| Area | Issue | Required interpretation |
|---|---|---|
| Workforce Presence | The module is named Workforce Presence, but many permissions still use `attendance:*`. | Treat `attendance:*` as the attendance/presence record permission namespace inside Workforce Presence. |
| `workforce:view` vs `attendance:read` | Both appear around presence screens. | `attendance:read` controls historical attendance/presence record access. `workforce:view` controls workforce intelligence/live status/dashboard access. |
| Exceptions | Older flows use `exceptions:view` and `exceptions:acknowledge`; the permissions reference says these are replaced by `monitoring:alerts:read` and `monitoring:alerts:resolve`. | Prefer the replacement names in new work unless the product explicitly keeps the older names. |
| Roles | Older flows use `roles:manage`; the permissions reference splits it into `roles:create`, `roles:update`, `roles:delete`, `roles:assign`, and `permissions:manage`. | Prefer the split permissions in new work unless backward compatibility requires `roles:manage`. |
| Automation / Workflow | Older docs referenced both `automation:*` and `workflows:*`. | Use `workflows:read` for visibility/status/history and `workflows:manage` for Automation Center rule, template, resolver, and SLA configuration. Runtime approve/reject actions use the automated resource permission, such as `leave:approve` or `expense:approve`, plus current assignment. |

## Phase 1 Feature To Permission Map

### Foundation Modules

| module | module_key | feature_key | owner_permissions | dependency_permissions | access_policy_applies | notes |
|---|---|---|---|---|---|---|
| Auth & Security | `auth` | `auth.google_login` | None | None | No | Login capability; not controlled by tenant role permission. Operational runtime flag candidate only. |
| Auth & Security | `auth` | `auth.mfa_enforcement` | `users:manage` for admin reset/enforcement actions | `settings:admin` if changing tenant-wide auth policy | No | End users enabling their own MFA do not need a grantable permission. |
| Configuration | `configuration` | `configuration.tenant_settings` | `settings:read`, `settings:admin` | None | No | Foundation tenant setting capability. |
| Roles & Permissions | `roles` | `roles.permission_management` | `roles:create`, `roles:update`, `roles:delete`, `roles:assign`, `permissions:manage` | `users:read` when selecting users for assignment | No | Older docs use `roles:manage`; split permissions are preferred for new design. |
| Notifications | `notifications` | `notifications.email_delivery` | `notifications:manage`, `settings:notifications` | None | No | Delivery itself is system behavior; permissions control template/channel configuration. |
| Notifications | `notifications` | `notifications.in_app_delivery` | `notifications:manage`, `settings:notifications` | None | No | Reading notifications is derived or authenticated-user behavior, not a normal feature owner permission. |
| Org Structure | `org` | `org.structure_management` | `org:read`, `org:manage` | `employees:read` when selecting or showing employees in the structure | Yes, only for employee lookup/detail dependency | `org:*` owns the structure; `employees:*` remains owned by Core HR. |
| Workflow Engine | `workflow_engine` | `workflow_engine.automation_execution` | `workflows:read`, `workflows:manage` | Module-specific permissions for the resource being automated, such as `leave:approve` or `expense:approve` | Depends on automated resource | `workflows:manage` controls workflow configuration. Runtime approve/reject actions require the relevant module permission plus current step assignment. |

### HR Core Package

| module | module_key | feature_key | owner_permissions | dependency_permissions | access_policy_applies | notes |
|---|---|---|---|---|---|---|
| Core HR | `core_hr` | `core_hr.employee_profiles` | `employees:read-own`, `employees:read`, `employees:write`, `employees:delete` | None | Yes for `employees:read`, `employees:write`, `employees:delete` | Own profile read is auto-grant. |
| Core HR | `core_hr` | `core_hr.employee_lifecycle` | `employees:read`, `employees:write` | `org:read` when showing department/job context | Yes | Lifecycle changes remain Core HR ownership. |
| Core HR | `core_hr` | `core_hr.onboarding` | `employees:write` | `users:manage` for auth invitation, `roles:assign` for assigning access, `org:read` for placement | Yes | Cross-module permissions are dependencies, not Core HR-owned permissions. |
| Core HR | `core_hr` | `core_hr.offboarding` | `employees:write` | `users:manage` for account suspension, `documents:manage` for document handoff, `payroll:write` for final payroll data | Yes | Dependencies apply only when the offboarding flow performs those actions. |
| Core HR | `core_hr` | `core_hr.dependents_contacts` | `employees:read-own`, `employees:write` | None | Yes for admin writes | Own dependent/contact management is self-scoped. |
| Core HR | `core_hr` | `core_hr.qualifications` | `employees:read-own`, `employees:write` | `skills:read`, `skills:write`, `skills:validate` when qualification data is handled through Skills | Yes | Boundary with Skills must be decided per screen/API. |
| Core HR | `core_hr` | `core_hr.compensation` | `employees:write` | `payroll:read`, `payroll:write` for salary/payroll-sensitive data | Yes | Compensation profile is Core HR; payroll amounts and payroll processing remain Payroll dependency. |
| Leave | `leave` | `leave.requests` | `leave:read-own`, `leave:read`, `leave:create` | `calendar:read` when showing calendar conflicts | Yes for `leave:read`, `leave:create` on behalf of others | Own leave read is auto-grant. |
| Leave | `leave` | `leave.approvals` | `leave:approve` | `employees:read` when showing employee context | Yes | Approval scope is controlled by access policy on `leave:approve`. |
| Leave | `leave` | `leave.balances` | `leave:read-own`, `leave:read`, `leave:manage` | None | Yes for `leave:read` and `leave:manage` over employee balances | Own balance read is auto-grant. |
| Leave | `leave` | `leave.accrual_rules` | `leave:manage` | None | No | Runtime flag candidate. |
| Leave | `leave` | `leave.leave_types` | `leave:read`, `leave:manage` | None | No | Leave type setup is tenant-wide configuration inside Leave. |
| Leave | `leave` | `leave.calendar_integration` | `leave:read`, `leave:manage` | `calendar:read`, `calendar:admin` for calendar sync/configuration | Yes for leave records | Calendar permission is dependency. |
| Calendar | `calendar` | `calendar.company_calendar` | `calendar:read`, `calendar:write` | None | No | `calendar:read` is an auto-grant in the permissions reference. |
| Calendar | `calendar` | `calendar.holidays` | `calendar:read`, `calendar:admin` | None | No | Holiday administration uses `calendar:admin`. |
| Calendar | `calendar` | `calendar.work_schedules` | `calendar:read`, `calendar:write` | `attendance:read`, `attendance:write` when tied to Workforce Presence schedules | No for calendar data; Yes for attendance schedule records | Schedule ownership must be clear per API. |
| Calendar | `calendar` | `calendar.leave_visibility` | `calendar:read` | `leave:read` for leave record visibility | Yes for leave dependency | Calendar can display leave only through Leave access rules. |
| Calendar | `calendar` | `calendar.event_sync` | `calendar:admin` | `settings:integrations` for tenant-wide external integration setup | No | External integration setup is dependency. |

### Intelligence Package

| module                | module_key     | feature_key                              | owner_permissions                                                          | dependency_permissions                                                                        | access_policy_applies                                                              | notes                                                                                  |
| --------------------- | -------------- | ---------------------------------------- | -------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| Activity Monitoring   | `monitoring`   | `monitoring.activity_tracking`           | `monitoring:read`, `workforce:view`                                        | `employees:read` for employee identity/context                                                | Yes for employee context                                                           | Monitoring data access must obey employee scope where employee-specific.               |
| Activity Monitoring   | `monitoring`   | `monitoring.app_usage`                   | `monitoring:read`, `workforce:view`                                        | `employees:read` for employee context                                                         | Yes                                                                                | App usage is monitoring data, not Core HR data.                                        |
| Activity Monitoring   | `monitoring`   | `monitoring.website_usage`               | `monitoring:read`, `workforce:view`                                        | `employees:read` for employee context                                                         | Yes                                                                                | Runtime flag candidate.                                                                |
| Activity Monitoring   | `monitoring`   | `monitoring.idle_detection`              | `monitoring:read`, `workforce:view`, `monitoring:configure` for thresholds | `employees:read` for employee context                                                         | Yes                                                                                | Configuration uses `monitoring:configure`.                                             |
| Activity Monitoring   | `monitoring`   | `monitoring.screenshot_on_demand`        | `monitoring:read`, `workforce:view`                                        | `agent:command` to request capture                                                            | Yes                                                                                | Runtime flag candidate.                                                                |
| Activity Monitoring   | `monitoring`   | `monitoring.app_allowlist`               | `monitoring:view-settings`, `monitoring:configure`                         | None                                                                                          | No                                                                                 | Runtime flag candidate.                                                                |
| Activity Monitoring   | `monitoring`   | `monitoring.productivity_classification` | `monitoring:configure`                                                     | `analytics:view` when surfaced in analytics dashboards                                        | No for config; depends on analytics screen for dashboard                           | Runtime flag candidate.                                                                |
| Activity Monitoring   | `monitoring`   | `monitoring.raw_data_processing`         | `monitoring:read`, `workforce:view`                                        | None                                                                                          | Yes when employee-specific raw data is exposed                                     | Internal processing has no user action unless exposed through UI/API.                  |
| Workforce Presence    | `workforce`    | `workforce.presence_sessions`            | `attendance:read`, `attendance:read-own`, `workforce:view` for live status | `employees:read` for employee context                                                         | Yes for `attendance:read`; live status scope must follow workforce dashboard rules | Historical presence uses `attendance:read`; live endpoint uses `workforce:view`.       |
| Workforce Presence    | `workforce`    | `workforce.shift_schedules`              | `attendance:read`, `attendance:write`                                      | `org:read` or `org:manage` for department/team assignment                                     | Yes for employee schedule assignment                                               | Department-wide assignment is the documented Org dependency.                           |
| Workforce Presence    | `workforce`    | `workforce.break_tracking`               | `attendance:read`, `attendance:write`, `attendance:write-own`              | None                                                                                          | Yes for `attendance:read` and admin writes                                         | Own break start/end uses auto-grant-style own write behavior.                          |
| Workforce Presence    | `workforce`    | `workforce.overtime`                     | `attendance:write`, `attendance:approve`                                   | `payroll:read` when viewing payroll impact                                                    | Yes                                                                                | Runtime flag candidate.                                                                |
| Workforce Presence    | `workforce`    | `workforce.attendance_corrections`       | `attendance:write`, `attendance:approve`, `attendance:write-own`           | None                                                                                          | Yes                                                                                | Runtime flag candidate.                                                                |
| Workforce Presence    | `workforce`    | `workforce.device_sessions`              | `workforce:view`                                                           | `agent:view-health` for agent/device health detail                                            | Yes when employee-specific                                                         | Device sessions are not presence sessions.                                             |
| Workforce Presence    | `workforce`    | `workforce.biometric_devices`            | `attendance:read`, `attendance:write`                                      | `settings:admin`, `agent:manage` for device-agent integration/configuration                   | Yes for employee enrollments                                                       | Runtime flag candidate.                                                                |
| Identity Verification | `verification` | `verification.identity_checks`           | `verification:view`                                                        | `employees:read` for employee context                                                         | Yes                                                                                | Verification results are employee-specific.                                            |
| Identity Verification | `verification` | `verification.face_match`                | `verification:view`, `verification:review`                                 | `employees:read` for employee context                                                         | Yes                                                                                | Runtime flag candidate.                                                                |
| Identity Verification | `verification` | `verification.verification_policies`     | `verification:configure`                                                   | `monitoring:configure` when tied to monitoring collection rules                               | No                                                                                 | Policy setup is tenant-wide.                                                           |
| Identity Verification | `verification` | `verification.manual_review`             | `verification:review`                                                      | `exceptions:manage` only when escalating confirmed mismatches into exception workflow         | Yes                                                                                | Runtime flag candidate.                                                                |
| Identity Verification | `verification` | `verification.photo_challenge`           | `verification:view`, `verification:review`, `verification:configure`       | `agent:command` if requesting photo via agent                                                 | Yes                                                                                | Runtime flag candidate.                                                                |
| Exception Engine      | `exceptions`   | `exceptions.rules`                       | `exceptions:manage`                                                        | `monitoring:read`, `attendance:read`, or other source permissions when previewing source data | No for rule config; source preview follows source permission                       | Rule configuration is owned by Exception Engine.                                       |
| Exception Engine      | `exceptions`   | `exceptions.alerts`                      | `monitoring:alerts:read`, `monitoring:alerts:resolve`                      | Source-module read permission for evidence drill-down                                         | Depends on alert evidence                                                          | Older docs use `exceptions:view` and `exceptions:acknowledge`.                         |
| Exception Engine      | `exceptions`   | `exceptions.escalation_chains`           | `exceptions:manage`                                                        | `employees:read`, `org:read` for resolver selection                                           | Yes for employee/org resolver data                                                 | Escalation setup owns rules; employee/org data is dependency.                          |
| Exception Engine      | `exceptions`   | `exceptions.baseline_relative_rules`     | `exceptions:manage`                                                        | `analytics:view` or `monitoring:read` when previewing baseline data                           | Depends on preview data                                                            | Runtime flag candidate.                                                                |
| Exception Engine      | `exceptions`   | `exceptions.remote_screenshot_request`   | `exceptions:manage`                                                        | `agent:command`, `monitoring.screenshot_on_demand` feature inclusion                          | Yes                                                                                | Runtime flag candidate.                                                                |
| Exception Engine      | `exceptions`   | `exceptions.remote_photo_request`        | `exceptions:manage`                                                        | `agent:command`, `verification.photo_challenge` feature inclusion                             | Yes                                                                                | Runtime flag candidate.                                                                |
| Analytics             | `analytics`    | `analytics.daily_reports`                | `analytics:view`                                                           | Source-module permissions for drill-down rows                                                 | Depends on report content                                                          | Aggregate report view uses analytics permission; row drill-down follows source module. |
| Analytics             | `analytics`    | `analytics.monthly_reports`              | `analytics:view`                                                           | Source-module permissions for drill-down rows                                                 | Depends on report content                                                          | Aggregate report view uses analytics permission.                                       |
| Analytics             | `analytics`    | `analytics.workforce_snapshots`          | `analytics:view`                                                           | `employees:read` for headcount detail                                                         | Yes for employee detail                                                            | Snapshot aggregates are analytics-owned.                                               |
| Analytics             | `analytics`    | `analytics.productivity_dashboard`       | `analytics:view`                                                           | `monitoring:read` or `workforce:view` for underlying evidence drill-down                      | Depends on drill-down                                                              | Runtime flag candidate.                                                                |
| Analytics             | `analytics`    | `analytics.data_export`                  | `analytics:export`                                                         | Source-module export/read permissions for included data categories                            | Depends on exported data                                                           | Runtime flag candidate.                                                                |
| Analytics             | `analytics`    | `analytics.scheduled_reports`            | `reports:create`                                                           | `analytics:view` for source report visibility                                                 | Depends on scheduled report content                                                | Runtime flag candidate.                                                                |

### Work Management Package

| module | module_key | feature_key | owner_permissions | dependency_permissions | access_policy_applies | notes |
|---|---|---|---|---|---|---|
| Work Management | `work_management` | `work_management.projects` | `projects:read`, `projects:write`, `projects:create` | None | No | Project access is not described as employee-record access in Phase 1 docs. |
| Work Management | `work_management` | `work_management.tasks` | `tasks:read`, `tasks:write`, `tasks:approve`, `tasks:delete` | `employees:read` when assigning tasks to employees | Yes for task approval where employee-data scoped | Access policy applies to `tasks:read` and `tasks:approve` per access-policy reference. |
| Work Management | `work_management` | `work_management.sprints` | `sprints:read`, `sprints:manage` | `tasks:read`, `tasks:write` for sprint task management | No | Sprint task contents follow task permissions. |
| Work Management | `work_management` | `work_management.boards` | `sprints:read`, `sprints:manage`, `tasks:read`, `tasks:write` | None | No | Board actions are represented through sprint/task permissions. |
| Work Management | `work_management` | `work_management.okrs` | `okr:read`, `okr:write` | `employees:read` when assigning OKRs to employees | Yes for employee assignment/detail | OKR ownership remains Work Management. |
| Work Management | `work_management` | `work_management.roadmaps` | `roadmaps:read`, `roadmaps:write` | `projects:read` when roadmaps are project-linked | No | Roadmaps use their own permissions. |
| Work Management | `work_management` | `work_management.time_tracking` | `time:read`, `time:write`, `time:approve` | `tasks:read` when time is task-linked | Yes for `time:read`, `time:approve` | Access policy applies to time read/approval. |
| Work Management | `work_management` | `work_management.resource_planning` | `resources:read`, `resources:manage` | `employees:read`, `analytics:read` for capacity/availability data | Yes for employee resource data | Runtime flag candidate. |
| Work Management | `work_management` | `work_management.work_analytics` | `analytics:read`, `analytics:write`, `analytics:export` | `tasks:read`, `time:read`, `projects:read` for underlying work data | Depends on report content | Runtime flag candidate. |
| Work Management | `work_management` | `work_management.github_integration` | `integrations:read`, `integrations:manage` | `projects:read`, `tasks:write` for linked project/task automation | No | Runtime flag candidate. |
| Work Management | `work_management` | `work_management.automation_rules` | `workflows:read`, `workflows:manage` for rule configuration | Feature-specific permission for the automated resource | Depends on automated resource | Runtime actions use the automated resource permission, not a generic workflow execute permission. |
| Chat | `chat` | `chat.channels` | `chat:read`, `chat:manage` | `workspaces:read` if channels are workspace-scoped | No | Channel management uses `chat:manage`. |
| Chat | `chat` | `chat.threads` | `chat:read`, `chat:write` | None | No | Thread read/write follows chat permissions. |
| Chat | `chat` | `chat.direct_messages` | `chat:read`, `chat:write` | None | No | Direct messages follow chat permissions. |
| Chat | `chat` | `chat.workspace_messages` | `chat:read`, `chat:write` | `workspaces:read` for workspace context | No | Workspace membership rules must also apply. |
| Chat | `chat` | `chat.message_search` | `chat:read` | None | No | Runtime flag candidate. |
| Chat | `chat` | `chat.teams_sync` | `chat:write`, `chat:manage` | `integrations:manage`, `workspaces:manage` | No | Runtime flag candidate. |
| Chat AI | `chat_ai` | `chat_ai.agentic_chat` | `chat:read`, `chat:write` | Permissions for any data/tool the assistant reads or mutates | Depends on tool/data accessed | Runtime flag candidate. |
| Chat AI | `chat_ai` | `chat_ai.streaming_responses` | `chat:read`, `chat:write` | None | No | Runtime flag candidate. |
| Chat AI | `chat_ai` | `chat_ai.ai_task_suggestions` | `chat:read`, `chat:write` | `tasks:write` to apply task suggestions | No | Runtime flag candidate. |
| Chat AI | `chat_ai` | `chat_ai.ai_summaries` | `chat:read` | Source permissions for summarized content | Depends on summarized content | Runtime flag candidate. |
| Chat AI | `chat_ai` | `chat_ai.ai_insights` | `chat:read` | `analytics:read` when insight uses analytics data | Depends on insight source | Runtime flag candidate. |
| Integrations | `integrations` | `integrations.microsoft_teams` | `integrations:read`, `integrations:manage` | `workspaces:manage`, `chat:write` for Teams workspace/chat sync | No | Runtime flag candidate. |
| Integrations | `integrations` | `integrations.github` | `integrations:read`, `integrations:manage` | `projects:read`, `tasks:write` for project/task sync | No | Runtime flag candidate. |
| Integrations | `integrations` | `integrations.google_workspace` | `integrations:read`, `integrations:manage` | `calendar:admin` for calendar sync | No | Not marked runtime flag candidate in registry. |
| Integrations | `integrations` | `integrations.slack` | `integrations:read`, `integrations:manage` | `chat:write` if Slack mirrors chat messages | No | Not marked runtime flag candidate in registry. |
| Integrations | `integrations` | `integrations.webhooks` | `integrations:read`, `integrations:manage` | Resource-specific permission for events/actions exposed by webhook | Depends on webhook scope | Runtime flag candidate. |
| Integrations | `integrations` | `integrations.api_access` | `integrations:read`, `integrations:manage` | Resource-specific permissions represented in API scopes | Depends on API scope | Runtime flag candidate. |

## Validation Checklist For Module Catalog

When seeding or editing Module Catalog:

1. Create or update `module_catalog` with the `module_key`.
2. Seed `module_features` from the `feature_key` values in this document.
3. Seed `module_permission_ownership` only from `owner_permissions`.
4. Do not seed dependency permissions as owned by the feature's module.
5. For any permission marked as access-policy scoped, require the role/override flow to carry the selected access policy.
6. If a feature is marked as not controlled by permission, do not add a fake permission just to make the table look complete.
7. If a feature is a runtime flag candidate, seed a matching `feature_flags` row only after the feature exists in `module_features`.
