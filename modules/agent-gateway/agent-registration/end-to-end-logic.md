# Agent Registration - End-to-End Logic

**Module:** Agent Gateway
**Feature:** Agent Registration

---

## Enroll New Windows Agent

### Flow

```
TrayApp Sign in
  -> Service generates/loads device_id
  -> POST /api/v1/agent/enroll/start
    -> AgentController.StartEnrollment(StartAgentEnrollmentCommand)
    -> Validation: device_id, device_name, os_version, agent_version required
    -> Create short-lived enrollment challenge
    -> Return auth_url + enrollment_id
  -> User authenticates through OneVo auth/SSO
  -> POST /api/v1/agent/enroll/complete
    -> AgentController.CompleteEnrollment(CompleteAgentEnrollmentCommand)
    -> Auth: validated user login + enrollment challenge
    -> Resolve tenant_id and employee_id from authenticated user
    -> Check registered_agents by tenant_id + device_id
       -> If exists and status = active -> update version/heartbeat/employee link
       -> If exists and status = revoked -> return 403 Forbidden
       -> If missing -> INSERT registered_agents
    -> End previous active agent_sessions row for device_id
    -> INSERT agent_sessions with is_active = true
    -> Build initial/effective agent_policies
    -> Generate internal device credential via ITokenService.GenerateDeviceTokenAsync()
       -> Claims: device_id, tenant_id, type = "agent"
    -> Publish AgentRegistered / AgentSessionStarted events
    -> Return Result.Success(new AgentEnrollmentDto { DeviceCredential, AgentId, Employee, Policy })
```

### Error Scenarios

| Error | Handling |
|:------|:---------|
| Enrollment challenge expired | Return 401; TrayApp restarts sign-in |
| User auth failed | Return 401; TrayApp shows sign-in failed |
| User has no employee record in tenant | Return 403; TrayApp shows contact admin |
| Device was revoked | Return 403 with revoked-device message |
| Duplicate active device_id | Update existing registration and refresh credential |
| Missing required device fields | Return 422 validation errors |

### Edge Cases

- Device credential is not a user JWT. It contains `device_id`, `tenant_id`, and `type: "agent"` only.
- The employee never enters API keys, tenant keys, tenant IDs, or server URLs.
- Employee-device binding is stored in `agent_sessions`; ingest validates against the active session.
- Monitoring does not start from enrollment alone. It starts only after policy fetch, consent gate, and Time & Attendance lifecycle allow collection.

## Related

- [[modules/agent-gateway/agent-registration/overview|Agent Registration Overview]]
- [[modules/agent-gateway/agent-server-protocol|Agent Server Protocol]]
- [[modules/agent-gateway/tray-app-ui|Tray App UI]]
- [[modules/agent-gateway/policy-distribution/overview|Policy Distribution]]
- [[modules/agent-gateway/heartbeat-monitoring/overview|Heartbeat Monitoring]]
- [[modules/agent-gateway/data-ingestion/overview|Data Ingestion]]
- [[modules/agent-gateway/monitoring-lifecycle/overview|Monitoring Lifecycle]]
- [[backend/messaging/event-catalog|Event Catalog]]
