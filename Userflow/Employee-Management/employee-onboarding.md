# Employee Onboarding

**Area:** Employee Management  
**Required Permission(s):** `employees:write`  
**Related Permissions:** `roles:manage` (override default role), `org:manage` (change department), `payroll:write` (set compensation)

---

## Preconditions

- Department exists → [[department-hierarchy]]
- Job family with levels configured → [[job-family-setup]]
- Onboarding workflow template configured → [[workflow-engine]]
- Required permissions: [[permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Initiate New Hire
- **UI:** Sidebar → Employees → click "Add Employee"
- **API:** `GET /api/v1/org/departments` + `GET /api/v1/org/job-families` (populate dropdowns)

### Step 2: Enter Personal Details
- **UI:** Form: first name, last name, email, phone, date of birth, gender, nationality, address
- **Validation:** Email unique across tenant, DOB is valid date in past

### Step 3: Set Employment Details
- **UI:** Select department → select team → select job family → select level within family → enter job title → set employment type (full-time, part-time, contract) → set start date → select reporting manager
- **Backend:** Job family level auto-assigns default role → [[job-hierarchy]]
- **Key:** The role assigned here determines what features/permissions the employee will have

### Step 4: Set Compensation (if `payroll:write`)
- **UI:** Enter base salary → select currency → add allowances → enter bank details (encrypted at rest)
- **DB:** `employee_compensation`, `employee_bank_details`

### Step 5: Submit
- **API:** `POST /api/v1/employees`
- **Backend:** EmployeeService.CreateAsync() → [[employee-profiles]]
- **DB:** `employees` — status: "Onboarding", `user_roles` — default role assigned
- **Triggers:**
  1. User account created with temporary password
  2. Invitation email sent
  3. Onboarding workflow instance created
  4. Onboarding checklist generated (IT setup, badge, training, docs to sign)

### Step 6: Employee Receives Invitation
- **UI:** Employee gets email → clicks link → sets password → completes profile (photo, emergency contacts)
- **API:** `POST /api/v1/auth/activate`

### Step 7: Complete Onboarding Checklist
- **UI:** Employee/admin sees checklist → tick off items as completed → all items done → status: "Active"
- **Backend:** WorkflowService.CompleteStepAsync() → [[workflow-engine]]
- **DB:** `employees.status` → "Active"

## Variations

### When user also has `roles:manage`
- Can override the default role from job family → assign different role or additional permissions

### When monitoring is enabled for tenant
- GDPR consent dialog appears on employee's first login → [[gdpr-consent]]
- Agent deployment instructions generated → [[agent-deployment]]

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Duplicate email | Validation fails | "An employee with this email already exists" |
| No job family level selected | Warning | "No default role — assign role manually" |
| Start date in past | Validation fails | "Start date cannot be in the past" |
| Salary outside band | Warning | "Salary is outside the band for this level (50k-70k)" |

## Events Triggered

- `EmployeeCreated` → [[event-catalog]]
- `EmployeeOnboardingStarted` → [[event-catalog]]
- `UserAccountCreated` → [[event-catalog]]
- Notification: invitation email → [[notification-system]]
- Notification: onboarding tasks to admin → [[notification-system]]

## Related Flows

- [[job-family-setup]] — determines default role/permissions
- [[permission-assignment]] — override or add permissions
- [[compensation-setup]] — detailed salary config
- [[employee-offboarding]] — reverse flow
- [[profile-management]] — employee completes profile

## Module References

- [[employee-profiles]]
- [[employee-lifecycle]]
- [[onboarding]]
- [[job-hierarchy]]
- [[authorization]]
- [[workflow-engine]]
- [[notification-system]]
