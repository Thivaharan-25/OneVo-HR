# Time Off Policies - End-to-End Logic

**Module:** Time Off
**Feature:** Time Off Policies

---

## Create Time Off Policy

### Flow

```
POST /api/v1/time-off/policies
  -> TimeOffPolicyController.Create(CreatePolicyCommand)
    -> [RequirePermission("time_off:manage")]
    -> Resolve selected Company from topbar context to legal_entity_id
    -> Verify actor has time_off:manage in selected Company
    -> Validation:
       -> name required
       -> each rule references an active time_off_type_id
       -> policy rule values are valid
       -> assignment targets are inside selected Company scope
    -> TimeOffPolicyService.CreateAsync(command, ct)
      -> 1. Create policy header
      -> 2. INSERT time_off_policy_rules for selected time off types
      -> 3. INSERT time_off_policy_assignments for legal_entity_default, department, position, or employee_override inside the selected Company
      -> 4. Close replaced policy with effective_to or deactivate it for the same assignment scope/effective period
      -> 5. Log to audit_logs
      -> 6. Trigger entitlement generation/recalculation for affected employees when active
      -> Return Result.Success(policyDto)
```

## Get Active Policies

### Flow

```
GET /api/v1/time-off/policies?scope=...
  -> TimeOffPolicyController.List(query)
    -> [RequirePermission("time_off:manage")]
    -> TimeOffPolicyService.GetActivePoliciesAsync(query, ct)
      -> Query active policies by tenant, legal_entity_id from selected Company, assignment scope, country/statutory context, and effective date
      -> Include rule summaries and assignment summaries
      -> Return Result.Success(policyDtos)
```

### Key Rules

- Time Off Type defines the kind; Time Off Policy defines rules and assignment scope.
- Time Off Policy management is Company-context first; selected Company comes from the topbar, resolves to `legal_entity_id`, and is permission checked before create/update/list actions.
- Policy owns rule configuration for entitlement, accrual, proration, carry-forward, eligibility, supporting documents, notice period, and request limits.
- Assignment scope can include `legal_entity_default` shown as Company default in UI, department, position, or employee override inside the selected Company.
- Multi-select departments/positions are supported in docs when the product supports them.
- Entitlements are output from active policy assignment for a period.
- Effective dating preserves historical requests and balances.

## Related

- [[modules/time-off/time-off-policies/overview|Time Off Policies Overview]]
- [[modules/time-off/time-off-entitlements/overview|Time Off Entitlements]]
- [[modules/time-off/time-off-types/overview|Time Off Types]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
