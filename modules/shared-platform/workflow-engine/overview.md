# Workflow Engine And Automation Center

**Module:** Shared Platform
**Feature:** Workflow Engine and Automation Center
**Phase:** Phase 2 - deferred
**Phase 1 Customer Route:** none

---

## Phase 1 Boundary

Workflow Engine and Automation Center are not active Phase 1 dependencies. Do not require workflow builder setup, automation templates, custom workflow definitions, or Automation Center screens for Phase 1 delivery.

Phase 1 approvals and routing are module-owned and use:

- Org Structure management coverage
- owner order from Primary owner and Backup owners
- granted action permissions
- active Company/legal entity context
- lightweight request records
- Notifications and Inbox

This applies to Time Off, overtime, attendance corrections, transfer, promotion, position-derived access, onboarding/offboarding checklist work, and monitoring alerts.

No Phase 1 behavior should hard-code job titles such as CEO or HR. Approval depends on the target employee, Org Structure management coverage, owner order, required permission, self-approval rules, and active Company/legal entity context.

---

## Purpose

This document is retained as the Phase 2 design reference for a resource-type agnostic automation and approval engine. In Phase 2, the same engine may handle Time Off, overtime, attendance corrections, document approvals, expense claims, skill validations, identity verification reviews, exception alerts, requests, escalations, and follow-ups.

Automation Center is Phase 2 only. It may become the customer-facing screen for creating and editing workflow automations, but it must not appear as a Phase 1 top-level customer route.

## Core Principle: Dynamic Resolvers

ONEVO must not route actions to fixed role names such as HR or CEO. Customers can create their own roles, job families, job levels, departments, teams, and permission structures, so workflow steps route through resolvers.

A resolver finds the right person dynamically based on the employee, department, team, permission, or selected rule owner.

Supported resolver types for Phase 2:

- First eligible approver in employee's position reporting chain
- Employee's reporting manager
- Employee's team lead
- Employee's department owner
- Users with selected permission
- Users in selected department
- Users in selected team
- Users in selected position or position branch
- Users in selected job level, only when job levels are configured and linked for the tenant
- Specific employee
- Configured escalation resolver
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
- For a custom Phase 2 workflow, route to users in a selected department, team, or position branch.
- Escalate to the configured escalation resolver only when the custom workflow explicitly chooses that route.

## Builder Model

The Phase 2 builder uses a simple step-by-step shape:

| Section | Meaning |
|:--------|:--------|
| When | Trigger |
| If | Conditions |
| Who | Resolver for assignee or approver |
| Then | Actions |
| Wait / Delay | Optional timing rule |
| If still unresolved | Escalation action and resolver |

Supported triggers may include Time Off request submitted, overtime request submitted, attendance correction submitted, exception alert created, identity verification failed, agent heartbeat lost, low activity detected, excess idle detected, presence/activity mismatch detected, approval unresolved, case unresolved, and message posted in a case conversation.

Supported actions may include create case conversation, send to Chat, send to Inbox, mirror to Teams if connected, notify assignee, notify employee, assign to resolver, request more information, escalate, create workflow task, add participant to case conversation, send daily summary, and mark for manager review.

Connected-company-aware actions may include request cross-company approval, create cross-company case conversation, share workflow evidence with a connected tenant, create target-tenant onboarding task, and revoke shared evidence after case closure. These actions require an active company connection and scoped cross-company permission.

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

ONEVO should not require a separate manager-absence configuration module for Phase 1 approvals. Phase 1 handles approver fallback through module-owned routing and Notifications.

In Phase 2, the workflow engine may handle unavailable approvers through the same approval engine:

- The assigned approver may use a workflow `delegate` action for that specific request.
- If the approver takes no action before `sla_deadline_at`, the workflow runs the configured unresolved/escalation path.
- The escalation resolver should usually target department owner, users with a selected permission, a specific employee, management coverage resolver, or configured escalation resolver.
- Every delegated or escalated action is recorded in `approval_actions` and remains auditable.

## Default Approval Fallback

Custom workflow definitions are not required for Phase 1. When a module requires approval in Phase 1, the module must choose an explicit built-in resolver.

For Time Off, the Phase 1 built-in resolver uses management coverage:

1. Resolve the request employee's current Company, position, and department.
2. Try position coverage owners in owner order.
3. If no valid owner exists, try department coverage owners in owner order.
4. If no valid owner exists, try company-wide coverage owners in owner order.
5. Return the first candidate who is an active employee, has an active user account, has the required action permission such as `time_off:approve`, and is allowed by self-approval policy.
6. If no valid candidate is found, create a routing issue. Do not require Workflow Engine.

Do not expose per-permission employee-coverage setup as a required role-creation step. Permission grants define the action capability; management coverage, workspace membership, project membership, and legal-entity context define where that action can operate.

## Case Conversations

Case conversations are Phase 2. Approval requests and alerts should not require case conversations in Phase 1.

In Phase 2, ONEVO may create a case conversation: a private, system-created conversation linked to one approval, alert, request, or workflow item.

A case conversation can start with:

- Assigned resolver only
- Assigned resolver plus employee
- Assigned resolver plus original requester

Participants can discuss evidence, invite another employee, approve or reject, acknowledge or dismiss, request more information, escalate, and resolve the case. Every action is audited.

## Delivery Router

The delivery router is Phase 2 workflow infrastructure. Phase 1 module-owned actions can still deliver to Notifications and Inbox directly.

In Phase 2, the workflow engine publishes an action card and asks the delivery router where it should appear.

| Capability | Delivery |
|:-----------|:---------|
| Work Chat enabled | Send action card to ONEVO Chat and create or reuse a case conversation |
| Work Chat not enabled | Send action card to Inbox and use the Inbox detail panel for comments and decisions |
| Microsoft Teams sync enabled | Mirror the case conversation into the linked Teams conversation |

Teams is for discussion only. ONEVO remains the source of truth for permissions, workflow state, decisions, and audit trail. Official actions happen in ONEVO through a secure link.

## Database Tables

The approved Phase 2 migration direction is additive and keeps legacy workflow rows readable. New workflow definitions must use resolver fields and child assignment rows instead of fixed role targeting.

Approved migration decisions:

- Resolver configuration lives on `workflow_steps` as `resolver_type` plus `resolver_config`.
- Multiple approvers live in `workflow_step_assignments`.
- Case conversation metadata lives in Shared Platform `case_conversations` and links to Work Chat `channels`.
- Delivery routing state lives in `workflow_delivery_routes`.
- Cross-company context lives as nullable provenance fields on `workflow_instances`.
- Legacy `approver_type`, `approver_role_id`, and `assigned_to_id` stay during expand-contract migration but are not used for new definitions.

## Deferred API Endpoints

The following API surface is Phase 2 only and must not be exposed in the Phase 1 customer app:

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

`workflows:manage` controls workflow configuration. Runtime approve/reject actions use the resource module permission configured on the workflow step, such as `time_off:approve` or `expense:approve`, plus current assignment, case participation, and tenant/resource checks. `Authenticated` by itself only means the caller is logged in.

## Related

- [[Userflow/Automation/automation-center|Automation Center]]
- [[modules/shared-platform/notification-infrastructure/overview|Notification Infrastructure]]
- [[modules/work-management/chat/overview|Chat & Messaging]]
- [[modules/work-management/chat/teams-sync/end-to-end-logic|Teams Chat Sync]]
- [[frontend/architecture/sidebar-nav|Sidebar Navigation]]
- [[frontend/cross-cutting/authorization|Authorization]]
