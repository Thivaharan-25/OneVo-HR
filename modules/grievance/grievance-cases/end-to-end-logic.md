# Grievance Cases — End-to-End Logic

**Module:** Grievance
**Feature:** Grievance Cases

---

## File Grievance

### Flow

```
POST /api/v1/grievances
  -> GrievanceController.File(FileGrievanceCommand)
    -> [RequirePermission("grievance:write")]
    -> GrievanceService.FileAsync(command, ct)
      -> 1. Validate category: harassment, discrimination, safety, policy_violation, other
      -> 2. If is_anonymous = true:
         -> Set filed_by_id = null (protect identity)
      -> 3. INSERT into grievance_cases
         -> status = 'filed', severity based on category
      -> 4. Notify HR team via notifications module
      -> Return Result.Success(grievanceDto)
```

## Resolve Grievance

### Flow

```
POST /api/v1/grievances/{id}/resolve
  -> GrievanceController.Resolve(id, ResolveCommand)
    -> [RequirePermission("grievance:manage")]
    -> GrievanceService.ResolveAsync(id, command, ct)
      -> 1. Load case, validate status = 'investigating'
      -> 2. UPDATE status = 'resolved'
         -> resolution text, resolved_by_id, resolved_at
      -> 3. Notify parties (if not anonymous)
      -> Return Result.Success()
```

### Error Scenarios

| Error | Handling |
|:------|:---------|
| Case not found | Return 404 |
| Already resolved | Return 400 |
| Cannot reveal anonymous filer | filed_by_id always null in response for anonymous cases |

## Related

- [[grievance-cases]] — feature overview
- [[disciplinary-actions]] — outcomes that may follow resolution
- [[event-catalog]] — events emitted on case filing, escalation, and resolution
- [[error-handling]] — workflow state machine error patterns
