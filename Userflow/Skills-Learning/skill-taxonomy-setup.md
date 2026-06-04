# Skill Taxonomy Setup

**Area:** Skills & Learning
**Phase:** Phase 2 for the full Skills sidebar experience
**Phase 1 exception:** Required skills can be created inline from Org Structure -> Job Families -> Required Skills.
**Trigger:** Admin manages the full skill catalog, categories, duplicate cleanup, imports, and proficiency labels.
**Required Permission(s):** `skills:manage`
**Related Permissions:** `skills:read` to view taxonomy without editing

---

## Phase 1 Behavior

The customer-facing `Skills -> Taxonomy` sidebar is not built in Phase 1.

Phase 1 only supports the skill records needed by Job Family required-skill setup:

```text
Org Structure
  Job Families
    Job Family Detail
      Required Skills tab
        Search skill
        Select existing skill if found
        Create simple skill inline if not found
        Set minimum proficiency 1-5
        Mark mandatory or optional
```

Inline-created skills are saved as tenant-scoped `skills` records so they can be reused by other job families later. The admin does not manage the full taxonomy tree in Phase 1.

See [[Userflow/Org-Structure/job-family-setup|Job Family Setup]].

---

## Phase 2 Full Flow

All steps below are Phase 2 only. They must not create Phase 1 sidebar navigation, pages, or direct `/api/v1/skills/*` integrations.

### Step 1: Navigate to Skill Taxonomy

- **UI:** Skills -> Taxonomy. Tree view displays existing skill categories with nested skills. Each category shows name, skill count, and last modified date. `Create Category` appears in the top-right. Expanding a category shows individual skills with proficiency level definitions.
- **API:** `GET /api/v1/skills/taxonomy`
- **Backend:** `SkillTaxonomyService.GetTaxonomyTreeAsync()` -> [[modules/skills/skill-taxonomy/overview|Skill Taxonomy]]
- **Validation:** Permission check for `skills:manage`
- **DB:** `skill_categories`, `skills`

### Step 2: Create Skill Category

- **UI:** Modal form opens: Category Name, Description, Icon/Color, Display Order.
- **API:** `POST /api/v1/skills/categories`
- **Backend:** `SkillCategoryService.CreateAsync()`
  1. Validate category name is unique within tenant
  2. Create `skill_categories` record
  3. Publish `SkillCategoryCreatedEvent`
  4. Create audit log entry
- **Validation:** Category name must be unique, max 100 characters. Display order must be positive integer.
- **DB:** `skill_categories`, `audit_logs`

### Step 3: Add Skills Within Category

- **UI:** Inside category detail view, click `Add Skill`. Fields: Skill Name, Description, Tags. Bulk add allows multiple skill names, one per line.
- **API:** `POST /api/v1/skills/categories/{categoryId}/skills`
- **Backend:** `SkillService.CreateAsync()`
  1. Validate skill name is unique within category and normalized duplicate rules
  2. Create `skills` record linked to category
  3. If bulk add: process each skill in a transaction
  4. Publish `SkillCreatedEvent` for each
- **Validation:** Skill name unique within category. Max 100 characters per name.
- **DB:** `skills`

### Step 4: Define Proficiency Level Labels Per Skill

- **UI:** Inside a skill detail view, click `Edit Proficiency Levels`. Shows 5 fixed level slots, 1-5. Admin customizes labels and descriptions.
- **API:** `PUT /api/v1/skills/{skillId}/proficiency-levels`
- **Backend:** `SkillService.UpdateProficiencyLabelsAsync()`
  1. Validate exactly 5 levels provided, values 1-5
  2. Update `skills.proficiency_levels` JSONB column for this skill
  3. Publish `SkillUpdatedEvent`
- **Validation:** Exactly 5 levels required. Names must be unique within the skill.
- **DB:** `skills`

## Variations

### Import Skills

- Taxonomy -> Import -> upload CSV with columns: Category, Skill Name, Description, Tags.
- System maps columns, shows preview, and admin confirms.
- Bulk creation includes duplicate detection.

### Deactivate Skill

- Click skill -> Deactivate. Skill is hidden from new declarations.
- Existing employee skills remain but are marked deprecated.

### Merge Duplicate Skills

- Select two or more skills -> Merge -> choose primary skill.
- All employee skill records and job skill requirements move to the primary skill.
- Duplicate skill records are soft-deleted.

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Duplicate category name | `409 Conflict` | "A category with this name already exists" |
| Duplicate skill in category | `409 Conflict` | "This skill already exists in the selected category" |
| Removing proficiency level in use | `400 Bad Request` | "Cannot remove this level because it is already used" |
| Empty category name | `400 Bad Request` | "Category name is required" |

## Related Flows

- [[Userflow/Org-Structure/job-family-setup|Job Family Setup]] - Phase 1 inline required-skill setup
- [[Userflow/Skills-Learning/employee-skill-declaration|Employee Skill Declaration]] - Phase 2
- [[Userflow/Skills-Learning/skill-assessment|Skill Assessment]] - Phase 2
- [[Userflow/Skills-Learning/development-plan|Development Plan]] - Phase 2

## Module References

- [[modules/skills/skill-taxonomy/overview|Skill Taxonomy]]
- [[modules/skills/employee-skills/overview|Employee Skills]]
