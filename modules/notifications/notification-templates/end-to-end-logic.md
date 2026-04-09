# Notification Templates — End-to-End Logic

**Module:** Notifications
**Feature:** Notification Templates

---

## Manage Templates

### Flow

```
Notification templates are pre-configured per event type + channel:
  -> Each domain event maps to a template:
     -> e.g., "leave.approved" + "email" -> template with subject + body
  -> Templates use Liquid/Handlebars syntax for variable substitution
  -> Variables: {{employee_name}}, {{leave_type}}, {{start_date}}, etc.

Notification Pipeline (when domain event fires):
  -> 1. Event handler receives domain event (e.g., LeaveApproved)
  -> 2. Resolve recipients (employee, manager, HR)
  -> 3. Load notification_templates WHERE event_type AND channel AND is_active
  -> 4. Render template with event data
  -> 5. Dispatch to channel (email via Resend, in_app via DB insert, SignalR push)
  -> 6. Log delivery status
```

### Key Rules

- **Templates are per-tenant** — each tenant can customize their notification content.
- **Multiple channels per event** — one event can trigger email + in_app + push simultaneously.

## Related

- [[frontend/architecture/overview|Notification Templates Overview]]
- [[frontend/architecture/overview|Notification Channels]]
- [[frontend/architecture/overview|SignalR Real-Time]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
