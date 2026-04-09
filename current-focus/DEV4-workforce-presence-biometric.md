# Task: Workforce Presence — Biometric + Agent Integration

**Assignee:** Dev 4
**Module:** WorkforcePresence + IdentityVerification (biometric tables only)
**Priority:** Critical
**Dependencies:** [[current-focus/DEV4-shared-platform-agent-gateway|DEV4 Shared Platform Agent Gateway]] (agent gateway, workflow engine), [[current-focus/DEV2-auth-security|DEV2 Auth Security]] (HMAC webhook auth), [[current-focus/DEV3-workforce-presence-setup|DEV3 Workforce Presence Setup]] (presence session schema)

---

## Step 1: Backend

### Acceptance Criteria

#### Biometric Integration
- [ ] `biometric_devices` table + CRUD (from identity verification module)
- [ ] `biometric_enrollments` table — employee fingerprint enrollment with consent tracking
- [ ] `biometric_events` table — raw clock-in/out events from terminals
- [ ] `biometric_audit_logs` table — tamper detection, device health
- [ ] `POST /api/v1/biometric/webhook` — HMAC-SHA256 signature verification
- [ ] Biometric events flow: webhook -> `biometric_events` -> `attendance_records` -> `presence_sessions` (via reconciliation)

#### Attendance Operations
- [ ] `attendance_records` table — clock-in/out records (biometric source)
- [ ] `overtime_requests` table + request/approve workflow via workflow engine
- [ ] `attendance_corrections` table — manager corrections to attendance data
- [ ] Overtime auto-flagging: `total_present_minutes > scheduled_minutes`

#### Agent Data Integration
- [ ] Agent device session data (from agent gateway `/ingest`) -> `device_sessions` table
- [ ] Agent data merged into `presence_sessions` by reconciliation job
- [ ] Source tracking: `biometric`, `agent`, `manual`, `mixed`
- [ ] Deduplication: earliest first_seen + latest last_seen from all sources

#### Domain Events
- [ ] `PresenceSessionStarted` -> notifications
- [ ] `PresenceSessionEnded` -> activity monitoring
- [ ] `BreakExceeded` -> exception engine
- [ ] `OvertimeRequested` -> notifications

### Backend References

- [[modules/workforce-presence/overview|workforce-presence]] — module architecture
- [[modules/identity-verification/overview|identity-verification]] — biometric tables shared with identity verification module
- [[modules/agent-gateway/overview|agent-gateway]] — agent data ingestion pipeline
- [[backend/notification-system|Notification System]] — event notifications
- [[infrastructure/multi-tenancy|Multi Tenancy]] — tenant-scoped biometric and attendance data

---

## Step 2: Frontend

### Pages to Build

```
# Biometric + attendance pages live under workforce/presence/ (colocated with DEV3 presence setup)
# Components are shared in workforce/presence/components/

app/(dashboard)/workforce/presence/
├── attendance/page.tsx           # Attendance records + corrections (AttendanceTable)
├── overtime/page.tsx             # Overtime requests + approvals (OvertimeTable)
├── components/                   # Adds to DEV3's colocated components
│   └── BiometricDeviceCard.tsx   # Device status + enrollment card
```

### What to Build

- [ ] Biometric device management (BiometricDeviceCard):
  - DataTable: device name, type, location, status (online/offline), last event
  - Device registration form (name, type, API key, location)
  - Device health status with alert for offline devices
- [ ] Employee enrollment management:
  - List enrolled employees per device
  - Enrollment flow: select employee, capture biometric, store consent
- [ ] Attendance records page (AttendanceTable — shared with DEV3):
  - DataTable: employee, date, check-in, check-out, source (biometric/agent/manual/mixed), total hours
  - Filter by date range, department, source
- [ ] Attendance correction dialog:
  - Manager selects employee + date
  - Modify check-in/check-out times with reason
  - Audit trail of corrections
- [ ] Overtime management page (OvertimeTable — shared with DEV3):
  - Pending requests list (for manager approval)
  - Request detail: employee, date, scheduled hours, actual hours, overtime hours
  - Approve/reject with comments
  - Auto-flagged overtime list
- [ ] PermissionGate: `workforce:manage-biometric`, `workforce:correct-attendance`, `workforce:approve-overtime`

### Userflows

- [[Userflow/Workforce-Presence/biometric-device-setup|Biometric Device Setup]] — register and manage biometric devices
- [[Userflow/Workforce-Presence/attendance-correction|Attendance Correction]] — correct attendance records
- [[Userflow/Workforce-Presence/overtime-management|Overtime Management]] — request and approve overtime
- [[Userflow/Workforce-Presence/break-tracking|Break Tracking]] — break records from biometric + agent

### API Endpoints (Frontend Consumes)

| Method | Endpoint | Purpose |
|:-------|:---------|:--------|
| GET | `/api/v1/biometric/devices` | List biometric devices |
| POST | `/api/v1/biometric/devices` | Register device |
| GET | `/api/v1/biometric/devices/{id}` | Device detail |
| GET | `/api/v1/biometric/enrollments` | List enrollments |
| POST | `/api/v1/biometric/enrollments` | Enroll employee |
| GET | `/api/v1/attendance/records` | Attendance records (filtered) |
| POST | `/api/v1/attendance/corrections` | Submit correction |
| GET | `/api/v1/attendance/corrections` | List corrections |
| PUT | `/api/v1/attendance/corrections/{id}/approve` | Approve correction |
| GET | `/api/v1/overtime/requests` | List overtime requests |
| POST | `/api/v1/overtime/requests` | Submit overtime request |
| PUT | `/api/v1/overtime/requests/{id}/approve` | Approve overtime |
| PUT | `/api/v1/overtime/requests/{id}/reject` | Reject overtime |

### Frontend References

- [[frontend/design-system/components/component-catalog|Component Catalog]] — DataTable, StatusBadge, Dialog, Badge
- [[frontend/design-system/foundations/color-tokens|Color Tokens]] — device status colors
- [[frontend/data-layer/api-integration|API Integration]] — API client pattern

---

## Related Tasks

- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4 Shared Platform Agent Gateway]] — workflow engine for overtime approvals; agent data source
- [[current-focus/DEV2-auth-security|DEV2 Auth Security]] — HMAC-SHA256 webhook secret management
- [[current-focus/DEV3-workforce-presence-setup|DEV3 Workforce Presence Setup]] — presence_sessions and device_sessions tables
- [[current-focus/DEV4-identity-verification|DEV4 Identity Verification]] — biometric_devices table shared
- [[current-focus/DEV2-exception-engine|DEV2 Exception Engine]] — consumes BreakExceeded events
- Payroll — deferred to Phase 2 (approved overtime_requests consumed by payroll)
