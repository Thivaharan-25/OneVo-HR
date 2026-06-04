# Positions — End-to-End Logic

**Module:** Org Structure  
**Feature:** Positions

---

## Create Position

### Flow

```
POST /api/v1/org/positions
  -> PositionController.Create(CreatePositionCommand)
    -> [RequirePermission("org:manage")]
    -> FluentValidation: name required, legal_entity_id required,
       department_id required,
       capacity required (>= 1), position_type required (unique|pooled),
       reports_to_position_id optional
    -> PositionService.CreateAsync(command, ct)
      -> 1. Validate legal entity exists and belongs to tenant
      -> 2. Validate department exists, belongs to same legal entity
      -> 3. Validate name uniqueness within legal entity
      -> 4. If reports_to_position_id provided:
           a. Verify target position exists and is active
           b. Verify target is in same legal entity
           c. Verify target position_type is 'unique' (pooled positions cannot be reporting targets)
           d. Detect reporting cycles: walk from target up to root;
              reject if current position id is encountered
      -> 5. Build Position entity (is_active = true)
      -> 6. Persist to positions table
      -> 7. Write initial row to position_reporting_history
             (effective_from = today, effective_to = null)
      -> 8. Rebuild employee_hierarchy_closure for affected branch
      -> 9. Publish PositionCreated domain event
      -> Return Result<PositionDto>
    -> 201 Created
```

## Bulk Create Positions

### Flow

```
POST /api/v1/org/positions/bulk
  -> PositionController.BulkCreate(BulkCreatePositionsCommand)
    -> [RequirePermission("org:manage")]
    -> FluentValidation: items required, non-empty, each item same rules as Create
    -> PositionService.BulkCreateAsync(command, ct)
      -> For each item, run the same validation pipeline as Create
      -> Execute all valid items in a single transaction
      -> Return Result<BulkPositionResultDto>:
           { succeeded: [...PositionDto], failed: [...{index, errors}] }
      -> Partial success is allowed: failed items do not roll back succeeded items
    -> 200 OK (even on partial failure; inspect result body for per-item outcome)
```

## List Positions

### Flow

```
GET /api/v1/org/positions?legalEntityId={id}&departmentId={id?}&includeInactive={bool?}
  -> [RequirePermission("employees:read")]
  -> PositionService.GetAllAsync(legalEntityId, filters, ct)
    -> Query positions scoped to tenant + legalEntityId
    -> Optionally filter by departmentId
    -> Include current occupancy count per position (from position_assignments)
    -> Return Result<List<PositionDto>>
  -> 200 OK
```

## Position Reporting Tree

### Flow

```
GET /api/v1/org/positions/tree?legalEntityId={id}
  -> [RequirePermission("employees:read")]
  -> PositionService.GetTreeAsync(legalEntityId, ct)
    -> Recursive CTE from employee_hierarchy_closure filtered to legalEntityId
    -> Each node includes: position name, type, capacity, current_occupancy,
       is_vacant (occupancy == 0), current occupant name if unique + occupied
    -> Return nested PositionTreeNodeDto[]
  -> 200 OK
```

## Update Position

### Flow

```
PUT /api/v1/org/positions/{id}
  -> [RequirePermission("org:manage")]
  -> PositionService.UpdateAsync(id, command, ct)
    -> 1. Load position by id (tenant-scoped)
    -> 2. legal_entity_id is immutable — reject if caller attempts to change it
    -> 3. If name changed: validate uniqueness within legal entity
    -> 4. If department_id changed:
           a. Validate new department belongs to same legal entity
    -> 5. If capacity changed:
           a. Reject reduction below current active occupancy count
    -> 6. If reports_to_position_id changed:
           a. Validate new target exists, is active, same legal entity, type 'unique'
           b. Detect cycles for new reporting target
           c. Update position_reporting_history:
                close current row (effective_to = today - 1)
                insert new row (effective_from = today, effective_to = null)
           d. Rebuild employee_hierarchy_closure for affected branch
    -> 7. Persist updated position
    -> 8. Publish PositionUpdated domain event
    -> Return Result<PositionDto>
  -> 200 OK
```

## Deactivate Position

### Flow

```
DELETE /api/v1/org/positions/{id}
  -> [RequirePermission("org:manage")]
  -> PositionService.DeactivateAsync(id, ct)
    -> 1. Load position by id
    -> 2. Reject if any active position_assignments exist:
           "Cannot deactivate a position with active occupants"
    -> 3. Reject if any active positions report to this position:
           "Cannot deactivate a position that other positions report to"
    -> 4. Set is_active = false
    -> 5. Close open position_reporting_history row (effective_to = today)
    -> 6. Rebuild employee_hierarchy_closure
    -> 7. Publish PositionDeactivated domain event
  -> 204 No Content
```

---

## Error Scenarios

| Scenario | HTTP | Error |
|:---------|:-----|:------|
| Legal entity not found or inactive | 422 | "Legal entity not found or is inactive" |
| Legal entity not in tenant | 422 | "Legal entity does not belong to this tenant" |
| Department not in legal entity | 422 | "Department does not belong to the selected legal entity" |
| Duplicate position name in legal entity | 409 | "A position with this name already exists in this legal entity" |
| Reports-to in different legal entity | 422 | "Reporting position must be in the same legal entity" |
| Reports-to is a pooled position | 422 | "Pooled positions cannot be reporting targets" |
| Circular reporting chain | 422 | "Cannot set reporting line — would create a circular reporting chain" |
| Capacity below current occupancy | 422 | "Capacity cannot be reduced below current occupancy of [N]" |
| Deactivate with active occupants | 422 | "Cannot deactivate a position with active occupants" |
| Deactivate with active reports-to dependents | 422 | "Cannot deactivate a position that other positions report to" |
| legal_entity_id change attempted | 422 | "Legal entity cannot be changed after creation" |
| Position not found | 404 | "Position not found" |

---

## Edge Cases

- **Cycle detection:** when updating `reports_to_position_id`, walk from the new target upward to the root via the current `reports_to_position_id` chain. Reject if the position being updated is encountered anywhere in that chain.
- **Closure table rebuild:** always scoped to the affected sub-tree, not a full table rebuild. Triggered by any create, reporting-target change, or deactivation.
- **Bulk partial failure:** bulk create returns per-item success/failure. Succeeded items are committed even when some items fail. Callers must inspect the `failed` array.
- **History gap prevention:** `position_reporting_history` effective date ranges for a given `position_id` must not overlap. On update, the existing open row is closed the day before the new row opens.

---

## Related

- [[modules/org-structure/positions/overview|Overview]]
- [[modules/org-structure/legal-entities/overview|Legal Entities]]
- [[modules/org-structure/departments/overview|Departments]]
- [[modules/org-structure/job-hierarchy/overview|Job Hierarchy]]
- [[modules/core-hr/overview|Core HR]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
- [[database/migration-patterns|Migration Patterns]]
