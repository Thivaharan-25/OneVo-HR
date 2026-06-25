# Userflow Index

**Purpose:** End-to-end user flows organized by feature area. Each flow specifies the **required permissions**. Roles are dynamic tenant security roles, and permissions are assigned per role, per position-generated grant, or per employee override, so flows are **permission-based, not role-based**.

**How to read:** Each flow file describes what a user with the listed permission(s) experiences step-by-step, including UI actions, API calls, backend logic, and database changes.

**Key flow:** [[Userflow/Auth-Access/permission-assignment|Permission Assignment]] - how permissions get assigned to roles/employees, which unlocks all other flows.

---

## Naming Conventions

All user-facing labels use simple, everyday language. When writing userflows, use the user-facing name, not the system/module name.

| System Module | User-Facing Label |
|:--------------|:------------------|
| Exception Engine | Alerts |
| Monitoring | Legacy intelligence naming |
| Compensation | Pay & Benefits |
| Grievance | Complaints |
| Presence | Online Status |
| Verification | ID Checks |
| Productivity Dashboard | Work Insights |
| Approvals | Inbox |
| Workflow Automation | Phase 2 only |
| Command Palette | Quick Search |

---

## Permission Legend

| Permission Pattern | Coverage |
|:-------------------|:------|
| `*:read` | View data allowed by management coverage or own-record self-service rules, not by the permission code alone |
| `*:write` | Create/edit data |
| `*:delete` | Remove data |
| `*:manage` | Full control (CRUD + config) |
| `*:approve` | Approval workflow |
| `*:read-own` | View own data only (auto-grant, not role-assigned) |


See [[frontend/cross-cutting/authorization|RBAC Overview]] for the full 90+ permission list.

---

## Status & Priority Legend

| Status | Meaning |
|:-------|:--------|
| `Documented` | Flow file exists with full steps, errors, events |
| `Stub` | Flow file exists but incomplete (missing sections) |
| `Planned` | No file yet - identified but not written |

| Priority | Meaning |
|:---------|:--------|
| `MUST` | Core flow - product doesn't work without it |
| `SHOULD` | Important flow - expected by most users |
| `COULD` | Nice-to-have - enhances experience but not critical |

**Audit tool:** [[Userflow/GAP-AUDIT-CHECKLIST|Gap Audit Checklist]] - 6-category checklist for reviewing flows for missing paths

---

## Flows by Feature Area

### Platform Setup - `settings:admin`, `billing:manage`

| Flow | Description | Status | Priority |
|:-----|:------------|:-------|:---------|
| [[Userflow/Platform-Setup/tenant-provisioning\|Tenant Provisioning]] | First-time tenant setup | Documented | MUST |
| [[Userflow/Platform-Setup/billing-subscription\|Billing Subscription]] | Plan selection, payment, upgrade/downgrade | Documented | MUST |
| [[Userflow/Platform-Setup/sso-configuration\|SSO Configuration]] | SSO provider setup (Google, Azure AD) | Documented | SHOULD |
| [[Userflow/Platform-Setup/feature-flag-management\|Feature Flag Management]] | Enable/disable modules per tenant | Documented | MUST |
| [[Userflow/Platform-Setup/tenant-branding\|Tenant Branding]] | Logo, colors, tenant URL display | Documented | COULD |

### Auth & Access - `roles:manage`, `users:manage`

| Flow | Description | Status | Priority |
|:-----|:------------|:-------|:---------|
| [[Userflow/Auth-Access/user-invitation\|User Invitation]] | Invite users, assign initial role | Documented | MUST |
| [[Userflow/Auth-Access/role-creation\|Role Creation]] | Create custom role, pick permissions | Documented | MUST |
| [[Userflow/Auth-Access/permission-assignment\|Permission Assignment]] | Assign permissions to role or specific employee | Documented | MUST |
| [[Userflow/Auth-Access/login-flow\|Login Flow]] | Login, MFA prompt, session creation | Documented | MUST |
| [[Userflow/Auth-Access/mfa-setup\|MFA Setup]] | Employee enables MFA on own account | Documented | SHOULD |
| [[Userflow/Auth-Access/password-reset\|Password Reset]] | Self-service + admin-initiated | Documented | MUST |
| [[Userflow/Auth-Access/gdpr-consent\|Legal & Privacy Acceptance]] | Terms, privacy, monitoring notice, and consent flow | Documented | MUST |

### Org Structure - `org:manage`

| Flow | Description | Status | Priority |
|:-----|:------------|:-------|:---------|
| [[Userflow/Org-Structure/legal-entity-setup\|Legal Entity Setup]] | Configure single-company or multi-company legal entities | Documented | MUST |
| [[Userflow/Org-Structure/department-hierarchy\|Department Hierarchy]] | Create departments, set parent-child | Documented | MUST |

### People - `employees:read/write/delete`

| Flow | Description | Status | Priority |
|:-----|:------------|:-------|:---------|
| [[Userflow/Employee-Management/employee-onboarding\|Employee Onboarding]] | Full hire flow: create profile -> assign role -> onboarding checklist | Documented | MUST |
| [[Userflow/Employee-Management/profile-management\|Profile Management]] | View/edit employee profile (own or by permission) | Documented | MUST |
| [[Userflow/Employee-Management/compensation-setup\|Compensation Setup]] | Salary, allowances, bank details (Phase 2) | Documented | COULD |
| [[Userflow/Employee-Management/employee-promotion\|Employee Promotion]] | Title change, salary revision | Documented | SHOULD |
| [[Userflow/Employee-Management/employee-offboarding\|Employee Offboarding]] | Exit workflow: checklist -> access revoke -> final pay | Documented | MUST |
| [[Userflow/Employee-Management/dependent-management\|Dependent Management]] | Add/edit dependents and emergency contacts | Documented | SHOULD |
| [[Userflow/Employee-Management/qualification-tracking\|Qualification Tracking]] | Education, certifications, experience (Phase 2) | Documented | COULD |

### Data Import - `employees:write`

| Flow | Description | Status | Priority |
|:-----|:------------|:-------|:---------|
| [[Userflow/Data-Import/data-import-wizard\|Data Import Wizard]] | Bulk employee/org import from CSV or Excel; PeopleHR is Phase 2 | Documented | MUST |

### Time Off - `time_off:create/approve/manage`

| Flow | Description | Status | Priority |
|:-----|:------------|:-------|:---------|
| [[Userflow/Time-Off/time-off-type-configuration\|Time Off Type Configuration]] | Admin creates Time Off types (annual, sick, etc.) | Documented | MUST |
| [[Userflow/Time-Off/time-off-policy-setup\|Time Off Policy Setup]] | Country-specific policies, accrual rules | Documented | MUST |
| [[Userflow/Time-Off/time-off-entitlement-assignment\|Time Off Entitlement Assignment]] | Assign entitlements to employees | Documented | MUST |
| [[Userflow/Time-Off/time-off-request-submission\|Time Off Request Submission]] | Employee submits Time Off request | Documented | MUST |
| [[Userflow/Time-Off/time-off-approval\|Time Off Approval]] | Approver reviews, approves/rejects | Documented | MUST |
| [[Userflow/Time-Off/time-off-cancellation\|Time Off Cancellation]] | Employee or admin cancels Time Off | Documented | SHOULD |
| [[Userflow/Time-Off/time-off-balance-view\|Time Off Balance View]] | View remaining balances, history | Documented | MUST |

### Time & Attendance - `attendance:read/write/approve`

| Flow | Description | Status | Priority |
|:-----|:------------|:-------|:---------|
| [[Userflow/Time-Attendance/shift-schedule-setup\|Shift Schedule Setup]] | Define work schedules under Time & Attendance; backend in Time & Attendance | Documented | MUST |
| [[Userflow/Time-Attendance/presence-overview\|Presence Overview]] | Live card grid, agent escalation sort, card anatomy | Documented | MUST |
| [[Userflow/Time-Attendance/employee-activity-detail\|Employee Activity Detail]] | Activity timeline, filters (date/task/project), productivity breakdown | Documented | MUST |
| [[Userflow/Time-Attendance/presence-session-view\|Presence Session View]] | View clock-in/out, active sessions | Documented | MUST |
| [[Userflow/Time-Attendance/attendance-correction\|Attendance Correction]] | Submit/approve attendance corrections | Documented | SHOULD |
| [[Userflow/Time-Attendance/overtime-management\|Overtime Management]] | Overtime requests and approval | Documented | SHOULD |
| [[Userflow/Time-Attendance/break-tracking\|Break Tracking]] | Break policy and tracking | Documented | COULD |
| [[Userflow/Time-Attendance/biometric-device-setup\|Biometric Device Setup]] | Register devices, enroll employees | Documented | COULD |

### Performance - Phase 2

Performance reviews, goal setting, succession planning, and full performance workflows are Phase 2 unless explicitly reactivated. Do not expose Performance as a Phase 1 customer navigation item.

| Flow | Description | Status | Priority |
|:-----|:------------|:-------|:---------|
| [[Userflow/Performance/review-cycle-setup|Review Cycle Setup]] | Phase 2 review-cycle reference | Documented | COULD |
| [[Userflow/Performance/goal-setting|Goal Setting]] | Phase 2 goal/OKR reference | Documented | COULD |

### Payroll - `payroll:read/write/run/approve`

| Flow | Description | Status | Priority |
|:-----|:------------|:-------|:---------|
| [[Userflow/Payroll/payroll-provider-setup\|Payroll Provider Setup]] | Configure external payroll provider | Documented | MUST |
| [[Userflow/Payroll/tax-configuration\|Tax Configuration]] | Country-specific tax rules | Documented | MUST |
| [[Userflow/Payroll/allowance-setup\|Allowance Setup]] | Define allowance types, assign | Documented | SHOULD |
| [[Userflow/Payroll/pension-configuration\|Pension Configuration]] | Pension scheme setup | Documented | SHOULD |
| [[Userflow/Payroll/payroll-run-execution\|Payroll Run Execution]] | Execute payroll run, review, approve | Documented | MUST |
| [[Userflow/Payroll/payroll-adjustment\|Payroll Adjustment]] | Post-run corrections | Documented | SHOULD |
| [[Userflow/Payroll/payslip-view\|Payslip View]] | Employee views own payslip | Documented | MUST |

### Skills & Learning - `skills:read/write/validate/manage` *(Mixed phase)*

Phase 1 does not include a customer-facing Skills sidebar. Phase 1 includes embedded position required skills plus employee skill requests and eligible-validator validation for existing tenant skills.

Full taxonomy management, courses, certifications, and development plans are Phase 2.

| Flow | Description | Status | Priority |
|:-----|:------------|:-------|:---------|
| [[Userflow/Skills-Learning/skill-taxonomy-setup\|Skill Taxonomy Setup]] | Full taxonomy setup for Phase 2 | Documented | SHOULD |
| [[Userflow/Skills-Learning/employee-skill-declaration\|Employee Skill Declaration]] | Employee requests existing skills for own profile | Documented | MUST |
| [[Userflow/Skills-Learning/skill-assessment\|Skill Assessment]] | Manager validates employee skill requests | Documented | MUST |
| [[Userflow/Skills-Learning/course-enrollment\|Course Enrollment]] | Browse and enroll in courses (Phase 2) | Documented | SHOULD |
| [[Userflow/Skills-Learning/certification-tracking\|Certification Tracking]] | Upload/verify certifications (Phase 2) | Documented | COULD |
| [[Userflow/Skills-Learning/development-plan\|Development Plan]] | Create learning path (Phase 2) | Documented | SHOULD |

### Documents - `documents:read/write/manage`

| Flow | Description | Status | Priority |
|:-----|:------------|:-------|:---------|
| [[Userflow/Documents/document-upload\|Document Upload]] | Upload company/employee documents | Documented | MUST |
| [[Userflow/Documents/document-access\|Document Access]] | View documents (own or by permission) | Documented | MUST |
| [[Userflow/Documents/document-acknowledgement\|Document Acknowledgement]] | Employee acknowledges policy docs | Documented | SHOULD |
| [[Userflow/Documents/template-management\|Template Management]] | Create/manage document templates | Documented | SHOULD |
| [[Userflow/Documents/document-versioning\|Document Versioning]] | Version history, rollback | Documented | COULD |

### Monitoring - `monitoring:view/manage`, `monitoring:configure`

| Flow | Description | Status | Priority |
|:-----|:------------|:-------|:---------|
| [[Userflow/Monitoring/monitoring-configuration\|Monitoring Configuration]] | Enable/disable monitoring per tenant/employee | Documented | MUST |
| [[Userflow/Monitoring/live-dashboard\|Live Dashboard]] | Real-time monitoring presence view | Documented | MUST |
| [[Userflow/Monitoring/activity-snapshot-view\|Activity Snapshot View]] | View app usage, screenshots, meetings | Documented | SHOULD |
| [[Userflow/Monitoring/identity-verification-setup\|Identity Verification Setup]] | Configure photo capture intervals | Documented | SHOULD |
| [[Userflow/Monitoring/identity-verification-review\|Identity Verification Review]] | Review flagged verification failures | Documented | SHOULD |
| [[Userflow/Monitoring/agent-deployment\|Agent Deployment]] | Install, register, monitor desktop agent | Documented | MUST |

### Discrepancy Engine - `exceptions:manage`

| Flow | Description | Status | Priority |
|:-----|:------------|:-------|:---------|
| [[Userflow/Discrepancy-Engine/discrepancy-review\|Discrepancy Review]] | Review mismatches between active time, WorkSync logs, and calendar context | Documented | MUST |

### Exception Engine - `monitoring:alerts:read/resolve`, `exceptions:manage`

| Flow | Description | Status | Priority |
|:-----|:------------|:-------|:---------|
| [[Userflow/Exception-Engine/exception-rule-setup\|Exception Rule Setup]] | Define anomaly detection rules | Documented | MUST |
| [[Userflow/Exception-Engine/alert-review\|Alert Review]] | View and acknowledge alerts | Documented | MUST |
| [[Userflow/Exception-Engine/escalation-chain-setup\|Escalation Chain Setup]] | Configure escalation paths | Documented | SHOULD |
| [[Userflow/Exception-Engine/exception-dashboard\|Alerts Overview]] | Overview of all active alerts | Documented | MUST |

### Analytics & Reporting - `analytics:view/export`, `reports:read/create`

| Flow | Description | Status | Priority |
|:-----|:------------|:-------|:---------|
| [[Userflow/Analytics-Reporting/productivity-dashboard\|Productivity Dashboard]] | Daily/weekly/monthly analytics view | Documented | MUST |
| [[Userflow/Analytics-Reporting/monitoring-snapshot\|Monitoring Snapshot]] | Point-in-time org snapshots | Documented | SHOULD |
| [[Userflow/Analytics-Reporting/report-creation\|Report Creation]] | Build custom reports | Documented | SHOULD |
| [[Userflow/Analytics-Reporting/scheduled-report-setup\|Scheduled Report Setup]] | Automate report delivery | Documented | COULD |
| [[Userflow/Analytics-Reporting/data-export\|Data Export]] | CSV/Excel export flow | Documented | SHOULD |

### Grievance - `grievance:read/write/manage`

| Flow | Description | Status | Priority |
|:-----|:------------|:-------|:---------|
| [[Userflow/Grievance/grievance-filing\|Grievance Filing]] | Employee files grievance | Documented | MUST |
| [[Userflow/Grievance/grievance-investigation\|Grievance Investigation]] | Admin reviews, assigns investigator | Documented | MUST |
| [[Userflow/Grievance/disciplinary-action\|Disciplinary Action]] | Issue disciplinary action | Documented | SHOULD |

### Expense - `expense:read/create/approve/manage`

| Flow | Description | Status | Priority |
|:-----|:------------|:-------|:---------|
| [[Userflow/Expense/expense-claim-submission\|Expense Claim Submission]] | Employee submits expense with receipts | Documented | MUST |
| [[Userflow/Expense/expense-approval\|Expense Approval]] | Approver reviews expense claims | Documented | MUST |
| [[Userflow/Expense/expense-category-setup\|Expense Category Setup]] | Admin defines expense categories | Documented | SHOULD |

### Calendar - `calendar:read/write`

| Flow | Description | Status | Priority |
|:-----|:------------|:-------|:---------|
| [[Userflow/Calendar/calendar-event-creation\|Calendar Event Creation]] | Create events (meetings, holidays) | Documented | SHOULD |
| [[Userflow/Calendar/calendar-integrations\|Calendar Integrations]] | Country holiday sync plus Google/Outlook calendar pull/push sync | Documented | MUST |
| [[Userflow/Calendar/conflict-detection\|Conflict Detection]] | View scheduling conflicts | Documented | COULD |

### Notifications - `notifications:read/manage`

| Flow | Description | Status | Priority |
|:-----|:------------|:-------|:---------|
| [[Userflow/Notifications/notification-preference-setup\|Notification Preference Setup]] | User configures notification channels | Documented | SHOULD |
| [[Userflow/Notifications/inbox\|Inbox]] | Unified approval, alert, and notification queue | Documented | MUST |
| [[Userflow/Notifications/notification-view\|Notification View]] | View/dismiss notifications | Documented | MUST |

### Automation Center - Phase 2 only

Automation Center, workflow builder, automation templates, and custom workflow routing are not active Phase 1 customer flows. Phase 1 approvals use Org Structure management coverage, owner order, granted permissions, lightweight request records, Notifications, and Inbox.

| Flow | Description | Status | Priority |
|:-----|:------------|:-------|:---------|
| [[Userflow/Automation/automation-center|Automation Center]] | Phase 2 deferred workflow/automation reference | Documented | COULD |

### Cross-Module Scenarios

These flows track chain reactions across multiple modules - when one action triggers downstream effects in 3+ modules.

| Flow | Description | Status | Priority |
|:-----|:------------|:-------|:---------|
| [[Userflow/Cross-Module/employee-full-onboarding\|Employee Full Onboarding]] | Hire -> auth + time_off + attendance + payroll + docs setup | Documented | MUST |
| [[Userflow/Cross-Module/employee-full-offboarding\|Employee Full Offboarding]] | Exit -> access revoke + final pay + data retention | Documented | MUST |
| [[Userflow/Cross-Module/time-off-request-and-approval-chain\|Time Off Request & Approval Chain]] | Request -> calendar + attendance override + payroll deduction | Documented | MUST |
| [[Userflow/Cross-Module/monthly-payroll-run-chain\|Monthly Payroll Run Chain]] | Attendance + time_off + expense data -> calculation -> payslips | Documented | MUST |
| [[Userflow/Cross-Module/attendance-dispute-chain\|Attendance Dispute & Correction Chain]] | Employee/system-detected -> correction -> payroll adjustment | Documented | SHOULD |
| [[Userflow/Cross-Module/performance-review-cycle-chain\|Performance Review Cycle Chain]] | Cycle -> assessments -> compensation + learning + succession | Documented | SHOULD |
| [[Userflow/Cross-Module/employee-transfer-chain\|Employee Transfer Chain]] | Transfer -> reporting line + shift + Time Off policy + payroll + access | Documented | SHOULD |

### Configuration - `settings:read/admin`

| Flow | Description | Status | Priority |
|:-----|:------------|:-------|:---------|
| [[Userflow/Configuration/tenant-settings\|Tenant Settings]] | Global tenant configuration | Documented | MUST |
| [[Userflow/Configuration/monitoring-toggles\|Monitoring Toggles]] | Per-feature monitoring on/off | Documented | SHOULD |
| [[Userflow/Configuration/employee-override\|Employee Override]] | Override settings for specific employee | Documented | SHOULD |
| [[Userflow/Configuration/retention-policy-setup\|Retention Policy Setup]] | Data retention configuration | Documented | SHOULD |
| [[Userflow/Configuration/app-allowlist-setup\|App Allowlist Setup]] | Configure productive/allowed applications for monitoring | Documented | SHOULD |
| [[Userflow/Configuration/integration-connection\|Integration Connection]] | Connect and test external providers and module integrations | Documented | SHOULD |

### Work Management - `projects:*`, `tasks:*`, `worklogs:*`

Phase 1 Work is intentionally simple. Active Phase 1 Work covers projects, work items, basic project membership, simple project settings, simple documents/pages where retained, and worklogs. Planner, Goals/OKR, broad resource planning, Chat AI, workspace-heavy planning, advanced roadmap, and automation rules are Phase 2.

| Flow | Description | Status | Priority |
|:-----|:------------|:-------|:---------|
| [[Userflow/Work-Management/wm-overview|Work Overview]] | Phase 1 Work scope and boundaries | Documented | MUST |
| [[Userflow/Work-Management/project-flow|Project Management]] | Projects, basic membership, simple settings | Documented | MUST |
| [[Userflow/Work-Management/task-flow|Work Item Management]] | Work items, assignments, status, comments/checklists where retained | Documented | MUST |
| [[Userflow/Work-Management/time-tracking-flow|Worklogs]] | Time logs/worklogs connected to Time & Attendance where applicable | Documented | SHOULD |
| [[Userflow/Work-Management/collaboration-flow|Simple Docs/Pages]] | Simple project documents/pages if retained in Phase 1 | Documented | SHOULD |
| [[Userflow/Work-Management/planning-flow|Planning / Planner]] | Phase 2 only | Documented | COULD |
| [[Userflow/Work-Management/goals-okr-flow|Goals and OKRs]] | Phase 2 only | Documented | COULD |
| [[Userflow/Work-Management/integration-automation-flow|Integration Automation]] | Phase 2 only | Documented | COULD |

### Chat - `chat:read`

| Flow | Description | Status | Priority |
|:-----|:------------|:-------|:---------|
| [[Userflow/Chat/chat-overview\|Chat Overview]] | Channels, DMs, messages, reactions, file attachments | Documented | MUST |

### Developer Platform - platform-admin only

| Flow | Description | Status | Priority |
|:-----|:------------|:-------|:---------|
| [[developer-platform/userflow/overview\|Developer Platform Overview]] | Internal operator console navigation and access levels | Documented | MUST |
| [[developer-platform/userflow/dashboard\|Dashboard]] | Cross-tenant platform summary and click-through | Documented | SHOULD |
| [[developer-platform/userflow/platform-access\|Platform Users and Platform Roles]] | Invite platform managers, assign roles, restrict module access, revoke sessions | Documented | MUST |
| [[developer-platform/userflow/provisioning-flow\|Operator Customer Provisioning]] | Internal 7-step tenant provisioning wizard | Documented | SHOULD |
| [[developer-platform/userflow/tenant-management\|Tenant Management]] | Manage tenant status, details, and operational actions | Documented | SHOULD |
| [[developer-platform/userflow/subscription-management\|Subscription Management]] | Reusable plans, payment gateways, invoices, and tenant commercial terms | Documented | SHOULD |
| [[developer-platform/userflow/module-catalog\|Module Catalog]] | Manage ONEVO product modules, pricing, permission ownership, and tenant impact | Documented | MUST |
| [[developer-platform/userflow/role-template-management\|Role Template Management]] | Manage reusable tenant role templates and materialize tenant roles | Documented | SHOULD |
| [[developer-platform/userflow/global-policies\|Global Policies]] | Manage platform policy defaults and explicit tenant propagation | Documented | SHOULD |
| [[developer-platform/userflow/feature-flags\|Feature Flags]] | Manage global and tenant-level feature flags | Documented | SHOULD |
| [[developer-platform/userflow/agent-versions\|Agent Versions]] | Manage desktop agent rollout rings and versions | Documented | SHOULD |
| [[developer-platform/userflow/platform-health\|Platform Health]] | View health and dependency status | Documented | SHOULD |
| [[developer-platform/userflow/device-management\|Device Management]] | Inspect devices and queue approved agent commands | Documented | SHOULD |
| [[developer-platform/userflow/infrastructure-operations\|Infrastructure Operations]] | Infrastructure capacity and dependency summary | Documented | SHOULD |
| [[developer-platform/userflow/background-jobs\|Background Jobs]] | Job observability, retry, and schedule controls | Documented | SHOULD |
| [[developer-platform/userflow/security-center\|Security Center]] | Security overview and session review | Documented | SHOULD |
| [[developer-platform/userflow/audit-console\|Audit Console]] | Cross-tenant audit query and export | Documented | SHOULD |
| [[developer-platform/userflow/compliance-center\|Compliance Center]] | Compliance exports and legal holds | Documented | SHOULD |
| [[developer-platform/userflow/data-retention\|Data Retention]] | Retention policy management and sweep behavior | Documented | SHOULD |
| [[developer-platform/userflow/platform-analytics\|Platform Analytics]] | Cross-tenant analytics | Documented | SHOULD |
| [[developer-platform/userflow/reports\|Reports]] | Platform report exports | Documented | SHOULD |
| [[developer-platform/userflow/system-config\|System Config]] | Global defaults and tenant setting overrides | Documented | SHOULD |
| [[developer-platform/userflow/app-catalog\|App Catalog]] | Global app catalog and uncatalogued app approval | Documented | SHOULD |
| [[developer-platform/userflow/api-keys\|API Keys]] | Phase 2 platform API key management | Documented | COULD |

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
