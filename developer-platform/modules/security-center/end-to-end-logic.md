# Security Center — End-to-End Logic

## Purpose

Security Center is the single screen where platform security team members review active alerts, investigate suspicious activity, revoke sessions, and take security actions. It is read-heavy — most actions are targeted responses to alerts that were raised by the detection pathways documented in [[developer-platform/modules/dashboard/end-to-end-logic|Dashboard End-to-End Logic]].

**Route:** `/security/security-center`
**Permission:** `platform.security.read`

---

## Screen Layout

Left tab navigation:
- Overview (default)
- Alerts
- Sessions
- Suspicious Activity

---

## Overview Tab

### Security KPI Cards (5 cards in a row)

| Card | Metric | Definition | Color |
|---|---|---|---|
| Active Critical Alerts | Count of unresolved `severity = 'critical'` alerts | `COUNT(*) FROM platform_alerts WHERE severity = 'critical' AND resolved_at IS NULL` | Red if > 0, green if 0 |
| Active Warning Alerts | Count of unresolved `severity = 'warning'` alerts | Same with warning | Orange if > 0, green if 0 |
| Active Sessions | Count of valid (non-expired) platform admin sessions | `COUNT(*) FROM dev_platform_sessions WHERE expires_at > NOW()` | Neutral |
| Tenant Sessions Revoked Today | Count of tenant user session invalidations in last 24h | From audit log | Neutral |
| Security Events (24h) | Security-category audit events in last 24h | Filtered from audit log | Neutral |

### Recent Critical Alerts (5 rows)

Top 5 most recent unresolved Critical alerts. Each row:
- Severity icon (red ⊗)
- Alert title
- Tenant name (or "Platform" for platform-level)
- Time since creation, e.g. "2 hours ago"
- "Acknowledge" button (inline)

"View All Alerts" → navigates to Alerts tab.

### Platform Admin Sessions (3 rows)

Most recent 3 active platform admin sessions:
- Account name + email
- IP address
- Login time
- "Revoke" button (inline)

"View All Sessions" → navigates to Sessions tab.

---

## Alerts Tab

### Filter Bar

| Filter | Type | Options |
|---|---|---|
| Search | Text | Alert title or alert code |
| Severity | Dropdown | All / Critical / Warning / Info |
| Status | Dropdown | Active (unresolved) / Acknowledged / Resolved / Auto-Resolved / Auto-Dismissed |
| Tenant | Autocomplete | All tenants + "Platform-level" for non-tenant alerts |
| Source Module | Dropdown | All + each module key |
| Alert Code | Text | Exact match on `alert_code` |
| Date Range | Date picker | `created_at` from/to |

### Alerts Table

**API:** `GET /admin/v1/security/alerts?{filters}&page={n}&per_page={n}&sort={field}&order={asc|desc}`

| Column | Description | Sortable |
|---|---|---|
| Severity | Red ⊗ Critical / Orange △ Warning / Blue ℹ Info icon | Yes |
| Alert Title | Human-readable summary | No |
| Alert Code | Machine-readable code, e.g. `auth.brute_force_detected` | Yes |
| Tenant | Company name (linked) or "Platform" | Yes |
| Source Module | Module badge | Yes |
| Detail | First 100 chars of `platform_alerts.detail` — expand on click | No |
| Created | Relative time + absolute on hover | Yes, default DESC |
| Status | Active (red) / Acknowledged (yellow) / Resolved (green) / Auto-Resolved (gray) / Auto-Dismissed (gray) | Yes |
| Actions | Acknowledge / Resolve / View Detail |

### Alert Detail Side Panel

Clicking any alert row opens a side panel with:

| Section | Contents |
|---|---|
| Header | Severity icon, title, alert code, created timestamp |
| Tenant | Company name linked to tenant detail; or "Platform-level" |
| Source Module | Module key + display name |
| Full Detail | Complete `platform_alerts.detail` text — IP addresses, user counts, thresholds, raw provider messages |
| Status Timeline | Created at → Acknowledged at (who) → Resolved at (who) + reason |
| Related Audit Events | Last 5 audit log entries with matching `tenant_id` and similar `action` category within ±30 minutes |
| Actions | Acknowledge, Resolve (with reason field), Escalate (creates a follow-up task in current-focus) |

---

## Acknowledge Alert — Full Flow

Acknowledging marks that a platform admin has seen the alert and is investigating. It does NOT resolve the alert.

**Trigger:** "Acknowledge" button on alert row or detail panel.

**No confirmation dialog** for acknowledgement — it is a lightweight action.

**API:** `POST /admin/v1/security/alerts/{alertId}/acknowledge`

```json
{}
```

**Response (200 OK):**
```json
{
  "alert_id": "...",
  "acknowledged_at": "2026-05-17T10:30:00Z",
  "acknowledged_by": "engineer@onevo.io"
}
```

**State written:**
- `platform_alerts.acknowledged_at` = now()
- `platform_alerts.acknowledged_by_id` = current platform account
- Audit log: `action = 'alert.acknowledged'`

**UI effect:** Status badge changes from Active (red) to Acknowledged (yellow). Alert remains in the Active filter view — acknowledged alerts are still active, they have just been seen.

---

## Resolve Alert — Full Flow

Resolving closes the alert. Critical alerts require a written reason of minimum 20 characters. Warning and Info alerts can be resolved without a reason.

**Trigger:** "Resolve" button on alert row or detail panel.

### Confirmation Dialog

| Element | Value |
|---|---|
| Title | "Resolve Alert" |
| Alert shown | Title + code |
| Severity shown | Critical / Warning / Info badge |

**Fields in dialog:**

| Field | Label | Type | Required | Validation | Notes |
|---|---|---|---|---|---|
| Resolution Note | "Resolution Note" | Textarea | Yes for Critical, No for Warning/Info | Min 20 chars for Critical | Describe what was investigated and what action was taken |
| Resolution Type | "Resolution Type" | Dropdown | Yes | | See resolution types below |

**Resolution types:**

| Value | Label | When to Use |
|---|---|---|
| `false_positive` | "False Positive" | Alert fired but no real security issue existed |
| `issue_resolved` | "Issue Resolved" | Real issue identified and fixed |
| `accepted_risk` | "Accepted Risk" | Issue acknowledged, risk accepted, no further action |
| `escalated_externally` | "Escalated Externally" | Handed off to external team or authority |
| `no_action_required` | "No Action Required" | Alert was informational; no response needed |

**API:** `POST /admin/v1/security/alerts/{alertId}/resolve`

```json
{
  "resolution_type": "issue_resolved",
  "resolution_note": "Confirmed brute force attempt from IP 82.45.12.99. IP blocked at WAF level. No successful logins from that IP. Auth team notified. Tenant advised to reset admin password as precaution."
}
```

**Response (200 OK):**
```json
{
  "alert_id": "...",
  "resolved_at": "2026-05-17T11:00:00Z",
  "resolved_by": "engineer@onevo.io",
  "resolution_type": "issue_resolved"
}
```

**State written:**
- `platform_alerts.resolved_at` = now()
- `platform_alerts.resolved_by_id` = current platform account
- `platform_alerts.resolved_reason` = resolution_note
- `platform_alerts.auto_resolved` = false
- Audit log: `action = 'alert.resolved'`, resolution_type, resolution_note (truncated to 200 chars in audit)

**UI effect:** Alert moves from Active to Resolved. No longer appears in Active filter. Visible in Resolved filter.

---

## Sessions Tab

Shows all active platform admin sessions. Operators use this to review who is currently logged in to the developer console and to revoke suspicious or stale sessions.

### Filter Bar

| Filter | Options |
|---|---|
| Search | Account name or email |
| Status | Active / Expired / Revoked |
| Date Range | Created from/to |

### Sessions Table

**API:** `GET /admin/v1/security/sessions?{filters}&page={n}&per_page={n}`

| Column | Description |
|---|---|
| Account | Platform admin name + email |
| IP Address | Source IP — `(current)` badge if it matches the operator's own IP |
| Created | Login timestamp |
| Expires | When session JWT expires — red if within 5 minutes |
| Status | Active (green) / Expired (gray) / Revoked (red) |
| Actions | Revoke (active sessions only) |

**Self-session:** The operator's own active session is highlighted with a `(you)` badge. Revoking your own session logs you out immediately.

### Revoke Session — Full Flow

**Trigger:** "Revoke" button on a session row.

**Confirmation dialog:**

```
Revoke session for sarah@onevo.io?

IP: 185.12.44.99
Logged in: 2026-05-17 09:15 AM
Expires: 2026-05-17 09:45 AM

This will immediately invalidate their session. They will be logged out of the developer console.
```

**API:** `POST /admin/v1/security/sessions/{sessionId}/revoke`

```json
{
  "reason": "Suspicious concurrent login from unexpected IP while account holder is on leave."
}
```

**Response (200 OK):**
```json
{
  "session_id": "...",
  "revoked_at": "2026-05-17T10:00:00Z",
  "revoked_by": "engineer@onevo.io"
}
```

**State written:**
- `dev_platform_sessions` row: `revoked_at` = now()
- JWT blocklist entry added (or session lookup now returns revoked — implementation-specific)
- Audit log: `action = 'session.revoked'`, actor, target_account_id, source_ip, reason

**Self-revoke:** If operator revokes their own session, they are redirected to the login screen immediately after the API call responds.

### Revoke All Sessions for an Account

Available from Platform Access → Account Detail → "Revoke All Active Sessions" action.

**API:** `POST /admin/v1/platform-accounts/{accountId}/sessions/revoke-all`

Revokes every non-expired session for the account. Used when an account is suspected compromised or when deactivating an account.

---

## Suspicious Activity Tab

Shows tenant-level security events that don't necessarily reach Critical alert threshold but warrant monitoring.

### Filter Bar

| Filter | Options |
|---|---|
| Tenant | Autocomplete |
| Activity Type | All / Failed Logins / Identity Verification Failures / Unusual Access Patterns / Agent Tampering |
| Date Range | From/to |
| Severity | Any / Warning / Info |

### Suspicious Activity Table

**API:** `GET /admin/v1/security/suspicious-activity?{filters}`

| Column | Description |
|---|---|
| Time | Event timestamp |
| Activity Type | Category label |
| Tenant | Company name — linked |
| Description | What happened — e.g. "5 failed logins from IP 192.168.1.1 in 10 minutes" |
| Affected User | Username + email if tenant-user-specific |
| Severity | Warning / Info badge |
| Actions | View in Audit Log (navigates to Audit Console filtered to this event) |

**Data source:** Audit log events with `action_category = 'security'` that have not been escalated to a `platform_alerts` row (i.e., they fell below the alert threshold).

---

## APIs — Full Catalog

| Method | Route | Purpose | Permission |
|---|---|---|---|
| GET | `/admin/v1/security/overview` | Security KPI summary | `platform.security.read` |
| GET | `/admin/v1/security/alerts` | Alert list with filters | `platform.security.read` |
| GET | `/admin/v1/security/alerts/{id}` | Alert detail | `platform.security.read` |
| POST | `/admin/v1/security/alerts/{id}/acknowledge` | Acknowledge alert | `platform.security.manage` |
| POST | `/admin/v1/security/alerts/{id}/resolve` | Resolve alert with note | `platform.security.manage` |
| GET | `/admin/v1/security/sessions` | Platform admin session list | `platform.security.read` |
| POST | `/admin/v1/security/sessions/{id}/revoke` | Revoke a platform admin session | `platform.security.manage` |
| POST | `/admin/v1/platform-accounts/{id}/sessions/revoke-all` | Revoke all sessions for an account | `platform.accounts.manage` |
| GET | `/admin/v1/security/suspicious-activity` | Below-threshold security events | `platform.security.read` |

---

## Error Taxonomy

| HTTP | Code | Condition |
|---|---|---|
| 404 | `alert_not_found` | Alert ID does not exist |
| 409 | `alert_already_resolved` | Attempt to resolve an already-resolved alert |
| 409 | `session_already_revoked` | Session already revoked or expired |
| 422 | `resolution_note_required` | Critical alert resolution without a note |
| 422 | `resolution_note_too_short` | Note below 20 characters for Critical |
| 403 | `permission_denied` | `platform.security.manage` required for write operations |

---

## Security Principles

- Every read of the security center is itself audit-logged with the operator's identity (reading sensitive data is a security event)
- Token hashes stored in `dev_platform_sessions` are never returned by any API — only session metadata
- Alert resolution notes are stored in plaintext — operators must not include credentials or secrets in resolution notes (UI warning shown)
- The security center cannot suppress or delete alerts — only acknowledge and resolve. The audit trail of every alert from creation to resolution is permanent.
