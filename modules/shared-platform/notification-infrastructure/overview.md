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

- [[shared-platform|Shared Platform Module]]
- [[workflow-engine]]
- [[real-time-integrations]]
- [[sso-authentication]]
- [[tenant-branding]]
- [[event-catalog]]
- [[multi-tenancy]]
- [[error-handling]]
- [[WEEK1-shared-platform]]
