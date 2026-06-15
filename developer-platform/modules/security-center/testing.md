# Security Center — Testing

## Test Fixtures Required

- Platform account with `platform.security.manage` (full security access)
- Platform account with `platform.security.read` only
- At least 2 `platform_alerts` rows: one Critical (unresolved), one Warning (unresolved)
- At least 2 active `platform_user_sessions` rows (for session revoke tests)
- `audit_log` table seeded with security-category events

---

## Alert Acknowledge

### TC-SC-001: Acknowledge sets acknowledged_at and actor
**Setup:** Unresolved Critical alert (`acknowledged_at = null`)
**Action:** `POST /admin/v1/security/alerts/{alertId}/acknowledge`
**Expected:**
- HTTP 200
- `platform_alerts.acknowledged_at` = now()
- `platform_alerts.acknowledged_by_id` = current platform account ID
- Alert status badge changes from Active to Acknowledged in response
- Audit log: `action = 'alert.acknowledged'`

### TC-SC-002: Acknowledge does NOT resolve the alert
**Setup:** Active Critical alert
**Action:** `POST /admin/v1/security/alerts/{alertId}/acknowledge`
**Expected:**
- `platform_alerts.resolved_at` remains null
- Alert still appears in Active filter (acknowledged alerts are still active)
- `platform_alerts.auto_resolved` remains false

### TC-SC-003: Acknowledge requires security.manage permission
**Setup:** Account with `platform.security.read` only
**Action:** `POST /admin/v1/security/alerts/{alertId}/acknowledge`
**Expected:** HTTP 403

---

## Alert Resolve

### TC-SC-004: Resolve Critical alert — resolution note required (min 20 chars)
**Action:** `POST /admin/v1/security/alerts/{criticalAlertId}/resolve` `{"resolution_type": "issue_resolved", "resolution_note": "Fixed"}`
**Expected:** HTTP 422 — note is only 5 chars; minimum 20 required for Critical severity

### TC-SC-005: Resolve Critical alert — happy path
**Action:** `POST /admin/v1/security/alerts/{criticalAlertId}/resolve`
```json
{
  "resolution_type": "issue_resolved",
  "resolution_note": "Brute force from IP 82.45.12.99. IP blocked at WAF. No successful logins detected."
}
```
**Expected:**
- HTTP 200
- `platform_alerts.resolved_at` = now()
- `platform_alerts.resolved_by_id` = current account
- `platform_alerts.resolved_reason` = the note text
- `platform_alerts.auto_resolved = false`
- Alert appears in Resolved filter; removed from Active filter
- Audit log: `action = 'alert.resolved'`, `resolution_type: "issue_resolved"`

### TC-SC-006: Resolve Warning alert — no note required
**Action:** `POST /admin/v1/security/alerts/{warningAlertId}/resolve` `{"resolution_type": "no_action_required"}`
**Expected:** HTTP 200 — resolution_note is optional for Warning

### TC-SC-007: Cannot resolve an already-resolved alert
**Setup:** Alert already has `resolved_at` set
**Action:** `POST /admin/v1/security/alerts/{alertId}/resolve`
**Expected:** HTTP 409, `code: "alert_already_resolved"`

### TC-SC-008: Auto-resolved alerts appear in Resolved filter with auto_resolved = true
**Setup:** `infra.service_degraded` warning alert that was auto-resolved by health check job
**Action:** `GET /admin/v1/security/alerts?status=resolved`
**Expected:**
- Alert appears in results
- `auto_resolved = true`
- `resolved_by_id = null` (system, not a platform admin)
- `resolved_reason = 'condition_cleared'`

---

## Session Revoke

### TC-SC-009: Revoke another account's session
**Setup:** Two active sessions: operator's own and another admin's
**Action:** `POST /admin/v1/security/sessions/{otherSessionId}/revoke` `{"reason": "Suspicious concurrent login"}`
**Expected:**
- HTTP 200
- `platform_user_sessions.revoked_at` set for the target session
- Target admin's next API call is rejected with 401
- Operator's own session is unaffected
- Audit log: `action = 'session.revoked'`, `actor_id` = operator, `target_account_id` set, `reason` stored

### TC-SC-010: Revoke own session logs out immediately
**Setup:** Operator revokes their own active session
**Action:** `POST /admin/v1/security/sessions/{ownSessionId}/revoke`
**Expected:**
- HTTP 200
- `platform_user_sessions.revoked_at` set
- Operator's next API call using this session returns 401
- Frontend should redirect to login screen

### TC-SC-011: Cannot revoke already-revoked session
**Setup:** Session with `revoked_at` already set
**Action:** `POST /admin/v1/security/sessions/{sessionId}/revoke`
**Expected:** HTTP 409, `code: "session_already_revoked"`

### TC-SC-012: Revoke all sessions for a platform user
**Setup:** Platform user with 3 active sessions
**Action:** `POST /admin/v1/platform-users/{userId}/sessions/revoke-all`
**Expected:**
- All 3 sessions get `revoked_at` set
- Platform user cannot make any API call with those sessions
- Single audit log entry recording all revoked sessions

---

## Security Overview and Data Protection

### TC-SC-013: Security overview KPI counts are accurate
**Setup:** 3 critical unresolved, 5 warning unresolved, 2 info unresolved alerts. 4 active sessions.
**Action:** `GET /admin/v1/security/overview`
**Expected:**
- `critical_alert_count: 3`
- `warning_alert_count: 5`
- `active_session_count: 4`

### TC-SC-014: Token hashes are never returned in session responses
**Action:** `GET /admin/v1/security/sessions`
**Expected:** Response contains `id`, `account_name`, `ip_address`, `created_at`, `expires_at`, `status` — NO `token_hash` or any raw token value

### TC-SC-015: Accessing the Security Center is itself audit-logged
**Action:** `GET /admin/v1/security/overview` (any security read)
**Expected:** `audit_log` entry: `action = 'security_center.accessed'`, actor, timestamp — reading sensitive data creates an audit record

### TC-SC-016: Suspicious activity returns security events below alert threshold
**Setup:** 5 failed logins from same tenant in 1 hour (below brute-force threshold of 10 in 5 min). No `platform_alerts` row created.
**Action:** `GET /admin/v1/security/suspicious-activity?tenant_id={id}`
**Expected:** Event appears in suspicious activity list with activity_type `failed_logins`, count, IP, timestamp — even though no alert was raised

### TC-SC-017: Security center read requires platform.security.read
**Setup:** Platform account with no permissions
**Action:** `GET /admin/v1/security/overview`
**Expected:** HTTP 403
