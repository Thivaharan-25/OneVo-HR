# Employee Promotion

**Area:** Employee Management  
**Trigger:** HR Admin initiates promotion (user action)
**Required Permission(s):** `employees:write`  
**Related Permissions:** `payroll:write` (salary revision), `roles:manage` (confirm role changes)

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
- **Backend:** System loads suggested role and membership changes for the new level, if configured

### Step 3: Salary Revision
- **UI:** Current salary shown → enter new salary → system shows salary band for new level → enter effective date
- **Validation:** Warning if salary outside new level's band

### Step 4: Role Review
- **UI:** System shows suggested role changes based on the new job family level for admin confirmation
- **Key:** Permissions do not change automatically because of the new job level. Role, team, workspace, or project membership changes take effect only after an authorized admin confirms them.
- Admin with `roles:manage` can confirm, reject, or replace the suggested role change.

### Step 5: Submit
- **API:** `POST /api/v1/employees/{id}/promote`
- **Backend:** EmployeeLifecycleService.PromoteAsync() → [[modules/core-hr/employee-lifecycle/overview|Employee Lifecycle]]
- **DB:** `employees` - title/level updated, `employee_compensation` - new salary record, confirmed role/member changes stored if approved

### Step 6: Effective Date Processing
- On effective date: confirmed changes become active; employee visibility changes only from confirmed permissions and memberships

## Variations

### When user also has `roles:manage`
- Can assign a confirmed role instead of the job family suggestion
- Can add additional confirmed permissions within entitlement boundaries

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Same level | Validation fails | "Select a different level for promotion" |
| Lower level | Warning | "This is a demotion — proceed?" |
| No salary change | Warning | "Consider adjusting salary for new level" |

## Events Triggered

- `EmployeePromoted` -> [[backend/messaging/event-catalog|Event Catalog]]
- `RoleChanged` -> emitted only when a role change was explicitly confirmed
- `CompensationUpdated` → [[backend/messaging/event-catalog|Event Catalog]]
- Notification to employee → [[backend/notification-system|Notification System]]

## Related Flows

- [[Userflow/Org-Structure/job-family-setup|Job Family Setup]] - defines levels and suggested roles
- [[Userflow/Employee-Management/compensation-setup|Compensation Setup]] — salary details
- [[Userflow/Auth-Access/permission-assignment|Permission Assignment]] - permissions change only from confirmed assignments
- [[Userflow/Employee-Management/employee-transfer|Employee Transfer]] — may accompany promotion

## Module References

- [[modules/core-hr/employee-lifecycle/overview|Employee Lifecycle]]
- [[modules/org-structure/job-hierarchy/overview|Job Hierarchy]]
- [[modules/core-hr/compensation/overview|Compensation]]
- [[frontend/cross-cutting/authorization|Authorization]]
