# Device Management — Testing

> Phase 2 only. In Phase 1, verify these routes are hidden and unavailable rather than testing full device operations.

## Test Fixtures Required

- Platform account with `platform.health.manage`
- Platform account with `platform.health.read` only
- At least 2 active tenants each with registered devices in `devices` table
- At least 1 device with recent heartbeat (online), 1 with no heartbeat (offline)

---

### TC-DM-001: Device list read requires health.read
**Setup:** Account with no permissions
**Action:** `GET /admin/v1/operations/devices`
**Expected:** HTTP 403

### TC-DM-002: Tenant JWT rejected
**Action:** `GET /admin/v1/operations/devices` with tenant JWT
**Expected:** HTTP 401

### TC-DM-003: Device list returns cross-tenant metadata only — no activity payloads
**Action:** `GET /admin/v1/operations/devices`
**Expected:** Response contains: device_id, tenant name, hostname, OS, agent version, ring, status, last heartbeat. Does NOT contain: application usage logs, screenshot data, keylog counts, employee names tied to specific activity sessions, or any monitoring payload content.

### TC-DM-004: Unknown command type rejected
**Action:** `POST /admin/v1/operations/devices/{deviceId}/commands` `{"command_type": "DELETE_ALL_DATA"}`
**Expected:** HTTP 400 — `DELETE_ALL_DATA` is not a registered approved command. Only pre-approved command types are accepted (e.g., `UPDATE_AGENT`, `RESTART_SERVICE`, `COLLECT_DIAGNOSTIC`).

### TC-DM-005: Device command requires health.manage
**Setup:** Account with `platform.health.read` only
**Action:** `POST /admin/v1/operations/devices/{deviceId}/commands`
**Expected:** HTTP 403

### TC-DM-006: Device command writes full audit record
**Action:** `POST /admin/v1/operations/devices/{deviceId}/commands` `{"command_type": "COLLECT_DIAGNOSTIC", "reason": "Investigating connectivity issue reported by tenant."}`
**Expected:**
- Command queued in agent command table
- Audit log: `action = 'device_command.queued'`, `tenant_id`, `device_id`, `command_type`, `reason`, actor, timestamp

### TC-DM-007: Device list filters work correctly
**Action:** `GET /admin/v1/operations/devices?status=offline`
**Expected:** Only devices with no heartbeat in last 15 minutes returned. Online/idle devices excluded.

### TC-DM-008: Device detail does not leak cross-tenant data
**Setup:** Device belongs to tenant A
**Action:** `GET /admin/v1/operations/devices/{deviceId}` (device from tenant A)
**Expected:** Response contains only tenant A device metadata. No tenant B data included.
