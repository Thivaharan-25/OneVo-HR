# Workflow Engine And Automation Center

**Module:** Shared Platform  
**Feature:** Workflow Engine and Automation Center  

---

## Purpose

Resource-type agnostic automation and approval engine. The same engine handles leave, overtime, attendance corrections, document approvals, expense claims, skill validations, identity verification reviews, exception alerts, requests, escalations, and follow-ups.

Automation Center is the customer-facing screen for creating and editing workflow automations. It is a first-class route, not a technical settings page. The screen normally opens into the automation builder or existing automations; templates appear only when the customer clicks Templates.

## Core Principle: Dynamic Resolvers

ONEVO must not route actions to fixed role names such as HR or CEO. Customers can create their own roles, job families, job levels, departments, teams, and permission structures, so workflow steps route through resolvers.

A resolver finds the right person dynamically based on the employee, department, team, permission, or selected rule owner.

Supported resolver types:

- Employee's reporting manager
- Employee's team lead
- Employee's department owner
- Users with selected permission
- Users in selected department
- Users in selected team
- Users in selected job level
- Specific employee
- Configured escalation owner
- Previous workflow approver
- Current case conversation participants
- Owner of connected company
- Users with selected permission in connected tenant
- Target company HR approver
- Source company manager
- Group-level reviewer across selected connected companies

Examples:

- Send to users with permission `exceptions:manage`.
- Assign to employee's reporting manager.
- Escalate to the configured escalation owner.

## Builder Model

The builder uses a simple step-by-step shape:

| Section | Meaning |
|:--------|:--------|
| When | Trigger |
| If | Conditions |
| Who | Resolver for assignee or approver |
| Then | Actions |
| Wait / Delay | Optional timing rule |
| If still unresolved | Escalation action and resolver |

Supported triggers include leave request submitted, overtime request submitted, attendance correction submitted, exception alert created, identity verification failed, agent heartbeat lost, low activity detected, excess idle detected, presence/activity mismatch detected, approval unresolved, case unresolved, and message posted in a case conversation.

Supported actions include create case conversation, send to Chat, send to Inbox, mirror to Teams if connected, notify assignee, notify employee, assign to resolver, request more information, escalate, create workflow task, add participant to case conversation, send daily summary, and mark for manager review.

Connected-company-aware actions include request cross-company approval, create cross-company case conversation, share workflow evidence with a connected tenant, create target-tenant onboarding task, and revoke shared evidence after case closure. These actions require an active company connection and scoped cross-company permission.

## Cross-Company Workflow Context

Any workflow instance that crosses company tenants must store requester tenant, source tenant, target tenant, subject tenant, actor tenant, connection ID, and data-sharing scope. Workflow routing through a connected company must stop when the connection is revoked unless an explicit completion policy allows an already-started case to finish.

## Multiple Approver Modes

When a resolver returns more than one approver, the approval step must specify an approval mode:

| Mode | Behavior | Example Use |
|:-----|:---------|:------------|
| Only one approval is required | First approval completes the step; other approvers see it as completed | Either manager has authority |
| All assigned approvers must approve | Step completes only after every assigned approver approves | Dual approval is required |
| Approve in order | Approvers receive the request sequentially | Reporting manager, then department owner |

## Unavailable Approvers

ONEVO should not require a separate manager-absence configuration module for Phase 1 approvals. When the primary approver is unavailable, the workflow handles it through the same approval engine:

- The assigned approver may use a workflow `delegate` action for that specific request.
- If the approver takes no action before `sla_deadline_at`, the workflow runs the configured unresolved/escalation path.
- The escalation resolver should usually target department owner, users with a selected permission, a specific employee, or configured escalation owner.
- Every delegated or escalated action is recorded in `approval_actions` and remains auditable.

This keeps normal leave, overtime, attendance correction, and expense approvals simple while still preventing a request from being blocked by one absent reporting manager.

## Case Conversations

Approval requests and alerts should not be handled inside normal one-to-one private chat. ONEVO creates a case conversation: a private, system-created conversation linked to one approval, alert, request, or workflow item.

A case conversation can start with:

- Assigned resolver only
- Assigned resolver plus employee
- Assigned resolver plus original requester

Participants can discuss evidence, invite another employee, approve or reject, acknowledge or dismiss, request more information, escalate, and resolve the case. Every action is audited.

## Delivery Router

The workflow engine publishes an action card and asks the delivery router where it should appear.

| Capability | Delivery |
|:-----------|:---------|
| WorkSync Chat enabled | Send action card to ONEVO Chat and create or reuse a case conversation |
| WorkSync Chat not enabled | Send action card to Inbox and use the Inbox detail panel for comments and decisions |
| Microsoft Teams sync enabled | Mirror the case conversation into the linked Teams conversation |

Teams is for discussion only. ONEVO remains the source of truth for permissions, workflow state, decisions, and audit trail. Official actions happen in ONEVO through a secure link.

## Database Tables

The approved migration direction is additive and keeps legacy workflow rows readable. New workflow definitions must use resolver fields and child assignment rows instead of fixed role targeting.

Approved migration decisions:

- Resolver configuration lives on `workflow_steps` as `resolver_type` plus `resolver_config`.
- Multiple approvers live in `workflow_step_assignments`.
- Case conversation metadata lives in Shared Platform `case_conversations` and links to WorkSync Chat `channels`.
- Delivery routing state lives in `workflow_delivery_routes`.
- Cross-company context lives as nullable provenance fields on `workflow_instances`.
- Legacy `approver_type`, `approver_role_id`, and `assigned_to_id` stay during expand-contract migration but are not used for new definitions.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/automations` | `workflows:read` | List automation/workflow definitions |
| POST | `/api/v1/automations` | `workflows:manage` | Create automation from builder |
| PATCH | `/api/v1/automations/{id}` | `workflows:manage` | Edit, enable, disable, or archive automation |
| GET | `/api/v1/automation-templates` | `workflows:read` | List practical starter templates |
| POST | `/api/v1/automation-templates/{id}/apply` | `workflows:manage` | Create editable automation from template |
| GET | `/api/v1/workflows/{resourceType}/{resourceId}` | Authenticated + `workflows:read` or workflow participant or resource-scoped viewer | Workflow or case status |
| POST | `/api/v1/workflows/{instanceId}/approve` | Authenticated + assigned approver + required module permission | Approve current assigned step |
| POST | `/api/v1/workflows/{instanceId}/reject` | Authenticated + assigned approver + required module permission | Reject current assigned step |
| POST | `/api/v1/workflows/{instanceId}/request-info` | Authenticated + assigned participant + required module permission | Request more information |
| POST | `/api/v1/cases/{caseId}/resolve` | Authenticated + case participant with resolve rights | Resolve a case conversation |

`workflows:manage` controls workflow configuration. Runtime approve/reject actions use the resource module permission configured on the workflow step, such as `leave:approve` or `expense:approve`, plus current assignment, case participation, and tenant/resource checks. `Authenticated` by itself only means the caller is logged in.

## Related

- [[Userflow/Automation/automation-center|Automation Center]]
- [[modules/shared-platform/notification-infrastructure/overview|Notification Infrastructure]]
- [[modules/work-management/chat/overview|Chat & Messaging]]
- [[modules/work-management/chat/teams-sync/end-to-end-logic|Teams Chat Sync]]
- [[modules/shared-platform/compliance-governance/overview|Compliance Governance]]
- [[modules/shared-platform/company-connections/overview|Company Connections]]
- [[frontend/architecture/sidebar-nav|Sidebar Navigation]]
- [[frontend/cross-cutting/authorization|Authorization]]
