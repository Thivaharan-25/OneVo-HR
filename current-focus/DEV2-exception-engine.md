# Task: Exception Engine Module

**Assignee:** Dev 2
**Module:** ExceptionEngine
**Priority:** Critical
**Dependencies:** [[current-focus/DEV3-activity-monitoring|DEV3 Activity Monitoring]] (IActivityMonitoringService), [[current-focus/DEV3-workforce-presence-setup|DEV3 Workforce Presence Setup]] (IWorkforcePresenceService)

---

## Step 1: Backend

### Acceptance Criteria

#### Rules & Configuration
- [ ] `exception_rules` table — configurable per tenant
- [ ] Rule types: `low_activity`, `excess_idle`, `unusual_pattern`, `excess_meeting`, `no_presence`, `break_exceeded`, `verification_failed`
- [ ] `threshold_json` JSONB with per-type schema validation
- [ ] Rules scoped: `all`, `department`, `team`, `employee`
- [ ] Severity levels: `info`, `warning`, `critical`
- [ ] `exception_schedules` table — work hours + days + timezone

#### Alert Generation
- [ ] `exception_alerts` table — generated when rule threshold breached
- [ ] Alert deduplication: one active alert per rule per employee per evaluation window
- [ ] `data_snapshot_json` — evidence capture at trigger time
- [ ] Alert statuses: `new`, `acknowledged`, `dismissed`, `escalated`
- [ ] `alert_acknowledgements` table — audit trail for actions

#### Escalation
- [ ] `escalation_chains` table — per-severity notification routing
- [ ] Step ordering: reporting_manager -> hr -> ceo (configurable)
- [ ] Time-based escalation: `delay_minutes` per step
- [ ] `EscalationJob` Hangfire job (every 5 min) — auto-escalate unacknowledged alerts

#### Evaluation Engine
- [ ] `ExceptionEngineEvaluationJob` Hangfire job (every 5 min, High queue)
- [ ] Only evaluates during configured work hours (check `exception_schedules`)
- [ ] Reads activity data from `IActivityMonitoringService`
- [ ] Reads presence data from `IWorkforcePresenceService`
- [ ] Checks monitoring toggles + employee overrides before evaluating
- [ ] Domain events: `ExceptionAlertCreated`, `AlertEscalated`, `AlertAcknowledged`

#### Real-Time
- [ ] SignalR push on `exception-alerts` channel for new alerts
- [ ] `IExceptionEngineService` public interface implementation
- [ ] Unit tests >= 80% coverage

### Backend References

- [[modules/exception-engine/overview|exception-engine]] — module architecture, evaluation flow diagram
- [[modules/activity-monitoring/overview|activity-monitoring]] — data source for low_activity, excess_idle, unusual_pattern, excess_meeting rules
- [[modules/workforce-presence/overview|workforce-presence]] — data source for no_presence, break_exceeded rules
- [[modules/configuration/monitoring-toggles/overview|configuration]] — monitoring toggles gate evaluation
- [[infrastructure/multi-tenancy|Multi Tenancy]] — tenant-configurable rules, schedules, and escalation chains

---

## Step 2: Frontend

### Pages to Build

```
app/(dashboard)/workforce/exceptions/
├── page.tsx                      # Alert queue (real-time feed via SignalR)
├── [id]/
│   ├── loading.tsx               # Skeleton while loading
│   └── page.tsx                  # Alert detail + evidence + escalation history
├── rules/page.tsx                # Rule configuration (admin)
├── escalations/page.tsx          # Escalation chain setup
├── components/                   # Colocated feature components
│   ├── AlertCard.tsx             # Alert summary card with actions (acknowledge, dismiss, escalate)
│   ├── RuleEditor.tsx            # Rule create/edit form with preview
│   ├── EscalationChainBuilder.tsx # Visual escalation chain editor
│   └── SeverityBadge.tsx         # info (blue) / warning (yellow) / critical (red) badge
└── _types.ts                     # Local TypeScript definitions
```

### What to Build

- [ ] Exception dashboard page:
  - Real-time alert feed (new alerts appear via SignalR, no refresh needed)
  - Filter by: severity (info/warning/critical), rule type, department, status
  - Alert cards: employee name, rule violated, evidence snapshot, timestamp, severity badge
  - Actions: acknowledge, dismiss (with reason), escalate manually
- [ ] Alert detail modal: full data_snapshot_json visualization, escalation history, acknowledgement trail
- [ ] Exception rule configuration page (admin):
  - List rules with enable/disable toggle
  - Create/edit rule: type, threshold values, scope (all/dept/team/employee), severity
  - Preview: "This rule will flag employees with < 30% activity for > 2 hours"
- [ ] Escalation chain configuration:
  - Define chains per severity
  - Add steps with recipient role + delay_minutes
- [ ] Exception schedule configuration:
  - Define work hours + work days + timezone
  - Rules only evaluate during these hours
- [ ] SeverityBadge component: info (blue), warning (yellow), critical (red)
- [ ] Real-time alert count badge in sidebar navigation

### Userflows

- [[Userflow/Exception-Engine/exception-rule-setup|Exception Rule Setup]] — configure exception detection rules
- [[Userflow/Exception-Engine/exception-dashboard|Exception Dashboard]] — view and manage active exceptions
- [[Userflow/Exception-Engine/alert-review|Alert Review]] — review, acknowledge, or dismiss alerts
- [[Userflow/Exception-Engine/escalation-chain-setup|Escalation Chain Setup]] — configure escalation chains

### API Endpoints (Frontend Consumes)

| Method | Endpoint | Purpose |
|:-------|:---------|:--------|
| GET | `/api/v1/exceptions/alerts` | List alerts (filtered, paginated) |
| GET | `/api/v1/exceptions/alerts/{id}` | Alert detail + evidence |
| PUT | `/api/v1/exceptions/alerts/{id}/acknowledge` | Acknowledge alert |
| PUT | `/api/v1/exceptions/alerts/{id}/dismiss` | Dismiss with reason |
| PUT | `/api/v1/exceptions/alerts/{id}/escalate` | Manual escalate |
| GET | `/api/v1/exceptions/rules` | List exception rules |
| POST | `/api/v1/exceptions/rules` | Create rule |
| PUT | `/api/v1/exceptions/rules/{id}` | Update rule |
| GET | `/api/v1/exceptions/escalation-chains` | List chains |
| POST | `/api/v1/exceptions/escalation-chains` | Create chain |
| GET | `/api/v1/exceptions/schedules` | List schedules |
| POST | `/api/v1/exceptions/schedules` | Create schedule |
| **SignalR** | `/hubs/notifications` | `exception-alerts` channel for real-time |

### Frontend References

- [[frontend/design-system/components/component-catalog|Component Catalog]] — DataTable, SeverityBadge, StatusBadge, Card
- [[frontend/design-system/foundations/color-tokens|Color Tokens]] — severity colors
- [[frontend/design-system/patterns/data-visualization|Data Visualization]] — evidence visualization
- [[frontend/data-layer/api-integration|API Integration]] — SignalR real-time setup

---

## Related Tasks

- [[current-focus/DEV3-activity-monitoring|DEV3 Activity Monitoring]] — IActivityMonitoringService consumed here
- [[current-focus/DEV3-workforce-presence-setup|DEV3 Workforce Presence Setup]] — IWorkforcePresenceService consumed here
- [[current-focus/DEV4-identity-verification|DEV4 Identity Verification]] — VerificationFailed events feed verification_failed rule type
- [[current-focus/DEV2-notifications|DEV2 Notifications]] — notifications module delivers alerts
- [[current-focus/DEV1-productivity-analytics|DEV1 Productivity Analytics]] — exception counts in productivity reports
