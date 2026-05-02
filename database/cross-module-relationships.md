# Cross-Module Relationships

Foreign keys that cross module boundaries. These are critical for understanding data dependencies between modules and for planning migration order.

> When building EF Core migrations, modules with cross-module FKs must be migrated **after** the modules they depend on.

---

## Activity Monitoring

| Source Table | Column | Target Table | Target Module |
|:------------|:-------|:-------------|:-------------|
| `activity_daily_summary` | `employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `activity_raw_buffer` | `agent_device_id` | [[database/schemas/agent-gateway#`registered_agents`\|registered_agents]] | Agent Gateway |
| `activity_snapshots` | `employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `application_categories` | `created_by_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `application_usage` | `employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `device_tracking` | `employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `meeting_sessions` | `employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `screenshots` | `employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `screenshots` | `file_record_id` | [[database/schemas/infrastructure#`file_records`\|file_records]] | Infrastructure |

## Agent Gateway

| Source Table | Column | Target Table | Target Module |
|:------------|:-------|:-------------|:-------------|
| `agent_commands` | `requested_by` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `registered_agents` | `employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `agent_install_entitlements` | `tenant_id` | [[database/schemas/infrastructure#`tenants`\|tenants]] | Infrastructure |
| `agent_install_entitlements` | `granted_by` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `agent_install_jobs` | `user_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `agent_install_jobs` | `install_id` | [[database/schemas/ide-extension#`ide_extension_installs`\|ide_extension_installs]] | IDE Extension |

## Auth & Security

| Source Table | Column | Target Table | Target Module |
|:------------|:-------|:-------------|:-------------|
| `audit_logs` | `user_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `feature_access_grants` | `granted_by` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `gdpr_consent_records` | `user_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `sessions` | `user_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `user_permission_overrides` | `user_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `user_permission_overrides` | `granted_by` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `user_roles` | `user_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `user_roles` | `assigned_by` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |

## Calendar

| Source Table | Column | Target Table | Target Module |
|:------------|:-------|:-------------|:-------------|
| `calendar_events` | `created_by_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |

## Configuration

| Source Table | Column | Target Table | Target Module |
|:------------|:-------|:-------------|:-------------|
| `app_allowlist_audit` | `changed_by_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `app_allowlists` | `set_by_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `employee_monitoring_overrides` | `employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `employee_monitoring_overrides` | `set_by_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |

## Core HR

| Source Table | Column | Target Table | Target Module |
|:------------|:-------|:-------------|:-------------|
| `employee_lifecycle_events` | `performed_by_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `employee_qualifications` | `document_file_id` | [[database/schemas/infrastructure#`file_records`\|file_records]] | Infrastructure |
| `employee_salary_history` | `approved_by_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `employees` | `user_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `employees` | `nationality_id` | [[database/schemas/infrastructure#`countries`\|countries]] | Infrastructure |
| `employees` | `department_id` | [[database/schemas/org-structure#`departments`\|departments]] | Org Structure |
| `employees` | `job_title_id` | [[database/schemas/org-structure#`job_titles`\|job_titles]] | Org Structure |
| `employees` | `legal_entity_id` | [[database/schemas/org-structure#`legal_entities`\|legal_entities]] | Org Structure |
| `employees` | `avatar_file_id` | [[database/schemas/infrastructure#`file_records`\|file_records]] | Infrastructure |
| `onboarding_tasks` | `assigned_to_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `onboarding_templates` | `department_id` | [[database/schemas/org-structure#`departments`\|departments]] | Org Structure |

## Documents

| Source Table | Column | Target Table | Target Module |
|:------------|:-------|:-------------|:-------------|
| `document_access_logs` | `employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `document_acknowledgements` | `employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `document_acknowledgements` | `acknowledged_by_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `document_templates` | `created_by_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `document_versions` | `uploaded_by_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `documents` | `legal_entity_id` | [[database/schemas/org-structure#`legal_entities`\|legal_entities]] | Org Structure |
| `documents` | `employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `documents` | `created_by_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `documents` | `workspace_id` | [[database/schemas/wms-project-management#`workspaces`\|workspaces]] | Work Management.Foundation |
| `documents` | `project_id` | [[database/schemas/wms-project-management#`projects`\|projects]] | Work Management.ProjectManagement |
| `documents` | `locked_by` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `documents` | `approved_version_id` | [[database/schemas/wms-collaboration#`document_versions`\|document_versions]] | Work Management.Collaboration |

## Exception Engine

| Source Table | Column | Target Table | Target Module |
|:------------|:-------|:-------------|:-------------|
| `alert_acknowledgements` | `acknowledged_by_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `exception_alerts` | `employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `exception_rules` | `created_by_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |

## Expense

| Source Table | Column | Target Table | Target Module |
|:------------|:-------|:-------------|:-------------|
| `expense_claims` | `employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `expense_items` | `receipt_file_id` | [[database/schemas/infrastructure#`file_records`\|file_records]] | Infrastructure |

## Grievance

| Source Table | Column | Target Table | Target Module |
|:------------|:-------|:-------------|:-------------|
| `disciplinary_actions` | `employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `disciplinary_actions` | `issued_by_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `grievance_cases` | `filed_by_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `grievance_cases` | `against_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `grievance_cases` | `resolved_by_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |

## Identity Verification

| Source Table | Column | Target Table | Target Module |
|:------------|:-------|:-------------|:-------------|
| `biometric_devices` | `office_location_id` | [[database/schemas/org-structure#`office_locations`\|office_locations]] | Org Structure |
| `biometric_enrollments` | `employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `biometric_events` | `employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `verification_records` | `employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `verification_records` | `photo_file_id` | [[database/schemas/infrastructure#`file_records`\|file_records]] | Infrastructure |
| `verification_records` | `device_id` | [[database/schemas/agent-gateway#`registered_agents`\|registered_agents]] | Agent Gateway |
| `verification_records` | `requested_by_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `verification_records` | `alert_id` | [[database/schemas/exception-engine#`exception_alerts`\|exception_alerts]] | Exception Engine |

## Infrastructure

| Source Table | Column | Target Table | Target Module |
|:------------|:-------|:-------------|:-------------|
| `tenants` | `subscription_plan_id` | [[database/schemas/shared-platform#`subscription_plans`\|subscription_plans]] | Shared Platform |

## Leave

| Source Table | Column | Target Table | Target Module |
|:------------|:-------|:-------------|:-------------|
| `leave_balances_audit` | `employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `leave_entitlements` | `employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `leave_policies` | `country_id` | [[database/schemas/infrastructure#`countries`\|countries]] | Infrastructure |
| `leave_policies` | `job_level_id` | [[database/schemas/org-structure#`job_levels`\|job_levels]] | Org Structure |
| `leave_requests` | `employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `leave_requests` | `approved_by_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `leave_requests` | `document_file_id` | [[database/schemas/infrastructure#`file_records`\|file_records]] | Infrastructure |

## Org Structure

| Source Table | Column | Target Table | Target Module |
|:------------|:-------|:-------------|:-------------|
| `departments` | `head_employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `legal_entities` | `country_id` | [[database/schemas/infrastructure#`countries`\|countries]] | Infrastructure |
| `team_members` | `employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `teams` | `team_lead_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |

## Payroll

| Source Table | Column | Target Table | Target Module |
|:------------|:-------|:-------------|:-------------|
| `employee_allowances` | `employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `employee_pension_enrollments` | `employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `payroll_adjustments` | `employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `payroll_connections` | `legal_entity_id` | [[database/schemas/org-structure#`legal_entities`\|legal_entities]] | Org Structure |
| `payroll_runs` | `legal_entity_id` | [[database/schemas/org-structure#`legal_entities`\|legal_entities]] | Org Structure |
| `payroll_runs` | `executed_by_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `payslips` | `employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `tax_configurations` | `country_id` | [[database/schemas/infrastructure#`countries`\|countries]] | Infrastructure |

## Performance

| Source Table | Column | Target Table | Target Module |
|:------------|:-------|:-------------|:-------------|
| `feedback_requests` | `requester_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `feedback_requests` | `respondent_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `feedback_requests` | `subject_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `goals` | `employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `performance_improvement_plans` | `employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `performance_improvement_plans` | `initiated_by_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `recognitions` | `from_employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `recognitions` | `to_employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `reviews` | `employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `reviews` | `reviewer_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `succession_plans` | `position_id` | [[database/schemas/org-structure#`job_titles`\|job_titles]] | Org Structure |
| `succession_plans` | `current_holder_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `succession_plans` | `successor_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |

## Productivity Analytics

| Source Table | Column | Target Table | Target Module |
|:------------|:-------|:-------------|:-------------|
| `daily_employee_report` | `employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `monthly_employee_report` | `employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `weekly_employee_report` | `employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |

## Reporting Engine

| Source Table | Column | Target Table | Target Module |
|:------------|:-------|:-------------|:-------------|
| `report_executions` | `file_record_id` | [[database/schemas/infrastructure#`file_records`\|file_records]] | Infrastructure |

## Shared Platform

| Source Table | Column | Target Table | Target Module |
|:------------|:-------|:-------------|:-------------|
| `api_keys` | `created_by_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `approval_actions` | `actor_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `approval_actions` | `delegated_to_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `compliance_exports` | `requested_by_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `compliance_exports` | `target_user_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `escalation_rules` | `escalate_to_role_id` | [[database/schemas/auth#`roles`\|roles]] | Auth & Security |
| `escalation_rules` | `created_by_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `feature_flags` | `toggled_by_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `legal_holds` | `placed_by_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `legal_holds` | `released_by_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `notification_channels` | `configured_by_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `notification_templates` | `created_by_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `refresh_tokens` | `user_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `retention_policies` | `created_by_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `signalr_connections` | `user_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `external_account_connections` | `tenant_id` | [[database/schemas/infrastructure#`tenants`\|tenants]] | Infrastructure |
| `external_account_connections` | `user_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `microsoft_graph_tokens` | `external_account_connection_id` | [[database/schemas/shared-platform#`external_account_connections`\|external_account_connections]] | Shared Platform |
| `teams_webhook_subscriptions` | `tenant_id` | [[database/schemas/infrastructure#`tenants`\|tenants]] | Infrastructure |
| `teams_delta_sync_state` | `tenant_id` | [[database/schemas/infrastructure#`tenants`\|tenants]] | Infrastructure |
| `system_settings` | `updated_by_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `tenant_branding` | `logo_file_id` | [[database/schemas/infrastructure#`file_records`\|file_records]] | Infrastructure |
| `tenant_branding` | `updated_by_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `tenant_feature_flags` | `overridden_by_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `tenant_subscriptions` | `created_by_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `user_preferences` | `user_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `webhook_endpoints` | `created_by_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `workflow_definitions` | `created_by_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `workflow_instances` | `initiated_by_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `workflow_step_instances` | `assigned_to_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `workflow_steps` | `approver_role_id` | [[database/schemas/auth#`roles`\|roles]] | Auth & Security |

## Skills & Learning

| Source Table | Column | Target Table | Target Module |
|:------------|:-------|:-------------|:-------------|
| `course_enrollments` | `employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `course_enrollments` | `assigned_by_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `courses` | `created_by_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `development_plans` | `employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `development_plans` | `created_by_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `development_plans` | `linked_review_cycle_id` | [[database/schemas/performance#`review_cycles`\|review_cycles]] | Performance |
| `employee_certifications` | `employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `employee_certifications` | `certificate_file_record_id` | [[database/schemas/infrastructure#`file_records`\|file_records]] | Infrastructure |
| `employee_skills` | `employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `employee_skills` | `validated_by_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `employee_skills` | `last_assessed_in_review_id` | [[database/schemas/performance#`review_cycles`\|review_cycles]] | Performance |
| `job_skill_requirements` | `job_family_id` | [[database/schemas/org-structure#`job_families`\|job_families]] | Org Structure |
| `lms_providers` | `created_by_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `skill_assessment_responses` | `employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `skill_assessment_responses` | `file_record_id` | [[database/schemas/infrastructure#`file_records`\|file_records]] | Infrastructure |
| `skill_assessment_responses` | `scored_by_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `skill_categories` | `created_by_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `skill_questions` | `created_by_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `skill_validation_requests` | `employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `skill_validation_requests` | `validator_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `skills` | `created_by_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |

## Workforce Presence

| Source Table | Column | Target Table | Target Module |
|:------------|:-------|:-------------|:-------------|
| `break_records` | `employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `device_sessions` | `employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `device_sessions` | `device_id` | [[database/schemas/agent-gateway#`registered_agents`\|registered_agents]] | Agent Gateway |
| `presence_sessions` | `employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |

## Work Management.Foundation

| Source Table | Column | Target Table | Target Module |
|:------------|:-------|:-------------|:-------------|
| `workspaces` | `tenant_id` | `tenants` | Infrastructure |
| `workspaces` | `owner_id` | `users` | Infrastructure |
| `workspaces` | `legal_entity_id` | [[database/schemas/org-structure#`legal_entities`|legal_entities]] | Org Structure |
| `workspace_roles` | `workspace_id` | `workspaces` | Work Management.Foundation |
| `workspace_members` | `workspace_id` | `workspaces` | Work Management.Foundation |
| `workspace_members` | `user_id` | `users` | Infrastructure |
| `workspace_members` | `employee_id` | `employees` | Core HR |
| `workspace_hr_team_links` | `workspace_id` | `workspaces` | Work Management.Foundation |
| `workspace_hr_team_links` | `hr_team_id` | [[database/schemas/org-structure#`teams`\|teams]] | Org Structure |
| `workspace_hr_team_links` | `created_by_id` | `users` | Infrastructure |
| `workspace_teams_links` | `workspace_id` | `workspaces` | Work Management.Foundation |
| `workspace_teams_links` | `created_by_id` | `users` | Infrastructure |
| `teams_member_sync_status` | `workspace_teams_link_id` | `workspace_teams_links` | Work Management.Foundation |
| `teams_member_sync_status` | `user_id` | `users` | Infrastructure |

## Work Management.ProjectManagement

| Source Table | Column | Target Table | Target Module |
|:------------|:-------|:-------------|:-------------|
| `projects` | `workspace_id` | `workspaces` | Work Management.Foundation |
| `projects` | `tenant_id` | `tenants` | Infrastructure |
| `projects` | `lead_id` | `users` | Infrastructure |
| `project_members` | `project_id` | `projects` | Work Management.ProjectManagement |
| `project_members` | `user_id` | `users` | Infrastructure |
| `project_members` | `employee_id` | `employees` | Core HR |
| `epics` | `project_id` | `projects` | Work Management.ProjectManagement |
| `milestones` | `project_id` | `projects` | Work Management.ProjectManagement |
| `versions` | `project_id` | `projects` | Work Management.ProjectManagement |

## Work Management.TaskManagement

| Source Table | Column | Target Table | Target Module |
|:------------|:-------|:-------------|:-------------|
| `tasks` | `project_id` | `projects` | Work Management.ProjectManagement |
| `tasks` | `sprint_id` | `sprints` | Work Management.SprintPlanning |
| `tasks` | `epic_id` | `epics` | Work Management.ProjectManagement |
| `tasks` | `created_by_id` | `users` | Infrastructure |
| `task_assignments` | `user_id` | `users` | Infrastructure |
| `task_assignments` | `employee_id` | `employees` | Core HR |
| `task_assignments` | `assigned_by_id` | `users` | Infrastructure |
| `task_approvals` | `requested_by_id` | `users` | Infrastructure |
| `task_approvals` | `approver_id` | `users` | Infrastructure |
| `task_approvals` | `approver_employee_id` | `employees` | Core HR |
| `task_watchers` | `user_id` | `users` | Infrastructure |
| `task_watchers` | `employee_id` | `employees` | Core HR |
| `board_columns` | `board_id` | `boards` | Work Management.TaskManagement |
| `board_task_positions` | `task_id` | `tasks` | Work Management.TaskManagement |

## Work Management.SprintPlanning

| Source Table | Column | Target Table | Target Module |
|:------------|:-------|:-------------|:-------------|
| `sprints` | `project_id` | `projects` | Work Management.ProjectManagement |
| `sprint_backlog_items` | `sprint_id` | `sprints` | Work Management.SprintPlanning |
| `sprint_backlog_items` | `task_id` | `tasks` | Work Management.TaskManagement |
| `sprint_daily_snapshots` | `sprint_id` | `sprints` | Work Management.SprintPlanning |
| `sprint_report_contributors` | `sprint_report_id` | `sprint_reports` | Work Management.SprintPlanning |
| `sprint_report_contributors` | `user_id` | `users` | Infrastructure |
| `sprint_report_contributors` | `employee_id` | `employees` | Core HR |
| `roadmaps` | `workspace_id` | `workspaces` | Work Management.Foundation |
| `roadmap_items` | `epic_id` | `epics` | Work Management.ProjectManagement |
| `roadmap_items` | `milestone_id` | `milestones` | Work Management.ProjectManagement |

## Work Management.Chat

| Source Table | Column | Target Table | Target Module |
|:------------|:-------|:-------------|:-------------|
| `channels` | `workspace_id` | `workspaces` | Work Management.Foundation |
| `channels` | `tenant_id` | `tenants` | Infrastructure |
| `messages` | `channel_id` | `channels` | Work Management.Chat |
| `messages` | `user_id` | `users` | Infrastructure |
| `premium_ai_detections` | `message_id` | `messages` | Work Management.Chat |
| `ai_action_jobs` | `detection_id` | `premium_ai_detections` | Work Management.ChatAI |
| `ai_action_jobs` | `tag_execution_id` | `ide_tag_executions` | IDE Extension |
| `ai_action_jobs` | `user_id` | `users` | Infrastructure |
| `chat_reminder_items` | `task_id` | `tasks` | Work Management.TaskManagement |
| `channel_teams_links` | `workspace_id` | `workspaces` | Work Management.Foundation |
| `channel_teams_links` | `channel_id` | `channels` | Work Management.Chat |
| `channel_teams_links` | `workspace_teams_link_id` | `workspace_teams_links` | Work Management.Foundation |
| `teams_message_sync_state` | `channel_id` | `channels` | Work Management.Chat |
| `teams_message_sync_state` | `message_id` | `messages` | Work Management.Chat |

## Work Management.Collaboration

| Source Table | Column | Target Table | Target Module |
|:------------|:-------|:-------------|:-------------|
| `document_versions` | `document_id` | `documents` | Documents |
| `document_approvals` | `document_id` | `documents` | Documents |
| `document_approvals` | `approver_id` | `users` | Infrastructure |
| `wiki_pages` | `project_id` | `projects` | Work Management.ProjectManagement |
| `task_documents` | `task_id` | `tasks` | Work Management.TaskManagement |
| `task_documents` | `document_id` | `documents` | Documents |

## Work Management.Analytics

| Source Table | Column | Target Table | Target Module |
|:------------|:-------|:-------------|:-------------|
| `dashboards` | `workspace_id` | `workspaces` | Work Management.Foundation |
| `chart_widgets` | `dashboard_id` | `dashboards` | Work Management.Analytics |
| `dashboard_shares` | `dashboard_id` | `dashboards` | Work Management.Analytics |
| `saved_view_shares` | `saved_view_id` | `saved_views` | Work Management.Analytics |

## Work Management.Integrations

| Source Table | Column | Target Table | Target Module |
|:------------|:-------|:-------------|:-------------|
| `repositories` | `workspace_id` | `workspaces` | Work Management.Foundation |
| `task_repository_links` | `task_id` | `tasks` | Work Management.TaskManagement |
| `code_activity_events` | `repository_id` | `repositories` | Work Management.Integrations |
| `code_activity_events` | `task_id` | `tasks` | Work Management.TaskManagement |
| `commit_records` | `repository_id` | `repositories` | Work Management.Integrations |
| `task_automation_rules` | `workspace_id` | `workspaces` | Work Management.Foundation |

## IDE Extension

| Source Table | Column | Target Table | Target Module |
|:------------|:-------|:-------------|:-------------|
| `ide_extension_installs` | `user_id` | `users` | Infrastructure |
| `ide_extension_installs` | `tenant_id` | `tenants` | Infrastructure |
| `ide_extension_installs` | `workspace_id` | `workspaces` | Work Management.Foundation |
| `ide_sessions` | `install_id` | `ide_extension_installs` | IDE Extension |
| `ide_sessions` | `active_project_id` | `projects` | Work Management.ProjectManagement |
| `ide_tag_executions` | `session_id` | `ide_sessions` | IDE Extension |
| `ide_context_links` | `entity_id` | tasks / projects / sprints / documents (polymorphic) | varies |
| `ide_chat_threads` | `channel_id` | `channels` | Work Management.Chat |
| `ide_chat_threads` | `context_task_id` | `tasks` | Work Management.TaskManagement |

---

## Migration Order

Based on FK dependencies, modules should be migrated in this order:

```
1. infrastructure (tenants, users, countries, file_records)
2. auth (roles, permissions, sessions)
3. org-structure (departments, job_titles, legal_entities, team_roles)
4. core-hr (employees — the central hub)
5. configuration (tenant_settings, monitoring_toggles)
6. agent-gateway (registered_agents)
7. All HR/WFI Phase 1 modules (can be parallel):
   - leave, calendar, workforce-presence
   - activity-monitoring, discrepancy-engine, exception-engine
   - identity-verification, productivity-analytics
   - shared-platform, notifications
8. Work Management Phase 1 (ordered by FK dependency):
   - wms-project-management (workspaces → projects → epics/milestones)
   - wms-task-management (tasks → boards → board_columns)
   - wms-planning (sprints → sprint_backlog_items → sprint_daily_snapshots → roadmaps)
   - wms-chat (channels → messages → ai_action_jobs)
   - wms-collaboration (document extensions → wiki_pages → task_documents)
   - wms-analytics (dashboards → dashboard_shares)
   - wms-integrations (repositories → code_activity_events → task_automation_rules)
9. IDE Extension (depends on workspaces, projects, tasks, channels):
   - ide_extension_installs → ide_sessions → ide_tag_executions
   - ide_context_links, ide_chat_threads
   - agent_install_entitlements, agent_install_jobs (Agent Gateway additions)
10. Phase 2 modules (after Phase 1 is stable):
   - Microsoft Teams sync additions (external_account_connections -> microsoft_graph_tokens -> workspace_teams_links -> channel_teams_links -> teams_message_sync_state)
    - payroll, performance, skills
    - hr-documents (Phase 2 additions), grievance, expense
    - reporting-engine
```

## Related

- [[database/schema-catalog|Schema Catalog]]
- [[database/migration-patterns|Migration Patterns]]
- [[database/README|Database Documentation]]
