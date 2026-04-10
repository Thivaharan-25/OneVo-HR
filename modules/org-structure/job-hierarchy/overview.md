# Job Hierarchy

**Module:** Org Structure  
**Feature:** Job Hierarchy

---

## Purpose

Job families, levels, and titles forming the career framework.

## Database Tables

### `job_families`
Groupings like "Engineering", "Sales".

### `job_levels`
Seniority levels with numeric `rank` for ordering (e.g., Junior, Senior, Lead, Director).

### `job_titles`
Specific titles linked to a family and level (e.g., "Software Engineer" in Engineering family, Senior level).

### `job_skill_requirements` *(from Skills Core — Phase 1)*
Required skills per job family with minimum proficiency. Fields: `job_family_id`, `skill_id`, `min_proficiency` (integer 1–5), `is_mandatory`. Used by gap analysis to compare employee skills against what their job family demands.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/job-families` | `employees:read` | List families |
| POST | `/api/v1/job-families` | `org:manage` | Create job family |
| GET | `/api/v1/job-titles` | `employees:read` | List titles |
| GET | `/api/v1/job-families/{familyId}/skill-requirements` | `skills:read` | Required skills for a job family |
| POST | `/api/v1/job-families/{familyId}/skill-requirements` | `skills:manage` | Assign required skill to job family |
| DELETE | `/api/v1/job-families/{familyId}/skill-requirements/{id}` | `skills:manage` | Remove skill requirement |

## Related

- [[modules/org-structure/overview|Org Structure Module]]
- [[modules/org-structure/departments/overview|Departments]]
- [[modules/org-structure/legal-entities/overview|Legal Entities]]
- [[modules/org-structure/cost-centers/overview|Cost Centers]]
- [[modules/org-structure/teams/overview|Teams]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[frontend/cross-cutting/authorization|Authorization]]
- [[backend/shared-kernel|Shared Kernel]]
- [[current-focus/DEV3-org-structure|DEV3: Org Structure]]
