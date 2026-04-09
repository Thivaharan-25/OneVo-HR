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

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/job-families` | `employees:read` | List families |
| GET | `/api/v1/job-titles` | `employees:read` | List titles |

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
