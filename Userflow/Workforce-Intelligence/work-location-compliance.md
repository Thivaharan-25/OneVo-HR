# Work Location Compliance

**Area:** Workforce Intelligence  
**Trigger:** Employee clocks in while work-location monitoring is enabled  
**Required Permission(s):** `monitoring:configure`, `exceptions:view`, `verification:review`  
**Related Permissions:** `settings:admin`, `employees:write`, `attendance:read`

---

## Purpose

Verify that employees work from their approved office or remote workplace during paid working time. The system uses network and device evidence to detect when an employee appears outside the approved work location, then triggers photo verification and manager escalation.

This is **network-based work-location verification**, not GPS-grade live tracking. AWS Rekognition verifies identity from the photo challenge; it does not prove the physical location by itself.

---

## Monitoring Window

Work-location evidence is collected only when all conditions are true:

```text
employee is clocked in
AND employee is not on break
AND employee is inside working hours or an active approved work session
AND work-location monitoring is enabled
AND employee has a work mode that requires location enforcement
```

No work-location evidence is collected before clock-in, after clock-out, during breaks, during approved leave, or when policy disables monitoring.

---

## Configuration Ownership

| Configuration | Owner | Notes |
|:--------------|:------|:------|
| Legal entity workplace | Admin / HR admin | Office, branch, or company-approved worksite |
| Employee work mode | Admin / HR admin | `office`, `remote`, `hybrid`, `field`, `no_enforcement` |
| Approved remote workplace | Employee initiates, manager approves changes | Captured from the employee's first approved remote clock-in |
| Grace period and severity | Admin / HR admin | Can inherit from tenant defaults or be overridden by workplace/rule |
| Escalation routing | Admin / HR admin | Reporting manager first, then hierarchy-aware reviewers/escalation chain |

---

## Legal Entity Workplace Setup

Admins configure company workplaces from **Settings -> Monitoring -> Work Locations**.

Required fields:

| Field | Required | Notes |
|:------|:---------|:------|
| Legal Entity | Yes | Example: `OneVo Sri Lanka` |
| Work Location Name | Yes | Example: `Colombo Office` |
| Work Location Type | Yes | `office`, `branch`, `remote_allowed`, `field` |
| Verification Method | Yes | At least one of Wi-Fi BSSID/router MAC, public IP range, or approved VPN range |
| Grace Period | Recommended | Default from tenant policy if blank |
| Alert Severity | Recommended | Default from exception rule if blank |
| Wi-Fi SSID | Optional | Helpful for display, not authoritative because SSIDs can be duplicated |
| Wi-Fi BSSID / Router MAC | Recommended | Strongest office-network signal |
| Public IP Ranges | Recommended | Useful for office networks and static VPN egress |
| Approved VPN IPs | Optional | Allows company VPN as an approved network |

Admins should not have to manually fill every network field. The preferred UX is **Capture Current Network**, where an admin device connected at the office auto-populates:

```text
Wi-Fi SSID
Wi-Fi BSSID
Gateway/router MAC
Public IP
Local IP range
```

The admin reviews the captured values and saves the workplace.

---

## Employee Work Modes

| Work Mode | Expected Location Behavior |
|:----------|:---------------------------|
| `office` | Must match assigned legal entity workplace network |
| `remote` | Must match the employee's approved remote workplace profile |
| `hybrid` | May match either assigned office workplace or approved remote workplace |
| `field` | No strict network enforcement; manager review may be used instead |
| `no_enforcement` | Work-location evidence is not evaluated |

---

## Remote Workplace First-Time Capture

When an employee is assigned `remote` or `hybrid` and has no approved remote workplace:

1. Employee clocks in from the tray app.
2. Tray app shows **Set this as your approved remote workplace**.
3. Employee takes a camera photo.
4. Agent captures network/location evidence:
   - public IP
   - local IP
   - Wi-Fi SSID
   - Wi-Fi BSSID / router MAC when available
   - gateway MAC when available
   - VPN detected flag
   - coarse OS location only if permission is granted
5. Identity Verification compares the photo against the enrolled employee profile.
6. If the face match passes, the system saves the approved remote workplace profile and locks it.
7. If the face match fails or expires, the work session is marked for manager review and a verification alert is created.

The remote workplace profile is treated as long-lived. Employees cannot edit it directly after setup.

---

## Remote Workplace Change Request

If an employee needs to change their remote workplace:

1. Employee opens **Employee Settings -> Remote Work Location**.
2. Employee clicks **Request Location Change**.
3. Employee enters a reason, such as `Moved house`.
4. Request is routed to the reporting manager's Inbox.
5. Manager approves or rejects.
6. If approved, the next remote clock-in becomes a re-capture session.
7. Employee takes a photo and the agent captures the new network profile.
8. Old profile is archived, new profile becomes active.

Only one active approved remote workplace profile is allowed per employee unless tenant policy explicitly supports multiple remote workplaces.

---

## Clock-In Evaluation

### Office Employee

```text
Clock in
-> Capture network evidence
-> Compare against assigned office workplace
-> If matched: mark location compliant
-> If mismatched: create suspected mismatch and apply grace period
```

### Remote Employee

```text
Clock in
-> If no approved remote profile: start first-time capture
-> If profile exists: compare current evidence against approved profile
-> If matched: mark location compliant
-> If mismatched: request photo verification and apply alert policy
```

### Hybrid Employee

```text
Clock in
-> Compare current evidence against assigned office workplaces
-> If not matched, compare against approved remote workplace
-> If neither matches: suspected mismatch
```

---

## During Work Hours

The agent sends lightweight work-location evidence on heartbeat while monitoring is active. The backend evaluates each heartbeat against the employee's expected location.

If the employee appears outside the approved location:

1. First mismatch creates `suspected_out_of_location`.
2. System starts the configured grace period.
3. If evidence returns to an approved location within grace, no alert is raised.
4. If mismatch continues beyond grace, Exception Engine creates `WORK_LOCATION_MISMATCH`.
5. Agent Gateway sends `capture_photo` to the tray app.
6. Identity Verification records the photo result.
7. Notifications alert the reporting manager and permitted hierarchy reviewers.

---

## Manager And Hierarchy Alert Routing

Immediate recipients:

```text
reporting manager
```

Additional recipients are included only when all are true:

```text
recipient is configured on the work-location alert rule
AND recipient is directly above the employee in the org hierarchy
AND recipient has exceptions:view or verification:review permission
AND recipient is in scope for the employee's legal entity, department, or team
```

If the alert is not acknowledged within the configured delay, the normal Exception Engine escalation chain applies.

---

## Alert Evidence

The alert detail should show enough evidence for action without exposing unnecessary private data:

```text
Employee
Expected location
Detected status
Mismatch start time
Mismatch duration
Clock status
Break status
Detected network summary
Confidence level
Photo verification status
```

Evidence should not display full raw location history to broad audiences. Detailed raw evidence is restricted to authorized reviewers.

---

## Outcomes

| Outcome | Meaning |
|:--------|:--------|
| `resolved_verified` | Employee completed verification and manager accepted |
| `resolved_false_positive` | Network change was accepted as non-violation |
| `acknowledged_policy_exception` | Manager accepted a business reason |
| `employee_failed_verification` | Face verification failed |
| `employee_did_not_respond` | Photo challenge expired |
| `escalated` | Alert was not acknowledged in time |

---

## Related

- [[Userflow/Workforce-Intelligence/monitoring-configuration|Monitoring Configuration]]
- [[Userflow/Workforce-Intelligence/identity-verification-review|Identity Verification Review]]
- [[Userflow/Configuration/monitoring-toggles|Monitoring Toggles]]
- [[modules/agent-gateway/work-location-evidence|Work Location Evidence]]
- [[modules/agent-gateway/work-location-evidence/overview|Work Location Evidence - Overview]]
- [[modules/agent-gateway/work-location-evidence/end-to-end-logic|Work Location Evidence - End-to-End Logic]]
- [[modules/agent-gateway/work-location-evidence/testing|Work Location Evidence - Testing]]
- [[modules/workforce-presence/presence-sessions/overview|Presence Sessions]]
- [[modules/workforce-presence/break-tracking/overview|Break Tracking]]
- [[modules/exception-engine/alert-generation/overview|Alert Generation]]
- [[modules/identity-verification/photo-verification/overview|Photo Verification]]
