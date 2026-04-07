# Userflow Index

**Purpose:** End-to-end user flows organized by feature area. Each flow specifies the **required permissions** — since roles are dynamic (created via [[job-family-setup|Job Family]]) and permissions are assigned per role or per employee, flows are **permission-based, not role-based**.

**How to read:** Each flow file describes what a user with the listed permission(s) experiences step-by-step, including UI actions, API calls, backend logic, and database changes.

**Key flow:** [[permission-assignment]] — how permissions get assigned to roles/employees, which unlocks all other flows.

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

See [[authorization|RBAC Overview]] for the full 90+ permission list.

---

## Flows by Feature Area

### Platform Setup — `settings:admin`, `billing:manage`
- [[tenant-provisioning]] — First-time tenant setup
- [[billing-subscription]] — Plan selection, payment, upgrade/downgrade
- [[sso-configuration]] — SSO provider setup (Google, Azure AD)
- [[feature-flag-management]] — Enable/disable modules per tenant
- [[tenant-branding]] — Logo, colors, custom domain

### Auth & Access — `roles:manage`, `users:manage`
- [[user-invitation]] — Invite users, assign initial role
- [[role-creation]] — Create custom role, pick permissions
- [[permission-assignment]] — Assign permissions to role or specific employee
- [[login-flow]] — Login, MFA prompt, session creation
- [[mfa-setup]] — Employee enables MFA on own account
- [[password-reset]] — Self-service + admin-initiated
- [[gdpr-consent]] — Consent collection flow

### Org Structure — `org:manage`
- [[legal-entity-setup]] — Create/configure legal entities
- [[department-hierarchy]] — Create departments, set parent-child
- [[job-family-setup]] — Job families, levels, salary bands
- [[team-creation]] — Teams, team leads
- [[cost-center-setup]] — Cost center management

### Employee Management — `employees:read/write/delete`
- [[employee-onboarding]] — Full hire flow: create profile → assign role → onboarding checklist
- [[profile-management]] — View/edit employee profile (own or by permission)
- [[compensation-setup]] — Salary, allowances, bank details
- [[employee-transfer]] — Department/team/location transfer
- [[employee-promotion]] — Title change, salary revision
- [[employee-offboarding]] — Exit workflow: checklist → access revoke → final pay
- [[dependent-management]] — Add/edit dependents and emergency contacts
- [[qualification-tracking]] — Education, certifications, experience

### Leave — `leave:create/approve/manage`
- [[leave-type-configuration]] — Admin creates leave types (annual, sick, etc.)
- [[leave-policy-setup]] — Country-specific policies, accrual rules
- [[leave-entitlement-assignment]] — Assign entitlements to employees
- [[leave-request-submission]] — Employee submits leave request
- [[leave-approval]] — Approver reviews, approves/rejects
- [[leave-cancellation]] — Employee or admin cancels leave
- [[leave-balance-view]] — View remaining balances, history

### Workforce Presence — `attendance:read/write/approve`
- [[shift-schedule-setup]] — Define shifts, assign schedules
- [[presence-session-view]] — View clock-in/out, active sessions
- [[attendance-correction]] — Submit/approve attendance corrections
- [[overtime-management]] — Overtime requests and approval
- [[break-tracking]] — Break policy and tracking
- [[biometric-device-setup]] — Register devices, enroll employees

### Performance — `performance:read/write/manage`
- [[review-cycle-setup]] — Admin creates review cycle
- [[self-assessment]] — Employee fills self-review
- [[manager-review]] — Manager evaluates team members
- [[peer-feedback]] — 360-degree feedback flow
- [[goal-setting]] — OKR/goal creation and tracking
- [[improvement-plan]] — PIP creation and monitoring
- [[recognition-submission]] — Peer/manager recognition
- [[succession-planning]] — Identify and track successors

### Payroll — `payroll:read/write/run/approve`
- [[payroll-provider-setup]] — Configure external payroll provider
- [[tax-configuration]] — Country-specific tax rules
- [[allowance-setup]] — Define allowance types, assign
- [[pension-configuration]] — Pension scheme setup
- [[payroll-run-execution]] — Execute payroll run, review, approve
- [[payroll-adjustment]] — Post-run corrections
- [[payslip-view]] — Employee views own payslip

### Skills & Learning — `skills:read/write/validate/manage`
- [[skill-taxonomy-setup]] — Define skill categories and levels
- [[employee-skill-declaration]] — Employee adds own skills
- [[skill-assessment]] — Manager validates/assesses skills
- [[course-enrollment]] — Browse and enroll in courses
- [[certification-tracking]] — Upload/verify certifications
- [[development-plan]] — Create learning path

### Documents — `documents:read/write/manage`
- [[document-upload]] — Upload company/employee documents
- [[document-access]] — View documents (own or by permission)
- [[document-acknowledgement]] — Employee acknowledges policy docs
- [[template-management]] — Create/manage document templates
- [[document-versioning]] — Version history, rollback

### Workforce Intelligence — `workforce:view/manage`, `monitoring:configure`
- [[monitoring-configuration]] — Enable/disable monitoring per tenant/employee
- [[live-dashboard]] — Real-time workforce presence view
- [[activity-snapshot-view]] — View app usage, screenshots, meetings
- [[identity-verification-setup]] — Configure photo capture intervals
- [[identity-verification-review]] — Review flagged verification failures
- [[agent-deployment]] — Install, register, monitor desktop agent

### Exception Engine — `exceptions:view/manage/acknowledge`
- [[exception-rule-setup]] — Define anomaly detection rules
- [[alert-review]] — View and acknowledge alerts
- [[escalation-chain-setup]] — Configure escalation paths
- [[exception-dashboard]] — Overview of all active exceptions

### Analytics & Reporting — `analytics:view/export`, `reports:read/create`
- [[productivity-dashboard]] — Daily/weekly/monthly analytics view
- [[workforce-snapshot]] — Point-in-time org snapshots
- [[report-creation]] — Build custom reports
- [[scheduled-report-setup]] — Automate report delivery
- [[data-export]] — CSV/Excel export flow

### Grievance — `grievance:read/write/manage`
- [[grievance-filing]] — Employee files grievance
- [[grievance-investigation]] — Admin reviews, assigns investigator
- [[disciplinary-action]] — Issue disciplinary action

### Expense — `expense:read/create/approve/manage`
- [[expense-claim-submission]] — Employee submits expense with receipts
- [[expense-approval]] — Approver reviews expense claims
- [[expense-category-setup]] — Admin defines expense categories

### Calendar — `calendar:read/write`
- [[calendar-event-creation]] — Create events (meetings, holidays)
- [[conflict-detection]] — View scheduling conflicts

### Notifications — `notifications:read/manage`
- [[notification-preference-setup]] — User configures notification channels
- [[notification-view]] — View/dismiss notifications

### Configuration — `settings:read/admin`
- [[tenant-settings]] — Global tenant configuration
- [[monitoring-toggles]] — Per-feature monitoring on/off
- [[employee-override]] — Override settings for specific employee
- [[retention-policy-setup]] — Data retention configuration

---

## Cross-References

| Layer | Folder | Purpose |
|:------|:-------|:--------|
| **What users do** | `Userflow/` (this folder) | End-to-end flows by permission |
| **What to build** | [[modules/]] | Feature specs, DB schema, APIs |
| **How to build (backend)** | [[backend/]] | .NET architecture, patterns |
| **How to build (frontend)** | [[frontend/]] | Next.js structure, components |
| **Data layer** | [[database/]] | Migrations, performance |
| **Code rules** | [[code-standards/]] | Naming, git, logging |
| **Security** | [[security/]] | Auth, RBAC, compliance |
| **Infrastructure** | [[infrastructure/]] | CI/CD, monitoring, multi-tenancy |
