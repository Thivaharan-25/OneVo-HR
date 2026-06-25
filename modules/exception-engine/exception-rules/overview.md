# Exception Rules

**Module:** Exception Engine  
**Feature:** Exception Rules

---

## Purpose

Configurable anomaly detection rules with JSON-based thresholds. Rule types: `low_activity`, `excess_idle`, `unusual_pattern`, `excess_meeting`, `no_presence`, `break_exceeded`, `verification_failed`, `non_allowed_app`, `presence_without_activity`, `heartbeat_gap`, `work_location_mismatch`.

> **Phase 1 note:** `non_allowed_app`, `verification_failed`, and `work_location_mismatch` detection is handled by their respective Phase 1 alert producers (Activity Monitoring, Identity Verification, Work Location Evidence) using lightweight detection and Notifications/Inbox routing. Phase 2 may move these into configurable Exception Engine rules.

> **`non_allowed_app` (Phase 2 as Exception Engine rule)** - fires when an employee accumulates time in an app where `application_usage.is_allowed = false` beyond the `violation_threshold_minutes` in `threshold_json`. Apps with `is_allowed = null` (pending review) are never evaluated. Phase 1 uses Activity Monitoring lightweight detection. See [[modules/activity-monitoring/overview|Activity Monitoring]] and [[docs/superpowers/plans/2026-04-26-app-catalog-observed-applications|App Catalog Plan]].

## Database Tables

**`work_location_mismatch`** fires when an employee remains outside the selected Company's office location or approved remote work location beyond the configured grace period. It must only evaluate sessions that Time & Attendance marks as active paid time, excluding breaks and post-clock-out periods. See [[Userflow/Monitoring/work-location-compliance|Work Location Compliance]].

### `exception_rules`

Threshold JSON must be validated against known schema before evaluation. Invalid JSON = skip rule + log warning.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/exceptions/rules` | `exceptions:manage` | List rules |
| POST | `/api/v1/exceptions/rules` | `exceptions:manage` | Create rule |
| PUT | `/api/v1/exceptions/rules/{id}` | `exceptions:manage` | Update rule |
| DELETE | `/api/v1/exceptions/rules/{id}` | `exceptions:manage` | Deactivate rule |

## Related

- [[modules/exception-engine/overview|Exception Engine Module]]
- [[frontend/architecture/overview|Alert Generation]]
- [[frontend/architecture/overview|Evaluation Engine]]
- [[frontend/architecture/overview|Escalation Chains]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[security/auth-architecture|Auth Architecture]]
- [[security/data-classification|Data Classification]]
- [[backend/shared-kernel|Shared Kernel]]
- [[current-focus/DEV2-exception-engine|DEV2: Exception Engine]]
