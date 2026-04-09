# Notification Infrastructure — End-to-End Logic

**Module:** Shared Platform
**Feature:** Notification Infrastructure

---

## Notification Pipeline

### Flow

```
1. Domain event published (e.g., LeaveApproved)
2. NotificationEventHandler receives event
3. Resolve recipients based on event context
4. Load notification_templates WHERE template_code AND channel
5. Render template with Liquid/Handlebars
6. For each channel:
   -> email: call Resend API via notification_channels config
   -> in_app: INSERT notification record + SignalR push
   -> push: FCM via notification_channels config
   -> slack: POST to webhook
7. Log delivery status
```

## Escalation Rules

### Flow

```
EscalationCheckJob (Hangfire, hourly)
  -> Check escalation_rules for pending items past SLA:
    -> e.g., leave_request pending > 48h -> remind manager
    -> If still pending after escalation -> auto_approve or escalate to next role

```

## Related

- [[modules/shared-platform/notification-infrastructure/overview|Overview]]
- [[modules/shared-platform/workflow-engine/overview|Workflow Engine]]
- [[modules/shared-platform/real-time-integrations/overview|Real Time Integrations]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
