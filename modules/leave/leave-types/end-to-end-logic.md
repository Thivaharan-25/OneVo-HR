# Leave Types — End-to-End Logic

**Module:** Leave  
**Feature:** Leave Types

---

## Create Leave Type

### Flow

```
POST /api/v1/leave/types
  → LeaveTypeController.Create(CreateLeaveTypeCommand)
    → [RequirePermission("leave:manage")]
    → FluentValidation: name required, max 50 chars, is_paid not null
    → LeaveTypeService.CreateAsync(command, ct)
      → Check duplicate name for tenant: SELECT WHERE tenant_id = @tid AND name = @name
      → Map command → LeaveType entity
      → _repository.AddAsync(entity)
      → SaveChangesAsync()
      → Return Result<LeaveTypeDto>
    → 201 Created + Location header
```

### Error Scenarios

| Scenario | HTTP | Error |
|:---------|:-----|:------|
| Missing name | 422 | Validation error |
| Duplicate name for tenant | 409 | "Leave type with this name already exists" |
| No `leave:manage` permission | 403 | Forbidden |

## List Leave Types

### Flow

```
GET /api/v1/leave/types
  → [RequirePermission("leave:read")]
  → LeaveTypeService.GetAllAsync(ct)
    → SELECT * FROM leave_types WHERE tenant_id = @tid AND is_active = true
    → Map to List<LeaveTypeDto>
  → 200 OK
```

## Related

- [[leave-types|Leave Types Overview]]
- [[leave-policies]]
- [[leave-requests]]
- [[event-catalog]]
- [[error-handling]]
