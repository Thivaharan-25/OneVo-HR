# Skill Assessment

**Area:** Skills & Learning  
**Phase:** Phase 1
**Trigger:** Assigned coverage owner validates employee skill request from Inbox
**Required Permission(s):** `skills:validate`  

---

## Preconditions

- Employee has submitted a pending skill request: [[Userflow/Skills-Learning/employee-skill-declaration|Employee Skill Declaration Flow]].
- Requested skill already exists in the tenant skill library.
- Assessor has `skills:validate` and is the assigned management coverage owner for the employee.
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Open Inbox Skill Request
- **API:** `GET /api/v1/skills/validation-requests`
- **Backend:** `SkillValidationRequestService.GetPendingForAssessorAsync()` -> [[skills]]
- **Validation:** Permission check for `skills:validate`; employee access is resolved through management coverage.
- **DB:** `employee_skills`, `employees`

### Step 2: Review Request
- **API:** `GET /api/v1/employees/{employeeId}/skills`
- **Backend:** `EmployeeSkillService.GetByEmployeeAsync()` -> [[skills]]
- **Validation:** Assessor must be the assigned coverage owner or otherwise have valid employee access for this action.
- **DB:** `employee_skills`, `skills`

### Step 3: Decide Proficiency
- **UI:** Manager selects `Validate`, `Adjust & Validate`, or `Reject`. For validate/adjust, choose proficiency 1-5. For reject, notes are required.
- **API:** N/A (client-side form entry)
- **Backend:** N/A
- **Validation:** Manager rating required. Notes optional but encouraged
- **DB:** None

### Step 4: Submit Validation
- **UI:** Three action buttons: "Validate" (accept - uses manager rating or agrees with self-rating), "Adjust & Validate" (accept with different proficiency), "Reject" (skill not demonstrated - requires reason). Click chosen action. Confirmation dialog for reject. Toast: "Skill assessment saved"
- **API:** `PUT /api/v1/employees/{employeeId}/skills/{skillId}/validate`
  ```json
  {
    "action": "validate",
    "proficiencyLevel": 3,
    "notes": "Demonstrated advanced Python skills in Q3 project"
  }
  ```
- **Backend:** `EmployeeSkillService.ValidateAsync()` -> [[skills]]
  1. Validate the assessor has `skills:validate` and valid management coverage for the employee
  2. Update `employee_skills`: set `proficiency_level` to assessor's rating, `validated_by_id` to assessor, `status = 'validated'`
  3. For reject: set `status = 'pending'`, time_off `validated_by_id` null
  4. Notify employee of result via [[backend/notification-system|Notification System]]
  5. Publish `SkillValidatedEvent` or `SkillRejectedEvent`
  6. Create audit log entry
- **Validation:** Assessor must have valid coverage for the employee. `proficiencyLevel` must be integer 1-5. Rejection requires notes
- **DB:** `employee_skills`, `audit_logs`

### Step 5: Employee Notified
- **UI:** Employee receives in-app notification: "Your [Skill Name] skill has been validated by [Manager Name] at [Proficiency Level]" or "Your [Skill Name] skill declaration was rejected: [reason]". Clicking notification navigates to skill on profile. Validated skills show green checkmark badge. Rejected skills show option to re-declare with updated proficiency
- **API:** N/A (notification-driven)
- **Backend:** Notification dispatched via [[backend/notification-system|Notification System]]
- **Validation:** N/A
- **DB:** `notifications`

## Variations

### When bulk-assessing multiple skills
- Manager selects multiple pending skills via checkboxes -> "Bulk Validate"
- All selected skills validated at their self-rated proficiency
- Individual notes not available in bulk mode
- API: `POST /api/v1/employees/{employeeId}/skills/bulk-assess`

### When reassessing a previously validated skill
- Manager can reassess a validated skill (e.g., after performance review)
- Opens same assessment panel with previous proficiency shown
- Updates `employee_skills.proficiency_level` and `validated_by_id` in place (no separate history table in Phase 1 baseline; full history is in `audit_logs`)

### When multiple owners can cover the employee
- The request is assigned to one eligible owner using management coverage ordering.
- Backup owners are used only when the primary owner is unavailable or invalid.
- Assessment history shows the assigned assessor.

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Employee outside assigned coverage | `403 Forbidden` | "You do not have access to assess this employee's skills" |
| Skill already assessed by another manager | Warning shown | "This skill was assessed by [Name] on [Date]. Your assessment will override it" |
| Rejection without notes | `400 Bad Request` | "Please provide a reason for rejection" |
| Invalid proficiency level | `400 Bad Request` | "Please select a valid proficiency level" |

## Events Triggered

- `SkillAssessedEvent` -> [[backend/messaging/event-catalog|Event Catalog]] - consumed by notification service, analytics, development plan suggestions
- `SkillRejectedEvent` -> [[backend/messaging/event-catalog|Event Catalog]] - consumed by notification service
- `AuditLogEntry` (action: `skill.assessed`) -> [[modules/auth/audit-logging/overview|Audit Logging]]

## Related Flows

- [[Userflow/Skills-Learning/employee-skill-declaration|Employee Skill Declaration]] - declaration that triggers this assessment
- [[Userflow/Skills-Learning/development-plan|Development Plan]] - assessment results inform skill gap analysis
- [[Userflow/Skills-Learning/certification-tracking|Certification Tracking]] - certifications provide evidence for assessment

## Module References

- [[skills]] - skills module overview and architecture
- [[modules/skills/skill-assessments/overview|Skill Assessments]] - Phase 2 quiz-based assessments; this flow is Phase 1 eligible-validator validation
- [[modules/skills/employee-skills/overview|Employee Skills]] - employee skill lifecycle
- [[backend/notification-system|Notification System]] - employee notification on assessment result


