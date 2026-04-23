# Schema Catalog

Central index of all database tables across ONEVO modules. This is the **single source of truth** for database schema design. When building EF Core entities, reference these definitions.

> **Important:** The `overview.md` files inside each module also show table definitions for contextual reference. The canonical schema lives here. If they conflict, update the module overview to match this catalog.

---

## Summary

- **Total Tables:** 175 (Phase 1)
- **Modules:** 22 + Developer Platform
- **Phase 1 Tables:** 133
- **Phase 2 Tables:** 42

> **Note:** Activity Monitoring (11 tables), Productivity Analytics (5), Shared Platform (33) include new WMS integration tables added in Phase 1. Skills Phase 2 count corrected to 10 (2 duplicate rows removed). See [[docs/wms-integration-analysis|WMS Integration Analysis]] for change history. Developer Platform adds 5 Phase 1 tables + 1 Phase 2 table (see section below). `tenants.status` enum updated to include `'provisioning'`.

## Hub Tables

These tables are referenced by many others — design changes here have wide impact:

| Table | Module | Referenced By |
|:------|:-------|:-------------|
| [[database/schemas/infrastructure#`tenants`\|tenants]] | Infrastructure | 102 tables |
| [[database/schemas/core-hr#`employees`\|employees]] | Core HR | 71 tables |
| [[database/schemas/infrastructure#`users`\|users]] | Infrastructure | 56 tables |
| [[database/schemas/infrastructure#`file_records`\|file_records]] | Infrastructure | 10 tables |
| [[database/schemas/agent-gateway#`registered_agents`\|registered_agents]] | Agent Gateway | 6 tables |
| [[database/schemas/skills#`skills`\|skills]] | Skills & Learning | 6 tables |
| [[database/schemas/org-structure#`departments`\|departments]] | Org Structure | 5 tables |
| [[database/schemas/org-structure#`legal_entities`\|legal_entities]] | Org Structure | 5 tables |
| [[database/schemas/auth#`roles`\|roles]] | Auth & Security | 5 tables |
| [[database/schemas/skills#`courses`\|courses]] | Skills & Learning | 4 tables |
| [[database/schemas/performance#`review_cycles`\|review_cycles]] | Performance | 4 tables |
| [[database/schemas/infrastructure#`countries`\|countries]] | Infrastructure | 4 tables |
| [[database/schemas/leave#`leave_types`\|leave_types]] | Leave | 4 tables |
| [[database/schemas/identity-verification#`biometric_devices`\|biometric_devices]] | Identity Verification | 3 tables |
| [[database/schemas/documents#`document_categories`\|document_categories]] | Documents | 3 tables |
| [[database/schemas/payroll#`payroll_runs`\|payroll_runs]] | Payroll | 3 tables |
| [[database/schemas/shared-platform#`subscription_plans`\|subscription_plans]] | Shared Platform | 3 tables |

---

## Phase 1 Modules

### [[database/schemas/infrastructure|Infrastructure]] (4 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `countries` | 5 | — |
| `file_records` | 8 | — |
| `tenants` | 9 | subscription_plan_id→subscription_plans |
| `users` | 9 | — |

### [[database/schemas/auth|Auth & Security]] (9 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `audit_logs` | 11 | tenant_id→tenants, user_id→users |
| `feature_access_grants` | 9 | tenant_id→tenants, granted_by→users |
| `gdpr_consent_records` | 7 | tenant_id→tenants, user_id→users |
| `permissions` | 4 | — |
| `role_permissions` | 2 | — |
| `roles` | 6 | tenant_id→tenants |
| `sessions` | 9 | user_id→users, tenant_id→tenants |
| `user_permission_overrides` | 8 | tenant_id→tenants, user_id→users, granted_by→users |
| `user_roles` | 4 | user_id→users, assigned_by→users |

### [[database/schemas/org-structure|Org Structure]] (9 tables)

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

> These 5 tables from the Skills & Learning module are built in Phase 1 to support skill taxonomy, job skill requirements, and employee skill profiles. The remaining 10 Skills tables (courses, LMS, assessments, development plans) are Phase 2.

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `employee_skills` | 11 | tenant_id→tenants, employee_id→employees, validated_by_id→employees |
| `job_skill_requirements` | 7 | tenant_id→tenants, job_family_id→job_families |
| `skill_categories` | 7 | tenant_id→tenants, created_by_id→users |
| `skill_validation_requests` | 11 | tenant_id→tenants, employee_id→employees, validator_id→employees |
| `skills` | 9 | tenant_id→tenants, category_id→skill_categories, created_by_id→users |

### [[database/schemas/leave|Leave]] (5 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `leave_balances_audit` | 9 | employee_id→employees |
| `leave_entitlements` | 9 | employee_id→employees |
| `leave_policies` | 13 | tenant_id→tenants, country_id→countries, job_level_id→job_levels |
| `leave_requests` | 14 | employee_id→employees, approved_by_id→users, document_file_id→file_records |
| `leave_types` | 9 | tenant_id→tenants |

### [[database/schemas/calendar|Calendar]] (1 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `calendar_events` | 14 | created_by_id→users |

### [[database/schemas/configuration|Configuration]] (6 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `app_allowlist_audit` | 8 | tenant_id→tenants, changed_by_id→users |
| `app_allowlists` | 10 | tenant_id→tenants, set_by_id→users |
| `employee_monitoring_overrides` | 14 | tenant_id→tenants, employee_id→employees, set_by_id→users |
| `integration_connections` | 7 | tenant_id→tenants |
| `monitoring_feature_toggles` | 11 | tenant_id→tenants |
| `tenant_settings` | 12 | tenant_id→tenants |

### [[database/schemas/agent-gateway|Agent Gateway]] (4 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `agent_commands` | 12 | tenant_id→tenants, requested_by→users |
| `agent_health_logs` | 8 | tenant_id→tenants |
| `agent_policies` | 7 | tenant_id→tenants |
| `registered_agents` | 12 | tenant_id→tenants, employee_id→employees |

### [[database/schemas/activity-monitoring|Activity Monitoring]] (11 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `activity_daily_summary` | 19 | tenant_id→tenants, employee_id→employees |
| `activity_raw_buffer` | 5 | tenant_id→tenants, agent_device_id→registered_agents |
| `activity_snapshots` | 11 | tenant_id→tenants, employee_id→employees |
| `application_categories` | 7 | tenant_id→tenants, created_by_id→users |
| `application_usage` | 12 | tenant_id→tenants, employee_id→employees |
| `browser_activity` | 9 | tenant_id→tenants, employee_id→employees |
| `device_tracking` | 8 | tenant_id→tenants, employee_id→employees |
| `discrepancy_events` | 13 | tenant_id→tenants, employee_id→employees |
| `meeting_sessions` | 9 | tenant_id→tenants, employee_id→employees |
| `screenshots` | 7 | tenant_id→tenants, employee_id→employees, file_record_id→file_records |
| `wms_daily_time_logs` | 8 | tenant_id→tenants, employee_id→employees |

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
| `roster_periods` | 8 | tenant_id→tenants, created_by_id→users |
| `shift_assignments` | 7 | tenant_id→tenants, employee_id→employees, shift_id→shifts |
| `shifts` | 9 | tenant_id→tenants |
| `work_schedules` | 5 | tenant_id→tenants |

### [[database/schemas/exception-engine|Exception Engine]] (5 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `alert_acknowledgements` | 6 | acknowledged_by_id→users |
| `escalation_chains` | 8 | tenant_id→tenants |
| `exception_alerts` | 10 | tenant_id→tenants, employee_id→employees |
| `exception_rules` | 12 | tenant_id→tenants, created_by_id→users |
| `exception_schedules` | 9 | tenant_id→tenants |

### [[database/schemas/identity-verification|Identity Verification]] (6 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `biometric_audit_logs` | 6 | tenant_id→tenants |
| `biometric_devices` | 10 | tenant_id→tenants, location_id→departments |
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
| `wms_productivity_snapshots` | 14 | tenant_id→tenants, employee_id→employees |
| `workforce_snapshot` | 11 | tenant_id→tenants |

### [[database/schemas/shared-platform|Shared Platform]] (33 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `api_keys` | 11 | tenant_id→tenants, created_by_id→users |
| `approval_actions` | 8 | actor_id→employees, delegated_to_id→employees |
| `compliance_exports` | 10 | tenant_id→tenants, requested_by_id→users, target_user_id→users |
| `escalation_rules` | 11 | tenant_id→tenants, escalate_to_role_id→roles, created_by_id→users |
| `feature_flags` | 8 | tenant_id→tenants, toggled_by_id→users |
| `hardware_terminals` | 11 | tenant_id→tenants |
| `legal_holds` | 9 | tenant_id→tenants, placed_by_id→users, released_by_id→users |
| `notification_channels` | 9 | tenant_id→tenants, configured_by_id→users |
| `notification_templates` | 12 | tenant_id→tenants, created_by_id→users |
| `payment_methods` | 10 | tenant_id→tenants |
| `plan_features` | 5 | — |
| `rate_limit_rules` | 7 | tenant_id→tenants |
| `refresh_tokens` | 9 | user_id→users, tenant_id→tenants |
| `retention_policies` | 9 | tenant_id→tenants, created_by_id→users |
| `scheduled_tasks` | 9 | tenant_id→tenants |
| `signalr_connections` | 9 | user_id→users, tenant_id→tenants |
| `sso_providers` | 12 | tenant_id→tenants |
| `subscription_invoices` | 10 | tenant_id→tenants |
| `subscription_plans` | 11 | — |
| `system_settings` | 6 | updated_by_id→users |
| `tenant_branding` | 9 | tenant_id→tenants, logo_file_id→file_records, updated_by_id→users |
| `tenant_feature_flags` | 6 | tenant_id→tenants, overridden_by_id→users |
| `tenant_subscriptions` | 11 | tenant_id→tenants, created_by_id→users |
| `user_preferences` | 6 | user_id→users, tenant_id→tenants |
| `webhook_deliveries` | 9 | tenant_id→tenants |
| `webhook_endpoints` | 8 | tenant_id→tenants, created_by_id→users |
| `workflow_definitions` | 11 | tenant_id→tenants, created_by_id→users |
| `workflow_instances` | 10 | tenant_id→tenants, initiated_by_id→employees |
| `workflow_step_instances` | 8 | assigned_to_id→employees |
| `workflow_steps` | 9 | approver_role_id→roles |
| `bridge_api_keys` | 11 | tenant_id→tenants, created_by_id→users |
| `wms_role_mappings` | 7 | tenant_id→tenants, onevo_role_id→roles |
| `wms_tenant_links` | 12 | tenant_id→tenants, bridge_api_key_id→bridge_api_keys |

### [[database/schemas/notifications|Notifications]] (2 tables)

> `notification_templates` and `notification_channels` are physically housed in the shared `AppDbContext` and counted under Shared Platform above. They are listed here for module-level reference.

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `notification_templates` | 7 | tenant_id→tenants |
| `notification_channels` | 6 | tenant_id→tenants |

## Phase 2 Modules

> These tables are designed but not built in Phase 1. Schema is defined here so Phase 1 tables can account for future FK dependencies.

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

> The 5 core skill tables (skill_categories, skills, job_skill_requirements, employee_skills, skill_validation_requests) are built in Phase 1 — see Skills Core section above.

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `course_enrollments` | 10 | tenant_id→tenants, employee_id→employees, assigned_by_id→employees |
| `course_skill_tags` | 4 | tenant_id→tenants |
| `courses` | 11 | tenant_id→tenants, created_by_id→users |
| `development_plan_items` | 9 | tenant_id→tenants |
| `development_plans` | 9 | tenant_id→tenants, employee_id→employees, created_by_id→users |
| `employee_certifications` | 14 | tenant_id→tenants, employee_id→employees, certificate_file_record_id→file_records |
| `lms_providers` | 9 | tenant_id→tenants, created_by_id→users |
| `skill_assessment_responses` | 10 | tenant_id→tenants, employee_id→employees, file_record_id→file_records |
| `skill_question_options` | 6 | tenant_id→tenants |
| `skill_questions` | 11 | tenant_id→tenants, created_by_id→users |

### [[database/schemas/documents|Documents]] (6 tables)

| Table | Columns | Key FKs |
|:------|:--------|:--------|
| `document_access_logs` | 7 | tenant_id→tenants, employee_id→employees |
| `document_acknowledgements` | 7 | employee_id→employees, acknowledged_by_id→users |
| `document_categories` | 8 | tenant_id→tenants |
| `document_templates` | 10 | tenant_id→tenants, created_by_id→users |
| `document_versions` | 10 | uploaded_by_id→users |
| `documents` | 11 | tenant_id→tenants, legal_entity_id→legal_entities, employee_id→employees |

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

> Tables for the internal developer console (`console.onevo.io`). These live in their own schema scope and are not tenant-scoped. See `developer-platform/backend/admin-api-layer.md` for context.

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
| `platform_api_keys` | Platform API keys *(Phase 2)* |

---

## Known Issues

- **Escalation boundary:** Two escalation systems exist — `escalation_rules` (Shared Platform) handles workflow SLA timeouts (e.g., leave pending >48h → escalate to manager's manager); `escalation_chains` (Exception Engine) handles alert routing for system-detected anomalies (e.g., GPS mismatch → alert security team). These are distinct concerns and not interchangeable.

## Related

- [[database/README|Database Documentation]]
- [[database/cross-module-relationships|Cross-Module Relationships]]
- [[database/migration-patterns|Migration Patterns]]
- [[database/performance|Performance]]