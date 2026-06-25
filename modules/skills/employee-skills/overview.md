# Employee Skills

**Module:** Skills & Learning  
**Feature:** Employee Skills
**Phase:** Phase 1

---

## Purpose

Employee-skill mapping with current proficiency levels and validation status. Phase 1 supports employee requests for existing tenant skills, eligible-validator direct-add, and validation of pending requests by management coverage owner or configured reviewer permission.


## Database Tables

### `employee_skills`
Fields: `employee_id`, `skill_id`, `proficiency_level` (integer 1-5, check `BETWEEN 1 AND 5`), `status` (`pending`, `validated`, `expired`), `validated_by_id` (nullable - set when an eligible validator validates or directly adds).

`last_assessed_in_review_id` remains `null` until Performance review integration is enabled.

### `skill_validation_requests`
Employee-initiated skill requests and level upgrade requests: `from_level`, `to_level`, `evidence_url`, `validator_id`, `status` (`pending`, `approved`, `rejected`), `review_note`.

When approved: `employee_skills.proficiency_level` is updated to `to_level` and status set to `validated`.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/employees/{employeeId}/skills` | `skills:read` | Skills profile |
| POST | `/api/v1/employees/me/skills` | `skills:write` | Employee requests an existing tenant skill |
| POST | `/api/v1/employees/{employeeId}/skills` | `skills:write` | Eligible validator directly adds skill to employee (status -> `validated`) |
| PUT | `/api/v1/employees/{employeeId}/skills/{skillId}/validate` | `skills:validate` | Eligible validator validates a pending employee declaration |
| PUT | `/api/v1/skills/validation-requests/{id}` | `skills:validate` | Approve or reject employee upgrade request |

## Related

- [[skills|Skills Module]] - parent module
- [[modules/skills/skill-taxonomy/overview|Skill Taxonomy]] - skill definitions and proficiency level descriptors
- [[modules/skills/skill-assessments/overview|Skill Assessments]] - assessments used to validate proficiency
- [[modules/skills/certifications/overview|Certifications]] - certifications as evidence for skill validation
- [[modules/skills/development-plans/overview|Development Plans]] - plans targeting skill growth
- [[modules/skills/courses-learning/overview|Courses Learning]] - courses that build specific skills
- [[infrastructure/multi-tenancy|Multi Tenancy]] - tenant-scoped employee skill profiles
- [[backend/messaging/event-catalog|Event Catalog]] - SkillValidated, SkillExpired events
- [[backend/messaging/error-handling|Error Handling]] - validation request state machine errors
- [[current-focus/DEV3-skills-core|DEV3: Skills Core]] - Phase 1 Required Skills and employee skill validation implementation task


