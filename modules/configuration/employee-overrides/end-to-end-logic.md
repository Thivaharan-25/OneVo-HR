# Employee Overrides — End-to-End Logic

**Module:** Configuration
**Feature:** Per-Employee Monitoring Overrides

---

## Set Employee Override

### Flow

```
POST /api/v1/settings/monitoring/overrides
  -> MonitoringController.SetOverride(SetOverrideCommand)
    -> [RequirePermission("monitoring:configure")]
    -> ConfigurationService.SetEmployeeOverrideAsync(command, ct)
      -> 1. Validate employee exists via IEmployeeService
      -> 2. UPSERT into employee_monitoring_overrides
         -> ON CONFLICT (tenant_id, employee_id) DO UPDATE
      -> 3. Store override_reason and set_by_id
      -> 4. Invalidate cache for this employee
      -> 5. Log to audit_logs
      -> Return Result.Success()
```

## Bulk Set Overrides

### Flow

```
POST /api/v1/settings/monitoring/overrides/bulk
  -> MonitoringController.BulkOverride(SetBulkOverrideCommand)
    -> [RequirePermission("monitoring:configure")]
    -> ConfigurationService.SetBulkOverrideAsync(command, ct)
      -> 1. Resolve target employees by department/team/job_family
      -> 2. For each employee: UPSERT override
         -> Skip employees who already have individual overrides (individual > bulk)
      -> 3. Invalidate cache for all affected employees
      -> Return Result.Success(affectedCount)
```

### Key Rules

- **Null means inherit from tenant toggle.** Only non-null values override.
- **Individual overrides take precedence** over bulk overrides.
- **Merge logic:** `effectivePolicy.Feature = employeeOverride?.Feature ?? tenantToggles.Feature`

## Related

- [[frontend/architecture/overview|Employee Overrides Overview]]
- [[frontend/architecture/overview|Monitoring Toggles]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
