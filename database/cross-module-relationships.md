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
| `monitoring_evidence_assets` | `employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `monitoring_evidence_assets` | `file_record_id` | [[database/schemas/infrastructure#`file_records`\|file_records]] | Infrastructure |

## Agent Gateway

| Source Table | Column | Target Table | Target Module |
|:------------|:-------|:-------------|:-------------|
| `agent_commands` | `requested_by` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `registered_agents` | `employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `agent_install_entitlements` | `tenant_id` | [[database/schemas/infrastructure#`tenants`\|tenants]] | Infrastructure |
| `agent_install_entitlements` | `granted_by` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `agent_install_jobs` | `user_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `agent_install_jobs` | `install_id` | [[database/schemas/ide-extension#`ide_extension_installs`\|ide_extension_installs]] | IDE Extension (Phase 2) |

## Auth & Security

| Source Table | Column | Target Table | Target Module |
|:------------|:-------|:-------------|:-------------|
| `audit_logs` | `user_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `feature_access_grants` | `granted_by` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `legal_acceptance_records` | `user_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `sessions` | `user_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `user_permission_overrides` | `user_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `user_permission_overrides` | `granted_by` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `user_roles` | `user_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `user_roles` | `assigned_by` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `user_roles` | `approved_by` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `user_roles` | `source_position_id` | [[database/schemas/org-structure#`positions`\|positions]] | Org Structure |
| `user_roles` | `source_position_access_template_id` | [[database/schemas/org-structure#`position_access_templates`\|position_access_templates]] | Org Structure |
| `access_grant_requests` | `employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `access_grant_requests` | `user_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `access_grant_requests` | `requested_by` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `access_grant_requests` | `approved_by` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `access_grant_requests` | `target_position_id` | [[database/schemas/org-structure#`positions`\|positions]] | Org Structure |
| `access_grant_requests` | `target_department_id` | [[database/schemas/org-structure#`departments`\|departments]] | Org Structure |
| `access_grant_requests` | `position_access_template_id` | [[database/schemas/org-structure#`position_access_templates`\|position_access_templates]] | Org Structure |
| `access_grant_requests` | `requested_role_id` | [[database/schemas/auth#`roles`\|roles]] | Auth & Security |

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
| `employees` | `legal_entity_id` | [[database/schemas/org-structure#`legal_entities`|legal_entities]] | Org Structure |
| `employees` | `avatar_file_id` | [[database/schemas/infrastructure#`file_records`\|file_records]] | Infrastructure |
| `employee_checklist_tasks` | `assigned_to_id` | [[database/schemas/infrastructure#`users`|users]] | Infrastructure |
| `employee_checklist_tasks` | `template_id` | [[database/schemas/core-hr#`checklist_templates`|checklist_templates]] | Core HR |
| `checklist_templates` | `department_id` | [[database/schemas/org-structure#`departments`|departments]] | Org Structure |

## Documents

| Source Table | Column | Target Table | Target Module |
|:------------|:-------|:-------------|:-------------|
| `document_access_logs` | `employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `document_acknowledgements` | `employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `document_acknowledgements` | `acknowledged_by_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `document_templates` | `created_by_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `document_versions` | `uploaded_by_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `documents` | `legal_entity_id` | [[database/schemas/org-structure#`legal_entities`|legal_entities]] | Org Structure |
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
| `biometric_devices` | `legal_entity_id` | [[database/schemas/org-structure#`legal_entities`\|legal_entities]] | Org Structure |
| `biometric_audit_logs` | `biometric_device_id` | [[database/schemas/identity-verification#`biometric_devices`\|biometric_devices]] | Identity Verification |
| `biometric_enrollments` | `biometric_device_id` | [[database/schemas/identity-verification#`biometric_devices`\|biometric_devices]] | Identity Verification |
| `biometric_events` | `biometric_device_id` | [[database/schemas/identity-verification#`biometric_devices`\|biometric_devices]] | Identity Verification |
| `biometric_enrollments` | `employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `biometric_events` | `employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `verification_records` | `employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `verification_evidence_assets` | `file_record_id` | [[database/schemas/infrastructure#`file_records`\|file_records]] | Infrastructure |
| `verification_records` | `agent_id` | [[database/schemas/agent-gateway#`registered_agents`\|registered_agents]] | Agent Gateway |
| `verification_records` | `biometric_device_id` | [[database/schemas/identity-verification#`biometric_devices`\|biometric_devices]] | Identity Verification |
| `verification_evidence_assets` | `agent_id` | [[database/schemas/agent-gateway#`registered_agents`\|registered_agents]] | Agent Gateway |
| `verification_evidence_assets` | `biometric_device_id` | [[database/schemas/identity-verification#`biometric_devices`\|biometric_devices]] | Identity Verification |
| `verification_records` | `requested_by_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `verification_records` | `alert_id` | Nullable — linked alert/notification ID (for on-demand captures triggered from a review case) | Notifications / Shared Platform |

## Infrastructure

| Source Table | Column | Target Table | Target Module |
|:------------|:-------|:-------------|:-------------|
| `tenants` | `subscription_plan_id` | [[database/schemas/shared-platform#`subscription_plans`\|subscription_plans]] | Shared Platform |

## Time Off

| Source Table | Column | Target Table | Target Module |
|:------------|:-------|:-------------|:-------------|
| `time_off_balances_audit` | `employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `time_off_balances_audit` | `attendance_record_id` | [[database/schemas/time-attendance#`attendance_records`\|attendance_records]] | Time & Attendance |
| `time_off_entitlements` | `employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `time_off_policies` | `country_id` | [[database/schemas/infrastructure#`countries`\|countries]] | Infrastructure |
| `time_off_requests` | `employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `time_off_requests` | `approved_by_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `time_off_requests` | `document_file_id` | [[database/schemas/infrastructure#`file_records`\|file_records]] | Infrastructure |

## Org Structure

| Source Table | Column | Target Table | Target Module |
|:------------|:-------|:-------------|:-------------|
| `legal_entities` | `country_id` | [[database/schemas/infrastructure#`countries`|countries]] | Infrastructure |
| `position_access_templates` | `role_id` | [[database/schemas/auth#`roles`\|roles]] | Auth & Security |
| `position_access_templates` | `created_by` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `management_coverage_records` | `owner_position_id` | [[database/schemas/org-structure#`positions`\|positions]] | Org Structure |
| `management_coverage_records` | `covered_position_id` | [[database/schemas/org-structure#`positions`\|positions]] | Org Structure |
| `management_coverage_records` | `covered_department_id` | [[database/schemas/org-structure#`departments`\|departments]] | Org Structure |

## Payroll

| Source Table | Column | Target Table | Target Module |
|:------------|:-------|:-------------|:-------------|
| `employee_allowances` | `employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `employee_pension_enrollments` | `employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `payroll_adjustments` | `employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `payroll_connections` | `legal_entity_id` | [[database/schemas/org-structure#`legal_entities`|legal_entities]] | Org Structure |
| `payroll_runs` | `legal_entity_id` | [[database/schemas/org-structure#`legal_entities`|legal_entities]] | Org Structure |
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
| `succession_plans` | `position_id` | [[database/schemas/org-structure#`positions`\|positions]] | Org Structure |
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
| `legal_holds` | `placed_by_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `legal_holds` | `released_by_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `notification_channels` | `configured_by_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `notification_templates` | `created_by_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `support_tickets` | `created_by_user_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `support_tickets` | `assigned_to_id` | [[developer-platform/database/schema#platform_users|platform_users]] | DevPlatform |
| `support_tickets` | `resolved_by_id` | [[developer-platform/database/schema#platform_users|platform_users]] | DevPlatform |
| `support_ticket_messages` | `sender_user_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `support_ticket_messages` | `sender_platform_user_id` | [[developer-platform/database/schema#platform_users|platform_users]] | DevPlatform |
| `support_ticket_internal_notes` | `author_platform_user_id` | [[developer-platform/database/schema#platform_users|platform_users]] | DevPlatform |
| `support_ticket_events` | `actor_user_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `support_ticket_events` | `actor_platform_user_id` | [[developer-platform/database/schema#platform_users|platform_users]] | DevPlatform |
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
| `feature_flag_overrides` | `granted_by_id` | [[developer-platform/database/schema#platform_users|platform_users]] | DevPlatform |
| `tenant_subscriptions` | `created_by_user_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure; tenant self-service actor |
| `tenant_subscriptions` | `created_by_platform_user_id` | [[developer-platform/database/schema#platform_users|platform_users]] | DevPlatform; platform-operator actor |
| `user_preferences` | `user_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `webhook_endpoints` | `created_by_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `workflow_definitions` | `created_by_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `automation_definitions` | `created_by_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `automation_runs` | `workflow_instance_id` | [[database/schemas/shared-platform#`workflow_instances`\|workflow_instances]] | Shared Platform |
| `workflow_instances` | `initiated_by_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `workflow_instances` | `requester/source/target/subject/actor_tenant_id` | [[database/schemas/infrastructure#`tenants`\|tenants]] | Infrastructure |
| `workflow_step_instances` | `assigned_to_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR; legacy compatibility only |
| `workflow_step_assignments` | `assigned_employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `workflow_step_assignments` | `assigned_user_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `workflow_steps` | `approver_role_id` | [[database/schemas/auth#`roles`\|roles]] | Auth & Security; legacy compatibility only |
| `case_conversations` | `channel_id` | [[database/schemas/wms-chat#`channels`\|channels]] | Work Management Chat |

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
| `position_skill_requirements` | `position_id` | [[database/schemas/org-structure#`positions`\|positions]] | Org Structure |
| `lms_providers` | `created_by_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `skill_assessment_responses` | `employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `skill_assessment_responses` | `file_record_id` | [[database/schemas/infrastructure#`file_records`\|file_records]] | Infrastructure |
| `skill_assessment_responses` | `scored_by_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `skill_categories` | `created_by_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `skill_questions` | `created_by_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |
| `skill_validation_requests` | `employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `skill_validation_requests` | `validator_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `skills` | `created_by_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |

## Time & Attendance

| Source Table | Column | Target Table | Target Module |
|:------------|:-------|:-------------|:-------------|
| `break_records` | `employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `device_sessions` | `employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `device_sessions` | `device_id` | [[database/schemas/agent-gateway#`registered_agents`\|registered_agents]] | Agent Gateway |
| `presence_sessions` | `employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `work_schedules` | `legal_entity_id` | [[database/schemas/org-structure#`legal_entities`\|legal_entities]] | Org Structure |
| `schedule_assignments` | `legal_entity_id` | [[database/schemas/org-structure#`legal_entities`\|legal_entities]] | Org Structure |
| `schedule_assignments` | `work_schedule_id` | [[database/schemas/time-attendance#`work_schedules`\|work_schedules]] | Time & Attendance |
| `schedule_assignments` | `department_id` | [[database/schemas/org-structure#`departments`\|departments]] | Org Structure |
| `schedule_assignments` | `position_id` | [[database/schemas/org-structure#`positions`\|positions]] | Org Structure |
| `schedule_assignments` | `employee_id` | [[database/schemas/core-hr#`employees`\|employees]] | Core HR |
| `clock_in_late_deduction_rules` | `time_off_type_id` | [[database/schemas/time_off#`time_off_types`\|time_off_types]] | Time Off |
| `work_schedule_holidays` | `work_schedule_id` | [[database/schemas/time-attendance#`work_schedules`\|work_schedules]] | Time & Attendance |
| `work_schedule_holidays` | `public_holiday_id` | [[database/schemas/time-attendance#`public_holidays`\|public_holidays]] | Time & Attendance |
| `work_schedule_holidays` | `created_by_id` | [[database/schemas/infrastructure#`users`\|users]] | Infrastructure |

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
| `workspace_teams_links` | `workspace_id` | `workspaces` | Work Management.Foundation |
| `workspace_teams_links` | `created_by_id` | `users` | Infrastructure |
| `teams_member_sync_status` | `workspace_teams_link_id` | `workspace_teams_links` | Work Management.Foundation |
| `teams_member_sync_status` | `user_id` | `users` | Infrastructure |

## Work Management.ProjectManagement

| Source Table | Column | Target Table | Target Module |
|:------------|:-------|:-------------|:-------------|
| `projects` | `tenant_id` | `tenants` | Infrastructure |
| `projects` | `workspace_id` | `workspaces` | Work Management.Foundation |
| `projects` | `lead_id` | `users` | Infrastructure |
| `project_workspaces` | `project_id` | `projects` | Work Management.ProjectManagement (Phase 2 reference) |
| `project_workspaces` | `workspace_id` | `workspaces` | Work Management.Foundation (Phase 2 reference) |
| `project_workspaces` | `tenant_id` | `tenants` | Infrastructure (Phase 2 reference) |
| `project_workspaces` | `linked_by_id` | `users` | Infrastructure (Phase 2 reference) |
| `project_member_invitations` | `project_id` | `projects` | Work Management.ProjectManagement |
| `project_member_invitations` | `invited_user_id` | `users` | Infrastructure |
| `project_member_invitations` | `invited_employee_id` | `employees` | Core HR |
| `project_member_invitations` | `invited_by_id` | `users` | Infrastructure |
| `project_link_invitations` | `source_project_id` | `projects` | Work Management.ProjectManagement |
| `project_link_invitations` | `target_project_id` | `projects` | Work Management.ProjectManagement |
| `project_link_invitations` | `invited_project_admin_id` | `users` | Infrastructure |
| `project_link_invitations` | `invited_by_id` | `users` | Infrastructure |
| `project_links` | `source_project_id` | `projects` | Work Management.ProjectManagement |
| `project_links` | `target_project_id` | `projects` | Work Management.ProjectManagement |
| `project_links` | `created_by_id` | `users` | Infrastructure |
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
| `ai_action_jobs` | `tag_execution_id` | `ide_tag_executions` | IDE Extension (Phase 2) |
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

## IDE Extension (Phase 2)

| Source Table | Column | Target Table | Target Module |
|:------------|:-------|:-------------|:-------------|
| `ide_extension_installs` | `user_id` | `users` | Infrastructure |
| `ide_extension_installs` | `tenant_id` | `tenants` | Infrastructure |
| `ide_extension_installs` | `workspace_id` | `workspaces` | Work Management.Foundation |
| `ide_sessions` | `install_id` | `ide_extension_installs` | IDE Extension (Phase 2) |
| `ide_sessions` | `active_project_id` | `projects` | Work Management.ProjectManagement |
| `ide_tag_executions` | `session_id` | `ide_sessions` | IDE Extension (Phase 2) |
| `ide_context_links` | `entity_id` | tasks / projects / sprints / documents (polymorphic) | varies |
| `ide_chat_threads` | `channel_id` | `channels` | Work Management.Chat |
| `ide_chat_threads` | `context_task_id` | `tasks` | Work Management.TaskManagement |

---

## Migration Order

Based on FK dependencies, modules should be migrated in this order:

```
1. infrastructure (tenants, users, countries, file_records)
2. auth (roles, permissions, sessions)
4. core-hr (employees - the central hub)
5. configuration (tenant_settings, monitoring_toggles)
6. agent-gateway (registered_agents)
7. All HR/WFI Phase 1 modules (can be parallel):
   - time_off, calendar, time-attendance
   - activity-monitoring, discrepancy-engine, exception-engine
   - identity-verification, productivity-analytics
   - shared-platform, notifications
8. Work Management Phase 1 (ordered by FK dependency):
   - wms-project-management (workspaces -> projects -> epics/milestones)
   - wms-task-management (tasks -> boards -> board_columns)
   - wms-planning (sprints -> sprint_backlog_items -> sprint_daily_snapshots -> roadmaps)
   - wms-chat (channels -> messages -> ai_action_jobs)
   - wms-collaboration (document extensions -> wiki_pages -> task_documents)
   - wms-analytics (dashboards -> dashboard_shares)
   - wms-integrations (repositories -> code_activity_events -> task_automation_rules)
   - optional Microsoft Teams sync additions (external_account_connections -> microsoft_graph_tokens -> workspace_teams_links -> channel_teams_links -> teams_message_sync_state)
9. IDE Extension (Phase 2; depends on workspaces, projects, tasks, channels):
   - ide_extension_installs -> ide_sessions -> ide_tag_executions
   - ide_context_links, ide_chat_threads
   - agent_install_entitlements, agent_install_jobs (Agent Gateway additions)
10. Phase 2 modules (after Phase 1 is stable):
    - payroll, performance, skills
    - hr-documents (Phase 2 additions), grievance, expense
    - reporting-engine
```

## Related

- [[database/schema-catalog|Schema Catalog]]
- [[database/migration-patterns|Migration Patterns]]
- [[database/README|Database Documentation]]
