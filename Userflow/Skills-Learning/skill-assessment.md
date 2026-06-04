# Skill Assessment

**Area:** Skills & Learning  
**Phase:** Phase 1
**Trigger:** Manager validates employee skill request from Inbox
**Required Permission(s):** `skills:validate`  
**Related Permissions:** `skills:read` (to view skills), `employees:read` with team access policy (to view team members)

---

## Preconditions

- Employee has submitted a pending skill request: [[Userflow/Skills-Learning/employee-skill-declaration|Employee Skill Declaration Flow]].
- Requested skill already exists in the tenant skill library.
- Assessor has `skills:validate` and is the employee's manager or has scoped HR access to that employee.
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Open Inbox Skill Request
- **UI:** Inbox shows `Skill validation request` items. The item displays employee name, requested skill, self-rated proficiency, whether the skill is required for the employee job family, and submitted date. `Team -> Skills` dashboards are Phase 2, not Phase 1.
- **API:** `GET /api/v1/skills/validation-requests`
- **Backend:** `SkillValidationRequestService.GetPendingForManagerAsync()` â†’ [[skills]]
- **Validation:** Permission check for `skills:validate`. Scoped to validator's direct reports from `employee_hierarchy_closure`, derived from position hierarchy
- **DB:** `employee_skills`, `employees`

### Step 2: Review Request
- **UI:** Open the Inbox item. Shows employee profile summary, requested skill, current job family required skills, self-rated proficiency, and employee notes. Certifications, courses, and project evidence panels are Phase 2.
- **API:** `GET /api/v1/employees/{employeeId}/skills`
- **Backend:** `EmployeeSkillService.GetByEmployeeAsync()` â†’ [[skills]]
- **Validation:** Manager must have reporting line to employee
- **DB:** `employee_skills`, `skills`

### Step 3: Decide Proficiency
- **UI:** Manager selects `Validate`, `Adjust & Validate`, or `Reject`. For validate/adjust, choose proficiency 1-5. For reject, notes are required.
- **API:** N/A (client-side form entry)
- **Backend:** N/A
- **Validation:** Manager rating required. Notes optional but encouraged
- **DB:** None

### Step 4: Submit Validation
- **UI:** Three action buttons: "Validate" (accept â€” uses manager rating or agrees with self-rating), "Adjust & Validate" (accept with different proficiency), "Reject" (skill not demonstrated â€” requires reason). Click chosen action. Confirmation dialog for reject. Toast: "Skill assessment saved"
- **API:** `PUT /api/v1/employees/{employeeId}/skills/{skillId}/validate`
  ```json
  {
    "action": "validate",
    "proficiencyLevel": 3,
    "notes": "Demonstrated advanced Python skills in Q3 project"
  }
  ```
- **Backend:** `EmployeeSkillService.ValidateAsync()` â†’ [[skills]]
  1. Validate manager is in employee's reporting chain
  2. Update `employee_skills`: set `proficiency_level` to manager's rating, `validated_by_id` to manager, `status = 'validated'`
  3. For reject: set `status = 'pending'`, leave `validated_by_id` null
  4. Notify employee of result via [[backend/notification-system|Notification System]]
  5. Publish `SkillValidatedEvent` or `SkillRejectedEvent`
  6. Create audit log entry
- **Validation:** Assessor must be manager of employee. `proficiencyLevel` must be integer 1â€“5. Rejection requires notes
- **DB:** `employee_skills`, `audit_logs`

### Step 5: Employee Notified
- **UI:** Employee receives in-app notification: "Your [Skill Name] skill has been validated by [Manager Name] at [Proficiency Level]" or "Your [Skill Name] skill declaration was rejected: [reason]". Clicking notification navigates to skill on profile. Validated skills show green checkmark badge. Rejected skills show option to re-declare with updated proficiency
- **API:** N/A (notification-driven)
- **Backend:** Notification dispatched via [[backend/notification-system|Notification System]]
- **Validation:** N/A
- **DB:** `notifications`

## Variations

### When bulk-assessing multiple skills
- Manager selects multiple pending skills via checkboxes â†’ "Bulk Validate"
- All selected skills validated at their self-rated proficiency
- Individual notes not available in bulk mode
- API: `POST /api/v1/employees/{employeeId}/skills/bulk-assess`

### When reassessing a previously validated skill
- Manager can reassess a validated skill (e.g., after performance review)
- Opens same assessment panel with previous proficiency shown
- Updates `employee_skills.proficiency_level` and `validated_by_id` in place (no separate history table in Phase 1 baseline; full history is in `audit_logs`)

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

- `SkillAssessedEvent` â†’ [[backend/messaging/event-catalog|Event Catalog]] â€” consumed by notification service, analytics, development plan suggestions
- `SkillRejectedEvent` â†’ [[backend/messaging/event-catalog|Event Catalog]] â€” consumed by notification service
- `AuditLogEntry` (action: `skill.assessed`) â†’ [[modules/auth/audit-logging/overview|Audit Logging]]

## Related Flows

- [[Userflow/Skills-Learning/employee-skill-declaration|Employee Skill Declaration]] â€” declaration that triggers this assessment
- [[Userflow/Skills-Learning/development-plan|Development Plan]] â€” assessment results inform skill gap analysis
- [[Userflow/Skills-Learning/certification-tracking|Certification Tracking]] â€” certifications provide evidence for assessment

## Module References

- [[skills]] â€” skills module overview and architecture
- [[modules/skills/skill-assessments/overview|Skill Assessments]] - Phase 2 quiz-based assessments; this flow is Phase 1 manager validation
- [[modules/skills/employee-skills/overview|Employee Skills]] â€” employee skill lifecycle
- [[backend/notification-system|Notification System]] â€” employee notification on assessment result


