# Job Hierarchy — End-to-End Logic

**Module:** Org Structure  
**Feature:** Job Hierarchy

---

## Create Job Family

### Flow

```
POST /api/v1/job-families
  -> JobHierarchyController.CreateFamily(CreateJobFamilyCommand)
    -> [RequirePermission("settings:admin")]
    -> FluentValidation: name required + unique within tenant
    -> JobHierarchyService.CreateFamilyAsync(command, ct)
      -> 1. Validate name uniqueness within tenant
      -> 2. Create JobFamily entity
      -> 3. Persist to job_families table
      -> 4. Publish JobFamilyCreated event
      -> Return Result<JobFamilyDto>
    -> 201 Created
```

## Create Job Level

### Flow

```
POST /api/v1/job-levels
  -> [RequirePermission("settings:admin")]
  -> JobHierarchyService.CreateLevelAsync(command, ct)
    -> 1. Validate name uniqueness within tenant
    -> 2. Validate rank uniqueness within tenant (numeric, e.g., 100, 200, 300)
    -> 3. Create JobLevel entity with name and rank
    -> 4. Persist to job_levels table
    -> Return Result<JobLevelDto>
  -> 201 Created
```

## Create Job Title

### Flow

```
POST /api/v1/job-titles
  -> [RequirePermission("settings:admin")]
  -> JobHierarchyService.CreateTitleAsync(command, ct)
    -> 1. Validate job_family_id exists
    -> 2. Validate job_level_id exists
    -> 3. Validate title name uniqueness within same family + level
    -> 4. Create JobTitle entity linked to family and level
    -> 5. Persist to job_titles table
    -> 6. Publish JobTitleCreated event
    -> Return Result<JobTitleDto>
  -> 201 Created
```

## List Job Families

### Flow

```
GET /api/v1/job-families
  -> [RequirePermission("employees:read")]
  -> JobHierarchyService.GetFamiliesAsync(ct)
    -> Query job_families filtered by tenant
    -> Include count of associated titles
    -> Return List<JobFamilyDto>
  -> 200 OK
```

## List Job Titles (with family and level info)

### Flow

```
GET /api/v1/job-titles?familyId={id}&levelId={id}
  -> [RequirePermission("employees:read")]
  -> JobHierarchyService.GetTitlesAsync(filters, ct)
    -> 1. Query job_titles with joins to job_families and job_levels
    -> 2. Apply optional filters (familyId, levelId)
    -> 3. Order by job_levels.rank ascending
    -> Return List<JobTitleDto> (includes family_name, level_name, rank)
  -> 200 OK
```

### Error Scenarios

| Scenario | HTTP | Error |
|:---------|:-----|:------|
| Duplicate family name | 409 | "Job family name already exists" |
| Duplicate level rank | 409 | "A level with this rank already exists" |
| Title with invalid family | 422 | "Job family not found" |
| Title with invalid level | 422 | "Job level not found" |
| Duplicate title in same family+level | 409 | "Title already exists for this family and level" |

### Edge Cases

- Rank values use gaps (100, 200, 300) to allow insertion without reordering
- Deleting a job level or family that has associated titles is blocked
- Job titles are used by employee_positions; deletion is blocked if in use
- Levels are ordered by numeric rank, not alphabetically

## Related

- [[modules/org-structure/job-hierarchy/overview|Overview]]
- [[modules/org-structure/departments/overview|Departments]]
- [[modules/org-structure/legal-entities/overview|Legal Entities]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
