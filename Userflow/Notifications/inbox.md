# Inbox

The personal action center - everything waiting for YOUR decision in one place. Inbox is also the fallback delivery surface for workflow action cards when WorkSync Chat is not enabled.

## Preconditions

- User is authenticated
- User has `inbox:read` permission

## Flow Steps

### Step 1: Open Inbox
- **Navigate:** Sidebar -> Inbox (badge shows unresolved count)
- **UI:** Single-column list sorted by urgency then date

### Step 2: Review Items
- **UI:** Each item shows: icon, title, source (who submitted), timestamp, action buttons
- **Item types:**
  - Leave requests -> Approve / Reject
  - Expense claims -> Approve / Reject / Request Info
  - Skill validation requests -> Validate / Adjust & Validate / Reject
  - Attendance correction requests -> Approve / Reject
  - Overtime requests -> Approve / Reject
  - Remote location change requests -> Approve / Reject
  - Exception alert cases -> Acknowledge / Dismiss / Escalate / Resolve
  - Identity verification cases -> Confirm / Request follow-up photo / Escalate
  - Assigned tasks -> View / Complete
  - Mentions -> View context
  - Automation follow-ups -> Review / Resolve / Escalate

### Step 2a: Skill Validation Request
- **Trigger:** Employee declares a skill from My Profile -> Skills.
- **Route:** Direct manager receives the Inbox item if they have `skills:validate`.
- **UI:** Item shows employee name, skill name, category, self-rated proficiency, years of experience, and employee notes.
- **Actions:** Validate, Adjust & Validate, Reject. Reject requires a reason.

### Step 2b: Remote Location Change Request
- **Trigger:** Employee opens Employee Settings -> Remote Work Location -> Request Location Change and submits a reason.
- **Route:** Reporting manager receives the Inbox item.
- **UI:** Item shows employee name, current remote workplace status, requested change reason, and submitted time.
- **Actions:** Approve or Reject. If approved, the employee can re-capture their remote work location profile on the next remote clock-in.

### Step 3: Take Action
- **UI:** Click action button -> inline confirmation or slide-over detail panel
- If the item came from Automation Center, the detail panel shows the case conversation comments and the audited decision actions configured by the automation.
- Bulk approve/reject available for similar items (e.g., 5 leave requests)
- Completed items move to "Done" section (collapsible, below active items)

### Step 4: Empty State
- **UI:** "You're all caught up" with illustration. No pending items.

## Distinction from Notification Bell

- **Inbox** = actionable (needs your decision)
- **Bell** = informational (FYI updates, no action needed)
- **Chat case conversation** = preferred discussion surface when WorkSync Chat is enabled

If WorkSync Chat is enabled, workflow action cards should normally appear in Chat case conversations. If Chat is not enabled, the same action card appears in Inbox and comments remain in the Inbox detail panel.

## Related Flows

- [[Userflow/Leave/leave-approval|Leave Approval]]
- [[Userflow/Expense/expense-approval|Expense Approval]]
- [[Userflow/Skills-Learning/skill-assessment|Skill Assessment]]
- [[Userflow/Workforce-Intelligence/work-location-compliance|Work Location Compliance]]
- [[Userflow/Automation/automation-center|Automation Center]]
- [[Userflow/Notifications/notification-view|Notification View]]

## Module References

- [[modules/notifications/overview|Notifications Module]]
