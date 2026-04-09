# Task: Org Structure Module

**Assignee:** Dev 3
**Module:** OrgStructure
**Priority:** Critical
**Dependencies:** [[current-focus/DEV1-infrastructure-setup|DEV1 Infrastructure Setup]] (shared kernel, solution structure)

---

## Step 1: Backend

### Acceptance Criteria

- [ ] Legal entity CRUD (with country association)
- [ ] Office location CRUD (linked to legal entity + country)
- [ ] Department CRUD with hierarchical tree (unlimited nesting via parent_department_id)
- [ ] Department tree query (returns full hierarchy for a tenant)
- [ ] Job family CRUD (linked to department)
- [ ] Job family levels CRUD (rank ordering within family)
- [ ] Job title CRUD (linked to job family)
- [ ] Team CRUD (linked to department)
- [ ] Team member management (add/remove employees from teams)
- [ ] All entities tenant-scoped with proper indexes (see [[infrastructure/multi-tenancy|Multi Tenancy]])

### Backend References

- [[backend/module-catalog|Module Catalog]] — OrgStructure module details
- [[backend/module-boundaries|Module Boundaries]] — dependency rules
- [[backend/shared-kernel|Shared Kernel]] — BaseEntity, BaseRepository
- [[code-standards/backend-standards|Backend Standards]] — naming conventions
- [[AI_CONTEXT/known-issues|Known Issues]] — self-referencing tables (departments)
- [[infrastructure/multi-tenancy|Multi Tenancy]] — tenant-scoped entity patterns

---

## Step 2: Frontend

### Pages to Build

```
app/(dashboard)/org/
├── page.tsx                      # Org chart (visual hierarchy)
├── departments/page.tsx          # Department hierarchy tree view
├── teams/page.tsx                # Team management
├── job-families/page.tsx         # Job families, levels, titles
├── legal-entities/page.tsx       # Legal entity management
├── locations/page.tsx            # Office locations
├── components/                   # Colocated feature components
│   ├── DepartmentTree.tsx        # Interactive department hierarchy (expand/collapse, drag-and-drop)
│   ├── TeamMemberList.tsx        # Team member add/remove list
│   ├── JobFamilyAccordion.tsx    # Family → levels → titles accordion
│   └── OrgChart.tsx              # Visual org chart component
└── _types.ts                     # Local TypeScript definitions
```

### What to Build

- [ ] Department hierarchy page:
  - DepartmentTree component: interactive tree view (expand/collapse, drag-and-drop reorder)
  - Create department dialog (name, parent, head)
  - Edit inline or via modal
  - Show employee count per department
- [ ] Team management page:
  - DataTable: team name, department, lead, member count
  - TeamMemberList: team detail with add/remove
- [ ] Job families page:
  - Accordion: family -> levels -> titles
  - CRUD for each level
- [ ] Legal entities page:
  - DataTable: entity name, country, registration number
  - CRUD dialogs
- [ ] Office locations page:
  - DataTable: location name, legal entity, country, address
  - CRUD dialogs

### Userflows

- [[Userflow/Org-Structure/department-hierarchy|Department Hierarchy]] — create and manage department tree
- [[Userflow/Org-Structure/team-creation|Team Creation]] — create teams and manage members
- [[Userflow/Org-Structure/job-family-setup|Job Family Setup]] — configure job families, levels, titles
- [[Userflow/Org-Structure/legal-entity-setup|Legal Entity Setup]] — manage legal entities
- [[Userflow/Org-Structure/cost-center-setup|Cost Center Setup]] — cost center configuration

### API Endpoints (Frontend Consumes)

| Method | Endpoint | Purpose |
|:-------|:---------|:--------|
| GET | `/api/v1/org/departments/tree` | Full department hierarchy |
| POST | `/api/v1/org/departments` | Create department |
| PUT | `/api/v1/org/departments/{id}` | Update department |
| DELETE | `/api/v1/org/departments/{id}` | Delete department |
| GET | `/api/v1/org/teams` | List teams |
| POST | `/api/v1/org/teams` | Create team |
| PUT | `/api/v1/org/teams/{id}` | Update team |
| POST | `/api/v1/org/teams/{id}/members` | Add team member |
| DELETE | `/api/v1/org/teams/{id}/members/{employeeId}` | Remove member |
| GET | `/api/v1/org/job-families` | List job families |
| POST | `/api/v1/org/job-families` | Create job family |
| GET | `/api/v1/org/job-families/{id}/levels` | List levels |
| POST | `/api/v1/org/job-families/{id}/levels` | Create level |
| GET | `/api/v1/org/job-titles` | List job titles |
| POST | `/api/v1/org/job-titles` | Create job title |
| GET | `/api/v1/org/legal-entities` | List legal entities |
| POST | `/api/v1/org/legal-entities` | Create legal entity |
| GET | `/api/v1/org/locations` | List office locations |
| POST | `/api/v1/org/locations` | Create location |

### Frontend References

- [[frontend/design-system/components/component-catalog|Component Catalog]] — DataTable, Dialog, DropdownMenu
- [[frontend/design-system/patterns/layout-patterns|Layout Patterns]] — tree view layout
- [[frontend/data-layer/api-integration|API Integration]] — API client pattern

---

## Related Tasks

- [[current-focus/DEV1-infrastructure-setup|DEV1 Infrastructure Setup]] — shared kernel and solution structure this depends on
- [[current-focus/DEV1-core-hr-profile|DEV1 Core Hr Profile]] — employees reference departments, job titles, teams
- Performance — deferred to Phase 2 (team and company goals reference org hierarchy)
- [[current-focus/DEV1-leave|DEV1 Leave]] — job levels referenced in leave policy matching
