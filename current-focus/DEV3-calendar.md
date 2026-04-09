# Task: Calendar Module

**Assignee:** Dev 3
**Module:** Calendar
**Priority:** High
**Dependencies:** [[current-focus/DEV1-infrastructure-setup|DEV1 Infrastructure Setup]] (shared kernel, multi-tenancy)

---

## Step 1: Backend

### Acceptance Criteria

- [ ] `calendar_events` table — unified calendar with polymorphic `source_type` + `source_id`
- [ ] Event types: `company`, `team`, `personal`, `leave`, `holiday`, `review`
- [ ] Source types: `manual`, `leave_request`, `holiday`, `review_cycle`
- [ ] Visibility levels: `public`, `team`, `private`
- [ ] CRUD endpoints: `GET/POST/PUT/DELETE /api/v1/calendar`
- [ ] `ICalendarConflictService` — detect overlapping events for employee + date range
- [ ] Conflict detection excludes `leave` and `holiday` event types
- [ ] Conflict severity: `review` and `company` = high, `team` and `personal` = medium
- [ ] `GET /api/v1/calendar/conflicts` endpoint — requires `leave:create` or `leave:approve`
- [ ] Domain events: `CalendarEventCreated`, `CalendarEventUpdated`, `CalendarEventDeleted`
- [ ] Listen for `LeaveApproved` → auto-create calendar event with `source_type=leave_request`
- [ ] Listen for `LeaveCancelled` → auto-delete corresponding calendar event
- [ ] Company holiday seeding via tenant setup
- [ ] Unit tests >= 80% coverage

### Backend References

- [[modules/calendar/overview|Calendar Module]] — module architecture, public interface
- [[modules/calendar/calendar-events/overview|Calendar Events]] — table schema, API endpoints
- [[modules/calendar/conflict-detection/overview|Conflict Detection]] — ICalendarConflictService, business rules
- [[infrastructure/multi-tenancy|Multi Tenancy]] — tenant-scoped events

---

## Step 2: Frontend

### Pages to Build

```
app/(dashboard)/calendar/
├── page.tsx                      # Unified calendar view (monthly, color-coded)

# Note: Calendar is a single-page feature. Components are simple enough to inline
# or extract only if they grow complex during implementation.
```

### What to Build

- [ ] Unified calendar view: monthly with color-coded events (leave=blue, holiday=green, review=orange, company=purple, team=teal, personal=gray)
- [ ] Create manual calendar events (company, team, personal types) — modal dialog
- [ ] Edit/delete own events
- [ ] Filter by event type
- [ ] Conflict warning display when viewing date ranges with overlapping events
- [ ] PermissionGate: authenticated (all users can view), event creation based on role

### Userflows

- [[Userflow/Calendar/calendar-event-creation|Calendar Event Creation]] — create calendar events
- [[Userflow/Calendar/conflict-detection|Conflict Detection]] — detect scheduling conflicts

### API Endpoints (Frontend Consumes)

| Method | Endpoint | Purpose |
|:-------|:---------|:--------|
| GET | `/api/v1/calendar` | Calendar events for date range |
| POST | `/api/v1/calendar` | Create event |
| PUT | `/api/v1/calendar/{id}` | Update event |
| DELETE | `/api/v1/calendar/{id}` | Delete event |
| GET | `/api/v1/calendar/conflicts` | Conflict check for date range |

### Frontend References

- [[frontend/design-system/components/component-catalog|Component Catalog]] — Calendar, Badge, Dialog
- [[frontend/data-layer/api-integration|API Integration]] — API client pattern

---

## Related Tasks

- [[current-focus/DEV1-infrastructure-setup|DEV1 Infrastructure Setup]] — shared kernel, multi-tenancy
- [[current-focus/DEV1-leave|DEV1 Leave]] — Leave module consumes ICalendarConflictService from this module
- [[current-focus/DEV2-auth-security|DEV2 Auth Security]] — permission checks
