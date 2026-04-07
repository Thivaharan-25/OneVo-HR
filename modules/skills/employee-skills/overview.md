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
- [[skill-taxonomy]] — skill definitions and proficiency level descriptors
- [[skill-assessments]] — assessments used to validate proficiency
- [[certifications]] — certifications as evidence for skill validation
- [[development-plans]] — plans targeting skill growth
- [[courses-learning]] — courses that build specific skills
- [[multi-tenancy]] — tenant-scoped employee skill profiles
- [[event-catalog]] — SkillValidated, SkillExpired events
- [[error-handling]] — validation request state machine errors
- [[WEEK4-supporting-bridges]] — implementation task
