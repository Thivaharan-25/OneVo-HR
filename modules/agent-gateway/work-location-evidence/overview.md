# Work Location Evidence

**Module:** Agent Gateway  
**Feature:** Work Location Evidence  
**Phase:** Phase 1 extension  
**Primary User Flow:** [[Userflow/Monitoring/work-location-compliance|Work Location Compliance]]

---

## Purpose

Collect and ingest network-based work-location evidence from the desktop agent while an employee is in paid working time, not on break, not on approved Time Off, and eligible for monitoring. This evidence allows the backend to determine whether the employee appears to be working from the expected work area — resolved from the schedule/roster/day override, not guessed from work_mode.

This feature does not provide GPS-grade live tracking. AWS Rekognition is used only for identity verification when a photo challenge is required.

## Expected Work Area Resolution

Work-location matching uses the **expected_work_area** for the employee/date, not just the employee's `work_mode`. See [[modules/time-attendance/overview#Expected Work Area Resolution|Expected Work Area Resolution]] for the 6-level resolution chain.

- `expected_work_area = onsite` → match against Company office location
- `expected_work_area = remote` → match against approved remote work profile
- `expected_work_area = either` → match against Company office location OR approved remote work profile
- `expected_work_area = field` → no strict office/remote match

Hybrid employees are not "system guesses onsite or remote." The expected work area is explicitly set by schedule, roster, shift override, or approved change request.

---

## Responsibilities

| Responsibility | Owner |
|:---------------|:------|
| Capture network evidence from desktop device | Agent Service |
| Show approved remote work location setup and mismatch prompts | Tray App |
| Ingest and store evidence | Agent Gateway |
| Determine clocked-in / break eligibility | Time & Attendance |
| Match evidence against Company office location or approved remote work location | Configuration |
| Trigger mismatch alert | Phase 1: lightweight alert through Notifications/Inbox; Phase 2: Exception Engine configurable rules |
| Trigger and store photo verification result | Identity Verification |

---

## Evidence Signals

| Signal | Required | Notes |
|:-------|:---------|:------|
| Public IP | Yes | Captured from backend request metadata |
| Local IP | Optional | Helpful for diagnostics |
| Wi-Fi SSID | Optional | Display hint; not authoritative |
| Wi-Fi BSSID hash | Recommended | Strong network signal |
| Gateway MAC hash | Recommended | Strong network signal |
| VPN detected | Optional | Explains public IP changes |
| Coarse OS location | Optional | Only if tenant policy and OS permission allow |

---

## Database Tables

Canonical definitions live in schema docs:

- Company office location fields on [[database/schemas/org-structure#`legal_entities`|legal_entities]]
- [[database/schemas/configuration#`employee_work_location_settings`|employee_work_location_settings]]
- [[database/schemas/configuration#`employee_remote_work_profiles`|employee_remote_work_profiles]]
- [[database/schemas/configuration#`remote_work_location_change_requests`|remote_work_location_change_requests]]

Phase 1 has no separate work-location list screen, no separate location CRUD, and no separate work-location canonical table. Company office location is edited through Settings > General for the selected Company. Remote approved location is employee-captured and approval-controlled.

---

## Policy Keys

Agent policy includes:

```json
{
  "work_location_verification": true,
  "work_location": {
    "mode": "remote",
    "grace_period_minutes": 5,
    "strict_unknown_evidence": false,
    "photo_challenge_on_mismatch": true
  }
}
```

---

## Phase 1 Monitoring Alerts

Phase 1 monitoring alerts do not use configurable Exception Engine rules or Workflow Engine routing.

Work Location Evidence is a Phase 1 alert producer. When a location mismatch is detected beyond the configured grace period, it creates a lightweight alert/notification record and routes it through Notifications/Inbox.

**Recipient resolution (controlled by Monitoring Policy):**

Monitoring Policy determines who receives work-location alerts via `monitoring_alert_recipient_resolver`:

- **`management_coverage_availability_chain`** (default): First available responsible person from management coverage assignments, filtered by alert permission and availability.
- **`reporting_manager`**: Reporting manager from position hierarchy, with fallback to management coverage chain when `monitoring_alert_fallback_to_management_coverage_chain` is enabled.
- **Unresolved**: Follow `monitoring_alert_unresolved_routing_action` (default: `create_routing_issue`).

Monitoring/verification alerts never blindly notify "reporting manager" unless Monitoring Policy explicitly selects `reporting_manager`.

---

## Related

- [[modules/agent-gateway/work-location-evidence/end-to-end-logic|Work Location Evidence - End-to-End Logic]]
- [[modules/agent-gateway/work-location-evidence/testing|Work Location Evidence - Testing]]
- [[modules/agent-gateway/data-collection|Data Collection Architecture]]
- [[modules/agent-gateway/tray-app-ui|Tray App UI]]
- [[modules/exception-engine/exception-rules/overview|Exception Rules]]
- [[modules/identity-verification/photo-verification/overview|Photo Verification]]
