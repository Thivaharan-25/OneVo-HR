# Time Off - Schema

**Module:** [[modules/time-off/overview|Time Off]]
**Phase:** Phase 1
**Canonical balance unit:** minutes

---

## Balance Unit Rule

Time Off balances are stored and calculated in **minutes** (integer). All entitlement, used, available, carry-forward, adjustment, request duration, and deduction fields use minute values.

Admin enters policy entitlement in hours and minutes. The system stores the canonical value in minutes. The UI displays balances as hours and minutes (e.g., "16h 30m available"). An optional approximate day helper may be shown in the UI for readability, but it is never used for calculation or storage.

Approved deductions keep the deducted minutes captured at approval time. Later schedule changes do not recalculate past approved Time Off unless an authorized admin explicitly recalculates and audits it.

---

## `time_off_balances_audit`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | |
| `employee_id` | `uuid` | FK -> employees |
| `time_off_type_id` | `uuid` | FK -> time_off_types |
| `policy_id` | `uuid` | FK -> time_off_policies, nullable for manual adjustments |
| `entitlement_id` | `uuid` | FK -> time_off_entitlements, nullable |
| `time_off_request_id` | `uuid` | FK -> time_off_requests, nullable |
| `attendance_record_id` | `uuid` | FK -> attendance_records, nullable; populated for late-arrival deductions |
| `change_type` | `varchar(20)` | `accrual`, `deduction`, `carry_forward`, `forfeiture`, `adjustment`, `late_deduction` |
| `minutes_changed` | `int` | Positive or negative |
| `balance_after_minutes` | `int` | Balance after mutation |
| `source` | `varchar(30)` | `time_off`, `time_attendance`, `manual`, `system` |
| `calculation_snapshot_json` | `jsonb` | Nullable; stores bracket calculation details for late deductions |
| `reason` | `varchar(255)` | |
| `created_by_id` | `uuid` | FK -> users, nullable for system jobs |
| `created_at` | `timestamptz` | |

---

## `time_off_entitlements`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | |
| `legal_entity_id` | `uuid` | FK -> legal_entities |
| `employee_id` | `uuid` | FK -> employees |
| `time_off_type_id` | `uuid` | FK -> time_off_types |
| `period_year` | `int` | Or policy period key |
| `policy_id` | `uuid` | FK -> time_off_policies |
| `entitlement_minutes` | `int` | Canonical entitlement balance in minutes |
| `used_minutes` | `int` | Updated on approval or late deduction |
| `pending_minutes` | `int` | Pending requests when stored |
| `carried_forward_minutes` | `int` | From previous policy period |
| `available_minutes` | `int` | Computed or stored as implemented |

---

## `time_off_policies`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `legal_entity_id` | `uuid` | FK -> legal_entities; derived from the selected Company context in the topbar |
| `name` | `varchar(100)` | |
| `country_id` | `uuid` | Nullable statutory context |
| `is_active` | `boolean` | Active within the selected Company context |
| `effective_from` | `date` | |
| `effective_to` | `date` | Nullable; closes the old policy when a replacement starts |
| `created_at` | `timestamptz` | |

Policy header and effective dating live in `time_off_policies`. Per-time-off-type entitlement and request rules live in `time_off_policy_rules`. Assignment scope lives in `time_off_policy_assignments`.

Time Off policies are stored against `legal_entity_id`. The UI shows this as the selected Company from the topbar and must check that the actor has Time Off policy permission in that Company. To create policy for another Company, the actor switches Company context first and permission is checked again.

---

## `time_off_policy_rules`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | |
| `policy_id` | `uuid` | FK -> time_off_policies |
| `time_off_type_id` | `uuid` | FK -> time_off_types |
| `entitlement_minutes` | `int` | Annual entitlement in minutes. Admin enters hours/minutes in UI |
| `accrual_method` | `varchar(20)` | `yearly`, `monthly`, `prorated` as supported |
| `proration_method` | `varchar(20)` | `calendar_days`, `working_days` as supported |
| `carry_forward_allowed` | `boolean` | |
| `carry_forward_limit_minutes` | `int` | Nullable |
| `carry_forward_expiry` | `varchar(50)` | Nullable policy period/month/date expression |
| `rollover_period` | `varchar(20)` | `monthly`, `yearly`, or `policy_period` |
| `minimum_request_minutes` | `int` | Nullable |
| `max_consecutive_minutes` | `int` | Nullable; unlimited when null |
| `notice_period_days` | `int` | Nullable |
| `created_at` | `timestamptz` | |

Policy rules inherit `legal_entity_id` through `policy_id`. Do not duplicate the Company/legal entity scope on each rule row unless a physical denormalization is intentionally added with a constraint that matches the parent policy.

---

## `time_off_policy_assignments`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | |
| `policy_id` | `uuid` | FK -> time_off_policies |
| `scope_type` | `varchar(30)` | `legal_entity_default`, `department`, `position`, or `employee_override` |
| `scope_id` | `uuid` | Nullable only for `legal_entity_default` |
| `effective_from` | `date` | Date-effective assignment start |
| `effective_to` | `date` | Nullable |
| `created_at` | `timestamptz` | |

Policy assignments inherit `legal_entity_id` through `policy_id`. Assignment priority should match policy resolution rules inside the selected Company: employee override, position, department, then `legal_entity_default`. The UI may label `legal_entity_default` as Company default.

---

## `time_off_requests`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | |
| `employee_id` | `uuid` | FK -> employees |
| `time_off_type_id` | `uuid` | FK -> time_off_types |
| `start_date` | `date` | |
| `end_date` | `date` | |
| `start_time` | `time` | Nullable; used when the user specifies exact start time |
| `end_time` | `time` | Nullable; used when the user specifies exact end time |
| `request_duration_minutes` | `int` | Required; canonical requested Time Off duration in minutes |
| `deduction_minutes` | `int` | Actual approved deduction in minutes; captured at approval time |
| `reason` | `text` | |
| `status` | `varchar(20)` | `pending`, `approved`, `rejected`, `cancelled` |
| `approved_by_id` | `uuid` | FK -> users |
| `approved_at` | `timestamptz` | |
| `conflict_snapshot_json` | `jsonb` | Calendar conflicts at submission time |
| `document_file_id` | `uuid` | FK -> file_records, nullable |
| `created_at` | `timestamptz` | |

---

## `time_off_types`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `name` | `varchar(50)` | e.g., Annual, Sick, Maternity |
| `code` | `varchar(30)` | Unique per tenant where implemented |
| `description` | `text` | Nullable |
| `is_paid` | `boolean` | Type-level classification if supported |
| `requires_document` | `boolean` | Whether supporting document is required |
| `is_active` | `boolean` | |
| `created_at` | `timestamptz` | |

Phase 1 does not persist full-day or half-day as canonical request modes. All requests store `request_duration_minutes`. If UI shortcuts like full-day or half-day are added later, they must convert to explicit minutes before saving. Consecutive limits, entitlement amount, carry-forward, notice, and document threshold belong to Time Off Policies.

---

## Related

- [[modules/time-off/overview|Time Off Module]]
- [[database/schema-catalog|Schema Catalog]]
- [[database/migration-patterns|Migration Patterns]]
- [[database/performance|Performance]]
