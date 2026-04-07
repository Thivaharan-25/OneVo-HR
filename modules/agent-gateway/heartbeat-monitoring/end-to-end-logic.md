# Heartbeat Monitoring — End-to-End Logic

**Module:** Agent Gateway
**Feature:** Heartbeat Monitoring

---

## Send Heartbeat

### Flow

```
POST /api/v1/agent/heartbeat
  -> AgentController.Heartbeat(HeartbeatPayload)
    -> Auth: Device JWT
    -> AgentHeartbeatService.ProcessHeartbeatAsync(deviceId, payload, ct)
      -> 1. UPDATE registered_agents SET last_heartbeat_at = now WHERE device_id = @id
      -> 2. INSERT into agent_health_logs
         -> cpu_usage, memory_mb, errors_json, tamper_detected
      -> 3. If tamper_detected = true:
         -> Publish AgentTamperDetected event
         -> Log critical warning
      -> Return 200 OK
```

## Detect Offline Agents

### Flow

```
DetectOfflineAgentsJob (Hangfire, every 5 min)
  -> AgentHealthService.DetectOfflineAsync(ct)
    -> 1. Query registered_agents WHERE status = 'active'
       AND last_heartbeat_at < now - interval '5 minutes'
    -> 2. For each offline agent:
       -> Check if AgentHeartbeatLost already published (dedup)
       -> Publish AgentHeartbeatLost event
       -> Event consumers: exception-engine flags offline agent, notifications alert admin
    -> 3. Log count of newly offline agents
```

### Error Scenarios

| Error | Handling |
|:------|:---------|
| Device JWT expired | Agent must re-register |
| Unknown device_id in JWT | Return 401 |
| Health log insert failure | Log error, heartbeat still succeeds (health logs are non-critical) |

### Edge Cases

- **Agents behind flaky networks:** May temporarily appear offline. A 5-minute threshold prevents false positives.
- **Heartbeat interval:** Agents send every 60 seconds. 5 missed heartbeats = offline.

## Related

- [[agent-gateway|Agent Gateway Module]]
- [[heartbeat-monitoring/overview|Heartbeat Monitoring Overview]]
- [[agent-registration/end-to-end-logic|Agent Registration — End-to-End Logic]]
- [[policy-distribution/end-to-end-logic|Policy Distribution — End-to-End Logic]]
- [[event-catalog]]
- [[error-handling]]
- [[auth-architecture]]
- [[multi-tenancy]]
- [[WEEK1-shared-platform]]
