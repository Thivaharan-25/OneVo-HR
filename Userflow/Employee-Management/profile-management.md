# Profile Management

**Area:** Employee Management  
**Trigger:** Employee or admin views/edits profile (user action - self-service or admin)
**Required Permission(s):** `employees:read-own` (own profile) or `employees:read` (any employee)  

---

## Preconditions

- Employee account exists and is active
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Navigate to Profile
- **UI (own):** Dashboard -> click avatar -> "My Profile"
- **UI (others):** Sidebar -> People -> Employees -> search/browse -> click employee name
- **API:** `GET /api/v1/employees/{id}` or `GET /api/v1/employees/me`

### Step 2: View Profile Sections
- **UI:** Single scrollable page with collapsible sections (no tabs):
  1. **Identity Card** (glass): Name, photo, title, dept, status badge, hire date, reports to, Managed by / coverage owner
  2. **Quick Facts Strip**: Tenure, time off balance, last review score, salary band, next milestone
  3. **Alerts / Action Items**: Expiring visa, pending review, probation ending (if any)
  5. **Pay & Benefits** (permission-gated, requires `payroll:read`): Salary, allowances, bank details (masked)
  6. **Documents** (collapsed by default, requires `documents:read`): Uploaded documents
  7. **Skills** (collapsed by default): requested/validated skills. Education and certifications are Phase 2 qualifications.
  8. **Dependents** (collapsed by default): Emergency contacts, family
  9. **Time Off** (collapsed by default, requires `time_off:read-own`): Balances and requests
  10. **Activity Timeline** (collapsed by default): Recent changes

### Step 3: Edit Fields (if `employees:write` or own editable fields)
- **UI:** Click edit icon -> modify fields -> save
- **API:** `PUT /api/v1/employees/{id}`
- **Backend:** EmployeeService.UpdateAsync() -> [[modules/core-hr/employee-profiles/overview|Employee Profiles]]
- **Validation:** Email unique, required fields present
- **DB:** `employees` - updated, audit trail created in `audit_logs`

## Variations

- Can only see employees allowed by management coverage - others hidden
- `Reports to` is org-chart/reporting context only. `Managed by / coverage owner` shows the effective management coverage owner used for employee visibility and Phase 1 routing.

### Own profile - limited editable fields
- Employee can update: phone, address, emergency contacts, photo

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| No permission for employee | 403 Forbidden | "You don't have access to this profile" |
| Invalid email format | Validation fails | "Please enter a valid email address" |

## Events Triggered

- `EmployeeUpdated` -> [[backend/messaging/event-catalog|Event Catalog]]

## Related Flows

- [[Userflow/Employee-Management/employee-onboarding|Employee Onboarding]]
- [[Userflow/Employee-Management/compensation-setup|Compensation Setup]]
- [[Userflow/Employee-Management/qualification-tracking|Qualification Tracking]]
- [[Userflow/Employee-Management/dependent-management|Dependent Management]]

## Module References

- [[modules/core-hr/employee-profiles/overview|Employee Profiles]]
- [[modules/auth/audit-logging/overview|Audit Logging]]

