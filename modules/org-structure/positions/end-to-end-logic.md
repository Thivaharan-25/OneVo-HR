# Positions - End-to-End Logic

**Module:** Org Structure  
**Feature:** Positions

---

## Create Position

### Flow

```
POST /api/v1/org/positions
  -> PositionController.Create(CreatePositionCommand)
    -> [RequirePermission("org:manage")]
    -> Resolve selected Company from topbar context and map it to legal_entity_id
    -> FluentValidation: name required,
       department_id required,
       max_occupancy required (>= 1), position_type required (unique|pooled),
       reports_to_position_id required unless root position
    -> PositionService.CreateAsync(command, ct)
      -> 1. Validate selected Company exists and belongs to tenant
      -> 1a. Validate caller can manage positions inside the selected Company context
      -> 2. Validate department exists, belongs to selected Company
      -> 3. Validate name uniqueness within selected Company
      -> 4. If reports_to_position_id provided:
           a. Verify target position exists and is active
           b. Verify target is in same Company
           c. Verify target position_type is 'unique' (pooled positions cannot be reporting targets)
           d. Detect reporting cycles: walk from target up to root;
              reject if current position id is encountered
      -> 5. Build Position entity (is_active = true)
      -> 6. Persist to positions table
      -> 7. Write initial row to position_reporting_history
             (effective_from = today, effective_to = null)
      -> 8. If reports_to_position_id exists:
             create locked management_coverage_records row:
             owner_position_id = reports_to_position_id,
             covered_target_type = Position,
             covered_position_id = new position id,
             source = ReportingStructure,
             is_locked = true
      -> 8a. Rebuild employee_hierarchy_closure for reporting views
      -> 9. If "Grant system access from this position" is enabled:
           a. Validate actor has roles:manage to edit position access template fields
           b. Persist internal position access grant rule
           c. Persist manual management_coverage_records from Can manage employees in
           d. If a selected covered target already has owners, add this position as the next backup owner unless the actor clicks Make primary
      -> 10. Publish PositionCreated domain event
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
GET /api/v1/org/positions?departmentId={id?}&includeInactive={bool?}
  -> [RequirePermission("employees:read")]
  -> Resolve selected Company from topbar context and map it to legal_entity_id
  -> PositionService.GetAllAsync(legalEntityContext, filters, ct)
    -> Query positions scoped to tenant + selected Company
    -> Optionally filter by departmentId
    -> Include current occupancy count per position (from position_assignments)
    -> Return Result<List<PositionDto>>
  -> 200 OK
```

## Position Reporting Tree

### Flow

```
GET /api/v1/org/positions/tree
  -> [RequirePermission("employees:read")]
  -> Resolve selected Company from topbar context and map it to legal_entity_id
  -> PositionService.GetTreeAsync(legalEntityContext, ct)
    -> Recursive CTE from employee_hierarchy_closure filtered to selected Company
    -> Each node includes: position name, assigned employee/vacancy, department,
       type, max_occupancy, current_occupancy, and quick vacancy/access badges
    -> Org chart is visualization only; permission editing opens position detail/modal
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
    -> 2. legal_entity_id is immutable - reject if caller attempts to change it
    -> 3. If name changed: validate uniqueness within selected Company
    -> 4. If department_id changed:
           a. Validate new department belongs to same Company
    -> 5. If max_occupancy changed:
           a. Reject reduction below current active occupancy count
    -> 6. If reports_to_position_id changed:
           a. Validate new target exists, is active, same Company, type 'unique'
           b. Detect cycles for new reporting target
           c. Update position_reporting_history:
                close current row (effective_to = today - 1)
                insert new row (effective_from = today, effective_to = null)
           d. Remove old locked ReportingStructure coverage created by the old Reports to relation
           e. Create new locked ReportingStructure coverage for the new Reports to relation
           f. Preserve manual coverage and recompute owner order for affected targets
           g. Rebuild employee_hierarchy_closure for reporting views
    -> 7. Persist updated position
      -> 8. If optional access block changed:
           a. Validate actor has roles:manage to edit position access template fields
           b. Persist internal access grant rule changes
           c. Persist manual management coverage changes
           d. If locked ReportingStructure coverage removal is attempted, reject:
              "This access comes from the reporting structure. Change the position's Reports to value to remove it."
           e. If approval is required for generated grants, create access_grant_requests
              and notify the single eligible owner resolved by management coverage;
              do not invoke Workflow Engine in Phase 1
    -> 9. Publish PositionUpdated domain event
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
| Company not found or inactive | 422 | "Company not found or is inactive" |
| Company not in tenant | 422 | "Company does not belong to this tenant" |
| Department not in Company | 422 | "Department does not belong to the selected Company" |
| Duplicate position name in Company | 409 | "A position with this name already exists in this Company" |
| Reports-to in different Company | 422 | "Reporting position must be in the same Company" |
| Reports-to is a pooled position | 422 | "Pooled positions cannot be reporting targets" |
| Circular reporting chain | 422 | "Cannot set reporting line - would create a circular reporting chain" |
| Capacity below current occupancy | 422 | "Capacity cannot be reduced below current occupancy of [N]" |
| Deactivate with active occupants | 422 | "Cannot deactivate a position with active occupants" |
| Deactivate with active reports-to dependents | 422 | "Cannot deactivate a position that other positions report to" |
| legal_entity_id change attempted | 422 | "Company cannot be changed after creation" |
| Locked reporting-structure coverage removal attempted | 422 | "This access comes from the reporting structure. Change the position's Reports to value to remove it." |
| Position not found | 404 | "Position not found" |

---

## Edge Cases

- **Cycle detection:** when updating `reports_to_position_id`, walk from the new target upward to the root via the current `reports_to_position_id` chain. Reject if the position being updated is encountered anywhere in that chain.
- **Closure table rebuild:** always scoped to the affected sub-tree, not a full table rebuild. Triggered by any create, reporting-target change, or deactivation.
- **Bulk partial failure:** bulk create returns per-item success/failure. Succeeded items are committed even when some items fail. Callers must inspect the `failed` array.
- **History gap prevention:** `position_reporting_history` effective date ranges for a given `position_id` must not overlap. On update, the existing open row is closed the day before the new row opens.
- **Assignment kinds:** `PrimaryEmployment` drives Company and policy inheritance. `AdditionalAuthority` grants role/access/approval authority only.
- **Management coverage owner order:** for each covered Position, Department, or Company target, try Primary owner first, then Backup owner 1, Backup owner 2, and so on. Primary owner / Backup owner labels are display labels for ordered management coverage owners — they are not hardcoded routing slots. Backend routing must support any number of active coverage owners. For monitoring alerts, recipient selection is availability-based through Monitoring Policy. For approval routing, owners are ordered by `owner_order` and permission checks; if the first owner is unavailable and the workflow/policy requires availability-aware routing, continue to the next eligible owner.
- **No duplicate approvals:** approval routing assigns one request to one eligible owner at a time. If none exists, create a routing issue.
- **No workflow dependency:** Position access approvals in Phase 1 use management coverage, lightweight approval records, routing issues, and Notifications, not Workflow Engine.

---

## Related

- [[modules/org-structure/positions/overview|Overview]]
- [[modules/org-structure/legal-entities/overview|Legal Entities]]
- [[modules/org-structure/departments/overview|Departments]]
- [[modules/core-hr/overview|Core HR]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
- [[database/migration-patterns|Migration Patterns]]
