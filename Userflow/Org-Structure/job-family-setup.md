# Job Family Setup

**Area:** Org Structure  
**Required Permission(s):** `org:manage`  
**Related Permissions:** `roles:manage` (to assign default role per level)

---

## Preconditions

- Roles created with permissions → [[role-creation]]
- Required permissions: [[permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Navigate to Job Families
- **UI:** Sidebar → Organization → Job Families → click "Create Job Family"
- **API:** `GET /api/v1/org/job-families`

### Step 2: Define Job Family
- **UI:** Enter family name (e.g., "Engineering", "Human Resources", "Sales") → add description
- **Validation:** Name unique within tenant

### Step 3: Define Levels Within Family
- **UI:** Add levels sequentially:
  - Level 1: Junior (e.g., "Junior Engineer")
  - Level 2: Mid (e.g., "Engineer")
  - Level 3: Senior (e.g., "Senior Engineer")
  - Level 4: Lead (e.g., "Engineering Lead")
  - Level 5: Director (e.g., "Engineering Director")
- For each level: set title, min/max salary band, description

### Step 4: Assign Default Role Per Level (CRITICAL for RBAC)
- **UI:** For each level → select a role from existing roles → this role's permissions become the default for employees at this level
- **Backend:** JobFamilyService.CreateAsync() → [[job-hierarchy]]
- **Example:** Junior Engineer → "Employee" role (basic permissions), Engineering Lead → "Team Lead" role (includes `performance:read-team`, `attendance:read-team`)

### Step 5: Save
- **API:** `POST /api/v1/org/job-families`
- **DB:** `job_families`, `job_family_levels` — records created with role associations
- **Result:** When employees are assigned to a job family level during onboarding, they automatically inherit the level's default role and its permissions

## Variations

### When editing levels
- Changing the default role on a level → existing employees at that level can be bulk-updated or kept on old role
- Adding a new level → existing employees unaffected

### When user also has `payroll:write`
- Salary bands become enforceable — system warns if employee salary is outside band during compensation setup

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Salary band overlap between levels | Warning (not blocking) | "Salary bands overlap with Level 2" |
| Delete level with employees | Blocked | "5 employees assigned to this level — reassign first" |
| No role assigned to level | Warning | "No default role set — employees will need manual role assignment" |

## Events Triggered

- `JobFamilyCreated` → [[event-catalog]]
- `JobFamilyLevelUpdated` → [[event-catalog]]

## Related Flows

- [[role-creation]] — create roles before assigning to levels
- [[permission-assignment]] — permissions come from role assigned to level
- [[employee-onboarding]] — job family level selected during onboarding
- [[employee-promotion]] — promotion changes job family level and potentially role

## Module References

- [[job-hierarchy]]
- [[authorization]]
- [[org-structure]]
