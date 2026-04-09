# Skill Taxonomy — End-to-End Logic

**Module:** Skills
**Feature:** Skill Taxonomy (Categories & Skills)

---

## Create Skill Category

### Flow

```
POST /api/v1/skills/categories
  -> SkillCategoryController.Create(CreateCategoryCommand)
    -> [RequirePermission("skills:manage")]
    -> SkillTaxonomyService.CreateCategoryAsync(command, ct)
      -> 1. Validate name unique within tenant
      -> 2. INSERT into skill_categories
      -> Return Result.Success(categoryDto)
```

## Create Skill

### Flow

```
POST /api/v1/skills
  -> SkillController.Create(CreateSkillCommand)
    -> [RequirePermission("skills:manage")]
    -> SkillTaxonomyService.CreateSkillAsync(command, ct)
      -> 1. Validate category exists
      -> 2. Validate proficiency_levels JSON (5 levels with labels)
      -> 3. INSERT into skills
      -> Return Result.Success(skillDto)
```

## Related

- [[modules/skills/skill-taxonomy/overview|Skill Taxonomy]] — feature overview
- [[modules/skills/employee-skills/overview|Employee Skills]] — skills consumed from taxonomy
- [[modules/skills/skill-assessments/overview|Skill Assessments]] — questions linked to taxonomy skills
- [[backend/messaging/event-catalog|Event Catalog]] — SkillCreated, SkillUpdated events
- [[backend/messaging/error-handling|Error Handling]] — duplicate name, inactive category, and FK constraint errors
