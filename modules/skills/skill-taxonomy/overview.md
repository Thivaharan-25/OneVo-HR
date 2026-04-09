# Skill Taxonomy

**Module:** Skills & Learning  
**Feature:** Skill Taxonomy

---

## Purpose

Defines skill categories and individual skills with proficiency level definitions.

## Database Tables

### `skill_categories`
Groupings: `name`, `is_active`.

### `skills`
Individual skills: `category_id`, `name`, `proficiency_levels` (jsonb with level 1-5 definitions), `evidence_required`.

### `job_skill_requirements`
Required skills per job family: `job_family_id`, `skill_id`, `min_proficiency`, `is_mandatory`.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/skills` | `skills:read` | List all skills |

## Related

- [[skills|Skills Module]] — parent module
- [[modules/skills/employee-skills/overview|Employee Skills]] — skills from taxonomy assigned to employees
- [[modules/skills/skill-assessments/overview|Skill Assessments]] — assessments built around taxonomy skills
- [[modules/skills/courses-learning/overview|Courses Learning]] — courses tagged to taxonomy skills
- [[modules/skills/development-plans/overview|Development Plans]] — plan milestones targeting taxonomy skills
- [[infrastructure/multi-tenancy|Multi Tenancy]] — tenant-scoped skill categories and definitions
- [[backend/messaging/event-catalog|Event Catalog]] — SkillCreated, SkillDeactivated events
- [[backend/messaging/error-handling|Error Handling]] — duplicate skill name and category integrity errors
- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4: Supporting Bridges]] — implementation task
