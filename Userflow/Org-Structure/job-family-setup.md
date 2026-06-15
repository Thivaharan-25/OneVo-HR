# Job Hierarchy Setup

**Area:** Org Structure  
**Trigger:** Admin creates job titles, job families, or job levels (user action — configuration)  
**Required Permission(s):** `org:manage`  
**Related Permissions:** `roles:manage` (to configure suggested roles per level)

---

## What Lives Here

This flow covers three related but independent concepts:

| Concept | Required for position setup? | Requires the others? |
|:--------|:-----------------------------|:---------------------|
| **Job Title** | Yes — every position needs one | No — family and level are optional |
| **Job Family** | No | No |
| **Job Level** | No | Requires a job family |

**The minimum path to create a position:** create a job title. Job families and levels are full first-class concepts that enable gap analysis, salary bands, and role prefill — but they are not a prerequisite for position setup or employee onboarding in Phase 1.

---

## Flow A: Create a Job Title (required for position setup)

### Step 1: Navigate to Job Titles
- **UI:** Sidebar → Organization → Job Titles → click "Add Job Title"
- **API:** `GET /api/v1/org/job-titles`

### Step 2: Enter Title Details

| Field | Required | Notes |
|:------|:---------|:------|
| Name | Yes | e.g., "Software Engineer", "HR Manager". Unique within tenant. |
| Job Family | No | Dropdown from existing families; leave blank if families not yet set up |
| Job Level | No | Filtered to levels inside the selected family; unavailable if no family selected |

- **Validation:** Name unique within tenant. Job level must belong to the selected family if both are set.

### Step 3: Save
- **API:** `POST /api/v1/org/job-titles`
- **DB:** `job_titles` — `job_family_id` and `job_level_id` are nullable; both remain null when omitted
- **Result:** Job title appears in the tenant catalog and is immediately selectable in position setup

### Inline Creation from Position Setup
Admins can create a job title without leaving the position form:
- In the Job Title field on the position form, type a name that doesn't match any existing title
- System shows "Create job title '{name}'" option
- Selecting it creates a minimal `job_titles` record (name only, no family or level) and links it to the position
- Family and level can be added to the title later from Sidebar → Organization → Job Titles

---

## Flow B: Create a Job Family with Levels (optional enrichment)

### Step 1: Navigate to Job Families
- **UI:** Sidebar → Organization → Job Families → click "Create Job Family"
- **API:** `GET /api/v1/org/job-families`

### Step 2: Define Job Family
- **UI:** Enter family name (e.g., "Engineering", "Human Resources", "Sales") → add description
- **Validation:** Name unique within tenant

### Step 3: Define Levels Within Family
- **UI:** Add levels in rank order. Each level has a name and a numeric rank (used for ordering — lower rank = more junior).

| Field | Required | Notes |
|:------|:---------|:------|
| Level Name | Yes | e.g., "Junior", "Mid", "Senior", "Lead", "Director" — seniority tier names, not job title names |
| Rank | Yes | Integer; unique within family; determines ordering |
| Description | No | |
| Min / Max Salary | No | Informational band; enforced only when payroll:write is active |

Level names describe seniority tiers, not specific roles. "Senior" is a level; "Software Engineer" is a job title that sits at that level — they are separate fields.

### Step 4: Configure Suggested Role Per Level
- **UI:** For each level, optionally select a suggested role from existing tenant roles. This prefills the role picker during onboarding and promotion for admin review — it never auto-grants permissions.
- **API:** Included in `POST /api/v1/org/job-families` payload; stored as `suggested_role_id` on the `job_levels` row
- **Example:** Junior level suggests "Employee" role; Lead level may suggest "Team Lead" role. Admin confirmation is always required before any role is assigned.

### Step 5: Save
- **API:** `POST /api/v1/org/job-families`
- **DB:** `job_families`, `job_levels` — no `job_titles` rows are created here
- **Result:** Family and levels are now available as optional fields in the job title form

### Step 6: Link Existing Job Titles to the Family
- **UI:** Organization → Job Titles → select a title → edit → choose family and level
- **API:** `PUT /api/v1/org/job-titles/{id}`
- Linking is optional and can be done any time after the family is created

### Step 7: Assign Required Skills to Job Family
- **UI:** Inside the job family detail view → Required Skills tab → Add Skill Requirement
- Type to search existing tenant skills. If no match, system shows "Create skill '{name}'" to create inline without a taxonomy sidebar.
- Set Minimum Proficiency (1–5) and Mandatory / Optional.
- **API:** `POST /api/v1/org/job-families/{familyId}/skill-requirements`

  When linking an existing skill:
  ```json
  { "skillId": "uuid", "minProficiency": 3, "isMandatory": true }
  ```
  When creating a skill inline:
  ```json
  { "skillId": null, "newSkill": { "name": "Rust", "categoryName": "Technical" }, "minProficiency": 3, "isMandatory": true }
  ```
- **Backend:** `JobSkillRequirementService.AssignAsync()`
  1. Validate job family belongs to tenant
  2. If `skillId` provided, validate skill exists and is active
  3. If `newSkill` provided, normalize name, prevent duplicates, create tenant-scoped `skills` record attached to the provided category or "Uncategorized"
  4. Validate `min_proficiency` is 1–5
  5. Prevent duplicate skill for the same family
  6. Create `job_skill_requirements` record
  7. Create audit log entry
- **Phase 1 rule:** There is no customer-facing Skills → Taxonomy sidebar in Phase 1. Skills are created inline here or imported. Full taxonomy management is Phase 2.
- **DB:** `skills`, `skill_categories`, `job_skill_requirements`
- **Result:** The skill becomes reusable for other job families even though the full Skill Taxonomy management screen is Phase 2.

---

## Variations

### When a Job Title Has No Family or Level
- Position setup proceeds normally when a title is selected; title, family, and level are optional in Phase 1 position setup
- Gap analysis is unavailable for employees in that title until a family is assigned
- Suggested role prefill during onboarding falls back to the role linked on the position itself

### When Editing a Level's Suggested Role
- Affects future admin suggestions only; does not bulk-update existing employee permissions

### When Adding a New Level to an Existing Family
- Existing employees at other levels are unaffected
- New level is immediately available in the job title form

### When Payroll is Active
- Salary bands on levels become enforceable — system warns if employee compensation is outside band during compensation setup

---

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Duplicate job title name in tenant | Validation fails | "A job title with this name already exists" |
| Duplicate job family name in tenant | Validation fails | "A job family with this name already exists" |
| Job level assigned to wrong family | Validation fails | "This level does not belong to the selected family" |
| Duplicate level rank within family | Validation fails | "Rank [N] is already used by another level in this family" |
| Salary band overlap between levels | Warning (not blocking) | "Salary bands overlap with [Level Name]" |
| Delete level with assigned employees | Blocked | "[N] employees assigned to this level — reassign first" |
| Duplicate skill on job family | Blocked | "This skill is already required for this job family" |

---

## Events Triggered

- `JobFamilyCreated` → [[backend/messaging/event-catalog|Event Catalog]]
- `JobFamilyLevelUpdated` → [[backend/messaging/event-catalog|Event Catalog]]

---

## Related Flows

- [[Userflow/Org-Structure/position-setup|Position Setup]] — positions may link to job titles, but title, family, and level are not required in Phase 1 position setup
- [[Userflow/Auth-Access/role-creation|Role Creation]] — create roles before using them as level suggestions
- [[Userflow/Auth-Access/permission-assignment|Permission Assignment]] — permissions come from confirmed role assignments, not job level alone
- [[Userflow/Employee-Management/employee-onboarding|Employee Onboarding]] — job family level selected during onboarding; suggested role prefills for admin review
- [[Userflow/Employee-Management/employee-promotion|Employee Promotion]] — promotion changes job family level and may prefill role suggestions
- [[Userflow/Skills-Learning/skill-taxonomy-setup|Skill Taxonomy Setup]] — Phase 2 full taxonomy management

---

## Module References

- [[modules/org-structure/job-hierarchy/overview|Job Hierarchy]]
- [[modules/org-structure/overview|Org Structure]]
- [[modules/org-structure/positions/overview|Positions]]
- [[frontend/cross-cutting/authorization|Authorization]]
