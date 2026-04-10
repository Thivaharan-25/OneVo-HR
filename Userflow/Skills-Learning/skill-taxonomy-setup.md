# Skill Taxonomy Setup

**Area:** Skills & Learning  
**Phase:** Phase 1
**Trigger:** Admin defines skill categories and levels (user action — configuration)
**Required Permission(s):** `skills:manage`  
**Related Permissions:** `skills:read` (to view taxonomy without editing)

---

## Preconditions

- Tenant is active and skills module is enabled
- User has admin-level access to the skills module
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Navigate to Skill Taxonomy
- **UI:** Skills → Taxonomy. Tree view displays existing skill categories with nested skills. Each category shows: name, skill count, last modified date. "Create Category" button in top-right. Expand category to see individual skills with proficiency level definitions
- **API:** `GET /api/v1/skills/taxonomy`
- **Backend:** `SkillTaxonomyService.GetTaxonomyTreeAsync()` → [[skills]]
- **Validation:** Permission check for `skills:manage`
- **DB:** `skill_categories`, `skills`, `proficiency_levels`

### Step 2: Create Skill Category
- **UI:** Modal form opens: Category Name (required, e.g., "Programming Languages"), Description (optional, e.g., "Software development languages and frameworks"), Icon/Color selector for visual identification, Display Order (numeric for sorting)
- **API:** `POST /api/v1/skills/categories`
  ```json
  {
    "name": "Programming Languages",
    "description": "Software development languages and frameworks",
    "icon": "code",
    "color": "#4A90D9",
    "displayOrder": 5
  }
  ```
- **Backend:** `SkillCategoryService.CreateAsync()` → [[skills]]
  1. Validate category name is unique within tenant
  2. Create `skill_categories` record
  3. Publish `SkillCategoryCreatedEvent`
  4. Create audit log entry
- **Validation:** Category name must be unique, max 100 characters. Display order must be positive integer
- **DB:** `skill_categories`, `audit_logs`

### Step 3: Add Skills Within Category
- **UI:** Inside category detail view, click "Add Skill". Form fields: Skill Name (e.g., "Python"), Description (optional, e.g., "Python programming language including frameworks like Django, Flask"), Tags (e.g., "backend", "data-science"). Bulk add option: paste multiple skill names (one per line) for quick creation
- **API:** `POST /api/v1/skills/categories/{categoryId}/skills`
  ```json
  {
    "name": "Python",
    "description": "Python programming language including frameworks",
    "tags": ["backend", "data-science"]
  }
  ```
- **Backend:** `SkillService.CreateAsync()` → [[skills]]
  1. Validate skill name is unique within category
  2. Create `skills` record linked to category
  3. If bulk add: process each skill in a transaction
  4. Publish `SkillCreatedEvent` for each
- **Validation:** Skill name unique within category. Max 100 characters per name
- **DB:** `skills`

### Step 4: Define Proficiency Level Labels Per Skill
- **UI:** Inside a skill's detail view, click "Edit Proficiency Levels". Shows 5 level slots (1–5, fixed count). For each level: Name (e.g., "Beginner", "Intermediate", "Advanced", "Expert", "Master"), Description (e.g., "Can perform basic tasks with guidance"). Levels 1–5 are always present — admin customises the labels and descriptions. Save applies to this skill only
- **API:** `PUT /api/v1/skills/{skillId}/proficiency-levels`
  ```json
  {
    "levels": [
      { "value": 1, "name": "Beginner", "description": "Can perform basic tasks with guidance" },
      { "value": 2, "name": "Intermediate", "description": "Can work independently on standard tasks" },
      { "value": 3, "name": "Advanced", "description": "Can handle complex tasks and mentor others" },
      { "value": 4, "name": "Expert", "description": "Industry-level expertise" },
      { "value": 5, "name": "Master", "description": "Drives innovation and defines best practices" }
    ]
  }
  ```
- **Backend:** `SkillService.UpdateProficiencyLabelsAsync()`
  1. Validate exactly 5 levels provided, values 1–5
  2. Update `skills.proficiency_levels` jsonb column for this skill
  3. Publish `SkillUpdatedEvent`
- **Validation:** Exactly 5 levels required (values 1–5 are fixed). Names must be unique within the skill. Max 50 characters per name
- **DB:** `skills` (updates `proficiency_levels` jsonb column)

### Step 5: Save and Publish Taxonomy
- **UI:** Taxonomy tree updates in real-time as changes are made. "Published" badge shown next to categories with at least one skill. Employees can immediately browse and declare skills from published categories. Toast notification: "Taxonomy updated successfully"
- **API:** N/A (changes saved in prior steps)
- **Backend:** Taxonomy is immediately available for employee skill declarations
- **Validation:** N/A
- **DB:** None (already persisted)

## Variations

### When importing skills from an external source
- Taxonomy → Import → upload CSV with columns: Category, Skill Name, Description, Tags
- System maps columns, shows preview, admin confirms
- Bulk creation with duplicate detection (skip or merge)

### When deactivating a skill
- Click skill → "Deactivate" — skill hidden from new declarations
- Existing employee skills retained but marked as deprecated
- Can be reactivated later

### When merging duplicate skills
- Select two or more skills → "Merge" → choose primary skill name
- All employee skill records reassigned to primary
- Duplicate skill records soft-deleted

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Duplicate category name | `409 Conflict` | "A category with this name already exists" |
| Duplicate skill in category | `409 Conflict` | "This skill already exists in the selected category" |
| Removing proficiency level in use | `400 Bad Request` | "Cannot remove level 'Expert' — 15 employees have this rating. Reassign first" |
| Empty category name | `400 Bad Request` | "Category name is required" |

## Events Triggered

- `SkillCategoryCreatedEvent` → [[backend/messaging/event-catalog|Event Catalog]] — consumed by audit logging
- `SkillCreatedEvent` → [[backend/messaging/event-catalog|Event Catalog]] — consumed by audit logging, search indexing
- `ProficiencyLevelsUpdatedEvent` → [[backend/messaging/event-catalog|Event Catalog]] — consumed by employee skill recalculation
- `AuditLogEntry` (action: `skill_taxonomy.updated`) → [[modules/auth/audit-logging/overview|Audit Logging]]

## Related Flows

- [[Userflow/Skills-Learning/employee-skill-declaration|Employee Skill Declaration]] — employees declare skills from this taxonomy
- [[Userflow/Skills-Learning/skill-assessment|Skill Assessment]] — managers validate employee skills
- [[Userflow/Skills-Learning/development-plan|Development Plan]] — skill gaps identified from taxonomy

## Module References

- [[skills]] — skills module overview and architecture
- [[modules/skills/skill-taxonomy/overview|Skill Taxonomy]] — taxonomy data model and tree structure
- [[modules/skills/employee-skills/overview|Employee Skills]] — employee skill records linked to taxonomy
