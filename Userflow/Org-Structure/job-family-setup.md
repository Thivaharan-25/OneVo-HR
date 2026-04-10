# Job Family Setup

**Area:** Org Structure  
**Trigger:** Admin creates job family and levels (user action — configuration)
**Required Permission(s):** `org:manage`  
**Related Permissions:** `roles:manage` (to assign default role per level)

---

## Preconditions

- Roles created with permissions → [[Userflow/Auth-Access/role-creation|Role Creation]]
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

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
- **Backend:** JobFamilyService.CreateAsync() → [[modules/org-structure/job-hierarchy/overview|Job Hierarchy]]
- **Example:** Junior Engineer → "Employee" role (basic permissions), Engineering Lead → "Team Lead" role (includes `performance:read-team`, `attendance:read-team`)

### Step 5: Save
- **API:** `POST /api/v1/org/job-families`
- **DB:** `job_families`, `job_levels`, `job_titles` — records created with role associations
- **Result:** When employees are assigned to a job family level during onboarding, they automatically inherit the level's default role and its permissions

### Step 5: Assign Required Skills to Job Family
- **UI:** Inside the job family detail view, navigate to "Required Skills" tab. Empty state: "No skills assigned yet — add skills this job family requires". Click "Add Skill Requirement". Modal: search and select a skill from the skill taxonomy (requires skills to be set up first — see [[Userflow/Skills-Learning/skill-taxonomy-setup|Skill Taxonomy Setup]]). For each skill: set Minimum Proficiency (slider 1–5 with level label), toggle Mandatory / Optional. Save
- **API:** `POST /api/v1/job-families/{familyId}/skill-requirements`
  ```json
  {
    "skillId": "uuid",
    "minProficiency": 3,
    "isMandatory": true
  }
  ```
- **Backend:** `JobSkillRequirementService.AssignAsync()`
  1. Validate skill exists in tenant's taxonomy
  2. Validate job family belongs to tenant
  3. Prevent duplicate skill for same job family
  4. Create `job_skill_requirements` record
  5. Create audit log entry
- **Validation:** Skill must exist and be active. `min_proficiency` must be 1–5. Cannot add the same skill twice to the same family
- **DB:** `job_skill_requirements`
- **Result:** Skill gap analysis (`GET /api/v1/skills/gap-analysis/{employeeId}`) now compares employees in this job family against these requirements

> **Note:** Skill taxonomy must be configured before this step. If skills are not yet set up, this step can be completed later without re-running the rest of the flow.

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

- `JobFamilyCreated` → [[backend/messaging/event-catalog|Event Catalog]]
- `JobFamilyLevelUpdated` → [[backend/messaging/event-catalog|Event Catalog]]

## Related Flows

- [[Userflow/Auth-Access/role-creation|Role Creation]] — create roles before assigning to levels
- [[Userflow/Auth-Access/permission-assignment|Permission Assignment]] — permissions come from role assigned to level
- [[Userflow/Employee-Management/employee-onboarding|Employee Onboarding]] — job family level selected during onboarding
- [[Userflow/Employee-Management/employee-promotion|Employee Promotion]] — promotion changes job family level and potentially role
- [[Userflow/Skills-Learning/skill-taxonomy-setup|Skill Taxonomy Setup]] — skills must exist before they can be assigned to a job family

## Module References

- [[modules/org-structure/job-hierarchy/overview|Job Hierarchy]]
- [[frontend/cross-cutting/authorization|Authorization]]
- [[modules/org-structure/overview|Org Structure]]
