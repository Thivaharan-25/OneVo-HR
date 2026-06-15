# Work Location Evidence - Testing

**Module:** Agent Gateway  
**Feature:** Work Location Evidence  

---

## Test Scope

Tests must prove that work-location evidence is collected, stored, evaluated, and escalated only during eligible working time.

---

## Unit Tests

### Policy Resolution

| Case | Expected |
|:-----|:---------|
| Tenant toggle off | `work_location_verification = false` in agent policy |
| Employee override disables verification | Agent does not collect location evidence |
| Office employee with workplace assigned | Policy includes `mode = office` and workplace identifiers |
| Remote employee without profile | Policy requires remote workplace capture |
| Hybrid employee | Policy allows office or approved remote profile |
| Field/no-enforcement employee | Evidence is not evaluated |

### Matching Logic

| Case | Expected |
|:-----|:---------|
| BSSID hash matches office | `matched`, `high` confidence |
| Gateway hash matches remote profile | `matched`, `high` confidence |
| Public IP range matches but no BSSID | `matched`, `medium` confidence |
| Only coarse location matches | `matched`, `low` confidence |
| No signals match | `mismatch` |
| Missing signals | `unknown` unless strict mode enabled |

### Lifecycle Guardrails

| Case | Expected |
|:-----|:---------|
| Before clock-in | No evidence stored |
| After clock-out | No evidence stored |
| During manual break | No evidence stored or evaluated |
| During auto-detected break | No evidence stored or evaluated |
| Monitoring policy paused | No evidence stored |

---

## Integration Tests

### Office Clock-In

1. Seed legal entity workplace with approved BSSID.
2. Assign employee `office` mode.
3. Submit heartbeat with matching BSSID.
4. Assert `agent_work_location_evidence.match_status = matched`.
5. Assert no exception alert is created.

### Remote First Capture

1. Assign employee `remote` mode with no active remote profile.
2. Submit clock-in.
3. Assert agent receives remote capture requirement.
4. Submit photo verification success and network evidence.
5. Assert `employee_remote_work_profiles.status = active`.
6. Assert profile is locked from direct employee edit.

### Remote Change Approval

1. Seed active remote profile.
2. Employee submits change request.
3. Configured approver approves.
4. Next clock-in submits new profile evidence and successful photo.
5. Assert old profile archived and new profile active.

### Mismatch Escalation

1. Employee is clocked in and not on break.
2. Submit mismatching evidence.
3. Advance time beyond grace period.
4. Assert `work_location_mismatch` alert exists.
5. Assert `capture_photo` command is queued.
6. Assert configured reviewer notification is created.
7. Assert hierarchy reviewer is notified only when above employee and permissioned.

---

## End-to-End Tests

| Scenario | Expected |
|:---------|:---------|
| Office employee works from approved office network | No alert |
| Office employee clocks in from unapproved network | Grace starts, then alert + photo challenge |
| Remote employee first clock-in | Remote profile capture + photo verification |
| Remote employee works from approved profile | No alert |
| Remote employee moves to another network during work | Alert after grace and photo challenge |
| Employee starts break before mismatch | No collection and no alert |
| Employee clocks out before grace expires | No alert |
| Configured approver approves remote location change | Next remote clock-in replaces profile |

---

## Security And Privacy Tests

| Case | Expected |
|:-----|:---------|
| Unauthorized user requests detailed evidence | Forbidden |
| Reviewer outside hierarchy opens alert | Forbidden unless explicit scope exception exists |
| Raw MAC address submitted | Stored as hash or rejected by validation |
| Photo evidence requested without identity verification policy | Command rejected |
| Retention job runs | Old evidence deleted according to retention policy |

---

## Regression Risks

- Break lifecycle must continue to pause all collectors.
- Photo verification must remain identity-only, not location proof.
- Unknown evidence should not create false alerts unless strict mode is configured.
- Public IP changes should not override a high-confidence BSSID/gateway match.

---

## Related

- [[modules/agent-gateway/work-location-evidence/overview|Work Location Evidence]]
- [[modules/agent-gateway/work-location-evidence/end-to-end-logic|Work Location Evidence - End-to-End Logic]]
- [[Userflow/Workforce-Intelligence/work-location-compliance|Work Location Compliance]]

