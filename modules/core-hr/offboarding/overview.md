# Offboarding

**Module:** Core HR  
**Feature:** Offboarding

---

## Purpose

Manages offboarding records including reason, last working date, knowledge risk assessment, knowledge transfer / handover status, exit interview notes, and outstanding penalties.

## Database Tables

### `offboarding_records`
Fields: `reason` (`resignation`, `termination`, `retirement`, `contract_end`), `last_working_date`, `knowledge_risk_level`, `exit_interview_notes`, `penalties_json`, `status`.

`penalties_json` is the Phase 1 container for offboarding deductions and exceptions that must be carried into final settlement. It may include outstanding loans, notice-period violations, asset recovery penalties, and knowledge-transfer bypass penalties.

Recommended `penalties_json` shape:

```json
{
  "items": [
    {
      "type": "knowledge_transfer_bypass",
      "amount": 0,
      "currency": "USD",
      "reason": "Critical handover skipped with HR approval",
      "approved_by_id": "uuid",
      "approved_at": "2026-04-29T00:00:00Z",
      "source": "offboarding_workflow"
    }
  ],
  "total_amount": 0,
  "currency": "USD"
}
```

## Knowledge Transfer and Bypass Policy

Knowledge transfer is part of the manager offboarding checklist. The manager is responsible for handover, task reassignment, and confirming that business-critical knowledge has been captured.

| Risk level | Required handling |
|:-----------|:------------------|
| `low` | Knowledge transfer task is optional unless the offboarding template requires it. |
| `medium` | Knowledge transfer task is created and assigned to the manager. |
| `high` | Knowledge transfer task is mandatory before offboarding completion unless bypassed by HR/Admin approval. |
| `critical` | Additional handover workflow is triggered. Offboarding cannot be completed until knowledge transfer is completed or an approved bypass is recorded. |

### Bypass Rules

- Bypass is allowed only when an authorized HR/Admin user approves it.
- Bypass requires a reason.
- Bypass is audit-sensitive and must be recorded in `penalties_json`.
- If the tenant policy applies a monetary penalty for bypassing knowledge transfer, the penalty item is stored with `type = "knowledge_transfer_bypass"`.
- Phase 1 records the penalty and makes it available for final-settlement review. Payroll execution remains downstream / Phase 2 unless explicitly implemented.
- If no penalty amount is configured, the bypass can still be recorded with `amount = 0` for audit purposes.

## Domain Events

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `EmployeeOffboardingStarted` | Offboarding initiated | [[modules/notifications/overview\|Notifications]], [[modules/documents/overview\|Documents]] |

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| POST | `/api/v1/employees/{id}/offboarding` | `employees:write` | Start offboarding |
| PUT | `/api/v1/offboarding/{id}/knowledge-transfer` | `employees:write` | Mark knowledge transfer complete or update handover status |
| POST | `/api/v1/offboarding/{id}/knowledge-transfer/bypass` | `employees:write` | Approve knowledge-transfer bypass and optionally record penalty |

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
