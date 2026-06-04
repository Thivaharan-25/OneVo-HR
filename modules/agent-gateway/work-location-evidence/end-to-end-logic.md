# Work Location Evidence - End-to-End Logic

**Module:** Agent Gateway  
**Feature:** Work Location Evidence  

---

## Flow A: Admin Configures Office Workplace

1. Admin opens **Settings -> Monitoring -> Work Locations**.
2. Admin selects legal entity and creates a workplace, e.g. `OneVo Sri Lanka / Colombo Office`.
3. Admin either manually enters network values or clicks **Capture Current Network**.
4. System captures available workplace signals:
   - Wi-Fi SSID
   - Wi-Fi BSSID hash
   - gateway MAC hash
   - public IP
   - local IP range
5. Admin saves the workplace.
6. Configuration validates that at least one verification method exists.
7. Configuration stores the row in `work_locations`.

## Flow B: Admin Assigns Employee Work Mode

1. Admin opens employee monitoring settings.
2. Admin sets work mode:
   - `office`
   - `remote`
   - `hybrid`
   - `field`
   - `no_enforcement`
3. Admin assigns primary office workplace when required.
4. Configuration stores `employee_work_location_settings`.
5. Agent Gateway refreshes agent policy on next heartbeat or via `refresh_policy`.

## Flow C: Remote Workplace First Capture

1. Employee with `remote` or `hybrid` mode clocks in.
2. Workforce Presence starts or updates the active presence session.
3. Agent Gateway returns policy showing remote profile is missing.
4. Tray App displays **Set this as your approved remote workplace**.
5. Tray App requests a photo and sends `capture_remote_workplace` evidence to the Service.
6. Service collects network evidence and submits it to Agent Gateway.
7. Identity Verification compares the photo against the enrolled employee.
8. If verification passes:
   - Configuration creates `employee_remote_work_profiles` with `status = active`.
   - Any previous profile remains archived.
   - Current session is marked location-compliant.
9. If verification fails or expires:
   - Identity Verification creates a failed verification record.
   - Exception Engine creates a verification alert for manager review.

## Flow D: Normal Clock-In Evaluation

1. Employee clocks in.
2. Agent sends initial work-location evidence with heartbeat.
3. Agent Gateway stores `agent_work_location_evidence`.
4. Workforce Presence confirms the employee is clocked in and not on break.
5. Matching logic compares evidence to allowed workplace profiles:
   - Office mode -> assigned `work_locations`
   - Remote mode -> active `employee_remote_work_profiles`
   - Hybrid mode -> either office or remote profile
6. System writes `match_status` and `confidence` to the evidence row.
7. If matched, no alert is created.
8. If mismatched, the grace timer starts.

## Flow E: Mismatch During Work Hours

1. Agent heartbeat reports evidence that does not match any approved workplace.
2. Workforce Presence confirms:
   - employee is clocked in
   - employee is not on break
   - session is active paid working time
3. Exception Engine evaluates `work_location_mismatch`.
4. If mismatch duration is below grace period, alert is deferred.
5. If mismatch continues beyond grace:
   - Exception Engine creates `exception_alerts`.
   - Alert evidence includes expected location, detected network summary, confidence, clock status, and break status.
   - Agent Gateway sends `capture_photo`.
   - Notifications alert the reporting manager.
   - Configured hierarchy reviewers are included only if they are above the employee and have the required permissions.
6. Identity Verification attaches photo result to the alert evidence.

## Flow F: Remote Workplace Change Request

1. Employee opens **Employee Settings -> Remote Work Location**.
2. Employee submits a reason.
3. System creates `remote_work_location_change_requests` with `status = pending`.
4. Reporting manager approves or rejects.
5. If approved, the next remote clock-in starts re-capture.
6. After successful photo verification:
   - old profile is archived
   - new profile becomes active
   - request status becomes `captured`

## Failure Handling

| Failure | Handling |
|:--------|:---------|
| Agent offline | Evidence is not evaluated; missing heartbeat rules may apply |
| Insufficient evidence | Mark `unknown`; do not alert unless strict mode is enabled |
| Photo challenge expires | Alert outcome `employee_did_not_respond` |
| Employee on break | Do not collect or evaluate evidence |
| VPN detected but allowed | Match approved VPN IP ranges |
| Public IP changes but BSSID matches | Keep high confidence match |

## Events

| Event | Publisher | Consumer |
|:------|:----------|:---------|
| `WorkLocationEvidenceReceived` | Agent Gateway | Workforce Presence, Exception Engine |
| `WorkLocationMismatchDetected` | Exception Engine | Notifications, Agent Gateway |
| `RemoteWorkplaceCaptureRequested` | Configuration / Agent Gateway | Tray App |
| `RemoteWorkplaceProfileApproved` | Configuration | Agent Gateway |
| `RemoteWorkplaceChangeRequested` | Configuration | Notifications |

## Related

- [[modules/agent-gateway/work-location-evidence/overview|Work Location Evidence]]
- [[Userflow/Workforce-Intelligence/work-location-compliance|Work Location Compliance]]
- [[database/schemas/agent-gateway|Agent Gateway Schema]]
- [[database/schemas/configuration|Configuration Schema]]

