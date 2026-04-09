# Policy Distribution — End-to-End Logic

**Module:** Agent Gateway
**Feature:** Policy Distribution

---

## Get Agent Policy

### Flow

```
GET /api/v1/agent/policy
  -> AgentController.GetPolicy()
    -> Auth: Device JWT (extracts device_id from claims)
    -> AgentPolicyService.GetPolicyAsync(deviceId, ct)
      -> 1. Load registered_agent by device_id
      -> 2. Get employee_id (may be null if not logged in)
      -> 3. Build effective policy:
         -> a. Get tenant toggles: IConfigurationService.GetMonitoringTogglesAsync(tenantId)
         -> b. If employee_id is set:
            -> Get employee overrides: IConfigurationService.GetEmployeeOverrideAsync(employeeId)
            -> Merge: override wins over tenant toggle for each feature
         -> c. Add interval settings from tenant_settings
      -> 4. UPDATE agent_policies SET policy_json = @effectivePolicy, last_synced_at = now
      -> Return Result.Success(policyDto)
```

### Policy Merge Logic

```csharp
// For each monitoring feature:
effectivePolicy.ActivityMonitoring = employeeOverride?.ActivityMonitoring ?? tenantToggles.ActivityMonitoring;
effectivePolicy.ScreenshotCapture = employeeOverride?.ScreenshotCapture ?? tenantToggles.ScreenshotCapture;
// ... same pattern for all 7 features
```

### Error Scenarios

| Error | Handling |
|:------|:---------|
| Agent not found | Return 401 (invalid device JWT) |
| Agent revoked | Return 401 with "agent_revoked" error code |
| No employee linked | Return policy with tenant defaults only |

### Edge Cases

- **Policy changes are pull-based** — agent polls `/policy` every 5 minutes. Changes are NOT pushed.
- **Employee logs out:** Policy reverts to tenant-only defaults (no employee overrides).

## Related

- [[modules/agent-gateway/overview|Agent Gateway Module]]
- [[frontend/architecture/overview|Policy Distribution Overview]]
- [[modules/agent-gateway/heartbeat-monitoring/end-to-end-logic|Heartbeat Monitoring — End-to-End Logic]]
- [[modules/agent-gateway/agent-registration/end-to-end-logic|Agent Registration — End-to-End Logic]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
- [[security/auth-architecture|Auth Architecture]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4: Shared Platform Agent Gateway]]
