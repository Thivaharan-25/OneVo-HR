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
| `EmployeeOffboardingStarted` | Offboarding initiated | [[modules/notifications/overview|Notifications]], [[modules/documents/overview|Documents]] |

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| POST | `/api/v1/employees/{id}/offboarding` | `employees:write` | Start offboarding |

## Related

- [[modules/core-hr/overview|Core HR Module]]
- [[modules/core-hr/employee-profiles/overview|Employee Profiles]]
- [[modules/core-hr/employee-lifecycle/overview|Employee Lifecycle]]
- [[modules/core-hr/onboarding/overview|Onboarding]]
- [[modules/core-hr/compensation/overview|Compensation]]
- [[modules/core-hr/qualifications/overview|Qualifications]]
- [[modules/core-hr/dependents-contacts/overview|Dependents Contacts]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[security/auth-architecture|Auth Architecture]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[security/compliance|Compliance]]
- [[backend/shared-kernel|Shared Kernel]]
- [[current-focus/DEV2-core-hr-lifecycle|DEV2: Core HR Lifecycle]]
