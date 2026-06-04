# Job Hierarchy — End-to-End Logic

**Module:** Org Structure  
**Feature:** Job Hierarchy

---

## Create Job Family

### Flow

```
POST /api/v1/org/job-families
  -> JobHierarchyController.CreateFamily(CreateJobFamilyCommand)
    -> [RequirePermission("org:manage")]
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
POST /api/v1/org/job-levels
  -> [RequirePermission("org:manage")]
  -> JobHierarchyService.CreateLevelAsync(command, ct)
    -> 1. Validate name uniqueness within job family
    -> 2. Validate job_family_id exists and rank uniqueness within that job family (numeric, e.g., 100, 200, 300)
    -> 3. Create JobLevel entity with job_family_id, name, rank, and optional suggested_role_id
    -> 4. Persist to job_levels table
    -> Return Result<JobLevelDto>
  -> 201 Created
```

## Create Job Title

### Flow

```
POST /api/v1/org/job-titles
  -> [RequirePermission("org:manage")]
  -> FluentValidation: name required; job_family_id optional; job_level_id optional
  -> JobHierarchyService.CreateTitleAsync(command, ct)
    -> 1. Validate name uniqueness within tenant
    -> 2. If job_family_id provided: validate family exists and belongs to tenant
    -> 3. If job_level_id provided:
           a. Validate level exists and belongs to tenant
           b. Validate level.job_family_id == job_family_id (level must belong to supplied family)
    -> 4. job_level_id without job_family_id is rejected:
           "Cannot set a level without a family"
    -> 5. Create JobTitle entity (job_family_id nullable, job_level_id nullable)
    -> 6. Persist to job_titles table
    -> 7. Publish JobTitleCreated event
    -> Return Result<JobTitleDto>
  -> 201 Created
```

Minimum valid request: `{ "name": "Software Engineer" }` — no family or level required.

## Update Job Title

### Flow

```
PUT /api/v1/org/job-titles/{id}
  -> [RequirePermission("org:manage")]
  -> JobHierarchyService.UpdateTitleAsync(id, command, ct)
    -> 1. Load title by id (tenant-scoped)
    -> 2. If name changed: validate uniqueness within tenant
    -> 3. If job_family_id changed: validate family exists and belongs to tenant
    -> 4. If job_level_id changed: validate level belongs to the (new or existing) family
    -> 5. Persist updated title
    -> Return Result<JobTitleDto>
  -> 200 OK
```

## List Job Families

### Flow

```
GET /api/v1/org/job-families
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
GET /api/v1/org/job-titles?familyId={id}&levelId={id}
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
| Duplicate family name in tenant | 409 | "Job family name already exists" |
| Duplicate level rank within family | 409 | "A level with this rank already exists for this job family" |
| Duplicate title name in tenant | 409 | "A job title with this name already exists" |
| job_family_id provided but not found | 422 | "Job family not found" |
| job_level_id provided but not found | 422 | "Job level not found" |
| job_level_id provided without job_family_id | 422 | "Cannot set a level without a family" |
| job_level_id does not belong to supplied family | 422 | "Job level does not belong to the selected family" |
| Delete family with linked titles | 422 | "Cannot delete — job titles are linked to this family" |
| Delete level with linked titles | 422 | "Cannot delete — job titles are linked to this level" |
| Delete title in use by positions or employees | 422 | "Cannot delete — job title is in use" |

### Edge Cases

- Rank values use gaps (100, 200, 300) to allow insertion without reordering
- Levels are ordered by numeric rank, not alphabetically
- A title with no family or level is valid and immediately usable in position setup
- Deleting a job family or level that has linked titles is blocked; titles must be unlinked first
- Job titles referenced by positions or employee_assignment_history cannot be deleted

## Related

- [[modules/org-structure/job-hierarchy/overview|Overview]]
- [[modules/org-structure/departments/overview|Departments]]
- [[modules/org-structure/legal-entities/overview|Legal Entities]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]



