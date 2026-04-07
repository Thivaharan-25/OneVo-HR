# Shift & Schedule Setup

**Area:** Workforce Presence  
**Required Permission(s):** `attendance:write`  
**Related Permissions:** `org:manage` (department-wide assignment)

---

## Preconditions

- Department/team structure exists → [[department-hierarchy]]
- Required permissions: [[permission-assignment|Permission Assignment Flow]]

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
- **Backend:** ScheduleService.AssignAsync() → [[shifts-schedules]]
- **DB:** `employee_schedules` — assignment records

### Step 4: Confirmation
- Employees see their schedule on dashboard → shift times determine late/early flags → feeds into exception engine

## Variations

### Rotating schedules
- Define multi-week pattern (Week A: Morning, Week B: Night) → system auto-rotates

### Holiday overrides
- Public holidays auto-applied from legal entity calendar → [[calendar-event-creation]]

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Overlapping shifts | Validation fails | "Employee already has a shift for this time" |
| Break > shift duration | Validation fails | "Break cannot exceed shift duration" |

## Events Triggered

- `ShiftCreated` → [[event-catalog]]
- `ScheduleAssigned` → [[event-catalog]]

## Related Flows

- [[presence-session-view]]
- [[overtime-management]]
- [[exception-rule-setup]]

## Module References

- [[shifts-schedules]]
- [[workforce-presence]]
