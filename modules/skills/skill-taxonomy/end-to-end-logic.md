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

- [[skill-taxonomy]] — feature overview
- [[employee-skills]] — skills consumed from taxonomy
- [[skill-assessments]] — questions linked to taxonomy skills
- [[event-catalog]] — SkillCreated, SkillUpdated events
- [[error-handling]] — duplicate name, inactive category, and FK constraint errors
