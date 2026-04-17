# Task: Skills Core (Phase 1)

**Assignee:** Dev 3
**Module:** Skills (Phase 1 subset — 5 tables)
**Priority:** High
**Dependencies:**
- [[current-focus/DEV1-infrastructure-setup|DEV1 Infrastructure Setup]] — shared kernel
- [[current-focus/DEV2-auth-security|DEV2 Auth Security]] — `skills:write`, `skills:validate`, `skills:manage` permissions
- [[current-focus/DEV1-core-hr-profile|DEV1 Core Hr Profile]] — `employees` table must exist for `employee_skills`
- [[current-focus/DEV3-org-structure|DEV3 Org Structure]] — `job_families` must exist for `job_skill_requirements`

> **Scope:** Only these 5 tables are Phase 1. Do NOT build courses, LMS, assessments, certifications, or development plans — those are Phase 2.

---

## Step 1: Backend

### Acceptance Criteria

#### Skill Taxonomy
- [ ] `skill_categories` CRUD (name, is_active, tenant-scoped)
- [ ] `skills` CRUD (linked to category, `proficiency_levels` jsonb stores label/description per level 1–5, `evidence_required` flag)
- [ ] Skill search endpoint with typeahead (min 2 chars, searches across all active skills)
- [ ] Deactivate skill (hides from new declarations; existing employee_skills retained)

#### Employee Skills
- [ ] `employee_skills` CRUD:
  - Employee self-declares: `POST /api/v1/employees/me/skills` → creates record with `status = 'pending'`
  - Manager direct-add: `POST /api/v1/employees/{employeeId}/skills` (requires `skills:write-team`) → creates with `status = 'validated'`, `validated_by_id = manager`
  - Manager validates pending: `PUT /api/v1/employees/{employeeId}/skills/{skillId}/validate` → updates `proficiency_level`, `validated_by_id`, `status = 'validated'`
  - Manager rejects: same endpoint with `action = 'reject'` → status stays `pending`, `validated_by_id` stays null
- [ ] `proficiency_level` is integer 1–5 (check constraint `BETWEEN 1 AND 5`). Not a UUID, not an enum string
- [ ] `last_assessed_in_review_id` always null in Phase 1 (nullable FK to review_cycles — Phase 2 only)
- [ ] Prevent duplicate skill declarations per employee (unique constraint on employee_id + skill_id)
- [ ] Skill gap analysis: `GET /api/v1/skills/gap-analysis/{employeeId}` — compares employee's validated skills vs `job_skill_requirements` for their job family

#### Skill Validation Requests
- [ ] `skill_validation_requests` CRUD — employee requests a proficiency upgrade (`from_level` → `to_level`)
- [ ] Manager approves → updates `employee_skills.proficiency_level` to `to_level`, `status = 'validated'`
- [ ] Manager rejects → `skill_validation_requests.status = 'rejected'`, no change to `employee_skills`

#### Permissions Required (seed via Auth module)
- `skills:read` — view skill taxonomy and employee skills
- `skills:write` — employee self-declares or edits own skills
- `skills:write-team` — manager directly adds skill to a report's profile
- `skills:validate` — manager validates/rejects employee skill declarations
- `skills:manage` — admin manages skill taxonomy (categories, skills, proficiency labels)

### Backend References

- [[database/schemas/skills|Skills Schema]] — `skill_categories`, `skills`, `employee_skills`, `job_skill_requirements`, `skill_validation_requests`
- [[modules/skills/overview|Skills Module Overview]] — Phase 1 tables, API contracts, business rules
- [[modules/skills/employee-skills/overview|Employee Skills]] — write path details (self-declare, manager-add, validate)
- [[modules/skills/skill-taxonomy/overview|Skill Taxonomy]] — taxonomy data model
- [[backend/module-catalog|Module Catalog]] — module ownership
- [[infrastructure/multi-tenancy|Multi Tenancy]] — all tables tenant-scoped

---

## Step 2: Frontend

### Pages to Build

```
app/(dashboard)/skills/
├── taxonomy/
│   └── page.tsx                  # Skill category + skill management (admin only)
│       └── components/
│           ├── SkillCategoryList.tsx     # Category accordion with skill count
│           ├── SkillForm.tsx             # Create/edit skill modal (name, category, proficiency labels)
│           └── ProficiencyLevelEditor.tsx # Edit 5 level labels per skill

app/(dashboard)/employees/[id]/
└── skills/
    └── page.tsx                  # Employee skills tab (manager view)
        └── components/
            ├── SkillProfileCard.tsx      # Skill + proficiency bar + validation badge
            ├── AddSkillModal.tsx         # Manager direct-add skill modal
            └── SkillGapPanel.tsx         # Gap vs job family requirements

app/(dashboard)/me/
└── skills/
    └── page.tsx                  # My Skills (self-service — employee view)
        └── components/
            ├── DeclareSkillModal.tsx     # Search taxonomy + set proficiency
            └── SkillCard.tsx             # Own skill card with status badge
```

### What to Build

- [ ] **Skill Taxonomy page** (admin, `skills:manage`):
  - Category list with nested skills (accordion)
  - Create/edit/deactivate category
  - Create/edit/deactivate skill within category
  - Proficiency level label editor per skill (5 fixed levels, customise name + description)

- [ ] **My Skills page** (employee, `skills:write`):
  - Grid of declared skills: name, category, self-rated proficiency bar, status badge (Pending / Validated)
  - "Add Skill" button → search taxonomy typeahead → set proficiency slider (1–5) → save
  - Edit/remove existing declarations

- [ ] **Employee Skills tab** on employee detail page (manager, `skills:validate` or `skills:write-team`):
  - List of employee's skills with validation status
  - "Add Skill" button → manager direct-add (creates as Validated immediately)
  - Pending skills highlighted → click to validate or reject (set manager proficiency rating)
  - Skill gap section: compare employee skills vs job family requirements

### Userflows

- [[Userflow/Skills-Learning/skill-taxonomy-setup|Skill Taxonomy Setup]] — admin configures categories + skills
- [[Userflow/Skills-Learning/employee-skill-declaration|Employee Skill Declaration]] — employee self-declares + manager direct-add variation
- [[Userflow/Skills-Learning/skill-assessment|Skill Assessment]] — manager validates pending declarations

### API Endpoints (Frontend Consumes)

| Method | Endpoint | Permission | Purpose |
|:-------|:---------|:-----------|:--------|
| GET | `/api/v1/skills/categories` | `skills:read` | List skill categories |
| POST | `/api/v1/skills/categories` | `skills:manage` | Create category |
| POST | `/api/v1/skills` | `skills:manage` | Create skill |
| GET | `/api/v1/skills?search={q}` | `skills:read` | Search skills (typeahead) |
| PUT | `/api/v1/skills/{id}/proficiency-levels` | `skills:manage` | Update level labels |
| GET | `/api/v1/employees/me/skills` | `skills:write` | Own skill profile |
| POST | `/api/v1/employees/me/skills` | `skills:write` | Self-declare skill |
| GET | `/api/v1/employees/{id}/skills` | `skills:read` | Employee skill profile |
| POST | `/api/v1/employees/{id}/skills` | `skills:write-team` | Manager direct-add |
| PUT | `/api/v1/employees/{id}/skills/{skillId}/validate` | `skills:validate` | Validate or reject |
| GET | `/api/v1/skills/gap-analysis/{id}` | `skills:manage` | Skill gap vs job family |
| GET | `/api/v1/teams/me/skills?status=pending` | `skills:validate` | Team pending validations |

### Frontend References

- [[frontend/design-system/components/component-catalog|Component Catalog]] — DataTable, Dialog, Badge, Slider
- [[frontend/data-layer/api-integration|API Integration]] — API client pattern
- [[frontend/cross-cutting/authorization|Authorization]] — PermissionGate for `skills:manage` vs `skills:write`

---

## Related Tasks

- [[current-focus/DEV3-org-structure|DEV3 Org Structure]] — job families must exist before job skill requirements; this task unblocks the "Required Skills" tab on the job families page
- [[current-focus/DEV1-core-hr-profile|DEV1 Core HR Profile]] — `employees` table must exist before `employee_skills` can be created
- [[current-focus/DEV2-auth-security|DEV2 Auth Security]] — skill permissions must be seeded
