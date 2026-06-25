# Photo Verification

**Module:** Identity Verification  
**Feature:** Photo Verification

---

## Purpose

Verifies employee identity via photo capture from desktop agent. Phase 1 uses simple comparison, Phase 2 may add ML matching. Captured verification photos compare against the employee's approved verification reference photo. If no reference exists, the first agent sign-in capture is treated as reference enrollment, not a verification attempt.

## Database Tables

### `verification_records`
Key columns: `employee_id`, `verified_at`, `method` (`photo`, `biometric`, `on_demand_photo`), `match_confidence` (0-100), `status` (`verified`, `failed`, `skipped`, `expired`), `agent_id`, `biometric_device_id`, `failure_reason`. WorkPulse photo verification sets `agent_id`; physical terminal verification sets `biometric_device_id`.

### `verification_evidence_assets`
Stores captured verification photos, clock-in/out photos, and verification failure photo evidence. Links each evidence file to `file_records` and, where applicable, `verification_records`. Biometric scan results live in `biometric_events` and do not automatically create photo evidence rows.

### `verification_reference_photos`
Stores the approved comparison baseline. First agent sign-in can create a `pending_review` reference candidate. Only `approved` active reference photos are used for matching.

## Key Business Rules

1. Photos are temporary - retained for configurable period (default 30 days), then auto-deleted.
2. Photos are RESTRICTED data - stored in blob storage, never in DB.
3. Verification policy respects monitoring overrides.
4. First agent sign-in can create a pending reference photo when no approved reference exists.
5. Missing or pending reference photo results in `skipped`/`reference_pending`, not `failed`.

## Phase 1 Alert Model

Phase 1 monitoring alerts do not use configurable Exception Engine rules or Workflow Engine routing. Identity Verification creates lightweight alert/notification records and routes them through Notifications/Inbox.

**Monitoring Policy recipient resolution:**

Monitoring Policy determines who receives monitoring/verification alerts using `monitoring_alert_recipient_resolver`.

Allowed values:
- `management_coverage_availability_chain` (default)
- `reporting_manager`

`management_coverage_availability_chain` routes to the first available responsible person from the employee's active management coverage assignments:
1. Load active date-effective coverage assignments.
2. Order responsible people by configured coverage priority / responsibility weight / effective assignment order.
3. Filter to users with the required alert permission.
4. Check availability:
   - scheduled to work now, or inside the alert routing window
   - clocked in / present
   - not on approved leave
   - not marked unavailable
5. If a responsible person is scheduled but has not reached scheduled start time + `monitoring_alert_wait_for_scheduled_recipient_grace_minutes`, wait before skipping.
6. If no eligible available person exists, follow `monitoring_alert_unresolved_routing_action`.

`reporting_manager` resolves the employee's reporting manager from position hierarchy, then applies the same permission and availability checks. If unavailable and `monitoring_alert_fallback_to_management_coverage_chain` is enabled, fall back to `management_coverage_availability_chain`.

Never silently route monitoring alerts to random HR/admin users.

### Challenge Lifecycle

For on-demand or absence-detected photo verification, `verification_records` tracks: `requested_at` (challenge created), `delivered_at` (agent received), `submitted_at` (photo captured), `expires_at` (challenge expiry), `response_duration_seconds` (submitted - requested), `reviewed_by_id`/`reviewed_at`/`review_status` (reviewer assessment). See [[modules/identity-verification/overview|Identity Verification Module]] for full field definitions.

## Domain Events

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `VerificationFailed` | Match below threshold | [[modules/notifications/overview\|Notifications]] (Phase 1 lightweight verification alert, recipient resolved by Monitoring Policy); Phase 2 may route through Exception Engine |
| `VerificationCompleted` | Successful verification | [[modules/time-attendance/overview\|Time & Attendance]] |

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| POST | `/api/v1/verification/verify` | Internal (agent) | Submit verification photo |
| GET | `/api/v1/verification/records/{employeeId}` | `verification:view` | History |

## Related

- [[modules/identity-verification/overview|Identity Verification Module]]
- [[modules/identity-verification/photo-verification/end-to-end-logic|Photo Verification - End-to-End Logic]]
- [[modules/identity-verification/photo-verification/testing|Photo Verification - Testing]]
- [[frontend/architecture/overview|Biometric Enrollment]]
- [[frontend/architecture/overview|Verification Policies]]
- [[security/data-classification|Data Classification]]
- [[security/compliance|Compliance]]
- [[security/auth-architecture|Auth Architecture]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[current-focus/DEV4-identity-verification|DEV4: Identity Verification]]
