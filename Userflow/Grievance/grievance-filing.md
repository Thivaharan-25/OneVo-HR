# Grievance Filing

**Area:** Grievance  
**Required Permission(s):** `grievance:write`  
**Related Permissions:** `documents:write` (attach evidence)

---

## Preconditions

- Employee is active
- Required permissions: [[permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: File Grievance
- **UI:** Sidebar → Grievance → "File Grievance" → select category: Harassment, Discrimination, Workplace Safety, Policy Violation, Other
- **API:** `POST /api/v1/grievance/cases`

### Step 2: Enter Details
- **UI:** Enter description (rich text) → attach evidence documents → select confidentiality level (Standard / Highly Confidential — restricts who can view)
- **Validation:** Description required, min 50 characters

### Step 3: Submit
- **Backend:** GrievanceService.FileAsync() → [[grievance]]
- **DB:** `grievance_cases` — case number generated (GRV-2026-001), status: "Open"
- **Result:** HR team notified → case assigned to HR admin

### Step 4: Track Status
- **UI:** Grievance → My Cases → see status (Open, Under Investigation, Resolved, Closed) → timeline of updates

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Empty description | Validation fails | "Please provide a detailed description" |
| File too large | Upload rejected | "Maximum attachment size is 10MB per file" |

## Events Triggered

- `GrievanceFiled` → [[event-catalog]]
- Notification to HR → [[notification-system]]

## Related Flows

- [[grievance-investigation]]
- [[disciplinary-action]]
- [[document-upload]]

## Module References

- [[grievance]]
