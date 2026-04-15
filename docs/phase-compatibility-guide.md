# Phase 1 → Phase 2 Compatibility Guide

**Purpose:** Ensure Phase 1 tables are designed so Phase 2 modules can be added without breaking migrations, data loss, or application conflicts.

> **Rule:** Phase 1 tables must never need a destructive change (column drop, type change, rename) when Phase 2 launches. Only additive changes (new columns, new tables, new FK references) are allowed. This guide documents every Phase 1 → Phase 2 dependency and confirms it is safe.

---

## How to Read This Guide

Each entry covers:
- **Phase 1 table** that Phase 2 depends on
- **Phase 2 module** that extends or reads it
- **Column names** Phase 2 will reference (verify exact spelling before Phase 2 build)
- **Safety verdict** and any preparation needed

---

## Employee Salary → Payroll

**Phase 1 table:** `employee_salary_history` (Core HR)
**Phase 2 module:** Payroll

### Columns Phase 2 Payroll reads:
| Column | Type | Phase 2 Use |
|:-------|:-----|:------------|
| `base_salary` | `decimal(15,2)` | Starting salary for payroll calculation |
| `currency_code` | `varchar(3)` | Currency for payslip generation |
| `effective_date` | `date` | When salary became effective |
| `change_reason` | `varchar(100)` | `hire`, `promotion`, `annual_review`, `adjustment` |

**Verdict: ✓ Safe.** Phase 2 Payroll reads these columns as-is. No conflict. When an employee is onboarded in Phase 1, their salary is recorded here. Phase 2 Payroll builds its `payslips` table on top — it never modifies `employee_salary_history`, only appends to it.

---

## Skills Core → Skills Full Module + WMS

**Phase 1 tables:** `skill_categories`, `skills`, `job_skill_requirements`, `employee_skills`, `skill_validation_requests`
**Phase 2 additions:** `courses`, `lms_providers`, `course_enrollments`, `development_plans`, `development_plan_items`, `skill_questions`, `skill_question_options`, `skill_assessment_responses`, `employee_certifications`, `course_skill_tags`

### Key columns Phase 2 extends:

| Table | Column | Phase 2 Dependency |
|:------|:-------|:-------------------|
| `employee_skills` | `last_assessed_in_review_id` | FK → `review_cycles` (Phase 2). NULL in Phase 1 — safe. |
| `employee_skills` | `source` | Added in Phase 1 for WMS. Phase 2 adds `assessment_result` as a new source value. |
| `skills` | `id` | Referenced by `course_skill_tags` and `skill_questions` (Phase 2) |
| `job_skill_requirements` | `min_proficiency` | Used by Phase 2 gap analysis and course recommendations |

**Verdict: ✓ Safe.** Phase 2 only adds new tables and one FK from `employee_skills.last_assessed_in_review_id` (already nullable). The `source` column added in Phase 1 covers WMS gaps — Phase 2 simply adds `assessment_result` as a new allowed value (additive).

---

## Productivity Analytics → Performance Module

**Phase 1 tables:** `daily_employee_report`, `weekly_employee_report`, `monthly_employee_report`, `wms_productivity_snapshots`
**Phase 2 module:** Performance (review cycles, goals, appraisals)

### Interface:

```csharp
// Phase 2 Performance module calls this:
IProductivityAnalyticsService.GetProductivityScoreAsync(employeeId, period)
// Returns composite score from agent-based reports + wms_productivity_snapshots
```

**Verdict: ✓ Safe.** Performance module uses `IProductivityAnalyticsService` as an abstraction — it never directly queries the underlying tables. The `wms_productivity_snapshots` table is added in Phase 1 so the bridge can start receiving WMS data immediately. Phase 2 Performance reads both sources through the service interface.

---

## Leave → Payroll

**Phase 1 tables:** `leave_requests`, `leave_entitlements`, `leave_balances_audit`
**Phase 2 module:** Payroll

### Columns Phase 2 Payroll reads:
| Table | Column | Phase 2 Use |
|:------|:-------|:------------|
| `leave_requests` | `total_days` | Days to deduct from payroll |
| `leave_requests` | `status` | Only `approved` requests affect payroll |
| `leave_requests` | `start_date`, `end_date` | Payroll period matching |
| `leave_entitlements` | `balance_days` | Verify against leave request |

**Verdict: ✓ Safe.** Payroll reads leave data as input — never writes to leave tables. All columns are already correctly typed in Phase 1.

---

## Workforce Presence → Payroll

**Phase 1 tables:** `presence_sessions`, `overtime_records`, `attendance_records`
**Phase 2 module:** Payroll

### Columns Phase 2 Payroll reads:
| Table | Column | Phase 2 Use |
|:------|:-------|:------------|
| `presence_sessions` | `total_minutes` | Actual hours for payroll |
| `overtime_records` | `overtime_minutes` | Overtime pay calculation |
| `attendance_records` | `status` | Absent days for deductions |

**Verdict: ✓ Safe.** Payroll reads presence data as reference — never modifies it.

---

## Calendar → Google Calendar Sync (Phase 2)

**Phase 1 table:** `calendar_events`
**Phase 2 feature:** Google Calendar sync (OAuth 2.0)

### Columns added to Phase 1 for Phase 2 readiness:
| Column | Type | Phase 2 Use |
|:-------|:-----|:------------|
| `external_id` | `varchar(255)` | Google Calendar event ID for deduplication |
| `external_source` | `varchar(30)` | `google_calendar`, `outlook`, `ical` |

Both are nullable — NULL in Phase 1. When Phase 2 syncs Google Calendar events, these fields are populated. Existing Phase 1 events are unaffected.

**Verdict: ✓ Safe.** Columns are additive and nullable. No Phase 1 code reads them (except to display in UI where they can simply be ignored when null).

---

## Employee Lifecycle Events → Performance + Payroll

**Phase 1 table:** `employee_lifecycle_events`
**Phase 2 modules:** Performance (reads promotion history for review context), Payroll (reads salary_change events)

### Event types used by Phase 2:
- `promoted` → Performance uses to set review baseline; Payroll uses to apply new salary
- `salary_change` → Payroll uses to recalculate
- `terminated` → Payroll final settlement

**Verdict: ✓ Safe.** All event types are already in Phase 1 `event_type` enum. Phase 2 modules only read this table — never modify. `details_json` (JSONB) is flexible enough for Phase 2 to add richer data without schema changes.

---

## Auth (RBAC) → All Phase 2 Modules

**Phase 1 tables:** `roles`, `permissions`, `role_permissions`, `user_permission_overrides`
**Phase 2 modules:** Payroll, Performance, Skills, Documents, etc.

Phase 2 modules add their own permissions to the `permissions` table:
```
payroll:read, payroll:write, payroll:run, payroll:approve
performance:read, performance:write, performance:manage
skills:validate, skills:manage
documents:read, documents:write, documents:manage
```

**Verdict: ✓ Safe.** Permissions table uses string keys (`resource:action`). Phase 2 simply inserts new rows — completely additive. No existing rows change.

---

## Notifications → Phase 2 Modules

**Phase 1 tables:** `notification_templates`, `notification_channels`
**Phase 2 additions:** New notification types for Performance, Payroll, Documents

Phase 2 inserts new templates into `notification_templates` for its events. Existing templates are untouched.

**Verdict: ✓ Safe.** Additive inserts only.

---

## Skills Phase 1 → WMS Skill Gap Bridge (Phase 2)

**Phase 1 table:** `employee_skills` (with `source` column added)
**WMS bridge:** `POST /api/v1/bridges/skills/{employeeId}/gap-report`

When WMS observes a skill gap:
1. Bridge creates/updates `employee_skills` row with `source = 'wms_observed'`, `status = 'pending'`
2. Creates `skill_validation_requests` entry flagging the issue for manager review
3. Skills dashboard surfaces `wms_observed` items at the top

**Verdict: ✓ Safe.** The `source` column addition in Phase 1 is specifically to support this without any Phase 2 migration. The `status` field (`pending`, `validated`, `expired`) already handles the workflow.

---

## WMS Bridges → Discrepancy Engine

**Phase 1 table:** `wms_daily_time_logs` (new, in Activity Monitoring schema)
**Consumer:** Discrepancy Engine (runs nightly)

If no WMS integration → `wms_daily_time_logs` is empty → Discrepancy Engine sets `wms_logged_minutes = 0` and only uses calendar cross-reference. Already handled by business rule:
> "WMS bridge is optional. If the tenant has no WMS integration, `wms_logged_minutes = 0` and only the calendar cross-reference is used."

**Verdict: ✓ Safe.** Optional dependency, gracefully handled.

---

## WMS Productivity Data → Phase 2 Performance Reviews

**Phase 1 table:** `wms_productivity_snapshots` (new, in Productivity Analytics schema)
**Phase 2 module:** Performance (review cycles)

The Performance module's review creation checks `include_productivity_data` flag on `review_cycles`. When true, it calls `IProductivityAnalyticsService.GetProductivityScoreAsync()` which aggregates:
1. Agent-based scores from `daily_employee_report` / `monthly_employee_report`
2. WMS-based scores from `wms_productivity_snapshots`

**Verdict: ✓ Safe.** `wms_productivity_snapshots` is already built in Phase 1. Phase 2 Performance simply reads it. No migration needed.

---

## Summary Table

| Phase 1 → Phase 2 | Safe? | Prep needed? |
|:------------------|:------|:-------------|
| `employee_salary_history` → Payroll | ✓ | None — columns match |
| `employee_skills` → Skills full module | ✓ | `source` column added |
| `employee_skills.last_assessed_in_review_id` → Performance | ✓ | Already nullable |
| `daily/weekly/monthly_employee_report` → Performance | ✓ | Via service interface |
| `wms_productivity_snapshots` → Performance | ✓ | Table exists Phase 1 |
| `leave_requests` → Payroll | ✓ | Columns correct |
| `presence_sessions` → Payroll | ✓ | None |
| `calendar_events` → Google Calendar sync | ✓ | `external_id` + `external_source` added |
| `employee_lifecycle_events` → Performance + Payroll | ✓ | All event types present |
| `roles` + `permissions` → all Phase 2 modules | ✓ | Additive inserts only |
| `notification_templates` → Phase 2 modules | ✓ | Additive inserts only |
| `wms_daily_time_logs` → Discrepancy Engine | ✓ | Graceful empty-table handling |
| `job_skill_requirements` → Skill gap analysis | ✓ | `min_proficiency` correct type |

**All Phase 1 → Phase 2 transitions are safe and additive. No destructive migrations required.**
