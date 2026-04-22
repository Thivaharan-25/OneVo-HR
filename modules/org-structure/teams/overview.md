# Teams

**Module:** Org Structure  
**Feature:** Teams

---

## Purpose

Teams live within departments. A user with `org:manage` can create teams, but the departments they can assign and the employees they can add depend on their position in the department hierarchy (creator tier). See [[modules/auth/authorization/end-to-end-logic|Authorization — Hierarchy Scoping]] for bypass resolution.

## Database Tables

### `teams`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `name` | `varchar(100)` | Unique within department |
| `department_id` | `uuid` | FK → departments |
| `team_lead_id` | `uuid` | FK → employees (nullable) |
| `description` | `text` | nullable |
| `is_active` | `boolean` | |
| `created_at` | `timestamptz` | |

### `team_members`
Join table: `team_id`, `employee_id`, `joined_at`. PK: `(team_id, employee_id)`.

## Creator Tier Resolution

On `POST /api/v1/org/teams`, the service resolves the creator's tier before validating the request:

```
TeamService.ResolveCreatorTierAsync(creatorEmployeeId)
  -> Query: departments WHERE head_employee_id = @creatorId
  -> For each headed department:
       - parentDepartmentId IS NULL → ROOT tier → break
       - Has child departments → PARENT tier
       - No children → LEAF tier
  -> If no departments headed → NON-HEAD tier (same restrictions as LEAF)
  -> If multiple headed → use highest tier
```

**Accessible departments by tier:**

| Tier | Accessible departments |
|:-----|:----------------------|
| Root | All active departments in tenant |
| Parent | Their department + all descendants (recursive CTE on `parent_department_id`) |
| Leaf / Non-head | Only their own `department_id` |

**Member pool by tier:**

| Tier | `subordinateIds` filter | `bypassIds` |
|:-----|:------------------------|:------------|
| Root / Parent | No extra filter | Always included |
| Leaf / Non-head | AND `department_id = creator.department_id` | Always included regardless of dept filter |

`IHierarchyScope.GetSubordinateIdsAsync(featureContext: "teams")` provides both sets.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/org/teams` | `org:manage` | List teams (scoped to creator's accessible departments) |
| POST | `/api/v1/org/teams` | `org:manage` | Create team — validates dept and members against creator tier + bypass grants |
| PUT | `/api/v1/org/teams/{id}` | `org:manage` | Update team |
| DELETE | `/api/v1/org/teams/{id}` | `org:manage` | Deactivate team |
| GET | `/api/v1/org/teams/{id}/members` | `org:manage` | List team members |
| POST | `/api/v1/org/teams/{id}/members` | `org:manage` | Add member — validated against member pool |

## Related

- [[modules/org-structure/overview|Org Structure Module]]
- [[modules/org-structure/departments/overview|Departments]]
- [[modules/auth/authorization/end-to-end-logic|Authorization]] — IHierarchyScope, bypass resolution
- [[modules/org-structure/legal-entities/overview|Legal Entities]]
- [[modules/org-structure/cost-centers/overview|Cost Centers]]
- [[modules/org-structure/job-hierarchy/overview|Job Hierarchy]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[backend/shared-kernel|Shared Kernel]]
- [[current-focus/DEV3-org-structure|DEV3: Org Structure]]
