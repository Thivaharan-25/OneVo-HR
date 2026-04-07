# Offboarding

**Module:** Core HR  
**Feature:** Offboarding

---

## Purpose

Manages offboarding records including reason, last working date, knowledge risk assessment, exit interview notes, and outstanding penalties.

## Database Tables

### `offboarding_records`
Fields: `reason` (`resignation`, `termination`, `retirement`, `contract_end`), `last_working_date`, `knowledge_risk_level`, `exit_interview_notes`, `penalties_json`, `status`.

## Domain Events

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `EmployeeOffboardingStarted` | Offboarding initiated | [[notifications]], [[documents]] |

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| POST | `/api/v1/employees/{id}/offboarding` | `employees:write` | Start offboarding |

## Related

- [[core-hr|Core HR Module]]
- [[employee-profiles]]
- [[employee-lifecycle]]
- [[onboarding]]
- [[compensation]]
- [[qualifications]]
- [[dependents-contacts]]
- [[multi-tenancy]]
- [[auth-architecture]]
- [[event-catalog]]
- [[compliance]]
- [[shared-kernel]]
- [[WEEK2-core-hr-lifecycle]]
