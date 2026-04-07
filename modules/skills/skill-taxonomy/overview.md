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
- [[employee-skills]] — skills from taxonomy assigned to employees
- [[skill-assessments]] — assessments built around taxonomy skills
- [[courses-learning]] — courses tagged to taxonomy skills
- [[development-plans]] — plan milestones targeting taxonomy skills
- [[multi-tenancy]] — tenant-scoped skill categories and definitions
- [[event-catalog]] — SkillCreated, SkillDeactivated events
- [[error-handling]] — duplicate skill name and category integrity errors
- [[WEEK4-supporting-bridges]] — implementation task
