# Employee Skill Declaration

**Area:** Skills & Learning  
**Phase:** Phase 1
**Trigger:** Employee requests an existing tenant skill to be added to their profile
**Required Permission(s):** `skills:write` (own profile)  
**Related Permissions:** `skills:read` (to search existing tenant skills), `skills:validate` (manager validation)

---

## Preconditions

- Employee has an active employment record.
- Tenant has existing `skills` records, usually created from `Org Structure -> Job Families -> Required Skills`.
- Employee can request only existing active tenant skills. Phase 1 does not let employees create new skills or manage the taxonomy.
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Navigate to Skills Section
- **UI:** My Profile -> Skills tab. Shows existing profile skills and pending requests. `Add Skill Request` opens a search modal. There is no `Skills -> Taxonomy` sidebar in Phase 1.
- **API:** `GET /api/v1/employees/me/skills`
- **Backend:** `EmployeeSkillService.GetByEmployeeAsync()` â†’ [[skills]]
- **Validation:** Permission check for `skills:write` scoped to own profile
- **DB:** `employee_skills`, `skills`, `skill_categories`

### Step 2: Search Existing Skill
- **UI:** Search existing tenant skills. Job-family required skills are shown first, then other active tenant skills. If the skill is not found, the employee cannot create it in Phase 1; they see `Ask HR to add this skill to your job family`.
- **API:** `GET /api/v1/skills?search={query}&source=employee-request`
- **Backend:** `SkillSearchService.SearchExistingSkillsAsync()` â†’ [[skills]]
- **Validation:** Search query min 2 characters. Employee cannot add a skill they already have declared
- **DB:** `skills`, `skill_categories`

### Step 3: Self-Rate Proficiency
- **UI:** Selected skill shown with: Proficiency level selector (visual slider or radio buttons): Beginner â†’ Intermediate â†’ Advanced â†’ Expert. Each level shows description tooltip on hover. "Years of Experience" numeric input (0-50). Optional "Notes" text area (e.g., "Used Python for 3 years in data pipeline development")
- **API:** N/A (client-side form entry)
- **Backend:** N/A
- **Validation:** Proficiency level required. Years of experience must be non-negative
- **DB:** None

### Step 4: Submit Skill Request
- **UI:** Click "Save". Skill request appears in profile with status badge "Pending". Toast: "Skill request submitted. Your manager will be notified for validation"
- **API:** `POST /api/v1/employees/me/skills`
  ```json
  {
    "skillId": "uuid",
    "proficiencyLevel": 2,
    "notes": "Used Python for 3 years in data pipeline development"
  }
  ```
- **Backend:** `EmployeeSkillService.DeclareSkillAsync()` â†’ [[skills]]
  1. Validate skill exists and is active in the tenant
  2. Validate employee hasn't already declared this skill
  3. Create `employee_skills` record with `proficiency_level = 2`, `status = 'pending'`
  4. Notify direct manager via [[backend/notification-system|Notification System]]
  5. Publish `SkillDeclaredEvent`
  6. Create audit log entry
- **Validation:** Skill must already exist in the tenant skill library. No duplicate declarations. `proficiencyLevel` must be integer 1â€“5
- **DB:** `employee_skills`, `audit_logs`

### Step 5: Skill Visible on Profile
- **UI:** Skill now appears on employee's public profile (visible to managers and HR). In team views, manager can see aggregated skill data. Skill contributes to team skill matrix and gap analysis
- **API:** N/A (data available through existing profile endpoints)
- **Backend:** Skill indexed for search and reporting
- **Validation:** N/A
- **DB:** `employee_skills`

## Variations

### When updating an existing skill declaration
- Click existing skill card â†’ "Edit" â†’ modify proficiency or years of experience
- API: `PUT /api/v1/employees/me/skills/{skillId}`
- Status resets to `pending_validation` if proficiency changed
- Manager re-notified for validation

### When removing a declared skill
- Click existing skill card â†’ "Remove" â†’ confirmation dialog
- API: `DELETE /api/v1/employees/me/skills/{skillId}`
- Soft-deleted, removed from profile view
- Historical record retained for analytics

### When manager directly adds a skill to an employee's profile
- Manager navigates to employee profile â†’ Skills tab â†’ "Add Skill" (only visible to users with `skills:write` and a team-scoped access policy)
- Same modal as employee self-declaration but scoped to the employee
- **API:** `POST /api/v1/employees/{employeeId}/skills`
  ```json
  {
    "skillId": "uuid",
    "proficiencyLevel": 3
  }
  ```
- Creates `employee_skills` record with `status = 'validated'` and `validated_by_id = managerId` immediately â€” no pending step
- Employee receives in-app notification: "Your manager [Name] has added [Skill] to your profile at [Level]"
- **DB:** `employee_skills`, `audit_logs`

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Duplicate skill declaration | `409 Conflict` | "You have already declared this skill. Edit your existing declaration instead" |
| Inactive skill selected | `400 Bad Request` | "This skill is no longer available" |
| Invalid proficiency level | `400 Bad Request` | "Please select a valid proficiency level" |
| Missing required fields | `400 Bad Request` | "Proficiency level is required" |

## Events Triggered

- `SkillDeclaredEvent` â†’ [[backend/messaging/event-catalog|Event Catalog]] â€” consumed by notification service, skill analytics
- `SkillUpdatedEvent` â†’ [[backend/messaging/event-catalog|Event Catalog]] â€” when proficiency changed
- `AuditLogEntry` (action: `employee_skill.declared`) â†’ [[modules/auth/audit-logging/overview|Audit Logging]]

## Related Flows

- [[Userflow/Org-Structure/position-setup|Position Setup]] - creates/selects skills for position required skills
- [[Userflow/Skills-Learning/skill-assessment|Skill Assessment]] â€” manager validates this declaration
- [[Userflow/Skills-Learning/development-plan|Development Plan]] â€” skill gaps drive development planning
- [[Userflow/Skills-Learning/course-enrollment|Course Enrollment]] â€” courses linked to skills

## Module References

- [[skills]] â€” skills module overview and architecture
- [[modules/skills/employee-skills/overview|Employee Skills]] â€” employee skill data model and lifecycle
- [[modules/skills/skill-taxonomy/overview|Skill Taxonomy]] - Phase 2 full taxonomy management; Phase 1 only searches existing tenant skills
- [[backend/notification-system|Notification System]] â€” manager notification on declaration

