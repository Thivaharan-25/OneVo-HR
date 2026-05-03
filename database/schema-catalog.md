# Schema Catalog

Central index of all database tables across ONEVO modules. This is the **single source of truth** for database schema design. When building EF Core entities, reference these definitions.

> **Important:** The `overview.md` files inside each module also show table definitions for contextual reference. The canonical schema lives here. If they conflict, update the module overview to match this catalog.

---

## Summary

- **Total Tables:** 258 unique product schema tables after removing old external-provisioning entities, adding Microsoft Teams sync entities, adding work-location compliance tables, promoting country holiday + Google/Outlook calendar sync to Phase 1, and adding the Phase 1 HR-to-Work-Management bridge tables. MassTransit outbox/idempotency infrastructure tables are intentionally not part of this catalog.
- **Pillars:** HR Management · Workforce Intelligence · Work Management
- **IDE Extension:** 5 tables (Phase 1)
- **Entity-map sections:** 39 numbered sections; these are planning/domain sections, not necessarily one backend module each

> **Note:** Work Management is now Pillar 3 - internal to ONEVO, not external. Old external-provisioning tables are removed from Shared Platform. Phase 1 SSO is Google only; Microsoft Teams is modeled as an optional integration for team/member sync and ONEVO Chat collaboration sync, not as a login provider. `agent_install_entitlements` and `agent_install_jobs` added to Agent Gateway for IDE Extension entitlement gating. Org Structure gains 3 team permission tables (`team_roles`, `team_role_permissions`, `team_member_roles`). The `documents` table is shared between WorkManagement.Collaboration (Phase 1, which defines it) and HR Documents (Phase 2, which adds HR-specific columns). Work Management schemas (W5 OKR, W6 Time, W7 Resource) are pending detailed schema docs - table counts are estimates.

---

## Hub Tables

These tables are referenced by many others — design changes here have wide impact:

| Table | Module | Referenced By |
|:------|:-------|:-------------|
| `tenants` | Infrastructure | 120+ tables |
| `employees` | Core HR | 71+ tables |
| `users` | Infrastructure | 70+ tables |
| `workspaces` | WorkManagement.Foundation | 40+ tables |
| `projects` | WorkManagement.Projects | 20+ tables |
| `tasks` | WorkManagement.Tasks | 15+ tables |
| `channels` | WorkManagement.Chat | 10 tables |
| `file_records` | Infrastructure | 10 tables |
| `registered_agents` | Agent Gateway | 8 tables |
| `skills` | Skills & Learning | 6 tables |
| `departments` | Org Structure | 5 tables |
| `legal_entities` | Org Structure | 5 tables |
| `roles` | Auth & Security | 5 tables |
| `leave_types` | Leave | 4 tables |
| `subscription_plans` | Shared Platform | 3 tables |

---

## Phase 1 — HR Management (Pillar 1)

### [[database/schemas/infrastructure|Infrastructure]] (4 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `countries` | 5 | — |
| `file_records` | 8 | — |
| `tenants` | 9 | subscription_plan_id→subscription_plans |
| `users` | 12 | — (includes must_change_password, password_set_by_admin, temporary_password_expires_at) |

> `users` gains 3 temporary-password fields: `must_change_password boolean`, `password_set_by_admin boolean`, `temporary_password_expires_at timestamptz`. Backend returns `403 MUST_CHANGE_PASSWORD` on login when `must_change_password = true`.

### [[database/schemas/auth|Auth & Security]] (9 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `audit_logs` | 11 | tenant_id→tenants, user_id→users |
| `feature_access_grants` | 9 | tenant_id→tenants, granted_by→users |
| `gdpr_consent_records` | 7 | tenant_id→tenants, user_id→users |
| `permissions` | 4 | — |
| `role_permissions` | 2 | — |
| `roles` | 6 | tenant_id→tenants |
| `job_levels` | 6 | tenant_id→tenants, default_role_id→roles |
| `sessions` | 9 | user_id→users, tenant_id→tenants |
| `user_permission_overrides` | 8 | tenant_id→tenants, user_id→users, granted_by→users |
| `user_roles` | 4 | user_id→users, assigned_by→users |

### [[database/schemas/org-structure|Org Structure]] (12 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `department_cost_centers` | 6 | tenant_id→tenants |
| `departments` | 9 | tenant_id→tenants, head_employee_id→employees |
| `job_families` | 5 | tenant_id→tenants |
| `job_levels` | 5 | tenant_id→tenants |
| `job_titles` | 7 | tenant_id→tenants |
| `legal_entities` | 8 | tenant_id→tenants, country_id→countries |
| `office_locations` | 8 | tenant_id→tenants, legal_entity_id→legal_entities |
| `team_members` | 3 | employee_id→employees |
| `team_member_roles` | 4 | team_id→teams, employee_id→employees, team_role_id→team_roles |
| `team_role_permissions` | 3 | team_role_id→team_roles, permission_id→permissions |
| `team_roles` | 5 | team_id→teams |
| `teams` | 7 | tenant_id→tenants, team_lead_id→employees |

### [[database/schemas/core-hr|Core HR]] (13 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `employee_addresses` | 6 | — |
| `employee_bank_details` | 8 | — |
| `employee_custom_fields` | 6 | — |
| `employee_dependents` | 8 | — |
| `employee_emergency_contacts` | 8 | — |
| `employee_lifecycle_events` | 8 | performed_by_id→users |
| `employee_qualifications` | 9 | document_file_id→file_records |
| `employee_salary_history` | 8 | approved_by_id→users |
| `employee_work_history` | 8 | — |
| `employees` | 25 | tenant_id→tenants, user_id→users, nationality_id→countries |
| `offboarding_records` | 10 | — |
| `onboarding_tasks` | 9 | assigned_to_id→users |
| `onboarding_templates` | 5 | department_id→departments |

### [[database/schemas/skills|Skills Core]] (5 tables — Phase 1 subset)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `employee_skills` | 11 | tenant_id→tenants, employee_id→employees, validated_by_id→employees |
| `job_skill_requirements` | 7 | tenant_id→tenants, job_family_id→job_families |
| `skill_categories` | 7 | tenant_id→tenants, created_by_id->users |
| `skill_validation_requests` | 11 | tenant_id→tenants, employee_id→employees, validator_id→employees |
| `skills` | 9 | tenant_id→tenants, category_id→skill_categories, created_by_id->users |

### [[database/schemas/leave|Leave]] (5 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `leave_balances_audit` | 9 | employee_id→employees |
| `leave_entitlements` | 9 | employee_id→employees |
| `leave_policies` | 13 | tenant_id→tenants, country_id→countries, job_level_id→job_levels |
| `leave_requests` | 14 | employee_id→employees, approved_by_id→users, document_file_id→file_records |
| `leave_types` | 9 | tenant_id→tenants |

### [[database/schemas/calendar|Calendar]] (5 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `calendar_events` | 18 | tenant_id→tenants, created_by_id->users |
| `calendar_event_participants` | 2 | event_id→calendar_events, employee_id→employees |
| `holiday_calendar_settings` | 13 | tenant_id→tenants, legal_entity_id→legal_entities, updated_by_id→users |
| `external_calendar_connections` | 15 | tenant_id→tenants, user_id→users |
| `external_calendar_event_links` | 14 | tenant_id→tenants, calendar_event_id→calendar_events, external_calendar_connection_id→external_calendar_connections |

### [[database/schemas/configuration|Configuration]] (10 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `app_allowlist_audit` | 8 | tenant_id->tenants, changed_by_id->users |
| `app_allowlists` | 10 | tenant_id->tenants, set_by_id->users |
| `employee_monitoring_overrides` | 14 | tenant_id->tenants, employee_id->employees, set_by_id->users |
| `employee_remote_work_profiles` | 15 | tenant_id->tenants, employee_id->employees, verification_record_id->verification_records |
| `employee_work_location_settings` | 11 | tenant_id->tenants, employee_id->employees, primary_work_location_id->work_locations |
| `integration_connections` | 7 | tenant_id->tenants |
| `monitoring_feature_toggles` | 11 | tenant_id->tenants |
| `remote_work_location_change_requests` | 11 | tenant_id->tenants, employee_id->employees, reviewed_by_id->users |
| `tenant_settings` | 12 | tenant_id->tenants |
| `work_locations` | 16 | tenant_id->tenants, legal_entity_id->legal_entities, created_by_id->users |

---

## Phase 1 — Workforce Intelligence (Pillar 2)

### [[database/schemas/activity-monitoring|Activity Monitoring]] (9 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `activity_daily_summary` | 19 | tenant_id→tenants, employee_id→employees |
| `activity_raw_buffer` | 5 | tenant_id→tenants, agent_device_id→registered_agents |
| `activity_snapshots` | 11 | tenant_id→tenants, employee_id→employees |
| `application_categories` | 7 | tenant_id→tenants, created_by_id->users |
| `application_usage` | 12 | tenant_id→tenants, employee_id→employees |
| `browser_activity` | 9 | tenant_id→tenants, employee_id→employees |
| `device_tracking` | 8 | tenant_id→tenants, employee_id→employees |
| `meeting_sessions` | 9 | tenant_id→tenants, employee_id→employees |
| `screenshots` | 7 | tenant_id→tenants, employee_id→employees, file_record_id→file_records |

### [[database/schemas/discrepancy-engine|Discrepancy Engine]] (2 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `discrepancy_events` | 13 | tenant_id→tenants, employee_id→employees |
| `work_management_daily_time_logs` | 8 | tenant_id→tenants, employee_id→employees |

### [[database/schemas/workforce-presence|Workforce Presence]] (12 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `attendance_records` | 12 | tenant_id→tenants, employee_id→employees |
| `break_records` | 8 | tenant_id→tenants, employee_id→employees |
| `device_sessions` | 9 | tenant_id→tenants, employee_id→employees, device_id→registered_agents |
| `employee_schedules` | 7 | tenant_id→tenants, employee_id→employees, work_schedule_id→work_schedules |
| `overtime_records` | 9 | tenant_id→tenants, employee_id→employees, approved_by_id→employees |
| `presence_sessions` | 12 | tenant_id→tenants, employee_id→employees |
| `public_holidays` | 6 | country_id→countries |
| `roster_entries` | 6 | tenant_id→tenants, employee_id→employees, shift_id→shifts |
| `roster_periods` | 8 | tenant_id→tenants, created_by_id->users |
| `shift_assignments` | 7 | tenant_id→tenants, employee_id→employees, shift_id→shifts |
| `shifts` | 9 | tenant_id→tenants |
| `work_schedules` | 5 | tenant_id→tenants |

### [[database/schemas/exception-engine|Exception Engine]] (5 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `alert_acknowledgements` | 6 | acknowledged_by_id→users |
| `escalation_chains` | 8 | tenant_id→tenants |
| `exception_alerts` | 10 | tenant_id→tenants, employee_id→employees |
| `exception_rules` | 12 | tenant_id→tenants, created_by_id->users |
| `exception_schedules` | 9 | tenant_id→tenants |

### [[database/schemas/identity-verification|Identity Verification]] (6 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `biometric_audit_logs` | 6 | tenant_id→tenants |
| `biometric_devices` | 10 | tenant_id->tenants, office_location_id->office_locations |
| `biometric_enrollments` | 8 | tenant_id→tenants, employee_id→employees |
| `biometric_events` | 8 | tenant_id→tenants, employee_id→employees |
| `verification_policies` | 9 | tenant_id→tenants |
| `verification_records` | 15 | tenant_id→tenants, employee_id→employees, photo_file_id→file_records |

### [[database/schemas/productivity-analytics|Productivity Analytics]] (5 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `daily_employee_report` | 15 | tenant_id→tenants, employee_id→employees |
| `monthly_employee_report` | 15 | tenant_id→tenants, employee_id→employees |
| `weekly_employee_report` | 13 | tenant_id→tenants, employee_id→employees |
| `work_management_productivity_snapshots` | 14 | tenant_id→tenants, employee_id→employees |
| `workforce_snapshot` | 11 | tenant_id→tenants |

---

## Phase 1 — Work Management (Pillar 3)

### [[database/schemas/wms-project-management|Work Management Foundation + Projects]] (13 tables)

Phase 2 Microsoft Teams workspace sync additions (optional integration, not SSO):

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `workspace_teams_links` | 14 | tenant_id->tenants, workspace_id->workspaces, created_by_id->users |
| `teams_member_sync_status` | 10 | workspace_teams_link_id->workspace_teams_links, user_id->users |

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `workspaces` | 12 | tenant_id->tenants, owner_id->users, legal_entity_id->legal_entities |
| `workspace_roles` | 4 | workspace_id->workspaces |
| `workspace_members` | 11 | workspace_id->workspaces, user_id->users, employee_id->employees, workspace_role_id->workspace_roles |
| `workspace_hr_team_links` | 10 | tenant_id->tenants, workspace_id->workspaces, hr_team_id->teams |
| `projects` | 14 | workspace_id->workspaces, tenant_id->tenants, lead_id->users |
| `project_members` | 9 | project_id->projects, user_id->users, employee_id->employees |
| `epics` | 9 | project_id->projects, created_by_id->users |
| `milestones` | 8 | project_id→projects |
| `versions` | 7 | project_id->projects |
| `release_calendar` | 7 | project_id→projects, version_id→versions |
| `labels` | 6 | workspace_id→workspaces |

### [[database/schemas/wms-task-management|Task Management]] (13 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `tasks` | 19 | project_id->projects, sprint_id->sprints, epic_id->epics, created_by_id->users |
| `task_assignments` | 9 | task_id->tasks, user_id->users, employee_id->employees, assigned_by_id->users |
| `task_checklists` | 5 | task_id->tasks |
| `task_checklist_items` | 7 | checklist_id->task_checklists, checked_by_id->users |
| `task_tags` | 3 | task_id→tasks, label_id→labels |
| `task_approvals` | 8 | task_id->tasks, requested_by_id->users, approver_id->users, approver_employee_id->employees |
| `task_watchers` | 3 | task_id->tasks, user_id->users, employee_id->employees |
| `task_links` | 6 | source_task_id→tasks, target_task_id→tasks |
| `custom_fields` | 8 | workspace_id→workspaces |
| `custom_field_values` | 6 | field_id→custom_fields, task_id→tasks |
| `boards` | 7 | project_id→projects, workspace_id→workspaces |
| `board_columns` | 7 | board_id→boards (status_key maps to tasks.status, wip_limit enforced) |
| `board_task_positions` | 5 | board_id→boards, column_id→board_columns, task_id→tasks |

### [[database/schemas/wms-planning|Sprint Planning + Roadmaps]] (8 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `sprints` | 9 | project_id->projects |
| `sprint_backlog_items` | 7 | sprint_id->sprints, task_id->tasks, added_by_id->users |
| `sprint_daily_snapshots` | 9 | sprint_id→sprints (total/completed/remaining/added/removed story_points for burndown) |
| `sprint_reports` | 7 | sprint_id->sprints |
| `sprint_report_contributors` | 8 | sprint_report_id->sprint_reports, user_id->users, employee_id->employees |
| `roadmaps` | 9 | workspace_id->workspaces, created_by_id->users |
| `roadmap_items` | 7 | roadmap_id->roadmaps |
| `baselines` | 6 | project_id->projects, created_by_id->users |

> Roadmaps are **Phase 1** (Work Management Phase 4 user flow depends on them).

### [[database/schemas/wms-chat|Chat + Chat AI]] (11 tables)

Phase 2 Microsoft Teams chat sync additions (optional integration, not SSO):

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `channel_teams_links` | 14 | workspace_id->workspaces, channel_id->channels, workspace_teams_link_id->workspace_teams_links |
| `teams_message_sync_state` | 14 | channel_id->channels, message_id->messages |

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `channels` | 9 | workspace_id→workspaces, tenant_id→tenants, created_by_id->users |
| `channel_members` | 6 | channel_id→channels, user_id→users |
| `messages` | 11 | channel_id→channels, user_id→users, parent_message_id→messages |
| `message_reactions` | 4 | message_id→messages, user_id→users |
| `message_attachments` | 3 | message_id→messages, file_asset_id→file_assets |
| `message_pins` | 5 | channel_id→channels, message_id→messages, pinned_by_id->users |
| `premium_ai_detections` | 10 | message_id→messages, channel_id→channels |
| `ai_action_jobs` | 14 | detection_id→premium_ai_detections, tag_execution_id→ide_tag_executions, user_id→users |
| `chat_reminder_items` | 8 | channel_id→channels, task_id→tasks, user_id→users |

> `ai_action_jobs` is the universal undo state machine for both Chat AI (10s window) and IDE tag executions (30s window). Hangfire scans `status=pending AND undo_expires_at < now()` every 5 seconds to finalize.

### [[database/schemas/wms-collaboration|Collaboration — Documents, Wiki]] (4 new tables + shared documents)

| Table | Columns | Key FKs | Notes |
|:------|:--------|:--------|:------|
| `documents` | extended | workspace_id→workspaces, project_id→projects | Shared with HR Documents. Work Management adds workspace_id, project_id, document_scope, locked_at, locked_by, approved_version_id. Status enum gains `approved`. |
| `document_versions` | 7 | document_id→documents, created_by_id->users | Canonical version table — Phase 1 |
| `document_approvals` | 8 | document_id→documents, requested_by_id->users, approver_id→users | On approve: sets documents.status=approved + lock fields |
| `wiki_pages` | 11 | project_id→projects, parent_page_id→wiki_pages, author_id→users | Hierarchical wiki |
| `task_documents` | 5 | task_id→tasks, document_id→documents, linked_by_id->users | Durable task↔document link |

### [[database/schemas/wms-analytics|Analytics + Dashboards]] (7 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `dashboards` | 9 | workspace_id→workspaces, tenant_id→tenants, created_by_id->users |
| `chart_widgets` | 9 | dashboard_id→dashboards |
| `saved_views` | 9 | workspace_id→workspaces, created_by_id->users |
| `report_snapshots` | 7 | workspace_id→workspaces |
| `report_exports` | 10 | workspace_id→workspaces, requested_by_id->users, file_asset_id→file_assets |
| `dashboard_shares` | 7 | dashboard_id→dashboards, shared_with_id→users/teams/workspaces |
| `saved_view_shares` | 6 | saved_view_id→saved_views |

### [[database/schemas/wms-integrations|Integrations — GitHub / GitLab / Bitbucket]] (7 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `repositories` | 10 | workspace_id→workspaces, tenant_id→tenants |
| `task_repository_links` | 5 | task_id→tasks, repository_id→repositories |
| `code_activity_events` | 10 | repository_id→repositories, task_id→tasks, user_id→users |
| `commit_records` | 8 | repository_id→repositories, author_user_id→users (task_ids uuid[]) |
| `pull_request_records` | 12 | repository_id→repositories, author_user_id→users (task_ids uuid[]) |
| `ci_pipeline_runs` | 9 | repository_id→repositories (task_ids uuid[]) |
| `task_automation_rules` | 10 | workspace_id→workspaces, created_by_id->users |

---

## Phase 1 — IDE Extension

### [[database/schemas/ide-extension|IDE Extension]] (5 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `ide_extension_installs` | 11 | user_id→users, tenant_id→tenants, workspace_id→workspaces |
| `ide_sessions` | 9 | install_id→ide_extension_installs, user_id→users, active_project_id→projects |
| `ide_tag_executions` | 15 | user_id→users, session_id→ide_sessions (raw_tag_input, parsed_entity, parsed_action, undo_expires_at) |
| `ide_context_links` | 11 | user_id→users, tenant_id→tenants (repository_url + branch_name → entity_id) |
| `ide_chat_threads` | 7 | channel_id→channels, ide_session_id→ide_sessions, context_task_id→tasks |

> `ide_tag_executions.id` is referenced by `ai_action_jobs.tag_execution_id` — IDE tag undo and Chat AI undo share the same state machine.

---

## Phase 1 — Shared Foundation

### [[database/schemas/shared-platform|Shared Platform]] (35 tables)

> Old external-provisioning tables removed because Work Management is internal.

Phase 2 Microsoft Teams integration additions (optional integration, not SSO):

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `external_account_connections` | 12 | tenant_id->tenants, user_id->users |
| `microsoft_graph_tokens` | 11 | external_account_connection_id->external_account_connections |
| `teams_webhook_subscriptions` | 12 | tenant_id->tenants |
| `teams_delta_sync_state` | 10 | tenant_id->tenants |

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `api_keys` | 11 | tenant_id→tenants, created_by_id->users |
| `approval_actions` | 8 | actor_id→employees, delegated_to_id→employees |
| `compliance_exports` | 10 | tenant_id→tenants, requested_by_id->users, target_user_id→users |
| `escalation_rules` | 11 | tenant_id→tenants, escalate_to_role_id→roles, created_by_id->users |
| `global_app_catalog` | 11 | created_by_id→dev_platform_accounts |
| `feature_flags` | 8 | tenant_id→tenants, toggled_by_id→users |
| `hardware_terminals` | 11 | tenant_id→tenants |
| `legal_holds` | 9 | tenant_id→tenants, placed_by_id→users, released_by_id→users |
| `notification_channels` | 9 | tenant_id→tenants, configured_by_id→users |
| `notification_templates` | 12 | tenant_id→tenants, created_by_id->users |
| `payment_methods` | 10 | tenant_id→tenants |
| `plan_features` | 5 | — |
| `rate_limit_rules` | 7 | tenant_id→tenants |
| `refresh_tokens` | 9 | user_id→users, tenant_id→tenants |
| `retention_policies` | 9 | tenant_id→tenants, created_by_id->users |
| `scheduled_tasks` | 9 | tenant_id→tenants |
| `signalr_connections` | 9 | user_id→users, tenant_id→tenants |
| `sso_providers` | 12 | tenant_id→tenants; Phase 1 provider_type = google only |
| `subscription_invoices` | 10 | tenant_id→tenants |
| `subscription_plans` | 11 | — |
| `system_settings` | 6 | updated_by_id→users |
| `tenant_branding` | 9 | tenant_id→tenants, logo_file_id→file_records, updated_by_id→users |
| `tenant_feature_flags` | 6 | tenant_id→tenants, overridden_by_id→users |
| `tenant_subscriptions` | 11 | tenant_id→tenants, created_by_id->users |
| `user_preferences` | 6 | user_id→users, tenant_id→tenants |
| `webhook_deliveries` | 9 | tenant_id→tenants |
| `webhook_endpoints` | 8 | tenant_id→tenants, created_by_id->users |
| `workflow_definitions` | 11 | tenant_id→tenants, created_by_id->users |
| `workflow_instances` | 10 | tenant_id→tenants, initiated_by_id→employees |
| `workflow_step_instances` | 8 | assigned_to_id→employees |
| `workflow_steps` | 9 | approver_role_id→roles |

### [[database/schemas/agent-gateway|Agent Gateway]] (6 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `agent_commands` | 12 | tenant_id→tenants, requested_by_id->users |
| `agent_health_logs` | 8 | tenant_id→tenants |
| `agent_install_entitlements` | 8 | tenant_id→tenants, granted_by→users — checked server-side on every IDE install request |
| `agent_install_jobs` | 9 | tenant_id→tenants, user_id→users, install_id→ide_extension_installs — created when user approves monitoring agent install from IDE |
| `agent_policies` | 7 | tenant_id→tenants |
| `registered_agents` | 12 | tenant_id→tenants, employee_id→employees |

### [[database/schemas/notifications|Notifications]] (0 own tables)

> `notification_templates` and `notification_channels` are physically housed in the Shared Platform and counted there.

---

## Phase 2 Modules

> Designed but not built in Phase 1. Schema defined here so Phase 1 tables can account for future FK dependencies.

### [[database/schemas/payroll|Payroll]] (11 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `allowance_types` | 5 | tenant_id→tenants |
| `employee_allowances` | 7 | employee_id→employees |
| `employee_pension_enrollments` | 6 | employee_id→employees |
| `payroll_adjustments` | 7 | employee_id→employees |
| `payroll_audit_trail` | 7 | — |
| `payroll_connections` | 5 | tenant_id→tenants, legal_entity_id→legal_entities |
| `payroll_providers` | 6 | — |
| `payroll_runs` | 13 | legal_entity_id→legal_entities, executed_by_id→users |
| `payslips` | 20 | employee_id→employees |
| `pension_plans` | 6 | tenant_id→tenants |
| `tax_configurations` | 5 | country_id→countries |

### [[database/schemas/performance|Performance]] (7 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `feedback_requests` | 9 | requester_id→employees, respondent_id→employees, subject_id→employees |
| `goals` | 14 | tenant_id→tenants, employee_id→employees |
| `performance_improvement_plans` | 11 | employee_id→employees, initiated_by_id→users |
| `recognitions` | 8 | tenant_id→tenants, from_employee_id→employees, to_employee_id→employees |
| `review_cycles` | 9 | tenant_id→tenants |
| `reviews` | 11 | employee_id→employees, reviewer_id→employees |
| `succession_plans` | 8 | position_id→job_titles, current_holder_id→employees, successor_id→employees |

### [[database/schemas/skills|Skills & Learning]] (10 tables — Phase 2 remainder)

> The 5 core skill tables are built in Phase 1. These 10 are the LMS and assessment tables.

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `course_enrollments` | 10 | tenant_id→tenants, employee_id→employees, assigned_by_id→employees |
| `course_skill_tags` | 4 | tenant_id→tenants |
| `courses` | 11 | tenant_id→tenants, created_by_id->users |
| `development_plan_items` | 9 | tenant_id→tenants |
| `development_plans` | 9 | tenant_id→tenants, employee_id→employees, created_by_id->users |
| `employee_certifications` | 14 | tenant_id→tenants, employee_id→employees, certificate_file_record_id→file_records |
| `lms_providers` | 9 | tenant_id→tenants, created_by_id->users |
| `skill_assessment_responses` | 10 | tenant_id→tenants, employee_id→employees, file_record_id→file_records |
| `skill_question_options` | 6 | tenant_id→tenants |
| `skill_questions` | 11 | tenant_id→tenants, created_by_id->users |

### [[database/schemas/documents|HR Documents]] (4 tables — Phase 2 additions)

> `documents` and `document_versions` are created in Phase 1 by WorkManagement.Collaboration. HR Documents (Phase 2) adds the HR-specific tables only.

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `document_access_logs` | 7 | tenant_id→tenants, employee_id→employees |
| `document_acknowledgements` | 7 | employee_id→employees, acknowledged_by_id→users |
| `document_categories` | 8 | tenant_id→tenants |
| `document_templates` | 10 | tenant_id→tenants, created_by_id->users |

### [[database/schemas/grievance|Grievance]] (2 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `disciplinary_actions` | 10 | employee_id→employees, issued_by_id→users |
| `grievance_cases` | 13 | filed_by_id→employees, against_id→employees, resolved_by_id→users |

### [[database/schemas/expense|Expense]] (3 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `expense_categories` | 6 | — |
| `expense_claims` | 10 | employee_id→employees |
| `expense_items` | 8 | receipt_file_id→file_records |

### [[database/schemas/reporting-engine|Reporting Engine]] (3 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `report_definitions` | 11 | — |
| `report_executions` | 9 | file_record_id→file_records |
| `report_templates` | 7 | — |

---

## Developer Platform

> Tables for the internal developer console (`console.onevo.io`). Not tenant-scoped. See `developer-platform/backend/admin-api-layer.md`.

### Phase 1 (5 tables)

| Table | Description |
|:------|:-----------|
| `dev_platform_accounts` | Developer platform user accounts |
| `dev_platform_sessions` | Platform session tokens |
| `agent_version_releases` | Desktop agent version catalog |
| `agent_deployment_rings` | Deployment ring definitions (0=Internal, 1=Beta, 2=GA) |
| `agent_deployment_ring_assignments` | Tenant ring assignments |

### Phase 2 (1 table)

| Table | Description |
|:------|:-----------|
| `platform_api_keys` | Platform API keys |

---

## Known Issues

- **Escalation boundary:** `escalation_rules` (Shared Platform) handles workflow SLA timeouts; `escalation_chains` (Exception Engine) handles alert routing for anomalies. These are distinct — do not merge.
- **documents table shared ownership:** WorkManagement.Collaboration owns the Phase 1 definition. HR Documents Phase 2 adds columns via migration. If `documents` columns conflict between HR and Work Management concerns, HR Documents wins for `employee_id`/`legal_entity_id` scope; Work Management wins for `workspace_id`/`project_id` scope.
- **HR/Work Management identity bridge:** Work Management membership, assignment, watcher, approval, and contributor tables persist both `user_id` and `employee_id` where HR state matters. Phase 1 must not assign work to users without active employee records.
- **Work Management schema coverage:** Core Work Management schema files now exist for project management, task management, planning, chat, collaboration, analytics, integrations, and IDE extension. OKR, time management, and resource management are covered in the unified entity map and module docs; create dedicated schema files if the implementation team wants one file per Work Management subdomain.

---

## Related

- [[database/README|Database Documentation]]
- [[database/cross-module-relationships|Cross-Module Relationships]]
- [[database/migration-patterns|Migration Patterns]]
- [[database/performance|Performance]]




