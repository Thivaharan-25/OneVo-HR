# WEEK4: Supporting Modules + WorkManage Pro Bridges

**Status:** Planned
**Priority:** Medium
**Assignee:** Dev 4
**Sprint:** Week 4 (Apr 28 – May 2)
**Module:** Documents, Notifications, Grievance, Expense, Configuration, Calendar

## Description

Implement remaining supporting modules and the 5 WorkManage Pro bridge interfaces.

## Acceptance Criteria

### Documents Module
- [ ] `document_categories` table — hierarchical via `parent_category_id`
- [ ] `documents` table + CRUD with versioning
- [ ] `document_versions` table — each version linked to `file_records`
- [ ] `document_access_log` — audit trail
- [ ] `document_templates` — reusable templates (offer letters, contracts)

### Notifications Module (Enhanced)
- [ ] `notification_templates` table — per event_type per channel
- [ ] New event types for Workforce Intelligence: `exception.alert.created`, `exception.alert.escalated`, `verification.failed`, `agent.heartbeat.lost`, `productivity.daily.report`, `productivity.weekly.report`
- [ ] `notification_channels` table — email (Resend), in-app, SignalR
- [ ] 6-step notification pipeline: event → resolve recipients → load template → render → dispatch → log
- [ ] SignalR channels: `notifications-{userId}`, `exception-alerts`, `workforce-live`, `agent-status`

### Grievance Module
- [ ] `grievance_cases` table + CRUD (anonymous reporting support)
- [ ] `disciplinary_actions` table

### Expense Module
- [ ] `expense_categories` table + CRUD
- [ ] `expense_claims` table + submit/approve workflow
- [ ] `expense_items` table with receipt upload

### Configuration Module (Enhanced)
- [ ] `tenant_settings` table — timezone, date format, work hours, **privacy mode**
- [ ] `monitoring_feature_toggles` table — global ON/OFF per feature
- [ ] Industry profile default seeding (office_it, manufacturing, retail, healthcare, custom)
- [ ] `employee_monitoring_overrides` table — per-employee feature overrides
- [ ] Merge logic: override wins over tenant toggle
- [ ] Bulk override API: set by department/team/job family
- [ ] `integration_connections` table
- [ ] `retention_policies` table — per data type

### Calendar Module
- [ ] `calendar_events` table — unified calendar (manual, leave, holiday, review)

### WorkManage Pro Bridges (5 interfaces)
- [ ] `GET /api/v1/bridges/people-sync/employees` — People Sync (HR → Work)
- [ ] `GET /api/v1/bridges/availability/{employeeId}` — Availability (HR → Work)
- [ ] `POST /api/v1/bridges/performance/metrics` — Performance (Work → HR)
- [ ] `GET/POST /api/v1/bridges/skills/{employeeId}` — Skills (Bidirectional)
- [ ] `POST /api/v1/bridges/work-activity/time-logs` — Work Activity (Work → HR) **NEW**
- [ ] All bridges authenticated via API key + tenant context
- [ ] Bridge data validated via FluentValidation

## Related Files

- [[documents]], [[notifications]], [[grievance]], [[expense]], [[configuration]], [[calendar]] — module architectures
- [[external-integrations]] — WorkManage Pro bridge definitions
- [[notification-system]] — notification pipeline
- [[data-classification]] — document classification
