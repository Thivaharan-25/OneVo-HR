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
- **UI:** Sidebar → Workforce → Shifts → "Create Shift" → enter: name (e.g., "Morning"), start time (09:00), end time (18:00), break duration (60 min), grace period for late (15 min)
- **API:** `POST /api/v1/workforce/shifts`
- **DB:** `shifts` — record created

### Step 2: Create Schedule Template
- **UI:** Workforce → Schedules → "Create Template" → name template → assign shifts per day of week (Mon-Fri: Morning, Sat-Sun: Off) → supports rotating schedules
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
- Public holidays auto-applied from legal entity calendar → [[Userflow/Calendar/calendar-event-creation|Calendar Event Creation]]

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
