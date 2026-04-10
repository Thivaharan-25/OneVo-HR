# Employee Onboarding

**Area:** Employee Management  
**Trigger:** HR Admin clicks Add Employee (user action)
**Required Permission(s):** `employees:write`  
**Related Permissions:** `roles:manage` (override default role), `org:manage` (change department), `payroll:write` (set compensation)

---

## Preconditions

- Department exists → [[Userflow/Org-Structure/department-hierarchy|Department Hierarchy]]
- Job family with levels configured → [[Userflow/Org-Structure/job-family-setup|Job Family Setup]]
- Onboarding workflow template configured → [[modules/shared-platform/workflow-engine/overview|Workflow Engine]]
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Initiate New Hire
- **UI:** Sidebar → Employees → click "Add Employee"
- **API:** `GET /api/v1/org/departments` + `GET /api/v1/org/job-families` (populate dropdowns)

### Step 2: Enter Personal Details
- **UI:** Form: first name, last name, email, phone, date of birth, gender, nationality, address
- **Validation:** Email unique across tenant, DOB is valid date in past

### Step 3: Set Employment Details
- **UI:** Select department → select team → select job family → select level within family → enter job title → set employment type (full-time, part-time, contract) → set start date → select reporting manager
- **Backend:** Job family level auto-assigns default role → [[modules/org-structure/job-hierarchy/overview|Job Hierarchy]]
- **Key:** The role assigned here determines what features/permissions the employee will have

### Step 4: Set Compensation (if `payroll:write`)
- **UI:** Enter base salary → select currency → add allowances → enter bank details (encrypted at rest)
- **DB:** `employee_compensation`, `employee_bank_details`

### Step 5: Submit
- **API:** `POST /api/v1/employees`
- **Backend:** EmployeeService.CreateAsync() → [[modules/core-hr/employee-profiles/overview|Employee Profiles]]
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
- **Backend:** WorkflowService.CompleteStepAsync() → [[modules/shared-platform/workflow-engine/overview|Workflow Engine]]
- **DB:** `employees.status` → "Active"

## Variations

### When user also has `roles:manage`
- Can override the default role from job family → assign different role or additional permissions

### When monitoring is enabled for tenant
- GDPR consent dialog appears on employee's first login → [[Userflow/Auth-Access/gdpr-consent|Gdpr Consent]]
- Agent deployment instructions generated → [[Userflow/Workforce-Intelligence/agent-deployment|Agent Deployment]]

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Duplicate email | Validation fails | "An employee with this email already exists" |
| No job family level selected | Warning | "No default role — assign role manually" |
| Start date in past | Validation fails | "Start date cannot be in the past" |
| Salary outside band | Warning | "Salary is outside the band for this level (50k-70k)" |

## Events Triggered

- `EmployeeCreated` → [[backend/messaging/event-catalog|Event Catalog]]
- `EmployeeOnboardingStarted` → [[backend/messaging/event-catalog|Event Catalog]]
- `UserAccountCreated` → [[backend/messaging/event-catalog|Event Catalog]]
- Notification: invitation email → [[backend/notification-system|Notification System]]
- Notification: onboarding tasks to admin → [[backend/notification-system|Notification System]]

## Related Flows

- [[Userflow/Org-Structure/job-family-setup|Job Family Setup]] — determines default role/permissions
- [[Userflow/Auth-Access/permission-assignment|Permission Assignment]] — override or add permissions
- [[Userflow/Employee-Management/compensation-setup|Compensation Setup]] — detailed salary config
- [[Userflow/Employee-Management/employee-offboarding|Employee Offboarding]] — reverse flow
- [[Userflow/Employee-Management/profile-management|Profile Management]] — employee completes profile

## Module References

- [[modules/core-hr/employee-profiles/overview|Employee Profiles]]
- [[modules/core-hr/employee-lifecycle/overview|Employee Lifecycle]]
- [[modules/core-hr/onboarding/overview|Onboarding]]
- [[modules/org-structure/job-hierarchy/overview|Job Hierarchy]]
- [[frontend/cross-cutting/authorization|Authorization]]
- [[modules/shared-platform/workflow-engine/overview|Workflow Engine]]
- [[backend/notification-system|Notification System]]
