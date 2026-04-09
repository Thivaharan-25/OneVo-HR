# Disciplinary Actions — End-to-End Logic

**Module:** Grievance
**Feature:** Disciplinary Actions

---

## Issue Disciplinary Action

### Flow

```
POST /api/v1/disciplinary
  -> DisciplinaryController.Issue(IssueDisciplinaryCommand)
    -> [RequirePermission("grievance:manage")]
    -> DisciplinaryService.IssueAsync(command, ct)
      -> 1. Validate employee exists
      -> 2. Validate action_type: verbal_warning, written_warning, suspension, termination
      -> 3. INSERT into disciplinary_actions
         -> Link to grievance_id if applicable
         -> issued_by_id = current user
      -> 4. Notify employee
      -> 5. If action_type = 'termination':
         -> Trigger offboarding workflow via core-hr
      -> Return Result.Success(actionDto)
```

## Get Disciplinary History

### Flow

```
GET /api/v1/disciplinary/{employeeId}
  -> DisciplinaryController.GetHistory(employeeId)
    -> [RequirePermission("grievance:read")]
    -> DisciplinaryService.GetHistoryAsync(employeeId, ct)
      -> Query disciplinary_actions ORDER BY effective_date DESC
      -> Return Result.Success(historyDtos)
```

## Related

- [[modules/grievance/disciplinary-actions/overview|Disciplinary Actions]] — feature overview
- [[modules/grievance/grievance-cases/overview|Grievance Cases]] — grievance case that may precede the action
- [[backend/messaging/event-catalog|Event Catalog]] — events emitted on action issuance and acknowledgement
- [[backend/messaging/error-handling|Error Handling]] — NotFoundException, BusinessRuleException patterns
