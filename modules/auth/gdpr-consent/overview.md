# Legal & Privacy Acceptance

**Module:** Auth & Security
**Feature:** Legal & Privacy Acceptance

---

## Purpose

Tracks versioned legal/privacy decisions for Terms & Conditions, Privacy Notice, WorkPulse monitoring notices, screenshot notices, biometric/photo consent, and marketing consent.

Platform-required items block account activation or dashboard access when missing. Collection-required items block only the affected collection category.

## Database Tables

### `legal_acceptance_records`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `user_id` | `uuid` | FK -> users |
| `document_type` | `varchar(80)` | `terms`, `privacy_notice`, `activity_monitoring_notice`, `screenshot_notice`, `biometric_photo_consent`, `marketing` |
| `document_version` | `varchar(50)` | Version accepted/acknowledged |
| `decision` | `varchar(20)` | `accepted`, `acknowledged`, `declined` |
| `required` | `boolean` | Whether the item blocks access or collection |
| `decided_at` | `timestamptz` | |
| `ip_address` | `varchar(45)` | |
| `user_agent` | `varchar(500)` | |
| `source` | `varchar(30)` | `invite`, `web`, `desktop-agent` |

## Key Business Rules

1. **Platform-required items block platform access.** Missing Terms or Privacy Notice acknowledgement blocks account activation or dashboard access.
2. **Collection-required items gate only the affected category.** Missing WorkPulse activity monitoring, screenshot, or biometric/photo notice/consent disables that collector or verification path even if admin policy enables it.
3. Photo/biometric notice or consent is mandatory before WorkPulse photo/biometric verification or biometric enrollment starts.
4. Do not collapse all legal/privacy decisions into one flag. Store each document type and version separately.

### Legal & Privacy Gate - Ingest Flow

```text
POST /api/v1/agent/ingest
  ->
1. Validate Device JWT (agent auth)
2. Validate employee_id against agent_sessions (device binding)
3. Resolve the payload category and check legal_acceptance_records for the matching required document/version
   -> missing/declined -> 403 for that category only
4. Validate payload bounds (see agent-server-protocol.md)
5. Queue batch for async processing -> 202 Accepted
```

**Caching:** The Legal & Privacy gate result may be cached in Redis for up to 5 minutes per `employee_id` and category to avoid a DB hit on every ingest. Cache must be invalidated immediately when a relevant decision is recorded, changed, or withdrawn.

## Related

- [[modules/auth/overview|Auth Module]]
- [[Userflow/Auth-Access/gdpr-consent|Legal & Privacy Acceptance]]
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
