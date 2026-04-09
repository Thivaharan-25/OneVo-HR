# Leave Balance View

**Area:** Leave Management  
**Required Permission(s):** `leave:read-own` (own balances) or `leave:read` (team/all balances)  
**Related Permissions:** `leave:create` (to initiate new request from balance view)

---

## Preconditions

- Employee has an active employment record
- Leave entitlements have been assigned: [[Userflow/Leave/leave-entitlement-assignment|Leave Entitlement Assignment Flow]]
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Navigate to Leave Balances
- **UI:** Employee: navigates to Leave → Balances (or Leave → My Leave → "Balances" tab). Manager/Admin: navigates to Leave → Team Balances (if `leave:read`) or Leave → All Balances (if `leave:manage`)
- **API:** `GET /api/v1/leave/entitlements/me?year={year}` (own) or `GET /api/v1/leave/entitlements?year={year}&departmentId={id}` (team/all)
- **Backend:** `LeaveEntitlementService.GetBalanceSummaryAsync()` → [[modules/leave/overview|Leave]]
- **Validation:** Checks `leave:read-own` or `leave:read` permission via RBAC middleware. Scope filtering: own = only self, team = direct reports, all = everyone (based on permission scope)
- **DB:** `leave_entitlements`, `leave_requests` (for pending calculations)

### Step 2: View Balance Summary
- **UI:** Dashboard cards for each leave type showing:
  - **Leave Type Name** (e.g., "Annual Leave")
  - **Entitled:** total annual entitlement + carry-forward days
  - **Used:** days already taken (approved and completed)
  - **Pending:** days in pending requests (not yet approved)
  - **Remaining:** entitled - used - pending
  - **Visual:** progress bar or donut chart (green = remaining, blue = used, yellow = pending)
- **API:** Response from Step 1 includes all balance fields
- **Backend:** N/A (data rendering)
- **Validation:** N/A
- **DB:** None (data already fetched)

### Step 3: Filter by Year
- **UI:** Year selector dropdown (current year selected by default). Switching years loads that year's entitlements and usage. Previous years show final balances (read-only)
- **API:** `GET /api/v1/leave/entitlements/me?year={selectedYear}`
- **Backend:** `LeaveEntitlementService.GetBalanceSummaryAsync()` → [[modules/leave/overview|Leave]]
- **Validation:** Year must be within tenant's active period (not before company registration)
- **DB:** `leave_entitlements` (filtered by `year`)

### Step 4: View Leave History
- **UI:** Below balance cards, a table showing all leave requests for the selected year with columns: Leave Type, Start Date, End Date, Total Days, Status (colour-coded: green = Approved, yellow = Pending, red = Rejected, grey = Cancelled), Approved By, Submitted On. Click on any row to view request details
- **API:** `GET /api/v1/leave/requests/me?year={year}`
- **Backend:** `LeaveRequestService.GetByEmployeeAsync()` → [[modules/leave/overview|Leave]]
- **Validation:** N/A (read-only)
- **DB:** `leave_requests` (filtered by `employee_id`, `year`)

### Step 5: View Team Balances (Manager/Admin)
- **UI:** If user has `leave:read` permission: Team Balances tab shows table with columns: Employee Name, Department, Leave Type (expandable), Entitled, Used, Pending, Remaining. Filter by department, leave type. Sort by any column. Search by employee name
- **API:** `GET /api/v1/leave/entitlements?year={year}&scope=team`
- **Backend:** `LeaveEntitlementService.GetTeamBalancesAsync()` → [[modules/leave/overview|Leave]]
- **Validation:** Scoped by reporting hierarchy — managers see only direct/indirect reports
- **DB:** `leave_entitlements`, `employees`, `org_hierarchy`

### Step 6: Export to CSV
- **UI:** "Export" button (top right) → options: "My Balances" (own) or "Team Balances" (if team permission). Downloads CSV file with all visible data
- **API:** `GET /api/v1/leave/entitlements/export?year={year}&format=csv&scope={own|team}`
- **Backend:** `LeaveReportService.ExportBalancesAsync()` → [[modules/leave/overview|Leave]]
- **Validation:** Export scoped to same data the user can view (permission-based)
- **DB:** `leave_entitlements`, `leave_requests`

## Variations

### When employee has negative balance
- Negative remaining balance shown in red
- Tooltip: "You have exceeded your entitlement by N days. Contact HR for resolution"
- Can occur when entitlement was reduced after leave was taken

### When carry-forward is expiring
- Banner warning: "You have N carry-forward days expiring on [Date]"
- Carry-forward days shown separately from annual entitlement

### When viewing balances with `leave:manage` (HR Admin)
- Can see all employees across all departments
- Additional filters: legal entity, employment status
- Can click "Adjust" to modify individual entitlements inline → [[Userflow/Leave/leave-entitlement-assignment|Leave Entitlement Assignment]]

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| No entitlements assigned | Empty state | "No leave entitlements found for [Year]. Contact HR if you believe this is an error" |
| Permission denied for team view | Tab not visible | Team Balances tab hidden if user lacks `leave:read` |
| Export fails | `500 Internal Server Error` | "Export failed. Please try again later" |
| Year out of range | Validation fails | "Balance data is not available for the selected year" |

## Events Triggered

- No events triggered (read-only flow)
- `AuditLogEntry` (action: `leave_balance.exported`) → [[modules/auth/audit-logging/overview|Audit Logging]] (only on CSV export)

## Related Flows

- [[Userflow/Leave/leave-request-submission|Leave Request Submission]] — initiate new request from balance view
- [[Userflow/Leave/leave-entitlement-assignment|Leave Entitlement Assignment]] — how entitlements are created
- [[Userflow/Leave/leave-cancellation|Leave Cancellation]] — cancelled requests restore balance

## Module References

- [[modules/leave/overview|Leave]] — leave module overview and architecture
- [[modules/leave/leave-entitlements/overview|Leave Entitlements]] — entitlement and balance data model
- [[modules/leave/leave-requests/overview|Leave Requests]] — request history data
