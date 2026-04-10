# Leave Entitlement Assignment

**Area:** Leave Management  
**Trigger:** System auto-assigns on employee creation or year rollover (system-triggered — scheduled/reaction)
**Required Permission(s):** `leave:manage`  
**Related Permissions:** `employee:read` (to view employee details)

---

## Preconditions

- Leave policies have been created and assigned to legal entities: [[Userflow/Leave/leave-policy-setup|Leave Policy Setup Flow]]
- Employees exist and are assigned to a legal entity
- User has `leave:manage` permission assigned via their Job Family role
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Navigate to Leave Entitlements
- **UI:** User navigates to Leave → Entitlements. Sees dashboard: total employees, entitlements generated count, pending generation count. Table of entitlements with columns: Employee, Leave Type, Annual Entitlement, Carry Forward, Used, Pending, Remaining
- **API:** `GET /api/v1/leave/entitlements?year={year}`
- **Backend:** `LeaveEntitlementService.GetAllAsync()` → [[modules/leave/overview|Leave]]
- **Validation:** Checks `leave:manage` permission via RBAC middleware
- **DB:** `leave_entitlements` (filtered by `tenant_id`, `year`)

### Step 2a: Auto-Generate Entitlements (Bulk)
- **UI:** Click "Auto-Generate Entitlements" → select year → select legal entity (or All) → preview shows: number of employees affected, entitlements per leave type based on policy → click "Generate"
- **API:** `POST /api/v1/leave/entitlements/generate`
- **Backend:** `LeaveEntitlementService.GenerateBulkAsync()` → [[modules/leave/overview|Leave]]
  1. Fetches all active employees in selected legal entity
  2. For each employee, determines applicable policy via legal entity assignment
  3. Calculates entitlement per leave type based on accrual method:
     - Yearly: full annual amount
     - Monthly: annual amount (accrues monthly)
     - Pro-rata: calculates based on join date within the year
  4. Checks probation status — if in probation and policy restricts, sets entitlement to 0 or reduced amount
  5. Calculates carry-forward from previous year's remaining balance (capped at policy max)
  6. Creates `leave_entitlements` records
- **Validation:** Cannot generate if entitlements already exist for the period (must use recalculate). Employee must have active employment status
- **DB:** `leave_entitlements`, `employees`, `leave_policies`, `leave_policy_rules`, `leave_policy_assignments`

### Step 2b: Manual Entitlement Assignment (Individual)
- **UI:** Click "Manual Assignment" → search and select employee → select leave type → enter fields: Annual Entitlement Days, Carry Forward Days (from previous year), Reason for Manual Assignment (required)
- **API:** `POST /api/v1/leave/entitlements`
- **Backend:** `LeaveEntitlementService.CreateManualAsync()` → [[modules/leave/overview|Leave]]
  1. Creates entitlement record with `source = manual`
  2. Records the admin who created it and reason
  3. Creates audit log entry
- **Validation:** Cannot create duplicate entitlement for same employee + leave type + year. Days must be positive. Reason required for audit compliance
- **DB:** `leave_entitlements`, `audit_logs`

### Step 3: Review Generated Entitlements
- **UI:** After generation, results page shows: Successful (count), Skipped (count, with reasons — e.g., already exists, inactive employee), Errors (count). Expandable list of each category. Option to download report as CSV
- **API:** Response from generation endpoint includes summary
- **Backend:** N/A (response rendering)
- **Validation:** N/A
- **DB:** None

### Step 4: Adjust Individual Entitlement (Optional)
- **UI:** From entitlements list → click employee row → Edit → modify Annual Entitlement or Carry Forward → enter reason → Save
- **API:** `PUT /api/v1/leave/entitlements/{entitlementId}`
- **Backend:** `LeaveEntitlementService.UpdateAsync()` → [[modules/leave/overview|Leave]]
  1. Updates entitlement record
  2. Recalculates remaining balance (entitlement + carry-forward - used - pending)
  3. If new entitlement < used: flags as over-utilized, does not retroactively reject approved leaves
  4. Creates audit log with old and new values
- **Validation:** New entitlement cannot be negative. If reducing below used amount, warning shown but allowed
- **DB:** `leave_entitlements`, `audit_logs`

## Variations

### When employee joins mid-year
- Auto-generation calculates pro-rata based on join date if policy uses pro-rata accrual
- Carry-forward is 0 (no previous year)
- HR can override with manual assignment if needed

### When employee changes legal entity mid-year
- Existing entitlements remain (from previous legal entity's policy)
- New entitlements may need manual creation for the new entity's policy
- System shows warning on entitlements page: "Employee changed legal entity on [date]"

### When recalculating entitlements
- Click "Recalculate" → recalculates based on current policy rules
- Only affects unprocessed entitlements; used/pending balances preserved
- API: `POST /api/v1/leave/entitlements/recalculate`

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| No policy assigned to legal entity | Employees skipped | "N employees skipped: no leave policy assigned to their legal entity" |
| Entitlements already exist for period | `409 Conflict` | "Entitlements already exist for [Year]. Use Recalculate to update" |
| Employee in probation | Entitlement set to 0 or reduced | Shown in results: "Probation restriction applied — entitlement reduced" |
| Inactive employee | Skipped | "N inactive employees skipped" |
| Manual adjustment below used days | Warning | "New entitlement (N days) is less than already used (M days). Employee will show negative balance" |

## Events Triggered

- `LeaveEntitlementCreatedEvent` → [[backend/messaging/event-catalog|Event Catalog]] — consumed by employee self-service to show updated balances
- `LeaveEntitlementUpdatedEvent` → [[backend/messaging/event-catalog|Event Catalog]] — triggers balance recalculation
- `AuditLogEntry` (action: `leave_entitlement.generated`) → [[modules/auth/audit-logging/overview|Audit Logging]]

## Related Flows

- [[Userflow/Leave/leave-policy-setup|Leave Policy Setup]] — policies that drive entitlement calculations
- [[Userflow/Leave/leave-type-configuration|Leave Type Configuration]] — leave types entitlements are created for
- [[Userflow/Leave/leave-request-submission|Leave Request Submission]] — employees use entitlements when requesting leave
- [[Userflow/Leave/leave-balance-view|Leave Balance View]] — view entitlement balances

## Module References

- [[modules/leave/overview|Leave]] — leave module overview and architecture
- [[modules/leave/leave-entitlements/overview|Leave Entitlements]] — entitlement data model and calculation logic
- [[modules/leave/leave-policies/overview|Leave Policies]] — policy rules driving entitlement amounts
