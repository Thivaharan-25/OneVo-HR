# Schema Catalog

Central index of all database tables across ONEVO modules. This file is a generated-style index of the detailed schema files under `database/schemas`.

> **Important:** The canonical table definitions live in the individual files under `database/schemas`. This catalog must match those files. The `overview.md` files inside each module show contextual references and must be updated when they conflict with the schema files.

---

## Summary

- **Pillars:** HR Management , Monitoring , Work Management
- **IDE Extension:** 5 tables (Phase 2)
- **Entity-map sections:** 39 numbered sections; these are planning/domain sections, not necessarily one backend module each

> **Note:** Work Management is now Pillar 3 - internal to ONEVO, not external. Old external-provisioning tables are removed from Shared Platform. Phase 1 projects belong to exactly one workspace through `projects.workspace_id`; `project_workspaces` is a Phase 2 reference only. Phase 1 SSO is Google only; Microsoft Teams workspace/member sync is Phase 2 unless explicitly reactivated, and Microsoft Teams is not a login provider. ONEVO Chat collaboration sync is Phase 2. `agent_install_entitlements` and `agent_install_jobs` are Phase 2 IDE Extension entitlement-gating tables. The `documents` table is shared between WorkManagement.Collaboration (Phase 1, which defines it) and HR Documents (Phase 2, which adds HR-specific columns). Work Management schemas (W5 OKR, W6 Time, W7 Resource) are pending detailed schema docs - table counts are estimates.

---

## Hub Tables

These tables are referenced by many others - design changes here have wide impact:

| Table | Module | Referenced By / Notes |
|:------|:-------|:-------------|
| `tenants` | Infrastructure | 120+ tables |
| `employees` | Core HR | 71+ tables |
| `users` | Infrastructure | 70+ tables |
| `workspaces` | WorkManagement.Foundation | 40+ tables |
| `projects` | WorkManagement.Projects | 20+ tables |
| `tasks` | WorkManagement.Tasks | 15+ tables |
| `channels` | WorkManagement.Chat | Phase 2 |
| `file_records` | Infrastructure | Referenced by 10+ tables |
| `registered_agents` | Agent Gateway | Referenced by Agent Gateway telemetry tables |
| `skills` | Skills & Learning | Referenced by 6+ Skills/Work tables |
| `departments` | Org Structure | Referenced by 5+ HR/org tables |
| `legal_entities` | Org Structure | Company/legal entity context inside a tenant |
| `roles` | Auth & Security | Referenced by role assignment/template tables |
| `time_off_types` | Time Off | Referenced by 4 Time Off tables |
| `subscription_plans` | Shared Platform | Referenced by subscription/billing tables |

---

## Phase 1 - HR Management (Pillar 1)

### [[database/schemas/infrastructure|Infrastructure]] (5 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `countries` | 5 | - |
| `file_records` | 8 | tenant_id->tenants, uploaded_by_id->users |
| `entity_assets` | 13 | tenant_id->tenants, file_record_id->file_records |
| `tenants` | 16 | subscription_plan_id->subscription_plans |
| `users` | 18 | tenant_id->tenants, created_by_id->users (who created this record) |

### [[database/schemas/auth|Auth & Security]] (17 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `audit_logs` | 11 | tenant_id->tenants, user_id->users (nullable for system actions) |
| `feature_access_grants` | 12 | tenant_id->tenants, grantee_id->roles.id OR users.id (polymorphic, granted_by->users |
| `legal_acceptance_records` | 11 | tenant_id->tenants, user_id->users |
| `permissions` | 5 | - |
| `invitation_tokens` | 20 | tenant_id->tenants, user_id->users, role_id->roles, revoked_by_user_id->users, revoked_by_platform_user_id->platform_users, created_by_user_id->users, created_by_platform_user_id->platform_users |
| `tenant_auth_policies` | 8 | tenant_id->tenants |
| `user_external_identities` | 9 | tenant_id->tenants, user_id->users |
| `role_permissions` | 2 | role_id->roles, permission_id->permissions |
| `roles` | 7 | tenant_id->tenants, source_template_id->role_templates when materialized from a reusable template |
| `role_templates` | 11 | - |
| `sessions` | 9 | user_id->users, tenant_id->tenants |
| `user_permission_overrides` | 10 | tenant_id->tenants, user_id->users, permission_id->permissions, granted_by->users (Super Admin who set this) |
| `user_roles` | 14 | tenant_id->tenants, user_id->users, role_id->roles, source_position_id->positions when generated from a position, source_position_access_template_id->position_access_templates, assigned_by->users (who granted this), approved_by->users |
| `access_grant_requests` | 17 | tenant_id->tenants, employee_id->employees, user_id->users who will receive the grant, target_position_id->positions, target_department_id->departments, position_access_template_id->position_access_templates, requested_role_id->roles |
| `refresh_tokens` | 7 | user_id->users |
| `user_mfa` | 9 | user_id->users, tenant_id->tenants |
| `mfa_recovery_codes` | 5 | user_id->users |

### [[database/schemas/org-structure|Org Structure]] (8 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `legal_entities` | 21 | tenant_id->tenants, parent_legal_entity_id->legal_entities, logo_file_id->file_records, country_id->countries |
| `departments` | 9 | tenant_id->tenants, legal_entity_id->legal_entities, head_position_id->positions |
| `positions` | 12 | tenant_id->tenants, legal_entity_id->legal_entities, department_id->departments |
| `position_access_templates` | 12 | tenant_id->tenants, position_id->positions, role_id->roles, created_by->users |
| `management_coverage_records` | 13 | tenant_id->tenants, legal_entity_id->legal_entities, owner_position_id->positions, covered_position_id->positions, covered_department_id->departments |
| `position_reporting_history` | 7 | tenant_id->tenants, position_id->positions, reports_to_position_id->positions |
| `position_assignments` | 10 | tenant_id->tenants, employee_id->employees, position_id->positions |
| `employee_hierarchy_closure` | 6 | tenant_id->tenants, source_position_assignment_id->position_assignments that produced the descendant placement |

### [[database/schemas/core-hr|Core HR]] (15 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `employee_addresses` | 6 | employee_id->employees |
| `employee_bank_details` | 8 | employee_id->employees |
| `employee_custom_fields` | 6 | employee_id->employees |
| `employee_dependents` | 8 | employee_id->employees |
| `employee_emergency_contacts` | 8 | employee_id->employees |
| `employee_lifecycle_events` | 8 | employee_id->employees, performed_by_id->users |
| `employee_qualifications` | 9 | employee_id->employees, document_file_id->file_records |
| `employee_salary_history` | 8 | employee_id->employees, approved_by_id->users |
| `employee_work_history` | 7 | employee_id->employees |
| `employees` | 23 | tenant_id->tenants, user_id->users (1:1), nationality_id->countries, department_id->departments, legal_entity_id->legal_entities, avatar_file_id->file_records |
| `employee_assignment_history` | 7 | tenant_id->tenants, employee_id->employees, department_id->departments, position_id->positions |
| `employee_transfers` | 12 | tenant_id->tenants, employee_id->employees, requested_by_id->users, approved_by_id->users |
| `offboarding_records` | 10 | employee_id->employees |
| `employee_checklist_tasks` | 12 | employee_id->employees, template_id->checklist_templates, assigned_to_id->users |
| `checklist_templates` | 7 | department_id->departments (nullable - global template) |

### [[database/schemas/skills|Skills Core]] (5 tables - Phase 1 subset)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `employee_skills` | 11 | tenant_id->tenants, employee_id->employees, skill_id->skills, validated_by_id->employees (nullable), last_assessed_in_review_id->review_cycles (nullable) |
| `position_skill_requirements` | 7 | tenant_id->tenants, position_id->positions, skill_id->skills |
| `skill_categories` | 7 | tenant_id->tenants, created_by_id->users |
| `skill_validation_requests` | 12 | tenant_id->tenants, employee_id->employees, skill_id->skills, validator_id->employees (manager/peer) |
| `skills` | 9 | tenant_id->tenants, category_id->skill_categories, created_by_id->users |

### [[database/schemas/time_off|Time Off]] (7 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `time_off_balances_audit` | 13 | employee_id->employees, time_off_type_id->time_off_types, policy_id->time_off_policies, entitlement_id->time_off_entitlements, time_off_request_id->time_off_requests, created_by_id->users |
| `time_off_entitlements` | 12 | legal_entity_id->legal_entities, employee_id->employees, time_off_type_id->time_off_types, policy_id->time_off_policies |
| `time_off_policies` | 9 | tenant_id->tenants, legal_entity_id->legal_entities |
| `time_off_policy_rules` | 18 | policy_id->time_off_policies, time_off_type_id->time_off_types |
| `time_off_policy_assignments` | 8 | policy_id->time_off_policies |
| `time_off_requests` | 19 | employee_id->employees, time_off_type_id->time_off_types, approved_by_id->users, document_file_id->file_records |
| `time_off_types` | 11 | tenant_id->tenants |

### [[database/schemas/calendar|Calendar]] (5 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `calendar_events` | 14 | tenant_id->tenants, created_by_id->users |
| `calendar_event_participants` | 4 | event_id->calendar_events, employee_id->employees |
| `holiday_calendar_settings` | 13 | tenant_id->tenants, legal_entity_id->legal_entities, updated_by_id->users |
| `external_calendar_connections` | 20 | tenant_id->tenants, user_id->users |
| `external_calendar_event_links` | 14 | tenant_id->tenants, calendar_event_id->calendar_events, external_calendar_connection_id->external_calendar_connections |

### [[database/schemas/configuration|Configuration]] (11 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `app_allowlist_audit` | 8 | tenant_id->tenants, allowlist_id->app_allowlists, changed_by_id->users |
| `app_allowlists` | 13 | tenant_id->tenants, global_catalog_id->global_app_catalog (if sourced from catalog), set_by_id->users (who configured this) |
| `observed_applications` | 10 | tenant_id->tenants, global_catalog_id->global_app_catalog when process_name matches (nullable) |
| `employee_monitoring_overrides` | 18 | tenant_id->tenants, employee_id->employees, set_by_id->users |
| `monitoring_policy_overrides` | 19 | tenant_id->tenants, set_by_id->users |
| `employee_work_location_settings` | 10 | tenant_id->tenants, employee_id->employees, set_by_id->users |
| `employee_remote_work_profiles` | 15 | tenant_id->tenants, employee_id->employees, verification_record_id->verification_records, approved_by_id->users |
| `remote_work_location_change_requests` | 11 | tenant_id->tenants, employee_id->employees, current_profile_id->employee_remote_work_profiles, reviewed_by_id->users, new_profile_id->employee_remote_work_profiles |
| `integration_connections` | 7 | tenant_id->tenants |
| `monitoring_feature_toggles` | 15 | tenant_id->tenants |
| `tenant_settings` | 12 | tenant_id->tenants |

---

## Phase 1 - Monitoring (Pillar 2)

### [[database/schemas/activity-monitoring|Activity Monitoring]] (9 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `activity_daily_summary` | 24 | tenant_id->tenants, employee_id->employees |
| `activity_raw_buffer` | 5 | tenant_id->tenants, agent_device_id->registered_agents |
| `activity_snapshots` | 11 | tenant_id->tenants, employee_id->employees |
| `application_categories` | 7 | tenant_id->tenants, created_by_id->users |
| `application_usage` | 13 | tenant_id->tenants, employee_id->employees |
| `device_tracking` | 8 | tenant_id->tenants, employee_id->employees |
| `meeting_sessions` | 9 | tenant_id->tenants, employee_id->employees |
| `monitoring_evidence_assets` | 15 | tenant_id->tenants, employee_id->employees, agent_device_id->registered_agents, activity_snapshot_id->activity_snapshots, file_record_id->file_records (blob storage), retention_policy_id->retention_policies, legal_hold_id->legal_holds |
| `browser_activity` | 9 | tenant_id->tenants, employee_id->employees |

### [[database/schemas/discrepancy-engine|Discrepancy Engine]] (3 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `discrepancy_events` | 17 | tenant_id->tenants, employee_id->employees |
| `work_management_daily_time_logs` | 8 | tenant_id->tenants, employee_id->employees |
| `employee_discrepancy_baselines` | 10 | tenant_id->tenants, employee_id->employees |

### [[database/schemas/time-attendance|Time & Attendance]] (17 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `attendance_corrections` | 22 | tenant_id->tenants, employee_id->employees, legal_entity_id->legal_entities, presence_session_id->presence_sessions, attendance_record_id->attendance_records, requested_by_id->users, reviewed_by_id->users |
| `break_records` | 8 | tenant_id->tenants, employee_id->employees |
| `clock_in_policies` | 36 | tenant_id->tenants, legal_entity_id->legal_entities, created_by_id->users |
| `device_sessions` | 9 | tenant_id->tenants, employee_id->employees, device_id->registered_agents |
| `presence_sessions` | 12 | tenant_id->tenants, employee_id->employees |
| `attendance_records` | 12 | tenant_id->tenants, employee_id->employees |
| `schedule_assignments` | 13 | tenant_id->tenants, legal_entity_id->legal_entities, work_schedule_id->work_schedules, department_id->departments, position_id->positions, employee_id->employees, created_by_id->users |
| `overtime_records` | 9 | tenant_id->tenants, employee_id->employees, approved_by_id->employees (nullable) |
| `public_holidays` | 6 | tenant_id->tenants (nullable - null means country-default), country_id->countries |
| `roster_entries` | 7 | tenant_id->tenants, roster_period_id->roster_periods, employee_id->employees, shift_id->shifts |
| `roster_periods` | 8 | tenant_id->tenants, created_by_id->users |
| `shift_assignments` | 8 | tenant_id->tenants, employee_id->employees, shift_id->shifts |
| `shifts` | 9 | tenant_id->tenants |
| `work_area_change_requests` | 14 | tenant_id->tenants, employee_id->employees, legal_entity_id->legal_entities, shift_assignment_id->shift_assignments, reviewed_by_id->users |
| `work_schedule_holidays` | 9 | tenant_id->tenants, work_schedule_id->work_schedules, public_holiday_id->public_holidays (nullable), created_by_id->users |
| `work_schedules` | 17 | tenant_id->tenants, legal_entity_id->legal_entities |
| `clock_in_late_deduction_rules` | 9 | tenant_id->tenants, clock_in_policy_id->clock_in_policies, time_off_type_id->time_off_types |

### [[database/schemas/exception-engine|Exception Engine]] (5 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `alert_acknowledgements` | 6 | alert_id->exception_alerts, acknowledged_by_id->users |
| `escalation_chains` | 6 | tenant_id->tenants |
| `exception_alerts` | 10 | tenant_id->tenants, employee_id->employees, rule_id->exception_rules |
| `exception_rules` | 10 | tenant_id->tenants, created_by_id->users |
| `exception_schedules` | 9 | tenant_id->tenants |

### [[database/schemas/identity-verification|Identity Verification]] (8 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `biometric_audit_logs` | 6 | tenant_id->tenants, biometric_device_id->biometric_devices |
| `biometric_devices` | 18 | tenant_id->tenants, legal_entity_id->legal_entities |
| `biometric_enrollments` | 9 | tenant_id->tenants, employee_id->employees, biometric_device_id->biometric_devices |
| `biometric_events` | 10 | tenant_id->tenants, employee_id->employees, biometric_device_id->biometric_devices |
| `verification_policies` | 13 | tenant_id->tenants |
| `verification_records` | 24 | tenant_id->tenants, employee_id->employees, agent_id->registered_agents, biometric_device_id->biometric_devices, requested_by_id->users, alert_id (nullable linked alert/notification ID), reviewed_by_id->users |
| `verification_evidence_assets` | 17 | tenant_id->tenants, employee_id->employees, verification_record_id->verification_records, presence_session_id->presence_sessions, biometric_event_id->biometric_events, file_record_id->file_records, agent_id->registered_agents when evidence came from WorkPulse/desktop agent |
| `verification_reference_photos` | 14 | tenant_id->tenants, employee_id->employees, photo_file_id->file_records, captured_device_id->registered_agents, reviewed_by_id->users, legal_acceptance_record_id->legal_acceptance_records for photo/biometric notice or consent |

### [[database/schemas/productivity-analytics|Productivity Analytics]] (5 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `daily_employee_report` | 22 | tenant_id->tenants, employee_id->employees |
| `monthly_employee_report` | 22 | tenant_id->tenants, employee_id->employees |
| `weekly_employee_report` | 20 | tenant_id->tenants, employee_id->employees |
| `monitoring_snapshot` | 15 | tenant_id->tenants |
| `wms_productivity_snapshots` | 14 | tenant_id->tenants, employee_id->employees |

---

## Phase 1 - Work Management (Pillar 3)

### [[database/schemas/wms-project-management|Work Management Foundation + Projects]] (16 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `workspaces` | 11 | tenant_id->tenants, owner_id->users |
| `workspace_roles` | 4 | workspace_id->workspaces |
| `workspace_members` | 10 | workspace_id->workspaces, user_id->users, employee_id->employees, workspace_role_id->workspace_roles, invited_by_id->users |
| `workspace_teams_links` | 13 | tenant_id->tenants, workspace_id->workspaces, created_by_id->users |
| `teams_member_sync_status` | 9 | tenant_id->tenants, workspace_teams_link_id->workspace_teams_links, workspace_id->workspaces, user_id->users |
| `projects` | 15 | tenant_id->tenants, owning_legal_entity_id->legal_entities, workspace_id->workspaces, lead_id->users |
| `project_workspaces` | 12 | project_id->projects, workspace_id->workspaces, tenant_id->tenants, legal_entity_id->legal_entities, requested_by_id->users, approved_by_id->users, linked_by_id->users |
| `project_member_invitations` | 10 | project_id->projects, tenant_id->tenants, invited_user_id->users, invited_employee_id->employees, invited_by_id->users |
| `project_link_invitations` | 9 | source_project_id->projects, target_project_id->projects, tenant_id->tenants, invited_project_admin_id->users, invited_by_id->users |
| `project_links` | 8 | source_project_id->projects, target_project_id->projects, tenant_id->tenants, created_by_id->users |
| `project_members` | 9 | project_id->projects, user_id->users, employee_id->employees |
| `epics` | 9 | project_id->projects, created_by_id->users |
| `milestones` | 7 | project_id->projects |
| `versions` | 7 | project_id->projects |
| `release_calendar` | 5 | version_id->versions, workspace_id->workspaces |
| `labels` | 5 | project_id->projects |

### [[database/schemas/wms-task-management|Task Management]] (13 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `tasks` | 19 | project_id->projects, workspace_id->workspaces, tenant_id->tenants, parent_task_id->tasks, epic_id->epics, milestone_id->milestones, created_by_id->users |
| `task_assignments` | 9 | task_id->tasks, user_id->users, employee_id->employees, assigned_by_id->users |
| `task_checklists` | 5 | task_id->tasks |
| `task_checklist_items` | 7 | checklist_id->task_checklists, checked_by_id->users |
| `task_tags` | 2 | task_id->tasks, label_id->labels |
| `task_approvals` | 8 | task_id->tasks, requested_by_id->users, approver_id->users, approver_employee_id->employees |
| `task_watchers` | 3 | task_id->tasks, user_id->users, employee_id->employees |
| `task_links` | 4 | source_task_id->tasks, target_task_id->tasks |
| `custom_fields` | 7 | project_id->projects |
| `custom_field_values` | 7 | task_id->tasks, field_id->custom_fields |
| `boards` | 6 | project_id->projects |
| `board_columns` | 7 | board_id->boards |
| `board_task_positions` | 5 | board_id->boards, column_id->board_columns, task_id->tasks |

### [[database/schemas/wms-planning|Sprint Planning + Roadmaps]] (7 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `sprints` | 9 | project_id->projects |
| `sprint_backlog_items` | 6 | sprint_id->sprints, task_id->tasks, added_by_id->users |
| `sprint_daily_snapshots` | 8 | sprint_id->sprints |
| `sprint_reports` | 7 | sprint_id->sprints |
| `sprint_report_contributors` | 17 | sprint_report_id->sprint_reports, user_id->users, employee_id->employees, workspace_id->workspaces, created_by_id->users |
| `roadmap_items` | 6 | roadmap_id->roadmaps |
| `baselines` | 6 | project_id->projects, created_by_id->users |

### [[database/schemas/wms-chat|Chat + Chat AI]] (11 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `channels` | 9 | workspace_id->workspaces, tenant_id->tenants, created_by_id->users |
| `channel_members` | 6 | channel_id->channels, user_id->users |
| `messages` | 13 | channel_id->channels, user_id->users, parent_message_id->messages |
| `message_reactions` | 4 | message_id->messages, user_id->users |
| `message_attachments` | 3 | message_id->messages, file_asset_id->file_assets |
| `message_pins` | 5 | channel_id->channels, message_id->messages, pinned_by_id->users |
| `premium_ai_detections` | 10 | message_id->messages, channel_id->channels |
| `ai_action_jobs` | 17 | detection_id->premium_ai_detections, tag_execution_id->ide_tag_executions, user_id->users, tenant_id->tenants, channel_id->channels, source_message_id->messages |
| `chat_reminder_items` | 8 | channel_id->channels, task_id->tasks, user_id->users |
| `channel_teams_links` | 14 | tenant_id->tenants, workspace_id->workspaces, channel_id->channels, workspace_teams_link_id->workspace_teams_links, created_by_id->users |
| `teams_message_sync_state` | 13 | tenant_id->tenants, channel_id->channels, message_id->messages |

### [[database/schemas/wms-collaboration|Collaboration - Documents, Wiki]] (5 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `documents` | 6 | workspace_id->workspaces, project_id->projects, locked_by->users, approved_version_id->document_versions |
| `document_versions` | 7 | document_id->documents, created_by_id->users |
| `document_approvals` | 7 | document_id->documents, requested_by_id->users, approver_id->users |
| `wiki_pages` | 12 | project_id->projects, parent_page_id->wiki_pages, author_id->users, last_edited_by->users |
| `task_documents` | 5 | task_id->tasks, document_id->documents, linked_by_id->users |

### [[database/schemas/wms-analytics|Analytics + Dashboards]] (7 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `dashboards` | 9 | workspace_id->workspaces, tenant_id->tenants, created_by_id->users |
| `chart_widgets` | 9 | dashboard_id->dashboards |
| `saved_views` | 10 | workspace_id->workspaces, created_by_id->users |
| `report_snapshots` | 7 | workspace_id->workspaces |
| `report_exports` | 10 | workspace_id->workspaces, requested_by_id->users, file_asset_id->file_assets |
| `dashboard_shares` | 5 | dashboard_id->dashboards, shared_by->users |
| `saved_view_shares` | 5 | saved_view_id->saved_views, shared_by->users |

### [[database/schemas/wms-integrations|Integrations - GitHub / GitLab / Bitbucket]] (7 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `repositories` | 11 | workspace_id->workspaces, tenant_id->tenants, auth_provider_id->auth_providers |
| `task_repository_links` | 5 | task_id->tasks, repository_id->repositories, linked_by_id->users |
| `code_activity_events` | 10 | user_id->users, tenant_id->tenants, repository_id->repositories, task_id->tasks |
| `commit_records` | 8 | repository_id->repositories, author_user_id->users |
| `pull_request_records` | 11 | repository_id->repositories, author_user_id->users |
| `ci_pipeline_runs` | 8 | repository_id->repositories |
| `task_automation_rules` | 10 | workspace_id->workspaces, created_by_id->users |

---

## Phase 2 - IDE Extension

### [[database/schemas/ide-extension|IDE Extension]] (5 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `ide_extension_installs` | 11 | user_id->users, tenant_id->tenants, workspace_id->workspaces |
| `ide_sessions` | 8 | install_id->ide_extension_installs, user_id->users, tenant_id->tenants, workspace_id->workspaces, active_project_id->projects |
| `ide_tag_executions` | 15 | user_id->users, tenant_id->tenants, session_id->ide_sessions |
| `ide_context_links` | 11 | user_id->users, tenant_id->tenants, created_by->users |
| `ide_chat_threads` | 16 | channel_id->channels, user_id->users, ide_session_id->ide_sessions, context_task_id->tasks |

---

## Phase 1 - Shared Foundation

### [[database/schemas/shared-platform|Shared Platform]] (63 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `api_keys` | 11 | tenant_id->tenants, created_by_id->users |
| `approval_actions` | 10 | workflow_instance_id->workflow_instances, workflow_step_id->workflow_steps, actor_id->employees, workflow_step_assignment_id->workflow_step_assignments, delegated_to_id->employees (nullable - only for delegate action) |
| `compliance_exports` | 10 | tenant_id->tenants, requested_by_id->users, target_user_id->users (whose data) |
| `escalation_rules` | 11 | tenant_id->tenants, escalate_to_role_id->roles (nullable), notification_template_id->notification_templates, created_by_id->users |
| `global_app_catalog` | 11 | created_by_id->platform_users |
| `feature_flags` | 9 | module_key->module_catalog(module_key), feature_key->module_features(feature_key) |
| `legal_holds` | 9 | tenant_id->tenants, placed_by_id->users, released_by_id->users (nullable) |
| `notifications` | 16 | tenant_id->tenants, recipient_user_id->users |
| `notification_channels` | 9 | tenant_id->tenants, configured_by_id->users |
| `notification_templates` | 12 | tenant_id->tenants, created_by_id->users |
| `email_delivery_logs` | 17 | tenant_id->tenants, notification_template_id->notification_templates, notification_channel_id->notification_channels |
| `support_tickets` | 16 | tenant_id->tenants, created_by_user_id->users, assigned_to_id->platform_users, resolved_by_id->platform_users |
| `support_ticket_messages` | 13 | support_ticket_id->support_tickets, tenant_id->tenants, sender_user_id->users, sender_platform_user_id->platform_users |
| `support_ticket_internal_notes` | 9 | support_ticket_id->support_tickets, tenant_id->tenants, author_platform_user_id->platform_users |
| `support_ticket_events` | 11 | support_ticket_id->support_tickets, tenant_id->tenants, actor_user_id->users, actor_platform_user_id->platform_users |
| `payment_methods` | 10 | tenant_id->tenants |
| `payment_gateway_configs` | 12 | created_by_id->platform_users |
| `payment_gateway_credentials` | 11 | payment_gateway_config_id->payment_gateway_configs, rotated_by_id->platform_users, deactivated_by_id->platform_users |
| `payment_gateway_country_routes` | 9 | gateway_config_id->payment_gateway_configs, created_by_id->platform_users |
| `plan_features` | 5 | plan_id->subscription_plans |
| `module_catalog` | 13 | - |
| `module_features` | 8 | module_key->module_catalog.module_key |
| `module_permission_ownership` | 5 | module_key->module_catalog.module_key, permission_code->permissions/code catalog |
| `tenant_module_entitlements` | 14 | tenant_id->tenants, module_key->module_catalog.module_key, created_by_user_id->users, created_by_platform_user_id->platform_users |
| `subscription_plan_price_history` | 13 | plan_id->subscription_plans, changed_by_id->platform_users |
| `module_catalog_price_history` | 13 | module_key->module_catalog.module_key, changed_by_id->platform_users |
| `tenant_provisioning_states` | 13 | tenant_id->tenants, last_updated_by_id->platform_users |
| `tenant_provisioning_validation_results` | 8 | tenant_id->tenants |
| `setup_services` | 12 | - |
| `tenant_setup_services` | 13 | tenant_id->tenants, setup_service_id->setup_services, selected_by_id->platform_users, configured_by_id->platform_users |
| `configuration_templates` | 14 | created_by_id->platform_users |
| `tenant_configuration_template_applications` | 12 | tenant_id->tenants, configuration_template_id->configuration_templates, applied_by_id->platform_users |
| `rate_limit_rules` | 7 | tenant_id->tenants (nullable - null for global rules) |
| `refresh_tokens` | 9 | user_id->users, tenant_id->tenants, replaced_by_id->refresh_tokens (rotation chain) |
| `retention_policies` | 9 | tenant_id->tenants, created_by_id->users |
| `scheduled_tasks` | 9 | tenant_id->tenants (nullable - null for system tasks) |
| `signalr_connections` | 9 | user_id->users, tenant_id->tenants |
| `sso_providers` | 12 | tenant_id->tenants |
| `external_account_connections` | 11 | tenant_id->tenants, user_id->users |
| `microsoft_graph_tokens` | 11 | tenant_id->tenants, external_account_connection_id->external_account_connections |
| `teams_webhook_subscriptions` | 11 | tenant_id->tenants |
| `teams_delta_sync_state` | 9 | tenant_id->tenants |
| `subscription_invoices` | 11 | tenant_id->tenants, subscription_id->tenant_subscriptions, payment_gateway_config_id->payment_gateway_configs |
| `billing_snapshots` | 8 | tenant_id->tenants |
| `subscription_plans` | 17 | - |
| `system_settings` | 6 | updated_by_id->users |
| `tenant_branding` | 8 | tenant_id->tenants, logo_file_id->file_records (nullable), updated_by_id->users |
| `feature_flag_overrides` | 7 | flag_key->feature_flags(key), tenant_id->tenants, granted_by_id->platform_users(id) |
| `tenant_subscriptions` | 26 | tenant_id->tenants, recommended_plan_id->subscription_plans, plan_id->subscription_plans, payment_gateway_config_id->payment_gateway_configs, created_by_user_id->users, created_by_platform_user_id->platform_users |
| `tenant_subscription_events` | 10 | tenant_subscription_id->tenant_subscriptions, tenant_id->tenants, actor_user_id->users, actor_platform_user_id->platform_users |
| `user_preferences` | 6 | user_id->users, tenant_id->tenants |
| `webhook_deliveries` | 9 | tenant_id->tenants, webhook_endpoint_id->webhook_endpoints |
| `webhook_endpoints` | 8 | tenant_id->tenants, created_by_id->users |
| `automation_definitions` | 11 | tenant_id->tenants, created_by_id->users |
| `automation_definition_versions` | 6 | automation_definition_id->automation_definitions, created_by_id->users |
| `automation_templates` | 8 | - |
| `automation_runs` | 12 | tenant_id->tenants, automation_definition_id->automation_definitions, automation_definition_version_id->automation_definition_versions, workflow_instance_id->workflow_instances |
| `workflow_definitions` | 11 | tenant_id->tenants, created_by_id->users |
| `workflow_instances` | 18 | tenant_id->tenants, workflow_definition_id->workflow_definitions, initiated_by_id->employees |
| `workflow_step_instances` | 8 | workflow_instance_id->workflow_instances, workflow_step_id->workflow_steps |
| `workflow_step_assignments` | 11 | tenant_id->tenants, workflow_step_instance_id->workflow_step_instances, assigned_employee_id->employees, assigned_user_id->users |
| `case_conversations` | 12 | tenant_id->tenants, channel_id->WorkSync Chat channels, workflow_instance_id->workflow_instances, workflow_step_instance_id->workflow_step_instances, created_by_automation_id->automation_definitions |
| `workflow_delivery_routes` | 9 | tenant_id->tenants, workflow_instance_id->workflow_instances, workflow_step_instance_id->workflow_step_instances |
| `workflow_steps` | 12 | workflow_definition_id->workflow_definitions |

### [[database/schemas/agent-gateway|Agent Gateway]] (6 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `agent_commands` | 12 | agent_id->registered_agents, tenant_id->tenants, requested_by->users (authorized user who initiated) |
| `agent_health_logs` | 8 | agent_id->registered_agents, tenant_id->tenants |
| `agent_work_location_evidence` | 19 | tenant_id->tenants, agent_id->registered_agents, employee_id->employees, presence_session_id->presence_sessions |
| `agent_policies` | 7 | agent_id->registered_agents, tenant_id->tenants |
| `registered_agents` | 12 | tenant_id->tenants, employee_id->employees (nullable - set at employee login) |
| `agent_sessions` | 7 | device_id->registered_agents.device_id, tenant_id->tenants, employee_id->employees - the currently logged-in employee |

### [[database/schemas/notifications|Notifications]] (0 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|

---

## Phase 2 Modules

> Designed but not built in Phase 1. Schema defined here so Phase 1 tables can account for future FK dependencies.

### [[database/schemas/payroll|Payroll]] (11 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `allowance_types` | 5 | tenant_id->tenants |
| `employee_allowances` | 7 | employee_id->employees, allowance_type_id->allowance_types |
| `employee_pension_enrollments` | 6 | employee_id->employees, pension_plan_id->pension_plans |
| `payroll_adjustments` | 7 | employee_id->employees, payroll_run_id->payroll_runs |
| `payroll_audit_trail` | 7 | payroll_run_id->payroll_runs |
| `payroll_connections` | 5 | tenant_id->tenants, provider_id->payroll_providers, legal_entity_id->legal_entities |
| `payroll_providers` | 6 | - |
| `payroll_runs` | 13 | legal_entity_id->legal_entities, executed_by_id->users |
| `payslips` | 20 | payroll_run_id->payroll_runs, employee_id->employees |
| `pension_plans` | 6 | tenant_id->tenants |
| `tax_configurations` | 5 | country_id->countries |

### [[database/schemas/performance|Performance]] (7 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `feedback_requests` | 9 | requester_id->employees, respondent_id->employees, subject_id->employees (who is being reviewed), cycle_id->review_cycles (nullable - ad hoc) |
| `goals` | 13 | tenant_id->tenants, employee_id->employees |
| `performance_improvement_plans` | 11 | employee_id->employees, initiated_by_id->users |
| `recognitions` | 8 | tenant_id->tenants, from_employee_id->employees, to_employee_id->employees |
| `review_cycles` | 9 | tenant_id->tenants |
| `reviews` | 13 | cycle_id->review_cycles, employee_id->employees, reviewer_id->employees |
| `succession_plans` | 8 | position_id->positions, current_holder_id->employees, successor_id->employees |

### [[database/schemas/skills|Skills & Learning]] (15 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `course_enrollments` | 10 | tenant_id->tenants, course_id->courses, employee_id->employees, assigned_by_id->employees (nullable - null if self-enrolled), linked_milestone_id->development_plan_items (nullable) |
| `course_skill_tags` | 4 | tenant_id->tenants, course_id->courses, skill_id->skills |
| `courses` | 11 | tenant_id->tenants, lms_provider_id->lms_providers (nullable - null for internal), created_by_id->users |
| `development_plan_items` | 9 | tenant_id->tenants, plan_id->development_plans, skill_id->skills (nullable), linked_course_id->courses (nullable) |
| `development_plans` | 9 | tenant_id->tenants, employee_id->employees, created_by_id->users, linked_review_cycle_id->review_cycles (nullable) |
| `employee_certifications` | 14 | tenant_id->tenants, employee_id->employees, course_id->courses (nullable - cert may not be from a course), certificate_file_record_id->file_records (nullable) |
| `employee_skills` | 11 | tenant_id->tenants, employee_id->employees, skill_id->skills, validated_by_id->employees (nullable), last_assessed_in_review_id->review_cycles (nullable) |
| `position_skill_requirements` | 7 | tenant_id->tenants, position_id->positions, skill_id->skills |
| `lms_providers` | 9 | tenant_id->tenants, created_by_id->users |
| `skill_assessment_responses` | 10 | tenant_id->tenants, employee_id->employees, question_id->skill_questions, selected_option_id->skill_question_options (nullable - for MCQ), file_record_id->file_records (nullable - for file uploads), scored_by_id->employees (nullable - for manual scoring) |
| `skill_categories` | 7 | tenant_id->tenants, created_by_id->users |
| `skill_question_options` | 6 | tenant_id->tenants, question_id->skill_questions |
| `skill_questions` | 11 | tenant_id->tenants, skill_id->skills, created_by_id->users |
| `skill_validation_requests` | 12 | tenant_id->tenants, employee_id->employees, skill_id->skills, validator_id->employees (manager/peer) |
| `skills` | 9 | tenant_id->tenants, category_id->skill_categories, created_by_id->users |

### [[database/schemas/documents|HR Documents]] (4 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `document_access_logs` | 7 | tenant_id->tenants, document_version_id->document_versions, employee_id->employees |
| `document_acknowledgements` | 7 | document_version_id->document_versions, employee_id->employees, acknowledged_by_id->users (may differ from employee if acknowledged on behalf) |
| `document_categories` | 8 | tenant_id->tenants, parent_category_id->document_categories (nullable |
| `document_templates` | 10 | tenant_id->tenants, category_id->document_categories (nullable), created_by_id->users |

### [[database/schemas/grievance|Grievance]] (2 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `disciplinary_actions` | 10 | employee_id->employees, grievance_id->grievance_cases (nullable), issued_by_id->users |
| `grievance_cases` | 13 | filed_by_id->employees (nullable if anonymous), against_id->employees (nullable), resolved_by_id->users |

### [[database/schemas/expense|Expense]] (3 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `expense_categories` | 6 | - |
| `expense_claims` | 10 | employee_id->employees |
| `expense_items` | 8 | claim_id->expense_claims, category_id->expense_categories, receipt_file_id->file_records (nullable) |

### [[database/schemas/reporting-engine|Reporting Engine]] (3 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `report_definitions` | 11 | - |
| `report_executions` | 9 | definition_id->report_definitions, file_record_id->file_records (generated report) |
| `report_templates` | 7 | - |

---

## Developer Platform

> Tables for the internal developer console (`console.onevo.io`). Not tenant-scoped. See `developer-platform/backend/admin-api-layer.md`.

### Phase 1 (5 tables)

| Table | Description |
|:------|:-----------|
| `platform_users` | Developer platform user accounts |
| `platform_user_sessions` | Platform session tokens |
| `agent_version_releases` | Desktop agent version catalog |
| `agent_deployment_rings` | Deployment ring definitions (0=Internal, 1=Beta, 2=GA) |
| `agent_deployment_ring_assignments` | Tenant ring assignments |

### Phase 2 (1 table)

| Table | Description |
|:------|:-----------|
| `platform_api_keys` | Platform API keys |

---

## Known Issues

- **Escalation boundary:** `escalation_rules` (Shared Platform) handles workflow SLA timeouts; `escalation_chains` (Exception Engine) handles alert routing for anomalies. These are distinct - do not merge.
- **documents table shared ownership:** WorkManagement.Collaboration owns the Phase 1 definition. HR Documents Phase 2 adds columns via migration. If `documents` columns conflict between HR and Work Management concerns, HR Documents wins for `employee_id` and company registration/compliance scope; Work Management wins for `workspace_id`/`project_id` scope.
- **HR/Work Management identity bridge:** Work Management membership, assignment, watcher, approval, and contributor tables persist both `user_id` and `employee_id` where HR state matters. Phase 1 must not assign work to users without active employee records.

---

## Related

- [[database/README|Database Documentation]]
- [[database/cross-module-relationships|Cross-Module Relationships]]
- [[database/migration-patterns|Migration Patterns]]
- [[database/performance|Performance]]
