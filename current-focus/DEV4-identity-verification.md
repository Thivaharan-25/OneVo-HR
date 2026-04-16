# Task: Identity Verification Module

**Assignee:** Dev 4
**Module:** IdentityVerification
**Priority:** High
**Dependencies:** [[current-focus/DEV1-infrastructure-setup|DEV1 Infrastructure Setup]] (shared kernel), [[current-focus/DEV4-shared-platform-agent-gateway|DEV4 Shared Platform Agent Gateway]] (agent gateway for photo capture)

---

## Step 1: Backend

### Acceptance Criteria

- [ ] `biometric_devices` table + CRUD — device registration, type (fingerprint/face/card), location, `api_key_hash` (HMAC-SHA256), `is_active` flag, tenant-scoped
- [ ] `verification_policies` table — per-tenant config (login/logout/interval, match threshold)
- [ ] `verification_records` table — each verification event with confidence score
- [ ] Photo verification endpoint: agent sends photo -> compare against employee avatar -> return match result
- [ ] Match confidence scoring (0-100), threshold from policy (default 80.0)
- [ ] Verification statuses: `verified`, `failed`, `skipped`, `expired`
- [ ] Failure reason tracking for failed verifications
- [ ] `IIdentityVerificationService` public interface implementation
- [ ] Domain events: `VerificationFailed` -> exception engine + notifications, `VerificationCompleted` -> workforce presence
- [ ] Verification respects monitoring overrides — skip if `identity_verification = false` for employee
- [ ] `PurgeExpiredVerificationPhotosJob` (daily 2 AM) — delete photos past retention period
- [ ] Verification photos are RESTRICTED data, stored in blob storage
- [ ] Verification photos are temporary (default 30 days retention) — NOT employee profile photos
- [ ] `CheckBiometricDeviceHealthJob` (every 5 min) — flag offline devices
- [ ] Phase 1: simple photo comparison. Phase 2: ML matching service
- [ ] Unit tests >= 80% coverage

### Backend References

- [[modules/identity-verification/overview|identity-verification]] — module architecture
- [[modules/configuration/monitoring-toggles/overview|configuration]] — monitoring overrides
- [[modules/workforce-presence/overview|workforce-presence]] — VerificationCompleted confirms presence
- [[security/data-classification|Data Classification]] — verification photos are RESTRICTED
- [[infrastructure/multi-tenancy|Multi Tenancy]] — per-tenant verification policies

---

## Step 2: Frontend

### Pages to Build

```
app/(dashboard)/workforce/verification/
├── page.tsx                      # Verification log (DataTable: employee, status, confidence, trigger)
├── pending/page.tsx              # Pending verification requests
├── components/                   # Colocated feature components
│   ├── VerificationLogTable.tsx  # Verification history DataTable with filters
│   └── PendingRequestCard.tsx    # Pending verification card with side-by-side photo
└── _types.ts                     # Local TypeScript definitions
```

### What to Build

- [ ] Verification log page:
  - DataTable: employee, timestamp, status (verified/failed/skipped/expired), confidence score, trigger (login/logout/interval)
  - Filter by status, date range, department
  - Failed verifications highlighted with SeverityBadge
  - Click row to see: captured photo vs profile photo side-by-side, confidence score, failure reason
- [ ] Verification policy configuration (admin):
  - Trigger settings: on login, on logout, periodic interval (minutes)
  - Match threshold slider (0-100, default 80)
  - Retention period for verification photos
  - Enable/disable per tenant
- [ ] Verification statistics dashboard widget:
  - Success rate %, total verifications today, failed count
  - Trend chart (daily success rate over time)
- [ ] PermissionGate: `verification:read`, `verification:configure`

### Userflows

- [[Userflow/Workforce-Intelligence/identity-verification-setup|Identity Verification Setup]] — configure verification policies
- [[Userflow/Workforce-Intelligence/identity-verification-review|Identity Verification Review]] — review verification records and failures

### API Endpoints (Frontend Consumes)

| Method | Endpoint | Purpose |
|:-------|:---------|:--------|
| GET | `/api/v1/verification/records` | List verification records |
| GET | `/api/v1/verification/records/{id}` | Record detail + photos |
| GET | `/api/v1/verification/records/{id}/photo` | Captured photo |
| GET | `/api/v1/verification/policies` | Verification policy config |
| PUT | `/api/v1/verification/policies` | Update policy |
| GET | `/api/v1/verification/stats` | Verification statistics |

### Frontend References

- [[frontend/design-system/components/component-catalog|Component Catalog]] — DataTable, SeverityBadge, StatCard
- [[frontend/design-system/patterns/data-visualization|Data Visualization]] — trend chart
- [[frontend/design-system/foundations/color-tokens|Color Tokens]] — severity colors

---

## Related Tasks

- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4 Shared Platform Agent Gateway]] — agent gateway is the photo capture source
- [[current-focus/DEV2-auth-security|DEV2 Auth Security]] — verification triggered at login/logout
- [[current-focus/DEV3-workforce-presence-setup|DEV3 Workforce Presence Setup]] — presence sessions updated on VerificationCompleted
- [[current-focus/DEV2-exception-engine|DEV2 Exception Engine]] — VerificationFailed triggers exception alert
- [[current-focus/DEV2-notifications|DEV2 Notifications]] — notifications module delivers VerificationFailed alerts
