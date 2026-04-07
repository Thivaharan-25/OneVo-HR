# Profile Management

**Area:** Employee Management  
**Required Permission(s):** `employees:read-own` (own profile) or `employees:read` (any employee)  
**Related Permissions:** `employees:write` (edit), `employees:read-team` (team profiles)

---

## Preconditions

- Employee account exists and is active
- Required permissions: [[permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Navigate to Profile
- **UI (own):** Dashboard → click avatar → "My Profile"
- **UI (others):** Sidebar → Employees → search/browse → click employee name
- **API:** `GET /api/v1/employees/{id}` or `GET /api/v1/employees/me`

### Step 2: View Profile Sections
- **UI:** Tabbed layout:
  - **Personal:** Name, email, phone, DOB, address, photo
  - **Employment:** Department, team, job family, level, title, manager, start date, status
  - **Compensation:** Salary, allowances, bank details (masked) → requires `payroll:read`
  - **Documents:** Uploaded documents → requires `documents:read`
  - **Skills:** Declared and validated skills → [[employee-skill-declaration]]
  - **Qualifications:** Education, certifications → [[qualification-tracking]]
  - **Dependents:** Emergency contacts, family → [[dependent-management]]
  - **Leave:** Balances and requests → requires `leave:read-own`

### Step 3: Edit Fields (if `employees:write` or own editable fields)
- **UI:** Click edit icon → modify fields → save
- **API:** `PUT /api/v1/employees/{id}`
- **Backend:** EmployeeService.UpdateAsync() → [[employee-profiles]]
- **Validation:** Email unique, required fields present
- **DB:** `employees` — updated, audit trail created in `audit_logs`

## Variations

### When viewing with `employees:read-team`
- Can only see employees in own team/department — others hidden

### Own profile — limited editable fields
- Employee can update: phone, address, emergency contacts, photo
- Cannot edit: department, title, salary, job family level (admin only)

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| No permission for employee | 403 Forbidden | "You don't have access to this profile" |
| Invalid email format | Validation fails | "Please enter a valid email address" |

## Events Triggered

- `EmployeeUpdated` → [[event-catalog]]

## Related Flows

- [[employee-onboarding]]
- [[compensation-setup]]
- [[qualification-tracking]]
- [[dependent-management]]

## Module References

- [[employee-profiles]]
- [[audit-logging]]
