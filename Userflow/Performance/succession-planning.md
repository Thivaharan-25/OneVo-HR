# Succession Planning

**Area:** Performance  
**Trigger:** HR Admin identifies successors for key positions (user action — strategic)
**Required Permission(s):** `performance:manage`  
**Related Permissions:** `employees:read` (view candidate profiles), `skills:read` (view competencies)

---

## Preconditions

- Critical roles identified in org structure → [[Userflow/Org-Structure/job-family-setup|Job Family Setup]]
- Employees have performance reviews and skill assessments → [[Userflow/Performance/manager-review|Manager Review]], [[Userflow/Skills-Learning/skill-assessment|Skill Assessment]]
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Identify Critical Role
- **UI:** Performance → Succession → "Add Critical Role" → select job family level or specific position → mark as succession-critical

### Step 2: Nominate Successors
- **UI:** Search employees → add as potential successors → rate readiness: "Ready Now", "1-2 Years", "3-5 Years"
- **API:** `POST /api/v1/performance/succession/nominees`
- **Backend:** SuccessionService.NominateAsync() → [[Userflow/Performance/succession-planning|Succession Planning]]
- **DB:** `succession_plans`, `succession_nominees`

### Step 3: Gap Analysis
- **UI:** View skill gaps between nominee and target role requirements → system highlights missing competencies
- Links: [[Userflow/Skills-Learning/skill-assessment|Skill Assessment]], [[modules/skills/employee-skills/overview|Employee Skills]]

### Step 4: Create Development Actions
- **UI:** For each nominee → assign development actions (training, mentoring, stretch assignments) → link to development plan → set milestones
- Links: [[Userflow/Skills-Learning/development-plan|Development Plan]], [[Userflow/Skills-Learning/course-enrollment|Course Enrollment]]

### Step 5: Track and Review
- **UI:** Review readiness quarterly → update status → succession pipeline dashboard shows coverage for all critical roles

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Nominee is inactive | Warning | "This employee is no longer active" |
| No critical roles | Empty dashboard | "No critical roles identified — add roles to start" |

## Events Triggered

- `SuccessionNomineeAdded` → [[backend/messaging/event-catalog|Event Catalog]]

## Related Flows

- [[Userflow/Performance/manager-review|Manager Review]]
- [[Userflow/Skills-Learning/skill-assessment|Skill Assessment]]
- [[Userflow/Skills-Learning/development-plan|Development Plan]]
- [[Userflow/Employee-Management/employee-promotion|Employee Promotion]]

## Module References

- [[Userflow/Performance/succession-planning|Succession Planning]]
- [[modules/skills/development-plans/overview|Development Plans]]
- [[modules/performance/goals-okr/overview|Goals Okr]]
