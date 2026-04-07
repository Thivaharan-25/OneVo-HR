# Leave Policies — End-to-End Logic

**Module:** Leave
**Feature:** Leave Policies

---

## Create Leave Policy

### Flow

```
POST /api/v1/leave/policies
  -> LeavePolicyController.Create(CreatePolicyCommand)
    -> [RequirePermission("leave:manage")]
    -> Validation: leave_type_id exists, annual_entitlement_days > 0
    -> LeavePolicyService.CreateAsync(command, ct)
      -> 1. Check if active policy exists for same leave_type + country + job_level
         -> If exists: create new version
            -> Set old policy: superseded_by_id = new_policy.id
         -> If not: create first version
      -> 2. INSERT into leave_policies
         -> effective_from = command.EffectiveFrom
         -> superseded_by_id = null (this is the active version)
      -> 3. Log to audit_logs
      -> Return Result.Success(policyDto)
```

## Get Active Policy

### Flow

```
GET /api/v1/leave/policies?leaveTypeId={id}&countryId={id}
  -> LeavePolicyController.List(query)
    -> [RequirePermission("leave:manage")]
    -> LeavePolicyService.GetActivePoliciesAsync(query, ct)
      -> Query: WHERE superseded_by_id IS NULL (active only)
      -> Filter by leave_type_id, country_id, job_level_id
      -> Return Result.Success(policyDtos)
```

### Key Rules

- **Policy versioning** via `superseded_by_id` chain. Active policy: `WHERE superseded_by_id IS NULL`.
- **Country-specific:** Policies can apply to specific countries (e.g., UK gets 28 days, US gets 15 days).
- **Job-level-specific:** Senior roles may get more days than junior roles.
- **Proration methods:** `calendar_days` or `working_days` for mid-year hires.

## Related

- [[leave-policies|Leave Policies Overview]]
- [[leave-entitlements]]
- [[leave-types]]
- [[event-catalog]]
- [[error-handling]]
