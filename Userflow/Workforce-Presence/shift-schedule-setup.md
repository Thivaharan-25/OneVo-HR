# Shift & Schedule Setup

**Area:** Workforce Presence  
**Trigger:** Admin defines shift patterns and assigns schedules (user action — configuration)
**Required Permission(s):** `attendance:write`  
**Related Permissions:** `org:manage` (department-wide assignment)

---

## Preconditions

- Department/team structure exists → [[Userflow/Org-Structure/department-hierarchy|Department Hierarchy]]
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Create Shift Definition
- **UI:** Calendar sidebar → Shifts → "Create Shift" → enter: name (e.g., "Morning"), start time (09:00), end time (18:00), break duration (60 min), grace period for late (15 min)
- **API:** `POST /api/v1/workforce/shifts`
- **DB:** `shifts` — record created

### Step 2: Create Schedule Template
- **UI:** Calendar sidebar → Schedules → "Create Template" → name template → assign shifts per day of week (Mon-Fri: Morning, Sat-Sun: Off) → supports rotating schedules
- **API:** `POST /api/v1/workforce/schedule-templates`
- **DB:** `schedule_templates`

### Step 3: Assign to Employees/Departments
- **UI:** Select template → assign to: individual employees, team, or entire department → set effective date range (permanent or temporary)
- **API:** `POST /api/v1/workforce/schedules/assign`
- **Backend:** ScheduleService.AssignAsync() → [[modules/workforce-presence/shifts-schedules/overview|Shifts Schedules]]
- **DB:** `employee_schedules` — assignment records

### Step 4: Confirmation
- Employees see their schedule on dashboard → shift times determine late/early flags → feeds into exception engine

## Variations

### Rotating schedules
- Define multi-week pattern (Week A: Morning, Week B: Night) → system auto-rotates

### Holiday overrides
- Public holidays auto-apply from the legal entity's Calendar holiday settings -> [[Userflow/Calendar/calendar-integrations|Calendar Integrations]]

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Overlapping shifts | Validation fails | "Employee already has a shift for this time" |
| Break > shift duration | Validation fails | "Break cannot exceed shift duration" |

## Events Triggered

- `ShiftCreated` → [[backend/messaging/event-catalog|Event Catalog]]
- `ScheduleAssigned` → [[backend/messaging/event-catalog|Event Catalog]]

## Related Flows

- [[Userflow/Workforce-Presence/presence-session-view|Presence Session View]]
- [[Userflow/Workforce-Presence/overtime-management|Overtime Management]]
- [[Userflow/Exception-Engine/exception-rule-setup|Exception Rule Setup]]

## Module References

- [[modules/workforce-presence/shifts-schedules/overview|Shifts Schedules]]
- [[modules/workforce-presence/overview|Workforce Presence]]

## Connection to Work Management

Shift schedule data from this flow feeds directly into WMS Resource Management:

- **Capacity baseline:** Each employee's scheduled hours per day/week (from their shift pattern) become the capacity baseline in WMS Resource Planning (`CAPACITY_SNAPSHOT`).
- **Overtime threshold:** When an employee's WMS time logs exceed their scheduled shift hours, the excess is flagged as potential overtime. The overtime entry (`OVERTIME_ENTRY`) is created automatically when the timesheet is approved.
- **Availability for sprint planning:** Resource management uses scheduled hours to determine how many hours an employee can realistically be allocated to a project sprint.

See [[Userflow/Work-Management/time-tracking-flow|Time Tracking Flow]] and [[Userflow/Work-Management/resource-flow|Resource Management Flow]].

