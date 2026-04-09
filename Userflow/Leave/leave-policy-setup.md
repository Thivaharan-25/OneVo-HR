# Leave Policy Setup

**Area:** Leave Management  
**Required Permission(s):** `leave:manage`  
**Related Permissions:** `org:read` (to view legal entities for assignment)

---

## Preconditions

- At least one leave type has been configured: [[Userflow/Leave/leave-type-configuration|Leave Type Configuration Flow]]
- Legal entities exist in the system: [[modules/org-structure/legal-entities/overview|Legal Entities]]
- User has `leave:manage` permission assigned via their Job Family role
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Navigate to Leave Policies
- **UI:** User navigates to Leave → Policies. Sees a list of existing policies with columns: Policy Name, Country, Leave Types Covered, Assigned Legal Entities, Status
- **API:** `GET /api/v1/leave/policies`
- **Backend:** `LeavePolicyService.GetAllAsync()` → [[modules/leave/overview|Leave]]
- **Validation:** Checks `leave:manage` permission via RBAC middleware
- **DB:** `leave_policies` (filtered by `tenant_id`)

### Step 2: Create New Policy
- **UI:** Click "Create Policy" → form page. Fields: Policy Name, Description, Country (dropdown from configured countries)
- **API:** N/A (client-side form entry)
- **Backend:** N/A
- **Validation:** Client-side: Name required, Country required
- **DB:** None

### Step 3: Select Leave Type and Configure Accrual
- **UI:** Section: "Leave Type Configuration" — select a leave type from dropdown → configure: Accrual Method (Yearly Lump Sum / Monthly Accrual / Pro-rata by Join Date), Accrual Start (Immediately / After Probation / After N Months). If monthly: show days accrued per month. If pro-rata: show calculation preview based on example join date
- **API:** N/A (client-side form entry)
- **Backend:** N/A
- **Validation:** Accrual days per month × 12 should not exceed the leave type's max annual days
- **DB:** None

### Step 4: Configure Probation and Tenure Rules
- **UI:** Section: "Eligibility Rules" — fields: Probation Period Restriction (toggle — if on, no leave during probation), Minimum Tenure for Eligibility (months, 0 = immediate), Reduced Entitlement During First Year (toggle — if on, show percentage field, e.g., 50%)
- **API:** N/A (client-side form entry)
- **Backend:** N/A
- **Validation:** Minimum tenure must be ≥ 0. Percentage must be 1–100
- **DB:** None

### Step 5: Configure Notice Period and Limits
- **UI:** Section: "Request Rules" — fields: Minimum Notice Period (days before leave start date), Maximum Consecutive Days, Minimum Days Per Request (e.g., 0.5 for half-day), Blackout Periods (date ranges when leave cannot be taken), Maximum Team Absence % (e.g., only 20% of team can be on leave simultaneously)
- **API:** N/A (client-side form entry)
- **Backend:** N/A
- **Validation:** Notice period must be ≥ 0. Max consecutive ≤ annual entitlement
- **DB:** None

### Step 6: Add Additional Leave Types (Repeat Step 3–5)
- **UI:** Click "Add Another Leave Type" → repeat configuration for each leave type the policy covers (e.g., Annual, Sick, Compassionate all in one policy)
- **API:** N/A
- **Backend:** N/A
- **Validation:** Same leave type cannot appear twice in one policy
- **DB:** None

### Step 7: Assign Policy to Legal Entity
- **UI:** Section: "Assignment" — multi-select dropdown of legal entities → select one or more → option to set effective date (defaults to today)
- **API:** N/A (client-side form entry)
- **Backend:** N/A
- **Validation:** A legal entity can only have one active policy per country at a time. Warning if replacing existing policy
- **DB:** None

### Step 8: Save Policy
- **UI:** Click "Save & Activate" button. Confirmation dialog if replacing an existing policy for any legal entity. Success toast shown
- **API:** `POST /api/v1/leave/policies`
- **Backend:** `LeavePolicyService.CreateAsync()` → [[modules/leave/overview|Leave]]
  1. Validates policy configuration
  2. Creates `leave_policies` record with nested `leave_policy_rules` for each leave type
  3. Creates `leave_policy_assignments` linking policy to legal entities
  4. Publishes `LeavePolicyCreatedEvent`
  5. If replacing existing policy: deactivates previous policy, triggers entitlement recalculation
- **Validation:** Policy name unique per tenant. No duplicate leave types within policy. Legal entity assignment conflicts checked
- **DB:** `leave_policies`, `leave_policy_rules`, `leave_policy_assignments`, `audit_logs`

## Variations

### When editing an existing policy
- Changes to accrual methods apply from next entitlement cycle
- Changes to limits apply immediately to new requests
- Existing approved requests unaffected
- API: `PUT /api/v1/leave/policies/{policyId}`

### When cloning a policy for another country
- Click "Clone" on existing policy → pre-fills all rules → change country and adjust country-specific rules (e.g., statutory minimums)
- API: `POST /api/v1/leave/policies/{policyId}/clone`

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Duplicate policy name | `409 Conflict` returned | "A policy with this name already exists" |
| Legal entity already has active policy | Warning dialog | "Legal Entity X already has an active policy. Activating this policy will replace it. Continue?" |
| Leave type not found | `404 Not Found` | "The selected leave type no longer exists" |
| Accrual exceeds annual max | Validation fails | "Monthly accrual (N × 12 = M days) exceeds the leave type's annual limit of X days" |
| Missing country | Validation fails | "Country is required to determine statutory compliance" |

## Events Triggered

- `LeavePolicyCreatedEvent` → [[backend/messaging/event-catalog|Event Catalog]] — triggers entitlement generation for employees in assigned legal entities
- `LeavePolicyUpdatedEvent` → [[backend/messaging/event-catalog|Event Catalog]] — triggers entitlement recalculation
- `AuditLogEntry` (action: `leave_policy.created`) → [[modules/auth/audit-logging/overview|Audit Logging]]

## Related Flows

- [[Userflow/Leave/leave-type-configuration|Leave Type Configuration]] — configure the leave types referenced by policies
- [[Userflow/Leave/leave-entitlement-assignment|Leave Entitlement Assignment]] — entitlements generated from policy rules
- [[Userflow/Leave/leave-request-submission|Leave Request Submission]] — policies govern request validation rules

## Module References

- [[modules/leave/overview|Leave]] — leave module overview and architecture
- [[modules/leave/leave-policies/overview|Leave Policies]] — policy data model and business rules
- [[modules/leave/leave-types/overview|Leave Types]] — leave type definitions
- [[modules/org-structure/legal-entities/overview|Legal Entities]] — organizational entities policies are assigned to
