# Succession Planning

**Area:** Performance  
**Required Permission(s):** `performance:manage`  
**Related Permissions:** `employees:read` (view candidate profiles), `skills:read` (view competencies)

---

## Preconditions

- Critical roles identified in org structure → [[job-family-setup]]
- Employees have performance reviews and skill assessments → [[manager-review]], [[skill-assessment]]
- Required permissions: [[permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Identify Critical Role
- **UI:** Performance → Succession → "Add Critical Role" → select job family level or specific position → mark as succession-critical

### Step 2: Nominate Successors
- **UI:** Search employees → add as potential successors → rate readiness: "Ready Now", "1-2 Years", "3-5 Years"
- **API:** `POST /api/v1/performance/succession/nominees`
- **Backend:** SuccessionService.NominateAsync() → [[succession-planning]]
- **DB:** `succession_plans`, `succession_nominees`

### Step 3: Gap Analysis
- **UI:** View skill gaps between nominee and target role requirements → system highlights missing competencies
- Links: [[skill-assessment]], [[employee-skills]]

### Step 4: Create Development Actions
- **UI:** For each nominee → assign development actions (training, mentoring, stretch assignments) → link to development plan → set milestones
- Links: [[development-plan]], [[course-enrollment]]

### Step 5: Track and Review
- **UI:** Review readiness quarterly → update status → succession pipeline dashboard shows coverage for all critical roles

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Nominee is inactive | Warning | "This employee is no longer active" |
| No critical roles | Empty dashboard | "No critical roles identified — add roles to start" |

## Events Triggered

- `SuccessionNomineeAdded` → [[event-catalog]]

## Related Flows

- [[manager-review]]
- [[skill-assessment]]
- [[development-plan]]
- [[employee-promotion]]

## Module References

- [[succession-planning]]
- [[development-plans]]
- [[goals-okr]]
