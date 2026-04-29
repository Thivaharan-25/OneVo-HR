# Userflow Index

**Purpose:** End-to-end user flows organized by feature area. Each flow specifies the **required permissions** — since roles are dynamic (created via [[Userflow/Org-Structure/job-family-setup|Job Family]]) and permissions are assigned per role or per employee, flows are **permission-based, not role-based**.

**How to read:** Each flow file describes what a user with the listed permission(s) experiences step-by-step, including UI actions, API calls, backend logic, and database changes.

**Key flow:** [[Userflow/Auth-Access/permission-assignment|Permission Assignment]] — how permissions get assigned to roles/employees, which unlocks all other flows.

---

## Naming Conventions

All user-facing labels use simple, everyday language. When writing userflows, use the user-facing name, not the system/module name.

| System Module | User-Facing Label |
|:--------------|:------------------|
| Exception Engine | Alerts |
| Workforce Intelligence | Workforce |
| Compensation | Pay & Benefits |
| Grievance | Complaints |
| Presence | Online Status |
| Verification | ID Checks |
| Productivity Dashboard | Work Insights |
| Approvals | Inbox |
| Command Palette | Quick Search |

---

## Permission Legend

| Permission Pattern | Scope |
|:-------------------|:------|
| `*:read` | View data |
| `*:write` | Create/edit data |
| `*:delete` | Remove data |
| `*:manage` | Full control (CRUD + config) |
| `*:approve` | Approval workflow |
| `*:read-own` | View own data only |
| `*:read-team` | View team data |

See [[frontend/cross-cutting/authorization|RBAC Overview]] for the full 90+ permission list.

---

## Status & Priority Legend

| Status | Meaning |
|:-------|:--------|
| `Documented` | Flow file exists with full steps, errors, events |
| `Stub` | Flow file exists but incomplete (missing sections) |
| `Planned` | No file yet — identified but not written |

| Priority | Meaning |
|:---------|:--------|
| `MUST` | Core flow — product doesn't work without it |
| `SHOULD` | Important flow — expected by most users |
| `COULD` | Nice-to-have — enhances experience but not critical |

**Audit tool:** [[Userflow/GAP-AUDIT-CHECKLIST|Gap Audit Checklist]] — 6-category checklist for reviewing flows for missing paths

---

## Flows by Feature Area

### Platform Setup — `settings:admin`, `billing:manage`

| Flow | Description | Status | Priority |
|:-----|:------------|:-------|:---------|
| [[Userflow/Platform-Setup/tenant-provisioning\|Tenant Provisioning]] | First-time tenant setup | Documented | MUST |
| [[Userflow/Platform-Setup/billing-subscription\|Billing Subscription]] | Plan selection, payment, upgrade/downgrade | Documented | MUST |
| [[Userflow/Platform-Setup/sso-configuration\|SSO Configuration]] | SSO provider setup (Google, Azure AD) | Documented | SHOULD |
| [[Userflow/Platform-Setup/feature-flag-management\|Feature Flag Management]] | Enable/disable modules per tenant | Documented | MUST |
| [[frontend/design-system/theming/tenant-branding\|Tenant Branding]] | Logo, colors, custom domain | Documented | COULD |

### Auth & Access — `roles:manage`, `users:manage`

| Flow | Description | Status | Priority |
|:-----|:------------|:-------|:---------|
| [[Userflow/Auth-Access/user-invitation\|User Invitation]] | Invite users, assign initial role | Documented | MUST |
| [[Userflow/Auth-Access/role-creation\|Role Creation]] | Create custom role, pick permissions | Documented | MUST |
| [[Userflow/Auth-Access/permission-assignment\|Permission Assignment]] | Assign permissions to role or specific employee | Documented | MUST |
| [[Userflow/Auth-Access/login-flow\|Login Flow]] | Login, MFA prompt, session creation | Documented | MUST |
| [[Userflow/Auth-Access/mfa-setup\|MFA Setup]] | Employee enables MFA on own account | Documented | SHOULD |
| [[Userflow/Auth-Access/password-reset\|Password Reset]] | Self-service + admin-initiated | Documented | MUST |
| [[Userflow/Auth-Access/gdpr-consent\|GDPR Consent]] | Consent collection flow | Documented | MUST |

### Org Structure — `org:manage`

| Flow | Description | Status | Priority |
|:-----|:------------|:-------|:---------|
| [[Userflow/Org-Structure/legal-entity-setup\|Legal Entity Setup]] | Create/configure legal entities | Documented | MUST |
| [[Userflow/Org-Structure/department-hierarchy\|Department Hierarchy]] | Create departments, set parent-child | Documented | MUST |
| [[Userflow/Org-Structure/job-family-setup\|Job Family Setup]] | Job families, levels, salary bands | Documented | MUST |
| [[Userflow/Org-Structure/team-creation\|Team Creation]] | Teams, team leads | Documented | SHOULD |
| [[Userflow/Org-Structure/cost-center-setup\|Cost Center Setup]] | Cost center management | Documented | SHOULD |

### People — `employees:read/write/delete`

| Flow | Description | Status | Priority |
|:-----|:------------|:-------|:---------|
| [[Userflow/Employee-Management/employee-onboarding\|Employee Onboarding]] | Full hire flow: create profile → assign role → onboarding checklist | Documented | MUST |
| [[Userflow/Employee-Management/profile-management\|Profile Management]] | View/edit employee profile (own or by permission) | Documented | MUST |
| [[Userflow/Employee-Management/compensation-setup\|Compensation Setup]] | Salary, allowances, bank details | Documented | MUST |
| [[Userflow/Employee-Management/employee-transfer\|Employee Transfer]] | Department/team/location transfer | Documented | SHOULD |
| [[Userflow/Employee-Management/employee-promotion\|Employee Promotion]] | Title change, salary revision | Documented | SHOULD |
| [[Userflow/Employee-Management/employee-offboarding\|Employee Offboarding]] | Exit workflow: checklist → access revoke → final pay | Documented | MUST |
| [[Userflow/Employee-Management/dependent-management\|Dependent Management]] | Add/edit dependents and emergency contacts | Documented | SHOULD |
| [[Userflow/Employee-Management/qualification-tracking\|Qualification Tracking]] | Education, certifications, experience | Documented | COULD |

### Leave — `leave:create/approve/manage`

| Flow | Description | Status | Priority |
|:-----|:------------|:-------|:---------|
| [[Userflow/Leave/leave-type-configuration\|Leave Type Configuration]] | Admin creates leave types (annual, sick, etc.) | Documented | MUST |
| [[Userflow/Leave/leave-policy-setup\|Leave Policy Setup]] | Country-specific policies, accrual rules | Documented | MUST |
| [[Userflow/Leave/leave-entitlement-assignment\|Leave Entitlement Assignment]] | Assign entitlements to employees | Documented | MUST |
| [[Userflow/Leave/leave-request-submission\|Leave Request Submission]] | Employee submits leave request | Documented | MUST |
| [[Userflow/Leave/leave-approval\|Leave Approval]] | Approver reviews, approves/rejects | Documented | MUST |
| [[Userflow/Leave/leave-cancellation\|Leave Cancellation]] | Employee or admin cancels leave | Documented | SHOULD |
| [[Userflow/Leave/leave-balance-view\|Leave Balance View]] | View remaining balances, history | Documented | MUST |

### Workforce Presence — `attendance:read/write/approve`

| Flow | Description | Status | Priority |
|:-----|:------------|:-------|:---------|
| [[Userflow/Workforce-Presence/shift-schedule-setup\|Shift Schedule Setup]] | Define shifts, assign schedules — UI entry via Calendar sidebar, backend in Workforce Presence | Documented | MUST |
| [[Userflow/Workforce-Presence/presence-overview\|Presence Overview]] | Live card grid, agent escalation sort, card anatomy | Documented | MUST |
| [[Userflow/Workforce-Presence/employee-activity-detail\|Employee Activity Detail]] | Activity timeline, filters (date/task/project), productivity breakdown | Documented | MUST |
| [[Userflow/Workforce-Presence/presence-session-view\|Presence Session View]] | View clock-in/out, active sessions | Documented | MUST |
| [[Userflow/Workforce-Presence/attendance-correction\|Attendance Correction]] | Submit/approve attendance corrections | Documented | SHOULD |
| [[Userflow/Workforce-Presence/overtime-management\|Overtime Management]] | Overtime requests and approval | Documented | SHOULD |
| [[Userflow/Workforce-Presence/break-tracking\|Break Tracking]] | Break policy and tracking | Documented | COULD |
| [[Userflow/Workforce-Presence/biometric-device-setup\|Biometric Device Setup]] | Register devices, enroll employees | Documented | COULD |

### Performance — `performance:read/write/manage`

| Flow | Description | Status | Priority |
|:-----|:------------|:-------|:---------|
| [[Userflow/Performance/review-cycle-setup\|Review Cycle Setup]] | Admin creates review cycle | Documented | MUST |
| [[Userflow/Performance/self-assessment\|Self Assessment]] | Employee fills self-review | Documented | MUST |
| [[Userflow/Performance/manager-review\|Manager Review]] | Manager evaluates team members | Documented | MUST |
| [[Userflow/Performance/peer-feedback\|Peer Feedback]] | 360-degree feedback flow | Documented | SHOULD |
| [[Userflow/Performance/goal-setting\|Goal Setting]] | OKR/goal creation and tracking | Documented | MUST |
| [[Userflow/Performance/improvement-plan\|Improvement Plan]] | PIP creation and monitoring | Documented | SHOULD |
| [[Userflow/Performance/recognition-submission\|Recognition Submission]] | Peer/manager recognition | Documented | COULD |
| [[Userflow/Performance/succession-planning\|Succession Planning]] | Identify and track successors | Documented | COULD |

### Payroll — `payroll:read/write/run/approve`

| Flow | Description | Status | Priority |
|:-----|:------------|:-------|:---------|
| [[Userflow/Payroll/payroll-provider-setup\|Payroll Provider Setup]] | Configure external payroll provider | Documented | MUST |
| [[Userflow/Payroll/tax-configuration\|Tax Configuration]] | Country-specific tax rules | Documented | MUST |
| [[Userflow/Payroll/allowance-setup\|Allowance Setup]] | Define allowance types, assign | Documented | SHOULD |
| [[Userflow/Payroll/pension-configuration\|Pension Configuration]] | Pension scheme setup | Documented | SHOULD |
| [[Userflow/Payroll/payroll-run-execution\|Payroll Run Execution]] | Execute payroll run, review, approve | Documented | MUST |
| [[Userflow/Payroll/payroll-adjustment\|Payroll Adjustment]] | Post-run corrections | Documented | SHOULD |
| [[Userflow/Payroll/payslip-view\|Payslip View]] | Employee views own payslip | Documented | MUST |

### Skills & Learning — `skills:read/write/validate/manage`

| Flow | Description | Status | Priority |
|:-----|:------------|:-------|:---------|
| [[Userflow/Skills-Learning/skill-taxonomy-setup\|Skill Taxonomy Setup]] | Define skill categories and levels | Documented | MUST |
| [[Userflow/Skills-Learning/employee-skill-declaration\|Employee Skill Declaration]] | Employee adds own skills | Documented | SHOULD |
| [[Userflow/Skills-Learning/skill-assessment\|Skill Assessment]] | Manager validates/assesses skills | Documented | SHOULD |
| [[Userflow/Skills-Learning/course-enrollment\|Course Enrollment]] | Browse and enroll in courses | Documented | SHOULD |
| [[Userflow/Skills-Learning/certification-tracking\|Certification Tracking]] | Upload/verify certifications | Documented | COULD |
| [[Userflow/Skills-Learning/development-plan\|Development Plan]] | Create learning path | Documented | SHOULD |

### Documents — `documents:read/write/manage`

| Flow | Description | Status | Priority |
|:-----|:------------|:-------|:---------|
| [[Userflow/Documents/document-upload\|Document Upload]] | Upload company/employee documents | Documented | MUST |
| [[Userflow/Documents/document-access\|Document Access]] | View documents (own or by permission) | Documented | MUST |
| [[Userflow/Documents/document-acknowledgement\|Document Acknowledgement]] | Employee acknowledges policy docs | Documented | SHOULD |
| [[Userflow/Documents/template-management\|Template Management]] | Create/manage document templates | Documented | SHOULD |
| [[Userflow/Documents/document-versioning\|Document Versioning]] | Version history, rollback | Documented | COULD |

### Workforce Intelligence — `workforce:view/manage`, `monitoring:configure`

| Flow | Description | Status | Priority |
|:-----|:------------|:-------|:---------|
| [[Userflow/Workforce-Intelligence/monitoring-configuration\|Monitoring Configuration]] | Enable/disable monitoring per tenant/employee | Documented | MUST |
| [[Userflow/Workforce-Intelligence/live-dashboard\|Live Dashboard]] | Real-time workforce presence view | Documented | MUST |
| [[Userflow/Workforce-Intelligence/activity-snapshot-view\|Activity Snapshot View]] | View app usage, screenshots, meetings | Documented | SHOULD |
| [[Userflow/Workforce-Intelligence/identity-verification-setup\|Identity Verification Setup]] | Configure photo capture intervals | Documented | SHOULD |
| [[Userflow/Workforce-Intelligence/identity-verification-review\|Identity Verification Review]] | Review flagged verification failures | Documented | SHOULD |
| [[Userflow/Workforce-Intelligence/agent-deployment\|Agent Deployment]] | Install, register, monitor desktop agent | Documented | MUST |

### Exception Engine — `exceptions:view/manage/acknowledge`

| Flow | Description | Status | Priority |
|:-----|:------------|:-------|:---------|
| [[Userflow/Exception-Engine/exception-rule-setup\|Exception Rule Setup]] | Define anomaly detection rules | Documented | MUST |
| [[Userflow/Exception-Engine/alert-review\|Alert Review]] | View and acknowledge alerts | Documented | MUST |
| [[Userflow/Exception-Engine/escalation-chain-setup\|Escalation Chain Setup]] | Configure escalation paths | Documented | SHOULD |
| [[Userflow/Exception-Engine/exception-dashboard\|Alerts Overview]] | Overview of all active alerts | Documented | MUST |

### Analytics & Reporting — `analytics:view/export`, `reports:read/create`

| Flow | Description | Status | Priority |
|:-----|:------------|:-------|:---------|
| [[Userflow/Analytics-Reporting/productivity-dashboard\|Productivity Dashboard]] | Daily/weekly/monthly analytics view | Documented | MUST |
| [[Userflow/Analytics-Reporting/workforce-snapshot\|Workforce Snapshot]] | Point-in-time org snapshots | Documented | SHOULD |
| [[Userflow/Analytics-Reporting/report-creation\|Report Creation]] | Build custom reports | Documented | SHOULD |
| [[Userflow/Analytics-Reporting/scheduled-report-setup\|Scheduled Report Setup]] | Automate report delivery | Documented | COULD |
| [[Userflow/Analytics-Reporting/data-export\|Data Export]] | CSV/Excel export flow | Documented | SHOULD |

### Grievance — `grievance:read/write/manage`

| Flow | Description | Status | Priority |
|:-----|:------------|:-------|:---------|
| [[Userflow/Grievance/grievance-filing\|Grievance Filing]] | Employee files grievance | Documented | MUST |
| [[Userflow/Grievance/grievance-investigation\|Grievance Investigation]] | Admin reviews, assigns investigator | Documented | MUST |
| [[Userflow/Grievance/disciplinary-action\|Disciplinary Action]] | Issue disciplinary action | Documented | SHOULD |

### Expense — `expense:read/create/approve/manage`

| Flow | Description | Status | Priority |
|:-----|:------------|:-------|:---------|
| [[Userflow/Expense/expense-claim-submission\|Expense Claim Submission]] | Employee submits expense with receipts | Documented | MUST |
| [[Userflow/Expense/expense-approval\|Expense Approval]] | Approver reviews expense claims | Documented | MUST |
| [[Userflow/Expense/expense-category-setup\|Expense Category Setup]] | Admin defines expense categories | Documented | SHOULD |

### Calendar — `calendar:read/write`

| Flow | Description | Status | Priority |
|:-----|:------------|:-------|:---------|
| [[Userflow/Calendar/calendar-event-creation\|Calendar Event Creation]] | Create events (meetings, holidays) | Documented | SHOULD |
| [[Userflow/Calendar/conflict-detection\|Conflict Detection]] | View scheduling conflicts | Documented | COULD |

### Notifications — `notifications:read/manage`

| Flow | Description | Status | Priority |
|:-----|:------------|:-------|:---------|
| [[Userflow/Notifications/notification-preference-setup\|Notification Preference Setup]] | User configures notification channels | Documented | SHOULD |
| [[Userflow/Notifications/notification-view\|Notification View]] | View/dismiss notifications | Documented | MUST |

### Cross-Module Scenarios

These flows track chain reactions across multiple modules — when one action triggers downstream effects in 3+ modules.

| Flow | Description | Status | Priority |
|:-----|:------------|:-------|:---------|
| [[Userflow/Cross-Module/employee-full-onboarding\|Employee Full Onboarding]] | Hire → auth + leave + attendance + payroll + docs setup | Documented | MUST |
| [[Userflow/Cross-Module/employee-full-offboarding\|Employee Full Offboarding]] | Exit → access revoke + final pay + data retention | Documented | MUST |
| [[Userflow/Cross-Module/leave-request-and-approval-chain\|Leave Request & Approval Chain]] | Request → calendar + attendance override + payroll deduction | Documented | MUST |
| [[Userflow/Cross-Module/monthly-payroll-run-chain\|Monthly Payroll Run Chain]] | Attendance + leave + expense data → calculation → payslips | Documented | MUST |
| [[Userflow/Cross-Module/attendance-dispute-chain\|Attendance Dispute & Correction Chain]] | Employee/system-detected → correction → payroll adjustment | Documented | SHOULD |
| [[Userflow/Cross-Module/performance-review-cycle-chain\|Performance Review Cycle Chain]] | Cycle → assessments → compensation + learning + succession | Documented | SHOULD |
| [[Userflow/Cross-Module/employee-transfer-chain\|Employee Transfer Chain]] | Transfer → reporting line + shift + leave policy + payroll + access | Documented | SHOULD |

### Configuration — `settings:read/admin`

| Flow | Description | Status | Priority |
|:-----|:------------|:-------|:---------|
| [[Userflow/Configuration/tenant-settings\|Tenant Settings]] | Global tenant configuration | Documented | MUST |
| [[Userflow/Configuration/monitoring-toggles\|Monitoring Toggles]] | Per-feature monitoring on/off | Documented | SHOULD |
| [[Userflow/Configuration/employee-override\|Employee Override]] | Override settings for specific employee | Documented | SHOULD |
| [[Userflow/Configuration/retention-policy-setup\|Retention Policy Setup]] | Data retention configuration | Documented | SHOULD |

### Work Management — `workforce:read` + feature-specific permissions

| Flow | Description | Status | Priority |
|:-----|:------------|:-------|:---------|
| [[Userflow/Work-Management/wm-overview\|WMS Overview]] | Module map, ownership, HR integration points | Documented | MUST |
| [[Userflow/Work-Management/project-flow\|Project Management]] | Project CRUD, membership, milestones, change control | Documented | MUST |
| [[Userflow/Work-Management/task-flow\|Task Management]] | Task lifecycle, bugs, submission, approval | Documented | MUST |
| [[Userflow/Work-Management/planning-flow\|Planning — Sprints and Boards]] | Sprints, boards, roadmap, releases | Documented | MUST |
| [[Userflow/Work-Management/goals-okr-flow\|Goals and OKRs]] | Objectives, key results, check-ins, alignment | Documented | MUST |
| [[Userflow/Work-Management/time-tracking-flow\|Time Tracking]] | Time logs, timesheets, overtime and attendance connections | Documented | MUST |
| [[Userflow/Work-Management/resource-flow\|Resource Management]] | Capacity, skills, allocation planning | Documented | MUST |

### Chat — `chat:read`

| Flow | Description | Status | Priority |
|:-----|:------------|:-------|:---------|
| [[Userflow/Chat/chat-overview\|Chat Overview]] | Channels, DMs, messages, reactions, file attachments | Documented | MUST |

---

## Cross-References

| Layer | Folder | Purpose |
|:------|:-------|:--------|
| **What users do** | `Userflow/` (this folder) | End-to-end flows by permission |
| **What to build** | [[backend/module-catalog\|Module Catalog]] | Feature specs, DB schema, APIs |
| **How to build (backend)** | [[backend/README\|Backend]] | .NET architecture, patterns |
| **How to build (frontend)** | [[frontend/README\|Frontend]] | Vite + React structure, components |
| **Data layer** | [[database/README\|Database]] | Migrations, performance |
| **Code rules** | [[code-standards/README\|Code Standards]] | Naming, git, logging |
| **Security** | [[security/README\|Security]] | Auth, RBAC, compliance |
| **Infrastructure** | [[infrastructure/README\|Infrastructure]] | CI/CD, monitoring, multi-tenancy |
