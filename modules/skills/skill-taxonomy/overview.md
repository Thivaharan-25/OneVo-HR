# Skill Taxonomy

**Module:** Skills & Learning  
**Feature:** Skill Taxonomy

---

## Purpose

Defines skill categories and individual skills with proficiency level definitions.

## Phase Rule

The full customer-facing `Skills -> Taxonomy` management area is Phase 2. In Phase 1, skills are only searched or created inline from `Org Structure -> Job Families -> Required Skills` so a job family can define required skills.

Phase 1 inline creation creates a simple tenant-scoped skill and category if needed. It does not expose full taxonomy cleanup, bulk management, proficiency-label editing, or a standalone Skills sidebar.

## Database Tables

### `skill_categories`
Groupings: `name`, `is_active`.

### `skills`
Individual skills: `category_id`, `name`, `proficiency_levels` (jsonb with level 1-5 definitions), `evidence_required`.

### `position_skill_requirements`
Required skills per position: `position_id`, `skill_id`, `min_proficiency`, `is_mandatory`.

## API Endpoints

### Phase 1 Embedded Use

Owned by Org Structure job hierarchy flow:

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/org/job-families/{familyId}/skill-requirements` | `skills:read` | List required skills for a job family |
| POST | `/api/v1/org/job-families/{familyId}/skill-requirements` | `skills:manage` | Select an existing skill or create a simple skill inline, then attach it to the job family |
| DELETE | `/api/v1/org/job-families/{familyId}/skill-requirements/{id}` | `skills:manage` | Remove a required skill from a job family |

### Phase 2 Full Taxonomy

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
