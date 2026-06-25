# Workflow Engine And Automation Center - End-to-End Logic

**Module:** Shared Platform
**Feature:** Workflow Engine and Automation Center
**Phase:** Phase 2 - deferred

---

## Phase 1 Boundary

Do not implement Workflow Engine or Automation Center as a Phase 1 customer-facing dependency.

Phase 1 modules must handle approvals with built-in logic:

- Time Off resolves approvers through reporting structure, permission, self-approval policy, and employee visibility.
- Overtime and attendance corrections use Time & Attendance policy/routing rules.
- Transfer, promotion, and position access use position authority plus lightweight approval request records.
- Monitoring alerts notify the recipient resolved by Monitoring Policy (default: first available responsible person from the management coverage availability chain).

Inbox may show module-owned action items, but those items are not workflow instances.

---

## Create Automation - Phase 2

```text
Customer opens Automation Center
  -> UI loads existing automations
  -> If first visit, show onboarding prompt
  -> Customer clicks Create Automation
  -> Builder captures:
       When trigger
       If conditions
       Who resolver
       Then actions
       Wait / Delay
       If still unresolved escalation resolver and action
  -> POST /api/v1/automations
  -> Validate trigger, resolver, action, permissions, and delivery options
  -> Save versioned automation definition
  -> Publish AutomationDefinitionCreated
```

This route and flow are Phase 2 only.

## Apply Template - Phase 2

```text
Customer clicks Templates
  -> GET /api/v1/automation-templates
  -> Customer selects a practical template
  -> POST /api/v1/automation-templates/{id}/apply
  -> Create editable automation definition
  -> Open builder with the template content prefilled
```

Templates are not locked. Customers can edit, disable, or delete the automation created from a template.

## Start Workflow From Trigger - Phase 2

```text
Domain event arrives, such as TimeOffRequestSubmitted or ExceptionAlertCreated
  -> AutomationTriggerHandler loads active automations for the trigger
  -> Evaluate conditions using resource context
  -> If matched:
       Create workflow instance
       Resolve first active step
       Create or reuse case conversation if configured
       Route action card through delivery router
       Schedule wait/escalation job if configured
```

Phase 1 domain events must not require this handler to complete normal approvals.

## Resolve Assignee Or Approver - Phase 2

```text
Resolver input:
  resource employee
  legal entity/department/team/position or position branch
  job level only when configured and linked
  selected permission
  configured escalation resolver
  previous workflow approver
  case conversation participants

Resolver output:
  zero, one, or many employee/user candidates

If zero candidates:
  mark step blocked
  notify automation owner
  optionally route to department owner, selected permission, specific employee,
  HR coverage assignment, or configured escalation resolver

If one candidate:
  assign step to that candidate

If many candidates:
  apply approval mode:
    only_one_required
    all_required
    sequential
```

Resolvers must use tenant-owned org structure and permission assignments. They must never check fixed role names.

For built-in Phase 1 Time Off approval when no custom workflow exists:

```text
Input:
  employee_id
  required_permission = time_off:approve

Flow:
  -> Resolve employee current position
  -> Walk positions.reports_to_position_id upward
  -> For each reporting position:
       find active occupant
       find active linked user
       verify required permission
       verify self-approval policy
  -> Assign first valid owner from management coverage order
  -> If none found:
       create a routing issue through the module-owned path
```

Do not require administrators to choose a scope policy for every permission on every role. Permission checks answer whether the action is available. Management coverage, workspace membership, project membership, legal-entity context, and resource context answer which employees, workspaces, projects, legal entities, or records are affected.

For connected-company workflows, resolver input also includes requester tenant, source tenant, target tenant, subject tenant, connection ID, and grant scope. The resolver must verify the connection is active and the grant includes the target tenant, resource type, and action before returning connected-tenant candidates.

## Cross-Company Workflow - Phase 2

```text
Cross-company trigger arrives, such as EmployeeCrossCompanyTransferRequested
  -> Load requester tenant, source tenant, target tenant, subject tenant, connection ID
  -> Verify active company connection
  -> Verify caller permission and scoped grant
  -> Create workflow instance with tenant provenance and data-sharing scope
  -> Resolve source approver and target approver
  -> Share only approved workflow evidence with target tenant
  -> Audit every action with actor tenant and source/target tenant IDs
```

## Delivery Router - Phase 2

```text
Workflow step assigned
  -> DeliveryRouter receives action card payload
  -> If Work Chat enabled:
       create or reuse case conversation
       send action card to ONEVO Chat
  -> Else:
       create Inbox item with detail panel comments/actions
  -> If Teams sync enabled and case conversation is linked:
       mirror discussion message to Teams
       include secure ONEVO link for official action
```

Teams replies can sync into the ONEVO case conversation for discussion. Approve, reject, request information, acknowledge, dismiss, escalate, and resolve actions still happen in ONEVO.

## Take Approval Action - Phase 2

```text
POST /api/v1/workflows/{instanceId}/approve
  -> Verify caller is an active assignee for the step
  -> Insert approval action with actor, comment, and timestamp
  -> Apply approval mode
  -> If step complete:
       publish WorkflowStepApproved and advance to next step, or finish workflow
  -> If workflow approved:
       publish WorkflowApproved
       source module updates resource state
  -> Write audit entry
  -> Update case conversation action card state
```

For all-required mode, the workflow remains waiting until every assigned approver approves. For only-one-required mode, the first approval completes the step. For sequential mode, the next approver is notified only after the prior approver approves.

## Delegate Current Approval - Phase 2

```text
Approver clicks Delegate on the action card
  -> Verify caller is an active assignee for the step
  -> Verify delegated employee is allowed by the workflow's resolver/scope rules
  -> Insert approval action:
       action = "delegate"
       actor_id = current approver
       delegated_to_id = selected employee
  -> Mark current workflow_step_assignment as skipped or delegated
  -> Create a new workflow_step_assignment for delegated employee
  -> Route the action card to the delegated employee through Chat or Inbox
  -> Write audit entry
```

Delegation is request-specific. Do not require a separate manager absence or acting-manager setup before approvals can move.

## Request Information - Phase 2

```text
Approver clicks Request information
  -> Write approval action
  -> Add employee or requester to case conversation if configured
  -> Send Chat or Inbox action card asking for response
  -> Pause approval timer or switch to waiting_for_info per automation settings
```

## Escalate Unresolved Item - Phase 2

```text
Wait/delay job fires
  -> Reload workflow/case status
  -> If already resolved, no-op
  -> Resolve configured escalation resolver dynamically
  -> Add escalation assignee or participant
  -> Send Chat or Inbox action card
  -> Mirror discussion to Teams if enabled
  -> Write audit entry
  -> Publish WorkflowEscalated
```

## Related

- [[modules/shared-platform/workflow-engine/overview|Overview]]
- [[Userflow/Automation/automation-center|Automation Center]]
- [[modules/shared-platform/notification-infrastructure/overview|Notification Infrastructure]]
- [[modules/work-management/chat/overview|Chat & Messaging]]
- [[modules/auth/audit-logging/overview|Audit Logging]]
