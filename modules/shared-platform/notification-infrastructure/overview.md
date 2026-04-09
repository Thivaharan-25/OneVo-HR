# Notification Infrastructure

**Module:** Shared Platform  
**Feature:** Notification Infrastructure

---

## Purpose

Template rendering, channel configuration, and SLA-based escalation rules.

## Database Tables

### `notification_templates`
Per-channel + locale templates: `template_code`, `channel`, `subject_template`, `body_template` (Handlebars/Liquid), `locale`, `version`.

### `notification_channels`
Provider config: `channel_type`, `provider` (`resend`, `fcm`, `slack_webhook`), `credentials_encrypted`.

### `escalation_rules`
SLA triggers: `resource_type`, `trigger_condition`, `sla_hours`, `action_type` (`remind`, `escalate`, `auto_approve`).

## Related

- [[modules/shared-platform/overview|Shared Platform Module]]
- [[modules/shared-platform/workflow-engine/overview|Workflow Engine]]
- [[modules/shared-platform/real-time-integrations/overview|Real Time Integrations]]
- [[modules/shared-platform/sso-authentication/overview|Sso Authentication]]
- [[frontend/design-system/theming/tenant-branding|Tenant Branding]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[backend/messaging/error-handling|Error Handling]]
- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4: Shared Platform Agent Gateway]]
