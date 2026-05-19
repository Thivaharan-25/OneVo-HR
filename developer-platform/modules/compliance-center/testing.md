# Compliance Center — Testing

## Test Fixtures Required

- Platform account with `platform.compliance.manage`
- Platform account with `platform.compliance.read` only
- 1 active tenant with audit data spanning 2 years
- At least 1 active legal hold in `legal_holds`
- Retention policy seeded with default retention periods

---

## Legal Holds

### TC-CC-001: Legal hold blocks data deletion for target tenant
**Setup:** Tenant T has active legal hold covering all data categories
**Action:** Data retention sweep job runs
**Expected:** No data deleted for tenant T — legal hold protection check skips tenant T in deletion queries. All other tenants processed normally.

### TC-CC-002: Legal hold create requires manage permission
**Setup:** Account with `platform.compliance.read` only
**Action:** `POST /admin/v1/legal-holds`
**Expected:** HTTP 403

### TC-CC-003: Legal hold create — happy path
**Action:** `POST /admin/v1/legal-holds`
```json
{
  "tenant_id": "<tenant_id>",
  "reason": "Pending litigation — DO NOT DELETE",
  "scope": "all",
  "expires_at": null
}
```
**Expected:**
- HTTP 201
- `legal_holds` row created: `is_active = true`
- Audit log: `action = 'legal_hold.created'`, actor, reason

### TC-CC-004: Releasing legal hold restores normal retention processing
**Setup:** Legal hold active for tenant T
**Action:** `PATCH /admin/v1/legal-holds/{id}` `{"is_active": false, "release_reason": "Litigation settled"}`
**Expected:**
- `legal_holds.is_active = false`, `released_at` set
- Next retention sweep includes tenant T
- Audit log: `action = 'legal_hold.released'`

---

## Compliance Export

### TC-CC-005: Export request requires scope and reason
**Action:** `POST /admin/v1/compliance/exports` without `scope` or `reason`
**Expected:** HTTP 422 — both fields required for compliance exports

### TC-CC-006: Compliance export access link expires
**Setup:** Completed compliance export with `download_expires_at` in the past
**Action:** Attempt to access the download URL
**Expected:** HTTP 410 Gone — link expired; re-request required

### TC-CC-007: All compliance actions are audit-logged
**Action:** Any write action (create legal hold, release hold, request export)
**Expected:** `audit_log` entry for each action with actor, target tenant, action details, reason
