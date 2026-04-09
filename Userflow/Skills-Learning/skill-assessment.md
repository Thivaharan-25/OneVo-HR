# Skill Assessment

**Area:** Skills & Learning  
**Required Permission(s):** `skills:validate`  
**Related Permissions:** `skills:read` (to view skills), `employees:read-team` (to view team members)

---

## Preconditions

- Employee has declared at least one skill with status `pending_validation`: [[Userflow/Skills-Learning/employee-skill-declaration|Employee Skill Declaration Flow]]
- Assessor (manager) has the employee in their reporting line
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Navigate to Team Skills
- **UI:** Team → Skills. Table view showing all direct reports with: Employee Name, Total Skills Declared, Pending Validation (count with badge), Last Assessment Date. Filter by: validation status (Pending, Validated, All). Sort by pending count descending to prioritize. Notification badge shows total pending validations across team
- **API:** `GET /api/v1/teams/me/skills?status=pending_validation`
- **Backend:** `TeamSkillService.GetTeamSkillSummaryAsync()` → [[skills]]
- **Validation:** Permission check for `skills:validate`. Scoped to manager's direct reports only
- **DB:** `employee_skills`, `employees`, `reporting_lines`

### Step 2: Select Employee
- **UI:** Click employee row to expand or navigate to employee skill detail view. Shows all declared skills for that employee in a list: Skill Name, Category, Self-Rated Proficiency (visual bar), Years of Experience, Employee Notes, Status (Pending / Validated / Rejected). Pending skills highlighted with amber indicator
- **API:** `GET /api/v1/employees/{employeeId}/skills`
- **Backend:** `EmployeeSkillService.GetByEmployeeAsync()` → [[skills]]
- **Validation:** Manager must have reporting line to employee
- **DB:** `employee_skills`, `skills`, `proficiency_levels`

### Step 3: Review and Assess Skill
- **UI:** Click pending skill to open assessment panel. Shows: Employee's self-rating (read-only), Manager's proficiency rating (slider/radio — same levels as self-rating), Assessment Notes (text area, e.g., "Demonstrated advanced Python skills in Q3 project. Agree with self-assessment"), Assessment Date (auto-set to today). Side panel shows context: employee's related certifications, completed courses for this skill, project history if available
- **API:** N/A (client-side form entry)
- **Backend:** N/A
- **Validation:** Manager rating required. Notes optional but encouraged
- **DB:** None

### Step 4: Submit Validation
- **UI:** Three action buttons: "Validate" (accept — uses manager rating or agrees with self-rating), "Adjust & Validate" (accept with different proficiency), "Reject" (skill not demonstrated — requires reason). Click chosen action. Confirmation dialog for reject. Toast: "Skill assessment saved"
- **API:** `PUT /api/v1/employees/{employeeId}/skills/{skillId}/assess`
  ```json
  {
    "action": "validate",
    "managerProficiencyLevelId": "uuid",
    "assessmentNotes": "Demonstrated advanced Python skills in Q3 project",
    "assessmentDate": "2026-04-07"
  }
  ```
- **Backend:** `SkillAssessmentService.AssessAsync()` → [[skills]]
  1. Validate manager has reporting line to employee
  2. Update `employee_skills` record: set `validated_proficiency`, `assessment_notes`, `assessed_by`, `assessed_at`
  3. Update status to `validated` or `rejected`
  4. If validated: effective proficiency = manager rating (overrides self-rating for reporting)
  5. Notify employee of assessment result via [[backend/notification-system|Notification System]]
  6. Publish `SkillAssessedEvent`
  7. Create audit log entry
- **Validation:** Assessor must be in employee's reporting chain. Proficiency level must be valid. Rejection requires notes
- **DB:** `employee_skills`, `skill_assessments`, `notifications`, `audit_logs`

### Step 5: Employee Notified
- **UI:** Employee receives in-app notification: "Your [Skill Name] skill has been validated by [Manager Name] at [Proficiency Level]" or "Your [Skill Name] skill declaration was rejected: [reason]". Clicking notification navigates to skill on profile. Validated skills show green checkmark badge. Rejected skills show option to re-declare with updated proficiency
- **API:** N/A (notification-driven)
- **Backend:** Notification dispatched via [[backend/notification-system|Notification System]]
- **Validation:** N/A
- **DB:** `notifications`

## Variations

### When bulk-assessing multiple skills
- Manager selects multiple pending skills via checkboxes → "Bulk Validate"
- All selected skills validated at their self-rated proficiency
- Individual notes not available in bulk mode
- API: `POST /api/v1/employees/{employeeId}/skills/bulk-assess`

### When reassessing a previously validated skill
- Manager can reassess a validated skill (e.g., after performance review)
- Opens same assessment panel with previous assessment shown
- New assessment creates a new `skill_assessments` record (history preserved)
- Previous proficiency shown for comparison

### When employee is in a dotted-line reporting relationship
- Both direct and dotted-line managers with `skills:validate` can assess
- Most recent assessment takes precedence
- Assessment history shows all assessors

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Employee not in reporting line | `403 Forbidden` | "You can only assess skills for your direct reports" |
| Skill already assessed by another manager | Warning shown | "This skill was assessed by [Name] on [Date]. Your assessment will override it" |
| Rejection without notes | `400 Bad Request` | "Please provide a reason for rejection" |
| Invalid proficiency level | `400 Bad Request` | "Please select a valid proficiency level" |

## Events Triggered

- `SkillAssessedEvent` → [[backend/messaging/event-catalog|Event Catalog]] — consumed by notification service, analytics, development plan suggestions
- `SkillRejectedEvent` → [[backend/messaging/event-catalog|Event Catalog]] — consumed by notification service
- `AuditLogEntry` (action: `skill.assessed`) → [[modules/auth/audit-logging/overview|Audit Logging]]

## Related Flows

- [[Userflow/Skills-Learning/employee-skill-declaration|Employee Skill Declaration]] — declaration that triggers this assessment
- [[Userflow/Skills-Learning/development-plan|Development Plan]] — assessment results inform skill gap analysis
- [[Userflow/Skills-Learning/certification-tracking|Certification Tracking]] — certifications provide evidence for assessment

## Module References

- [[skills]] — skills module overview and architecture
- [[modules/skills/skill-assessments/overview|Skill Assessments]] — assessment data model and history
- [[modules/skills/employee-skills/overview|Employee Skills]] — employee skill lifecycle
- [[backend/notification-system|Notification System]] — employee notification on assessment result
