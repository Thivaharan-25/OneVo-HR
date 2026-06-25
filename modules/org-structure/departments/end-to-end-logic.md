# Departments - End-to-End Logic

**Module:** Org Structure  
**Feature:** Departments

---

## Create Department

### Flow

```
POST /api/v1/org/departments
  -> DepartmentController.Create(CreateDepartmentCommand)
    -> [RequirePermission("org:manage")]
    -> Resolve selected Company from topbar context and map it to legal_entity_id
    -> Validate actor has org:manage in selected Company
    -> FluentValidation: name required,
       code optional (generated if omitted), parent_department_id optional
    -> DepartmentService.CreateAsync(command, ct)
      -> 1. Validate selected Company exists and belongs to tenant
      -> 2. Validate name uniqueness within selected Company
      -> 3. Validate code uniqueness within selected Company (if provided)
      -> 4. If parent_department_id provided:
           a. Verify parent exists and is active
           b. Verify parent belongs to same Company
      -> 5. If head_position_id provided:
           a. Validate position exists and is active
           b. Validate position type is `unique` (pooled positions cannot be department heads)
           c. Validate position belongs to same Company as department
      -> 6. Build Department entity (legal_entity_id, is_active = true)
      -> 5. Persist to departments table
      -> 6. Publish DepartmentCreated domain event
      -> Return Result<DepartmentDto>
    -> 201 Created
```

## List Departments (Flat or Tree)

### Flow

```
GET /api/v1/org/departments?view=tree|flat
  -> [RequirePermission("employees:read")]
  -> Resolve selected Company from topbar context and map it to legal_entity_id
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
PUT /api/v1/org/departments/{id}
  -> [RequirePermission("org:manage")]
  -> DepartmentService.UpdateAsync(id, command, ct)
    -> 1. Load department by id
    -> 2. If parent_department_id changed:
         a. Validate new parent exists
         b. Verify new parent belongs to same Company as this department
         c. Detect circular references using CTE:
            Walk from new parent up to root; if current dept id found -> reject
    -> 3. If code changed, re-validate uniqueness within selected Company
    -> 4. If head_position_id changed:
         a. Validate position exists and is active
         b. Validate position type is `unique`
         c. Validate position belongs to same Company as department
    -> 5. Update fields and persist
    -> 6. Publish DepartmentUpdated event
    -> Return Result<DepartmentDto>
  -> 200 OK
```

### Error Scenarios

| Scenario | HTTP | Error |
|:---------|:-----|:------|
| Company not found or inactive | 422 | "Company not found or is inactive" |
| Company not in tenant | 422 | "Company does not belong to this tenant" |
| Duplicate name in Company | 409 | "Department name already exists in this Company" |
| Duplicate code in Company | 409 | "Department code already exists in this Company" |
| Parent not found | 422 | "Parent department not found" |
| Parent in different Company | 422 | "Parent department must belong to the same Company" |
| Circular reference detected | 422 | "Circular department hierarchy detected" |
| Head position not found or inactive | 422 | "Position not found or is inactive" |
| Head position is pooled type | 422 | "Department head must be a unique-type position" |
| Head position in different Company | 422 | "Head position must belong to the same Company" |
| Department not found | 404 | "Department not found" |

### Edge Cases

- Circular reference detection: when moving department A under department B, must walk B's ancestry to ensure A is not an ancestor of B
- Deactivating a parent department should cascade-deactivate children or block if children are active
- Department tree can be arbitrarily deep; CTE handles unlimited depth
- head_position_id is nullable (new departments may not have a head position yet)
- A head position may be vacant (no current occupant in position_assignments); this is valid - UI surfaces it as "Vacant"
- head_position_id and positions.department_id form a circular nullable FK within Org Structure; both sides are nullable, so create the department first (head_position_id = NULL), create the position with department_id set, then update the department with head_position_id

## Related

- [[modules/org-structure/departments/overview|Overview]]
- [[modules/org-structure/legal-entities/overview|Legal Entities]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]


