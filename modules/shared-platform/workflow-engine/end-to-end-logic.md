# Workflow Engine — End-to-End Logic

**Module:** Shared Platform
**Feature:** Generic Workflow Engine

---

## Create Workflow Instance

### Flow

```
Called by modules (leave, expense, overtime, documents):
  -> IWorkflowService.CreateInstanceAsync(resourceType, resourceId, ct)
    -> 1. Find workflow_definition for resource_type
    -> 2. INSERT into workflow_instances
       -> status = 'in_progress', current_step_order = 1
    -> 3. Resolve first step approver:
       -> reporting_manager: lookup from employee hierarchy
       -> department_head: lookup from department
       -> role: find user with matching role
       -> specific_user: use configured user_id
    -> 4. INSERT into workflow_step_instances
       -> assigned_to_id = resolved approver
       -> sla_deadline_at = now + sla_hours
    -> 5. Notify approver via notifications
    -> Return workflow_instance_id
```

## Take Action (Approve/Reject)

### Flow

```
POST /api/v1/workflows/{instanceId}/approve
  -> WorkflowController.Approve(instanceId, ApproveCommand)
    -> [Authenticated]
    -> WorkflowService.ApproveStepAsync(instanceId, command, ct)
      -> 1. Verify caller is assigned_to for current step
      -> 2. INSERT into approval_actions (action = 'approve')
      -> 3. UPDATE current step: status = 'approved'
      -> 4. If next step exists:
         -> Advance: UPDATE workflow_instance current_step_order++
         -> Resolve next step approver
         -> CREATE new workflow_step_instance
      -> 5. If no next step:
         -> UPDATE workflow_instance status = 'completed'
         -> Publish WorkflowCompleted event with outcome = 'approved'
         -> Module handles completion (e.g., leave status -> approved)
      -> Return Result.Success()

```

## Related

- [[modules/shared-platform/workflow-engine/overview|Overview]]
- [[modules/shared-platform/notification-infrastructure/overview|Notification Infrastructure]]
- [[modules/shared-platform/compliance-governance/overview|Compliance Governance]]
- [[modules/auth/audit-logging/overview|Audit Logging]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
