# Resource Management — End-to-End Logic

**Module:** WorkSync
**Feature:** Resource Management

---

## Create Resource Allocation

```
POST /api/v1/projects/{id}/resource-plan/allocations
  body: { user_id, start_date, end_date, allocation_percentage, role_description }
  → CreateAllocationHandler
    → 1. Verify project exists, user has resources:manage
    → 2. Verify user is workspace member
    → 3. Check total allocation for user in date range:
         SELECT SUM(allocation_percentage) FROM resource_allocations
         WHERE user_id = ? AND date ranges overlap
         existing_total = SUM(...)
         If existing_total + new_percentage > 100:
           Emit over-allocation warning (not a hard block)
           Publish ResourceOverAllocatedEvent
    → 4. INSERT resource_allocations
    → Return Result<AllocationDto>
  → 201 Created
```

## Availability Calculation

```
GET /api/v1/workspaces/{wsId}/availability
  query: { user_ids, date_from, date_to }
  → GetAvailabilityHandler
    → For each user:
        1. Get base capacity: employees.standard_hours_per_week / 5 (hours/day)
           via IEmployeeService.GetContractedHoursAsync()
        2. Apply overrides: SELECT * FROM resource_availability_overrides
                            WHERE user_id = ? AND date ranges overlap
           → override.available_hours_per_day takes precedence
        3. Get leave days: IEmployeeService.GetLeaveAsync(user_id, date_from, date_to)
           → approved leave_requests in range
        4. Available working days = total working days - leave days
        5. Available hours = available_hours_per_day × available_working_days
    → Return availability per user per day
```

## Add Availability Override

```
POST /api/v1/workspaces/{wsId}/availability-overrides
  body: { user_id, date_from, date_to, available_hours_per_day, reason }
  → CreateOverrideHandler
    → 1. Verify user is workspace member
    → 2. No overlap validation — multiple overrides allowed (last one wins per day)
    → 3. INSERT resource_availability_overrides
    → Return 201
```

### Error Scenarios

| Scenario | HTTP | Error |
|:---------|:-----|:------|
| User not in workspace | 422 | User must be a workspace member |
| allocation_percentage < 1 or > 100 | 422 | Percentage must be 1–100 |
| available_hours_per_day < 0 | 422 | Hours cannot be negative |

## Related

- [[modules/work-management/resources/overview|Resources Overview]]
- [[modules/work-management/resources/testing|Resources Testing]]
