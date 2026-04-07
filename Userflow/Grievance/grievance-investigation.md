# Grievance Investigation

**Area:** Grievance  
**Required Permission(s):** `grievance:manage`  
**Related Permissions:** `employees:read` (view involved parties)

---

## Preconditions

- Grievance case filed → [[grievance-filing]]
- Required permissions: [[permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Review Case
- **UI:** Grievance → Open Cases → select case → read description and evidence
- **API:** `GET /api/v1/grievance/cases/{id}`

### Step 2: Assign Investigator
- **UI:** Assign investigator (HR staff or external) → set target resolution date
- **API:** `PUT /api/v1/grievance/cases/{id}/assign`
- **DB:** `grievance_cases` — status: "Under Investigation", `investigator_id` set

### Step 3: Investigation
- **UI:** Investigator adds notes from interviews → uploads additional evidence → records findings → timeline visible to authorized parties only
- **API:** `POST /api/v1/grievance/cases/{id}/notes`

### Step 4: Recommend Action
- **UI:** Investigator recommends: No action, Mediation, Warning, Disciplinary Action, Policy Change
- HR reviews recommendation

### Step 5: Resolve Case
- **UI:** Enter resolution summary → select outcome → close case → employee notified of resolution (appropriate detail level based on confidentiality)
- **API:** `PUT /api/v1/grievance/cases/{id}/resolve`
- **DB:** Status: "Resolved"

## Variations

### Escalation to disciplinary
- If outcome = disciplinary → [[disciplinary-action]] triggered

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Conflict of interest | Warning | "Assigned investigator is in the same department as the subject" |
| Past target date | Alert | "Resolution target date has passed" |

## Events Triggered

- `GrievanceInvestigationStarted` → [[event-catalog]]
- `GrievanceResolved` → [[event-catalog]]
- Notifications to parties → [[notification-system]]

## Related Flows

- [[grievance-filing]]
- [[disciplinary-action]]

## Module References

- [[grievance]]
- [[audit-logging]]
