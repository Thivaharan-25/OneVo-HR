# Employee Promotion

**Area:** Employee Management  
**Required Permission(s):** `employees:write`  
**Related Permissions:** `payroll:write` (salary revision), `roles:manage` (override role)

---

## Preconditions

- Employee is active → [[Userflow/Employee-Management/profile-management|Profile Management]]
- Job family levels defined → [[Userflow/Org-Structure/job-family-setup|Job Family Setup]]
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Initiate Promotion
- **UI:** Employee Profile → Actions → "Promote" → form opens

### Step 2: Set New Level
- **UI:** Select new job family level (e.g., Mid → Senior) → new title auto-filled from level → override title if needed
- **Backend:** System loads the default role for the new level

### Step 3: Salary Revision
- **UI:** Current salary shown → enter new salary → system shows salary band for new level → enter effective date
- **Validation:** Warning if salary outside new level's band

### Step 4: Role Change (Automatic)
- **UI:** System shows: "Role will change from [Employee] to [Senior Employee] based on new job family level"
- **Key:** Permissions change automatically when role changes — user may gain or lose features
- Admin with `roles:manage` can override to a different role

### Step 5: Submit
- **API:** `POST /api/v1/employees/{id}/promote`
- **Backend:** EmployeeLifecycleService.PromoteAsync() → [[modules/core-hr/employee-lifecycle/overview|Employee Lifecycle]]
- **DB:** `employees` — title/level updated, `employee_compensation` — new salary record, `user_roles` — role updated

### Step 6: Effective Date Processing
- On effective date: new role active → permission changes take effect → employee may see new menu items / features

## Variations

### When user also has `roles:manage`
- Can assign a completely different role instead of the job family default
- Can add additional permissions on top of the default role

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Same level | Validation fails | "Select a different level for promotion" |
| Lower level | Warning | "This is a demotion — proceed?" |
| No salary change | Warning | "Consider adjusting salary for new level" |

## Events Triggered

- `EmployeePromoted` → [[backend/messaging/event-catalog|Event Catalog]]
- `RoleChanged` → [[backend/messaging/event-catalog|Event Catalog]]
- `CompensationUpdated` → [[backend/messaging/event-catalog|Event Catalog]]
- Notification to employee → [[backend/notification-system|Notification System]]

## Related Flows

- [[Userflow/Org-Structure/job-family-setup|Job Family Setup]] — defines levels and default roles
- [[Userflow/Employee-Management/compensation-setup|Compensation Setup]] — salary details
- [[Userflow/Auth-Access/permission-assignment|Permission Assignment]] — permissions change with role
- [[Userflow/Employee-Management/employee-transfer|Employee Transfer]] — may accompany promotion

## Module References

- [[modules/core-hr/employee-lifecycle/overview|Employee Lifecycle]]
- [[modules/org-structure/job-hierarchy/overview|Job Hierarchy]]
- [[modules/core-hr/compensation/overview|Compensation]]
- [[frontend/cross-cutting/authorization|Authorization]]
