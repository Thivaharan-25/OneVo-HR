# Time Off Types - End-to-End Logic

**Module:** Time Off  
**Feature:** Time Off Types

---

## Create Time Off Type

### Flow

```
POST /api/v1/time-off/types
  -> TimeOffTypeController.Create(CreateTimeOffTypeCommand)
    -> [RequirePermission("time_off:manage")]
    -> FluentValidation: name required, max 50 chars, is_paid not null
    -> TimeOffTypeService.CreateAsync(command, ct)
      -> Check duplicate name for tenant: SELECT WHERE tenant_id = @tid AND name = @name
      -> Map command -> TimeOffType entity
      -> _repository.AddAsync(entity)
      -> SaveChangesAsync()
      -> Return Result<TimeOffTypeDto>
    -> 201 Created + Location header
```

### Error Scenarios

| Scenario | HTTP | Error |
|:---------|:-----|:------|
| Missing name | 422 | Validation error |
| Duplicate name for tenant | 409 | "Time off type with this name already exists" |
| No `time_off:manage` permission | 403 | Forbidden |

## List Time Off Types

### Flow

```
GET /api/v1/time-off/types
  -> [RequirePermission("time_off:read")]
  -> TimeOffTypeService.GetAllAsync(ct)
    -> SELECT * FROM time_off_types WHERE tenant_id = @tid AND is_active = true
    -> Map to List<TimeOffTypeDto>
  -> 200 OK
```

## Related

- [[modules/time-off/time-off-types/overview|Time Off Types Overview]]
- [[modules/time-off/time-off-policies/overview|Time Off Policies]]
- [[modules/time-off/time-off-requests/overview|Time Off Requests]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
