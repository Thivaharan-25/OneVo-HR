# Departments — End-to-End Logic

**Module:** Org Structure  
**Feature:** Departments

---

## Create Department

### Flow

```
POST /api/v1/departments
  -> DepartmentController.Create(CreateDepartmentCommand)
    -> [RequirePermission("settings:admin")]
    -> FluentValidation: name required, code required + unique,
       legal_entity_id required, parent_department_id optional
    -> DepartmentService.CreateAsync(command, ct)
      -> 1. Validate legal_entity_id exists and is active
      -> 2. Validate code uniqueness within tenant
      -> 3. If parent_department_id provided:
           a. Verify parent exists and is active
           b. Verify parent belongs to same legal entity
      -> 4. If head_employee_id provided, validate employee exists
      -> 5. Build Department entity (is_active = true)
      -> 6. Persist to departments table
      -> 7. Publish DepartmentCreated domain event
      -> Return Result<DepartmentDto>
    -> 201 Created
```

## List Departments (Flat or Tree)

### Flow

```
GET /api/v1/departments?view=tree|flat
  -> [RequirePermission("employees:read")]
  -> DepartmentService.GetAllAsync(view, ct)
    -> If view = "flat":
         -> Simple query with optional filtering
    -> If view = "tree":
         -> CTE recursive query:
            WITH RECURSIVE dept_tree AS (
              SELECT * FROM departments WHERE parent_department_id IS NULL
              UNION ALL
              SELECT d.* FROM departments d
              JOIN dept_tree dt ON d.parent_department_id = dt.id
            )
         -> Materialize into nested DepartmentTreeDto
    -> Return result
  -> 200 OK
```

## Update Department

### Flow

```
PUT /api/v1/departments/{id}
  -> [RequirePermission("settings:admin")]
  -> DepartmentService.UpdateAsync(id, command, ct)
    -> 1. Load department by id
    -> 2. If parent_department_id changed:
         a. Validate new parent exists
         b. Detect circular references using CTE:
            Walk from new parent up to root; if current dept id found -> reject
    -> 3. If code changed, re-validate uniqueness
    -> 4. If head_employee_id changed, validate employee exists
    -> 5. Update fields and persist
    -> 6. Publish DepartmentUpdated event
    -> Return Result<DepartmentDto>
  -> 200 OK
```

### Error Scenarios

| Scenario | HTTP | Error |
|:---------|:-----|:------|
| Duplicate code | 409 | "Department code already exists" |
| Invalid legal entity | 422 | "Legal entity not found or inactive" |
| Parent not found | 422 | "Parent department not found" |
| Circular reference detected | 422 | "Circular department hierarchy detected" |
| Cross-entity parent | 422 | "Parent must belong to same legal entity" |
| Head employee not found | 422 | "Employee not found" |
| Department not found | 404 | "Department not found" |

### Edge Cases

- Circular reference detection: when moving department A under department B, must walk B's ancestry to ensure A is not an ancestor of B
- Deactivating a parent department should cascade-deactivate children or block if children are active
- Department tree can be arbitrarily deep; CTE handles unlimited depth
- head_employee_id is nullable (new departments may not have a head yet)

## Related

- [[departments|Overview]]
- [[legal-entities]]
- [[cost-centers]]
- [[teams]]
- [[job-hierarchy]]
- [[event-catalog]]
- [[error-handling]]
