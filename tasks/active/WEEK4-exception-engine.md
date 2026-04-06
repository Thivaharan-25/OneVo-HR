# WEEK4: Exception Engine Module

**Status:** Planned
**Priority:** Critical
**Assignee:** Dev 2
**Sprint:** Week 4 (Apr 28 – May 2)
**Module:** ExceptionEngine

## Description

Implement configurable anomaly detection rules, threshold-based alert generation, escalation chains with time-based escalation, and exception schedules (work hours only evaluation).

## Acceptance Criteria

### Rules & Configuration
- [ ] `exception_rules` table — configurable per tenant
- [ ] Rule types: `low_activity`, `excess_idle`, `unusual_pattern`, `excess_meeting`, `no_presence`, `break_exceeded`, `verification_failed`
- [ ] `threshold_json` JSONB with per-type schema validation
- [ ] Rules scoped: `all`, `department`, `team`, `employee`
- [ ] Severity levels: `info`, `warning`, `critical`
- [ ] `exception_schedules` table — work hours + days + timezone

### Alert Generation
- [ ] `exception_alerts` table — generated when rule threshold breached
- [ ] Alert deduplication: one active alert per rule per employee per evaluation window
- [ ] `data_snapshot_json` — evidence capture at trigger time
- [ ] Alert statuses: `new`, `acknowledged`, `dismissed`, `escalated`
- [ ] `alert_acknowledgements` table — audit trail for actions

### Escalation
- [ ] `escalation_chains` table — per-severity notification routing
- [ ] Step ordering: reporting_manager → hr → ceo (configurable)
- [ ] Time-based escalation: `delay_minutes` per step
- [ ] `EscalationJob` Hangfire job (every 5 min) — auto-escalate unacknowledged alerts

### Evaluation Engine
- [ ] `ExceptionEngineEvaluationJob` Hangfire job (every 5 min, High queue)
- [ ] Only evaluates during configured work hours (check `exception_schedules`)
- [ ] Reads activity data from `IActivityMonitoringService`
- [ ] Reads presence data from `IWorkforcePresenceService`
- [ ] Checks monitoring toggles + employee overrides before evaluating
- [ ] Domain events: `ExceptionAlertCreated`, `AlertEscalated`, `AlertAcknowledged`

### Real-Time
- [ ] SignalR push on `exception-alerts` channel for new alerts
- [ ] `IExceptionEngineService` public interface implementation
- [ ] Unit tests ≥80% coverage

## Related Files

- [[exception-engine]] — module architecture, evaluation flow diagram
- [[activity-monitoring]] — data source for rules
- [[workforce-presence]] — presence data for rules
- [[configuration]] — monitoring toggles
- [[notifications]] — alert delivery
