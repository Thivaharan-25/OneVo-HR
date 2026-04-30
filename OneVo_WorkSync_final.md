# OneVo WorkSync — Deep User Flow & User Scenarios

---

## Phase 1 — Authentication

### 1.1 Login

**User Flow**

- User opens the app and enters their email and password on the Login screen
- User clicks Login
- System validates the credentials
- If MFA is enabled, system shows the second-factor prompt
- User enters the one-time code from their authenticator app
- System validates the code — if correct, full access is granted
- System issues a session token and stores it on the client
- System redirects the user to the Workspace Selection screen
- If the user clicks Continue with Google or Continue with GitHub, system redirects to the OAuth provider, completes authentication, and returns a session token on success
- If credentials are wrong at any step, system shows an error and logs the failed attempt to the audit log

**User Scenarios**

*Scenario A — Successful Login with MFA*

- User opens the app → Login screen appears
- User enters email and password → clicks Login
- System validates credentials → MFA prompt appears
- User opens authenticator app and enters the OTP
- System validates OTP → session token issued and stored on client
- System redirects to Workspace Selection screen
- User selects workspace → lands on My Space

*Scenario B — Failed Login (Wrong Password)*

- User enters email and an incorrect password → clicks Login
- System validates credentials → validation fails
- System shows error message on screen
- System logs the failed attempt to the Audit Log with timestamp
- User corrects the password → login succeeds

---

### 1.2 HR-Managed Employee Onboarding (No Self-Registration)

**User Flow**

- There is no public Register option in the app — employees cannot create their own accounts
- HR logs into the workspace using their HR role credentials
- HR navigates to Workspace Settings → Members → Add Employee
- HR fills in the employee's full name, email, department, team, and assigns a role such as Developer, Designer, or Viewer
- HR sets a temporary username and temporary password for the employee and clicks Save
- System creates the employee account immediately
- System sends a welcome email to the employee containing their temporary credentials
- Employee opens the app, enters the temporary username and password, and clicks Login
- System validates the credentials and detects this is a first-time login with a temporary password
- System does not take the employee to the dashboard yet
- System immediately redirects to a forced password change screen
- Employee enters the temporary password in the Current Password field, types a new password, confirms it, and clicks Save New Password
- System validates the new password against the password policy
- System marks the account as active and the password as permanent
- System now redirects the employee directly to their personal dashboard — My Space
- From this point the employee logs in normally using their email and the new password they set
- If the employee tries to navigate away before completing the password change, system blocks all navigation — no sidebar or dashboard is accessible until the new password is saved

**User Scenarios**

*Scenario A — New Employee First Login with Forced Password Change*

- HR logs in with HR credentials
- HR navigates to Workspace Settings → Members → Add Employee
- HR fills in full name, email, department, team, and role → sets temporary username and password → clicks Save
- System creates the account → sends welcome email with temporary credentials
- Employee opens the app → enters temporary credentials → clicks Login
- System detects first-time login with temporary password → redirects to Forced Password Change screen — no dashboard access yet
- Employee enters temporary password in Current Password field → types and confirms new password → clicks Save New Password
- System validates against password policy → marks account active → redirects employee to My Space
- All future logins use email and the new password

*Edge Case — Employee Tries to Navigate Away Before Completing Password Change*

- Employee attempts to click away from the password change screen
- System blocks all navigation — sidebar and dashboard remain inaccessible
- Employee must complete the password change to proceed

---

### 1.3 Session & Security

**User Flow**

- Every request the user makes carries the session token automatically
- If the session expires due to inactivity, system invalidates the token and redirects the user to the login screen
- The expiry event is written to the audit log
- If the user clicks Forgot Password, system shows an email input
- User enters their email and clicks Send Reset Link
- System sends a password reset email with a time-limited token
- User clicks the link — system shows the new password form
- User sets a new password and clicks Save — system updates the credential and redirects to login
- If the reset link has expired, system shows an error and asks the user to request a new one

**User Scenarios**

*Scenario A — Session Expiry*

- User is inactive for the configured session timeout duration
- System invalidates the session token → redirects user to login screen
- System writes the expiry event to the Audit Log

*Scenario B — Forgot Password Reset*

- User clicks Forgot Password on the login screen
- User enters registered email → clicks Send Reset Link
- System generates a time-limited reset token → sends reset email
- User opens email → clicks the reset link → system shows New Password form
- User enters and confirms new password → clicks Save
- System updates the credential → redirects to login screen

*Edge Case — Expired Reset Link*

- User clicks the reset link after it has expired
- System shows an error
- System prompts the user to request a new reset link

---

## Phase 2 — Workspace & Organisation Setup

### 2.1 Workspace Selection

**User Flow**

- After login, user sees a list of all workspaces they belong to
- User clicks the workspace they want to enter
- System creates a session scoped to that workspace and loads all workspace context
- System takes the user to their personal My Space inside that workspace
- If the user wants to create a new workspace, they click Create New Workspace
- User fills in name, timezone, and billing details and clicks Create
- System provisions the workspace and assigns the user as Admin automatically

**User Scenarios**

*Scenario A — Entering an Existing Workspace*

- User logs in → sees the list of all workspaces they belong to
- User clicks the target workspace
- System creates a scoped session → loads all workspace context → takes user to My Space

*Scenario B — Creating a New Workspace*

- User clicks Create New Workspace on the selection screen
- User fills in name, timezone, and billing details → clicks Create
- System provisions the workspace → assigns user as Admin automatically
- User enters the new workspace → lands on My Space

---

### 2.2 Roles & Permissions

**User Flow**

- Admin navigates to Workspace Settings and opens the Members tab
- Admin sees the full member list with a role dropdown next to each name
- Admin clicks the role dropdown for any member and selects a new role
- System immediately applies the new permissions — the next action that member takes is subject to the updated role
- If any user tries to perform an action above their permission level, system rejects it with a permission denied error and logs the attempt to the audit trail

**User Scenarios**

*Scenario A — Changing a Member's Role*

- Admin navigates to Workspace Settings → Members tab
- Admin finds the member → clicks the role dropdown next to their name
- Admin selects a new role → system applies the change immediately
- The next action that member takes is governed by the updated permissions

*Scenario B — Unauthorised Action Attempt*

- A user attempts to perform an action above their permission level
- System rejects the action with a permission denied error
- System logs the attempt to the Audit Trail

---

### 2.3 Organisation Structure

**User Flow**

- Admin opens the Organisation section in settings
- Admin clicks + New Department, types the department name, and clicks Save
- System creates the department under the workspace
- Admin clicks + New Team inside a department, fills in the team name, adds members, and clicks Save
- System creates the team — members receive a notification of their team assignment
- A user can belong to multiple teams — their permissions stack accordingly

**User Scenarios**

*Scenario A — Creating Departments and Teams*

- Admin opens Organisation in settings
- Admin clicks + New Department → types department name → clicks Save
- System creates the department under the workspace
- Admin clicks + New Team inside the department → fills in team name → adds members → clicks Save
- System creates the team → each member receives a notification of their team assignment

*Scenario B — Member Belonging to Multiple Teams*

- A member is added to two separate teams within the same workspace
- System stacks permissions from both team assignments
- The member can act under the combined permission set of all their teams

---

### 2.4 Inviting Users

**User Flow**

- Admin clicks Invite Member
- Admin enters the recipient's email, selects their role, and clicks Send Invite
- System creates an invite record with an expiry time and sends the invite email to the recipient
- Recipient opens the email and clicks Accept Invitation
- System adds the recipient to the workspace with the assigned role — they can now log in and access the workspace
- If the recipient does not accept before the invite expires, the link becomes invalid
- Admin must go back and resend the invite for the same email address

**User Scenarios**

*Scenario A — Successful Invite Acceptance*

- Admin clicks Invite Member
- Admin enters recipient email, selects role → clicks Send Invite
- System creates an invite record with expiry → sends invite email
- Recipient opens email → clicks Accept Invitation
- System adds recipient to workspace with assigned role → recipient can now log in

*Edge Case — Invite Link Expired*

- Recipient does not accept before the invite expires → link becomes invalid
- Admin must resend the invite for the same email address

---

## Phase 3 — My Space (Personal Hub)

### 3.1 Calendar View

**User Flow**

- Every user lands on My Space after entering a workspace
- The Calendar is shown by default on the My Space home screen
- System pulls all events belonging to the user — task deadlines, meetings, goal milestones, reminders — and renders them in one unified calendar
- User clicks the Day, Week, or Month toggle to switch the calendar view
- System re-renders the calendar in the selected format — the current date is always highlighted
- User clicks any event on the calendar
- System navigates to the source of that event — the task detail page, meeting record, or goal page depending on the event type

**User Scenarios**

*Scenario A — Reviewing the Day from Calendar*

- User logs in → lands on My Space with Calendar open by default
- System pulls all user events — task deadlines, meetings, goal milestones, reminders — and renders them in one unified calendar
- User clicks Day toggle → calendar re-renders to today's events with current date highlighted
- User clicks an event → system navigates directly to the task detail page, meeting record, or goal page for that event

---

### 3.2 Personal Task Board

**User Flow**

- User clicks the Task Board tab inside My Space
- System fetches all tasks assigned to the user across every project in the workspace
- Tasks are displayed in a Kanban board grouped into status columns
- User drags a task card from one column to another — for example from To Do to In Progress
- System updates the task status and immediately syncs the change to the project-level board — the project team sees the update in real time
- User clicks Configure Columns to open the column editor
- User renames, reorders, or adds columns and clicks Save — the customised layout is stored for this user's personal view only

**User Scenarios**

*Scenario A — Managing Tasks from Personal Board*

- User clicks Task Board tab inside My Space
- System fetches all tasks assigned to the user across every project in the workspace
- Tasks appear in a Kanban board grouped by status columns
- User drags a task card from To Do to In Progress
- System updates the task status instantly → project board reflects the change in real time → project team sees the update without refreshing

*Scenario B — Customising Column Layout*

- User clicks Configure Columns → column editor opens
- User renames, reorders, or adds columns → clicks Save
- System stores the customised layout for this user's personal view only — project board is unaffected

---

### 3.3 To-dos

**User Flow**

- User clicks + New To-do on the My Space screen
- User types the item and presses Enter or clicks Save
- System creates the to-do — it is personal, not linked to any project, and visible only to this user
- User clicks the repeat icon on a to-do and selects Daily, Weekly, or Monthly
- System sets the recurrence — the item auto-regenerates at the end of each cycle
- User clicks the date field on a to-do and sets a due date
- System adds the to-do to the Calendar view on that date
- User clicks the delete icon — system removes it immediately with no confirmation prompt

**User Scenarios**

*Scenario A — Creating and Scheduling a Personal To-do*

- User clicks + New To-do → types the item → presses Enter
- System creates the to-do — personal, not linked to any project, visible only to this user
- User clicks the date field → sets a due date
- System adds the to-do to the Calendar view on that date
- User clicks the repeat icon → selects Weekly
- System sets recurrence → item auto-regenerates at the end of each week

*Scenario B — Deleting a To-do*

- User clicks the delete icon on a to-do
- System removes it immediately with no confirmation prompt

---

### 3.4 Goals (OKR)

**User Flow**

- User clicks the Goals tab inside My Space
- System shows all Objectives and Key Results assigned to this user
- User clicks on an Objective to open it
- User clicks Log Check-in, fills in the progress update, and clicks Submit
- System saves the check-in and updates the progress indicator on the goal
- If the goal has a milestone with a date attached, that milestone appears in the Calendar view automatically

**User Scenarios**

*Scenario A — Logging a Goal Check-in*

- User clicks Goals tab inside My Space
- System shows all Objectives and Key Results assigned to the user
- User clicks on an Objective → clicks Log Check-in
- User fills in the progress update → clicks Submit
- System saves the check-in → updates the progress indicator on the goal
- If a milestone with a date is attached to the goal, it appears in the Calendar view automatically

---

### 3.5 Activity Log

**User Flow**

- User clicks the Activity tab inside My Space
- System shows a chronological log of every action the user has taken across the workspace — creates, edits, comments, status changes, approvals — with timestamps

**User Scenarios**

*Scenario A — Reviewing Personal Activity*

- User clicks the Activity tab inside My Space
- System shows a chronological log of every action the user has taken across the workspace
- Log entries include creates, edits, comments, status changes, and approvals — each with a timestamp

---

## Phase 4 — Project Management

### 4.1 Project Creation

**User Flow**

- Manager or Admin clicks + New Project in the workspace sidebar
- Manager fills in project name, status, timezone, working days, and default priority
- Manager clicks Create Project
- System creates the project and assigns the Manager as Project Manager
- Manager clicks Add Members inside the project settings
- Manager searches for users by name, selects them, assigns each a project role, and clicks Confirm
- System adds those users to the project — each receives a notification immediately
- Manager clicks + New Epic, enters a name, and clicks Save
- System creates the Epic as a high-level theme under the project
- Manager clicks + New Milestone inside an Epic, sets a name and target date, and clicks Save
- System creates the milestone — it appears on the project timeline and in the Calendar view of all assigned members

**User Scenarios**

*Scenario A — Creating a Project with Epics and Milestones*

- Manager clicks + New Project in the workspace sidebar
- Manager fills in project name, status, timezone, working days, and default priority → clicks Create Project
- System creates the project → assigns the Manager as Project Manager automatically
- Manager clicks Add Members → searches for users → assigns each a project role → clicks Confirm
- System adds users to the project → each receives an immediate notification
- Manager clicks + New Epic → enters a name → clicks Save
- System creates the Epic as a high-level theme under the project
- Manager clicks + New Milestone inside the Epic → sets name and target date → clicks Save
- System creates the milestone → it appears on the project timeline and in the Calendar view of all assigned members

---

### 4.2 Sprint Planning

**User Flow**

- Team Lead opens the project and clicks + New Sprint
- Team Lead sets start date, end date, and the sprint goal, then clicks Create Sprint
- System creates the sprint — the sprint board is now ready to receive tasks
- Team Lead clicks the Roadmap tab to view all sprints across a timeline
- Team Lead drags sprints to reorder them or attaches version and release targets to sprint end dates
- System saves the roadmap arrangement

**User Scenarios**

*Scenario A — Creating a Sprint and Arranging the Roadmap*

- Team Lead opens the project → clicks + New Sprint
- Team Lead sets start date, end date, and sprint goal → clicks Create Sprint
- System creates the sprint → sprint board is ready to receive tasks
- Team Lead clicks Roadmap tab → views all sprints across a timeline
- Team Lead drags sprints to reorder or attaches version and release targets to sprint end dates
- System saves the roadmap arrangement

---

### 4.3 Task Creation & Assignment

**User Flow**

- Team Lead clicks + Add Task inside a sprint
- Team Lead fills in title, description, priority, status, and due date, then clicks Save
- System creates the task inside the sprint with a unique ID — status defaults to To Do
- Team Lead clicks Add Sub-items and types checklist items one by one
- System adds each as a checkbox inside the task card
- Team Lead clicks Add Dependency and searches for another task
- Team Lead selects the blocking task and clicks Confirm
- System links the two tasks — this task is now marked as blocked and cannot move to Done until the dependency is resolved
- Team Lead clicks the Assignee field, searches for and selects one or more developers, and clicks Confirm
- System assigns the task — it instantly appears in each developer's My Space task board and Calendar view
- A notification fires to each assignee the moment the assignment is saved

**User Scenarios**

*Scenario A — Creating a Task with Checklist, Dependency, and Assignee*

- Team Lead clicks + Add Task inside a sprint
- Team Lead fills in title, description, priority, status, and due date → clicks Save
- System creates the task with a unique ID — status defaults to To Do
- Team Lead clicks Add Sub-items → types checklist items one by one
- System adds each as a checkbox inside the task card
- Team Lead clicks Add Dependency → searches for and selects the blocking task → clicks Confirm
- System links the two tasks → this task is now marked as blocked → cannot move to Done until the dependency is resolved
- Team Lead clicks Assignee field → selects one or more developers → clicks Confirm
- System assigns the task → it appears instantly in each developer's My Space task board and Calendar view
- A notification fires to each assignee immediately

*Edge Case — Dependency Blocks Task Completion*

- Developer attempts to move a blocked task to Done
- System keeps the Done option greyed out while the dependency task is still open
- Once the dependency task is resolved, the Done option becomes available automatically — no manual refresh needed

---

### 4.4 GitHub Repository Linking to Tasks

**User Flow**

- Team Lead opens a task inside a project and scrolls to the Linked Repositories section
- Team Lead clicks + Link Repository
- System shows a GitHub OAuth prompt — Team Lead authorises WorkSync to access their GitHub account
- After authorisation, system fetches and displays all repositories the Team Lead has access to
- Team Lead selects the specific repository relevant to this task and clicks Confirm
- System stores the repository link against the task — the task now shows the connected repo name and a direct link
- Multiple repositories can be linked to a single task if needed
- The same repository can be linked to tasks across different projects — monitoring covers all linked tasks simultaneously

**User Scenarios**

*Scenario A — Linking a GitHub Repository to a Task*

- Team Lead opens a task → scrolls to Linked Repositories → clicks + Link Repository
- System shows GitHub OAuth prompt → Team Lead authorises WorkSync
- System fetches all accessible repositories → displays the list
- Team Lead selects the relevant repository → clicks Confirm
- System stores the repository link against the task → task shows the connected repo name and a direct link
- Multiple repositories can be linked to a single task if needed
- The same repository can be linked to tasks across different projects — monitoring covers all linked tasks simultaneously

---

## Phase 5 — Task Execution

### 5.1 Developer Starts Work

**User Flow**

- Developer opens My Space and sees the assigned task on their personal board
- Developer clicks on the task card to open the task detail page
- Developer clicks the status dropdown and selects In Progress, or drags the card to the In Progress column
- System updates the task status and syncs it to the project board instantly — the Team Lead and Manager see the change in real time
- Developer clicks Start Timer on the task detail page
- System begins a running timer displayed in the task header

**User Scenarios**

*Scenario A — Starting Work and Tracking Time*

- Developer opens My Space → sees the assigned task on the personal board
- Developer clicks the task card → task detail page opens
- Developer clicks status dropdown → selects In Progress
- System updates the status → Team Lead and Manager see the change on the project board in real time
- Developer clicks Start Timer → a running timer appears in the task header

---

### 5.2 Collaboration on the Task

**User Flow**

- Developer clicks the Comments section and types a message, then clicks Send
- Developer types @username to mention a teammate — system sends a notification to that person immediately
- Developer clicks the Attachments section, clicks Upload File, and selects a file from their device
- System uploads the file and attaches it directly to the task
- Developer notices a bug during work and clicks Create Bug Report
- Developer fills in the bug title, reproduction steps, and severity, then clicks Submit
- System creates a Bug Report, links it to the current task, and shows it as a related item on the task card
- Developer assigns the Bug Report to a fixer — that person receives a notification

**User Scenarios**

*Scenario A — Collaborating via Comments and Attachments*

- Developer clicks Comments section → types a message → clicks Send
- Developer types @username to mention a teammate → system sends a notification to that person immediately
- Developer clicks Attachments section → clicks Upload File → selects file from device
- System uploads the file and attaches it directly to the task

*Scenario B — Raising a Bug Report from a Task*

- Developer notices a bug during work → clicks Create Bug Report
- Developer fills in bug title, reproduction steps, and severity → clicks Submit
- System creates a Bug Report → links it to the current task → shows it as a related item on the task card
- Developer assigns the Bug Report to a fixer → that person receives a notification

---

### 5.3 Checklist & Dependencies

**User Flow**

- Developer opens the task and sees the checklist items inside
- Developer ticks a checklist item by clicking the checkbox — system marks it done and shows updated progress on the task card
- If the task has a dependency, system shows the dependency status in the task detail view
- If the dependency task is still open, the Done option is greyed out — the developer cannot move this task to Done until the blocking task is resolved
- Once the dependency is resolved, the Done option becomes available automatically — no manual refresh needed

**User Scenarios**

*Scenario A — Working Through a Checklist*

- Developer opens the task → sees checklist items inside
- Developer ticks a checklist item by clicking the checkbox
- System marks it done → shows updated progress on the task card

*Scenario B — Dependency Blocking Task Completion*

- Developer opens the task → system shows the dependency status in the task detail view
- Dependency task is still open → Done option is greyed out
- Developer cannot move the task to Done until the blocking task is resolved
- Once the dependency is resolved → Done option becomes available automatically — no manual refresh needed

---

### 5.4 Time Logging

**User Flow**

- Developer clicks Stop Timer when done with a work session
- System records the time entry against the task with a timestamp
- Developer can also click Log Time Manually, enter hours and minutes, and click Save
- All time entries roll up into the developer's Timesheet — visible to managers at end of week or month

**User Scenarios**

*Scenario A — Stopping Timer and Logging Time*

- Developer clicks Stop Timer when done with a work session
- System records the time entry against the task with a timestamp

*Scenario B — Manual Time Entry*

- Developer clicks Log Time Manually → enters hours and minutes → clicks Save
- System records the entry → all time entries roll up into the developer's Timesheet
- Timesheet is visible to managers at end of week or month

---

### 5.5 IDE Extension — GitHub Repository Monitoring

**User Flow**

- Developer opens VS Code — the WorkSync IDE Extension is active in the background
- Developer opens any file inside a repository that is linked to a WorkSync task
- Extension automatically detects which WorkSync task this repository belongs to
- Extension displays the linked task details in the sidebar — task title, status, assignee, due date, and priority — without the developer needing to search for it manually
- Every commit the developer makes inside the linked repository is captured by the extension — commit message, timestamp, branch name, and files changed are all recorded against the linked task
- Every branch creation, branch switch, and pull request raised inside the linked repository is tracked and logged
- If the developer is working on a branch that does not match the task's expected branch naming convention, the extension shows a warning in the sidebar
- Time spent actively coding inside the linked repository is logged automatically and feeds directly into the task's time log and the developer's timesheet
- If the developer pushes code and a CI/CD pipeline result is available, the pass or fail status is shown on the task card inside the extension sidebar
- If the developer works on tasks linked to multiple repositories, the extension monitors all of them simultaneously and routes activity to the correct task automatically — no mixing of data between tasks

**User Scenarios**

*Scenario A — Developer Works Inside VS Code with Extension Active*

- Developer opens VS Code → WorkSync IDE Extension is active in the background
- Developer opens a file inside a repository linked to a WorkSync task
- Extension automatically detects which task this repository belongs to
- Extension displays task details in the VS Code sidebar — title, status, assignee, due date, priority — without the developer needing to search
- Developer creates a new branch → extension logs the branch creation against the task
- Developer writes code → makes a commit
- Extension captures the commit — message, timestamp, branch name, and files changed — all recorded against the linked task
- Developer raises a pull request → extension tracks and logs the PR event
- CI/CD pipeline runs → pass or fail result appears on the task card inside the extension sidebar
- Time spent actively coding is logged automatically and feeds into the task's time log and the developer's timesheet

*Edge Case — Branch Naming Convention Mismatch*

- Developer works on a branch that does not match the task's expected branch naming convention
- Extension shows a warning in the sidebar

*Scenario B — Multiple Linked Repositories*

- Developer works on tasks linked to multiple repositories
- Extension monitors all of them simultaneously → routes activity to the correct task automatically
- No mixing of data between tasks

---

### 5.6 Task Submission

**User Flow**

- When work is complete, developer clicks Submit Task
- System opens a submission form — developer adds completion notes and attaches any deliverable files
- Developer clicks Submit
- System creates an approval request and sends a notification to the Team Lead or Manager

**User Scenarios**

*Scenario A — Submitting a Completed Task*

- Developer completes all checklist items → clicks Submit Task
- System opens a submission form → developer adds completion notes and attaches deliverable files
- Developer clicks Submit
- System creates an approval request → sends a notification to the Team Lead or Manager

---

### 5.7 Approval Flow

**User Flow**

- Approver receives a notification and clicks on it to open the submission
- Approver reviews the notes, attached files, and any linked bug reports
- Approver types a comment in the review field
- If the approver clicks Approve — system marks the task status as Done, time log is finalised, developer receives a confirmation notification
- If the approver clicks Reject — system reopens the task, records the rejection reason in the reopen log, task status returns to In Progress, developer receives a notification with the rejection reason and resumes work

**User Scenarios**

*Scenario A — Task Approved*

- Approver receives notification → clicks to open the submission
- Approver reviews notes, attached files, and any linked bug reports → types a comment in the review field
- Approver clicks Approve
- System marks the task as Done → time log is finalised → developer receives a confirmation notification

*Scenario B — Task Rejected*

- Approver reviews the submission → clicks Reject
- System reopens the task → records the rejection reason in the reopen log
- Task status returns to In Progress → developer receives a notification with the rejection reason
- Developer resumes work

---

## Phase 6 — Chat & AI Automation

### 6.1 Group Channel

**User Flow**

- User clicks Chat in the workspace sidebar
- System opens the workspace group channel by default
- User types a message and presses Enter — system sends it to all workspace members
- User hovers over a message and clicks the emoji reaction icon — system adds the reaction and shows the count
- User clicks the Attach icon, selects a file, and clicks Send — system uploads and shares the file in the channel
- System shows read receipts under each message indicating who has seen it

**User Scenarios**

*Scenario A — Sending a Message and Attaching a File*

- User clicks Chat in the workspace sidebar → system opens the workspace group channel by default
- User types a message → presses Enter → system sends it to all workspace members
- System shows read receipts under the message indicating who has seen it
- User clicks Attach icon → selects a file → clicks Send
- System uploads and shares the file in the channel
- User hovers over a message → clicks the emoji reaction icon → system adds the reaction and shows the count

---

### 6.2 Direct Messages

**User Flow**

- User clicks the + New DM icon in the Chat sidebar
- User searches for a colleague by name and clicks their profile to open a 1-on-1 DM
- To create a group DM, user selects multiple people and clicks Open Conversation
- System creates the DM scoped to the current workspace — it is not visible outside that workspace

**User Scenarios**

*Scenario A — Opening a 1-on-1 DM*

- User clicks + New DM icon in the Chat sidebar
- User searches for a colleague by name → clicks their profile
- System opens the 1-on-1 DM scoped to the current workspace — not visible outside that workspace

*Scenario B — Creating a Group DM*

- User clicks + New DM icon → selects multiple people → clicks Open Conversation
- System creates the group DM scoped to the current workspace

---

### 6.3 Tag-based AI Automation — Standard Users

**User Flow**

- User types a message in any channel with a tag and an @mention
- Example: @john #task Please design the homepage banner by Friday
- System detects the #task tag and checks whether all required fields are present — title, assignee, and due date
- All fields are present — system shows a confirmation suggestion card inside the chat asking the user to accept
- User clicks Accept
- System creates the task in the project board, assigns it to John, and sends John a notification
- The tagged message appears in the Chat Reminder section for both the sender and the assignee
- If any required field is missing, system shows an inline popup asking only for the missing field — user fills it in without leaving the conversation — once all fields are collected the confirmation card appears
- Supported tags: #task requires title, assignee, due date — #issue requires issue description and assignee — #report requires report type and target user or channel — #motion requires motion description — #decision requires decision description

**User Scenarios**

*Scenario A — Creating a Task from Chat with All Fields Present*

- User types a message in any channel with a tag and an @mention — e.g. @username #task Please design the homepage banner by Friday
- System detects the #task tag → checks required fields: title ✓, assignee ✓, due date ✓
- All fields present → system shows a confirmation suggestion card inside the chat
- User clicks Accept → system creates the task in the project board → assigns it to the mentioned user → sends a notification
- Tagged message appears in Chat Reminder section for both the sender and the assignee

*Scenario B — Missing Required Field in Tag*

- User types a tagged message but omits the due date
- System detects the missing field → shows an inline popup asking only for the due date
- User fills in the date without leaving the conversation
- System now has all required fields → shows the confirmation card → user clicks Accept → task is created

*Supported Tags Reference*

- #task — requires title, assignee, due date
- #issue — requires issue description and assignee
- #report — requires report type and target user or channel
- #motion — requires motion description
- #decision — requires decision description

---

### 6.4 Chat Reminder

**User Flow**

- User clicks Reminders inside the Chat section
- System shows two lists — tags the user created, and tags where they were mentioned or assigned
- Each item shows its current status — To Do, In Progress, or Done
- User clicks the status dropdown on any Chat Reminder item and changes the status
- System immediately updates the corresponding Kanban column on the project board — this is the two-way sync
- If a developer updates the task on the Kanban board, the Chat Reminder item reflects the new status automatically
- Admin sees all tagged messages from all members in one consolidated list, can filter by user, status, or date, and can track team progress entirely from this view

**User Scenarios**

*Scenario A — Updating Task Status from Chat Reminders*

- User clicks Reminders inside the Chat section
- System shows two lists — tags the user created, and tags where they were mentioned or assigned
- Each item shows its current status — To Do, In Progress, or Done
- User clicks the status dropdown on a reminder item → selects In Progress
- System immediately updates the corresponding Kanban column on the project board

*Scenario B — Two-Way Sync from Kanban Board*

- Developer updates a task status on the Kanban board
- Chat Reminder item reflects the new status automatically — no action needed from the user

*Scenario C — Admin Overview*

- Admin opens Reminders → sees all tagged messages from all members in one consolidated list
- Admin filters by user, status, or date
- Admin tracks team progress entirely from this view

---

### 6.5 Premium AI Automation — Paid Workspaces

**User Flow**

- User types a normal message in chat with no tags — for example: I'll finish the marketing report by tomorrow afternoon
- System reads the message passively in the background — no tags required
- AI detects task intent and extracts what, who, and when from the message
- System auto-creates the task in the project framework without asking the user anything
- A notification toast appears with a 10-second undo option — if the user clicks Undo the task is deleted — if the user does nothing the task remains and the assignee receives a notification

**User Scenarios**

*Scenario A — Auto Task Creation from Natural Language*

- User types a normal message in chat with no tags — e.g. I'll finish the marketing report by tomorrow afternoon
- System reads the message passively in the background
- AI detects task intent → extracts what, who, and when from the message
- System auto-creates the task in the project framework without asking the user anything
- A notification toast appears with a 10-second undo option
- If the user clicks Undo → task is deleted
- If the user does nothing → task remains → assignee receives a notification

---

## Phase 7 — Documents

### 7.1 Create & Manage Documents

**User Flow**

- User clicks Documents in the sidebar, or opens a task and clicks Attach Document
- User clicks + New Document
- System creates a blank document editor inside the platform
- User types content and clicks Save
- System saves the document and creates Version 1 — every subsequent save creates a new version automatically
- User can click Version History to view and restore any previous version
- User clicks the Status dropdown and sets the document to Draft, In Review, Approved, or Archived

**User Scenarios**

*Scenario A — Creating and Versioning a Document*

- User clicks Documents in the sidebar → clicks + New Document
- System creates a blank document editor
- User types content → clicks Save
- System saves the document and creates Version 1
- Every subsequent save creates a new version automatically
- User clicks Version History → views all previous versions → restores a version if needed
- User clicks Status dropdown → sets the document to Draft, In Review, Approved, or Archived

---

### 7.2 Document Approval

**User Flow**

- User clicks Send for Review on the document and selects the approver, then clicks Submit
- System sends a notification to the approver with a link to the document
- Approver opens the document, reads through it, and types comments in the review panel
- If the approver clicks Approve — system marks the document as Approved and locks it from further edits, user receives a confirmation notification
- If the approver clicks Request Changes — system reopens the document and notifies the user with the approver's comments, user makes edits and re-submits for review

**User Scenarios**

*Scenario A — Document Approved*

- User clicks Send for Review → selects approver → clicks Submit
- System sends a notification to the approver with a link to the document
- Approver opens the document → reads through it → types comments in the review panel → clicks Approve
- System marks the document as Approved → locks it from further edits → user receives a confirmation notification

*Scenario B — Document Sent Back for Changes*

- Approver reviews the document → clicks Request Changes
- System reopens the document → notifies the user with the approver's comments
- User makes edits → re-submits for review

---

### 7.3 Wiki

**User Flow**

- User opens a project and clicks the Wiki tab
- User clicks + New Page, types the title, writes the content, and clicks Publish
- System creates the Wiki page — all project members can view it immediately
- Any project member can click Edit on a Wiki page, make changes, and click Save
- System creates a new version of the page — previous versions remain accessible in the version history

**User Scenarios**

*Scenario A — Creating and Editing a Wiki Page*

- User opens a project → clicks the Wiki tab → clicks + New Page
- User types the title → writes the content → clicks Publish
- System creates the Wiki page → all project members can view it immediately
- A project member clicks Edit → makes changes → clicks Save
- System creates a new version of the page — previous versions remain accessible in the version history

---

## Phase 8 — Notifications & Reminders

### 8.1 Notifications

**User Flow**

- Every key event triggers a notification automatically — task assigned, task status changed, comment added, approval requested or resolved, deadline approaching, document sent for review
- Notifications are delivered as an in-app alert and an email simultaneously — on mobile, push notifications are also sent
- User clicks the bell icon in the top navigation to open the notification panel
- User clicks a notification — system navigates directly to the relevant task, document, or approval
- User clicks Notification Settings to configure which events trigger alerts and on which channels
- User enables Digest Mode — instead of individual alerts, system sends one daily or weekly summary email

**User Scenarios**

*Scenario A — Receiving and Acting on a Notification*

- A key event occurs — e.g. a task is assigned to the user
- System triggers a notification → delivers it as an in-app alert and an email simultaneously — push notification sent on mobile
- User clicks the bell icon in the top navigation → notification panel opens
- User clicks the notification → system navigates directly to the relevant task, document, or approval

*Scenario B — Configuring Notification Preferences*

- User clicks Notification Settings → configures which events trigger alerts and on which channels
- User enables Digest Mode → system sends one daily or weekly summary email instead of individual alerts

---

### 8.2 Reminders

**User Flow**

- User opens a task, event, or deadline and clicks Set Reminder
- User picks the date and time and selects the delivery channel — in-app, email, or push — then clicks Save Reminder
- System fires the reminder at the specified time via the configured channel
- When the reminder fires, user can click Snooze — system prompts for a snooze duration, records the snooze in the snooze log, and reschedules the reminder
- Workspace Admin can create Reminder Templates in settings that apply workspace-wide — for example a daily standup reminder at 9am every weekday

**User Scenarios**

*Scenario A — Setting and Snoozing a Reminder*

- User opens a task → clicks Set Reminder
- User picks the date and time → selects delivery channel (in-app, email, or push) → clicks Save Reminder
- System fires the reminder at the specified time via the configured channel
- User clicks Snooze → system prompts for a snooze duration
- System records the snooze in the snooze log → reschedules the reminder for the new time

*Scenario B — Admin Creates a Workspace-wide Reminder Template*

- Admin opens Workspace Settings → creates a Reminder Template
- Admin sets the template — e.g. daily standup reminder at 9am every weekday → saves
- Template applies across the workspace automatically

---

## Phase 9 — Reports & Analytics

### 9.1 Dashboards

**User Flow**

- Manager or Admin clicks Analytics in the workspace sidebar and clicks + New Dashboard
- System creates a blank dashboard canvas
- Manager clicks + Add Widget and selects a chart type — bar chart, line chart, pie chart, or KPI card
- Manager configures the widget with a data source, metric, and date range, then clicks Save Widget
- Widget appears on the dashboard populated with live data
- Manager sets a KPI target on a widget — system tracks and visualises progress toward that target over time
- Manager clicks Share Dashboard, selects specific team members or toggles workspace-wide access, and clicks Confirm
- System saves point-in-time snapshots of dashboard data automatically for trend analysis

**User Scenarios**

*Scenario A — Building and Sharing a Dashboard*

- Manager clicks Analytics in the sidebar → clicks + New Dashboard
- System creates a blank dashboard canvas
- Manager clicks + Add Widget → selects a chart type (bar chart, line chart, pie chart, or KPI card)
- Manager configures the widget with a data source, metric, and date range → clicks Save Widget
- Widget appears on the dashboard populated with live data
- Manager sets a KPI target on a widget → system tracks and visualises progress toward the target over time
- Manager clicks Share Dashboard → selects specific team members or toggles workspace-wide access → clicks Confirm
- System saves point-in-time snapshots of dashboard data automatically for trend analysis

---

### 9.2 Saved Views

**User Flow**

- Team Lead opens the project board and applies filters — for example status is Open, sprint is Sprint 3, team is Backend
- Team Lead clicks Save View, gives it a name, and clicks Confirm
- System saves the filtered view — it can be opened from the saved views list in one click at any time
- Team Lead clicks Share View and shares it with specific team members
- Shared views are used during standup meetings to review only the relevant slice of work

**User Scenarios**

*Scenario A — Saving and Sharing a Filtered View*

- Team Lead opens the project board → applies filters — e.g. status: Open, sprint: Sprint 3, team: Backend
- Team Lead clicks Save View → gives it a name → clicks Confirm
- System saves the filtered view → accessible from the saved views list in one click at any time
- Team Lead clicks Share View → shares it with specific team members
- Shared view is used during standup meetings to review only the relevant slice of work

---

### 9.3 Reports

**User Flow**

- Manager clicks Reports inside the Analytics section
- Manager clicks Sprint Velocity Report — system generates a chart showing planned vs completed story points per sprint
- Manager clicks Time Report — system shows hours logged per user, per task, and per project for a selected date range
- Manager clicks Resource Allocation Report — system shows who is over capacity and who is under-utilised based on assigned tasks and logged hours
- Manager clicks Code Activity Report — system shows commits, pull requests, and CI/CD results per developer, per task, per repository, and per date range — sourced from the IDE extension monitoring
- Manager clicks Export on any report — system generates a downloadable file in the selected format

**User Scenarios**

*Scenario A — Generating and Exporting Reports*

- Manager clicks Reports inside the Analytics section
- Manager clicks Sprint Velocity Report → system generates a chart showing planned vs completed story points per sprint
- Manager clicks Time Report → system shows hours logged per user, per task, and per project for the selected date range
- Manager clicks Resource Allocation Report → system shows who is over capacity and who is under-utilised based on assigned tasks and logged hours
- Manager clicks Code Activity Report → system shows commits, pull requests, and CI/CD results per developer, per task, per repository, and per date range — sourced from IDE extension monitoring
- Manager clicks Export on any report → system generates a downloadable file in the selected format

---

### 9.4 Forms

**User Flow**

- Admin clicks + New Form in the Forms section
- Admin builds the form by adding fields — text inputs, dropdowns, date pickers — and clicks Publish
- System generates a shareable form link
- When a user submits the form, system creates a linked task automatically from the submission data
- Form submission data flows into the relevant reports and dashboards

**User Scenarios**

*Scenario A — Creating a Form and Receiving a Submission*

- Admin clicks + New Form in the Forms section
- Admin builds the form by adding fields — text inputs, dropdowns, date pickers → clicks Publish
- System generates a shareable form link
- A user submits the form → system creates a linked task automatically from the submission data
- Form submission data flows into the relevant reports and dashboards

---

## Phase 10 — Integrations

### 10.1 GitHub Integration

**User Flow**

- Admin opens Workspace Settings and clicks the Integrations tab
- Admin clicks Connect GitHub
- System redirects to the GitHub OAuth screen — Admin authorises the connection
- System links the GitHub account to the WorkSync workspace
- From this point, repositories can be linked to tasks by any Team Lead or Manager with appropriate permissions
- All commit activity, branch events, pull request events, and CI/CD results from linked repositories flow into WorkSync automatically
- Manager can view a full code activity feed per task directly inside WorkSync without opening GitHub
- When a pull request is merged in GitHub, system automatically moves the linked task status to Ready for Review or Done depending on the project's configured automation rules
- When a task is moved to Done in WorkSync, system posts a comment on the linked GitHub pull request confirming the task closure — both sides stay updated automatically

**User Scenarios**

*Scenario A — Connecting GitHub to the Workspace*

- Admin opens Workspace Settings → clicks Integrations tab → clicks Connect GitHub
- System redirects to the GitHub OAuth screen → Admin authorises the connection
- System links the GitHub account to the WorkSync workspace
- From this point, repositories can be linked to tasks by any Team Lead or Manager with appropriate permissions
- All commit activity, branch events, pull request events, and CI/CD results from linked repositories flow into WorkSync automatically

*Scenario B — Two-Way GitHub-WorkSync Sync*

- A pull request is merged in GitHub
- System automatically moves the linked task status to Ready for Review or Done — depending on the project's configured automation rules
- A task is moved to Done in WorkSync
- System automatically posts a comment on the linked GitHub pull request confirming the task closure
- Both sides stay updated automatically — no manual action needed from either side

---

### 10.2 API Access

**User Flow**

- Admin clicks API Keys inside Integrations settings
- Admin clicks + Generate New Key, gives the key a name, sets its scope, and clicks Create
- System generates the API key and displays it once — Admin must copy it immediately as it will not be shown again
- Admin can view all active keys, see their last-used timestamps, and click Revoke on any key to invalidate it immediately

**User Scenarios**

*Scenario A — Generating and Revoking an API Key*

- Admin clicks API Keys inside Integrations settings → clicks + Generate New Key
- Admin gives the key a name → sets its scope → clicks Create
- System generates the API key and displays it once — Admin must copy it immediately as it will not be shown again
- Admin views all active keys → sees their last-used timestamps
- Admin clicks Revoke on a key → system invalidates it immediately

---

### 10.3 Webhooks

**User Flow**

- Admin clicks Webhooks inside Integrations settings
- Admin clicks + New Webhook, enters the destination URL, selects the trigger events — for example task created, status changed, sprint completed — and clicks Save
- System registers the webhook
- When a selected event occurs, system sends an HTTP POST payload to the destination URL in real time
- Admin can click any webhook in the list to view its delivery log — each delivery shows the status code, response body, and whether a retry was attempted

**User Scenarios**

*Scenario A — Setting Up and Monitoring a Webhook*

- Admin clicks Webhooks inside Integrations settings → clicks + New Webhook
- Admin enters the destination URL → selects trigger events (e.g. task created, status changed, sprint completed) → clicks Save
- System registers the webhook
- A selected event occurs → system sends an HTTP POST payload to the destination URL in real time
- Admin clicks the webhook in the list → views the delivery log
- Each delivery entry shows the status code, response body, and whether a retry was attempted

---

## System-wide Behaviours — Always Active

**Real-time Sync**

- Any status change on a task — whether made from the project board, My Space, Chat Reminder, or IDE extension — is reflected everywhere instantly with no polling delay

**Two-way Chat-Kanban Sync**

- When a user changes a Chat Reminder item status, the Kanban board column updates automatically
- When a developer updates a task on the Kanban board, the Chat Reminder reflects the new status
- Both directions are always active simultaneously

**Two-way GitHub-WorkSync Sync**

- When a pull request is merged in GitHub, the linked task status updates in WorkSync automatically
- When a task is closed in WorkSync, a confirmation comment is posted on the linked GitHub pull request automatically
- Both directions are always active simultaneously

**Notification on Every Assignment**

- Any time a task, document, or approval is assigned to a user, a notification fires immediately — no delay, no batching unless the user has configured digest mode

**AI Confirmation — Standard Tier**

- The AI never creates, deletes, or modifies any record without an explicit user click on the confirmation card
- Premium AI auto-creates tasks but always shows a confirmation toast with a 10-second undo window

**Audit Trail**

- Every action — create, update, delete, login, logout, approval, rejection — is logged with the actor's identity, a timestamp, and the affected entity
- Admins can open the Audit Log from Workspace Settings and filter by user, date, or action type

**Multi-workspace Isolation**

- A user's data, projects, and conversations in one workspace are completely invisible from any other workspace
- Even if the same user is a member of both, switching workspaces creates a fully new scoped session with no data leaking across
