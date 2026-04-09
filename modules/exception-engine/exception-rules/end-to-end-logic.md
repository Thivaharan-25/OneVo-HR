# Exception Rules — End-to-End Logic

**Module:** Exception Engine
**Feature:** Exception Rules

---

## Create Exception Rule

### Flow

```
POST /api/v1/exceptions/rules
  -> ExceptionRuleController.Create(CreateRuleCommand)
    -> [RequirePermission("exceptions:manage")]
    -> ExceptionRuleService.CreateAsync(command, ct)
      -> 1. Validate rule_type: low_activity, excess_idle, unusual_pattern, excess_meeting, no_presence, break_exceeded, verification_failed
      -> 2. Validate threshold_json against schema for rule_type
         -> e.g., low_activity requires: idle_percent_max, window_minutes, consecutive_snapshots
      -> 3. Validate applies_to + applies_to_id:
         -> 'all': applies_to_id must be null
         -> 'department': validate department exists
         -> 'team': validate team exists
         -> 'employee': validate employee exists
      -> 4. INSERT into exception_rules
      -> Return Result.Success(ruleDto)
```

### Error Scenarios

| Error | Handling |
|:------|:---------|
| Invalid rule_type | Return 422 |
| Invalid threshold_json for rule_type | Return 422 with schema validation errors |
| applies_to target not found | Return 404 |

## Related

- [[frontend/architecture/overview|Exception Rules Overview]]
- [[frontend/architecture/overview|Evaluation Engine]]
- [[frontend/architecture/overview|Alert Generation]]
- [[backend/messaging/error-handling|Error Handling]]
- [[backend/shared-kernel|Shared Kernel]]
- [[current-focus/DEV2-exception-engine|DEV2: Exception Engine]]
