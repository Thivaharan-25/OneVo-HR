# Employee Skill Declaration

**Area:** Skills & Learning  
**Phase:** Phase 1
**Trigger:** Employee adds own skills to profile (user action — self-service)
**Required Permission(s):** `skills:write` (own profile)  
**Related Permissions:** `skills:read` (to browse taxonomy), `skills:validate` (manager validation)

---

## Preconditions

- Employee has an active employment record
- Skill taxonomy has been configured with at least one category and skill: [[Userflow/Skills-Learning/skill-taxonomy-setup|Skill Taxonomy Setup Flow]]
- Proficiency levels have been defined
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Navigate to Skills Section
- **UI:** My Profile → Skills tab. Shows current declared skills in a card grid: each card displays skill name, category badge, self-rated proficiency (progress bar), years of experience, validation status (Pending / Validated / Rejected). "Add Skill" button prominent. Empty state message if no skills declared: "Declare your skills to help your team understand your capabilities"
- **API:** `GET /api/v1/employees/me/skills`
- **Backend:** `EmployeeSkillService.GetByEmployeeAsync()` → [[skills]]
- **Validation:** Permission check for `skills:write` scoped to own profile
- **DB:** `employee_skills`, `skills`, `skill_categories`

### Step 2: Add Skill
- **UI:** Modal opens with search-first interface. Search box with typeahead: type to search across all skills (e.g., typing "Py" shows "Python", "PyTorch"). Below search: browse by category accordion (Programming Languages, Project Management, etc.). Click a skill to select it. If skill not found: "Request New Skill" link (sends request to admin)
- **API:** `GET /api/v1/skills/taxonomy?search={query}`
- **Backend:** `SkillTaxonomyService.SearchSkillsAsync()` → [[skills]]
- **Validation:** Search query min 2 characters. Employee cannot add a skill they already have declared
- **DB:** `skills`, `skill_categories`

### Step 3: Self-Rate Proficiency
- **UI:** Selected skill shown with: Proficiency level selector (visual slider or radio buttons): Beginner → Intermediate → Advanced → Expert. Each level shows description tooltip on hover. "Years of Experience" numeric input (0-50). Optional "Notes" text area (e.g., "Used Python for 3 years in data pipeline development")
- **API:** N/A (client-side form entry)
- **Backend:** N/A
- **Validation:** Proficiency level required. Years of experience must be non-negative
- **DB:** None

### Step 4: Save Declaration
- **UI:** Click "Save". Skill card appears in profile with status badge "Pending". Toast: "Skill added successfully. Your manager will be notified for validation"
- **API:** `POST /api/v1/employees/me/skills`
  ```json
  {
    "skillId": "uuid",
    "proficiencyLevel": 2,
    "notes": "Used Python for 3 years in data pipeline development"
  }
  ```
- **Backend:** `EmployeeSkillService.DeclareSkillAsync()` → [[skills]]
  1. Validate skill exists and is active in taxonomy
  2. Validate employee hasn't already declared this skill
  3. Create `employee_skills` record with `proficiency_level = 2`, `status = 'pending'`
  4. Notify direct manager via [[backend/notification-system|Notification System]]
  5. Publish `SkillDeclaredEvent`
  6. Create audit log entry
- **Validation:** Skill must exist in taxonomy. No duplicate declarations. `proficiencyLevel` must be integer 1–5
- **DB:** `employee_skills`, `audit_logs`

### Step 5: Skill Visible on Profile
- **UI:** Skill now appears on employee's public profile (visible to managers and HR). In team views, manager can see aggregated skill data. Skill contributes to team skill matrix and gap analysis
- **API:** N/A (data available through existing profile endpoints)
- **Backend:** Skill indexed for search and reporting
- **Validation:** N/A
- **DB:** `employee_skills`

## Variations

### When updating an existing skill declaration
- Click existing skill card → "Edit" → modify proficiency or years of experience
- API: `PUT /api/v1/employees/me/skills/{skillId}`
- Status resets to `pending_validation` if proficiency changed
- Manager re-notified for validation

### When removing a declared skill
- Click existing skill card → "Remove" → confirmation dialog
- API: `DELETE /api/v1/employees/me/skills/{skillId}`
- Soft-deleted, removed from profile view
- Historical record retained for analytics

### When manager directly adds a skill to an employee's profile
- Manager navigates to employee profile → Skills tab → "Add Skill" (only visible to users with `skills:write-team`)
- Same modal as employee self-declaration but scoped to the employee
- **API:** `POST /api/v1/employees/{employeeId}/skills`
  ```json
  {
    "skillId": "uuid",
    "proficiencyLevel": 3
  }
  ```
- Creates `employee_skills` record with `status = 'validated'` and `validated_by_id = managerId` immediately — no pending step
- Employee receives in-app notification: "Your manager [Name] has added [Skill] to your profile at [Level]"
- **DB:** `employee_skills`, `audit_logs`

### When skill is linked to a completed course *(Phase 2)*
- If employee completes a course that maps to a skill, system auto-suggests declaring that skill
- Pre-fills proficiency based on course level

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Duplicate skill declaration | `409 Conflict` | "You have already declared this skill. Edit your existing declaration instead" |
| Inactive skill selected | `400 Bad Request` | "This skill is no longer available in the taxonomy" |
| Invalid proficiency level | `400 Bad Request` | "Please select a valid proficiency level" |
| Missing required fields | `400 Bad Request` | "Proficiency level is required" |

## Events Triggered

- `SkillDeclaredEvent` → [[backend/messaging/event-catalog|Event Catalog]] — consumed by notification service, skill analytics
- `SkillUpdatedEvent` → [[backend/messaging/event-catalog|Event Catalog]] — when proficiency changed
- `AuditLogEntry` (action: `employee_skill.declared`) → [[modules/auth/audit-logging/overview|Audit Logging]]

## Related Flows

- [[Userflow/Skills-Learning/skill-taxonomy-setup|Skill Taxonomy Setup]] — taxonomy that defines available skills
- [[Userflow/Skills-Learning/skill-assessment|Skill Assessment]] — manager validates this declaration
- [[Userflow/Skills-Learning/development-plan|Development Plan]] — skill gaps drive development planning
- [[Userflow/Skills-Learning/course-enrollment|Course Enrollment]] — courses linked to skills

## Module References

- [[skills]] — skills module overview and architecture
- [[modules/skills/employee-skills/overview|Employee Skills]] — employee skill data model and lifecycle
- [[modules/skills/skill-taxonomy/overview|Skill Taxonomy]] — taxonomy browsing and search
- [[backend/notification-system|Notification System]] — manager notification on declaration
