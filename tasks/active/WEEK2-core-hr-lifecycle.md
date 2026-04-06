# WEEK2: Core HR — Employee Lifecycle

**Status:** Planned
**Priority:** Critical
**Assignee:** Dev 2
**Sprint:** Week 2 (Apr 14-18)
**Module:** CoreHR

## Description

Implement employee lifecycle management: onboarding workflows, offboarding (with knowledge risk + penalties), and lifecycle events (promotions, transfers, salary changes).

## Acceptance Criteria

- [ ] `employee_lifecycle_events` table — append-only audit trail
- [ ] Lifecycle event types: `hired`, `promoted`, `transferred`, `salary_change`, `suspended`, `terminated`, `resigned`
- [ ] `onboarding_templates` — reusable task templates (per department or global)
- [ ] `onboarding_tasks` — generated from template on hire, assigned to various users
- [ ] Onboarding status tracking (pending → in_progress → completed)
- [ ] `offboarding_records` — initiated on termination/resignation
- [ ] Knowledge risk assessment (`low`, `medium`, `high`, `critical`)
- [ ] Penalties tracking (outstanding loans, notice period violations) in `penalties_json`
- [ ] Offboarding workflow integration with [[shared-platform]] workflow engine
- [ ] Domain events: `EmployeeCreated`, `EmployeePromoted`, `EmployeeTransferred`, `EmployeeTerminated`
- [ ] `EmployeeTerminated` event triggers: leave forfeiture, final payroll, agent revocation
- [ ] Promotion flow: update job_title_id + create salary_history entry + lifecycle event
- [ ] Transfer flow: update department_id/team + lifecycle event
- [ ] Unit tests ≥80% coverage

## Related Files

- [[core-hr]] — module architecture, domain events
- [[notification-system]] — lifecycle notifications
- [[event-catalog]] — domain event definitions
- [[agent-gateway]] — revoke agent on termination
