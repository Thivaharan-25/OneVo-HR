# Notification System: ONEVO

## Overview

6-step notification pipeline supporting events across in-app, email, push, Chat, and Inbox delivery surfaces. Workflow action cards are routed by the Automation Center delivery router before notification dispatch.

```
Event Trigger → Preferences Check → Deduplication → Template Rendering → Channel Routing → Dispatch → Track
```

## Architecture

### Pipeline Steps

1. **Preferences Check:** Read `notification_preferences` — does the user want this category on this channel?
2. **Deduplication:** Check if same notification sent within time window (prevents spam)
3. **Template Rendering:** Load `notification_templates` for the channel + locale, render with event data
4. **Channel Routing:** Route to appropriate channel(s) based on user preferences
5. **Dispatch:** Send via channel provider (in-app DB insert, email via Resend, push via FCM)
6. **Track:** Create `notifications` record, mark as delivered

### Channels

| Channel | Provider | Implementation | Phase |
|:--------|:---------|:---------------|:------|
| In-app | Database + SignalR | Insert `notifications` row, push via SignalR | Phase 1 |
| Email | Resend | Template-based via `notification_templates`; required for Phase 1 customer release | Phase 1 |
| Push | FCM (Firebase) | Mobile push notifications | Phase 2 (with mobile app) |
| Chat action card | WorkSync Chat | Case conversation action card when Chat is enabled | Phase 1 when WorkSync is enabled |
| Inbox action card | Inbox | Detail panel action card when Chat is not enabled | Phase 1 |

### Phase 1 Email Requirement

Phase 1 allows logger-only email stubs for local development before the notification module is implemented, but it must not ship to customers with the stub. Customer onboarding, employee invites/account setup, password reset links, temporary-password flows, and any user-enabled email notification channel must dispatch through the Resend-backed email provider before Phase 1 release.

Required configuration:

- `RESEND_API_KEY`
- Verified sender address/domain
- Environment-specific app base URL for generated links
- Template records for every email notification type shipped in Phase 1

### Tables

- `notifications` — In-app notification records (user_id, type, title, message, is_read, severity)
- `notification_preferences` — Per-user channel preferences by category
- `notification_templates` — Templates per channel + locale (from SharedPlatform)
- `notification_channels` — Channel provider configuration (from SharedPlatform)
- `escalation_rules` — SLA-based escalation triggers (from SharedPlatform)

## Notification Categories

| Category | Events | Default Channels |
|:---------|:-------|:----------------|
| `leave` | LeaveRequested (includes conflict count), LeaveApproved, LeaveRejected | In-app + Email |
| `attendance` | OvertimeApproved, AttendanceCorrected | In-app |
| `payroll` | PayrollRunCompleted, PayrollRunFailed | In-app + Email |
| `performance` | ReviewCycleStarted, ReviewCompleted, GoalCreated | In-app + Email |
| `skills` | SkillValidated, CourseCompleted, CertificationExpiring | In-app |
| `documents` | DocumentPublished, AcknowledgementRequired | In-app + Email |
| `grievance` | GrievanceFiled, DisciplinaryActionIssued | In-app + Email |
| `expense` | ExpenseClaimApproved, ExpenseClaimPaid | In-app |
| `system` | RoleAssigned, SettingsChanged | In-app |
| `recognition` | RecognitionGiven | In-app |

## Quiet Hours

Configurable per tenant in `tenant_settings`:

```json
{
  "setting_group": "notifications",
  "setting_key": "quiet_hours",
  "setting_value": {
    "enabled": true,
    "start": "22:00",
    "end": "07:00",
    "timezone": "Asia/Colombo",
    "exceptions": ["payroll", "system"]
  }
}
```

During quiet hours, non-exception notifications are queued and delivered at quiet hours end.

## Escalation Rules

Configured in `escalation_rules` table:

```
If leave_request status = "pending" for > 48 hours:
  -> Send reminder to assigned approver resolver
  -> If still pending after 72 hours: escalate to configured escalation resolver
```

Checked by a Hangfire recurring job (every hour).

Escalation rules and workflow notifications must not target fixed role names. They should target resolver outputs such as first eligible approver in the position reporting chain, employee's reporting manager, users with selected permission, users in selected legal entity/department/team/position/position branch, optional job level when configured, specific employee, previous workflow approver, case conversation participants, HR coverage resolver, or configured escalation resolver.

## Related

- [[backend/module-catalog|Module Catalog]] — Notifications module and SharedPlatform module details
- [[backend/domain-events|Domain Events]] — all domain events that trigger notifications
- [[backend/external-integrations|External Integrations]] — Resend (email) and Slack integration details
- [[code-standards/logging-standards|Logging Standards]] — notification event logging patterns
- [[infrastructure/observability|Observability]] — monitoring notification delivery
