# Time Off Policies

**Module:** Time Off
**Feature:** Time Off Policies

---

## Purpose

Defines who gets which time_off rules. Time Off Type defines the kind of time_off and allowed request modes; Time Off Policy defines the rules and assignment scope for that time_off.

Policy is the source of truth for entitlement amount, accrual, proration, carry-forward, eligibility, document requirements, notice period, request limits, and assignment scope. Balances are stored in minutes. Admin enters entitlement in hours/minutes; the system stores the canonical value in minutes.

Policies are created inside the topbar-selected Company. The backend must check that the actor has time off policy permission in that Company. To manage another Company's policies, the actor switches Company context first.

## Database Tables

### `time_off_policies`

Policy header and effective dating. Key columns can include `tenant_id`, `legal_entity_id`, `name`, statutory/country context, `effective_from`, `effective_to`, and `is_active`. The UI selected Company resolves to `legal_entity_id`; persist only `legal_entity_id`. Do not store per-time-off-type entitlement, carry-forward, notice, or request-limit fields on the policy header when `time_off_policy_rules` exists.

### `time_off_policy_rules`

Rules per time off type inside a policy. Key rule data:

- `time_off_type_id`
- `entitlement_minutes`: annual entitlement in minutes (admin enters hours/minutes in UI)
- `accrual_method`: yearly, monthly, prorated as supported
- `proration_method`: calendar days, working days as supported
- `carry_forward_allowed`
- `carry_forward_limit_minutes`
- `carry_forward_expiry`
- `rollover_period`: monthly, yearly, or policy period
- probation/tenure eligibility
- notice period
- `minimum_request_minutes`
- `max_consecutive_minutes`
- supporting document threshold
- unpaid/over-balance behavior where supported

### `time_off_policy_assignments`

Assignment scope inside the selected Company: `legal_entity_default` shown as Company default in UI, department, position, or employee override.

## Key Business Rules

- One source of truth per rule: do not duplicate carry-forward or document requirements in Time Off Types.
- Company context is not chosen inside the policy form; it comes from the topbar-selected Company, resolves to `legal_entity_id`, and permission is checked against that Company.
- Entitlement is entered in hours/minutes and stored canonically in minutes. No day-based entitlement input.
- Carry-forward is not universally yearly; policy defines whether it is allowed, limit in minutes, expiry, and rollover period.
- Multiple departments or positions can be selected when the product supports multi-select.
- Policy assignment produces employee-level minute entitlements for a period.
- Effective dating should preserve historical requests and balances.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/time-off/policies` | `time_off:manage` | List policies |
| POST | `/api/v1/time-off/policies` | `time_off:manage` | Create policy |

## Related

- [[modules/time-off/overview|Time Off Module]]
- [[modules/time-off/time-off-types/overview|Time Off Types]]
- [[modules/time-off/time-off-entitlements/overview|Time Off Entitlements]]
- [[modules/time-off/time-off-requests/overview|Time Off Requests]]
