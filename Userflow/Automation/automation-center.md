# Automation Center

**Area:** Automation Center (`/automation`)  
**Trigger:** Customer opens Automation Center or clicks Create Automation  
**Required Permission(s):** `workflows:read`, `workflows:manage` to create/edit  
**Related Permissions:** Permission selectors can reference any tenant permission key, such as `exceptions:manage`, but Automation Center visibility and edits remain governed by `workflows:read` and `workflows:manage`.

---

## Purpose

Automation Center lets customers create workflows that route approvals, alerts, requests, and follow-ups to the right people. Automations can create private case conversations, deliver action cards through Chat or Inbox, mirror discussions to Microsoft Teams, and escalate unresolved items using dynamic resolvers instead of fixed roles.

Automation Center is a first-class product area. It is not hidden inside technical settings because automation is central to reducing manual management work.

---

## Core Rules

1. Automation routing must use resolvers, not hard-coded role names such as HR, CEO, or department head.
2. Templates are starter automations only. After selecting a template, the customer can edit, disable, or delete it.
3. The normal screen opens into automation creation and editing. Templates appear only when the customer clicks Templates.
4. Approval requests and alerts use case conversations instead of normal one-to-one private chat.
5. Official approval, rejection, acknowledgement, escalation, and resolve actions happen inside ONEVO and are audited.
6. Microsoft Teams is discussion-only. Teams replies can sync back into ONEVO, but Teams does not decide the workflow state.

---

## Screen Structure

Header:

- Title: Automation Center
- Top right actions: Templates, Create Automation

Main area:

- If no automation exists, show "Create your first automation" with a Create Automation action.
- If automations exist, show a focused list or cards with status, trigger, assigned resolver, last run, and unresolved count.
- Avoid tab-heavy layouts. Use one focused page with builder, list, or template picker states.

First-time onboarding prompt:

```text
Start faster with ready-made automations, or build your own from scratch.

[View Templates] [Create Automation]
```

---

## Builder Flow

### Step 1: Create Automation
- **UI:** Customer clicks Create Automation.
- **Result:** Builder opens directly.

Builder sections:

| Section | What Customer Configures |
|:--------|:-------------------------|
| When | Trigger |
| If | Conditions |
| Who | Resolver for assignee or approver |
| Then | Actions |
| Wait / Delay | Optional timing rule |
| If still unresolved | Escalation resolver and action |

Example:

```text
When:
Exception alert is created

If:
Alert type is Low Activity
Count is more than 2
Within 5 working days

Then:
Create case conversation
Assign to employee's reporting manager
Send to Chat, or Inbox if Chat is not enabled

If not resolved after:
2 working days

Then:
Escalate to configured escalation owner
```

### Step 2: Select Trigger

Supported triggers:

- Leave request submitted
- Overtime request submitted
- Attendance correction submitted
- Exception alert created
- Identity verification failed
- Agent heartbeat lost
- Low activity detected
- Excess idle detected
- Presence/activity mismatch detected
- Approval unresolved
- Case unresolved
- Message posted in case conversation

### Step 3: Add Conditions

Conditions can check request type, alert type, severity, count, time window, working-day calendar, employee, department, team, job level, permission, case state, previous approver, or integration state.

### Step 4: Choose Resolver

Supported resolvers:

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
- Case conversation participants

Examples:

- Send to users with permission `exceptions:manage`.
- Send to the configured escalation owner.
- Assign to employee's reporting manager.

### Step 5: Configure Actions

Supported actions:

- Create case conversation
- Send to Chat
- Send to Inbox
- Mirror to Teams if connected
- Notify assignee
- Notify employee
- Assign to resolver
- Request more information
- Escalate
- Create workflow task
- Add participant to case conversation
- Send daily summary
- Mark for manager review

### Step 6: Multiple Approver Mode

When a resolver returns multiple approvers, the approval step asks:

- Only one approval is required
- All assigned approvers must approve
- Approve in order

Use "Only one approval is required" when either approver has authority and the company wants fast approvals. Once one manager approves, the request is completed and other assigned managers see it as already completed.

Use "All assigned approvers must approve" when dual approval is required. Example: Manager A approves, then the status becomes "Waiting for Manager B"; only after Manager B approves is the request approved.

Use "Approve in order" when hierarchy-based approval is required. Example: reporting manager first, then department owner.

---

## Case Conversations

A case conversation is a private, system-created conversation linked to one approval, alert, request, or workflow item. It behaves like a private thread/channel, not a normal DM.

Examples:

- Leave request case
- Low activity alert case
- Attendance correction case
- Identity verification case
- Overtime approval case
- Document approval case

The automation decides who starts in the case:

- Assigned resolver only
- Assigned resolver plus employee
- Assigned resolver plus original requester
- Any additional participants from the rule

Inside a case conversation, users can discuss the issue, view evidence, invite another employee, approve or reject, acknowledge or dismiss, request more information, escalate, and resolve the case. Every action is audited.

---

## Delivery Router

The delivery router decides where the action card appears.

| Tenant Capability | Delivery Behavior |
|:------------------|:------------------|
| WorkSync Chat enabled | Send action card to ONEVO Chat and create or reuse a case conversation |
| WorkSync Chat not enabled | Send action card to Inbox and use the Inbox detail panel for comments and decisions |
| Microsoft Teams sync enabled | Mirror the ONEVO case conversation into the linked Teams conversation |

ONEVO remains the source of truth. Teams is used for discussion only. No Teams bot, Teams-native approval buttons, or text command parsing is required.

Example Teams message:

```text
Leave request from Nimal Perera
Dates: May 10-12
Status: Waiting for approval

Reply here to discuss.
Open ONEVO to approve or reject:
[Open Request]
```

---

## Template Picker

Templates appear only after the customer clicks Templates.

### Recommended Approval Setup

Purpose: Creates standard approval automations for common HR requests.

Includes leave request, attendance correction, overtime request, and remote work location request routing to employee's reporting manager, case conversation creation, approver notification, and escalation if unresolved after configured working days.

Best for most companies that want approval requests to flow automatically without designing every rule manually.

### Low-Noise Workforce Alerts

Purpose: Reduces notification noise. Most minor issues are logged or summarized instead of interrupting managers instantly.

Includes low-severity alert logging, daily summaries, repeated warning notifications, immediate critical alert notifications, and unresolved critical alert escalation after configured working hours.

Best for companies that want visibility without disturbing employees and managers all day.

### High-Control Workforce Alerts

Purpose: Creates faster escalation for companies that need stricter workforce monitoring.

Includes low activity notifications, excess idle case conversations, presence without laptop activity cases, agent heartbeat gap notifications, and quick escalation to configured escalation owner.

Best for remote-work risk, compliance, or operational sensitivity.

### Repeated Issue Review

Purpose: Automatically creates a review case when the same employee triggers repeated issues.

Editable settings: alert types included, repeat count, time window, assignee resolver, employee inclusion, escalation delay, and escalation resolver.

Best for managers who do not want to react to every single alert but need action when a pattern appears.

### Attendance And Activity Mismatch

Purpose: Detects when attendance records and device activity do not match.

Includes clocked-in/no-laptop-activity cases, biometric-entry/device-inactive notifications, activity-outside-presence flags, and unresolved mismatch escalation.

Best for office or hybrid companies using biometric attendance and device monitoring together.

### Meeting Time Review

Purpose: Identifies excessive meeting time or passive meeting-heavy days.

Includes meeting-time summaries, repeated high-meeting-time manager notifications, and high-meeting-time plus low-activity case creation.

Best for companies concerned about meeting overload and hidden idle time.

### Identity Verification Review

Purpose: Routes failed or missed identity checks to the correct reviewer.

Includes failed login photo verification cases, missed scheduled identity check notifications, repeated verification failure escalation, and permitted follow-up photo requests.

Best for remote or hybrid companies using camera-based identity verification.

### Escalate Unresolved Approvals

Purpose: Prevents leave, overtime, attendance corrections, and other approvals from getting stuck.

Includes reminders, escalation to next resolver, and second-delay escalation to configured owner.

Best for companies where managers often delay approvals.

### Daily Manager Summary

Purpose: Sends managers a digest instead of constant individual notifications.

Includes pending approvals, new alerts, unresolved cases, team attendance issues, and high-priority exceptions.

Best for companies that want managers to review workforce issues once or twice per day.

### Build From Scratch

Purpose: Allows the customer to create any automation manually using the builder.

---

## Events Triggered

- `AutomationDefinitionCreated`
- `AutomationTemplateApplied`
- `AutomationTriggered`
- `CaseConversationCreated`
- `WorkflowStepAssigned`
- `WorkflowApprovalActionRecorded`
- `WorkflowEscalated`
- `CaseResolved`

## Related Flows

- [[Userflow/Leave/leave-approval|Leave Approval]]
- [[Userflow/Notifications/inbox|Inbox]]
- [[Userflow/Chat/chat-overview|Chat Overview]]
- [[Userflow/Work-Management/workspace-teams-sync|Workspace Teams Sync]]
- [[Userflow/Exception-Engine/alert-review|Alert Review]]

## Module References

- [[modules/shared-platform/workflow-engine/overview|Workflow Engine]]
- [[modules/shared-platform/notification-infrastructure/overview|Notification Infrastructure]]
- [[modules/work-management/chat/overview|Chat & Messaging]]
- [[modules/work-management/chat/teams-sync/end-to-end-logic|Teams Chat Sync]]
