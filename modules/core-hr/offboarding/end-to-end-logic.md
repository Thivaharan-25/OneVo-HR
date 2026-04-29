# Offboarding — End-to-End Logic

**Module:** Core HR
**Feature:** Offboarding

---

## Start Offboarding

### Flow

```
POST /api/v1/employees/{id}/offboarding
  -> EmployeeController.StartOffboarding(id, StartOffboardingCommand)
    -> [RequirePermission("employees:write")]
    -> OffboardingService.StartAsync(employeeId, command, ct)
      -> 1. Load employee, validate status = 'active'
      -> 2. INSERT into offboarding_records
         -> reason, last_working_date, knowledge_risk_level
         -> penalties_json initialized with any known outstanding loans / notice period items
         -> status = 'initiated'
      -> 3. Create offboarding workflow checklist
         -> IT: revoke access and collect devices
         -> HR: exit interview and final documents
         -> Finance: final settlement inputs
         -> Manager: knowledge transfer and task reassignment
         -> Admin: badge/key return and org chart updates
      -> 4. If knowledge_risk_level is high or critical:
         -> Mark knowledge transfer task as mandatory
         -> If critical: trigger additional handover workflow
      -> 5. Create lifecycle event: event_type = 'terminated' or 'resigned'
      -> 6. Publish EmployeeOffboardingStarted event
         -> Consumers:
            -> leave: forfeit unused entitlements
            -> payroll: initiate final settlement
            -> agent-gateway: revoke agent access
            -> notifications: notify HR and manager
      -> 7. Calculate/update penalties_json (outstanding loans, notice period, asset recovery)
      -> Return Result.Success(offboardingDto)
```

## Knowledge Transfer Completion

### Flow

```
PUT /api/v1/offboarding/{id}/knowledge-transfer
  -> OffboardingController.UpdateKnowledgeTransfer(id, UpdateKnowledgeTransferCommand)
    -> [RequirePermission("employees:write")]
    -> OffboardingService.UpdateKnowledgeTransferAsync(id, command, ct)
      -> 1. Load offboarding_record and validate status != 'completed'
      -> 2. Validate caller is assigned manager, HR/Admin, or workflow assignee
      -> 3. Store handover status in workflow step / details_json:
         -> completed_by_id
         -> completed_at
         -> notes
         -> handover_documents / links if provided
      -> 4. Mark knowledge transfer checklist item as completed
      -> 5. Audit log entry
      -> Return Result.Success()
```

## Knowledge Transfer Bypass and Penalty

### Flow

```
POST /api/v1/offboarding/{id}/knowledge-transfer/bypass
  -> OffboardingController.BypassKnowledgeTransfer(id, BypassKnowledgeTransferCommand)
    -> [RequirePermission("employees:write")]
    -> OffboardingService.BypassKnowledgeTransferAsync(id, command, ct)
      -> 1. Load offboarding_record and validate status != 'completed'
      -> 2. Validate knowledge_risk_level is high or critical, or tenant policy allows bypass recording for all risk levels
      -> 3. Validate caller is authorized to approve bypass (HR/Admin or configured workflow approver)
      -> 4. Require bypass reason
      -> 5. Resolve penalty amount:
         -> If command.amount is provided, use manual amount
         -> Else if tenant policy has knowledge_transfer_bypass default, use configured amount
         -> Else amount = 0 and record audit-only bypass
      -> 6. Append item to penalties_json.items:
         -> type = 'knowledge_transfer_bypass'
         -> amount, currency, reason
         -> approved_by_id, approved_at
         -> source = 'offboarding_workflow'
      -> 7. Update penalties_json.total_amount
      -> 8. Mark knowledge transfer checklist item as bypassed
      -> 9. Audit log entry
      -> Return Result.Success(offboardingDto)
```

### Penalty Rules

| Rule | Handling |
|:-----|:---------|
| No penalty policy configured | Record bypass with `amount = 0` for audit only. |
| Manual penalty entered | Store manual amount, currency, approver, timestamp, and reason in `penalties_json`. |
| Tenant default penalty configured | Use configured amount when no manual amount is supplied. |
| Payroll integration unavailable | Phase 1 records final-settlement input only; payroll execution remains downstream. |
| Legal/compliance review required | Keep bypass and penalty history in offboarding audit trail. |

## Complete Offboarding

### Flow

```
PUT /api/v1/offboarding/{id}/complete
  -> OffboardingController.Complete(id, CompleteOffboardingCommand)
    -> [RequirePermission("employees:write")]
    -> OffboardingService.CompleteAsync(id, command, ct)
      -> 1. Store exit_interview_notes
      -> 2. Validate required checklist items complete
         -> If knowledge_risk_level is high/critical:
            -> Require knowledge transfer completed OR bypassed with approved reason
      -> 3. Validate penalties_json is finalized for final-settlement review
      -> 4. UPDATE employee: employment_status = 'terminated', termination_date
      -> 5. Deactivate user account: is_active = false
      -> 6. Revoke all sessions and refresh tokens
      -> 7. UPDATE offboarding_records: status = 'completed'
      -> 8. Publish EmployeeTerminated event
      -> Return Result.Success()
```

### Edge Cases

- **Knowledge risk assessment:** Critical employees trigger additional handover workflows.
- **Notice period tracking:** Tracked in penalties_json with expected end date.
- **Knowledge transfer bypass:** High/critical risk offboarding requires completed handover or approved bypass. Bypass is stored in `penalties_json`; penalty amount can be manual, tenant-policy driven, or zero for audit-only cases.

## Related

- [[modules/core-hr/offboarding/overview|Offboarding Overview]]
- [[modules/core-hr/employee-lifecycle/overview|Employee Lifecycle]]
- [[modules/core-hr/employee-profiles/overview|Employee Profiles]]
- [[modules/core-hr/onboarding/overview|Onboarding]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
