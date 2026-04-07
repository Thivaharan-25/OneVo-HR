# Employee Skills — End-to-End Logic

**Module:** Skills
**Feature:** Employee Skills Profile

---

## Get Employee Skills

### Flow

```
GET /api/v1/skills/employee/{employeeId}
  -> SkillController.GetEmployeeSkills(employeeId)
    -> [RequirePermission("skills:read")]
    -> SkillsService.GetEmployeeSkillsAsync(employeeId, ct)
      -> Query employee_skills JOIN skills JOIN skill_categories
      -> Return Result.Success(skillDtos with proficiency levels)
```

## Skill Gap Analysis

### Flow

```
GET /api/v1/skills/gap-analysis/{employeeId}
  -> SkillController.GetGapAnalysis(employeeId)
    -> [RequirePermission("skills:manage")]
    -> SkillsService.GetSkillGapAnalysisAsync(employeeId, ct)
      -> 1. Get employee's job_family via IOrgStructureService
      -> 2. Get required skills: job_skill_requirements for job_family
      -> 3. Get employee's current skills: employee_skills
      -> 4. Compare: for each required skill:
         -> If missing: gap = full requirement
         -> If below min_proficiency: gap = difference
      -> 5. Recommend courses: query course_skill_tags matching gap skills
      -> Return Result.Success(gapAnalysisDtos)
```

## Related

- [[employee-skills]] — feature overview
- [[skill-taxonomy]] — skill and proficiency definitions
- [[skill-assessments]] — assessment responses that drive validation
- [[event-catalog]] — SkillValidated, SkillUpgradeRequested events
- [[error-handling]] — invalid proficiency level and duplicate skill errors
