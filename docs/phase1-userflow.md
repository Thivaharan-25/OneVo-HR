# ONEVO Phase 1 — Complete User Flow

**Date:** 2026-04-24  
**Branch:** Thivah  
**Scope:** All Phase 1 modules, start-to-end, across all actors  
**Plans incorporated:**
- `docs/superpowers/plans/2026-04-24-hr-import-onboarding.md` — 7-step import wizard (DataImport module)
- `docs/superpowers/plans/2026-04-24-intelligence-layer-statistical-baselines.md` — Statistical baselines + AI enrichment on Discrepancy/Exception engines

---

## Actors

| Actor | Role in Phase 1 |
|:------|:----------------|
| **Super Admin** | Tenant owner. Manages billing, user invitations, feature grants, top-level org setup. Has unrestricted access across all modules and all employees. |
| **HR Admin** | Day-to-day HR operations. Manages employees, org structure, leave policies, monitoring config, and import wizard. Operates within org hierarchy scope. |
| **Manager** | Approves leave, promotions, transfers. Reviews team monitoring dashboards and receives exception/discrepancy alerts. Sees only employees below them. |
| **Employee** | Self-service. Submits leave requests, views own activity data (per transparency mode), installs and runs the desktop agent. |
| **System** | Hangfire background jobs, event handlers, domain event pipeline. No human interaction — runs on schedule or on domain event. |

---

## Cross-Cutting Rules (Apply to Every Flow)

> These rules govern every interaction in the platform. They are not repeated in each flow.

1. **Every request resolves permissions** — Effective permissions = role template + per-employee overrides, filtered by feature grants, scoped by org hierarchy. Hierarchy scope: Super Admin sees all; Manager sees subordinates only; Employee sees own data only.
2. **Every write creates an audit log entry** — `audit_logs` table. Append-only. Partitioned by month. Never deleted.
3. **JWT RS256 auth on every endpoint** — Access tokens expire in 15 min; refresh tokens rotate on use (7-day lifetime). Device JWT (agent) is a separate token type and is never accepted on user endpoints.
4. **Multi-tenant isolation** — Every query is scoped to `tenant_id`. Row-level security in PostgreSQL.
5. **GDPR consent gates monitoring** — `consent_type: "monitoring"` record must exist for an employee before monitoring features activate for that employee.
6. **SignalR delivers real-time updates** — Live dashboards, alert panels, and the import wizard progress bar all receive push notifications via SignalR.

---

## Flow Index

| # | Flow | Primary Actor |
|:--|:-----|:--------------|
| A | Platform Onboarding (new tenant) | Super Admin |
| B | HR Import Wizard (7 steps) | HR Admin |
| C | Post-Import Admin Setup | HR Admin |
| D | Authentication & Access Control | All |
| E | Manual Employee Creation | HR Admin |
| F | Employee Onboarding Workflow | HR Admin + Employee |
| G | Employee Offboarding | HR Admin + Manager |
| H | Promotion & Transfer | Manager + HR Admin |
| I | Compensation Management | HR Admin |
| J | Organisation Structure Management | HR Admin |
| K | Leave Policy Setup | HR Admin |
| L | Leave Request & Approval | Employee + Manager |
| M | Leave Cancellation | Employee + Manager |
| N | Desktop Agent Install & Registration | Employee + System |
| O | Daily Monitoring Data Collection | System + Agent |
| P | Identity Verification | System + Manager |
| Q | Exception Engine + Statistical Baselines | System + Manager |
| R | Discrepancy Engine + AI Enrichment | System + Manager |
| S | Manager Response to Alerts | Manager |
| T | Productivity Analytics | Manager + HR Admin |
| U | Tenant Configuration & Monitoring Toggles | HR Admin |
| V | GDPR Consent Management | Employee + HR Admin |
| W | Calendar | HR Admin + All |
| X | Notification Delivery | System + All |
| Y | User Invitations & Permission Management | Super Admin + HR Admin |
| Z | System Background Job Schedule | System |

---

## A. Platform Onboarding (New Tenant)

**Actor:** Super Admin  
**Entry:** Public marketing site → "Start Free Trial" / "Get Started"

```
[Public Site]
  → Registration form: company name, admin email, password
  → Email sent → admin clicks verification link
  → Account verified

[Plan Selection]
  → Choose configuration:
    ┌─────────────────────────────────────────────────────────────────┐
    │ HR Management         │ HR + Workforce Intelligence              │
    │ HR + Work Management  │ Full Suite (all modules)                 │
    └─────────────────────────────────────────────────────────────────┘
  → Billing setup (Stripe): credit card → subscription activated
  → Tenant provisioned: tenant_id assigned, feature grants written per plan

[Initial Setup Wizard]
  Step 1: Company basics
    → Name, industry, timezone, locale, default currency
    → Upload company logo (optional)

  Step 2: Legal entities
    → Add registered business entity (name, registration number, country)
    → Multiple entities allowed from the start

  Step 3: Employee data decision point
    ┌────────────────────────────────────────────────────────────────┐
    │ DECISION: How will you add your employees?                     │
    │                                                                │
    │  A) Import from CSV, Excel, or PeopleHR → [Flow B]            │
    │  B) Set up manually → skip to dashboard, use Flow E per user   │
    └────────────────────────────────────────────────────────────────┘
```

**System writes:** `tenants`, `feature_access_grants`, `legal_entities`  
**Outcome:** Tenant active, admin logged in, directed to HR Import Wizard or empty dashboard.

---

## B. HR Import Wizard (7 Steps)

> **Plan:** `docs/superpowers/plans/2026-04-24-hr-import-onboarding.md`  
> **Actor:** HR Admin (requires `employees:write` + `settings:admin`)  
> **Entry:** Employee list → "Import Employees" button OR Settings → Integrations → "New Import"  
> **UI:** Full-screen overlay wizard. Back/Next throughout. Zustand state machine drives all 7 steps.  
> **Backend:** `DataImport` module. ETL runs as Hangfire background jobs. Endpoint: `POST /api/migration/bulk-import`.

---

### Step 1 — Choose Import Method

```
[Wizard opens full-screen]
  Two cards presented side-by-side:

  ┌──────────────────────────┐   ┌──────────────────────────┐
  │  Upload CSV or Excel     │   │  Connect PeopleHR         │
  │  .csv · .xlsx · .xls     │   │  via API key              │
  └──────────────────────────┘   └──────────────────────────┘
           │                                │
           ▼                                ▼
       [Step 2a]                        [Step 2b]
```

---

### Step 2a — Upload File (CSV/Excel Path)

```
[File Upload UI]
  → Drag & drop area or browse button
  → Accepts: .csv, .xlsx, .xls ONLY
  → File validates client-side: type check, size limit
  → System issues pre-signed Railway S3-compatible blob storage URL (expires 1 hour)
  → Browser uploads file DIRECTLY to storage (never through ONEVO API server)
  → System reads file from storage:
      - Parses column headers
      - Loads Row 1 as the sample employee record
      - Counts total rows
  → "File uploaded — 247 employees found" confirmation
  → Proceed to Step 3

  ERROR STATES:
    - Unsupported format → "Please upload a .csv, .xlsx or .xls file"
    - Empty file         → "File contains no employee rows"
    - Parse failure      → "Could not read file. Try re-saving as .csv"
```

---

### Step 2b — Connect PeopleHR (API Path)

```
[API Connection UI]
  → If saved PeopleHR connection exists in Integrations:
      "Use saved connection" option offered → skip key entry
  → Otherwise: API key input field
  → Submit → system calls PeopleHR API:
      - Validates key → success: fetch employee list
      - Invalid key  → inline error: "API key not recognised. Check your PeopleHR account."
      - Rate limit   → "PeopleHR is rate-limiting requests. Retrying... (auto-backoff)"
  → Employee list fetched → fields auto-mapped to ONEVO fields
  → Toggle: "Save this connection to Integrations" (default: ON)
  → Proceed to Step 3

  Note: PeopleHR path auto-maps fields — Step 3 shows confirmation table
        rather than a blank mapping UI.
```

---

### Step 3 — Review Column Mapping

```
[Mapping Table]
  Columns: Your Column | Mapped To | Sample Value (Row 1) | Status

  Auto-matching logic (system runs before step is shown):
    - Name similarity match: "first_name" → First Name, "email" → Email, etc.
    - Type detection on sample value:
        date format         → Start Date or Date of Birth only
        email format        → Email only
        "Full Time/Part..." → Employment Type only
        short name text     → name fields, Job Title, Manager
        comma-separated     → Skills
    - All auto-matched rows are pre-filled but fully editable

  Dropdown filtering rules (applied live per row):
    1. EXCLUSIVITY  — fields claimed by another row removed from this dropdown
    2. TYPE COMPAT  — incompatible fields hidden based on sample value type
    3. GROUPING     — remaining options grouped: Personal / Employment / Compensation / Skip

  Required fields (blocking — must be mapped):
    First Name, Last Name, Email, Department, Job Title,
    Employment Type, Start Date, Reporting Manager

  Optional fields:
    Phone, Date of Birth, Gender, Nationality, Address,
    Team, Salary, Skills

  Status column indicators:
    ✓ Green  — field mapped, sample value valid
    ⚠ Amber  — unrecognised column (dropdown to assign or skip)
    ✗ Red    — required field missing ("Employees will be flagged Needs Completion")

  Job Title special case:
    If NO Job Family or Job Level column detected →
      Notice: "No Job Family/Level column found — you'll group these in the next step."
      → Step 4 (Organise Job Titles) will be inserted

  Preview bar (below table):
    Shows Row 1 parsed with current mapping → admin confirms:
    "Looks right → Apply to all 247 employees"

  PeopleHR path:
    Fields auto-mapped. Same table shown for confirmation.
    Admin may edit any row. Proceed same as CSV path.
```

---

### Step 4 — Organise Job Titles

```
ONLY shown when no Job Family / Job Level column was detected in Step 3.

[Job Grouping UI]
  System scans all rows, extracts unique job titles.
  Groups them by department name as a suggested job family.

  Layout: one card per detected job family.
  Each card shows:
    - Editable job family name (text input)
    - List of job titles within that family
    - Level dropdown per job title
    - Employee count per title

  Level dropdown source:
    → If tenant has existing job levels: show those
    → If no levels exist (typical new tenant):
        Wizard offers 4 defaults: Junior (rank 100), Senior (200), Lead (300), Director (400)
        These are auto-created in job_levels on import. Admin can rename in
        Organisation → Job Families post-import.

  Admin actions:
    - Rename job family
    - Move title between families
    - Create new family
    - Assign level to title

  Ungrouped titles (amber, at bottom):
    Auto-grouping couldn't determine family → admin assigns family + level manually.

  Auto-create inventory (confirmed at end of this step):
    job_families → created as stubs
    job_levels   → created with numeric rank
    job_titles   → created linking family + level
```

---

### Step 5 — Validation

```
[Two-panel validation layout]
  ETL pipeline runs BEFORE this step as a Hangfire background job.
  Admin sees "Processing your file..." spinner while it runs.

  ETL transformations applied to all rows:
    Date fields      → normalised to ISO 8601 (accepts DD/MM, MM/DD, YYYY-MM-DD)
    Phone numbers    → normalised to E.164 (+44XXXXXXXXXX) — invalid: flagged, not blocked
    Salary fields    → validated numeric — non-numeric: flagged
    Duplicate emp ID → detected within file — duplicate rows flagged
    Duplicate email  → checked against existing ONEVO records — blocked if exists
    Null required    → flagged → employees imported with "Needs Completion" status

LEFT PANEL — Employee Counts:
  ✓ 231 employees ready
  ⚠ 14 employees have issues (missing required fields)
    → Options per flagged row: [Skip] [Fix inline]

RIGHT PANEL — Auto-created Dependencies:
  System will automatically create:
    Departments (8)       — created without department heads
    Teams (5)             — with detected leads if column found
    Job Families (4)      — stubs
    Job Levels (4)        — stubs with rank
    Job Titles (22)       — linking family + level
    Draft Skills (18)     — "Imported" category, no proficiency levels yet

HIERARCHY VALIDATION:
  Reporting lines mapped and validated across all rows.
  Circular references detected (employee reports to themselves) → flagged for admin.
  "Preview org chart →" button opens org chart overlay.

  Note at bottom: "Departments will be created without heads.
  Assign in Organisation → Departments after import."
```

---

### Step 6 — Confirm & Import

```
[Summary Screen]
  Totals shown:
    231 employees to import
    14 rows to skip
    8 departments, 5 teams, 4 job families, 22 job titles, 18 draft skills to create

  "Start Import" button
  → Hangfire job enqueued (Hangfire Batch queue, NOT BullMQ)
  → migration_runs record created: status = Processing

  Live progress bar (SignalR push):
    "Importing... 142 / 231 employees"

  Admin can navigate away → import continues in background.
  Notification sent on completion (in-app + email).

  IMPORT TRANSACTION ORDER (backend, single transaction):
    1. Departments (headless — head_employee_id = null)
    2. Teams (without leads)
    3. Job Families
    4. Job Levels
    5. Job Titles (links family + level)
    6. Skill taxonomy drafts ("Imported" category)
    7. Employees (linked to department, job title)
    8. Employee skill declarations (links employees → draft skills)
    9. Reporting lines (employees.manager_id populated — all exist now)
    10. Team leads assigned (all employees exist now)

  If any step fails → full rollback. No partial state. Admin sees clear error report.

  IDEMPOTENCY: POST /api/migration/bulk-import uses INSERT … ON CONFLICT DO UPDATE
  keyed on employee ID and email. Safe to re-run on partial failure.

  BATCHING: Written in batches of 500–1,000 records per API call.
```

---

### Step 7 — Done

```
[Completion Screen]
  "231 employees imported successfully. 14 skipped. (View skip report)"

  POST-IMPORT RECONCILIATION (runs automatically after job completes):
    1. Record count check — source rows must match destination employee count
    2. Checksum validation — total salary sum + department counts compared
    3. Reconciliation report generated (downloadable PDF):
         Total migrated records, errors, warnings, skipped entries
    4. Spot-check checklist — 10–15 randomly sampled employees for manual verify

  [Return to Employee List] — now populated

  POST-IMPORT ADMIN CHECKLIST (shown on screen):
    □ Assign department heads in Organisation → Departments
    □ Configure roles per job level in Organisation → Job Families
    □ Set required skills on job families (feeds Phase 2 gap analysis)
    □ Enrich skill taxonomy (add categories, proficiency labels) in Skills & Talent
    □ Review "Needs Completion" employees and fill missing fields

  AUDIT & SECURITY:
    - migration_runs row updated: status = Completed, completed_at, row counts
    - All migration activity included in platform-wide audit_logs
    - Uploaded files auto-deleted within 48 hours of successful import (scheduled cleanup job)
    - Failed import files retained 7 days for retry, then deleted

  SETTINGS → INTEGRATIONS (accessible after):
    PeopleHR card shows:
      Status: Connected / Not connected
      API key: masked (last 4 chars)
      Last import: date + employee count
      Import history: log of all past imports with status
```

---

## C. Post-Import Admin Setup

**Actor:** HR Admin  
**Entry:** Done screen checklist items OR direct navigation after import

```
[Assign Department Heads]
  Organisation → Departments → select department → "Assign Head" → pick employee

[Configure Roles per Job Level]
  Organisation → Job Families → select family → per level: set default role template
  → Employees at that level inherit permissions from assigned role template

[Set Required Skills on Job Families]
  Organisation → Job Families → select family → "Required Skills" tab
  → Pick from draft skills taxonomy (created by import) or search existing
  → Set minimum proficiency level per skill
  → These requirements feed Phase 2 gap analysis

[Enrich Skill Taxonomy]
  Skills & Talent → Taxonomy → "Imported" category
  → Rename skills, move to proper categories, set proficiency level labels
  → Draft skills become validated taxonomy entries

[Review Needs Completion Employees]
  Employees → filter: Status = "Needs Completion"
  → Per employee: fill missing required fields (phone, DOB, etc.)
  → Mark as complete → status updated to Active
```

---

## D. Authentication & Access Control

**Actor:** All users  
**Entry:** Any protected URL → redirect to login

```
[Login]
  POST /api/v1/auth/login
  → Email + password validated
  → MFA check:
      If MFA enabled: → prompt for TOTP code
                        POST /api/v1/auth/mfa/verify
                        → code valid: continue
                        → code invalid: "Incorrect code. Try again." (max 5 attempts)
      If MFA disabled: → continue directly
  → JWT RS256 issued: access token (15 min) + refresh token (7 days)
  → Session record written to sessions table
  → Permission resolver runs: resolves effective permissions for this user
  → Hierarchy filter computed: SubordinatesOf(managerId) or OwnOnly or All
  → Redirect to dashboard

[Token Refresh]
  POST /api/v1/auth/refresh
  → Refresh token validated (not revoked, not expired)
  → New access token + new refresh token issued (rotation)
  → Old refresh token marked replaced_by_id → chain maintained for theft detection
  → If revoked token reused: entire chain revoked (token theft response)

[SSO Path]
  External IdP → SAML assertion received
  → Mapped to ONEVO user → session established → same permission resolution

[Logout]
  POST /api/v1/auth/logout
  → Session marked revoked
  → Refresh token revoked
  → Redirect to login

[Permission Model]
  Every API call: RequirePermissionAttribute resolves:
    effective = role_permissions + individual_overrides (overrides always win)
    filtered by feature_access_grants (module-level on/off)
    scoped by IHierarchyScopeService (org hierarchy — never materialized as ID list)

[Bridge Token (service-to-service)]
  POST /api/v1/auth/bridge/token
  client_id + client_secret → BridgeJWT issued (aud: "onevo-bridge", 1 hour)
  → Accepted ONLY on /api/v1/bridges/* endpoints
  → User JWTs rejected on bridge endpoints; bridge JWTs rejected on user endpoints
```

---

## E. Manual Employee Creation

**Actor:** HR Admin (`employees:write`)  
**Entry:** Employees → "Add Employee"

```
[Multi-step form]
  Step 1 — Personal Details
    First name, last name, email, phone, date of birth, gender, nationality, address

  Step 2 — Employment Details
    Employment type (Full Time / Part Time / Contract)
    Start date, job title (from taxonomy), department, reporting manager

  Step 3 — Compensation
    Base salary, currency, effective date (requires payroll:write if salary included)

  Step 4 — Org Assignment
    Team, cost centre, legal entity

  Step 5 — Review & Submit
    → employee record created in DB
    → employee_lifecycle_events entry: event_type = "hired"
    → employee_salary_history entry created
    → Onboarding workflow triggered [see Flow F]
    → Welcome email dispatched via Resend
    → Audit log entry written
```

---

## F. Employee Onboarding Workflow

**Actor:** HR Admin + Employee  
**Entry:** Auto-triggered on employee creation

```
[System]
  Onboarding task checklist generated per company template:
    - Document collection (ID, bank details, etc.)
    - IT setup tasks (assigned to IT team)
    - Manager welcome tasks
    - GDPR consent acknowledgement

[Employee — First Login]
  Receives welcome email → "Set your password" link (time-limited token)
  → Sets password → logs in
  → GDPR consent screen shown (if monitoring enabled):
      "Your employer has enabled activity monitoring..."
      Consent types: data_processing, monitoring
      Employee: Accept / Decline
      → gdpr_consent_records entry written
      → If monitoring declined: monitoring features do NOT activate for this employee
  → Onboarding checklist visible on dashboard
  → Employee completes assigned tasks

[HR Admin]
  Tracks onboarding progress per employee
  Marks tasks complete or reassigns
  Can send reminders
```

---

## G. Employee Offboarding

**Actor:** HR Admin  
**Entry:** Employee profile → "Initiate Offboarding"

```
[Initiate]
  HR Admin sets: termination date, reason, notice type

[System]
  Offboarding task checklist generated:
    - Equipment return (assigned to manager)
    - Access revocation (scheduled at termination date)
    - Final leave balance calculation
    - Exit interview scheduling

[Timeline]
  Tasks assigned to relevant parties (manager, IT, HR)
  On termination date:
    → User session revoked
    → JWT refresh tokens revoked
    → Desktop agent device JWT revoked (agent receives 401 on next heartbeat)
    → Agent status set to "revoked"
    → Employee status set to "terminated"
    → Data retention policy applied (GDPR)
    → employee_lifecycle_events entry: event_type = "terminated"
  Final payslip trigger → Phase 2 Payroll module (not built in Phase 1)
  → Audit log: full offboarding trail
```

---

## H. Promotion & Transfer

**Actor:** Manager or HR Admin (`employees:write`)  
**Entry:** Employee profile → "Promote" or "Transfer"

```
[Initiate Request]
  Select new job title / department / manager
  Set effective date + reason

[Approval Chain]
  Configurable per tenant (Workflow Engine):
    default: requesting manager → HR Admin → department head
  Each approver: Approve / Reject / Request amendment
  → Notifications sent at each step via Notification Engine

[On Approval]
  employee record updated: job_title_id, department_id, manager_id
  employee_salary_history entry created (if salary changed)
  employee_lifecycle_events entry: "promoted" or "transferred"
  Notification sent to employee
  Audit log entry
  [If Workforce Intelligence enabled]
    Policy recalculated for agent → RefreshPolicy command pushed via SignalR
```

---

## I. Compensation Management

**Actor:** HR Admin (`employees:write`, `payroll:write` for salary data)  
**Entry:** Employee profile → Compensation tab

```
[Update Salary]
  Enter: new base salary, currency, effective date, change reason
  → employee_salary_history entry appended (old record kept — history preserved)
  → employee_lifecycle_events: event_type = "salary_change"
  → Audit log entry
  → Notification to employee (optional, per tenant config)

[View History]
  Full salary history displayed with effective dates and change reasons
  Accessible to: HR Admin, Super Admin (not the employee directly in Phase 1)
```

---

## J. Organisation Structure Management

**Actor:** HR Admin (`settings:admin`)  
**Entry:** Organisation menu

```
[Department Hierarchy]
  Create department → set name, parent department (unlimited nesting), legal entity
  Edit: rename, move in hierarchy
  Assign head: pick employee → department_head_id set
  View: tree visualisation

[Legal Entities]
  Create entity: name, registration number, country
  Employees assigned to legal entity via their department

[Job Families & Levels]
  Create job family → add job levels (name, rank, description)
  Add job titles within family+level
  Configure required skills per level (Phase 2 gap analysis reads these)
  Configure role template per level (employees at level inherit permissions)

[Teams]
  Create team: name, description, parent team (optional)
  Add members: pick employees
  Assign team lead
  Teams are cross-functional (span departments)

[Cost Centres]
  Create cost centre: code, name, assigned departments
  Used for budgeting and reporting (Phase 2 analytics)
```

---

## K. Leave Policy Setup

**Actor:** HR Admin (`settings:admin`)  
**Entry:** Leave → Policies

```
[Create Leave Type]
  Name (Annual Leave, Sick Leave, Maternity, Paternity, etc.)
  Paid / unpaid
  Accrual rules: per month, per year, or none
  Carry-over rules: max days, expiry date
  Country-specific rules: can vary per legal entity
  Job-level-specific rules: can vary per level

[Assign Entitlements]
  Mode A: Automatic → system computes balance on employee start date
  Mode B: Manual → HR Admin sets balance per employee
  leave_entitlements + leave_balances_audit entries written

[Approval Chain per Leave Type]
  Configure approver chain: direct manager → HR Admin (if escalated)
  Set auto-approve rules (e.g., < 1 day sick leave, no approval needed)
```

---

## L. Leave Request & Approval

**Actor:** Employee (submit) + Manager (approve)  
**Entry:** Employee dashboard → Leave → "Request Leave"

```
[Employee Submits]
  Select leave type
  Select date range (calendar picker)
  System checks: balance available? ✓ / ✗
  Add note (optional)
  Submit → leave_requests entry: status = "pending"
  → Notification sent to approver (in-app + email)
  → Calendar shows leave as "pending" (amber)

[Manager Approves]
  Notification received → opens request
  Sees: employee name, dates, type, remaining balance, note
  Actions:
    Approve  → status = "approved"
               leave_balances_audit entry: balance deducted
               calendar_events entry created for employee
               notification to employee: "Your leave was approved"
               calendar shows leave as "approved" (confirmed colour)

    Reject   → status = "rejected"
               reason field (required)
               notification to employee: "Your leave was rejected: [reason]"

    Request amendment → "Please change the dates to X" (comment)
               employee notified → can resubmit

[Conflict Detection]
  System checks for calendar conflicts before approval:
    - Other leave in same period for same employee
    - Company events on requested dates
  Manager alerted if conflicts found (not a hard block — manager decides)
```

---

## M. Leave Cancellation

**Actor:** Employee (initiate) + Manager (approve)

```
[Employee]
  Leave → view approved leave → "Cancel Request"
  Can cancel before start date or (depending on policy) during leave

[System]
  Cancellation request routed to manager

[Manager]
  Approve cancellation:
    leave_requests status → "cancelled"
    balance restored (leave_balances_audit entry)
    calendar_events entry removed
    notification to employee

  Reject cancellation:
    leave remains approved, employee notified
```

---

## N. Desktop Agent Install & Registration

**Actor:** Employee + System  
**Entry:** Employee receives agent download link (email notification or in-app)

```
[Download & Install]
  Employee downloads MSIX installer (Windows)
  Installs: Windows Service (monitoring) + System Tray App (MAUI)
  On install: unique device_id generated and stored on device

[Agent Registration]
  POST /api/v1/agent/register (Tenant API key)
  → registered_agents entry created: employee_id = null (not yet linked)
  → Device JWT issued (contains device_id + tenant_id, type: "agent")
  → AgentRegistered domain event published
  → Configuration module pushes initial policy (monitoring_feature_toggles for tenant)

[Employee Login via Tray App]
  Employee enters ONEVO credentials in tray app
  POST /api/v1/agent/login (Device JWT + employee credentials)
  → employee_id linked to device in registered_agents
  → agent_policies entry computed:
      tenant policy + role override + employee override → merged (most specific wins)
  → Policy fetched by agent via GET /api/v1/agent/policy
  → SignalR connection established: agent connects to /hubs/agent-commands

[GDPR Consent Check]
  If consent_type: "monitoring" not recorded for this employee:
    → Consent overlay shown in tray app (per transparency mode)
    → Employee accepts → gdpr_consent_records entry written
    → Monitoring begins
    If employee declines → monitoring does NOT start. HR Admin notified.

[Monitoring Starts]
  StartMonitoring SignalR command pushed to agent
  → Agent begins data collection per policy:
      keyboard/mouse events, active/idle periods, app usage
      meeting detection, device sessions
      identity verification photos (if enabled, per policy interval)
```

---

## O. Daily Monitoring Data Collection

**Actor:** System (Agent + Backend Jobs)  
**Runs:** Continuously during work hours + nightly aggregation jobs

```
[Agent-Side Collection — Every ~2–3 minutes]
  7 data collectors running per policy:
    activity_snapshot    → keyboard count, mouse count, active_seconds, idle_seconds
    app_usage            → foreground app, duration, category
    document_usage       → app + doc category + duration
    communication_usage  → messaging app + send events
    device_session       → session start, active/idle minutes
    meeting_detection    → detected meeting (Teams/Zoom/etc.) + duration
    verification_photo   → only on schedule or command (NOT continuous)

  Data buffered in SQLite (local, offline resilience)
  Sync to server: POST /api/v1/agent/ingest (Device JWT)
    → 202 Accepted immediately
    → Schema validation only (detailed processing async)
    → Batch INSERT via unnest() to activity_raw_buffer

[Heartbeat — Every 60 seconds]
  POST /api/v1/agent/heartbeat
  → last_heartbeat_at updated
  → agent_health_logs entry written (CPU, memory, errors, tamper flag)
  → Response includes: pending commands queue
  → If no heartbeat for 5 min: AgentHeartbeatLost event fired
      → Exception Engine: flag offline agent exception

[Monitoring Lifecycle — Event-Driven]
  PresenceSessionStarted  → StartMonitoring  pushed via SignalR
  BreakStarted            → PauseMonitoring  pushed via SignalR (NO data captured on break)
  BreakEnded              → ResumeMonitoring pushed via SignalR
  PresenceSessionEnded    → StopMonitoring   pushed via SignalR

[Nightly Processing Jobs]
  Raw data processing job (async from ingestion):
    → activity_raw_buffer → activity_sessions (segmented)
    → App categories applied from app_allowlist config
    → Application usage records written

  Daily aggregation job:
    → daily_employee_report computed per employee
    → weekly_employee_report updated
    → Workforce presence record created (agent data + biometric terminal data combined)
    → Break detection: idle > threshold → auto-detected break inserted
```

---

## P. Identity Verification

**Actor:** System (automated) + Manager (on-demand)  
**Entry:** Scheduled per policy interval OR manager-triggered

```
[Scheduled Verification]
  Agent policy: verification_interval_minutes (e.g., 60)
  Agent captures photo → sent via POST /api/v1/agent/ingest (type: "verification_photo")
  → Identity Verification module routes photo
  → Compares against registered employee profile photo
  → Match:    verification_logs entry: result = "match" → no alert
  → Mismatch: verification_logs entry: result = "mismatch"
              → Exception Engine alert created
              → Manager notified: "Identity verification failed for [Employee]"

[On-Demand Verification (Manager)]
  Manager → Agent detail page → "Request Photo Verification"
  POST /api/v1/agents/{agentId}/capture-photo (User JWT, agent:command permission)
  → agent_commands entry: command_type = "capture_photo"
  → Command pushed via SignalR ExecuteCommand to agent (if online)
  → Agent captures photo → CommandCompleted sent back
  → Result routed to Identity Verification module
  → Manager sees result in panel (real-time via SignalR)
  → If offline: command expires in 5 minutes → "Agent offline, try again later"
```

---

## Q. Exception Engine + Statistical Baselines

> **Plan:** `docs/superpowers/plans/2026-04-24-intelligence-layer-statistical-baselines.md` (Phase 2 of that plan)  
> **Actor:** System (automated evaluation) + Manager (receives alerts, configures rules)

### Rule Configuration (HR Admin / Manager)

```
[Configure Exception Rules]
  Settings → Workforce → Exception Rules
  Create rule: name, conditions, severity, escalation chain

  Condition types (Phase 1 — absolute thresholds):
    idle_minutes > 120    → flag as "excessive idle"
    active_minutes < 60   → flag as "low activity"
    intensity_avg < 20    → flag as "minimal activity"

  Condition types (Phase 1 — with Intelligence Layer):
    Operator: "baseline_relative"
    SigmaMultiplier: 2.0 (threshold = avg + 2σ from 30-day rolling baseline)
    FallbackAbsoluteThreshold: 180 (used when < 5 samples available)
```

### Activity Baselines Computation (System — Nightly, 9:45 PM)

```
[ComputeActivityBaselinesJob — Hangfire, 9:45 PM daily]
  For each tenant, for each metric in:
    [idle_minutes, active_minutes, intensity_avg, keyboard_total, mouse_total]

  SQL aggregate over past 30 days of activity_daily_summary per employee:
    SELECT employee_id,
           AVG(metric_value)     AS avg_value,
           STDDEV(metric_value)  AS stddev_value,
           COUNT(*)              AS sample_count
    FROM   activity_daily_summary
    WHERE  tenant_id = @tenantId AND date >= (today - 30 days)
    GROUP  BY employee_id

  Upserts to employee_activity_baselines table.
  Minimum 5 samples required before baseline is considered usable.
```

### Exception Evaluation (System — runs after nightly aggregation)

```
[RuleEvaluationService — per employee per rule]
  For each rule condition:

  IF condition.Operator == "baseline_relative":
    baseline = employee_activity_baselines (latest, for this metric)

    IF baseline available AND sample_count >= 5 AND stddev > 0:
      threshold = baseline.avg + (condition.SigmaMultiplier × baseline.stddev)
      evaluate: metric_value > threshold → TRIGGERED
      [uses baseline_relative method — personalised to employee's norm]

    ELSE (new employee or insufficient data):
      threshold = condition.FallbackAbsoluteThreshold
      evaluate: metric_value > threshold → TRIGGERED
      [uses absolute fallback — safe for day-1 employees]

  IF condition.Operator == "gt" / "lt" / etc.:
    standard absolute comparison (unchanged from pre-Intelligence Layer behaviour)

  ON TRIGGERED:
    exception_alerts entry created
    escalation chain notified (in-app + email)
    AgentHeartbeatLost flag also checked
```

---

## R. Discrepancy Engine + Statistical Baselines + AI Enrichment

> **Plan:** `docs/superpowers/plans/2026-04-24-intelligence-layer-statistical-baselines.md` (Phase 1 + Phase 3)  
> **Actor:** System (nightly Hangfire jobs + MediatR event handlers) + Manager (receives enriched alerts)

### Discrepancy Baselines Computation (System — 10:00 PM nightly)

```
[ComputeDiscrepancyBaselinesJob — Hangfire, 10:00 PM daily]
  Runs BEFORE DiscrepancyEngineJob (which runs at 10:30 PM).

  For each tenant, for each employee:

  SQL aggregate over past 30 days of discrepancy_events:
    SELECT employee_id,
           AVG(unaccounted_minutes)    AS avg_unaccounted,
           STDDEV(unaccounted_minutes) AS stddev_unaccounted,
           COUNT(*)                    AS sample_count
    FROM   discrepancy_events
    WHERE  tenant_id = @tenantId AND date >= (today - 30 days)
    GROUP  BY employee_id

  Upserts to employee_discrepancy_baselines:
    avg_unaccounted_minutes, stddev_unaccounted_minutes, sample_count, computed_at

  Baseline is marked usable only when: sample_count >= 5 AND stddev > 0
  New employees → baseline not usable → absolute fallback used automatically
  Baselines retained 90 days, pruned by CleanupOldBaselinesJob
```

### Discrepancy Engine Evaluation (System — 10:30 PM nightly)

```
[DiscrepancyEngineJob — Hangfire, 10:30 PM daily]
  For each employee, per tenant:

  Inputs:
    HR active minutes    (from hr_daily_time_logs)
    WMS logged minutes   (from wms_daily_time_logs — 0 if no WMS integration)
    Calendar minutes     (from calendar_events for that day)

  Compute: unaccounted_minutes = HR active - max(WMS, Calendar)

  Severity Classification (DiscrepancySeverityCalculator):

    Step 1: Fetch employee_discrepancy_baselines (latest for this employee)

    IF baseline.IsUsable() (sample_count >= 5 AND stddev > 0):
      z_score = (unaccounted_minutes - baseline.avg) / baseline.stddev
      severity = z_score < 1.0  → none
                 z_score 1.0–1.5 → low
                 z_score 1.5–2.5 → high
                 z_score >= 2.5  → critical
      severity_method = "baseline_relative"

    ELSE (new employee, < 5 samples, or stddev = 0):
      severity = unaccounted < 30  → none
                 30–60 min          → low
                 60–180 min         → high
                 > 180 min          → critical
      severity_method = "absolute"

  Upsert discrepancy_events:
    unaccounted_minutes, severity, severity_method
    z_score (nullable), baseline_avg_minutes (nullable), baseline_stddev_minutes (nullable)

  IF severity == "critical":
    → Publish DiscrepancyCriticalDetected domain event (MediatR)
    → DiscrepancyEnrichmentHandler handles it [see AI Enrichment below]
```

### AI Notification Enrichment (System — on DiscrepancyCriticalDetected)

```
[DiscrepancyEnrichmentHandler — MediatR INotificationHandler]
  Triggered ONLY on DiscrepancyCriticalDetected. Never in detection loop.

  Step 1: Fetch 30-day discrepancy history for this employee
    (IDiscrepancyEngineService.GetDiscrepanciesForRangeAsync)

  Step 2: Determine enrichment path:

    IF no history (first-ever critical event for this employee):
      insight = "No prior discrepancy history. This is the first detected event."
      → No Claude API call (saves cost, prevents meaningless insight)

    IF history exists:
      Build prompt:
        "An employee has a critical discrepancy alert today with {X} unaccounted minutes.
         Past 30 days: {N} critical events, {M} high events, avg {Y} min unaccounted.
         Provide a 2–3 sentence neutral, factual insight for the manager.
         Note whether this is a pattern or an anomaly."

      → AnthropicInsightProvider.GetInsightAsync(prompt)
         Model: claude-sonnet-4-6
         Max tokens: 300
         System prompt: "HR analytics assistant. Neutral. Factual. No accusation."
      → Returns 2–3 sentence insight string

  Step 3: Send notification to manager
    INotificationService.SendAsync:
      Recipient:    manager of the employee
      Type:         DiscrepancyAlertEnriched
      Data:         { employeeId, severity: "critical", unaccountedMinutes, insight }
    → Manager receives in-app notification (SignalR push) + email
```

---

## S. Manager Response to Alerts

**Actor:** Manager  
**Entry:** In-app notification OR Workforce Intelligence → Alerts panel

```
[View Alert]
  Alert card shows:
    Employee name, date, alert type (exception or discrepancy)
    Severity level (none / low / high / critical)
    Metric details (e.g., "247 unaccounted minutes — 4.1σ above baseline")
    [If critical discrepancy]: AI-enriched narrative insight (2–3 sentences)
    Severity method: "baseline_relative" or "absolute (new employee)"

[Manager Actions]
  Acknowledge    → alert status = "acknowledged", audit log
  Add comment    → comment written to alert, audit trail
  Escalate       → alert forwarded to HR Admin, notification sent
  Request screenshot (if permitted by policy):
    → POST /api/v1/agents/{agentId}/capture-screenshot
    → Command pushed via SignalR → agent captures → result returned
    → Screenshot displayed in panel (real-time via SignalR)
  Create note    → disciplinary or observation note on employee profile

[Bulk Actions]
  Manager can bulk-acknowledge alerts for their team
  Filters: by date range, severity, employee, alert type
```

---

## T. Productivity Analytics

**Actor:** Manager + HR Admin (`analytics:view`, `analytics:export`)  
**Entry:** Workforce Intelligence → Productivity

```
[Dashboard Views]
  Daily summary per employee:
    Total active minutes, idle minutes, app breakdown, intensity score
    Activity timeline (visual blocks of active vs idle periods)

  Weekly summary:
    Trend chart (this week vs last 3 weeks)
    Top apps by time spent, categorised

  Team comparison:
    Side-by-side productivity scores for manager's direct reports
    Flagged employees (below team average by > 1σ)

[Export]
  CSV / PDF export of any view
  Date range selector
  Filter by department, team, individual employee

[Data Source]
  daily_employee_report + weekly_employee_report + monthly_employee_report
  wms_productivity_snapshots (if WMS integration enabled)
  Score composite = agent-based data + WMS data (via IProductivityAnalyticsService)
```

---

## U. Tenant Configuration & Monitoring Toggles

**Actor:** HR Admin (`monitoring:configure`, `settings:admin`)  
**Entry:** Settings → Workforce / Settings → Tenant

```
[Monitoring Feature Toggles — Tenant-Wide Defaults]
  activity_monitoring:      on/off
  application_tracking:     on/off
  screenshot_capture:       on/off (Phase 1: only on-demand, never automated)
  meeting_detection:        on/off
  device_tracking:          on/off
  identity_verification:    on/off
  verification_interval:    minutes (e.g., 60)
  idle_threshold:           seconds (e.g., 300)

[Transparency Mode]
  Full:    Employees see all their own monitoring data
  Partial: Employees see daily summaries only (no raw app-level detail)
  Covert:  Employer only — employees see nothing (GDPR consent still required)

[App Allowlist]
  Mode: allowlist / blocklist / off
  Per app: name, category, allowed: true/false
  alert_on_violation: true/false, violation_threshold_minutes

[Employee-Level Overrides]
  HR Admin → Employee profile → Monitoring tab
  Override any tenant default for this specific employee
  Example: disable screenshots for senior executives

[Role-Level Overrides]
  Organisation → Job Families → per level → Monitoring Overrides
  Override tenant defaults for all employees at this level

[Policy Merge Order]
  tenant_default → role_override → employee_override (most specific wins)
  On any change: RefreshPolicy command pushed to affected agents via SignalR

[Data Retention Policies]
  Raw activity data: configurable retention (default: 90 days)
  Screenshots: shorter retention (default: 30 days, or per jurisdiction)
  Audit logs: never deleted (compliance)
  Migration files: 48h after success, 7 days after failure
```

---

## V. GDPR Consent Management

**Actor:** Employee (consents) + HR Admin (monitors)  
**Entry:** First login (if monitoring enabled) OR explicit consent request

```
[Consent Flow]
  Triggered when: employee account created + monitoring is enabled for their profile
  → Consent overlay shown on first login (cannot be skipped if monitoring is active)

  Consent types presented:
    data_processing: "ONEVO processes your employment data..."
    monitoring:      "Your employer has enabled activity monitoring on your device..."

  Employee: Accept / Decline each type
  → gdpr_consent_records entries written per consent type
  → If monitoring declined: agent receives MonitoringDisabled flag on next policy fetch
                             monitoring stops for this employee
                             HR Admin notified

[HR Admin View]
  Settings → Compliance → Consent Status
  Table: employee, consent type, consented (yes/no), date, IP address
  Can filter: employees who declined monitoring

[Right to Erasure (future — not Phase 1)]
  Planned for Phase 2 compliance module.
  Phase 1 prepares: all employee data is tagged with tenant_id + employee_id for targeted erasure.
```

---

## W. Calendar

**Actor:** HR Admin (create/manage) + All (view)  
**Entry:** Calendar menu item

```
[HR Admin — Create Events]
  New event: title, date/time, recurrence, description, attendees
  Event types: company holiday, all-hands, training, deadline
  → calendar_events entry created
  → notifications sent to relevant employees

[All Users — View]
  Personal calendar view: own events + approved leave + company events
  Conflict detection:
    When submitting leave: system checks calendar_events for overlapping dates
    → Manager alerted if conflict exists (not a hard block)

[Phase 2 Readiness]
  calendar_events table has external_id + external_source columns (nullable in Phase 1)
  → Ready for Google Calendar OAuth sync in Phase 2 (no migration needed)
```

---

## X. Notification Delivery

**Actor:** System (generates) + All (receives)

```
[Event → Notification pipeline]
  Domain events (MediatR) → Notification Engine

  Channels per notification type:
    in-app:  SignalR push → real-time banner + notification bell count
    email:   Resend API → template rendered → sent to employee/manager email
    webhook: POST to tenant-configured webhook URL (40+ event types)

  Key notification events (Phase 1):
    leave.submitted           → manager (in-app + email)
    leave.approved            → employee (in-app + email)
    leave.rejected            → employee (in-app + email)
    exception.detected        → manager (in-app + email)
    discrepancy.critical      → manager (in-app + email, AI-enriched narrative)
    agent.heartbeat_lost      → manager (in-app)
    identity.mismatch         → manager (in-app + email)
    import.completed          → HR Admin (in-app + email)
    import.failed             → HR Admin (in-app + email)
    employee.promoted         → employee (in-app + email)
    onboarding.task_assigned  → assignee (in-app + email)

[Notification Templates]
  notification_templates table stores per-event templates
  Phase 2 modules add new templates (additive inserts only — no existing rows change)
```

---

## Y. User Invitations & Permission Management

**Actor:** Super Admin + HR Admin (`roles:manage`)

```
[Invite User]
  Settings → Users → "Invite User"
  Enter email + select role template
  → Invitation email sent (time-limited token)
  → User clicks link → sets password → first login

[Role Management]
  Create role: name + select permissions from 90+ available permission codes
  System roles (HR Admin, Manager, Employee) cannot be deleted
  Custom roles: create as many as needed, fully configurable

[Assign Role to Employee]
  Employee profile → Roles tab → pick role
  → user_roles entry written
  → Effective permissions recalculated on next request

[Permission Overrides (per-employee)]
  Employee profile → Permissions tab
  Super Admin only: grant or revoke individual permissions independent of role
  → user_permission_overrides entry written (grant_type: "grant" or "revoke")
  → Override always wins over role template
  Reason field required (audit trail)

[Feature Access Grants (module-level)]
  Settings → Feature Access
  Toggle entire modules on/off for a role or individual employee
  Example: enable payroll:read for one specific HR Admin who manages compensation audits
  → feature_access_grants entry written
  → Permission resolver checks feature grant before evaluating module permissions

[Password Reset]
  Self-service: "Forgot password" on login screen
  → Email sent with time-limited reset link
  → Employee sets new password → old sessions revoked
```

---

## Z. System Background Job Schedule

**Actor:** System (Hangfire)

| Time | Job | Queue | Purpose |
|:-----|:----|:------|:--------|
| Every 60 sec | Agent heartbeat received (per agent) | — | Update last_heartbeat_at |
| Every 1 min | `ExpirePendingCommandsJob` | High | Expire undelivered agent commands |
| Every 5 min | `DetectOfflineAgentsJob` | High | Fire AgentHeartbeatLost if >5 min silent |
| Continuous | Raw data processing (async from ingestion) | Default | Process activity_raw_buffer → sessions |
| 9:45 PM | `ComputeActivityBaselinesJob` | Default | Roll 30-day avg+σ per employee per metric → employee_activity_baselines |
| 10:00 PM | `ComputeDiscrepancyBaselinesJob` | Default | Roll 30-day avg+σ per employee for discrepancy_events → employee_discrepancy_baselines |
| 10:30 PM | `DiscrepancyEngineJob` | Default | Cross-reference HR/WMS/calendar; z-score or absolute severity; fire DiscrepancyCriticalDetected |
| 10:35 PM | `ExceptionEngineJob` | Default | Evaluate all active exception rules against daily metrics; baseline_relative or absolute |
| 11:00 PM | `DailyAggregationJob` | Default | Compute daily/weekly/monthly employee reports |
| 3:00 AM | `CleanupRevokedAgentsJob` | Low | Remove health logs for revoked agents >30 days |
| 3:00 AM | `CleanupCompletedCommandsJob` | Low | Remove completed/expired commands >7 days |
| 3:00 AM | `CleanupOldBaselinesJob` | Low | Prune employee_discrepancy_baselines >90 days |
| 3:30 AM | `ImportFileCleanupJob` | Low | Delete S3 files: success imports >48h, failed >7 days |
| On event | `DiscrepancyEnrichmentHandler` | MediatR | Handle DiscrepancyCriticalDetected → fetch history → Claude API → enriched notification |

---

## End-to-End: New Tenant Journey (Full Sequence)

```
Day 0  — Registration + billing + company setup
Day 0  — HR Import Wizard: upload CSV, map columns, validate, import 231 employees
Day 0  — Post-import: assign department heads, configure job levels
Day 0  — Leave policies created, entitlements assigned
Day 0  — User invitations sent to managers and HR team

Day 1  — Managers and HR admins accept invitations, set passwords
Day 1  — Employees receive welcome emails, set passwords, complete onboarding tasks
Day 1  — Employees who need monitoring: GDPR consent on first login
Day 1  — Agent download links sent to employees requiring monitoring
Day 1  — Agents installed, registered, policies distributed

Week 1 — Day-to-day leave requests flowing through approval chains
Week 1 — Agent data flowing: keyboard/mouse, app usage, presence sessions
Week 1 — Daily aggregation jobs running nightly

Day 5+ — First statistical baseline data available (5-day minimum)
         Activity baselines and discrepancy baselines now have enough samples
         Exception Engine switches from absolute thresholds to z-score-relative evaluation
         Discrepancy Engine switches from absolute thresholds to z-score severity classification

Day 6+ — First discrepancy critical alert fires
         If employee has prior history: Claude narrative enrichment added to manager notification
         Manager sees: "This is the 3rd critical event in 30 days, avg 210 min unaccounted (σ=4.1)"

Month 1 — All baselines stable (30-day rolling window fully populated)
          False positive rate decreases: employees with naturally high unaccounted time
          no longer flagged unless they significantly deviate from their personal baseline
          Exception rules tuned by HR Admin based on real data patterns
```

---

*This document covers all Phase 1 modules and both plans (HR Import Onboarding, Intelligence Layer). Phase 2 modules (Payroll, Performance, Skills full module, Documents, Grievance, Expense, Reporting) build on top of the Phase 1 foundation documented here — all Phase 1 → Phase 2 transitions are additive and safe (see `docs/phase-compatibility-guide.md`).*
