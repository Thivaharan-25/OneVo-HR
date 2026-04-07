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

- [[org-structure|Org Structure Module]]
- [[departments]]
- [[legal-entities]]
- [[cost-centers]]
- [[teams]]
- [[multi-tenancy]]
- [[authorization]]
- [[shared-kernel]]
- [[WEEK1-org-structure]]
