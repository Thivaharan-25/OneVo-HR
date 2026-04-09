# Alerts Overview

Alerts surface contextually across the application — on the dashboard, in employee profiles, and via the notification bell. There is no dedicated alerts page.

## Where Alerts Appear

1. **Dashboard** — Alert cards in the Activity & Alerts section (position 5 in dashboard priority). Severity-colored left border. Click → navigates to relevant record.
2. **Employee Profile** — Banner at position 3 (Alerts / Action Items section). Shows alerts specific to that employee (expiring visa, pending review, probation ending).
3. **Notification Bell** — Real-time alert push via SignalR. Click → navigates to relevant record.

## Alert Configuration

Alert rules are configured under **Settings → Alert Rules** (admin only). See [[Userflow/Exception-Engine/exception-rule-setup|Alert Rule Setup]].

## Preconditions

- Alert rules active → [[Userflow/Exception-Engine/exception-rule-setup|Alert Rule Setup]]
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Related Flows

- [[Userflow/Exception-Engine/alert-review|Alert Review]]
- [[Userflow/Exception-Engine/exception-rule-setup|Alert Rule Setup]]
- [[Userflow/Notifications/notification-view|Notification View]]

## Module References

- [[modules/exception-engine/overview|Exception Engine]]
- [[modules/exception-engine/alert-generation/overview|Alert Generation]]
