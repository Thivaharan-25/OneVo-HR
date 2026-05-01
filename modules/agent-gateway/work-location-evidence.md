# Work Location Evidence

**Module:** Agent Gateway  
**Feature:** Work Location Evidence  
**Phase:** Phase 1 extension  

---

## Purpose

Collect lightweight network and device evidence from the desktop agent so Workforce Presence and Exception Engine can verify whether a clocked-in employee appears to be working from an approved office or approved remote workplace.

This feature deliberately avoids continuous GPS-style tracking. Network evidence is captured only while the monitoring lifecycle is active and is paused during breaks.

---

## Evidence Captured

| Signal | Source | Reliability | Notes |
|:-------|:-------|:------------|:------|
| Public IP | Backend request metadata | Medium | Can change with ISP/VPN |
| Local IP | Agent | Low | Useful only with other signals |
| Wi-Fi SSID | Agent | Low | Display signal; names can be duplicated |
| Wi-Fi BSSID / access point MAC | Agent | High | Strongest Wi-Fi workplace signal |
| Gateway MAC | Agent | High | Strong network fingerprint when available |
| VPN detected | Agent/backend | Medium | Helps explain IP changes |
| Coarse OS location | Agent, permission-based | Optional | Captured only if tenant policy and OS permission allow |

---

## Collection Lifecycle

Work-location evidence collector follows the same lifecycle contract as other collectors:

```text
StartMonitoring -> collect evidence on heartbeat
PauseMonitoring -> stop collection immediately
ResumeMonitoring -> resume collection
StopMonitoring -> stop collection and flush buffer
```

The collector must not run during breaks or after clock-out.

---

## Heartbeat Payload

```json
{
  "presence_session_id": "uuid",
  "captured_at": "2026-05-01T09:15:00Z",
  "public_ip": "203.0.113.10",
  "local_ip": "192.168.1.42",
  "wifi_ssid": "OneVo-Office",
  "wifi_bssid_hash": "sha256:...",
  "gateway_mac_hash": "sha256:...",
  "vpn_detected": false,
  "coarse_location": {
    "latitude": 6.9271,
    "longitude": 79.8612,
    "accuracy_meters": 500
  }
}
```

MAC-style identifiers should be hashed before long-term storage unless the tenant explicitly needs raw values for IT administration.

---

## Matching Confidence

| Confidence | Meaning |
|:-----------|:--------|
| `high` | BSSID or gateway MAC matches approved profile |
| `medium` | Public IP/VPN range and SSID match |
| `low` | Only coarse IP or coarse location matches |
| `mismatch` | Evidence does not match any approved profile |
| `unknown` | Insufficient evidence; do not alert unless policy explicitly requires strict mode |

---

## Server Evaluation

Agent Gateway stores raw evidence and publishes `WorkLocationEvidenceReceived`. Workforce Presence determines whether the employee is inside an active paid work window. Exception Engine evaluates the mismatch rule only when Workforce Presence says the session is eligible for monitoring.

```text
Agent heartbeat
-> Agent Gateway records work_location_evidence
-> Workforce Presence checks clock/break/session state
-> Exception Engine evaluates WORK_LOCATION_MISMATCH
-> Agent Gateway sends capture_photo if challenge is required
```

---

## Privacy Rules

1. Do not collect evidence outside active monitoring.
2. Do not collect during breaks.
3. Do not use photo verification as a location proof; it is identity proof only.
4. Keep detailed evidence restricted to authorized reviewers.
5. Retain evidence according to monitoring retention policy.

---

## Related

- [[Userflow/Workforce-Intelligence/work-location-compliance|Work Location Compliance]]
- [[modules/agent-gateway/work-location-evidence/overview|Work Location Evidence - Overview]]
- [[modules/agent-gateway/work-location-evidence/end-to-end-logic|Work Location Evidence - End-to-End Logic]]
- [[modules/agent-gateway/work-location-evidence/testing|Work Location Evidence - Testing]]
- [[modules/agent-gateway/data-collection|Data Collection Architecture]]
- [[modules/agent-gateway/tray-app-ui|Tray App UI]]
- [[modules/workforce-presence/presence-sessions/overview|Presence Sessions]]
- [[modules/identity-verification/photo-verification/overview|Photo Verification]]
