# Task: Notifications Module

**Assignee:** Dev 2
**Module:** Notifications
**Priority:** High
**Dependencies:** [[current-focus/DEV4-shared-platform-agent-gateway|DEV4 Shared Platform Agent Gateway]] (notification scaffolding), [[current-focus/DEV2-exception-engine|DEV2 Exception Engine]] (exception alert event types)

---

## Step 1: Backend

### Acceptance Criteria

- [ ] `notification_templates` table — per event_type per channel (email, in_app, signalr)
- [ ] Template rendering via Liquid/Handlebars
- [ ] `notification_channels` table — email (Resend), in-app, SignalR
- [ ] 6-step notification pipeline: event → resolve recipients → load template → render → dispatch → log
- [ ] Event types for Workforce Intelligence: `exception.alert.created`, `exception.alert.escalated`, `verification.failed`, `agent.heartbeat.lost`, `productivity.daily.report`, `productivity.weekly.report`
- [ ] Event types for HR: `leave.requested`, `leave.approved`, `leave.rejected`, `review.cycle.started`, `onboarding.started`
- [ ] SignalR hub at `/hubs/notifications`
- [ ] SignalR channels: `notifications-{userId}`, `exception-alerts`, `workforce-live`, `agent-status`
- [ ] `GET /api/v1/notifications` — list notifications (paginated)
- [ ] `PUT /api/v1/notifications/{id}/read` — mark as read
- [ ] `PUT /api/v1/notifications/read-all` — mark all as read
- [ ] `GET/PUT /api/v1/notifications/preferences` — user notification preferences
- [ ] Domain event listeners for all registered event types
- [ ] Unit tests >= 80% coverage

### Backend References

- [[modules/notifications/overview|Notifications Module]] — module architecture, pipeline, channels
- [[modules/notifications/notification-templates/overview|Notification Templates]] — template schema, rendering
- [[modules/notifications/notification-channels/overview|Notification Channels]] — channel providers
- [[modules/notifications/signalr-real-time/overview|SignalR Real-Time]] — real-time push channels
- [[backend/notification-system|Notification System]] — system-wide notification architecture

---

## Step 2: Frontend

### Pages to Build

```
app/(dashboard)/notifications/
├── page.tsx                      # Notification inbox (paginated, mark read/unread)
└── preferences/page.tsx          # Per-event-type channel toggles (email, in-app)

# Note: Notification bell lives in the DashboardLayout topbar (not a routed page).
# It's a shared component at components/NotificationBell.tsx or inside the layout's components/.
```

### What to Build

- [ ] Notification bell in topbar: dropdown list of recent notifications, unread count badge (shared component, not feature-colocated)
- [ ] Notification inbox page: full list with filters, mark as read, bulk actions
- [ ] Notification preferences page: per-event-type channel toggles (email, in-app)
- [ ] Real-time notification delivery via SignalR (`@microsoft/signalr`)
- [ ] Toast notifications for high-priority alerts
- [ ] PermissionGate: `notifications:read`, `notifications:manage`

### Userflows

- [[Userflow/Notifications/notification-preference-setup|Notification Preference Setup]] — configure notification preferences
- [[Userflow/Notifications/notification-view|Notification View]] — view notifications

### API Endpoints (Frontend Consumes)

| Method | Endpoint | Purpose |
|:-------|:---------|:--------|
| GET | `/api/v1/notifications` | List notifications |
| PUT | `/api/v1/notifications/{id}/read` | Mark as read |
| PUT | `/api/v1/notifications/read-all` | Mark all as read |
| GET | `/api/v1/notifications/preferences` | Notification preferences |
| PUT | `/api/v1/notifications/preferences` | Update preferences |
| SignalR | `/hubs/notifications` | `notifications-{userId}` channel |

### Frontend References

- [[frontend/design-system/components/component-catalog|Component Catalog]] — Badge, Dropdown, Switch
- [[frontend/data-layer/api-integration|API Integration]] — API client pattern
- [[frontend/data-layer/state-management|State Management]] — SignalR integration with TanStack Query

---

## Related Tasks

- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4 Shared Platform Agent Gateway]] — notification scaffolding
- [[current-focus/DEV2-exception-engine|DEV2 Exception Engine]] — exception alerts flow through notifications
- [[current-focus/DEV1-productivity-analytics|DEV1 Productivity Analytics]] — report-ready events delivered via notifications
