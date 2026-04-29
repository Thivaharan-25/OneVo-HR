# ONEVO — Unified Single-DB Entity Map
# ONEVO-HRMS + ONEVO-WorkSync — One PostgreSQL Schema

**Architecture:** Single unified PostgreSQL database — no bridge API, no microservice split
**Multi-tenant:** `tenants` → `workspaces` → `workspace_members`
**RBAC:** Hybrid — HRMS granular permissions (tenant-level) + workspace roles (WMS-level)
**Total Tables:** ~287 across 38 modules
**Last Updated:** 2026-04-29

---

## Scoping Rules

| Data Domain | Scope Key | Examples |
|---|---|---|
| HR data (employees, leave, payroll, attendance) | `tenant_id` | Core HR, Payroll, Leave |
| WMS data (projects, tasks, chat) | `workspace_id` | Projects, Tasks, Chat |
| User identity | `tenant_id` (belongs to tenant, member of many workspaces) | `users`, `workspace_members` |
| Merged entities | both nullable | `audit_logs`, `calendar_events`, `overtime_records` |

---

## Merge Decisions

| Merged Into | Sources | Key Addition |
|---|---|---|
| `users` | HRMS `users` + WMS `AUTH_ACCOUNT` | unified identity |
| `sessions` | HRMS `sessions` + WMS `AUTH_SESSION` | `workspace_id` nullable |
| `audit_logs` | HRMS `audit_logs` + WMS `AUDIT_LOG` + `ACTIVITY_LOG` | `workspace_id` nullable |
| `calendar_events` | HRMS `calendar_events` + WMS `CALENDAR_EVENT` | unified `event_type` enum |
| `overtime_records` | HRMS `overtime_records` + WMS `OVERTIME_ENTRY` | `source` col + nullable `task_id` |
| `file_assets` + `file_versions` | HRMS `file_records` (dropped) + WMS `FILE_ASSET`/`FILE_VERSION` | WMS versioned approach wins |
| `teams` + `team_members` | HRMS `teams` (tenant) + WMS `TEAM` (workspace) | `workspace_id` nullable |
| `notifications` (full stack) | HRMS templates/channels + WMS delivery stack | all kept, one module |
| `skills` (full HRMS stack) | HRMS wins; WMS `SKILL`/`USER_SKILL` mapped to HRMS tables | `workspace_id` nullable on `skills` |

**Removed (single-DB no longer needed):** `bridge_clients`, `wms_tenant_links`, `wms_role_mappings`, `bridge_api_keys`

---

## Architecture Diagram

```
tenants
  └── workspaces (many per tenant)
        └── workspace_members (users ↔ workspaces, many-to-many)
              └── workspace_roles (Admin / Member / Viewer per workspace)

users (tenant_id → tenants)
  ├── employee profile (employees → users)
  ├── workspace_members (user_id + workspace_id)
  ├── user_roles (HRMS tenant-level RBAC)
  └── sessions

HRMS scope (tenant_id):        WMS scope (workspace_id):
  employees                      workspaces
  leave_requests                 projects → tasks
  payroll_runs                   sprints → boards
  attendance_records             channels → messages
  activity monitoring            okr objectives
  exception / discrepancy        chat ai
  ...                            ...
```

---

## 1. FOUNDATION

### `tenants` — Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `name` | varchar(200) | Company name |
| `slug` | varchar(100) | UNIQUE, URL-safe |
| `industry_profile` | varchar(30) | office_it / manufacturing / retail / healthcare / custom |
| `status` | varchar(20) | trial / active / suspended / cancelled |
| `subscription_plan_id` | uuid | FK → subscription_plans |
| `settings_json` | jsonb | Tenant-level config |
| `created_at` | timestamptz | |
| `updated_at` | timestamptz | |

---

### `users` — Phase 1 — MERGED (HRMS users + WMS AUTH_ACCOUNT)

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `tenant_id` | uuid | FK → tenants |
| `email` | varchar(255) | UNIQUE per tenant |
| `password_hash` | varchar(255) | bcrypt |
| `is_active` | boolean | |
| `email_verified` | boolean | |
| `full_name` | varchar(255) | display name |
| `avatar_url` | varchar(500) | |
| `phone` | varchar(30) | |
| `timezone` | varchar(50) | |
| `locale` | varchar(10) | |
| `last_login_at` | timestamptz | |
| `created_at` | timestamptz | |
| `updated_at` | timestamptz | |

---

### `workspaces` — Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `tenant_id` | uuid | FK → tenants |
| `name` | varchar(200) | |
| `slug` | varchar(100) | UNIQUE per tenant |
| `description` | text | |
| `owner_id` | uuid | FK → users |
| `icon_url` | varchar(500) | |
| `is_active` | boolean | |
| `created_at` | timestamptz | |
| `updated_at` | timestamptz | |

---

### `workspace_members` — Phase 1 (junction: users ↔ workspaces)

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `workspace_id` | uuid | FK → workspaces |
| `user_id` | uuid | FK → users |
| `workspace_role_id` | uuid | FK → workspace_roles |
| `joined_at` | timestamptz | |
| `invited_by` | uuid | FK → users, nullable |
| `is_active` | boolean | |

UNIQUE: `(workspace_id, user_id)`

---

### `workspace_roles` — Phase 1 (WMS-level roles: Admin/Member/Viewer)

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `workspace_id` | uuid | FK → workspaces |
| `name` | varchar(50) | Admin / Member / Viewer / custom |
| `permissions_json` | jsonb | WMS feature permissions |
| `is_system` | boolean | |
| `created_at` | timestamptz | |

---

### `workspace_invites` — Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `workspace_id` | uuid | FK → workspaces |
| `email` | varchar(255) | |
| `workspace_role_id` | uuid | FK → workspace_roles |
| `invited_by` | uuid | FK → users |
| `token_hash` | varchar(255) | |
| `expires_at` | timestamptz | |
| `accepted_at` | timestamptz | nullable |

---

### `workspace_billing` — Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `workspace_id` | uuid | FK → workspaces |
| `plan` | varchar(30) | free / pro / enterprise |
| `billing_cycle` | varchar(10) | monthly / annual |
| `is_active` | boolean | |
| `next_billing_at` | timestamptz | |

---

### `user_preferences` — Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `user_id` | uuid | FK → users, UNIQUE |
| `theme` | varchar(20) | light / dark / system |
| `language` | varchar(10) | |
| `timezone` | varchar(50) | |
| `notification_prefs_json` | jsonb | per-channel preferences |

---

### `countries` — Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `name` | varchar(100) | |
| `code` | varchar(3) | ISO 3166-1 alpha-3 |
| `phone_code` | varchar(10) | |
| `currency_code` | varchar(3) | |

---

## 2. AUTH & SECURITY

### `roles` — Phase 1 (HRMS tenant-level HR roles)

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `tenant_id` | uuid | FK → tenants |
| `name` | varchar(50) | HR Manager / CEO / Employee |
| `description` | varchar(255) | |
| `is_system` | boolean | system roles cannot be deleted |
| `created_at` | timestamptz | |

---

### `permissions` — Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `code` | varchar(50) | e.g., employees:read, leave:approve |
| `description` | varchar(255) | |
| `module` | varchar(50) | owning module |

---

### `role_permissions` — Phase 1

| Column | Type |
|---|---|
| `role_id` | uuid FK → roles |
| `permission_id` | uuid FK → permissions |

PK: `(role_id, permission_id)`

---

### `user_roles` — Phase 1

| Column | Type | Notes |
|---|---|---|
| `user_id` | uuid | FK → users |
| `role_id` | uuid | FK → roles |
| `assigned_at` | timestamptz | |
| `assigned_by` | uuid | FK → users |

PK: `(user_id, role_id)`

---

### `user_permission_overrides` — Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `tenant_id` | uuid | FK → tenants |
| `user_id` | uuid | FK → users |
| `permission_id` | uuid | FK → permissions |
| `grant_type` | varchar(10) | grant / revoke |
| `reason` | varchar(255) | |
| `granted_by` | uuid | FK → users |
| `created_at` | timestamptz | |

---

### `sessions` — Phase 1 — MERGED (HRMS sessions + WMS AUTH_SESSION)

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `user_id` | uuid | FK → users |
| `tenant_id` | uuid | FK → tenants |
| `workspace_id` | uuid | FK → workspaces, nullable |
| `token_hash` | varchar(255) | |
| `ip_address` | varchar(45) | |
| `user_agent` | varchar(500) | |
| `started_at` | timestamptz | |
| `last_activity_at` | timestamptz | |
| `expires_at` | timestamptz | |
| `is_revoked` | boolean | |

---

### `audit_logs` — Phase 1 — MERGED (HRMS + WMS AUDIT_LOG + ACTIVITY_LOG)

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `tenant_id` | uuid | FK → tenants |
| `workspace_id` | uuid | FK → workspaces, nullable (null = HR-only action) |
| `user_id` | uuid | FK → users, nullable (system actions) |
| `action` | varchar(100) | e.g., task.created, employee.updated |
| `resource_type` | varchar(50) | Employee / Task / LeaveRequest |
| `resource_id` | uuid | |
| `old_values_json` | jsonb | |
| `new_values_json` | jsonb | |
| `ip_address` | varchar(45) | |
| `correlation_id` | uuid | |
| `created_at` | timestamptz | |

---

### `feature_access_grants` — Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `tenant_id` | uuid | FK → tenants |
| `grantee_type` | varchar(10) | role / employee |
| `grantee_id` | uuid | polymorphic (roles.id or employees.id) |
| `module` | varchar(50) | leave / payroll / performance |
| `is_enabled` | boolean | |
| `granted_by` | uuid | FK → users |
| `created_at` | timestamptz | |
| `updated_at` | timestamptz | |

---

### `gdpr_consent_records` — Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `tenant_id` | uuid | FK → tenants |
| `user_id` | uuid | FK → users |
| `consent_type` | varchar(50) | data_processing / biometric / monitoring / marketing |
| `consented` | boolean | |
| `consented_at` | timestamptz | |
| `ip_address` | varchar(45) | |

---

### `auth_devices` — Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `user_id` | uuid | FK → users |
| `name` | varchar(100) | |
| `device_type` | varchar(30) | mobile / desktop / tablet |
| `fingerprint_hash` | varchar(255) | |
| `is_trusted` | boolean | |
| `last_seen_at` | timestamptz | |
| `created_at` | timestamptz | |

---

### `auth_providers` — Phase 1 (OAuth/SSO)

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `user_id` | uuid | FK → users |
| `provider` | varchar(30) | google / microsoft / github |
| `provider_user_id` | varchar(255) | |
| `is_active` | boolean | |
| `created_at` | timestamptz | |

---

### `mfa_configs` — Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `user_id` | uuid | FK → users, UNIQUE |
| `method` | varchar(20) | totp / sms / email |
| `secret_hash` | varchar(255) | |
| `is_enabled` | boolean | |
| `verified_at` | timestamptz | |
| `backup_codes_hash` | jsonb | hashed backup codes |

---

### `password_reset_tokens` — Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `user_id` | uuid | FK → users |
| `token_hash` | varchar(255) | |
| `expires_at` | timestamptz | |
| `used_at` | timestamptz | nullable |

---

### `access_policies` — Phase 2

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `workspace_id` | uuid | FK → workspaces |
| `policy_type` | varchar(30) | ip_allowlist / session_timeout / sso_required |
| `config_json` | jsonb | |
| `is_active` | boolean | |
| `created_at` | timestamptz | |

---

## 3. ORG STRUCTURE

### `departments` — Phase 1 (HRMS, tenant-scoped)

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `tenant_id` | uuid | FK → tenants |
| `name` | varchar(100) | |
| `code` | varchar(20) | |
| `parent_department_id` | uuid | FK → departments, nullable |
| `head_employee_id` | uuid | FK → employees, nullable |
| `legal_entity_id` | uuid | FK → legal_entities, nullable |
| `is_active` | boolean | |
| `created_at` | timestamptz | |

---

### `workspace_groups` — Phase 1 (WMS dept equivalent, workspace-scoped)

> WMS grouping within a workspace. Optionally linked to an HR department.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `workspace_id` | uuid | FK → workspaces |
| `name` | varchar(100) | |
| `department_id` | uuid | FK → departments, nullable |
| `lead_user_id` | uuid | FK → users, nullable |
| `description` | text | |
| `created_at` | timestamptz | |

---

### `workspace_group_members` — Phase 1

| Column | Type |
|---|---|
| `workspace_group_id` | uuid FK → workspace_groups |
| `user_id` | uuid FK → users |
| `joined_at` | timestamptz |

PK: `(workspace_group_id, user_id)`

---

### `teams` — Phase 1 — MERGED (HRMS org teams + WMS workspace teams)

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `tenant_id` | uuid | FK → tenants |
| `workspace_id` | uuid | FK → workspaces, nullable (null = HR org team) |
| `name` | varchar(100) | |
| `description` | text | |
| `department_id` | uuid | FK → departments, nullable |
| `lead_user_id` | uuid | FK → users, nullable |
| `created_at` | timestamptz | |

---

### `team_members` — Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `team_id` | uuid | FK → teams |
| `user_id` | uuid | FK → users |
| `role` | varchar(30) | lead / member |
| `joined_at` | timestamptz | |

UNIQUE: `(team_id, user_id)`

---

### `job_titles` — Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `tenant_id` | uuid | FK → tenants |
| `name` | varchar(100) | |
| `job_family_id` | uuid | FK → job_families, nullable |
| `job_level_id` | uuid | FK → job_levels, nullable |
| `is_active` | boolean | |

---

### `job_families` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `tenant_id` | uuid FK → tenants |
| `name` | varchar(100) |
| `description` | text |

---

### `job_levels` — Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `tenant_id` | uuid | FK → tenants |
| `name` | varchar(50) | L1 / L2 / Senior / Principal |
| `rank` | int | ordering |

---

### `legal_entities` — Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `tenant_id` | uuid | FK → tenants |
| `name` | varchar(200) | |
| `country_id` | uuid | FK → countries |
| `registration_number` | varchar(100) | |
| `is_active` | boolean | |

---

### `office_locations` — Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `tenant_id` | uuid | FK → tenants |
| `legal_entity_id` | uuid | FK → legal_entities |
| `name` | varchar(100) | |
| `address_line1` | varchar(255) | |
| `city` | varchar(100) | |
| `country_id` | uuid | FK → countries |
| `timezone` | varchar(50) | |
| `is_headquarter` | boolean | |

---

### `department_cost_centers` — Phase 2

| Column | Type |
|---|---|
| `id` | uuid PK |
| `department_id` | uuid FK → departments |
| `cost_center_code` | varchar(50) |
| `name` | varchar(100) |
| `is_primary` | boolean |

---

## 4. CORE HR

### `employees` — Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `tenant_id` | uuid | FK → tenants |
| `user_id` | uuid | FK → users, UNIQUE per tenant |
| `employee_code` | varchar(50) | UNIQUE per tenant |
| `first_name` | varchar(100) | |
| `last_name` | varchar(100) | |
| `preferred_name` | varchar(100) | nullable |
| `date_of_birth` | date | |
| `gender` | varchar(20) | |
| `nationality` | varchar(3) | ISO country code |
| `national_id` | varchar(50) | |
| `job_title_id` | uuid | FK → job_titles |
| `department_id` | uuid | FK → departments |
| `office_location_id` | uuid | FK → office_locations |
| `manager_id` | uuid | FK → employees, nullable |
| `employment_type` | varchar(30) | full_time / part_time / contract |
| `hire_date` | date | |
| `probation_end_date` | date | nullable |
| `termination_date` | date | nullable |
| `status` | varchar(20) | active / on_leave / terminated |
| `created_at` | timestamptz | |
| `updated_at` | timestamptz | |

---

### `employee_addresses` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `employee_id` | uuid FK → employees |
| `type` | varchar(20) — home / mailing / emergency |
| `address_line1` | varchar(255) |
| `address_line2` | varchar(255) |
| `city` | varchar(100) |
| `state` | varchar(100) |
| `country_id` | uuid FK → countries |
| `postal_code` | varchar(20) |
| `is_current` | boolean |

---

### `employee_bank_details` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `employee_id` | uuid FK → employees |
| `bank_name` | varchar(100) |
| `account_number_encrypted` | text |
| `routing_number` | varchar(50) |
| `account_type` | varchar(20) |
| `is_primary` | boolean |

---

### `employee_custom_fields` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `tenant_id` | uuid FK → tenants |
| `employee_id` | uuid FK → employees |
| `field_key` | varchar(100) |
| `field_value` | text |

---

### `employee_dependents` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `employee_id` | uuid FK → employees |
| `name` | varchar(200) |
| `relationship` | varchar(30) |
| `date_of_birth` | date |
| `national_id` | varchar(50) |

---

### `employee_emergency_contacts` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `employee_id` | uuid FK → employees |
| `name` | varchar(200) |
| `relationship` | varchar(30) |
| `phone` | varchar(30) |
| `is_primary` | boolean |

---

### `employee_lifecycle_events` — Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `employee_id` | uuid | FK → employees |
| `event_type` | varchar(30) | hire / promotion / transfer / termination |
| `effective_date` | date | |
| `details_json` | jsonb | |
| `created_by` | uuid | FK → users |
| `created_at` | timestamptz | |

---

### `employee_qualifications` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `employee_id` | uuid FK → employees |
| `qualification_type` | varchar(50) — degree / diploma / certificate |
| `institution` | varchar(200) |
| `field_of_study` | varchar(200) |
| `grade` | varchar(50) |
| `completed_year` | int |

---

### `employee_salary_history` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `employee_id` | uuid FK → employees |
| `effective_date` | date |
| `salary_amount` | numeric(15,2) |
| `currency_code` | varchar(3) |
| `reason` | varchar(100) |
| `approved_by` | uuid FK → users |

---

### `employee_work_history` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `employee_id` | uuid FK → employees |
| `company_name` | varchar(200) |
| `job_title` | varchar(100) |
| `start_date` | date |
| `end_date` | date nullable |
| `description` | text |

---

### `onboarding_templates` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `tenant_id` | uuid FK → tenants |
| `name` | varchar(100) |
| `department_id` | uuid FK → departments nullable |
| `job_title_id` | uuid FK → job_titles nullable |
| `is_active` | boolean |

---

### `onboarding_tasks` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `template_id` | uuid FK → onboarding_templates |
| `employee_id` | uuid FK → employees nullable |
| `title` | varchar(255) |
| `description` | text |
| `due_days_after_hire` | int |
| `assigned_to_role_id` | uuid FK → roles nullable |
| `status` | varchar(20) — pending/done |
| `completed_at` | timestamptz nullable |

---

### `offboarding_records` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `employee_id` | uuid FK → employees |
| `exit_date` | date |
| `reason` | varchar(100) |
| `exit_interview_notes` | text |
| `clearance_status_json` | jsonb |
| `created_by` | uuid FK → users |
| `created_at` | timestamptz |

---

## 5. WORKFORCE PRESENCE

### `work_schedules` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `tenant_id` | uuid FK → tenants |
| `name` | varchar(100) |
| `timezone` | varchar(50) |
| `work_days_json` | jsonb — {mon:true, tue:true, ...} |
| `daily_hours` | numeric(4,2) |
| `is_default` | boolean |

---

### `shifts` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `tenant_id` | uuid FK → tenants |
| `name` | varchar(100) |
| `start_time` | time |
| `end_time` | time |
| `break_minutes` | int |
| `is_night_shift` | boolean |

---

### `employee_schedules` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `employee_id` | uuid FK → employees |
| `work_schedule_id` | uuid FK → work_schedules |
| `effective_from` | date |
| `effective_to` | date nullable |

---

### `roster_periods` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `tenant_id` | uuid FK → tenants |
| `name` | varchar(100) |
| `start_date` | date |
| `end_date` | date |
| `status` | varchar(20) — draft/published |

---

### `roster_entries` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `roster_period_id` | uuid FK → roster_periods |
| `employee_id` | uuid FK → employees |
| `shift_id` | uuid FK → shifts |
| `work_date` | date |

---

### `shift_assignments` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `employee_id` | uuid FK → employees |
| `shift_id` | uuid FK → shifts |
| `assigned_date` | date |
| `status` | varchar(20) |

---

### `attendance_records` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `employee_id` | uuid FK → employees |
| `work_date` | date |
| `clock_in_at` | timestamptz |
| `clock_out_at` | timestamptz nullable |
| `total_minutes` | int |
| `status` | varchar(20) — present/absent/late/half_day |
| `source` | varchar(20) — agent/manual/biometric |

---

### `break_records` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `attendance_record_id` | uuid FK → attendance_records |
| `break_start_at` | timestamptz |
| `break_end_at` | timestamptz nullable |
| `type` | varchar(20) — lunch/short/prayer |

---

### `presence_sessions` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `employee_id` | uuid FK → employees |
| `device_session_id` | uuid FK → device_sessions nullable |
| `started_at` | timestamptz |
| `ended_at` | timestamptz nullable |
| `status` | varchar(20) — online/idle/offline |

---

### `device_sessions` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `employee_id` | uuid FK → employees |
| `device_id` | varchar(255) |
| `os` | varchar(50) |
| `app_version` | varchar(30) |
| `started_at` | timestamptz |
| `ended_at` | timestamptz nullable |

---

### `overtime_records` — Phase 1 — MERGED (HRMS + WMS OVERTIME_ENTRY)

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `tenant_id` | uuid | FK → tenants |
| `employee_id` | uuid | FK → employees |
| `task_id` | uuid | FK → tasks, nullable (null = HR manual) |
| `workspace_id` | uuid | FK → workspaces, nullable |
| `work_date` | date | |
| `minutes` | int | overtime minutes |
| `source` | varchar(20) | hr_manual / task_logged |
| `approved_by` | uuid | FK → users, nullable |
| `approved_at` | timestamptz | nullable |
| `notes` | text | |
| `created_at` | timestamptz | |

---

### `public_holidays` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `tenant_id` | uuid FK → tenants |
| `country_id` | uuid FK → countries |
| `name` | varchar(100) |
| `holiday_date` | date |
| `is_recurring` | boolean |

---

## 6. LEAVE

### `leave_types` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `tenant_id` | uuid FK → tenants |
| `name` | varchar(100) |
| `code` | varchar(20) |
| `is_paid` | boolean |
| `requires_approval` | boolean |
| `max_days_per_year` | numeric(5,2) |
| `is_active` | boolean |

---

### `leave_policies` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `tenant_id` | uuid FK → tenants |
| `leave_type_id` | uuid FK → leave_types |
| `name` | varchar(100) |
| `accrual_method` | varchar(30) |
| `rules_json` | jsonb |

---

### `leave_entitlements` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `employee_id` | uuid FK → employees |
| `leave_type_id` | uuid FK → leave_types |
| `year` | int |
| `entitled_days` | numeric(5,2) |
| `used_days` | numeric(5,2) |
| `carried_over_days` | numeric(5,2) |

---

### `leave_requests` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `employee_id` | uuid FK → employees |
| `leave_type_id` | uuid FK → leave_types |
| `start_date` | date |
| `end_date` | date |
| `total_days` | numeric(5,2) |
| `reason` | text |
| `status` | varchar(20) — pending/approved/rejected/cancelled |
| `approved_by` | uuid FK → users nullable |
| `approved_at` | timestamptz nullable |
| `created_at` | timestamptz |

---

### `leave_balances_audit` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `employee_id` | uuid FK → employees |
| `leave_type_id` | uuid FK → leave_types |
| `change_type` | varchar(30) — accrual/used/adjusted/carried_over |
| `delta_days` | numeric(5,2) |
| `new_balance` | numeric(5,2) |
| `reference_id` | uuid nullable |
| `created_at` | timestamptz |

---

## 7. PERFORMANCE

### `review_cycles` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `tenant_id` | uuid FK → tenants |
| `name` | varchar(100) |
| `period_start` | date |
| `period_end` | date |
| `status` | varchar(20) — draft/active/closed |
| `type` | varchar(30) — annual/mid_year/probation |

---

### `reviews` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `cycle_id` | uuid FK → review_cycles |
| `employee_id` | uuid FK → employees |
| `reviewer_id` | uuid FK → employees |
| `status` | varchar(20) |
| `rating` | numeric(3,1) nullable |
| `submitted_at` | timestamptz nullable |

---

### `feedback_requests` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `review_id` | uuid FK → reviews |
| `requestor_id` | uuid FK → employees |
| `target_id` | uuid FK → employees |
| `status` | varchar(20) |
| `submitted_at` | timestamptz nullable |

---

### `goals` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `employee_id` | uuid FK → employees |
| `cycle_id` | uuid FK → review_cycles nullable |
| `title` | varchar(255) |
| `description` | text |
| `target_value` | numeric |
| `actual_value` | numeric |
| `status` | varchar(20) |
| `due_date` | date |

---

### `performance_improvement_plans` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `employee_id` | uuid FK → employees |
| `manager_id` | uuid FK → employees |
| `start_date` | date |
| `end_date` | date |
| `objectives` | text |
| `status` | varchar(20) |

---

### `recognitions` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `tenant_id` | uuid FK → tenants |
| `giver_id` | uuid FK → employees |
| `receiver_id` | uuid FK → employees |
| `category` | varchar(50) |
| `message` | text |
| `points` | int |
| `created_at` | timestamptz |

---

### `succession_plans` — Phase 2

| Column | Type |
|---|---|
| `id` | uuid PK |
| `tenant_id` | uuid FK → tenants |
| `position_id` | uuid FK → job_titles |
| `incumbent_id` | uuid FK → employees |
| `successor_id` | uuid FK → employees |
| `readiness` | varchar(20) — ready_now/1_year/2_year |
| `notes` | text |

---

## 8. PAYROLL

### `allowance_types` — Phase 2

| Column | Type |
|---|---|
| `id` | uuid PK |
| `tenant_id` | uuid FK → tenants |
| `name` | varchar(100) |
| `is_taxable` | boolean |
| `is_active` | boolean |

---

### `employee_allowances` — Phase 2

| Column | Type |
|---|---|
| `id` | uuid PK |
| `employee_id` | uuid FK → employees |
| `allowance_type_id` | uuid FK → allowance_types |
| `amount` | numeric(15,2) |
| `currency_code` | varchar(3) |
| `effective_from` | date |
| `effective_to` | date nullable |

---

### `pension_plans` — Phase 2

| Column | Type |
|---|---|
| `id` | uuid PK |
| `tenant_id` | uuid FK → tenants |
| `name` | varchar(100) |
| `employer_contribution_pct` | numeric(5,2) |
| `employee_contribution_pct` | numeric(5,2) |

---

### `employee_pension_enrollments` — Phase 2

| Column | Type |
|---|---|
| `id` | uuid PK |
| `employee_id` | uuid FK → employees |
| `pension_plan_id` | uuid FK → pension_plans |
| `enrolled_at` | date |
| `opted_out_at` | date nullable |

---

### `tax_configurations` — Phase 2

| Column | Type |
|---|---|
| `id` | uuid PK |
| `tenant_id` | uuid FK → tenants |
| `country_id` | uuid FK → countries |
| `tax_year` | int |
| `rules_json` | jsonb |
| `is_active` | boolean |

---

### `payroll_providers` — Phase 2

| Column | Type |
|---|---|
| `id` | uuid PK |
| `tenant_id` | uuid FK → tenants |
| `name` | varchar(100) |
| `provider_type` | varchar(30) |
| `config_json` | jsonb |
| `is_active` | boolean |

---

### `payroll_connections` — Phase 2

| Column | Type |
|---|---|
| `id` | uuid PK |
| `tenant_id` | uuid FK → tenants |
| `payroll_provider_id` | uuid FK → payroll_providers |
| `credentials_encrypted` | text |
| `is_active` | boolean |

---

### `payroll_runs` — Phase 2

| Column | Type |
|---|---|
| `id` | uuid PK |
| `tenant_id` | uuid FK → tenants |
| `period_start` | date |
| `period_end` | date |
| `status` | varchar(20) — draft/processing/completed/failed |
| `total_gross` | numeric(15,2) |
| `total_net` | numeric(15,2) |
| `run_by` | uuid FK → users |
| `completed_at` | timestamptz nullable |

---

### `payroll_adjustments` — Phase 2

| Column | Type |
|---|---|
| `id` | uuid PK |
| `payroll_run_id` | uuid FK → payroll_runs |
| `employee_id` | uuid FK → employees |
| `type` | varchar(30) — bonus/deduction/correction |
| `amount` | numeric(15,2) |
| `reason` | text |

---

### `payslips` — Phase 2

| Column | Type |
|---|---|
| `id` | uuid PK |
| `payroll_run_id` | uuid FK → payroll_runs |
| `employee_id` | uuid FK → employees |
| `gross_pay` | numeric(15,2) |
| `net_pay` | numeric(15,2) |
| `deductions_json` | jsonb |
| `pdf_asset_id` | uuid FK → file_assets nullable |
| `issued_at` | timestamptz |

---

### `payroll_audit_trail` — Phase 2

| Column | Type |
|---|---|
| `id` | uuid PK |
| `payroll_run_id` | uuid FK → payroll_runs |
| `action` | varchar(50) |
| `performed_by` | uuid FK → users |
| `details_json` | jsonb |
| `created_at` | timestamptz |

---

## 9. SKILLS & LEARNING (HRMS wins)

### `skill_categories` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `tenant_id` | uuid FK → tenants |
| `name` | varchar(100) |
| `description` | text |

---

### `skills` — Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `tenant_id` | uuid | FK → tenants |
| `workspace_id` | uuid | FK → workspaces, nullable (WMS workspace-specific skill) |
| `category_id` | uuid | FK → skill_categories |
| `name` | varchar(100) | |
| `description` | text | |
| `is_active` | boolean | |

---

### `employee_skills` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `employee_id` | uuid FK → employees |
| `skill_id` | uuid FK → skills |
| `proficiency_level` | varchar(20) — beginner/intermediate/advanced/expert |
| `verified_by` | uuid FK → users nullable |
| `verified_at` | timestamptz nullable |

---

### `skill_validation_requests` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `employee_skill_id` | uuid FK → employee_skills |
| `requested_by` | uuid FK → users |
| `validator_id` | uuid FK → users |
| `status` | varchar(20) |
| `created_at` | timestamptz |

---

### `job_skill_requirements` — Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `job_title_id` | uuid | FK → job_titles, nullable |
| `project_id` | uuid | FK → projects, nullable (WMS resource requirement) |
| `skill_id` | uuid | FK → skills |
| `required_level` | varchar(20) | |
| `headcount` | int | nullable |
| `is_mandatory` | boolean | |

---

### `skill_questions` — Phase 2

| Column | Type |
|---|---|
| `id` | uuid PK |
| `skill_id` | uuid FK → skills |
| `question_text` | text |
| `type` | varchar(20) — mcq/text |

---

### `skill_question_options` — Phase 2

| Column | Type |
|---|---|
| `id` | uuid PK |
| `question_id` | uuid FK → skill_questions |
| `option_text` | text |
| `is_correct` | boolean |

---

### `skill_assessment_responses` — Phase 2

| Column | Type |
|---|---|
| `id` | uuid PK |
| `employee_id` | uuid FK → employees |
| `question_id` | uuid FK → skill_questions |
| `response_text` | text |
| `selected_option_id` | uuid FK → skill_question_options nullable |
| `assessed_at` | timestamptz |

---

### `employee_certifications` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `employee_id` | uuid FK → employees |
| `skill_id` | uuid FK → skills nullable |
| `name` | varchar(200) |
| `issuing_body` | varchar(200) |
| `issued_at` | date |
| `expires_at` | date nullable |
| `certificate_asset_id` | uuid FK → file_assets nullable |

---

### `lms_providers` — Phase 2

| Column | Type |
|---|---|
| `id` | uuid PK |
| `tenant_id` | uuid FK → tenants |
| `name` | varchar(100) |
| `provider_type` | varchar(30) |
| `config_json` | jsonb |

---

### `courses` — Phase 2

| Column | Type |
|---|---|
| `id` | uuid PK |
| `tenant_id` | uuid FK → tenants |
| `lms_provider_id` | uuid FK → lms_providers nullable |
| `title` | varchar(255) |
| `description` | text |
| `duration_hours` | numeric(5,2) |
| `is_active` | boolean |

---

### `course_skill_tags` — Phase 2

| Column | Type |
|---|---|
| `course_id` | uuid FK → courses |
| `skill_id` | uuid FK → skills |

PK: `(course_id, skill_id)`

---

### `course_enrollments` — Phase 2

| Column | Type |
|---|---|
| `id` | uuid PK |
| `employee_id` | uuid FK → employees |
| `course_id` | uuid FK → courses |
| `enrolled_at` | timestamptz |
| `completed_at` | timestamptz nullable |
| `progress_pct` | int |

---

### `development_plans` — Phase 2

| Column | Type |
|---|---|
| `id` | uuid PK |
| `employee_id` | uuid FK → employees |
| `manager_id` | uuid FK → employees |
| `title` | varchar(255) |
| `status` | varchar(20) |
| `review_date` | date |

---

### `development_plan_items` — Phase 2

| Column | Type |
|---|---|
| `id` | uuid PK |
| `plan_id` | uuid FK → development_plans |
| `skill_id` | uuid FK → skills nullable |
| `course_id` | uuid FK → courses nullable |
| `target_level` | varchar(20) |
| `due_date` | date |
| `status` | varchar(20) |

---

## 10. CALENDAR (MERGED)

### `calendar_events` — Phase 1 — MERGED (HRMS + WMS CALENDAR_EVENT)

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `tenant_id` | uuid | FK → tenants |
| `workspace_id` | uuid | FK → workspaces, nullable |
| `user_id` | uuid | FK → users, nullable (null = tenant-wide) |
| `title` | varchar(255) | |
| `description` | text | |
| `event_type` | varchar(30) | task_deadline / meeting / goal / availability / reminder / hr_event / public_holiday |
| `entity_type` | varchar(50) | nullable — Task / LeaveRequest / Sprint / OKR |
| `entity_id` | uuid | nullable |
| `start_at` | timestamptz | |
| `end_at` | timestamptz | |
| `is_all_day` | boolean | |
| `recurrence_rule` | varchar(255) | RRULE nullable |
| `created_by` | uuid | FK → users |
| `created_at` | timestamptz | |

---

### `calendar_preferences` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `user_id` | uuid FK → users UNIQUE |
| `default_view` | varchar(20) — day/week/month |
| `show_weekends` | boolean |
| `working_hours_start` | time |
| `working_hours_end` | time |

---

## 11. NOTIFICATIONS (MERGED)

### `notification_templates` — Phase 1 (HRMS)

| Column | Type |
|---|---|
| `id` | uuid PK |
| `tenant_id` | uuid FK → tenants |
| `event_type` | varchar(100) |
| `channel` | varchar(20) — email/sms/push/in_app |
| `subject_template` | text |
| `body_template` | text |
| `is_active` | boolean |

---

### `notification_channels` — Phase 1 (HRMS)

| Column | Type |
|---|---|
| `id` | uuid PK |
| `tenant_id` | uuid FK → tenants |
| `channel_type` | varchar(20) — email/sms/push/webhook |
| `config_json` | jsonb |
| `is_active` | boolean |

---

### `notifications` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `tenant_id` | uuid FK → tenants |
| `workspace_id` | uuid FK → workspaces nullable |
| `user_id` | uuid FK → users |
| `type` | varchar(50) |
| `title` | varchar(255) |
| `body` | text |
| `entity_type` | varchar(50) nullable |
| `entity_id` | uuid nullable |
| `is_read` | boolean |
| `created_at` | timestamptz |

---

### `notification_deliveries` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `notification_id` | uuid FK → notifications |
| `channel` | varchar(20) |
| `status` | varchar(20) — pending/sent/failed |
| `attempted_at` | timestamptz |
| `error_message` | text nullable |

---

### `notification_rules` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `tenant_id` | uuid FK → tenants |
| `workspace_id` | uuid FK → workspaces nullable |
| `event_type` | varchar(100) |
| `channel` | varchar(20) |
| `is_active` | boolean |

---

### `notification_batches` — Phase 2

| Column | Type |
|---|---|
| `id` | uuid PK |
| `user_id` | uuid FK → users |
| `batch_type` | varchar(30) |
| `scheduled_at` | timestamptz |
| `sent_at` | timestamptz nullable |
| `status` | varchar(20) |

---

### `notification_batch_items` — Phase 2

| Column | Type |
|---|---|
| `id` | uuid PK |
| `batch_id` | uuid FK → notification_batches |
| `notification_id` | uuid FK → notifications |

---

### `digest_schedules` — Phase 2

| Column | Type |
|---|---|
| `id` | uuid PK |
| `user_id` | uuid FK → users UNIQUE |
| `frequency` | varchar(20) — daily/weekly |
| `timezone` | varchar(50) |
| `next_send_at` | timestamptz |

---

### `push_subscriptions` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `user_id` | uuid FK → users |
| `endpoint` | varchar(1000) |
| `device_type` | varchar(20) |
| `keys_json` | jsonb |
| `is_active` | boolean |

---

## 12. DOCUMENTS (HRMS)

### `document_categories` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `tenant_id` | uuid FK → tenants |
| `name` | varchar(100) |
| `parent_id` | uuid FK → document_categories nullable |

---

### `document_templates` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `tenant_id` | uuid FK → tenants |
| `name` | varchar(200) |
| `category_id` | uuid FK → document_categories nullable |
| `body_template` | text |
| `is_active` | boolean |

---

### `documents` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `tenant_id` | uuid FK → tenants |
| `workspace_id` | uuid FK → workspaces nullable |
| `project_id` | uuid FK → projects nullable |
| `category_id` | uuid FK → document_categories nullable |
| `title` | varchar(255) |
| `status` | varchar(20) — draft/published/archived |
| `owner_id` | uuid FK → users |
| `created_at` | timestamptz |
| `updated_at` | timestamptz |

---

### `document_versions` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `document_id` | uuid FK → documents |
| `version_no` | int |
| `body` | text |
| `file_asset_id` | uuid FK → file_assets nullable |
| `created_by` | uuid FK → users |
| `created_at` | timestamptz |

---

### `document_acknowledgements` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `document_id` | uuid FK → documents |
| `user_id` | uuid FK → users |
| `acknowledged_at` | timestamptz |

---

### `document_access_logs` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `document_id` | uuid FK → documents |
| `user_id` | uuid FK → users |
| `action` | varchar(20) — view/download/edit |
| `accessed_at` | timestamptz |

---

## 13. FILE STORAGE (WMS wins — versioned)

### `file_assets` — Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `tenant_id` | uuid | FK → tenants |
| `workspace_id` | uuid | FK → workspaces, nullable |
| `uploaded_by` | uuid | FK → users |
| `file_name` | varchar(255) | |
| `mime_type` | varchar(100) | |
| `size_bytes` | bigint | |
| `storage_path` | varchar(500) | blob storage path |
| `is_public` | boolean | |
| `created_at` | timestamptz | |

---

### `file_versions` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `file_asset_id` | uuid FK → file_assets |
| `version_no` | int |
| `storage_url` | varchar(500) |
| `size_bytes` | bigint |
| `uploaded_by` | uuid FK → users |
| `uploaded_at` | timestamptz |

---

## 14. ACTIVITY MONITORING

### `activity_daily_summary` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `employee_id` | uuid FK → employees |
| `work_date` | date |
| `productive_minutes` | int |
| `idle_minutes` | int |
| `total_active_minutes` | int |
| `top_app_json` | jsonb |
| `productivity_score` | numeric(5,2) |

UNIQUE: `(employee_id, work_date)`

---

### `activity_raw_buffer` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `employee_id` | uuid FK → employees |
| `device_session_id` | uuid FK → device_sessions |
| `event_type` | varchar(50) |
| `payload_json` | jsonb |
| `captured_at` | timestamptz |

---

### `activity_snapshots` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `employee_id` | uuid FK → employees |
| `snapshot_at` | timestamptz |
| `active_window_title` | varchar(500) |
| `application_name` | varchar(200) |
| `idle_seconds` | int |

---

### `application_categories` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `tenant_id` | uuid FK → tenants |
| `name` | varchar(100) |
| `is_productive` | boolean |
| `is_system` | boolean |

---

### `application_usage` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `employee_id` | uuid FK → employees |
| `work_date` | date |
| `application_name` | varchar(200) |
| `category_id` | uuid FK → application_categories nullable |
| `total_minutes` | int |
| `is_allowed` | boolean |

---

### `device_tracking` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `employee_id` | uuid FK → employees |
| `device_id` | varchar(255) |
| `hostname` | varchar(255) |
| `ip_address` | varchar(45) |
| `mac_address` | varchar(20) |
| `last_seen_at` | timestamptz |

---

### `meeting_sessions` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `employee_id` | uuid FK → employees |
| `platform` | varchar(50) — teams/zoom/meet |
| `started_at` | timestamptz |
| `ended_at` | timestamptz nullable |
| `duration_minutes` | int |

---

### `screenshots` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `employee_id` | uuid FK → employees |
| `file_asset_id` | uuid FK → file_assets |
| `captured_at` | timestamptz |
| `trigger` | varchar(20) — scheduled/event |

---

### `browser_activity` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `employee_id` | uuid FK → employees |
| `work_date` | date |
| `domain` | varchar(255) |
| `total_minutes` | int |
| `is_allowed` | boolean |

---

## 15. AGENT GATEWAY

### `registered_agents` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `tenant_id` | uuid FK → tenants |
| `employee_id` | uuid FK → employees |
| `device_id` | varchar(255) |
| `agent_version` | varchar(30) |
| `platform` | varchar(30) |
| `status` | varchar(20) — active/inactive/revoked |
| `registered_at` | timestamptz |

---

### `agent_sessions` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `agent_id` | uuid FK → registered_agents |
| `started_at` | timestamptz |
| `ended_at` | timestamptz nullable |
| `ip_address` | varchar(45) |

---

### `agent_commands` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `agent_id` | uuid FK → registered_agents |
| `command_type` | varchar(50) |
| `payload_json` | jsonb |
| `status` | varchar(20) |
| `issued_at` | timestamptz |
| `acknowledged_at` | timestamptz nullable |

---

### `agent_health_logs` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `agent_id` | uuid FK → registered_agents |
| `status` | varchar(20) — healthy/degraded/offline |
| `details_json` | jsonb |
| `recorded_at` | timestamptz |

---

### `agent_policies` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `tenant_id` | uuid FK → tenants |
| `policy_type` | varchar(50) |
| `config_json` | jsonb |
| `is_active` | boolean |

---

## 16. EXCEPTION ENGINE

### `exception_rules` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `tenant_id` | uuid FK → tenants |
| `name` | varchar(100) |
| `condition_json` | jsonb |
| `severity` | varchar(20) — low/medium/high/critical |
| `is_active` | boolean |

---

### `exception_alerts` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `rule_id` | uuid FK → exception_rules |
| `employee_id` | uuid FK → employees |
| `triggered_at` | timestamptz |
| `details_json` | jsonb |
| `status` | varchar(20) — open/acknowledged/resolved |

---

### `alert_acknowledgements` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `alert_id` | uuid FK → exception_alerts |
| `acknowledged_by` | uuid FK → users |
| `notes` | text |
| `acknowledged_at` | timestamptz |

---

### `escalation_chains` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `tenant_id` | uuid FK → tenants |
| `rule_id` | uuid FK → exception_rules |
| `level` | int |
| `escalate_to_role_id` | uuid FK → roles nullable |
| `escalate_after_minutes` | int |

---

### `exception_schedules` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `rule_id` | uuid FK → exception_rules |
| `cron_expression` | varchar(100) |
| `last_run_at` | timestamptz nullable |
| `is_active` | boolean |

---

## 17. DISCREPANCY ENGINE

### `discrepancy_events` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `tenant_id` | uuid FK → tenants |
| `employee_id` | uuid FK → employees |
| `work_date` | date |
| `discrepancy_type` | varchar(50) |
| `hr_value` | numeric |
| `wms_value` | numeric |
| `delta` | numeric |
| `status` | varchar(20) — open/resolved/ignored |
| `detected_at` | timestamptz |

---

### `wms_daily_time_logs` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `employee_id` | uuid FK → employees |
| `workspace_id` | uuid FK → workspaces |
| `work_date` | date |
| `total_logged_minutes` | int |
| `synced_at` | timestamptz |

---

### `employee_discrepancy_baselines` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `employee_id` | uuid FK → employees UNIQUE |
| `expected_daily_minutes` | int |
| `tolerance_pct` | numeric(5,2) |
| `updated_at` | timestamptz |

---

## 18. REPORTING ENGINE

### `report_definitions` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `tenant_id` | uuid FK → tenants |
| `name` | varchar(100) |
| `query_json` | jsonb |
| `module` | varchar(50) |
| `is_system` | boolean |

---

### `report_templates` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `tenant_id` | uuid FK → tenants |
| `name` | varchar(100) |
| `definition_id` | uuid FK → report_definitions |
| `layout_json` | jsonb |

---

### `report_executions` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `definition_id` | uuid FK → report_definitions |
| `triggered_by` | uuid FK → users |
| `status` | varchar(20) — queued/running/done/failed |
| `result_asset_id` | uuid FK → file_assets nullable |
| `started_at` | timestamptz |
| `completed_at` | timestamptz nullable |

---

## 19. CONFIGURATION

### `tenant_settings` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `tenant_id` | uuid FK → tenants UNIQUE |
| `monitoring_enabled` | boolean |
| `screenshot_interval_mins` | int |
| `idle_threshold_mins` | int |
| `working_hours_json` | jsonb |
| `settings_json` | jsonb |

---

### `monitoring_feature_toggles` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `tenant_id` | uuid FK → tenants |
| `feature` | varchar(50) — screenshots/browser/keystrokes |
| `is_enabled` | boolean |

---

### `employee_monitoring_overrides` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `employee_id` | uuid FK → employees |
| `feature` | varchar(50) |
| `is_enabled` | boolean |
| `reason` | text |
| `set_by` | uuid FK → users |

---

### `app_allowlists` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `tenant_id` | uuid FK → tenants |
| `name` | varchar(100) |
| `type` | varchar(20) — allowed/blocked |
| `is_active` | boolean |

---

### `app_allowlist_audit` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `allowlist_id` | uuid FK → app_allowlists |
| `changed_by` | uuid FK → users |
| `change_json` | jsonb |
| `changed_at` | timestamptz |

---

### `observed_applications` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `allowlist_id` | uuid FK → app_allowlists |
| `application_name` | varchar(200) |
| `executable_pattern` | varchar(255) |

---

### `integration_connections` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `tenant_id` | uuid FK → tenants |
| `provider` | varchar(50) — slack/jira/github |
| `credentials_encrypted` | text |
| `config_json` | jsonb |
| `is_active` | boolean |

---

## 20. IDENTITY VERIFICATION

### `biometric_devices` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `tenant_id` | uuid FK → tenants |
| `office_location_id` | uuid FK → office_locations |
| `name` | varchar(100) |
| `device_type` | varchar(30) — fingerprint/face/iris |
| `serial_number` | varchar(100) |
| `is_active` | boolean |

---

### `biometric_enrollments` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `employee_id` | uuid FK → employees |
| `device_id` | uuid FK → biometric_devices |
| `template_hash` | varchar(500) |
| `enrolled_at` | timestamptz |
| `is_active` | boolean |

---

### `biometric_events` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `device_id` | uuid FK → biometric_devices |
| `employee_id` | uuid FK → employees |
| `event_type` | varchar(30) — checkin/checkout/failed |
| `occurred_at` | timestamptz |
| `confidence_score` | numeric(5,3) nullable |

---

### `biometric_audit_logs` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `device_id` | uuid FK → biometric_devices |
| `action` | varchar(50) |
| `performed_by` | uuid FK → users nullable |
| `details_json` | jsonb |
| `created_at` | timestamptz |

---

### `verification_policies` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `tenant_id` | uuid FK → tenants |
| `method` | varchar(30) — biometric/photo/both |
| `required_for` | varchar(30) — checkin/checkout/all |
| `is_active` | boolean |

---

### `verification_records` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `employee_id` | uuid FK → employees |
| `policy_id` | uuid FK → verification_policies |
| `method_used` | varchar(30) |
| `result` | varchar(20) — pass/fail |
| `photo_asset_id` | uuid FK → file_assets nullable |
| `verified_at` | timestamptz |

---

## 21. GRIEVANCE

### `grievance_cases` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `tenant_id` | uuid FK → tenants |
| `employee_id` | uuid FK → employees |
| `against_employee_id` | uuid FK → employees nullable |
| `category` | varchar(50) |
| `description` | text |
| `status` | varchar(20) — open/investigating/resolved/closed |
| `assigned_to` | uuid FK → users nullable |
| `resolved_at` | timestamptz nullable |
| `created_at` | timestamptz |

---

### `disciplinary_actions` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `grievance_case_id` | uuid FK → grievance_cases nullable |
| `employee_id` | uuid FK → employees |
| `action_type` | varchar(50) — warning/suspension/termination |
| `issued_by` | uuid FK → users |
| `effective_date` | date |
| `notes` | text |

---

## 22. EXPENSE

### `expense_categories` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `tenant_id` | uuid FK → tenants |
| `name` | varchar(100) |
| `requires_receipt` | boolean |
| `max_amount` | numeric(15,2) nullable |

---

### `expense_claims` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `employee_id` | uuid FK → employees |
| `title` | varchar(255) |
| `total_amount` | numeric(15,2) |
| `currency_code` | varchar(3) |
| `status` | varchar(20) — draft/submitted/approved/rejected/paid |
| `submitted_at` | timestamptz nullable |
| `approved_by` | uuid FK → users nullable |

---

### `expense_items` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `claim_id` | uuid FK → expense_claims |
| `category_id` | uuid FK → expense_categories |
| `description` | varchar(255) |
| `amount` | numeric(15,2) |
| `expense_date` | date |
| `receipt_asset_id` | uuid FK → file_assets nullable |

---

## 23. PRODUCTIVITY ANALYTICS

### `daily_employee_report` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `employee_id` | uuid FK → employees |
| `work_date` | date |
| `total_minutes` | int |
| `productive_minutes` | int |
| `idle_minutes` | int |
| `attendance_status` | varchar(20) |
| `tasks_completed` | int |

UNIQUE: `(employee_id, work_date)`

---

### `weekly_employee_report` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `employee_id` | uuid FK → employees |
| `week_start` | date |
| `total_hours` | numeric(5,2) |
| `avg_productivity_score` | numeric(5,2) |
| `leave_days` | numeric(3,1) |
| `tasks_completed` | int |

---

### `monthly_employee_report` — Phase 2

| Column | Type |
|---|---|
| `id` | uuid PK |
| `employee_id` | uuid FK → employees |
| `month` | int |
| `year` | int |
| `total_hours` | numeric(6,2) |
| `overtime_hours` | numeric(5,2) |
| `avg_score` | numeric(5,2) |

---

### `workforce_snapshot` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `tenant_id` | uuid FK → tenants |
| `snapshot_date` | date |
| `total_employees` | int |
| `present_count` | int |
| `on_leave_count` | int |
| `data_json` | jsonb |

---

### `wms_productivity_snapshots` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `workspace_id` | uuid FK → workspaces |
| `snapshot_date` | date |
| `tasks_open` | int |
| `tasks_completed` | int |
| `avg_cycle_time_hours` | numeric(8,2) |
| `data_json` | jsonb |

---

## 24. SHARED PLATFORM

### `subscription_plans` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `name` | varchar(100) |
| `tier` | varchar(20) — free/starter/pro/enterprise |
| `max_employees` | int |
| `max_workspaces` | int |
| `features_json` | jsonb |
| `price_monthly` | numeric(10,2) |
| `price_annual` | numeric(10,2) |
| `is_active` | boolean |

---

### `subscription_usage` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `tenant_id` | uuid FK → tenants |
| `period_start` | date |
| `period_end` | date |
| `employee_count` | int |
| `workspace_count` | int |
| `storage_gb` | numeric(10,3) |

---

### Outbox / Messaging (MassTransit — per module DbContext)

> Not written to directly. MassTransit manages these.

| Table | Notes |
|---|---|
| `*_outbox_events` | per module — (tenant_id, event_type, payload jsonb, processed_at, retry_count, last_error) |
| `processed_integration_events` | idempotency — (event_id PK, event_type, processed_at) |

---

## 25. WMS — PROJECT MANAGEMENT

### `projects` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `workspace_id` | uuid FK → workspaces |
| `name` | varchar(200) |
| `description` | text |
| `status` | varchar(20) — active/archived/on_hold |
| `lead_id` | uuid FK → users nullable |
| `start_date` | date nullable |
| `end_date` | date nullable |
| `created_by` | uuid FK → users |
| `created_at` | timestamptz |

---

### `project_members` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `project_id` | uuid FK → projects |
| `user_id` | uuid FK → users |
| `role` | varchar(30) — lead/member/viewer |
| `joined_at` | timestamptz |

UNIQUE: `(project_id, user_id)`

---

### `project_components` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `project_id` | uuid FK → projects |
| `name` | varchar(100) |
| `lead_id` | uuid FK → users nullable |
| `description` | text |

---

### `epics` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `project_id` | uuid FK → projects |
| `title` | varchar(255) |
| `status` | varchar(20) |
| `start_date` | date nullable |
| `end_date` | date nullable |

---

### `milestones` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `project_id` | uuid FK → projects |
| `name` | varchar(200) |
| `target_date` | date |
| `status` | varchar(20) |

---

### `project_settings` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `project_id` | uuid FK → projects UNIQUE |
| `timezone` | varchar(50) |
| `default_priority` | varchar(20) |
| `working_days_json` | jsonb |
| `estimation_unit` | varchar(20) — hours/points |

---

### `change_requests` — Phase 2

| Column | Type |
|---|---|
| `id` | uuid PK |
| `project_id` | uuid FK → projects |
| `requested_by` | uuid FK → users |
| `title` | varchar(255) |
| `description` | text |
| `status` | varchar(20) |
| `created_at` | timestamptz |

---

## 26. WMS — TASK MANAGEMENT

### `tasks` — Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `workspace_id` | uuid | FK → workspaces |
| `project_id` | uuid | FK → projects, nullable |
| `sprint_id` | uuid | FK → sprints, nullable |
| `epic_id` | uuid | FK → epics, nullable |
| `parent_task_id` | uuid | FK → tasks, nullable (subtasks) |
| `issue_type_id` | uuid | FK → issue_types |
| `title` | varchar(500) | |
| `description` | text | |
| `priority` | varchar(20) | urgent/high/medium/low |
| `status` | varchar(30) | |
| `story_points` | int | nullable |
| `due_date` | date | nullable |
| `created_by` | uuid | FK → users |
| `created_at` | timestamptz | |
| `updated_at` | timestamptz | |

---

### `issue_types` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `workspace_id` | uuid FK → workspaces |
| `name` | varchar(50) |
| `color` | varchar(20) |
| `icon` | varchar(50) |
| `is_default` | boolean |

---

### `task_assignees` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `task_id` | uuid FK → tasks |
| `user_id` | uuid FK → users |
| `assigned_by` | uuid FK → users |
| `assigned_at` | timestamptz |

UNIQUE: `(task_id, user_id)`

---

### `checklist_items` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `task_id` | uuid FK → tasks |
| `title` | varchar(255) |
| `is_checked` | boolean |
| `position` | int |
| `assigned_to` | uuid FK → users nullable |

---

### `task_dependencies` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `task_id` | uuid FK → tasks |
| `depends_on_id` | uuid FK → tasks |
| `type` | varchar(20) — blocks/is_blocked_by/relates_to |
| `created_at` | timestamptz |

---

### `labels` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `project_id` | uuid FK → projects |
| `name` | varchar(50) |
| `color` | varchar(20) |

---

### `task_labels` — Phase 1

| Column | Type |
|---|---|
| `task_id` | uuid FK → tasks |
| `label_id` | uuid FK → labels |
| `linked_at` | timestamptz |

PK: `(task_id, label_id)`

---

### `task_submissions` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `task_id` | uuid FK → tasks |
| `submitted_by` | uuid FK → users |
| `notes` | text |
| `status` | varchar(20) — pending/approved/rejected |
| `created_at` | timestamptz |

---

### `task_submission_files` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `submission_id` | uuid FK → task_submissions |
| `file_asset_id` | uuid FK → file_assets |
| `is_primary` | boolean |
| `uploaded_at` | timestamptz |

---

### `task_approvals` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `task_id` | uuid FK → tasks |
| `requested_by` | uuid FK → users |
| `approver_id` | uuid FK → users |
| `status` | varchar(20) — pending/approved/rejected |
| `decided_at` | timestamptz nullable |

---

### `task_reopen_logs` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `task_id` | uuid FK → tasks |
| `reopened_by` | uuid FK → users |
| `reason` | text |
| `reopened_at` | timestamptz |

---

### `bug_reports` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `project_id` | uuid FK → projects |
| `task_id` | uuid FK → tasks nullable |
| `title` | varchar(255) |
| `severity` | varchar(20) — critical/major/minor/trivial |
| `status` | varchar(20) |
| `reported_by` | uuid FK → users |
| `created_at` | timestamptz |

---

### `bug_reproduction_steps` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `bug_id` | uuid FK → bug_reports |
| `step_number` | int |
| `action` | text |
| `expected` | text |
| `actual` | text |

---

### `bug_resolutions` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `bug_id` | uuid FK → bug_reports UNIQUE |
| `resolution_type` | varchar(30) — fixed/wont_fix/duplicate/by_design |
| `resolved_by` | uuid FK → users |
| `resolution_notes` | text |
| `resolved_at` | timestamptz |

---

## 27. WMS — PLANNING

### `sprints` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `project_id` | uuid FK → projects |
| `name` | varchar(100) |
| `goal` | text nullable |
| `start_date` | date |
| `end_date` | date |
| `status` | varchar(20) — planned/active/completed |

---

### `sprint_reports` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `sprint_id` | uuid FK → sprints UNIQUE |
| `velocity` | numeric(8,2) |
| `completed_points` | int |
| `incomplete_points` | int |
| `summary_json` | jsonb |
| `created_at` | timestamptz |

---

### `boards` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `project_id` | uuid FK → projects |
| `name` | varchar(100) |
| `type` | varchar(20) — kanban/scrum/list |
| `is_default` | boolean |

---

### `board_views` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `board_id` | uuid FK → boards |
| `user_id` | uuid FK → users |
| `view_type` | varchar(20) — board/list/timeline |
| `filter_json` | jsonb |
| `is_default` | boolean |

---

### `roadmaps` — Phase 2

| Column | Type |
|---|---|
| `id` | uuid PK |
| `workspace_id` | uuid FK → workspaces |
| `name` | varchar(100) |
| `start_date` | date |
| `end_date` | date |
| `is_shared` | boolean |

---

### `roadmap_items` — Phase 2

| Column | Type |
|---|---|
| `id` | uuid PK |
| `roadmap_id` | uuid FK → roadmaps |
| `entity_type` | varchar(30) — Epic/Milestone/Sprint |
| `entity_id` | uuid |
| `position` | int |

---

### `baselines` — Phase 2

| Column | Type |
|---|---|
| `id` | uuid PK |
| `project_id` | uuid FK → projects |
| `name` | varchar(100) |
| `snapshot_json` | jsonb |
| `created_by` | uuid FK → users |
| `created_at` | timestamptz |

---

### `versions` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `project_id` | uuid FK → projects |
| `name` | varchar(100) |
| `status` | varchar(20) — planned/released/archived |
| `release_date` | date nullable |
| `description` | text |

---

### `release_calendars` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `project_id` | uuid FK → projects |
| `version_id` | uuid FK → versions |
| `release_at` | timestamptz |
| `status` | varchar(20) |
| `notes` | text |

---

## 28. WMS — OKR

### `objectives` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `workspace_id` | uuid FK → workspaces |
| `owner_id` | uuid FK → users |
| `title` | varchar(255) |
| `description` | text |
| `progress` | numeric(5,2) |
| `start_date` | date |
| `end_date` | date |
| `status` | varchar(20) |

---

### `key_results` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `objective_id` | uuid FK → objectives |
| `owner_id` | uuid FK → users |
| `title` | varchar(255) |
| `target_value` | numeric |
| `current_value` | numeric |
| `unit` | varchar(30) |
| `status` | varchar(20) |

---

### `okr_updates` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `entity_type` | varchar(20) — objective/key_result |
| `entity_id` | uuid |
| `new_value` | numeric |
| `updated_by` | uuid FK → users |
| `notes` | text |
| `created_at` | timestamptz |

---

### `okr_alignments` — Phase 2

| Column | Type |
|---|---|
| `id` | uuid PK |
| `parent_objective_id` | uuid FK → objectives |
| `child_objective_id` | uuid FK → objectives |
| `contribution_weight` | numeric(5,2) |
| `created_at` | timestamptz |

---

### `initiatives` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `key_result_id` | uuid FK → key_results |
| `title` | varchar(255) |
| `owner_id` | uuid FK → users |
| `status` | varchar(20) |
| `created_at` | timestamptz |

---

### `goal_checkins` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `objective_id` | uuid FK → objectives |
| `author_id` | uuid FK → users |
| `progress_delta` | numeric(5,2) |
| `notes` | text |
| `created_at` | timestamptz |

---

## 29. WMS — MY SPACE

### `personal_boards` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `user_id` | uuid FK → users |
| `workspace_id` | uuid FK → workspaces |
| `name` | varchar(100) |
| `created_at` | timestamptz |

---

### `personal_board_columns` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `personal_board_id` | uuid FK → personal_boards |
| `name` | varchar(50) |
| `position` | int |
| `color` | varchar(20) |

---

> `calendar_events` and `user_preferences` already defined above. My Space aggregates from those.

---

## 30. WMS — TO-DO

### `todos` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `user_id` | uuid FK → users |
| `workspace_id` | uuid FK → workspaces |
| `title` | varchar(255) |
| `description` | text |
| `priority` | varchar(20) — low/medium/high |
| `status` | varchar(20) — pending/done |
| `due_date` | date nullable |
| `created_at` | timestamptz |

---

### `todo_labels` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `todo_id` | uuid FK → todos |
| `name` | varchar(50) |
| `color` | varchar(20) |

---

### `todo_recurrences` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `todo_id` | uuid FK → todos UNIQUE |
| `frequency` | varchar(20) — daily/weekly/monthly |
| `interval` | int |
| `next_due_at` | date |
| `ends_at` | date nullable |

---

## 31. WMS — TIME MANAGEMENT

### `time_logs` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `task_id` | uuid FK → tasks |
| `user_id` | uuid FK → users |
| `workspace_id` | uuid FK → workspaces |
| `duration_mins` | int |
| `description` | text nullable |
| `logged_at` | timestamptz |

---

### `timer_sessions` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `user_id` | uuid FK → users |
| `task_id` | uuid FK → tasks |
| `started_at` | timestamptz |
| `ended_at` | timestamptz nullable |
| `duration_mins` | int nullable |

---

### `timesheets` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `user_id` | uuid FK → users |
| `workspace_id` | uuid FK → workspaces |
| `period_start` | date |
| `period_end` | date |
| `status` | varchar(20) — draft/submitted/approved |
| `submitted_at` | timestamptz nullable |

---

### `timesheet_entries` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `timesheet_id` | uuid FK → timesheets |
| `task_id` | uuid FK → tasks nullable |
| `date` | date |
| `duration_mins` | int |
| `notes` | text |

---

### `billable_rates` — Phase 2

| Column | Type |
|---|---|
| `id` | uuid PK |
| `workspace_id` | uuid FK → workspaces |
| `user_id` | uuid FK → users nullable |
| `project_id` | uuid FK → projects nullable |
| `rate` | numeric(10,2) |
| `currency_code` | varchar(3) |
| `effective_from` | date |

---

### `time_reports` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `workspace_id` | uuid FK → workspaces |
| `project_id` | uuid FK → projects nullable |
| `report_type` | varchar(30) |
| `period_start` | date |
| `period_end` | date |
| `generated_by` | uuid FK → users |
| `generated_at` | timestamptz |

---

> `overtime_records` already defined in Workforce Presence (merged).

---

## 32. WMS — RESOURCE MANAGEMENT

### `resource_plans` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `project_id` | uuid FK → projects |
| `user_id` | uuid FK → users |
| `allocation_pct` | int |
| `start_date` | date |
| `end_date` | date |
| `status` | varchar(20) |

---

### `resource_allocation_logs` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `resource_plan_id` | uuid FK → resource_plans |
| `changed_by` | uuid FK → users |
| `old_pct` | int |
| `new_pct` | int |
| `changed_at` | timestamptz |

---

### `capacity_snapshots` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `workspace_id` | uuid FK → workspaces |
| `user_id` | uuid FK → users |
| `week_start` | date |
| `utilization_pct` | numeric(5,2) |
| `available_hours` | numeric(5,2) |

UNIQUE: `(workspace_id, user_id, week_start)`

---

> `skills`, `employee_skills`, `job_skill_requirements` already defined in Skills module.

---

## 33. WMS — CHAT

### `channels` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `workspace_id` | uuid FK → workspaces |
| `name` | varchar(100) |
| `type` | varchar(20) — public/private/announcement |
| `topic` | varchar(255) nullable |
| `created_by` | uuid FK → users |
| `created_at` | timestamptz |

---

### `channel_members` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `channel_id` | uuid FK → channels |
| `user_id` | uuid FK → users |
| `role` | varchar(20) — admin/member |
| `joined_at` | timestamptz |
| `is_muted` | boolean |

UNIQUE: `(channel_id, user_id)`

---

### `messages` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `channel_id` | uuid FK → channels |
| `sender_id` | uuid FK → users |
| `body` | text |
| `parent_message_id` | uuid FK → messages nullable (thread) |
| `is_edited` | boolean |
| `edited_at` | timestamptz nullable |
| `is_deleted` | boolean |
| `created_at` | timestamptz |

---

### `message_reactions` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `message_id` | uuid FK → messages |
| `user_id` | uuid FK → users |
| `emoji` | varchar(50) |
| `created_at` | timestamptz |

UNIQUE: `(message_id, user_id, emoji)`

---

### `message_attachments` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `message_id` | uuid FK → messages |
| `file_asset_id` | uuid FK → file_assets |
| `uploaded_by` | uuid FK → users |
| `created_at` | timestamptz |

---

### `direct_message_channels` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `workspace_id` | uuid FK → workspaces |
| `is_group` | boolean |
| `name` | varchar(100) nullable |
| `created_at` | timestamptz |

---

### `dm_participants` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `dm_channel_id` | uuid FK → direct_message_channels |
| `user_id` | uuid FK → users |
| `is_muted` | boolean |
| `joined_at` | timestamptz |

---

### `message_read_receipts` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `message_id` | uuid FK → messages |
| `user_id` | uuid FK → users |
| `read_at` | timestamptz |

UNIQUE: `(message_id, user_id)`

---

## 34. WMS — CHAT AI

### `chat_tags` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `message_id` | uuid FK → messages |
| `channel_id` | uuid FK → channels |
| `tagged_by` | uuid FK → users |
| `tag_type` | varchar(20) — task/issue/report/motion/decision |
| `mentioned_user_id` | uuid FK → users nullable |
| `detected_at` | timestamptz |

---

### `ai_suggestions` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `chat_tag_id` | uuid FK → chat_tags |
| `channel_id` | uuid FK → channels |
| `suggested_by_ai` | boolean |
| `suggestion_type` | varchar(30) — create_task/create_report/create_issue/create_decision |
| `payload_json` | jsonb |
| `status` | varchar(20) — pending/accepted/rejected/expired |
| `responded_by` | uuid FK → users nullable |
| `responded_at` | timestamptz nullable |

---

### `missing_detail_prompts` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `chat_tag_id` | uuid FK → chat_tags |
| `ai_suggestion_id` | uuid FK → ai_suggestions |
| `field_name` | varchar(100) |
| `prompt_message` | text |
| `is_resolved` | boolean |
| `resolved_value` | text nullable |
| `resolved_at` | timestamptz nullable |

---

### `chat_reminder_items` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `chat_tag_id` | uuid FK → chat_tags |
| `task_id` | uuid FK → tasks nullable |
| `workspace_id` | uuid FK → workspaces |
| `created_by` | uuid FK → users |
| `assigned_to` | uuid FK → users |
| `status` | varchar(20) — todo/in_progress/done |
| `source_channel_id` | uuid FK → channels |
| `created_at` | timestamptz |

---

### `chat_kanban_syncs` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `chat_reminder_item_id` | uuid FK → chat_reminder_items |
| `task_id` | uuid FK → tasks |
| `board_id` | uuid FK → boards |
| `sync_direction` | varchar(30) — chat_to_board/board_to_chat |
| `triggered_by` | varchar(30) — status_change/tag_action |
| `synced_at` | timestamptz |

---

### `ai_session_contexts` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `channel_id` | uuid FK → channels |
| `user_id` | uuid FK → users |
| `context_snapshot_json` | jsonb |
| `last_updated_at` | timestamptz |
| `expires_at` | timestamptz |

---

### `premium_ai_detections` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `message_id` | uuid FK → messages |
| `channel_id` | uuid FK → channels |
| `detected_intent` | varchar(20) — task/report/issue/other |
| `confidence_score` | numeric(5,4) |
| `auto_created` | boolean |
| `created_entity_type` | varchar(30) nullable |
| `created_entity_id` | uuid nullable |
| `detected_at` | timestamptz |

---

## 35. WMS — COLLABORATION

### `comments` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `task_id` | uuid FK → tasks nullable |
| `document_id` | uuid FK → documents nullable |
| `author_id` | uuid FK → users |
| `body` | text |
| `parent_comment_id` | uuid FK → comments nullable |
| `is_edited` | boolean |
| `created_at` | timestamptz |

---

### `comment_reactions` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `comment_id` | uuid FK → comments |
| `user_id` | uuid FK → users |
| `emoji` | varchar(50) |
| `created_at` | timestamptz |

---

### `mentions` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `comment_id` | uuid FK → comments |
| `mentioned_user_id` | uuid FK → users |
| `created_at` | timestamptz |

---

### `attachments` — Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `task_id` | uuid | FK → tasks, nullable |
| `comment_id` | uuid | FK → comments, nullable |
| `file_asset_id` | uuid | FK → file_assets |
| `uploaded_by` | uuid | FK → users |
| `created_at` | timestamptz | |

---

### `wiki_pages` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `project_id` | uuid FK → projects |
| `title` | varchar(255) |
| `slug` | varchar(255) |
| `parent_page_id` | uuid FK → wiki_pages nullable |
| `created_by` | uuid FK → users |
| `updated_at` | timestamptz |

---

### `wiki_versions` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `wiki_page_id` | uuid FK → wiki_pages |
| `author_id` | uuid FK → users |
| `body` | text |
| `version_no` | int |
| `created_at` | timestamptz |

---

### `document_approvals` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `document_id` | uuid FK → documents |
| `requested_by` | uuid FK → users |
| `approver_id` | uuid FK → users |
| `status` | varchar(20) — pending/approved/rejected |
| `decided_at` | timestamptz nullable |

---

### `approval_comments` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `task_approval_id` | uuid FK → task_approvals nullable |
| `document_approval_id` | uuid FK → document_approvals nullable |
| `author_id` | uuid FK → users |
| `comment` | text |
| `created_at` | timestamptz |

---

## 36. WMS — REMINDERS

### `reminders` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `user_id` | uuid FK → users |
| `workspace_id` | uuid FK → workspaces nullable |
| `title` | varchar(255) |
| `entity_type` | varchar(30) nullable — Task/OKR/Meeting |
| `entity_id` | uuid nullable |
| `remind_at` | timestamptz |
| `status` | varchar(20) — pending/sent/snoozed/dismissed |

---

### `reminder_deliveries` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `reminder_id` | uuid FK → reminders |
| `channel` | varchar(20) |
| `status` | varchar(20) |
| `attempted_at` | timestamptz |

---

### `reminder_templates` — Phase 2

| Column | Type |
|---|---|
| `id` | uuid PK |
| `workspace_id` | uuid FK → workspaces |
| `name` | varchar(100) |
| `delivery_channel` | varchar(20) |
| `body_template` | text |
| `is_active` | boolean |

---

### `reminder_snooze_logs` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `reminder_id` | uuid FK → reminders |
| `snoozed_by` | uuid FK → users |
| `snoozed_until` | timestamptz |
| `created_at` | timestamptz |

---

## 37. WMS — INSIGHT & ANALYTICS

### `dashboards` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `workspace_id` | uuid FK → workspaces |
| `name` | varchar(100) |
| `owner_id` | uuid FK → users |
| `is_shared` | boolean |
| `created_at` | timestamptz |

---

### `chart_widgets` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `dashboard_id` | uuid FK → dashboards |
| `type` | varchar(30) — bar/line/pie/table |
| `config_json` | jsonb |
| `pos_x` | int |
| `pos_y` | int |
| `width` | int |
| `height` | int |

---

### `saved_views` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `project_id` | uuid FK → projects nullable |
| `workspace_id` | uuid FK → workspaces |
| `name` | varchar(100) |
| `filter_config_json` | jsonb |
| `created_by` | uuid FK → users |
| `is_shared` | boolean |

---

### `forms` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `project_id` | uuid FK → projects |
| `name` | varchar(100) |
| `fields_json` | jsonb |
| `is_published` | boolean |
| `created_by` | uuid FK → users |

---

### `form_submissions` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `form_id` | uuid FK → forms |
| `task_id` | uuid FK → tasks nullable |
| `submitted_by` | uuid FK → users nullable |
| `data_json` | jsonb |
| `submitted_at` | timestamptz |

---

### `kpi_targets` — Phase 2

| Column | Type |
|---|---|
| `id` | uuid PK |
| `dashboard_id` | uuid FK → dashboards |
| `name` | varchar(100) |
| `target_value` | numeric |
| `period` | varchar(20) — weekly/monthly/quarterly |
| `metric_type` | varchar(50) |

---

### `report_snapshots` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `dashboard_id` | uuid FK → dashboards |
| `snapshot_date` | date |
| `summary_json` | jsonb |
| `generated_at` | timestamptz |

---

### `report_exports` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `workspace_id` | uuid FK → workspaces |
| `report_type` | varchar(50) |
| `format` | varchar(10) — csv/xlsx/pdf |
| `status` | varchar(20) — queued/done/failed |
| `file_asset_id` | uuid FK → file_assets nullable |
| `requested_by` | uuid FK → users |
| `created_at` | timestamptz |

---

## 38. WMS — INTEGRATION & API

### `integrations` — Phase 2

| Column | Type |
|---|---|
| `id` | uuid PK |
| `workspace_id` | uuid FK → workspaces |
| `provider` | varchar(30) — github/jira/slack/figma |
| `config_json` | jsonb |
| `credentials_encrypted` | text |
| `is_connected` | boolean |
| `connected_by` | uuid FK → users |
| `connected_at` | timestamptz |

---

### `api_keys` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `workspace_id` | uuid FK → workspaces |
| `user_id` | uuid FK → users |
| `name` | varchar(100) |
| `key_hash` | varchar(255) |
| `scopes_json` | jsonb |
| `expires_at` | date nullable |
| `last_used_at` | timestamptz nullable |
| `created_at` | timestamptz |

---

### `webhooks` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `workspace_id` | uuid FK → workspaces |
| `url` | varchar(1000) |
| `events_json` | jsonb |
| `secret_hash` | varchar(255) |
| `is_active` | boolean |
| `created_by` | uuid FK → users |
| `created_at` | timestamptz |

---

### `webhook_deliveries` — Phase 1

| Column | Type |
|---|---|
| `id` | uuid PK |
| `webhook_id` | uuid FK → webhooks |
| `event_type` | varchar(100) |
| `payload_json` | jsonb |
| `response_status` | int nullable |
| `status` | varchar(20) — pending/success/failed |
| `attempted_at` | timestamptz |
| `duration_ms` | int nullable |

---

### `integration_sync_logs` — Phase 2

| Column | Type |
|---|---|
| `id` | uuid PK |
| `integration_id` | uuid FK → integrations |
| `sync_type` | varchar(30) |
| `status` | varchar(20) |
| `records_synced` | int |
| `error_message` | text nullable |
| `executed_at` | timestamptz |

---

## Table Count Summary

| Module | Tables | Phase |
|---|---|---|
| 1. Foundation | 9 | P1 |
| 2. Auth & Security | 14 | P1/P2 |
| 3. Org Structure | 11 | P1/P2 |
| 4. Core HR | 13 | P1 |
| 5. Workforce Presence | 12 | P1 |
| 6. Leave | 5 | P1 |
| 7. Performance | 7 | P1/P2 |
| 8. Payroll | 11 | P2 |
| 9. Skills & Learning | 18 | P1/P2 |
| 10. Calendar | 2 | P1 |
| 11. Notifications | 9 | P1/P2 |
| 12. Documents | 6 | P1 |
| 13. File Storage | 2 | P1 |
| 14. Activity Monitoring | 9 | P1 |
| 15. Agent Gateway | 5 | P1 |
| 16. Exception Engine | 5 | P1 |
| 17. Discrepancy Engine | 3 | P1 |
| 18. Reporting Engine | 3 | P1 |
| 19. Configuration | 7 | P1 |
| 20. Identity Verification | 6 | P1 |
| 21. Grievance | 2 | P1 |
| 22. Expense | 3 | P1 |
| 23. Productivity Analytics | 5 | P1/P2 |
| 24. Shared Platform | 2 + outbox | P1 |
| 25. WMS Projects | 7 | P1/P2 |
| 26. WMS Tasks | 14 | P1 |
| 27. WMS Planning | 9 | P1/P2 |
| 28. WMS OKR | 6 | P1/P2 |
| 29. WMS My Space | 2 | P1 |
| 30. WMS Todo | 3 | P1 |
| 31. WMS Time | 6 | P1/P2 |
| 32. WMS Resource | 3 | P1 |
| 33. WMS Chat | 8 | P1 |
| 34. WMS Chat AI | 7 | P1 |
| 35. WMS Collaboration | 8 | P1 |
| 36. WMS Reminders | 4 | P1/P2 |
| 37. WMS Insight | 8 | P1/P2 |
| 38. WMS Integration | 5 | P1/P2 |
| **TOTAL** | **~287** | |

---

## Key Cross-Module FK References

```
users.id ←──────────────────── workspace_members.user_id
                                sessions.user_id
                                employees.user_id (1:1 per tenant)
                                task_assignees.user_id
                                messages.sender_id
                                comments.author_id

tenants.id ←────────────────── users.tenant_id
                                workspaces.tenant_id
                                employees.tenant_id
                                all HR tables

workspaces.id ←─────────────── workspace_members.workspace_id
                                projects.workspace_id
                                channels.workspace_id
                                objectives.workspace_id
                                todos.workspace_id

employees.id ←──────────────── attendance_records.employee_id
                                leave_requests.employee_id
                                activity_daily_summary.employee_id
                                overtime_records.employee_id

tasks.id ←──────────────────── time_logs.task_id
                                overtime_records.task_id (nullable)
                                task_assignees.task_id
                                checklist_items.task_id

file_assets.id ←────────────── task_submission_files.file_asset_id
                                message_attachments.file_asset_id
                                payslips.pdf_asset_id
                                screenshots.file_asset_id
                                employee_certifications.certificate_asset_id
```
