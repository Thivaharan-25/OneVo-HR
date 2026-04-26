# GDPR Consent

**Module:** Auth & Security
**Feature:** GDPR Consent

---

## Purpose

Tracks employee consent for data processing, biometric, monitoring, and marketing activities. Monitoring consent (`consent_type: "monitoring"`) must be recorded before monitoring features activate.

## Database Tables

### `gdpr_consent_records`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `user_id` | `uuid` | FK → users |
| `consent_type` | `varchar(50)` | `data_processing`, `biometric`, `monitoring`, `marketing` |
| `consented` | `boolean` | |
| `consented_at` | `timestamptz` | |
| `ip_address` | `varchar(45)` | |

## Key Business Rules

1. **Monitoring consent is a hard gate on ingest.** The `POST /api/v1/agent/ingest` endpoint checks `gdpr_consent_records` for the employee before processing any batch. If no active `monitoring` consent record exists (`consented = true`), the endpoint returns `403 Forbidden` with `detail: "Monitoring consent not recorded for this employee"`. The agent must surface this in the tray app and halt data collection. Consent is recorded by the employee accepting the monitoring disclosure during onboarding or via the tray app consent dialog.
2. Biometric consent is mandatory before fingerprint enrollment (GDPR/PDPA).

### Consent Gate — Ingest Flow

```
POST /api/v1/agent/ingest
  ↓
1. Validate Device JWT (agent auth)
2. Validate employee_id against agent_sessions (device binding)
3. CHECK gdpr_consent_records WHERE user_id = employee.user_id
         AND consent_type = 'monitoring' AND consented = true
   → not found → 403 "Monitoring consent not recorded for this employee"
4. Validate payload bounds (see agent-server-protocol.md)
5. Queue batch for async processing → 202 Accepted
```

**Caching:** The consent check result may be cached in Redis for up to 5 minutes per `employee_id` to avoid a DB hit on every ingest. Cache must be invalidated immediately when consent is withdrawn.

## Related

- [[modules/auth/overview|Auth Module]]
- [[frontend/cross-cutting/authentication|Authentication]]
- [[frontend/cross-cutting/authorization|Authorization]]
- [[modules/auth/audit-logging/overview|Audit Logging]]
- [[modules/auth/session-management/overview|Session Management]]
- [[modules/auth/mfa/overview|MFA]]
- [[security/auth-architecture|Auth Architecture]]
- [[security/compliance|Compliance]]
- [[security/data-classification|Data Classification]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[current-focus/DEV2-auth-security|DEV2: Auth Security]]
