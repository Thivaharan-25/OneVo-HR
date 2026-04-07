# Application Tracking — End-to-End Logic

**Module:** Activity Monitoring
**Feature:** Application Tracking

---

## Get Application Usage

### Flow

```
GET /api/v1/activity/apps/{employeeId}?date=2026-04-05
  -> ActivityController.GetAppUsage(employeeId, date)
    -> [RequirePermission("workforce:view")]
    -> ActivityMonitoringService.GetAppUsageAsync(employeeId, date, ct)
      -> 1. Validate employeeId exists via IEmployeeService
      -> 2. Check caller has access (own data or manager/admin)
      -> 3. Query application_usage WHERE employee_id = @id AND date = @date
         -> JOIN application_categories ON application_name LIKE application_name_pattern
      -> 4. Group by application_category, order by total_seconds DESC
      -> 5. Map to List<ApplicationUsageDto>
      -> Return Result.Success(usageDtos)
```

## Manage Application Categories

### Flow

```
POST /api/v1/activity/categories
  -> ActivityCategoryController.Create(CreateCategoryCommand)
    -> [RequirePermission("monitoring:configure")]
    -> Validation: application_name_pattern is valid glob, category not empty
    -> ActivityCategoryService.CreateAsync(command, ct)
      -> 1. Check for duplicate pattern in tenant
      -> 2. INSERT into application_categories
      -> 3. Invalidate category cache (tenant-scoped)
      -> Return Result.Success(categoryDto)
```

### Error Scenarios

| Error | Handling |
|:------|:---------|
| Employee not found | Return 404 |
| No data for date | Return 200 with empty list |
| Duplicate category pattern | Return 409 Conflict |
| Invalid glob pattern | Return 422 with validation error |

### Edge Cases

- **Window titles are never exposed** — only `application_name` and `window_title_hash` are stored.
- **Category changes don't retroactively update** — existing `is_productive` flags on `application_usage` rows stay as-is. New data uses updated categories.

## Related

- [[activity-monitoring|Activity Monitoring Module]]
- [[application-tracking/overview|Application Tracking Overview]]
- [[raw-data-processing/end-to-end-logic|Raw Data Processing — End-to-End Logic]]
- [[daily-aggregation/end-to-end-logic|Daily Aggregation — End-to-End Logic]]
- [[event-catalog]]
- [[error-handling]]
- [[data-classification]]
- [[multi-tenancy]]
- [[WEEK3-activity-monitoring]]
