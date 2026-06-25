# Time Off Balance Audit

**Module:** Time Off
**Feature:** Balance Audit

---

## Purpose

Append-only audit trail for all Time Off balance changes. Time Off balances are stored in minutes (integer), so audit amounts are stored in minutes too.

## Database Tables

### `time_off_balances_audit`

Core fields:

| Column | Notes |
|:-------|:------|
| `employee_id` | Employee whose balance changed |
| `time_off_type_id` | Time Off type affected |
| `attendance_record_id` | Nullable; populated for late-arrival deductions from Time & Attendance |
| `change_type` | `accrual`, `deduction`, `carry_forward`, `forfeiture`, `adjustment`, `late_deduction` |
| `minutes_changed` | Positive for added/restored minutes, negative for deducted/forfeited minutes |
| `balance_after_minutes` | Remaining balance in minutes after the change |
| `source` | `time_off`, `time_attendance`, `manual`, `system` |
| `calculation_snapshot_json` | Nullable; stores bracket calculation details for late deductions |
| `reason` | Human-readable reason or system job context |
| `created_at` | Audit timestamp |

Day equivalents can be shown in UI as derived display values only; minutes are the canonical audit unit.

### Late Deduction Audit Entry

Every late-arrival deduction from Time & Attendance must create a balance audit entry:

| Field | Value |
|:------|:------|
| `change_type` | `late_deduction` |
| `source` | `time_attendance` |
| `attendance_record_id` | The attendance record that triggered the deduction |
| `minutes_changed` | Negative deduction amount |
| `calculation_snapshot_json` | Bracket calculation details (rules applied, minutes per bracket, multipliers) |
| `reason` | "Late arrival deduction" |
| `created_by_id` | null (system) |

The audit must allow HR/admin to understand why a balance changed, including which Clock-in Policy rules were applied and how the deduction was calculated.

## Related

- [[modules/time-off/overview|Time Off Module]]
- [[modules/time-off/time-off-requests/overview|Time Off Requests]]
- [[modules/time-off/time-off-entitlements/overview|Time Off Entitlements]]
- [[modules/time-off/time-off-policies/overview|Time Off Policies]]
- [[modules/time-off/time-off-types/overview|Time Off Types]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
- [[security/data-classification|Data Classification]]
- [[modules/configuration/retention-policies/overview|Retention Policies]]
- [[current-focus/DEV1-time_off|DEV1: Time Off]]
