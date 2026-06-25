# Work Location Compliance

**Area:** Monitoring
**Trigger:** Work-location verification is enabled and an employee is in paid working time
**Required Permission(s):** `monitoring:configure`, `monitoring:alerts:read`, `verification:review`
**Related Permissions:** `settings:admin`, `employees:write`, `attendance:read`

---

## Purpose

Verify that employees work from the expected onsite Company office location or approved remote work location during paid working time. The system uses network and device evidence to detect location mismatch and may trigger identity verification for review.

This is network-based work-location verification, not GPS-grade live tracking. AWS Rekognition verifies identity from a photo challenge; it does not prove physical location by itself.

## Canonical Model

- User-facing term: Company.
- Internal storage term: `legal_entities`.
- Company context is selected from the topbar dropdown.
- Settings > General is Company-scoped.
- One Company has one office location, stored on `legal_entities`.
- If a customer needs another branch, sub-office, or physical office location, they create another Company/legal entity.
- Phase 1 has no separate work-location list screen, no separate location CRUD, no branch/sub-office model, and no office-location table.

## Monitoring Window

Work-location evidence is evaluated only when all conditions are true:

```text
employee is in a paid working session
AND employee is not on break
AND employee is not in an approved Time Off interval
AND work-location verification is enabled
AND employee expected_work_area requires location verification
```

No work-location evidence is evaluated before paid work starts, after work ends, during breaks, during approved Time Off intervals, or when policy disables monitoring.

## Configuration Ownership

| Configuration | Owner | Notes |
|:--------------|:------|:------|
| Company office location | Settings admin for selected Company | Edited in Settings > General; one office location per Company |
| Employee work mode | Authorized monitoring configuration user | `onsite`, `remote`, `hybrid`, or `field` |
| Approved remote work location | Employee first capture, approver-controlled changes | First remote clock-in captures automatically after identity verification |
| Grace period and severity | Authorized monitoring configuration user | Monitoring configuration only; does not create location records |
| Approval routing | Org Structure management coverage owner | Requires the relevant approval/review permission; Phase 1 does not invoke Workflow Engine |

## Company Office Location

Company office location is defined in **Settings > General** for the currently selected Company.

Required fields:

| Field | Required | Notes |
|:------|:---------|:------|
| Office address label | Yes | Human-readable office label |
| Latitude | Yes when onsite verification is enabled | Used for office-location verification |
| Longitude | Yes when onsite verification is enabled | Used for office-location verification |
| Allowed radius in meters | Yes when onsite verification is enabled | Mismatch threshold |

Monitoring configuration can warn when onsite verification is enabled but the selected Company has no office location. Monitoring does not own a Company office-location setup page.

## Employee Work Modes and Expected Work Area

`work_mode` defines what the employee is *allowed* to do. `expected_work_area` defines where the employee is *planned* to work today. Do not treat hybrid as "system can guess onsite or remote."

| Work Mode | Meaning |
|:----------|:--------|
| `onsite` | Employee works from the Company office |
| `remote` | Employee works from an approved remote location |
| `hybrid` | Employee is allowed both onsite and remote days — the actual expected work area comes from the schedule/roster/day override |
| `field` | No strict office/remote match |

**Expected work area resolution** — for any employee/date, resolve in this order:

1. Approved work area change request
2. Roster entry override (`roster_entries.expected_work_area`)
3. Shift assignment override (`shift_assignments.expected_work_area`)
4. Schedule day setting (per-day from `work_schedules.workdays_json`)
5. Schedule default (`work_schedules.default_work_area`)
6. Employee `work_mode` fallback (`hybrid` → `either` only as last resort)

See [[modules/time-attendance/overview#Expected Work Area Resolution|Expected Work Area Resolution]] for full details.

**Location matching by expected_work_area:**

| Expected Work Area | Validate Against |
|:-------------------|:-----------------|
| `onsite` | Company office location |
| `remote` | Approved remote work profile |
| `either` | Company office location OR approved remote work profile |
| `field` | No strict office/remote match; review rules may apply separately |

There is no separate "no enforcement" work-mode enum in Phase 1. Disable work-location verification through policy/override settings instead.

## Remote First-Time Capture

When an employee is assigned `remote` or `hybrid` and has no approved remote work location:

1. Employee clocks in remotely.
2. Time & Attendance starts the paid work session.
3. Tray app shows **Set this as your approved remote work location**.
4. Employee completes photo verification.
5. Agent captures evidence:
   - public IP
   - local IP
   - Wi-Fi SSID
   - Wi-Fi BSSID / router MAC hash when available
   - gateway MAC hash when available
   - VPN detected flag
   - coarse OS location only if permission is granted
6. If identity verification passes, the system saves the approved remote work location profile.
7. If identity verification fails or expires, the session is marked for review and a verification alert is created.

Only one active approved remote work location is allowed per employee in Phase 1.

## Remote Work Location Change Request

If an employee needs to change their approved remote work location:

1. Employee opens **Employee Settings -> Remote Work Location**.
2. Employee clicks **Request Location Change**.
3. Employee enters a reason, such as `Moved house`.
4. Request is routed through Org Structure management coverage to one eligible owner with the required permission.
5. Approver approves or rejects.
6. If approved, the next remote clock-in becomes a re-capture session.
7. Employee completes photo verification and the agent captures the new profile.
8. Old profile is archived and the new profile becomes active.

## Onsite Verification

Onsite attendance source can be biometric or device punch. Work-location compliance does not need to be checked at the attendance punch moment.

```text
Employee is onsite
-> Attendance may already exist from biometric/device punch
-> Laptop becomes active during the paid work session
-> Agent captures work-location evidence
-> Backend compares against selected Company's single office location
-> If matched: mark location compliant
-> If mismatched beyond grace: create compliance/review signal
```

Location mismatch is a compliance/review signal. It is not necessarily the attendance source itself.

## During Work Hours

The agent sends lightweight work-location evidence while monitoring is active. The backend resolves the `expected_work_area` for today (via the 6-level resolution chain) and evaluates each eligible heartbeat against the expected location source:

- `expected_work_area = onsite`: selected Company office location from `legal_entities`
- `expected_work_area = remote`: active employee remote work profile
- `expected_work_area = either`: selected Company office location OR active employee remote work profile
- `expected_work_area = field`: no strict office/remote match

If the employee appears outside the expected location:

1. First mismatch creates `suspected_out_of_location`.
2. System starts the configured grace period.
3. If evidence returns to an approved location within grace, no alert is raised.
4. If mismatch continues beyond grace, create `WORK_LOCATION_MISMATCH`.
5. Agent Gateway may send `capture_photo`.
6. Identity Verification records the photo result when required.
7. Notifications alert the recipient resolved by Monitoring Policy (default: first available responsible person from the management coverage availability chain).

## Alert Routing

Monitoring Policy controls who receives monitoring alerts. The `monitoring_alert_recipient_resolver` setting determines the resolution strategy:

- **`management_coverage_availability_chain`** (default): Load active date-effective management coverage assignments for the employee, order by configured priority, filter to users with the required alert permission (e.g., `monitoring:alerts:read`, `monitoring:alerts:resolve`, `verification:review`), then check availability (scheduled to work, clocked in, not on approved leave, not marked unavailable). If a responsible person is scheduled but has not reached scheduled start time + configured grace window (`monitoring_alert_wait_for_scheduled_recipient_grace_minutes`), wait before skipping. If no eligible available person exists, follow `monitoring_alert_unresolved_routing_action` (default: `create_routing_issue`).
- **`reporting_manager`**: Resolve reporting manager from position hierarchy, check required alert permission and availability. If unavailable, fall back to management coverage availability chain when `monitoring_alert_fallback_to_management_coverage_chain` is enabled.

Phase 1 routing uses Monitoring Policy and does not invoke Workflow Engine or a generic escalation chain.

## Alert Evidence

Alert detail should show enough evidence for action without exposing unnecessary private data:

```text
Employee
Expected location source
Detected status
Mismatch start time
Mismatch duration
Attendance / paid-work status
Break status
Detected network summary
Confidence level
Photo verification status
```

Evidence must not display full raw location history to broad audiences. Detailed raw evidence is restricted to authorized reviewers.

## Outcomes

| Outcome | Meaning |
|:--------|:--------|
| `resolved_verified` | Employee completed verification and manager accepted |
| `resolved_false_positive` | Network change was accepted as non-violation |
| `acknowledged_policy_exception` | Manager accepted a business reason |
| `employee_failed_verification` | Face verification failed |
| `employee_did_not_respond` | Photo challenge expired |

## Related

- [[Userflow/Monitoring/monitoring-configuration|Monitoring Configuration]]
- [[Userflow/Monitoring/identity-verification-review|Identity Verification Review]]
- [[Userflow/Configuration/monitoring-toggles|Monitoring Toggles]]
- [[Userflow/Configuration/tenant-settings|General Settings]]
- [[modules/agent-gateway/work-location-evidence|Work Location Evidence]]
- [[modules/agent-gateway/work-location-evidence/overview|Work Location Evidence - Overview]]
- [[modules/agent-gateway/work-location-evidence/end-to-end-logic|Work Location Evidence - End-to-End Logic]]
- [[modules/agent-gateway/work-location-evidence/testing|Work Location Evidence - Testing]]
- [[modules/time-attendance/presence-sessions/overview|Presence Sessions]]
- [[modules/time-attendance/break-tracking/overview|Break Tracking]]
- [[modules/exception-engine/alert-generation/overview|Alert Generation]]
- [[modules/identity-verification/photo-verification/overview|Photo Verification]]
