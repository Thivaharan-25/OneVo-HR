# Employee Promotion

**Area:** Employee Management  
**Required Permission(s):** `employees:write`  
**Related Permissions:** `payroll:write` (salary revision), `roles:manage` (override role)

---

## Preconditions

- Employee is active → [[profile-management]]
- Job family levels defined → [[job-family-setup]]
- Required permissions: [[permission-assignment|Permission Assignment Flow]]

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
- **Backend:** EmployeeLifecycleService.PromoteAsync() → [[employee-lifecycle]]
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

- `EmployeePromoted` → [[event-catalog]]
- `RoleChanged` → [[event-catalog]]
- `CompensationUpdated` → [[event-catalog]]
- Notification to employee → [[notification-system]]

## Related Flows

- [[job-family-setup]] — defines levels and default roles
- [[compensation-setup]] — salary details
- [[permission-assignment]] — permissions change with role
- [[employee-transfer]] — may accompany promotion

## Module References

- [[employee-lifecycle]]
- [[job-hierarchy]]
- [[compensation]]
- [[authorization]]
