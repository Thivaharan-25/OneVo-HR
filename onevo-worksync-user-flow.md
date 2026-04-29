# OneVo WorkSync — User Flow (System Behaviour Reference)

> **Purpose:** This document describes how the system behaves from start to end, from the perspective of a user moving through the platform. It is written for AI-assisted code generation. Every section maps to a discrete system behaviour — read it as "when the user does X, the system does Y."

---

## Phase 1 — Authentication

**Entry point:** User opens the app for the first time or after session expiry.

### 1.1 Register
- User submits email and password.
- System creates an account and sends a verification email.
- User cannot proceed until email is verified.
- After verification, the user is redirected to workspace selection.

### 1.2 Login
- User submits email and password (or OAuth via Google/GitHub).
- System validates credentials and creates a session scoped to the selected workspace.
- If MFA is enabled, system prompts for the second factor before granting access.
- On success, a session token is issued and stored on the client.

### 1.3 Session & security
- Every request carries the session token.
- Sessions expire after inactivity. On expiry, the user is redirected to login.
- All auth events (login, logout, failed attempts) are written to an audit log.
- Password reset is token-based with expiry.

---

## Phase 2 — Workspace & Organisation Setup

**Entry point:** After login, user lands on workspace selection screen.

### 2.1 Workspace selection
- A user can belong to multiple workspaces.
- User selects the workspace they want to enter.
- Each workspace is a fully isolated boundary — separate projects, teams, roles, and billing.

### 2.2 Role & permissions
- Inside a workspace, every user has a role (Admin, Manager, Team Lead, Developer, Viewer).
- Permissions are defined per role. The system enforces them on every action.
- Access policies can be configured at workspace level (e.g. SSO enforcement, session duration).

### 2.3 Organisation structure
- Workspace is divided into Departments.
- Each Department contains Teams.
- Teams have members with specific team-level roles.
- Users can belong to multiple teams across one workspace.

### 2.4 Inviting users
- Admin sends an invite by email with a specified role.
- Invite has an expiry. If expired, it must be resent.
- Accepting the invite adds the user to the workspace with the assigned role.

---

## Phase 3 — My Space (Personal Hub)

**Entry point:** After entering a workspace, every user lands on their personal My Space.

> My Space is scoped entirely to the individual user. It does not show team-level data directly — it pulls the user's own tasks, goals, and events from all frameworks into one view.

### 3.1 Calendar view
- The central feature of My Space.
- Displays all events relevant to the user in one unified calendar: task deadlines, meetings, goal milestones, reminders, and availability blocks.
- User can switch between day, week, and month views.
- Clicking an event navigates to the relevant task, meeting, or goal.

### 3.2 Personal task board
- All tasks assigned to this user across any project appear here automatically.
- Displayed as a Kanban board with columns the user can configure.
- User can re-prioritise, add notes, and track their own progress without leaving My Space.
- Status changes here sync back to the project-level board.

### 3.3 To-dos
- Lightweight personal to-do items not linked to any project.
- User creates, completes, and deletes them freely.
- Can be set to repeat (daily, weekly, monthly).
- Appear in the Calendar view when a due date is set.

### 3.4 Goals (OKR)
- User views their assigned Objectives and Key Results.
- Can log check-ins and update progress directly.
- Goal milestones appear in the Calendar view.

### 3.5 Activity log
- A chronological log of every action the user has taken across the workspace.
- Useful for reviewing what was done and when.

---

## Phase 4 — Project Management

**Entry point:** Manager or Admin creates a project from the workspace sidebar.

### 4.1 Project creation
- Project Manager creates a project with name, status, and settings (timezone, working days, default priority).
- Adds members and assigns roles within the project.
- Creates Epics (high-level themes) and Milestones (target dates) to structure the work.

### 4.2 Sprint planning
- Team Lead receives the project and creates a Sprint with a start date, end date, and goal.
- Uses the visual board planner to break the sprint into tasks.
- Can define a roadmap across multiple sprints and set version/release targets.

### 4.3 Task creation & assignment
- Team Lead creates tasks inside the sprint.
- Each task has: title, description, priority, status, due date.
- Tasks can have sub-items (checklist), dependencies on other tasks, and labels.
- Documents and files are attached to tasks for context.
- Task is assigned to one or more developers.

### 4.4 Task lands in developer's My Space
- The moment a task is assigned, it automatically appears in the developer's personal task board.
- The due date appears in the developer's Calendar view.
- Developer receives a notification.

---

## Phase 5 — Task Execution

**Entry point:** Developer opens their My Space and picks up an assigned task.

### 5.1 Developer starts work
- Developer moves the task to "In Progress" on their personal board or the project board.
- Status syncs across both views instantly.
- Developer can start a timer to log time against the task.

### 5.2 Collaboration on task
- Developer adds comments to the task. Can mention teammates with @mention, which triggers a notification.
- Files and attachments are uploaded directly to the task.
- If a bug is found during work, a Bug Report is created and linked to the task, with reproduction steps and severity.

### 5.3 Checklist & dependencies
- Developer works through the checklist items on the task.
- If the task depends on another task, the system shows the dependency status. A blocked task cannot move to Done while its dependency is incomplete.

### 5.4 Time logging
- Developer logs time manually or stops the running timer.
- Time entries roll up into Timesheets reviewed by managers at end of week/month.

### 5.5 Task submission
- When work is complete, developer submits the task with notes and any deliverable files.
- Submission creates an approval request for the Team Lead or Manager.

### 5.6 Approval flow
- Approver receives a notification and opens the submission.
- Approver can leave a comment and either Approve or Reject.
- If approved: task status becomes Done. Time log is finalised.
- If rejected: task is reopened. A reopen log records the reason. Developer is notified and resumes work.

---

## Phase 6 — Chat & AI Automation

**Entry point:** User opens the Chat section from the workspace sidebar.

> This is the most distinctive part of the system. Chat is not just messaging — it is an action layer. The AI layer sits on top of messages and converts conversations into project actions automatically.

### 6.1 Group channel
- Every workspace has a group channel.
- All workspace members can post messages, react with emoji, and share attachments.
- Messages have read receipts.

### 6.2 Direct messages
- Users can open 1-on-1 DMs or create small group DMs.
- DMs are workspace-scoped — they exist within the workspace context.

### 6.3 Tag-based AI automation (standard users)

This is the standard flow for triggering automation from chat.

**Step-by-step:**

1. User types a message containing a tag and an @mention.
   - Example: `@john #task Please design the homepage banner by Friday`
2. AI detects the tag type (`#task`, `#issue`, `#report`, `#motion`, `#decision`).
3. AI checks whether all required fields are present:
   - For `#task`: title, assignee, due date
   - For `#report`: report type, target user or channel
4. If any field is missing, the system shows a popup prompt inline in chat, asking only for the missing field. User fills it without leaving the conversation.
5. Once all fields are collected, the system shows a confirmation suggestion card: "Create task: Design homepage banner, assigned to John, due Friday — Accept?"
6. User clicks Accept.
7. The task is created in the Project Management framework and assigned. No form-filling. No screen switching.
8. The tagged message appears in the Chat Reminder section for both the sender and the assignee.

### 6.4 Chat Reminder

The Chat Reminder is a dedicated section inside Chat that tracks all tagged messages.

**Normal user view:**
- Shows two lists: tags they created, and tags where they were mentioned/assigned.
- Each item has a status: To-Do / In Progress / Done.
- Changing the status here automatically updates the corresponding Kanban board column. This is the 2-way sync.

**Group Admin view:**
- Admin sees all tagged messages from all members in the group.
- Can filter by user, status, or date to track team progress without opening the project board.

### 6.5 Premium AI automation (paid workspaces)

For premium workspaces, the AI reads all messages passively — no tags required.

**How it works:**
1. User sends a normal message: `"I'll finish the marketing report by tomorrow afternoon."`
2. AI analyses the message in the background and detects task intent.
3. AI extracts: what (marketing report), who (the sender), when (tomorrow afternoon).
4. AI auto-creates the task in the project framework without asking the user.
5. A subtle notification confirms the task was created. User can undo if needed.

### 6.6 Slack sync (integration)
- If the workspace connects Slack, all Slack messages are mirrored into WorkSync in real time.
- Users working in Slack do not need to switch tools — the message history is unified.
- Slack itself is not modified by WorkSync.

---

## Phase 7 — Documents

**Entry point:** From the sidebar or directly from a task.

### 7.1 Create & manage documents
- Users create documents inside the platform (not an external link).
- Documents are versioned — every save creates a new version, previous versions are accessible.
- Documents have a status (Draft, In Review, Approved, Archived).
- Documents are attached to tasks, providing context alongside the work.

### 7.2 Document approval
- User sends a document for internal review.
- Approver is notified, reviews the document, and leaves comments.
- Approver approves or requests changes.
- Approved documents are marked and locked from further edits unless re-opened.

### 7.3 Wiki
- Each project has a Wiki section for persistent knowledge (how-tos, architecture notes, team agreements).
- Wiki pages are versioned and editable by project members.

---

## Phase 8 — Notifications & Reminders

**Entry point:** Triggered automatically by system events or set manually by the user.

### 8.1 Notifications
- Every key event triggers a notification: task assigned, status changed, comment added, approval requested, deadline approaching.
- Delivered via in-app alert and email.
- Push notifications are supported for mobile.
- Users configure which events they want to be notified about, and on which channel.
- Digest mode: instead of one notification per event, user gets a single daily/weekly summary.

### 8.2 Reminders
- Users set reminders against tasks, events, or deadlines.
- Reminders fire at the specified time via the configured delivery channel.
- Reminders can be snoozed — a snooze log records when and by how long.
- Workspace Admins can configure standard reminder templates (e.g. "daily standup reminder at 9am").

---

## Phase 9 — Reports & Analytics

**Entry point:** Manager or Admin opens the Analytics section from the sidebar.

### 9.1 Dashboards
- Workspace owners and managers build dashboards with chart widgets.
- KPI targets are set and progress is tracked over time.
- Dashboards can be shared with specific team members or made workspace-wide.
- Point-in-time snapshots are saved automatically for trend analysis.

### 9.2 Saved views
- Teams create filtered views of the project board (e.g. "All open bugs in Sprint 3 assigned to backend team").
- Views can be saved and shared. Used for standup meetings and status reviews.

### 9.3 Reports
- Sprint velocity reports show planned vs completed points per sprint.
- Time reports show hours logged per user, per task, per project.
- Resource allocation reports show who is over/under capacity.
- All reports are exportable.

### 9.4 Forms
- Workspace can create structured forms (e.g. bug intake form, leave request form).
- Submissions are linked to tasks automatically.
- Form data feeds into reports and dashboards.

---

## Phase 10 — Integrations

**Entry point:** Admin opens Workspace Settings > Integrations.

### 10.1 Slack
- Connect Slack workspace to OneVo WorkSync.
- All Slack messages sync into the WorkSync chat in real time.
- Configured via OAuth. No Slack app installation required on the user side.

### 10.2 API access
- Workspace Admins create API keys for external tools (CI/CD pipelines, analytics platforms, internal scripts).
- Keys are scoped and can be revoked at any time.

### 10.3 Webhooks
- Admins configure webhooks to fire on specific events (task created, status changed, sprint completed).
- External systems receive the payload and react in real time (e.g. trigger a build, post to external log).
- Each webhook delivery is logged with status and retry information.

---

## System-wide behaviours

These behaviours apply at all times, across all phases.

### Real-time sync
- Any status change on a task — whether made from the project board, My Space, or Chat Reminder — is reflected immediately everywhere. There is no polling delay.

### Two-way chat-kanban sync
- When a user changes a Chat Reminder item status, the Kanban board updates.
- When a developer updates a task on the Kanban board, the Chat Reminder reflects the new status.
- Both directions are always active.

### Notification on every assignment
- Any time a task, document, or approval is assigned to a user, a notification fires immediately.

### AI requires user confirmation (standard tier)
- The AI never creates, deletes, or modifies any record without explicit user confirmation.
- The confirmation is a single click on the suggestion card.
- Premium AI auto-creates but sends a confirmation toast with an undo option.

### Audit trail
- Every action in the system — create, update, delete, login, approval — is logged with the actor, timestamp, and affected entity.
- Admins can view the full audit log for the workspace.

### Multi-workspace isolation
- A user's data, projects, and conversations in Workspace A are completely invisible from Workspace B, even if the same user is a member of both.

---

## User roles — what each role can do

| Role | Can do |
|---|---|
| Admin | Everything — settings, billing, integrations, all projects, all users |
| Manager | Create projects, view all tasks, approve submissions, view reports |
| Team Lead | Create sprints, assign tasks, approve submissions within their team |
| Developer | Work on assigned tasks, log time, submit work, chat |
| Viewer | Read-only access to projects and dashboards they are granted access to |

---

## Key flows at a glance

### Flow A — Task created from project board
`Manager creates project` → `Team Lead creates sprint` → `Task created & assigned` → `Developer sees task in My Space` → `Developer works, logs time` → `Developer submits` → `Manager approves` → `Task Done`

### Flow B — Task created from chat
`User types @mention + #task in chat` → `AI detects tag` → `AI checks for missing fields` → `Popup collects missing info` → `User confirms suggestion` → `Task auto-created in project board` → `Assignee notified` → `Task appears in Chat Reminder`

### Flow C — Premium AI task creation
`User writes normal message about work` → `AI reads message in background` → `AI detects intent + extracts details` → `Task auto-created silently` → `User sees confirmation toast` → `Can undo within 10 seconds`

### Flow D — Document review
`User creates document` → `Attaches to task` → `Sends for approval` → `Approver reviews & comments` → `Approved or changes requested` → `If approved: locked` → `If changes: document reopened`

### Flow E — Bug found during work
`Developer finds bug` → `Creates Bug Report linked to task` → `Adds reproduction steps + severity` → `Bug assigned to fixer` → `Fixer resolves` → `Resolution logged` → `Original task continues`
