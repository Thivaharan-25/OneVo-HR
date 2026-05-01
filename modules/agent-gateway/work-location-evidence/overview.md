# Work Location Evidence

**Module:** Agent Gateway  
**Feature:** Work Location Evidence  
**Phase:** Phase 1 extension  
**Primary User Flow:** [[Userflow/Workforce-Intelligence/work-location-compliance|Work Location Compliance]]

---

## Purpose

Collect and ingest network-based workplace evidence from the desktop agent while an employee is clocked in, not on break, and eligible for monitoring. This evidence allows the backend to determine whether the employee appears to be working from an approved office or approved remote workplace.

This feature does not provide GPS-grade live tracking. AWS Rekognition is used only for identity verification when a photo challenge is required.

---

## Responsibilities

| Responsibility | Owner |
|:---------------|:------|
| Capture network evidence from desktop device | Agent Service |
| Show remote workplace setup and mismatch prompts | Tray App |
| Ingest and store evidence | Agent Gateway |
| Determine clocked-in / break eligibility | Workforce Presence |
| Match evidence against approved workplace profiles | Configuration + Exception Engine |
| Trigger mismatch alert and escalation | Exception Engine |
| Trigger and store photo verification result | Identity Verification |

---

## Evidence Signals

| Signal | Required | Notes |
|:-------|:---------|:------|
| Public IP | Yes | Captured from backend request metadata |
| Local IP | Optional | Helpful for diagnostics |
| Wi-Fi SSID | Optional | Display hint; not authoritative |
| Wi-Fi BSSID hash | Recommended | Strong workplace/network signal |
| Gateway MAC hash | Recommended | Strong workplace/network signal |
| VPN detected | Optional | Explains public IP changes |
| Coarse OS location | Optional | Only if tenant policy and OS permission allow |

---

## Database Tables

Canonical definitions live in schema docs:

- [[database/schemas/agent-gateway#`agent_work_location_evidence`|agent_work_location_evidence]]
- [[database/schemas/configuration#`work_locations`|work_locations]]
- [[database/schemas/configuration#`employee_work_location_settings`|employee_work_location_settings]]
- [[database/schemas/configuration#`employee_remote_work_profiles`|employee_remote_work_profiles]]
- [[database/schemas/configuration#`remote_work_location_change_requests`|remote_work_location_change_requests]]

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

## Related

- [[modules/agent-gateway/work-location-evidence/end-to-end-logic|Work Location Evidence - End-to-End Logic]]
- [[modules/agent-gateway/work-location-evidence/testing|Work Location Evidence - Testing]]
- [[modules/agent-gateway/data-collection|Data Collection Architecture]]
- [[modules/agent-gateway/tray-app-ui|Tray App UI]]
- [[modules/exception-engine/exception-rules/overview|Exception Rules]]
- [[modules/identity-verification/photo-verification/overview|Photo Verification]]
