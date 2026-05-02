# DEV2: Backend HR + Workforce Core

**Track:** Backend
**Primary ownership:** org structure, core HR, employee lifecycle, skills core, HR import, leave, calendar, workforce presence, notifications
**Current Unfinished Task:** Task 1 - Core HR
**Blocked By:** DEV1 backend foundation and auth skeleton

---

## ADE Instructions

When Dev 2 asks to continue, start with the first unchecked item in **Current Unfinished Task**. If DEV1 auth is incomplete, create only the smallest interface/mock required and record the contract gap here.

---

## Task 1: Org Structure + Core HR

**Goal:** implement employee and org data needed by HR, workforce, and WorkSync users.

### Acceptance Criteria

- [ ] Legal entities, departments, teams, job families, jobs, locations, cost centers, and reporting lines exist.
- [ ] Legal entity creation publishes `LegalEntityCreated` with the selected country so Calendar can seed default holiday settings.
- [ ] Team permission stacking tables exist for `team_roles`, `team_role_permissions`, and `team_member_roles`.
- [ ] Employee aggregate supports personal, contact, employment, manager, department, and team fields.
- [ ] Employee create/update/list/detail APIs exist.
- [ ] Employee lifecycle supports onboarding, transfer, promotion, and offboarding state changes.
- [ ] Employee offboarding publishes `EmployeeOffboarded` with `employee_id`, `user_id`, and tenant context so Work Management can deactivate memberships, watchers, and future assignability.
- [ ] Team membership changes publish `TeamMemberAdded` and `TeamMemberRemoved` with `team_id`, `employee_id`, `user_id`, and tenant context for Work Management HR team sync.
- [ ] Org references validate legal entity, department, team, job, and location IDs.
- [ ] Domain events are emitted for employee created, updated, transferred, and offboarded.
- [ ] Tests cover create, update, lifecycle transition, and tenant isolation.
- [ ] Tests cover event payloads consumed by Work Management (`EmployeeOffboarded`, `TeamMemberAdded`, `TeamMemberRemoved`).

### References

- [[modules/core-hr/overview|Core HR]]
- [[modules/org-structure/overview|Org Structure]]
- [[Userflow/Employee-Management/profile-management|Profile Management]]
- [[Userflow/Org-Structure/department-hierarchy|Department Hierarchy]]
- [[Userflow/Org-Structure/team-creation|Team Creation]]
- [[Userflow/Employee-Management/employee-onboarding|Employee Onboarding]]
- [[database/schemas/core-hr|Core HR Schema]]

### Verification

```bash
dotnet test ONEVO.sln --filter CoreHR
dotnet test ONEVO.sln --filter OrgStructure
```

---

## Task 2: Employee Lifecycle + HR Import + Skills Core

**Goal:** build employee lifecycle transitions, bulk import onboarding, and the core skills model.

### Acceptance Criteria

- [ ] Employee lifecycle supports onboarding, offboarding, transfer, promotion, compensation setup, dependent management, and qualification tracking.
- [ ] Lifecycle actions publish domain events used by notifications, WorkSync identity, and audit.
- [ ] HR import supports CSV and Excel upload, column mapping, validation preview, error export, and staged commit.
- [ ] Import creates employees only after validation passes.
- [ ] Skills core supports skill categories, skills, job skill requirements, employee skills, and skill validation requests.
- [ ] Employee skill declarations and manager validation flow exist.
- [ ] Tests cover onboarding, offboarding, transfer, import validation, import commit, skill taxonomy, employee skill declaration, and skill validation.

### References

- [[modules/core-hr/overview|Core HR]]
- [[modules/data-import/overview|Data Import]]
- [[modules/skills/overview|Skills]]
- [[Userflow/Employee-Management/employee-onboarding|Employee Onboarding]]
- [[Userflow/Employee-Management/employee-offboarding|Employee Offboarding]]
- [[Userflow/Employee-Management/employee-transfer|Employee Transfer]]
- [[Userflow/Skills-Learning/skill-taxonomy-setup|Skill Taxonomy Setup]]
- [[Userflow/Skills-Learning/employee-skill-declaration|Employee Skill Declaration]]

### Verification

```bash
dotnet test ONEVO.sln --filter EmployeeLifecycle
dotnet test ONEVO.sln --filter DataImport
dotnet test ONEVO.sln --filter Skills
```

---

## Task 3: Leave + Calendar

**Goal:** build leave and calendar APIs consumed by web UI and IDE extension HR tags.

### Acceptance Criteria

- [ ] Leave policies, leave types, balances, requests, approvals, and balance ledger exist.
- [ ] Leave request approval uses the Shared Platform workflow engine.
- [ ] Leave request API validates balance, dates, overlap, and approval routing.
- [ ] Calendar APIs return holidays, shifts, leaves, and company events in one feed.
- [ ] Calendar supports Phase 1 country holiday sync through `holiday_calendar_settings`, defaulting to legal entity country.
- [ ] Calendar admins can disable country holiday sync or override the holiday calendar country without changing the legal entity.
- [ ] Google Calendar and Outlook Calendar connections support OAuth callback, encrypted token storage, pull/push/two-way sync direction, and idempotent event links.
- [ ] IDE-ready endpoints exist for leave types, leave balance, and leave request creation.
- [ ] Notifications are emitted for leave submitted, approved, rejected, and cancelled.
- [ ] Tests cover balance validation, approval flow, calendar feed composition, holiday setting default/override, and external calendar event deduplication.

### References

- [[modules/leave/overview|Leave]]
- [[Userflow/Leave/leave-request-submission|Leave Request Submission]]
- [[Userflow/Calendar/calendar-event-creation|Calendar Event Creation]]
- [[Userflow/Calendar/calendar-integrations|Calendar Integrations]]
- [[modules/calendar/calendar-events/end-to-end-logic|Calendar Events Logic]]
- [[database/schemas/calendar|Calendar Schema]]
- [[database/schemas/leave|Leave Schema]]

### Verification

```bash
dotnet test ONEVO.sln --filter Leave
dotnet test ONEVO.sln --filter Calendar
```

---

## Task 4: Workforce Presence

**Goal:** implement presence sessions, breaks, overtime, and schedule-backed work state.

### Acceptance Criteria

- [ ] Presence session start/end APIs exist.
- [ ] Break start/end APIs exist.
- [ ] Overtime request API exists.
- [ ] Shift and schedule APIs expose current and upcoming shifts.
- [ ] Presence lifecycle validates employee active status and policy.
- [ ] APIs used by IDE tags exist for `clockin`, `break:start`, `break:end`, `clockout`, and `overtime:request`.
- [ ] Tests cover session lifecycle, break lifecycle, and invalid transitions.

### References

- [[modules/workforce-presence/overview|Workforce Presence]]
- [[Userflow/Workforce-Presence/presence-session-view|Presence Session View]]
- [[Userflow/Workforce-Presence/overtime-management|Overtime Management]]

### Verification

```bash
dotnet test ONEVO.sln --filter WorkforcePresence
```

---

## Task 5: Notifications

**Goal:** provide in-app, email, and SignalR notifications for HR, WorkSync, IDE, and agent events.

### Acceptance Criteria

- [ ] Notification entity supports tenant, recipient, channel, title, body, read state, and metadata.
- [ ] Notification preferences exist per user.
- [ ] In-app notification APIs support list, unread count, mark read, and mark all read.
- [ ] SignalR event is sent when a new notification is created.
- [ ] Notification templates can be resolved by event type.
- [ ] Tests cover creation, unread count, and SignalR dispatch contract.

### References

- [[backend/notification-system|Notification System]]
- [[Userflow/Notifications/inbox|Inbox]]
- [[Userflow/Notifications/notification-preference-setup|Notification Preference Setup]]

### Verification

```bash
dotnet test ONEVO.sln --filter Notifications
```

---

## Open Backend Contracts

- [ ] Confirm exact auth user ID and tenant context interfaces from DEV1.
- [ ] Confirm shared encryption abstraction from DEV1 for Google/Outlook calendar token storage.
