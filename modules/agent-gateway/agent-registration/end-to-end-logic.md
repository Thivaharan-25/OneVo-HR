# Agent Registration — End-to-End Logic

**Module:** Agent Gateway
**Feature:** Agent Registration

---

## Register New Agent

### Flow

```
POST /api/v1/agent/register
  -> AgentController.Register(RegisterAgentCommand)
    -> Auth: Tenant API key (not user JWT, not device JWT)
    -> Validation: device_id, device_name, os_version, agent_version required
    -> AgentRegistrationService.RegisterAsync(command, ct)
      -> 1. Check if device_id already registered for this tenant
         -> If exists and status = 'active' -> return existing agent with refreshed JWT
         -> If exists and status = 'revoked' -> return 403 Forbidden
      -> 2. INSERT into registered_agents
         -> employee_id = null (set at employee login)
         -> status = 'active'
         -> last_heartbeat_at = now
      -> 3. Create initial agent_policies with tenant defaults
         -> IConfigurationService.GetMonitoringTogglesAsync(tenantId)
         -> Serialize to policy_json
      -> 4. Generate device JWT via ITokenService.GenerateDeviceTokenAsync()
         -> Claims: device_id, tenant_id, type = "agent"
      -> 5. Publish AgentRegistered event
      -> Return Result.Success(new AgentRegistrationDto { DeviceJwt, AgentId, Policy })
```

### Error Scenarios

| Error | Handling |
|:------|:---------|
| Invalid tenant API key | Return 401 |
| Revoked device re-registering | Return 403 with message |
| Duplicate device_id (active) | Return existing agent with new JWT |
| Missing required fields | Return 422 validation errors |

### Edge Cases

- **Device JWT is NOT a user JWT** — it contains `device_id` + `tenant_id` + `type: "agent"` claim. No user permissions.
- **Employee linking happens separately** at `/api/v1/agent/login` when employee logs into MAUI tray app.

## Related

- [[modules/agent-gateway/agent-registration/overview|Agent Registration Overview]]
- [[modules/agent-gateway/policy-distribution/overview|Policy Distribution]]
- [[modules/agent-gateway/heartbeat-monitoring/overview|Heartbeat Monitoring]]
- [[modules/agent-gateway/data-ingestion/overview|Data Ingestion]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
