# Job Hierarchy

**Module:** Org Structure  
**Feature:** Job Hierarchy

---

## Purpose

Job families, levels, and titles forming the career framework. The three concepts are independent:

- **Job Title** — the named role label that can be used on a position (e.g., "Software Engineer"). Job title is optional in Phase 1 position setup. `job_family_id` and `job_level_id` on `job_titles` are nullable; a title can exist without being linked to a family or level.
- **Job Family** — a grouping of related roles (e.g., "Engineering"). Enables skill gap analysis and salary bands. Not required for position setup.
- **Job Level** — a seniority tier within a family (e.g., "Senior"), with a numeric `rank` for ordering and an optional suggested role for onboarding/promotion prefill. Requires a job family. Not required for position setup.

A job title may carry a family and level, but position setup does not require title, family, or level in Phase 1. These fields enrich positions with career structure and are not a prerequisite for creating positions or onboarding employees.

## Database Tables

### `job_families`
Groupings like "Engineering", "Sales".

### `job_levels`
Seniority levels with numeric `rank` for ordering (e.g., Junior, Senior, Lead, Director).

### `job_titles`
Named roles used by positions. `job_family_id` and `job_level_id` are nullable — a title can be created standalone and linked to a family/level later. Example: "Software Engineer" may sit in the Engineering family at the Senior level, but the title is valid without those links.

### `job_skill_requirements` *(from Skills Core â€” Phase 1)*
Required skills per job family with minimum proficiency. Fields: `job_family_id`, `skill_id`, `min_proficiency` (integer 1â€“5), `is_mandatory`. Used by gap analysis to compare employee skills against what their job family demands.

Phase 1 required-skill setup is embedded in this Job Hierarchy flow. Admins search existing tenant skills from the Required Skills tab; if no match exists, they can create a simple skill inline and attach it to the job family. The full `Skills -> Taxonomy` sidebar is Phase 2.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/org/job-titles` | `employees:read` | List job titles |
| POST | `/api/v1/org/job-titles` | `org:manage` | Create job title; `job_family_id` and `job_level_id` are optional |
| PUT | `/api/v1/org/job-titles/{id}` | `org:manage` | Update job title, or link/unlink family and level |
| GET | `/api/v1/org/job-families` | `employees:read` | List job families |
| POST | `/api/v1/org/job-families` | `org:manage` | Create job family with levels |
| PUT | `/api/v1/org/job-families/{id}` | `org:manage` | Update job family name or description |
| GET | `/api/v1/org/job-families/{familyId}/skill-requirements` | `skills:read` | Required skills for a job family |
| POST | `/api/v1/org/job-families/{familyId}/skill-requirements` | `skills:manage` | Attach an existing skill or create one inline, then link to the job family |
| DELETE | `/api/v1/org/job-families/{familyId}/skill-requirements/{id}` | `skills:manage` | Remove skill requirement |

## Related

- [[modules/org-structure/overview|Org Structure Module]]
- [[modules/org-structure/positions/overview|Positions]] — positions may link to job titles, but title, family, and level are not required in Phase 1 position setup
- [[Userflow/Org-Structure/job-family-setup|Job Hierarchy Setup]]
- [[modules/org-structure/departments/overview|Departments]]
- [[modules/org-structure/legal-entities/overview|Legal Entities]]
- [[modules/org-structure/cost-centers/overview|Cost Centers]]
- [[modules/org-structure/teams/overview|Teams]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[frontend/cross-cutting/authorization|Authorization]]
- [[backend/shared-kernel|Shared Kernel]]
- [[current-focus/DEV3-org-structure|DEV3: Org Structure]]



