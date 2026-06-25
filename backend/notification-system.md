# Notification System: ONEVO

## Overview

6-step notification pipeline supporting Phase 1 events across in-app, email, and Inbox delivery surfaces. Chat and Workflow action cards are Phase 2; Phase 1 uses direct module-owned approval records and management coverage routing.

```
Event Trigger ? Preferences Check ? Deduplication ? Template Rendering ? Channel Routing ? Dispatch ? Track
```

## Phase 1 Monitoring Alert Routing

Phase 1 monitoring alerts do not use configurable Exception Engine rules or Workflow Engine routing.

Phase 1 alert producers are:
- **Identity Verification** — photo/biometric verification failures and expirations
- **Activity Monitoring** — non-allowed app usage violations, idle threshold breaches
- **Discrepancy Engine** — unaccounted time gaps after day close
- **Work Location Evidence** — work location mismatch beyond grace period

**Recipient resolution (canonical — controlled by Monitoring Policy):**

Monitoring Policy determines who receives monitoring/verification alerts via the `monitoring_alert_recipient_resolver` setting:

- **`management_coverage_availability_chain`** (default): Load active date-effective management coverage assignments for the employee, order by configured priority, filter to users with the required alert permission (e.g., `monitoring:alerts:read`, `monitoring:alerts:resolve`, `verification:review`), check availability (scheduled to work, clocked in, not on approved leave, not marked unavailable). Wait for scheduled recipients within `monitoring_alert_wait_for_scheduled_recipient_grace_minutes` (default: 15) before skipping.
- **`reporting_manager`**: Resolve reporting manager from position hierarchy, check required alert permission and availability. If unavailable and `monitoring_alert_fallback_to_management_coverage_chain` is enabled, fall back to management coverage availability chain.
- **Unresolved**: If no eligible available person exists, follow `monitoring_alert_unresolved_routing_action` (default: `create_routing_issue`). Never silently route to random HR/admin.

Monitoring/verification alerts never blindly notify "reporting manager" unless Monitoring Policy explicitly selects `reporting_manager`.

## Architecture

### Pipeline Steps

1. **Preferences Check:** Read `notification_preferences` — does the user want this category on this channel?
2. **Deduplication:** Check if same notification sent within time window (prevents spam)
3. **Template Rendering:** Load `notification_templates` for the channel + locale, render with event data
4. **Channel Routing:** Route to appropriate channel(s) based on user preferences
5. **Dispatch:** Send via channel provider (in-app DB insert, email via Resend, push via FCM)
6. **Track:** Create `notifications` records for in-app delivery and `email_delivery_logs` rows for Resend email attempts

### Channels

| Channel | Provider | Implementation | Phase |
|:--------|:---------|:---------------|:------|
| In-app | Database + SignalR | Insert `notifications` row, push via SignalR | Phase 1 |
| Email | Resend | Template-based via `notification_templates`; required for Phase 1 customer release | Phase 1 |
| Push | FCM (Firebase) | Mobile push notifications | Phase 2 (with mobile app) |
| Chat action card | WorkSync Chat | Case conversation action card when Chat is enabled | Phase 2 |
| Inbox action card | Inbox | Detail panel action card when Chat is not enabled | Phase 1 |

### Phase 1 Email Requirement

Phase 1 allows logger-only email stubs for local development before the notification module is implemented, but it must not ship to customers with the stub. Customer onboarding, employee invites/account setup, password reset links, temporary-password flows, and any user-enabled email notification channel must dispatch through the Resend-backed email provider before Phase 1 release.

Required configuration:

- `RESEND_API_KEY`
- Verified sender address/domain
- Environment-specific app base URL for generated links
- Template records for every email notification type shipped in Phase 1

### Tables

**Notifications module owns delivery behavior. Shared Platform owns physical notification tables.**

- `notifications` — In-app notification records. Owned by Shared Platform. See [[database/schemas/shared-platform#`notifications`|notifications schema]].
- `notification_preferences` — Per-user channel preferences by category
- `notification_templates` — Templates per channel + locale (owned by Shared Platform)
- `notification_channels` — Channel provider configuration (owned by Shared Platform)
- `escalation_rules` — SLA-based escalation triggers (owned by Shared Platform)

### Email Delivery Tracking

Every Resend-backed email creates an `email_delivery_logs` row before dispatch. The row is updated when Resend accepts the message and again from Resend webhook events such as delivered, bounced, failed, or complained. This supports the invitation, password reset, onboarding, scheduled report, and notification troubleshooting userflows. Admin-visible retry actions create a new delivery log row instead of overwriting prior attempts.

## Notification Categories

| Category | Events | Default Channels |
|:---------|:-------|:----------------|
| `time_off` | TimeOffRequested (includes conflict count), TimeOffApproved, TimeOffRejected | In-app + Email |
| `attendance` | OvertimeApproved, AttendanceCorrected | In-app |
| `payroll` | PayrollRunCompleted, PayrollRunFailed | In-app + Email |
| `performance` | ReviewCycleStarted, ReviewCompleted, GoalCreated | In-app + Email |
| `skills` | SkillValidated, CourseCompleted, CertificationExpiring | In-app |
| `documents` | DocumentPublished, AcknowledgementRequired | In-app + Email |
| `grievance` | GrievanceFiled, DisciplinaryActionIssued | In-app + Email |
| `expense` | ExpenseClaimApproved, ExpenseClaimPaid | In-app |
| `system` | RoleAssigned, SettingsChanged | In-app |
| `recognition` | RecognitionGiven | In-app |
| `monitoring` | AppAllowlistViolationDetected, IdleThresholdExceeded, VerificationFailed, VerificationExpired, WorkLocationMismatch | In-app + Email (critical) |
| `discrepancy` | DiscrepancyCriticalDetected, DiscrepancyHighDetected | In-app + Email (critical) |

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
If Time Off request status = "pending" for > 48 hours:
  -> Send reminder to assigned approver resolver
  -> If still pending after 72 hours: escalate to configured escalation resolver
```

Checked by a Hangfire recurring job (every hour).


## Related

- [[backend/module-catalog|Module Catalog]] — Notifications module and SharedPlatform module details
- [[backend/domain-events|Domain Events]] — all domain events that trigger notifications
- [[backend/external-integrations|External Integrations]] — Resend (email) integration details; Slack is Phase 2
- [[code-standards/logging-standards|Logging Standards]] — notification event logging patterns
- [[infrastructure/observability|Observability]] — monitoring notification delivery
