# Work Location Evidence - End-to-End Logic

**Module:** Agent Gateway
**Feature:** Work Location Evidence

---

## Flow A: Admin Configures Company Office Location

1. Admin selects a Company from the topbar tenant/company dropdown.
2. Admin opens **Settings > General**.
3. Admin fills the Company office location fields:
   - office address label
   - latitude
   - longitude
   - allowed radius in meters
4. Admin saves.
5. Org Structure updates the selected `legal_entities` row.
6. Monitoring policy can now use that Company's single office location for onsite verification.

Phase 1 has no separate work-location list screen, no separate location CRUD, no branch/sub-office records, and no separate work-location canonical table.

## Flow B: Admin Assigns Employee Work Mode

1. Admin opens employee monitoring settings.
2. Admin sets work mode:
   - `onsite`
   - `remote`
   - `hybrid`
   - `field`
3. Configuration stores `employee_work_location_settings`.
4. Agent Gateway refreshes agent policy on next heartbeat or via `refresh_policy`.

Disable work-location verification through policy or employee override. Do not use a separate "no enforcement" work-mode enum.

## Flow C: Remote Work Location First Capture

1. Employee with `remote` or `hybrid` mode clocks in remotely.
2. Time & Attendance starts or updates the active paid work session.
3. Agent Gateway returns policy showing remote profile is missing.
4. Tray App displays **Set this as your approved remote work location**.
5. Tray App requests a photo and sends `capture_remote_work_location` evidence to the Service.
6. Service collects network evidence and submits it to Agent Gateway.
7. Identity Verification compares the photo against the enrolled employee.
8. If verification passes:
   - Configuration creates `employee_remote_work_profiles` with `status = active`.
   - Any previous profile remains archived.
   - Current session is marked location-compliant.
9. If verification fails or expires:
   - Identity Verification creates a failed verification record.
   - Phase 1: lightweight verification alert via Notifications/Inbox, recipient resolved by Monitoring Policy. Phase 2: may route through Exception Engine configurable rules.

Only one active approved remote work location profile is allowed per employee in Phase 1.

## Flow D: Onsite Laptop-Active Evaluation

1. Employee attendance may already exist from biometric/device punch.
2. Laptop becomes active during the paid work session.
3. Agent sends initial work-location evidence with heartbeat.
4. Agent Gateway stores work-location evidence.
5. Time & Attendance confirms the employee is in paid work and not on break.
6. Backend resolves the employee's primary Company from the active primary employment assignment.
7. Matching logic compares evidence to the Company office location on `legal_entities`.
8. If matched, mark location compliant.
9. If mismatched beyond grace, create a location compliance/review signal.

Location mismatch is not necessarily the attendance source itself. Attendance can remain sourced from biometric/device punch while laptop-active evidence verifies onsite compliance.

## Flow E: Normal Work-Location Evaluation (All Work Modes)

1. Agent heartbeat reports work-location evidence during paid work.
2. Time & Attendance confirms:
   - employee is in paid work
   - employee is not on break
   - employee is not in an approved Time Off interval
   - session is active paid working time
3. System resolves `expected_work_area` for today using the 6-level resolution chain (see [[modules/time-attendance/overview#Expected Work Area Resolution|Expected Work Area Resolution]]):
   1. Approved work area change request
   2. Roster entry override
   3. Shift assignment override
   4. Schedule day setting (per-day from `workdays_json`)
   5. Schedule default (`default_work_area`)
   6. Employee `work_mode` fallback
4. Matching logic selects expected source based on resolved `expected_work_area`:
   - `onsite` → Company office location from `legal_entities`
   - `remote` → active `employee_remote_work_profiles`
   - `either` → Company office location OR active remote work location profile
   - `field` → no strict office/remote match; review rules may apply separately
5. System writes `match_status` and `confidence` to the evidence row.
6. If matched, no alert is created.
7. If mismatched, the grace timer starts.

Hybrid employees do not default to "either." The expected work area is determined by their schedule's per-day setting. `either` only applies as a fallback when no schedule/roster/shift rule exists.

## Flow F: Mismatch During Work Hours

1. Agent heartbeat reports evidence that does not match the expected location source.
2. Phase 1 lightweight alert detection evaluates `work_location_mismatch`.
3. If mismatch duration is below grace period, alert is deferred.
4. If mismatch continues beyond grace:
   - Phase 1: lightweight work-location mismatch alert via Notifications/Inbox, recipient resolved by Monitoring Policy. Phase 2: may route through Exception Engine configurable rules.
   - Alert evidence includes expected location source, detected network summary, confidence, paid-work status, and break status.
   - Agent Gateway may send `capture_photo`.
   - Notifications alert the first available responsible person from the management coverage availability chain, as resolved by Monitoring Policy.
   - Additional evidence reviewers are included only if the module explicitly supports review participation and they have the required permissions.
5. Identity Verification attaches photo result to the alert evidence when a photo challenge is required.

## Flow G: Remote Work Location Change Request

1. Employee opens **Employee Settings -> Remote Work Location**.
2. Employee submits a reason.
3. System creates `remote_work_location_change_requests` with `status = pending`.
4. Approval resolves through Org Structure management coverage to one eligible owner with the required permission.
5. Approver approves or rejects.
6. If approved, the next remote clock-in starts re-capture.
7. After successful photo verification:
   - old profile is archived
   - new profile becomes active
   - request status becomes `captured`

## Flow H: One-Day Work Area Change Request

Distinct from Flow G (permanent remote location change). This handles a single-day override to the expected work area.

1. Employee opens Time Tracking → Request → Work Area Change Request.
2. Form shows current planned `expected_work_area` (resolved from schedule/roster/shift).
3. Employee selects new requested work area and provides a reason.
4. System creates `work_area_change_requests` with `status = pending`.
5. Approval resolves through Org Structure management coverage.
6. If approved:
   - Today's `expected_work_area` changes to the approved value.
   - Work-location matching uses the new expected work area.
   - No work-location mismatch alert for the approved area.
7. If rejected:
   - Expected work area remains unchanged.
   - If employee works from a different location anyway, mismatch rules apply.

## Failure Handling

| Failure | Handling |
|:--------|:---------|
| Agent offline | Evidence is not evaluated; missing heartbeat rules may apply |
| Insufficient evidence | Mark `unknown`; do not alert unless strict mode is enabled |
| Company office location missing | Onsite enforcement cannot start; show configuration warning |
| Remote profile missing | Next remote clock-in starts first-capture |
| Photo challenge expires | Alert outcome `employee_did_not_respond` |
| Employee on break | Do not collect or evaluate evidence |
| Employee in approved Time Off interval | Do not collect or evaluate evidence; treat as explained absence |
| Public IP changes but stronger signal matches | Keep high confidence match |

## Events

| Event | Publisher | Consumer |
|:------|:----------|:---------|
| `WorkLocationEvidenceReceived` | Agent Gateway | Time & Attendance; Phase 2: Exception Engine |
| `WorkLocationMismatchDetected` | Work Location Evidence (Phase 1 lightweight detection) | Notifications, Agent Gateway; Phase 2: Exception Engine |
| `RemoteWorkLocationCaptureRequested` | Configuration / Agent Gateway | Tray App |
| `RemoteWorkLocationProfileApproved` | Configuration | Agent Gateway |
| `RemoteWorkLocationChangeRequested` | Configuration | Notifications |

## Related

- [[modules/agent-gateway/work-location-evidence/overview|Work Location Evidence]]
- [[Userflow/Monitoring/work-location-compliance|Work Location Compliance]]
- [[database/schemas/agent-gateway|Agent Gateway Schema]]
- [[database/schemas/configuration|Configuration Schema]]
- [[database/schemas/org-structure|Org Structure Schema]]
