# Time & Attendance - Schema

**Module:** [[modules/time-attendance/overview|Time & Attendance]]
**Phase:** Phase 1
**Tables:** 17

---

## `break_records`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `employee_id` | `uuid` | FK -> employees |
| `break_start` | `timestamptz` |  |
| `break_end` | `timestamptz` | Null if ongoing |
| `break_type` | `varchar(30)` | `lunch`, `prayer`, `smoke`, `personal`, `other` |
| `auto_detected` | `boolean` | True if detected by agent idle threshold |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` -> [[database/schemas/core-hr#`employees`|employees]]

---

## `device_sessions`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `employee_id` | `uuid` | FK -> employees |
| `device_id` | `uuid` | FK -> registered_agents |
| `session_start` | `timestamptz` | When active period began |
| `session_end` | `timestamptz` | When active period ended (null if ongoing) |
| `active_minutes` | `int` | Minutes with input activity |
| `idle_minutes` | `int` | Minutes without input |
| `active_percentage` | `decimal(5,2)` | `active / (active + idle) * 100` |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` -> [[database/schemas/core-hr#`employees`|employees]], `device_id` -> [[database/schemas/agent-gateway#`registered_agents`|registered_agents]]

---

## `presence_sessions`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `employee_id` | `uuid` | FK -> employees |
| `date` | `date` | The work day |
| `first_seen_at` | `timestamptz` | First sign of presence (any source) |
| `last_seen_at` | `timestamptz` | Last sign of presence |
| `total_present_minutes` | `int` | Computed from all sources |
| `total_break_minutes` | `int` | Sum of break records |
| `source` | `varchar(20)` | `biometric`, `agent`, `manual`, `mixed` |
| `status` | `varchar(20)` | `present`, `absent`, `partial`, `on_leave` |
| `created_at` | `timestamptz` | Audit |
| `updated_at` | `timestamptz` | Audit |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` -> [[database/schemas/core-hr#`employees`|employees]]

---

## `attendance_records`

Daily attendance summary per employee - one row per employee per work day.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `employee_id` | `uuid` | FK -> employees |
| `date` | `date` | The work day |
| `scheduled_start` | `time` | From shift_assignments for that day |
| `scheduled_end` | `time` | From shift_assignments for that day |
| `actual_start` | `timestamptz` | First check-in (biometric or agent) |
| `actual_end` | `timestamptz` | Last check-out |
| `worked_minutes` | `int` | Total clocked time minus breaks |
| `late_minutes` | `int` | Minutes late vs scheduled start; 0 if on time or early |
| `status` | `varchar(20)` | `present`, `absent`, `late`, `on_leave` |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` -> [[database/schemas/core-hr#`employees`|employees]]

---

## `attendance_corrections`

Employee, manager, or admin corrections to attendance data. Each correction targets a specific presence session or attendance record and follows an approval flow when required by policy.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `employee_id` | `uuid` | FK -> employees |
| `legal_entity_id` | `uuid` | FK -> legal_entities |
| `presence_session_id` | `uuid` | Nullable FK -> presence_sessions |
| `attendance_record_id` | `uuid` | Nullable FK -> attendance_records |
| `correction_type` | `varchar(30)` | `clock_in`, `clock_out`, `break`, `full_day`, `other` |
| `original_clock_in_at` | `timestamptz` | Nullable |
| `original_clock_out_at` | `timestamptz` | Nullable |
| `requested_clock_in_at` | `timestamptz` | Nullable |
| `requested_clock_out_at` | `timestamptz` | Nullable |
| `original_break_json` | `jsonb` | Nullable; original break intervals |
| `requested_break_json` | `jsonb` | Nullable; requested break intervals |
| `reason` | `varchar(255)` | Employee-provided reason |
| `notes` | `text` | Nullable |
| `status` | `varchar(20)` | `pending`, `approved`, `rejected`, `cancelled` |
| `requested_by_id` | `uuid` | FK -> users |
| `reviewed_by_id` | `uuid` | Nullable FK -> users |
| `reviewed_at` | `timestamptz` | Nullable |
| `review_comment` | `text` | Nullable |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` -> [[database/schemas/core-hr#`employees`|employees]], `legal_entity_id` -> [[database/schemas/org-structure#`legal_entities`|legal_entities]], `presence_session_id` -> [[#`presence_sessions`|presence_sessions]], `attendance_record_id` -> [[#`attendance_records`|attendance_records]], `requested_by_id` -> [[database/schemas/infrastructure#`users`|users]], `reviewed_by_id` -> [[database/schemas/infrastructure#`users`|users]]

**Indexes:** `(tenant_id, employee_id, status)`, `(tenant_id, status)`

**Rules:**
- Attendance corrections are only for correcting attendance facts after they happened: clock-in, clock-out, break, full-day attendance, or other attendance-record errors. They must not be used to request or approve planned work area changes
- One pending correction per employee/date/session unless policy allows multiple
- Approved correction updates attendance/presence through service logic, not by manually editing historical agent snapshots
- Approval must create an audit trail entry
- If correction changes clock-in time, recalculate late minutes and reverse/reapply late Time Off deductions with balance audit entries

---

## `schedule_assignments`

Date-effective assignment of a work schedule to the selected company context, department, position, or employee override.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `legal_entity_id` | `uuid` | FK -> legal_entities; selected topbar Company context |
| `work_schedule_id` | `uuid` | FK -> work_schedules |
| `assignment_type` | `varchar(30)` | `full_company`, `department`, `position`, `employee` |
| `department_id` | `uuid` | Nullable FK -> departments; required for department assignment |
| `position_id` | `uuid` | Nullable FK -> positions; required for position assignment |
| `employee_id` | `uuid` | Nullable FK -> employees; required for employee override |
| `effective_from` | `date` |  |
| `effective_to` | `date` | Nullable - null means currently active |
| `is_default_for_new_employee` | `boolean` | Applies only where the assignment is marked as the selected company default |
| `created_by_id` | `uuid` | FK -> users |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `legal_entity_id` -> [[database/schemas/org-structure#`legal_entities`|legal_entities]], `work_schedule_id` -> [[#`work_schedules`|work_schedules]], `department_id` -> [[database/schemas/org-structure#`departments`|departments]], `position_id` -> [[database/schemas/org-structure#`positions`|positions]], `employee_id` -> [[database/schemas/core-hr#`employees`|employees]], `created_by_id` -> [[database/schemas/infrastructure#`users`|users]]

**Rule:** exactly one target is set for `department`, `position`, or `employee`. `full_company` uses null target columns and applies to the selected `legal_entity_id`.

---

## `overtime_records`

Logged overtime per employee per day.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `employee_id` | `uuid` | FK -> employees |
| `date` | `date` |  |
| `overtime_minutes` | `int` | Minutes worked beyond scheduled end |
| `reason` | `varchar(255)` | Nullable |
| `approved_by_id` | `uuid` | FK -> employees (nullable) |
| `status` | `varchar(20)` | `pending`, `approved`, `rejected` |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` -> [[database/schemas/core-hr#`employees`|employees]], `approved_by_id` -> [[database/schemas/core-hr#`employees`|employees]]

---

## `public_holidays`

Country-level or tenant-level non-working days.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants (nullable - null means country-default) |
| `country_id` | `uuid` | FK -> countries |
| `date` | `date` |  |
| `name` | `varchar(100)` | e.g., "National Day" |
| `is_mandatory` | `boolean` | False allows tenant-level override |

**Foreign Keys:** `country_id` -> [[database/schemas/infrastructure#`countries`|countries]]

---

## `roster_entries`

An employee's placement within a roster period.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `roster_period_id` | `uuid` | FK -> roster_periods |
| `employee_id` | `uuid` | FK -> employees |
| `shift_id` | `uuid` | FK -> shifts |
| `date` | `date` |  |
| `expected_work_area` | `varchar(10)` | Nullable. Override expected work area for this roster date. Allowed: `onsite`, `remote`, `either`, `field` |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `roster_period_id` -> [[#`roster_periods`|roster_periods]], `employee_id` -> [[database/schemas/core-hr#`employees`|employees]], `shift_id` -> [[#`shifts`|shifts]]

---

## `roster_periods`

A planning window for shift rosters (e.g., a single week or fortnight).

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `name` | `varchar(100)` | e.g., "Week 15 - Apr 7-13" |
| `start_date` | `date` |  |
| `end_date` | `date` |  |
| `status` | `varchar(20)` | `draft`, `published`, `locked` |
| `created_by_id` | `uuid` | FK -> users |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `created_by_id` -> [[database/schemas/infrastructure#`users`|users]]

---

## `shift_assignments`

Maps an employee to a specific shift for a specific date.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `employee_id` | `uuid` | FK -> employees |
| `shift_id` | `uuid` | FK -> shifts |
| `date` | `date` |  |
| `expected_work_area` | `varchar(10)` | Nullable. Override expected work area for this shift date. Allowed: `onsite`, `remote`, `either`, `field` |
| `is_override` | `boolean` | True if manually overriding the employee's default schedule |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` -> [[database/schemas/core-hr#`employees`|employees]], `shift_id` -> [[#`shifts`|shifts]]

---

## `shifts`

Named shift definitions - the reusable building blocks of schedules.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `name` | `varchar(100)` | e.g., "Morning Shift", "Night Shift" |
| `start_time` | `time` | e.g., `09:00` |
| `end_time` | `time` | e.g., `18:00` |
| `break_minutes` | `int` | Expected total break duration |
| `is_overnight` | `boolean` | True if end_time < start_time |
| `is_active` | `boolean` |  |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]]

---

## `work_schedules`

Work schedule definitions for the Schedules screen. Scheduled working hours equal work time minus break time.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `legal_entity_id` | `uuid` | FK -> legal_entities; selected topbar Company context |
| `name` | `varchar(100)` | Schedule title |
| `workdays_json` | `jsonb` | Selected working days with per-day expected work area. Example: `{"monday": {"enabled": true, "expected_work_area": "onsite"}, "tuesday": {"enabled": true, "expected_work_area": "remote"}}` |
| `default_work_area` | `varchar(10)` | Default expected work area when per-day setting is absent. Allowed: `onsite`, `remote`, `either`, `field` |
| `holiday_country_code` | `char(2)` | Holiday source only. Does not define schedule timezone. Used to fetch candidate public holidays for admin selection |
| `work_hour_type` | `varchar(20)` | `fixed` or `flexible` |
| `start_time` | `time` | Required for fixed work hour. Interpreted in `legal_entities.timezone` for the selected `legal_entity_id` |
| `end_time` | `time` | Required for fixed work hour. Interpreted in `legal_entities.timezone` for the selected `legal_entity_id` |
| `break_start_time` | `time` | Required for fixed work hour when break applies |
| `break_end_time` | `time` | Required for fixed work hour when break applies |
| `daily_duration_minutes` | `int` | Required for flexible work hour |
| `break_duration_minutes` | `int` | Required for flexible work hour when break applies |
| `default_for_new_employee` | `boolean` | Default assignment behavior for new employees in the selected company context |
| `is_active` | `boolean` |  |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `legal_entity_id` -> [[database/schemas/org-structure#`legal_entities`|legal_entities]]

`holiday_country_code` fetches candidate public holidays from the selected country. `work_schedule_holidays` stores which holidays the admin has selected for each schedule. A country holiday that is not selected does not apply to that schedule.

---

## `work_schedule_holidays`

Per-schedule holiday selections. Each row is a holiday that applies to a specific work schedule — either selected from the country's `public_holidays` or manually added by the admin.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `work_schedule_id` | `uuid` | FK -> work_schedules |
| `public_holiday_id` | `uuid` | Nullable FK -> public_holidays. Populated when `source` = `country_public_holiday` |
| `date` | `date` | Holiday date. Copied from `public_holidays.date` for country-sourced rows; entered by admin for manual rows |
| `name` | `varchar(100)` | Holiday name. Copied from `public_holidays.name` for country-sourced rows; entered by admin for manual rows |
| `source` | `varchar(30)` | `country_public_holiday` or `manual` |
| `created_by_id` | `uuid` | FK -> users |
| `created_at` | `timestamptz` | |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `work_schedule_id` -> [[database/schemas/time-attendance#`work_schedules`|work_schedules]], `public_holiday_id` -> [[database/schemas/time-attendance#`public_holidays`|public_holidays]] (nullable), `created_by_id` -> [[database/schemas/infrastructure#`users`|users]]

---

## `work_area_change_requests`

Employee requests to change the expected work area for a specific date. Distinct from `remote_work_location_change_requests` (Configuration), which changes the permanent approved remote work location profile. This table handles one-day work area overrides. All planned one-day work area changes use this table (e.g., planned onsite -> requested remote for today). Do not store these requests in `attendance_corrections`.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `employee_id` | `uuid` | FK -> employees |
| `legal_entity_id` | `uuid` | FK -> legal_entities; selected topbar Company context |
| `date` | `date` | The date the override applies to |
| `shift_assignment_id` | `uuid` | Nullable FK -> shift_assignments; links to specific shift when applicable |
| `current_expected_work_area` | `varchar(10)` | The resolved expected work area before the change request |
| `requested_work_area` | `varchar(10)` | The requested work area. Allowed: `onsite`, `remote`, `either`, `field` |
| `reason` | `text` | Employee-provided reason |
| `status` | `varchar(20)` | `pending`, `approved`, `rejected`, `cancelled` |
| `requested_at` | `timestamptz` |  |
| `reviewed_by_id` | `uuid` | Nullable FK -> users |
| `reviewed_at` | `timestamptz` | Nullable |
| `review_comment` | `text` | Nullable |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` -> [[database/schemas/core-hr#`employees`|employees]], `legal_entity_id` -> [[database/schemas/org-structure#`legal_entities`|legal_entities]], `shift_assignment_id` -> [[#`shift_assignments`|shift_assignments]], `reviewed_by_id` -> [[database/schemas/infrastructure#`users`|users]]

**Indexes:** `(tenant_id, employee_id, date)`, `(tenant_id, status)`

---

## `clock_in_policies`

Clock-in requirement, source control, verification behavior, scope, and effective dates. Each policy is scoped to a company context and targets the full company, departments, positions, or specific employees. Late deduction rules are stored as child rows in `clock_in_late_deduction_rules`.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `legal_entity_id` | `uuid` | FK -> legal_entities; selected topbar Company context |
| `name` | `varchar(120)` | Policy name |
| `scope_type` | `varchar(30)` | `full_company`, `department`, `position`, `employee` |
| `department_ids` | `uuid[]` | Nullable; required when scope_type = department |
| `position_ids` | `uuid[]` | Nullable; required when scope_type = position |
| `employee_ids` | `uuid[]` | Nullable; required when scope_type = employee |
| `effective_from` | `date` | |
| `effective_to` | `date` | Nullable - null means currently active |
| `clock_in_required` | `boolean` | If false, selected people/positions are exempt and late handling is hidden |
| `location_verification_required` | `boolean` | |
| `allowed_radius_meters` | `int` | Nullable; applies to both onsite office and approved remote work location |
| `onsite_biometric_enabled` | `boolean` | |
| `onsite_web_enabled` | `boolean` | |
| `onsite_tray_enabled` | `boolean` | |
| `onsite_photo_required` | `boolean` | |
| `remote_biometric_enabled` | `boolean` | |
| `remote_web_enabled` | `boolean` | |
| `remote_tray_enabled` | `boolean` | |
| `remote_photo_required` | `boolean` | |
| `hybrid_biometric_enabled` | `boolean` | |
| `hybrid_web_enabled` | `boolean` | |
| `hybrid_tray_enabled` | `boolean` | |
| `hybrid_photo_required` | `boolean` | |
| `field_biometric_enabled` | `boolean` | |
| `field_web_enabled` | `boolean` | |
| `field_tray_enabled` | `boolean` | |
| `field_photo_requirement` | `varchar(20)` | `off`, `optional`, `required` |
| `correction_requires_approval` | `boolean` | Whether attendance corrections require manager approval |
| `outage_fallback_enabled` | `boolean` | Allow time-limited onsite web/tray clock-in during biometric outage |
| `notification_recipient_resolver` | `varchar(50)` | e.g., `management_coverage_owner` |
| `is_active` | `boolean` | |
| `created_by_id` | `uuid` | FK -> users |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `legal_entity_id` -> [[database/schemas/org-structure#`legal_entities`|legal_entities]], `created_by_id` -> [[database/schemas/infrastructure#`users`|users]]

**Validation:**
- `legal_entity_id` comes from the selected Company context; the Clock-in Policy form does not expose a legal entity picker
- Scope target ids must belong to the selected `legal_entity_id`
- `effective_to` must be null or >= `effective_from`
- If `clock_in_required` = false, late deduction rules do not apply
- Late deduction rules in `clock_in_late_deduction_rules` reference `clock_in_policies.id`

---

## `clock_in_late_deduction_rules`

Progressive late-arrival deduction rules for a Clock-in Policy. Each rule defines a bracket: minutes beyond a threshold are multiplied and deducted from a selected Time Off type.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `clock_in_policy_id` | `uuid` | FK -> clock_in_policies |
| `late_arrival_minute` | `int` | Bracket threshold in minutes; must be positive |
| `multiplier` | `decimal(5,2)` | Multiplier applied to late minutes in this bracket; 0 = no deduction (free range) |
| `time_off_type_id` | `uuid` | FK -> time_off_types; the Time Off type to deduct from |
| `is_active` | `boolean` | |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `clock_in_policy_id` -> clock_in_policies, `time_off_type_id` -> [[database/schemas/time_off#`time_off_types`|time_off_types]]

**Validation:**
- `late_arrival_minute` must be positive
- `multiplier` must be zero or positive
- `time_off_type_id` is required
- Duplicate `late_arrival_minute` values are not allowed within the same clock-in policy
- Rules must be evaluated in ascending `late_arrival_minute` order

**Bracket evaluation algorithm:**

The first rule creates the first bracket. Every later rule starts from its `late_arrival_minute` and runs until the minute before the next rule. The last rule continues until the actual late minutes.

If the first rule has `multiplier` = 0, it represents the free/no-deduction late range (replaces the old "grace period" concept).

Rules with non-contiguous thresholds: minutes between a zero-multiplier bracket end and the next rule's `late_arrival_minute` remain in the no-deduction range until the next active threshold starts.

---

### Late Deduction Examples

**Example 1** — Three-bracket policy (Annual Time Off):

| Rule | late_arrival_minute | multiplier | Time Off Type |
|:-----|:--------------------|:-----------|:--------------|
| 1 | 10 | 0 | Annual Time Off |
| 2 | 11 | 3 | Annual Time Off |
| 3 | 20 | 5 | Annual Time Off |

**Scenario A:** Employee is late by 10 minutes.
- Minutes 1–10 × multiplier 0 = 0
- **Result:** Deduct 0 minutes from Annual Time Off.

**Scenario B:** Employee is late by 14 minutes.
- Minutes 1–10 × multiplier 0 = 0
- Minutes 11–14 × multiplier 3 = 12
- **Result:** Deduct 12 minutes from Annual Time Off.

**Scenario C:** Employee is late by 23 minutes.
- Minutes 1–10 × multiplier 0 = 0
- Minutes 11–19 × multiplier 3 = 27
- Minutes 20–23 × multiplier 5 = 20
- **Result:** Deduct 47 minutes from Annual Time Off.

**Example 2** — Non-contiguous brackets (Sick Time Off):

| Rule | late_arrival_minute | multiplier | Time Off Type |
|:-----|:--------------------|:-----------|:--------------|
| 1 | 10 | 0 | Sick Time Off |
| 2 | 15 | 3 | Sick Time Off |

**Scenario A:** Employee is late by 8 minutes.
- Actual late minutes are below the first rule threshold range.
- **Result:** Deduct 0 minutes.

**Scenario B:** Employee is late by 13 minutes.
- Minutes 1–10 × multiplier 0 = 0
- Minutes 11–13 have no higher rule yet and remain inside the no-deduction range until the next active threshold starts at 15.
- **Result:** Deduct 0 minutes.

**Scenario C:** Employee is late by 18 minutes.
- Minutes 1–14 are before the 15-minute deduction bracket. Deduction = 0.
- Minutes 15–18 × multiplier 3 = 12
- **Result:** Deduct 12 minutes from Sick Time Off.

---

### Insufficient Balance Rule

If the selected Time Off type does not have enough balance to cover the deduction:
- Record an attendance exception or balance issue on the attendance record.
- Surface the issue to the responsible manager or HR coverage owner.
- Do not silently deduct from another Time Off type.

---

## Related

- [[modules/time-attendance/overview|Time & Attendance Module]]
- [[database/schema-catalog|Schema Catalog]]
- [[database/migration-patterns|Migration Patterns]]
- [[database/performance|Performance]]
