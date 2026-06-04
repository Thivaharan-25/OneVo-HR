# Employee Skills

**Module:** Skills & Learning  
**Feature:** Employee Skills
**Phase:** Phase 1

---

## Purpose

Employee-skill mapping with current proficiency levels and validation status. Phase 1 supports employee requests for existing tenant skills, manager direct-add, and manager validation of pending requests.

Phase 1 does not expose full taxonomy management. Employees can request only existing active tenant skills, usually skills created from `Org Structure -> Job Families -> Required Skills`.

## Database Tables

### `employee_skills`
Fields: `employee_id`, `skill_id`, `proficiency_level` (integer 1â€“5, check `BETWEEN 1 AND 5`), `status` (`pending`, `validated`, `expired`), `validated_by_id` (nullable â€” set when manager validates or directly adds).

`last_assessed_in_review_id` remains `null` until Performance review integration is enabled.

### `skill_validation_requests`
Employee-initiated skill requests and level upgrade requests: `from_level`, `to_level`, `evidence_url`, `validator_id`, `status` (`pending`, `approved`, `rejected`), `review_note`.

When approved: `employee_skills.proficiency_level` is updated to `to_level` and status set to `validated`.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/employees/{employeeId}/skills` | `skills:read` | Skills profile |
| POST | `/api/v1/employees/me/skills` | `skills:write` | Employee requests an existing tenant skill |
| POST | `/api/v1/employees/{employeeId}/skills` | `skills:write` | Manager directly adds skill to employee (status â†’ `validated`) |
| PUT | `/api/v1/employees/{employeeId}/skills/{skillId}/validate` | `skills:validate` | Manager validates a pending employee declaration |
| GET | `/api/v1/skills/validation-requests` | `skills:validate` | List pending requests for manager's team |
| PUT | `/api/v1/skills/validation-requests/{id}` | `skills:validate` | Approve or reject employee upgrade request |
| GET | `/api/v1/skills/gap-analysis/{employeeId}` | `skills:manage` | Skill gap vs job family requirements |

## Related

- [[skills|Skills Module]] â€” parent module
- [[modules/skills/skill-taxonomy/overview|Skill Taxonomy]] â€” skill definitions and proficiency level descriptors
- [[modules/skills/skill-assessments/overview|Skill Assessments]] â€” assessments used to validate proficiency
- [[modules/skills/certifications/overview|Certifications]] â€” certifications as evidence for skill validation
- [[modules/skills/development-plans/overview|Development Plans]] â€” plans targeting skill growth
- [[modules/skills/courses-learning/overview|Courses Learning]] â€” courses that build specific skills
- [[infrastructure/multi-tenancy|Multi Tenancy]] â€” tenant-scoped employee skill profiles
- [[backend/messaging/event-catalog|Event Catalog]] â€” SkillValidated, SkillExpired events
- [[backend/messaging/error-handling|Error Handling]] â€” validation request state machine errors
- [[current-focus/DEV3-skills-core|DEV3: Skills Core]] - Phase 1 Required Skills and employee skill validation implementation task


