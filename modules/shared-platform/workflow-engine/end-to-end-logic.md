# Workflow Engine And Automation Center - End-to-End Logic

**Module:** Shared Platform  
**Feature:** Workflow Engine and Automation Center

---

## Create Automation

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

## Apply Template

```text
Customer clicks Templates
  -> GET /api/v1/automation-templates
  -> Customer selects a practical template
  -> POST /api/v1/automation-templates/{id}/apply
  -> Create editable automation definition
  -> Open builder with the template content prefilled
```

Templates are not locked. Customers can edit, disable, or delete the automation created from a template.

## Start Workflow From Trigger

```text
Domain event arrives, such as LeaveRequestSubmitted or ExceptionAlertCreated
  -> AutomationTriggerHandler loads active automations for the trigger
  -> Evaluate conditions using resource context
  -> If matched:
       Create workflow instance
       Resolve first active step
       Create or reuse case conversation if configured
       Route action card through delivery router
       Schedule wait/escalation job if configured
```

## Resolve Assignee Or Approver

```text
Resolver input:
  resource employee
  department/team/job level
  selected permission
  configured escalation owner
  previous workflow approver
  case conversation participants

Resolver output:
  zero, one, or many employee/user candidates

If zero candidates:
  mark step blocked
  notify automation owner
  optionally route to configured escalation owner

If one candidate:
  assign step to that candidate

If many candidates:
  apply approval mode:
    only_one_required
    all_required
    sequential
```

Resolvers must use tenant-owned org structure and permission assignments. They must never check fixed role names.

## Delivery Router

```text
Workflow step assigned
  -> DeliveryRouter receives action card payload
  -> If WorkSync Chat enabled:
       create or reuse case conversation
       send action card to ONEVO Chat
  -> Else:
       create Inbox item with detail panel comments/actions
  -> If Teams sync enabled and case conversation is linked:
       mirror discussion message to Teams
       include secure ONEVO link for official action
```

Teams replies can sync into the ONEVO case conversation for discussion. Approve, reject, request information, acknowledge, dismiss, escalate, and resolve actions still happen in ONEVO.

## Take Approval Action

```text
POST /api/v1/workflows/{instanceId}/approve
  -> Verify caller is an active assignee for the step
  -> Insert approval action with actor, comment, and timestamp
  -> Apply approval mode
  -> If step complete:
       advance to next step or complete workflow
  -> If workflow complete:
       publish WorkflowCompleted with outcome
       source module updates resource state
  -> Write audit entry
  -> Update case conversation action card state
```

For all-required mode, the workflow remains waiting until every assigned approver approves. For only-one-required mode, the first approval completes the step. For sequential mode, the next approver is notified only after the prior approver approves.

## Request Information

```text
Approver clicks Request information
  -> Write approval action
  -> Add employee or requester to case conversation if configured
  -> Send Chat or Inbox action card asking for response
  -> Pause approval timer or switch to waiting_for_info per automation settings
```

## Escalate Unresolved Item

```text
Wait/delay job fires
  -> Reload workflow/case status
  -> If already resolved, no-op
  -> Resolve escalation owner dynamically
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
