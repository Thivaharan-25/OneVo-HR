# Employee Skills

**Module:** Skills & Learning  
**Feature:** Employee Skills

---

## Purpose

Employee-skill mapping with current proficiency levels and validation status.

## Database Tables

### `employee_skills`
Fields: `employee_id`, `skill_id`, `proficiency_level` (1-5), `status` (`pending`, `validated`, `expired`), `validated_by_id`.

### `skill_validation_requests`
Level upgrade requests: `from_level`, `to_level`, `evidence_url`, `validator_id`, `status`, `review_note`.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/skills/employee/{employeeId}` | `skills:read` | Skills profile |
| POST | `/api/v1/skills/validate` | `skills:validate` | Validate/endorse |
| GET | `/api/v1/skills/gap-analysis/{employeeId}` | `skills:manage` | Skill gap report |

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
- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4: Supporting Bridges]] — implementation task
