# Employee Skills

**Module:** Skills & Learning  
**Feature:** Employee Skills
**Phase:** Phase 1

---

## Purpose

Employee-skill mapping with current proficiency levels and validation status. Supports three write paths: employee self-declaration (creates `pending` record), manager direct-add (creates `validated` record), and manager validation of a pending declaration.

## Database Tables

### `employee_skills`
Fields: `employee_id`, `skill_id`, `proficiency_level` (integer 1–5, check `BETWEEN 1 AND 5`), `status` (`pending`, `validated`, `expired`), `validated_by_id` (nullable — set when manager validates or directly adds).

`last_assessed_in_review_id` is always `null` in Phase 1 — populated once Performance module is live.

### `skill_validation_requests`
Employee-initiated upgrade requests: `from_level`, `to_level`, `evidence_url`, `validator_id` (FK → employees), `status` (`pending`, `approved`, `rejected`), `review_note`.

When approved: `employee_skills.proficiency_level` is updated to `to_level` and status set to `validated`.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/employees/{employeeId}/skills` | `skills:read` | Skills profile |
| POST | `/api/v1/employees/me/skills` | `skills:write` | Employee self-declares a skill |
| POST | `/api/v1/employees/{employeeId}/skills` | `skills:write-team` | Manager directly adds skill to employee (status → `validated`) |
| PUT | `/api/v1/employees/{employeeId}/skills/{skillId}/validate` | `skills:validate` | Manager validates a pending employee declaration |
| GET | `/api/v1/skills/validation-requests` | `skills:validate` | List pending requests for manager's team |
| PUT | `/api/v1/skills/validation-requests/{id}` | `skills:validate` | Approve or reject employee upgrade request |
| GET | `/api/v1/skills/gap-analysis/{employeeId}` | `skills:manage` | Skill gap vs job family requirements |

## Related

- [[skills|Skills Module]] — parent module
- [[modules/skills/skill-taxonomy/overview|Skill Taxonomy]] — skill definitions and proficiency level descriptors
- [[modules/skills/skill-assessments/overview|Skill Assessments]] — assessments used to validate proficiency
- [[modules/skills/certifications/overview|Certifications]] — certifications as evidence for skill validation
- [[modules/skills/development-plans/overview|Development Plans]] — plans targeting skill growth
- [[modules/skills/courses-learning/overview|Courses Learning]] — courses that build specific skills
- [[infrastructure/multi-tenancy|Multi Tenancy]] — tenant-scoped employee skill profiles
- [[backend/messaging/event-catalog|Event Catalog]] — SkillValidated, SkillExpired events
- [[backend/messaging/error-handling|Error Handling]] — validation request state machine errors
- [[current-focus/DEV3-skills-core|DEV3: Skills Core]] — Phase 1 implementation task
