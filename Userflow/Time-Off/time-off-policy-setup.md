# Time Off Policy Setup

**Area:** Time Off
**Trigger:** Authorized management user creates or edits time_off rules and assignment scope inside the selected Company context
**Required Permission(s):** `time_off:manage`
**Related Permissions:** `org:read` (to view assignment targets)

---

## Purpose

Time Off Type defines the kind of time_off. Time Off Policy defines who gets which rule set for that time_off.

Policy is the source of truth for entitlement amount, accrual, carry-forward, proration, eligibility, document requirements, notice period, request limits, and assignment scope. Balances are stored in minutes. Admin enters entitlement in hours/minutes; the system stores the canonical value in minutes.

Time Off Policy Setup is Company-context first. The topbar-selected Company is the policy owner. The user must have time off policy permission through their position/access in that Company. To create policies for another Company, the user switches Company in the topbar and permission is checked again.

## Preconditions

- At least one time off type exists: [[Userflow/Time-Off/time-off-type-configuration|Time Off Type Configuration]]
- A Company is selected in the topbar.
- Departments and positions exist inside the selected Company when used as assignment targets.
- User has `time_off:manage` in the selected Company.

## Flow Steps

### Step 1: Open Time Off Policies
- **UI:** Authorized user opens the Time Off management area and selects **Time Off Policies**.
- **API:** `GET /api/v1/time-off/policies`
- **Backend:** `TimeOffPolicyService.GetAllAsync()` -> [[modules/time-off/overview|Time Off]]
- **DB:** `time_off_policies`, `time_off_policy_rules`, `time_off_policy_assignments`

Avoid obsolete navigation wording that implies an old disconnected route. Describe the screen ownership instead.

### Step 2: Create Policy
- **UI:** Click "Create Policy".
- **Fields:**
  - Policy name
  - Description
  - Country or statutory context, if applicable
  - Effective date
  - Active/inactive toggle where supported

The form does not expose Company as a free assignment field. The selected Company context resolves to `legal_entity_id`; persist only `legal_entity_id`.

### Step 3: Add Time Off Rules
- **UI:** Select one or more time off types and configure policy-owned rules for each:
  - Annual entitlement in hours and minutes (stored canonically in minutes)
  - Accrual method
  - Proration method
  - Carry-forward allowed/not allowed
  - Carry-forward limit in hours/minutes and expiry
  - Rollover period: monthly, yearly, or policy period
  - Probation and tenure eligibility
  - Notice period
  - Minimum request duration in hours/minutes
  - Maximum consecutive Time Off in hours/minutes
  - Supporting document requirement and threshold
  - Unpaid/over-balance behavior where supported
- **Validation:** The same time off type cannot be duplicated inside one policy unless the implementation explicitly supports multiple date-effective rule rows.

### Step 4: Assign Policy Scope
- **UI:** Select assignment targets:
  - Company default for the selected Company, stored as `legal_entity_default`
  - Department, including multi-select if supported
  - Position, including multi-select if supported
  - Employee-specific override only when intentionally supported
- **Rule:** Assignment scope determines which employees receive the policy output inside the selected Company. Do not imply cross-Company assignment from this screen.

### Step 5: Save Policy
- **API:** `POST /api/v1/time-off/policies`
- **Backend:** `TimeOffPolicyService.CreateAsync()`
- **DB:** `time_off_policies`, `time_off_policy_rules`, `time_off_policy_assignments`, `audit_logs`
- **Result:** Entitlements can be generated or recalculated for employees in the policy scope. Entitlement is stored in minutes.

## Variations

### Editing policy
- Policy changes apply based on effective dates.
- Existing approved time off requests are not retroactively rejected.
- Entitlements may need recalculation for affected future/current periods.

### Replacing active policy
- If an assignment target already has an active policy, user sees a replacement warning.
- The system closes the old policy with `effective_to` and creates/activates the new policy from its `effective_from` date.
- Users do not manually manage technical replacement states.

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Duplicate policy name | `409 Conflict` | "A policy with this name already exists" |
| Assignment target already has active policy | Warning or validation | "This target already has an active policy" |
| Time off type not found | `404 Not Found` | "The selected time off type no longer exists" |
| Invalid rule values | Validation fails | Specific rule error |

## Events Triggered

- `TimeOffPolicyCreatedEvent` -> entitlement generation/recalculation consumers
- `TimeOffPolicyUpdatedEvent` -> entitlement recalculation consumers
- `AuditLogEntry` (action: `time_off_policy.created`) -> audit logging

## Related Flows

- [[Userflow/Time-Off/time-off-type-configuration|Time Off Type Configuration]] - defines available time off types
- [[Userflow/Time-Off/time-off-entitlement-assignment|Time Off Entitlement Assignment]] - employee-level output from policy assignment
- [[Userflow/Time-Off/time-off-request-submission|Time Off Request Submission]] - policies govern request validation

## Module References

- [[modules/time-off/overview|Time Off]]
- [[modules/time-off/time-off-policies/overview|Time Off Policies]]
- [[modules/time-off/time-off-types/overview|Time Off Types]]
