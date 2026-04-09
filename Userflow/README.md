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

## Flows by Feature Area

### Platform Setup — `settings:admin`, `billing:manage`
- [[Userflow/Platform-Setup/tenant-provisioning|Tenant Provisioning]] — First-time tenant setup
- [[Userflow/Platform-Setup/billing-subscription|Billing Subscription]] — Plan selection, payment, upgrade/downgrade
- [[Userflow/Platform-Setup/sso-configuration|Sso Configuration]] — SSO provider setup (Google, Azure AD)
- [[Userflow/Platform-Setup/feature-flag-management|Feature Flag Management]] — Enable/disable modules per tenant
- [[frontend/design-system/theming/tenant-branding|Tenant Branding]] — Logo, colors, custom domain

### Auth & Access — `roles:manage`, `users:manage`
- [[Userflow/Auth-Access/user-invitation|User Invitation]] — Invite users, assign initial role
- [[Userflow/Auth-Access/role-creation|Role Creation]] — Create custom role, pick permissions
- [[Userflow/Auth-Access/permission-assignment|Permission Assignment]] — Assign permissions to role or specific employee
- [[Userflow/Auth-Access/login-flow|Login Flow]] — Login, MFA prompt, session creation
- [[Userflow/Auth-Access/mfa-setup|Mfa Setup]] — Employee enables MFA on own account
- [[Userflow/Auth-Access/password-reset|Password Reset]] — Self-service + admin-initiated
- [[Userflow/Auth-Access/gdpr-consent|Gdpr Consent]] — Consent collection flow

### Org Structure — `org:manage`
- [[Userflow/Org-Structure/legal-entity-setup|Legal Entity Setup]] — Create/configure legal entities
- [[Userflow/Org-Structure/department-hierarchy|Department Hierarchy]] — Create departments, set parent-child
- [[Userflow/Org-Structure/job-family-setup|Job Family Setup]] — Job families, levels, salary bands
- [[Userflow/Org-Structure/team-creation|Team Creation]] — Teams, team leads
- [[Userflow/Org-Structure/cost-center-setup|Cost Center Setup]] — Cost center management

### People — `employees:read/write/delete`
- [[Userflow/Employee-Management/employee-onboarding|Employee Onboarding]] — Full hire flow: create profile → assign role → onboarding checklist
- [[Userflow/Employee-Management/profile-management|Profile Management]] — View/edit employee profile (own or by permission)
- [[Userflow/Employee-Management/compensation-setup|Compensation Setup]] — Salary, allowances, bank details
- [[Userflow/Employee-Management/employee-transfer|Employee Transfer]] — Department/team/location transfer
- [[Userflow/Employee-Management/employee-promotion|Employee Promotion]] — Title change, salary revision
- [[Userflow/Employee-Management/employee-offboarding|Employee Offboarding]] — Exit workflow: checklist → access revoke → final pay
- [[Userflow/Employee-Management/dependent-management|Dependent Management]] — Add/edit dependents and emergency contacts
- [[Userflow/Employee-Management/qualification-tracking|Qualification Tracking]] — Education, certifications, experience

### Leave — `leave:create/approve/manage`
- [[Userflow/Leave/leave-type-configuration|Leave Type Configuration]] — Admin creates leave types (annual, sick, etc.)
- [[Userflow/Leave/leave-policy-setup|Leave Policy Setup]] — Country-specific policies, accrual rules
- [[Userflow/Leave/leave-entitlement-assignment|Leave Entitlement Assignment]] — Assign entitlements to employees
- [[Userflow/Leave/leave-request-submission|Leave Request Submission]] — Employee submits leave request
- [[Userflow/Leave/leave-approval|Leave Approval]] — Approver reviews, approves/rejects
- [[Userflow/Leave/leave-cancellation|Leave Cancellation]] — Employee or admin cancels leave
- [[Userflow/Leave/leave-balance-view|Leave Balance View]] — View remaining balances, history

### Workforce Presence — `attendance:read/write/approve`
- [[Userflow/Workforce-Presence/shift-schedule-setup|Shift Schedule Setup]] — Define shifts, assign schedules
- [[Userflow/Workforce-Presence/presence-session-view|Presence Session View]] — View clock-in/out, active sessions
- [[Userflow/Workforce-Presence/attendance-correction|Attendance Correction]] — Submit/approve attendance corrections
- [[Userflow/Workforce-Presence/overtime-management|Overtime Management]] — Overtime requests and approval
- [[Userflow/Workforce-Presence/break-tracking|Break Tracking]] — Break policy and tracking
- [[Userflow/Workforce-Presence/biometric-device-setup|Biometric Device Setup]] — Register devices, enroll employees

### Performance — `performance:read/write/manage`
- [[Userflow/Performance/review-cycle-setup|Review Cycle Setup]] — Admin creates review cycle
- [[Userflow/Performance/self-assessment|Self Assessment]] — Employee fills self-review
- [[Userflow/Performance/manager-review|Manager Review]] — Manager evaluates team members
- [[Userflow/Performance/peer-feedback|Peer Feedback]] — 360-degree feedback flow
- [[Userflow/Performance/goal-setting|Goal Setting]] — OKR/goal creation and tracking
- [[Userflow/Performance/improvement-plan|Improvement Plan]] — PIP creation and monitoring
- [[Userflow/Performance/recognition-submission|Recognition Submission]] — Peer/manager recognition
- [[Userflow/Performance/succession-planning|Succession Planning]] — Identify and track successors

### Payroll — `payroll:read/write/run/approve`
- [[Userflow/Payroll/payroll-provider-setup|Payroll Provider Setup]] — Configure external payroll provider
- [[Userflow/Payroll/tax-configuration|Tax Configuration]] — Country-specific tax rules
- [[Userflow/Payroll/allowance-setup|Allowance Setup]] — Define allowance types, assign
- [[Userflow/Payroll/pension-configuration|Pension Configuration]] — Pension scheme setup
- [[Userflow/Payroll/payroll-run-execution|Payroll Run Execution]] — Execute payroll run, review, approve
- [[Userflow/Payroll/payroll-adjustment|Payroll Adjustment]] — Post-run corrections
- [[Userflow/Payroll/payslip-view|Payslip View]] — Employee views own payslip

### Skills & Learning — `skills:read/write/validate/manage`
- [[Userflow/Skills-Learning/skill-taxonomy-setup|Skill Taxonomy Setup]] — Define skill categories and levels
- [[Userflow/Skills-Learning/employee-skill-declaration|Employee Skill Declaration]] — Employee adds own skills
- [[Userflow/Skills-Learning/skill-assessment|Skill Assessment]] — Manager validates/assesses skills
- [[Userflow/Skills-Learning/course-enrollment|Course Enrollment]] — Browse and enroll in courses
- [[Userflow/Skills-Learning/certification-tracking|Certification Tracking]] — Upload/verify certifications
- [[Userflow/Skills-Learning/development-plan|Development Plan]] — Create learning path

### Documents — `documents:read/write/manage`
- [[Userflow/Documents/document-upload|Document Upload]] — Upload company/employee documents
- [[Userflow/Documents/document-access|Document Access]] — View documents (own or by permission)
- [[Userflow/Documents/document-acknowledgement|Document Acknowledgement]] — Employee acknowledges policy docs
- [[Userflow/Documents/template-management|Template Management]] — Create/manage document templates
- [[Userflow/Documents/document-versioning|Document Versioning]] — Version history, rollback

### Workforce Intelligence — `workforce:view/manage`, `monitoring:configure`
- [[Userflow/Workforce-Intelligence/monitoring-configuration|Monitoring Configuration]] — Enable/disable monitoring per tenant/employee
- [[Userflow/Workforce-Intelligence/live-dashboard|Live Dashboard]] — Real-time workforce presence view
- [[Userflow/Workforce-Intelligence/activity-snapshot-view|Activity Snapshot View]] — View app usage, screenshots, meetings
- [[Userflow/Workforce-Intelligence/identity-verification-setup|Identity Verification Setup]] — Configure photo capture intervals
- [[Userflow/Workforce-Intelligence/identity-verification-review|Identity Verification Review]] — Review flagged verification failures
- [[Userflow/Workforce-Intelligence/agent-deployment|Agent Deployment]] — Install, register, monitor desktop agent

### Exception Engine — `exceptions:view/manage/acknowledge`
- [[Userflow/Exception-Engine/exception-rule-setup|Exception Rule Setup]] — Define anomaly detection rules
- [[Userflow/Exception-Engine/alert-review|Alert Review]] — View and acknowledge alerts
- [[Userflow/Exception-Engine/escalation-chain-setup|Escalation Chain Setup]] — Configure escalation paths
- [[Userflow/Exception-Engine/exception-dashboard|Alerts Overview]] — Overview of all active alerts

### Analytics & Reporting — `analytics:view/export`, `reports:read/create`
- [[Userflow/Analytics-Reporting/productivity-dashboard|Productivity Dashboard]] — Daily/weekly/monthly analytics view
- [[Userflow/Analytics-Reporting/workforce-snapshot|Workforce Snapshot]] — Point-in-time org snapshots
- [[Userflow/Analytics-Reporting/report-creation|Report Creation]] — Build custom reports
- [[Userflow/Analytics-Reporting/scheduled-report-setup|Scheduled Report Setup]] — Automate report delivery
- [[Userflow/Analytics-Reporting/data-export|Data Export]] — CSV/Excel export flow

### Grievance — `grievance:read/write/manage`
- [[Userflow/Grievance/grievance-filing|Grievance Filing]] — Employee files grievance
- [[Userflow/Grievance/grievance-investigation|Grievance Investigation]] — Admin reviews, assigns investigator
- [[Userflow/Grievance/disciplinary-action|Disciplinary Action]] — Issue disciplinary action

### Expense — `expense:read/create/approve/manage`
- [[Userflow/Expense/expense-claim-submission|Expense Claim Submission]] — Employee submits expense with receipts
- [[Userflow/Expense/expense-approval|Expense Approval]] — Approver reviews expense claims
- [[Userflow/Expense/expense-category-setup|Expense Category Setup]] — Admin defines expense categories

### Calendar — `calendar:read/write`
- [[Userflow/Calendar/calendar-event-creation|Calendar Event Creation]] — Create events (meetings, holidays)
- [[Userflow/Calendar/conflict-detection|Conflict Detection]] — View scheduling conflicts

### Notifications — `notifications:read/manage`
- [[Userflow/Notifications/notification-preference-setup|Notification Preference Setup]] — User configures notification channels
- [[Userflow/Notifications/notification-view|Notification View]] — View/dismiss notifications

### Configuration — `settings:read/admin`
- [[Userflow/Configuration/tenant-settings|Tenant Settings]] — Global tenant configuration
- [[Userflow/Configuration/monitoring-toggles|Monitoring Toggles]] — Per-feature monitoring on/off
- [[Userflow/Configuration/employee-override|Employee Override]] — Override settings for specific employee
- [[Userflow/Configuration/retention-policy-setup|Retention Policy Setup]] — Data retention configuration

---

## Cross-References

| Layer | Folder | Purpose |
|:------|:-------|:--------|
| **What users do** | `Userflow/` (this folder) | End-to-end flows by permission |
| **What to build** | [[backend/module-catalog|Module Catalog]] | Feature specs, DB schema, APIs |
| **How to build (backend)** | [[backend/README|Backend]] | .NET architecture, patterns |
| **How to build (frontend)** | [[frontend/README|Frontend]] | Next.js structure, components |
| **Data layer** | [[database/README|Database]] | Migrations, performance |
| **Code rules** | [[code-standards/README|Code Standards]] | Naming, git, logging |
| **Security** | [[security/README|Security]] | Auth, RBAC, compliance |
| **Infrastructure** | [[infrastructure/README|Infrastructure]] | CI/CD, monitoring, multi-tenancy |
