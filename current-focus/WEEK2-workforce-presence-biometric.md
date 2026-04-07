# WEEK2: Workforce Presence — Biometric + Agent Integration

**Status:** Planned
**Priority:** Critical
**Assignee:** Dev 4
**Sprint:** Week 2 (Apr 14-18)
**Module:** WorkforcePresence + IdentityVerification (biometric tables only)

## Description

Implement biometric device registration, employee enrollment, biometric event capture via HMAC-SHA256 webhooks, overtime requests/approvals, attendance corrections, and agent data integration into presence sessions.

## Acceptance Criteria

### Biometric Integration
- [ ] `biometric_devices` table + CRUD (from [[identity-verification]])
- [ ] `biometric_enrollments` table — employee fingerprint enrollment with consent tracking
- [ ] `biometric_events` table — raw clock-in/out events from terminals
- [ ] `biometric_audit_logs` table — tamper detection, device health
- [ ] `POST /api/v1/biometric/webhook` — HMAC-SHA256 signature verification
- [ ] Biometric events flow: webhook → `biometric_events` → `attendance_records` → `presence_sessions` (via reconciliation)

### Attendance Operations
- [ ] `attendance_records` table — clock-in/out records (biometric source)
- [ ] `overtime_requests` table + request/approve workflow via [[shared-platform]]
- [ ] `attendance_corrections` table — manager corrections to attendance data
- [ ] Overtime auto-flagging: `total_present_minutes > scheduled_minutes`

### Agent Data Integration
- [ ] Agent device session data (from [[agent-gateway]] `/ingest`) → `device_sessions` table
- [ ] Agent data merged into `presence_sessions` by reconciliation job
- [ ] Source tracking: `biometric`, `agent`, `manual`, `mixed`
- [ ] Deduplication: earliest first_seen + latest last_seen from all sources

### Domain Events
- [ ] `PresenceSessionStarted` → [[notifications]]
- [ ] `PresenceSessionEnded` → [[activity-monitoring]]
- [ ] `BreakExceeded` → [[exception-engine]]
- [ ] `OvertimeRequested` → [[notifications]]

## Related

- [[workforce-presence]] — module architecture
- [[identity-verification]] — biometric tables shared with identity verification module
- [[agent-gateway]] — agent data ingestion pipeline
- [[notification-system]] — event notifications
- [[multi-tenancy]] — tenant-scoped biometric and attendance data
- [[WEEK1-shared-platform]] — workflow engine for overtime approvals; agent gateway data source
- [[WEEK1-auth-security]] — HMAC-SHA256 webhook secret management
- [[WEEK2-workforce-presence-setup]] — presence_sessions and device_sessions tables defined here (same week)
- [[WEEK3-identity-verification]] — biometric_devices table originated here, referenced by identity verification
- [[WEEK4-exception-engine]] — consumes BreakExceeded events
