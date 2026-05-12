# Data Ingestion — End-to-End Logic

**Module:** Agent Gateway
**Feature:** Data Ingestion

---

## Ingest Activity Data Batch

### Flow

```
POST /api/v1/agent/ingest
  -> AgentController.Ingest(IngestionPayload)
    -> Auth: Device JWT
       -> Resolve tenant_id, agent_id, device_id from JWT claims
       -> Never trust tenant_id from the JSON payload
    -> Return 202 Accepted immediately (async processing)
    -> DataIngestionService.IngestAsync(agentIdentity, payload, ct)
      -> 1. Minimal schema validation (structure check only)
         -> payload.device_id matches JWT device_id claim when present
         -> payload.employee_id matches active agent_sessions employee_id
         -> timestamp is within 24h window
         -> batch array is not empty
      -> 2. Batch INSERT entire payload into activity_raw_buffer
         -> Use COPY or unnest() for performance
         -> Store payload_json with server-resolved tenant_id, agent_id, device_id, employee_id,
            captured_at from payload, and received_at from server clock
      -> 3. Route different types to different modules:
         -> "activity_snapshot" -> stays in raw buffer for ProcessRawBufferJob
         -> "app_usage"        -> UPSERT observed_applications (tenant_id, process_name)
                                  increment employee_count, update last_seen_at, total_seconds
                                  auto-fill global_catalog_id if global_app_catalog has matching process_name
                                  then resolve is_allowed via app_allowlists using process_name as the
                                  authoritative key; application_name is display metadata only
                                  null match → is_allowed = null (pending, never triggers non_allowed_app rule)
         -> "device_session" -> workforce-presence raw processing
         -> "verification_photo" -> identity-verification pipeline
      -> 4. Rate limit check: 30 requests/min/device (Redis sliding window)
```

### Error Scenarios

| Error | Handling |
|:------|:---------|
| Rate limit exceeded | Return 429 Too Many Requests |
| Invalid JWT / expired | Return 401 |
| Payload too large (> 1MB) | Return 413 |
| Schema validation failure | Return 400 with error details |
| Raw buffer insert failure | Return 500, agent retries with exponential backoff |

### Edge Cases

- **This is the ONLY ingestion endpoint for agent data.** All data flows through here.
- **Tenant isolation comes from Device JWT.** Agents do not submit trusted tenant identity in the payload.
- **Application identity uses `process_name`.** Display names can change and are not authoritative for allowlist decisions.
- **Detailed validation is deferred** to `ProcessRawBufferJob` — ingestion does minimal checks for throughput.
- **Agent retries:** Agent has built-in retry with exponential backoff (1s, 2s, 4s, 8s, max 30s).
- **Volume:** ~240 snapshots/employee/day. 500 employees = 120,000 raw buffer rows/day.

## Related

- [[modules/agent-gateway/data-ingestion/overview|Data Ingestion Overview]]
- [[modules/agent-gateway/agent-registration/overview|Agent Registration]]
- [[modules/agent-gateway/heartbeat-monitoring/overview|Heartbeat Monitoring]]
- [[modules/agent-gateway/policy-distribution/overview|Policy Distribution]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
