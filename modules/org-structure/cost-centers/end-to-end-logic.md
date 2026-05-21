# Cost Centers — End-to-End Logic

**Module:** Org Structure
**Feature:** Cost Centers  
**Phase:** Phase 2

---

## Create Cost Center

### Flow

```
POST /api/v1/org/cost-centers
  -> CostCenterController.Create(CreateCostCenterCommand)
    -> [RequirePermission("org:manage")]
    -> CostCenterService.CreateAsync(command, ct)
      -> 1. Validate: code unique within tenant, name required
      -> 2. INSERT into cost_centers
      -> Return Result.Success(costCenterDto)
```

## Assign Department to Cost Center

### Flow

```
PUT /api/v1/org/departments/{id}/cost-center
  -> DepartmentController.AssignCostCenter(id, AssignCostCenterCommand)
    -> [RequirePermission("org:manage")]
    -> OrgStructureService.AssignCostCenterAsync(departmentId, costCenterId, ct)
      -> 1. Validate both exist
      -> 2. UPDATE departments SET cost_center_id = @id
      -> Return Result.Success()
```

### Key Rules

- **Cost centers are Phase 2** and are used in payroll for expense allocation across departments.
- **Budget tracking** per cost center is included in the Phase 2 scope.

## Related

- [[modules/org-structure/cost-centers/overview|Overview]]
- [[modules/org-structure/departments/overview|Departments]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
