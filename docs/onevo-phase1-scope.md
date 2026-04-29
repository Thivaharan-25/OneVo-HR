# OneVo — Phase 1 Full Scope Document

**Prepared for:** Client  
**Date:** April 2026  
**Phase:** Phase 1 (Active Delivery)  
**Status:** In Development — 4-week delivery plan, 4 developers

---

## Table of Contents

1. [What Is OneVo?](#1-what-is-onevo)
2. [Platform Architecture](#2-platform-architecture)
3. [Product Tiers](#3-product-tiers)
4. [Module-by-Module Breakdown (Phase 1)](#4-module-by-module-breakdown-phase-1)
   - 4.1 Infrastructure
   - 4.2 Auth & Security
   - 4.3 Org Structure
   - 4.4 Core HR — Employee Lifecycle
   - 4.5 Skills Core
   - 4.6 Leave Management
   - 4.7 Calendar
   - 4.8 Configuration
   - 4.9 Agent Gateway
   - 4.10 Activity Monitoring
   - 4.11 Discrepancy Engine
   - 4.12 Workforce Presence
   - 4.13 Exception Engine
   - 4.14 Identity Verification
   - 4.15 Productivity Analytics
   - 4.16 Shared Platform
   - 4.17 Notifications
5. [Desktop Monitoring Agent — Deep Dive](#5-desktop-monitoring-agent--deep-dive)
6. [Developer Platform — Internal Operator Console](#6-developer-platform--internal-operator-console)
7. [Phase 2 Modules](#7-phase-2-modules-defined-not-built-in-phase-1)
8. [Cross-Module Scenarios](#8-cross-module-scenarios)
9. [User Flows at a Glance](#9-user-flows-at-a-glance)
10. [Technical Highlights](#10-technical-highlights)
11. [Delivery Timeline](#11-delivery-timeline)
12. [Database Scale Summary](#12-database-scale-summary)

---

## 1. What Is OneVo?

OneVo is a **multi-tenant, white-label SaaS platform** that combines two product pillars into a single unified system:

**Pillar 1 — HR Management**
Everything a company needs to manage the full employee lifecycle: hiring, onboarding, leave, payroll, skills, performance reviews, documents, expenses, and grievances.

**Pillar 2 — Workforce Intelligence**
Real-time visibility into how work is actually happening: desktop activity monitoring, workforce presence and attendance, identity verification, automated exception detection, and productivity analytics — all powered by a lightweight desktop agent installed on employee machines.

**Optional Third Pillar — Work Management System (WMS) Integration**
OneVo connects to an external Work Management System (projects, tasks, sprints, OKRs, chat) via 5 bridge contracts. This is consumed by the OneVo frontend — the WMS is built and maintained by a separate team.

### At a Glance

| Property | Value |
|:---------|:------|
| Type | Multi-tenant white-label SaaS |
| Backend | .NET 9 - Clean Architecture + CQRS |
| Frontend | Vite + React 19 (React Router v7) |
| Desktop Agent | .NET MAUI + Windows Service |
| Database | PostgreSQL 16 with Row-Level Security |
| Phase 1 Tables | 133 across 17 modules |
| Total Tables (Phase 1 + 2) | 175 across 23+ modules |
| Team Size | 4 developers |
| Delivery | 4 weeks |

---

## 2. Platform Architecture

### Overview Diagram

```
┌──────────────────────────────────────────────────────────┐
│                    End Users (Customers)                  │
│              HR Managers · Employees · Executives        │
└───────────────────────────┬──────────────────────────────┘
                            │  HTTPS
                            ▼
┌──────────────────────────────────────────────────────────┐
│              app.onevo.io — Main Frontend                │
│           Vite + React 19 (React Router v7)                 │
│   Single app consuming OneVo backend + WMS backend       │
└────────────────┬─────────────────────┬───────────────────┘
                 │ Tenant JWT           │ Bridge API key
                 ▼                     ▼
┌──────────────────────┐   ┌──────────────────────────────┐
│   OneVo Backend      │   │     WMS Backend              │
│   .NET 9             │   │   (External team)            │
│   /api/v1/*          │   │   5 bridge contracts         │
│   23+ modules        │   │   Projects · Tasks           │
│   1 PostgreSQL DB    │   │   Sprints · OKRs · Chat      │
└──────────┬───────────┘   └──────────────────────────────┘
           │
           │  HTTPS + Device JWT
           ▼
┌──────────────────────────────────────────────────────────┐
│      Desktop Agent (per employee machine)                │
│   .NET MAUI tray app + Windows Service                   │
│   Collects: activity, screenshots, identity photos       │
│   Heartbeats every 60 seconds                            │
└──────────────────────────────────────────────────────────┘

Internal Only (VPN-gated):
┌──────────────────────────────────────────────────────────┐
│   console.onevo.io — Developer Platform (Operator UI)    │
│   Next.js — separate app, separate domain                │
│   Used only by OneVo engineering team                    │
└──────────────────────────┬───────────────────────────────┘
                           │  Platform-Admin JWT
                           ▼
                  OneVo Backend /admin/v1/*
```

### Key Architectural Decisions

**Clean Architecture + CQRS - Not Microservices**
The backend is one deployable .NET 9 application organized into Domain, Application, Infrastructure, and API host projects. Features are folders inside those layers, with strict dependency rules enforced by architecture tests.

**Clean Architecture Layers**
Every feature follows the shared 4-layer solution structure:
- `Domain` — entities, value objects, domain events
- `Application` — commands, queries, handlers (MediatR/CQRS)
- `Infrastructure` — EF Core, external services, repository implementations
- `Api` — controllers, request/response DTOs

**Multi-Tenancy by Default**
Every database table includes a `tenant_id` column. Tenant isolation is enforced at two layers simultaneously:
1. PostgreSQL Row-Level Security (RLS) — database rejects cross-tenant queries at the DB level
2. Application layer — ITenantContext injects tenant_id into every query

**Single Database, 175 Tables**
One PostgreSQL 16 database serves all tenants and all modules. All 175 tables belong to a single `ApplicationDbContext`. This is a deliberate choice — it eliminates the distributed transaction complexity of microservices while keeping module code boundaries clean.

**Event-Driven Cross-Module Integration**
When features need to communicate, they publish in-process MediatR domain events. Phase 1 does not require RabbitMQ or MassTransit.

**CQRS with MediatR**
Commands (writes) and Queries (reads) are separated throughout the application. Every command goes through a handler, validation (FluentValidation), and authorization check. This makes every write operation explicit, traceable, and testable.

**Result<T> Over Exceptions**
The application never throws exceptions for business logic failures. Every operation returns a `Result<T>` — a discriminated union of success or error — which forces callers to handle failure explicitly. Exceptions are reserved for truly unexpected infrastructure failures.

---

## 3. Product Tiers

OneVo is sold in configurable tiers. Each tenant gets exactly the modules they subscribe to — unsubscribed modules are disabled at the feature flag level and their API endpoints return 403.

| Tier | What's Included |
|:-----|:---------------|
| **HR Management** | Infrastructure + Auth + Org Structure + Core HR + Leave + Calendar + Skills (core) + Performance + Payroll + Documents + Notifications + Shared Platform |
| **Work Management** | Infrastructure + Auth + WMS bridge (People Sync contract only) |
| **HR + Workforce Intel** | Everything in HR Management + Activity Monitoring + Workforce Presence + Identity Verification + Exception Engine + Productivity Analytics + Agent Gateway |
| **HR + Work Management** | Everything in HR Management + WMS full integration (all 5 bridge contracts) |
| **Full Suite** | All modules + WMS + Workforce Intelligence |

**Core (always active in every tier):** Infrastructure, Auth, Notifications, Shared Platform

---

## 4. Module-by-Module Breakdown (Phase 1)

Phase 1 delivers 17 modules with 133 database tables. Every module is explained below with its purpose, what it does, and its tables.

---

### 4.1 Infrastructure

**Purpose:** The absolute foundation. Provides global reference data and the two hub tables that almost every other table references.

**What it contains:**
- **Tenants** — each customer organisation is a tenant. The `tenants` table is the most-referenced table in the system (102 other tables have a foreign key to it). Includes subscription plan, status (active / provisioning / suspended), and branding config link.
- **Users** — authentication identities. A user has an email, password hash, MFA secret, and status. The `users` table is referenced by 56 other tables.
- **Countries** — ISO country reference list. Used by legal entities, leave policies, public holidays, and employee nationality.
- **File Records** — a central registry of all uploaded files (documents, photos, receipts, certificates). Every file upload creates a `file_records` row and 10 other tables reference it.

**Tables (4):** `tenants`, `users`, `countries`, `file_records`

---

### 4.2 Auth & Security

**Purpose:** Controls who can log in, what they can see, and what they can do. OneVo uses a fully dynamic, permission-based access control system — not hard-coded roles.

**What it does:**

**Authentication**
- JWT-based login (email + password) with configurable session TTL per tenant
- MFA: TOTP-based (Google Authenticator, Authy) — optional per tenant, mandatory per role or per employee
- SSO: Google OAuth and Azure Active Directory (configured per tenant in Shared Platform)
- Password reset: self-service via email link + admin-initiated reset
- Session tracking: every active session recorded, admins can revoke sessions

**Authorisation — RBAC with Employee-Level Overrides**
- Roles are created dynamically per tenant (e.g., "HR Manager", "Team Lead", "Payroll Officer") — there are no hard-coded system roles
- Each role is assigned a set of permissions from 90+ available granular permissions
- Permissions follow the pattern `resource:action` — e.g., `employees:read`, `leave:approve`, `payroll:run`, `monitoring:configure`
- Any permission can be overridden at the individual employee level (grant or revoke beyond their role)
- This means: an employee can be given `payroll:read` without being assigned the full Payroll Officer role

**GDPR & Compliance**
- Consent records: when monitoring is enabled, employees must give GDPR consent — recorded in `gdpr_consent_records`
- Audit logs: every write operation is logged with who did what, when, from which IP, on which tenant
- Feature access grants: when a feature is temporarily unlocked for a specific user (time-limited grants)

**Tables (9):** `roles`, `permissions`, `role_permissions`, `user_roles`, `user_permission_overrides`, `sessions`, `audit_logs`, `gdpr_consent_records`, `feature_access_grants`

**Key User Flows:**
- User invitation → role assignment → first login
- Role creation → permission selection → assign to employees
- MFA setup (employee self-service)
- GDPR consent collection (required before monitoring activates)
- Audit log review (admin/compliance officer)

---

### 4.3 Org Structure

**Purpose:** Defines the skeleton of the customer's organisation — the hierarchy, legal entities, job structure, and teams that everything else references.

**What it does:**

**Legal Entities**
- A company may have multiple legal entities (subsidiaries, country-specific entities). Each has its own country, registration details, and address. Leave policies, payroll runs, and offices are scoped to legal entities.

**Department Hierarchy**
- Departments form a parent-child tree (e.g., Engineering → Backend Team → API Squad). Each department can have a head employee. Departments are used for leave approvals, monitoring overrides, and onboarding templates.

**Job Structure**
- Job Families: broad groupings (e.g., "Engineering", "Sales", "Finance")
- Job Levels: seniority within a family (e.g., L1 → L5 with salary bands)
- Job Titles: specific titles (e.g., "Senior Software Engineer") linked to a family + level
- This three-tier structure drives leave policy assignment, skill requirements, and compensation bands

**Teams**
- Lightweight grouping separate from department hierarchy. A team has a lead and members. Teams are used for task assignment in WMS.

**Cost Centers**
- Financial allocation units linked to departments. Used for expense tracking and payroll reporting.

**Office Locations**
- Physical office addresses per legal entity. Used for identity verification (GPS matching), presence tracking, and public holiday calendars.

**Tables (9):** `legal_entities`, `departments`, `job_families`, `job_levels`, `job_titles`, `teams`, `team_members`, `office_locations`, `department_cost_centers`

**Key User Flows:**
- Create legal entity → link to country + offices
- Build department hierarchy → assign head
- Define job family → add levels with salary bands → create job titles
- Create team → assign lead + members
- Set up cost centers → link to departments

---

### 4.4 Core HR — Employee Lifecycle

**Purpose:** The central module. Every person who works at a tenant company is an employee record. This module manages the full journey from hire to exit.

**What it does:**

**Employee Profile**
- The `employees` table has 25 columns covering: personal info (name, DOB, national ID, nationality), work info (employment type, start date, job title, department, manager, office location), status (active / on-leave / terminated), and photo.
- Extended profile tables: addresses, bank details (for payroll), emergency contacts, dependents (for benefits), and custom fields (tenant-configurable extra fields)

**Qualification Tracking**
- Education history, professional certifications, previous work experience — each stored with dates and supporting documents (linked to `file_records`)

**Onboarding**
- Onboarding templates: admin creates templates per department with a task checklist (e.g., "Sign employment contract", "Set up workstation", "Complete security training")
- When an employee is hired, an onboarding task list is created from the template
- Tasks are assigned to specific people (HR, IT, manager), tracked with completion status

**Lifecycle Events**
- Every significant change to an employee's record generates a lifecycle event: hire, transfer, promotion, salary change, termination. This creates a complete audit trail of the employee's history at the company.

**Salary History**
- Every compensation change is recorded with effective date, who approved it, and reason. This feeds into payroll and reporting.

**Offboarding**
- Exit workflow: HR initiates → checklist (return equipment, revoke access, final payroll calculation, exit interview) → each step tracked → on completion, employee status set to `terminated`, auth sessions revoked, desktop agent unregistered

**Tables (13):** `employees`, `employee_addresses`, `employee_bank_details`, `employee_emergency_contacts`, `employee_dependents`, `employee_qualifications`, `employee_salary_history`, `employee_work_history`, `employee_custom_fields`, `employee_lifecycle_events`, `onboarding_templates`, `onboarding_tasks`, `offboarding_records`

**Key User Flows:**
- Full onboarding: create employee → assign role → assign leave entitlements → create onboarding checklist → notify
- Profile management: self-service for own profile, manager/HR for team
- Promotion: title + level change → salary revision → lifecycle event
- Transfer: department + manager change → shift reassignment + leave policy update
- Offboarding: exit checklist → access revocation → final pay trigger

---

### 4.5 Skills Core

**Purpose:** Provides the skill taxonomy and employee skill profiles needed for job matching, hiring decisions, and learning recommendations. The full Skills & Learning module (courses, LMS, development plans) is Phase 2 — this Phase 1 subset provides the structural foundation.

**What it does:**
- **Skill Taxonomy:** Admin defines skill categories (e.g., "Programming Languages", "Leadership") and individual skills within each (e.g., "Python", "TypeScript", "Conflict Resolution")
- **Job Skill Requirements:** Link skills to job families with a required proficiency level — enables gap analysis for hiring and promotions
- **Employee Skill Profiles:** Employees declare their own skills with self-assessed proficiency. Each skill can be marked as validated or pending validation.
- **Skill Validation:** Employee requests validation → manager or designated validator reviews → approves/rejects with notes. Validated skills appear prominently in the employee's profile.

**Tables (5):** `skill_categories`, `skills`, `job_skill_requirements`, `employee_skills`, `skill_validation_requests`

---

### 4.6 Leave Management

**Purpose:** End-to-end leave management — from configuring leave policies to employee requests and approvals, with automatic balance tracking and calendar integration.

**What it does:**

**Leave Types**
Admin defines the leave types the company offers: Annual Leave, Sick Leave, Maternity/Paternity Leave, Unpaid Leave, etc. Each type has a colour, rules (paid/unpaid, requires documentation), and whether it accrues.

**Leave Policies**
Policies are country-specific and job-level-specific. A policy defines: accrual rate, maximum days per year, carry-over rules (how many days carry to next year), notice period required, and which leave types it governs. Example: Malaysian employees at Level 1-2 get 14 days annual leave; Level 3+ get 21 days.

**Leave Entitlements**
When a policy is assigned to an employee, an entitlement record is created showing their total days, days used, and days remaining. Entitlements auto-update on approval.

**Request & Approval Workflow**
1. Employee submits leave request (type, dates, optional note/document)
2. System checks balance → calendar conflicts → routing rules
3. Approver receives notification → reviews → approves or rejects with comments
4. On approval: balance deducted, calendar event created, attendance system notified (so the employee shows as "on leave" in presence), payroll notified (if leave type affects pay)
5. Cancellation: employee can cancel pending or approved future leave (subject to policy rules)

**Leave Balance View**
Employees see their current balance per leave type, accrued vs. used, upcoming approved leave, and history. Managers see their whole team's balances.

**Tables (5):** `leave_types`, `leave_policies`, `leave_entitlements`, `leave_requests`, `leave_balances_audit`

**Key User Flows:**
- Admin: configure leave types → set policies per country/level → assign entitlements
- Employee: view balance → submit request → receive approval notification
- Approver: review request → approve/reject → employee notified
- Cross-module: approved leave → calendar block + attendance mark + payroll deduction

---

### 4.7 Calendar

**Purpose:** A shared organisational calendar that serves as the integration point between leave, shifts, meetings, and public holidays.

**What it does:**
- Create calendar events: meetings, company events, public holidays, training sessions
- Events are tenant-scoped and can be visible to specific departments or all employees
- Conflict detection: checks if a new leave request or shift conflicts with an existing calendar block
- Leave approvals and shift assignments create calendar events automatically

**Tables (1):** `calendar_events`

---

### 4.8 Configuration

**Purpose:** The settings control centre for tenant administrators. Every configurable behaviour — monitoring, integrations, data retention — is managed here.

**What it does:**

**Tenant Settings**
Global settings per tenant: timezone, locale, date format, working week definition, branding overrides, feature toggles. Stored in `tenant_settings`.

**Monitoring Feature Toggles**
Controls what the desktop agent tracks for this tenant. Each monitoring feature (app usage, browser activity, screenshots, idle detection, identity verification, meeting detection) can be turned on or off independently. Stored in `monitoring_feature_toggles`.

**Employee Monitoring Overrides**
Any monitoring setting can be overridden at the individual employee level. Example: disable screenshots for the Legal team's lawyers for confidentiality reasons, while keeping it on for the rest of the organisation. Stored in `employee_monitoring_overrides`.

**App Allowlists**
Tenant admin can define a whitelist of approved applications. If an employee uses an app not on the allowlist, it's flagged. Changes to the allowlist are audited. Stored in `app_allowlists` and `app_allowlist_audit`.

**Integration Connections**
Records of connected third-party systems (e.g., Slack for notifications, BambooHR for HR data sync). Stored in `integration_connections`.

**Tables (6):** `tenant_settings`, `monitoring_feature_toggles`, `employee_monitoring_overrides`, `app_allowlists`, `app_allowlist_audit`, `integration_connections`

---

### 4.9 Agent Gateway

**Purpose:** The communication backbone between the cloud backend and every desktop agent running on employee machines. This is the module that makes the Workforce Intelligence pillar possible.

**What it does:**

**Agent Registration**
When the desktop agent is installed on an employee's machine and runs for the first time, it sends a registration request to the backend with a unique machine ID and the tenant key embedded in the installer. The backend validates the tenant key, creates a `registered_agents` record (assigning a UUID), and the agent is now a known device in the system. Admin then maps each registered agent to an employee.

**Agent Sessions**
The `agent_sessions` table tracks which employee is currently logged in on each device. When the employee logs into the OneVo tray app, a new session is started. This is how the backend knows which employee's data is being submitted from which machine. Only one active session per device is allowed at any time.

**Policy Distribution**
The monitoring configuration (what to track, screenshot intervals, idle thresholds, identity photo settings) is compiled into a policy JSON document and stored in `agent_policies`. On every heartbeat, the agent checks if the policy has changed and pulls the latest version. This is a pull model — the agent controls its own update cycle, making it resilient to connectivity gaps.

**Command Dispatch**
Beyond policy configuration, admins and managers can send ad-hoc commands to specific agents via the `agent_commands` table. Commands are queued and picked up by the agent on its next heartbeat. Commands include:
- `capture_screenshot` — take an immediate screenshot
- `capture_photo` — take an immediate identity photo via webcam
- `start_monitoring` / `stop_monitoring` — activate or deactivate monitoring
- `pause_monitoring` / `resume_monitoring` — temporarily suspend and restore
- `refresh_policy` — force the agent to re-fetch its policy immediately

Each command has a 5-minute expiry — if the agent doesn't pick it up within 5 minutes (e.g., machine is off), the command expires automatically.

**Health Monitoring**
Every 60 seconds, the agent sends a health report: CPU usage, memory consumption, recent errors, and a tamper detection flag. If the Windows Service is stopped or modified externally, `tamper_detected` is set to true and an alert is raised. The backend uses the last heartbeat timestamp to determine online/offline status in real time via SignalR.

**Tables (4 + messaging):** `registered_agents`, `agent_sessions`, `agent_policies`, `agent_commands`, `agent_health_logs`

**Integration Events:** `AgentRegistered`, `AgentOffline`, `PolicyDistributed`

---

### 4.10 Activity Monitoring

**Purpose:** The data-capture heart of the Workforce Intelligence pillar. All raw activity data collected by the desktop agent flows into this module, where it is processed, categorised, and summarised.

**What it does:**

**Raw Data Ingest**
Activity data arrives from desktop agents as high-frequency events. The `activity_raw_buffer` holds unprocessed events for 7 days before they are archived. Raw events are processed into structured records by background jobs.

**Application Usage Tracking**
Every time an employee switches to a different application, the agent records the app name, window title, process name, and time spent. The backend classifies each application into a category (productive / neutral / unproductive / blocked) defined by the admin. Example: "Visual Studio Code" → Productive; "YouTube" → Unproductive. Stored in `application_usage`.

**Application Categories**
Admins create and manage categories and assign known applications to them. New applications discovered by agents are surfaced for admin review and categorisation. Stored in `application_categories`.

**Browser Activity**
URLs and domains visited during work hours. Stored in `browser_activity`. Sensitive domains can be excluded from logging.

**Screenshots**
Periodic screen captures at admin-configured intervals (5, 10, 15, or 30 minutes). Screenshot files are stored via the `file_records` system and references held in `screenshots`. Managers and HR can review screenshots in the Activity Snapshot View.

**Meeting / Video Call Detection**
The agent detects when an employee is in a video call (Zoom, Teams, Meet, etc.) based on process detection. Meeting sessions are recorded in `meeting_sessions` to distinguish between "idle" and "in a call" — an employee who's been idle at the keyboard for 40 minutes because they're in a video call is not unproductive.

**Idle Detection**
If no keyboard or mouse input is detected for the configured threshold (5/10/15 minutes), the agent marks the period as idle. Idle time is distinguished from active time in all productivity metrics.

**Device Tracking**
Which employee was using which machine, and when. Stored in `device_tracking`. Useful for detecting shared machine usage or unexpected device access.

**Daily Summaries**
A background job runs at end of day and compiles each employee's activity into a `activity_daily_summary` record: total active time, total idle time, top apps, productive vs. unproductive ratio. This is the primary input to the Productivity Analytics module.

**Activity Snapshots**
Point-in-time snapshots of an employee's current activity, used by the Live Dashboard to show what an employee is doing right now.

**Tables (9):** `activity_raw_buffer`, `activity_snapshots`, `activity_daily_summary`, `application_usage`, `browser_activity`, `screenshots`, `meeting_sessions`, `device_tracking`, `application_categories`

---

### 4.11 Discrepancy Engine

**Purpose:** Detects inconsistencies between what an employee reports in the Work Management System (time logs, task completion) and what the desktop agent actually observed.

**What it does:**
The Discrepancy Engine cross-references two data sources daily:
1. `wms_daily_time_logs` — time logged by the employee in the WMS (hours worked on tasks and projects)
2. `activity_daily_summary` — actual computer activity observed by the desktop agent

If the WMS shows an employee logged 8 hours but the agent only detected 3 hours of productive activity, a `discrepancy_events` record is created. Discrepancy events feed into the Exception Engine (which can raise alerts) and the Productivity Analytics dashboard.

**Tables (2):** `discrepancy_events`, `wms_daily_time_logs`

---

### 4.12 Workforce Presence

**Purpose:** Tracks when employees are at work — their shifts, clock-in/out, breaks, overtime, and attendance records. This is the physical presence layer, complementary to the digital activity layer of Activity Monitoring.

**What it does:**

**Shift Scheduling**
Admin defines shifts (e.g., "Morning Shift: 8am–4pm", "Night Shift: 10pm–6am") with start time, end time, break rules, and overtime thresholds. Shifts are assigned to employees via `shift_assignments`. Rosters are created for scheduling periods (e.g., monthly rosters). Stored in `shifts`, `work_schedules`, `employee_schedules`, `shift_assignments`, `roster_periods`, `roster_entries`.

**Clock-In / Clock-Out**
Employees clock in and out via:
- **Biometric terminal** — fingerprint or face scan at a physical device
- **Desktop agent** — detected automatically when the employee logs into the tray app on their work machine
- **Manual entry** — HR can enter attendance records manually

Presence sessions are recorded in `presence_sessions` and summarised in `attendance_records`.

**Break Tracking**
Breaks during the shift are tracked separately in `break_records`. Break duration is compared against the shift's configured break allowance.

**Device Sessions**
Links the desktop agent session to a presence session — so the system knows that the employee's computer activity is correlated with their physical clock-in.

**Overtime**
When an employee works beyond their shift's end time, an overtime record is created. Overtime requires approval (stored in `overtime_records`). Approved overtime feeds into payroll calculations.

**Attendance Corrections**
If an employee forgets to clock in, or the biometric reader fails, HR or the employee can submit an attendance correction. The correction goes through an approval workflow before the attendance record is updated.

**Public Holidays**
Per-country public holiday calendar (`public_holidays`). Used to automatically mark days as non-working and exclude them from leave balance deductions.

**Tables (12):** `shifts`, `work_schedules`, `employee_schedules`, `shift_assignments`, `roster_periods`, `roster_entries`, `presence_sessions`, `attendance_records`, `break_records`, `device_sessions`, `overtime_records`, `public_holidays`

**Key User Flows:**
- Admin: define shifts → create roster → assign employees
- Employee: clock in (biometric/agent) → work → clock out
- Manager: review attendance → approve overtime → correct missed clock-ins
- HR: manage public holiday calendar per country

---

### 4.13 Exception Engine

**Purpose:** An automated anomaly detection system that continuously monitors employee activity and presence data, raises alerts when predefined rules are violated, and routes those alerts to the right people.

**What it does:**

**Exception Rules**
Admin defines rules that describe what constitutes an anomaly. Each rule has:
- A condition (e.g., "idle time > 45 minutes", "GPS location doesn't match assigned office", "no clock-in by 9:15am", "unproductive app usage > 60%")
- A severity level (Low / Medium / High / Critical)
- A scope (all employees, specific department, specific employee)

Rules are stored in `exception_rules`. Example rules:
- Flag if an employee is idle for more than 45 minutes without a meeting
- Flag if an employee uses a blocked application for more than 10 minutes
- Flag if the desktop agent's identity verification fails 3 times in a row
- Flag if an employee hasn't clocked in 15 minutes after their shift started

**Scheduled Evaluation**
Exception rules are evaluated on a schedule (configured per rule — e.g., every 15 minutes for real-time rules, daily for daily summary rules). `exception_schedules` controls the evaluation timing.

**Alert Generation**
When a rule condition is met, an `exception_alerts` record is created with the employee, rule, timestamp, severity, and evidence data (e.g., screenshot URL, GPS coordinates, idle duration).

**Alert Review & Acknowledgement**
Alerts appear in the Exception Dashboard (visible to managers/HR with the `exceptions:view` permission). Each alert can be:
- Acknowledged with a note (e.g., "Employee was in an unscheduled meeting — verified with manager")
- Escalated up the escalation chain if unacknowledged within a time window

**Escalation Chains**
If an alert is not acknowledged within its SLA window, it escalates. An escalation chain defines who gets notified at each level. Example: Level 1 → Direct manager (30 min). Level 2 → HR manager (60 min). Level 3 → CEO (120 min). Stored in `escalation_chains`.

**Tables (5):** `exception_rules`, `exception_schedules`, `exception_alerts`, `alert_acknowledgements`, `escalation_chains`

**Key User Flows:**
- Admin: define exception rules → set escalation chains
- System: evaluate rules on schedule → create alerts automatically
- Manager: open exception dashboard → review alerts → acknowledge with notes
- HR: escalation review for unacknowledged high-severity alerts

---

### 4.14 Identity Verification

**Purpose:** Confirms that the person sitting at the computer is actually the employee they're supposed to be. Uses webcam-based identity photo capture and biometric device support.

**What it does:**

**Verification Policies**
Admin configures the verification policy per tenant: how often to capture identity photos (e.g., every 30 minutes), the matching confidence threshold, and what to do on a mismatch (flag for review, raise an alert, notify manager). Stored in `verification_policies`.

**Biometric Enrollment**
Each employee must be enrolled with a reference photo before identity verification can run. Enrollment can happen via:
- **Webcam** during first login through the desktop agent
- **Biometric terminal** at the office entrance (fingerprint or face scan)

Enrollment records stored in `biometric_enrollments`.

**Automatic Identity Photo Capture**
At the configured interval, the desktop agent silently captures a photo via the employee's webcam. The photo is sent to the backend. The backend compares it against the enrolled reference photo. Result: `match`, `no_match`, or `inconclusive`. The photo file is stored in `file_records`; the verification result in `verification_records`.

**Biometric Devices (Physical Terminals)**
Physical biometric readers at office entrances are registered in `biometric_devices` and linked to an office location. When an employee uses a terminal to clock in, the biometric event is recorded in `biometric_events` and used to create/confirm a presence session.

**Verification Review**
HR and managers with `verification:review` permission see a dashboard of flagged verifications. Each flagged event shows the captured photo, the reference photo, confidence score, and timestamp. Reviewer can mark it as a false positive or escalate.

**Audit**
All biometric data access is logged in `biometric_audit_logs` for compliance purposes.

**Tables (6):** `verification_policies`, `biometric_devices`, `biometric_enrollments`, `biometric_events`, `verification_records`, `biometric_audit_logs`

---

### 4.15 Productivity Analytics

**Purpose:** Aggregates all the raw activity, presence, and WMS data into structured, time-windowed reports that give managers and executives an objective view of workforce productivity.

**What it does:**

**Daily, Weekly, Monthly Employee Reports**
Background jobs run at end of each period and compile a structured report per employee:
- Total active time vs. idle time vs. time-in-meetings
- Productive app usage % vs. unproductive %
- Top 5 applications used
- Clock-in punctuality rate
- Discrepancy score (WMS time logged vs. actual activity)
- Comparison vs. team average

Stored in `daily_employee_report`, `weekly_employee_report`, `monthly_employee_report`.

**WMS Productivity Snapshots**
Cross-pillar snapshots that map WMS task completion rates and OKR progress to the activity monitoring data. Shows: tasks completed per hour of active time, sprint velocity correlated with focus time. Stored in `wms_productivity_snapshots`.

**Workforce Snapshot**
An org-level point-in-time view: how many employees are active right now, what's the overall productivity score across the organisation, which departments are trending up or down. Stored in `workforce_snapshot`. Refreshed periodically.

**Tables (5):** `daily_employee_report`, `weekly_employee_report`, `monthly_employee_report`, `wms_productivity_snapshots`, `workforce_snapshot`

---

### 4.16 Shared Platform

**Purpose:** Cross-cutting infrastructure shared by all modules. This is the "plumbing" of the platform — workflows, subscriptions, webhooks, real-time connections, and WMS bridge configuration.

**What it contains (33 tables):**

**Workflow Engine**
Powers all approval workflows in the system (leave approval, expense approval, overtime approval, attendance corrections, offboarding sign-off). Workflows are defined as step sequences with assignee roles and SLA timeouts. Tables: `workflow_definitions`, `workflow_steps`, `workflow_instances`, `workflow_step_instances`, `approval_actions`.

**Feature Flags**
Global and per-tenant feature flags control which modules and features are enabled. Used by the Developer Platform to enable/disable features without code deployment. Tables: `feature_flags`, `tenant_feature_flags`.

**Subscription & Billing**
Subscription plans, tenant subscriptions, invoices, and payment methods. Tables: `subscription_plans`, `plan_features`, `tenant_subscriptions`, `subscription_invoices`, `payment_methods`.

**Webhooks**
Tenants can configure outbound webhooks to receive real-time event notifications in their own systems. Tables: `webhook_endpoints`, `webhook_deliveries`.

**API Keys**
Tenant-level API keys for programmatic access. Tables: `api_keys`.

**Real-Time Infrastructure**
SignalR connection tracking for live dashboard updates (agent online/offline, alert notifications, presence changes). Table: `signalr_connections`. Rate limiting per tenant: `rate_limit_rules`.

**SSO**
SSO provider configuration per tenant (Google, Azure AD). Table: `sso_providers`. Auth tokens: `refresh_tokens`.

**Notification Infrastructure**
Notification templates (email, push, in-app) and delivery channels. Tables: `notification_templates`, `notification_channels`.

**Compliance**
Data retention policies, legal holds (freeze data from deletion during legal proceedings), compliance exports (GDPR data subject requests). Tables: `retention_policies`, `legal_holds`, `compliance_exports`.

**Scheduled Tasks**
Background job scheduling for recurring system tasks (report generation, entitlement renewal, snapshot refresh). Table: `scheduled_tasks`.

**WMS Bridge**
Configuration for the WMS integration: bridge API keys exchanged with the WMS backend, tenant linking, and role mapping (OneVo HR roles mapped to WMS roles for People Sync). Tables: `bridge_api_keys`, `wms_tenant_links`, `wms_role_mappings`.

**Tenant Branding**
Logo, primary colour, and custom domain config. Table: `tenant_branding`.

**User Preferences**
Per-user UI preferences (language, notification settings, theme). Table: `user_preferences`.

**Hardware Terminals**
Registration of physical hardware terminals (biometric readers, time-clock kiosks). Table: `hardware_terminals`.

**Tables (33):** see above categories.

---

### 4.17 Notifications

**Purpose:** Delivers real-time and asynchronous notifications to users across all channels — in-app inbox, email, and push.

**What it does:**
- Triggered by events from other modules (leave approved, alert raised, task assigned, offboarding initiated)
- Uses templates from Shared Platform to compose the message body
- Delivers via user's configured channels (in-app always; email and push per user preference)
- In-app inbox: user sees all notifications, can mark as read, dismiss, or click through to the relevant record
- Real-time: in-app notifications are pushed via SignalR — no page refresh needed

**Database tables:** Notifications owns no tables of its own. It uses `notification_templates` and `notification_channels` from Shared Platform, and delivers events via the messaging bus.

---

## 5. Desktop Monitoring Agent — Deep Dive

The desktop agent is the most technically distinctive component of OneVo. It is what makes the Workforce Intelligence pillar possible — without the agent, there is no activity data, no presence tracking from machines, no identity verification, and no productivity analytics.

### What It Is

A **dual-component desktop application** for Windows:

1. **Windows Service** — runs in the background with SYSTEM or a dedicated service account. It is the data collection engine. It survives user logoffs and machine restarts. Runs 24/7 from the moment the machine boots.

2. **.NET MAUI Tray Application** — a lightweight tray icon in the Windows system tray. This is the user-facing component. Employees see the OneVo icon in their tray. They log in via the tray app, which starts their session. The tray app can also show them their current monitoring status and sync state.

Both components are deployed together as a single `.msi` installer package.

### Installation & Registration

```
Admin in OneVo UI
    â†“ Downloads .msi with embedded tenant key
    â†“
IT deploys via Group Policy / SCCM / manual install
    â†“
Agent installs Windows Service + MAUI tray app
    â†“
On first run: agent sends registration request to backend
    │  → machine ID (generated at install, unique per device)
    │  → tenant key (embedded in installer)
    â†“
Backend validates tenant key → creates registered_agents record → assigns UUID
    â†“
Admin maps registered agent to employee
    │  (auto-matched by Windows login username if possible, manual otherwise)
    â†“
Backend compiles monitoring policy → agent pulls policy on next heartbeat
    â†“
Agent begins collecting data per policy configuration
```

### What the Agent Collects

| Data Type | Mechanism | Default Interval | Tenant Configurable |
|:----------|:----------|:----------------|:-------------------|
| Application usage | Window title + process name sampling | Continuous | ON/OFF |
| Browser activity | Process/extension hook | Continuous | ON/OFF |
| Screenshots | Screen capture | Every 10 min | ON/OFF + 5/10/15/30 min |
| Identity photos | Webcam capture | Every 30 min | ON/OFF + interval |
| Meeting detection | Process detection (Zoom, Teams, Meet) | Continuous | ON/OFF |
| Idle detection | Keyboard/mouse inactivity | 10-min threshold | ON/OFF + threshold |
| Health heartbeat | CPU%, memory, errors, tamper flag | Every 60 sec | Always on |

### Agent ↔ Backend Communication

```
Agent (on employee machine)                    Backend (cloud)
─────────────────────────────                  ────────────────
Every 60 seconds:
  POST /api/v1/agent/heartbeat  ──────────────â–º  Update last_heartbeat_at
  GET  /api/v1/agent/policy     ──────────────â–º  Return policy if changed
  GET  /api/v1/agent/commands   ──────────────â–º  Return pending commands

On activity event:
  POST /api/v1/agent/ingest     ──────────────â–º  Write to activity_raw_buffer

On screenshot / photo:
  POST /api/v1/agent/file       ──────────────â–º  Write to file_records → activity/verification
```

**Authentication:** The agent authenticates with a Device JWT (issued at registration). The employee additionally authenticates via the tray app when they log in (creating an agent session).

**Offline Resilience:** If the network is unavailable, the agent queues data locally and flushes on reconnect. Commands expire after 5 minutes if not delivered.

### Command Dispatch

Managers and admins can push commands to specific agents from the OneVo UI:

| Command | Effect |
|:--------|:-------|
| `capture_screenshot` | Agent takes an immediate screenshot and uploads it |
| `capture_photo` | Agent takes an immediate webcam photo for identity check |
| `start_monitoring` | Resume all monitoring (if previously stopped) |
| `stop_monitoring` | Halt all data collection immediately |
| `pause_monitoring` | Temporarily suspend collection (e.g., for a lunch break) |
| `resume_monitoring` | Resume after a pause |
| `refresh_policy` | Force the agent to immediately re-fetch its monitoring policy |

Commands are stored in `agent_commands` with a status lifecycle: `pending → delivered → completed / failed`. If not delivered within 5 minutes, they expire automatically.

### Privacy & Consent Framework

OneVo treats monitoring data with strict GDPR compliance built in:

1. **Consent first:** Monitoring cannot be enabled for any employee until a GDPR consent policy is configured and the employee has provided consent. Consent is recorded in `gdpr_consent_records`.
2. **Transparent to employees:** Employees can see their monitoring status via the tray app at any time.
3. **Configurable granularity:** Tenants can selectively enable features (screenshots on, browser tracking off).
4. **Department overrides:** Entire departments can be excluded from specific monitoring features (e.g., Legal team: no screenshots).
5. **Employee overrides:** Individual employees can have custom exceptions.
6. **Data retention limits:** Screenshots purged after 30 days (default, configurable). Activity data after 90 days. Raw buffer after 7 days.
7. **Right to erasure:** Compliance export and deletion flows managed via Shared Platform legal holds and retention policies.

### Agent Updates & Version Management

Agent version management is handled entirely through the Developer Platform. See Section 6.3 for full details.

---

## 6. Developer Platform — Internal Operator Console

### What It Is

`console.onevo.io` is a **completely separate application** from the customer-facing `app.onevo.io`. It is OneVo's internal operator console — the "back of house" control plane used exclusively by OneVo's own engineering and operations team.

Customers, HR managers, employees — nobody external ever sees or interacts with it.

### Why It's Separate

| Reason | Detail |
|:-------|:-------|
| Different auth model | Operator Google SSO vs. tenant JWT — must not share session infrastructure |
| Network isolation | Console is VPN-gated at the infrastructure level — not reachable from the public internet |
| No accidental exposure | A permission bug in the customer app cannot expose admin controls |
| Independent deployment | Console can be versioned, deployed, and rolled back independently of the main product |

### Architecture

```
VPN / IP Allowlist Gate
        │
        ▼
console.onevo.io (separate Next.js app)
        │  HTTPS + Platform-Admin JWT
        ▼
OneVo Backend — /admin/v1/* namespace
(same backend, separate controller namespace, separate JWT issuer)
        │  DI / module interfaces (read/write existing data)
        ▼
Existing OneVo Modules (SharedPlatform · Configuration · Auth · AgentGateway · etc.)
```

**Key principle:** There is no new database, no new microservice. The Developer Platform is a separate frontend + a separate API namespace inside the existing backend. All data lives in the same existing tables — the admin API layer is purely an access control boundary that allows privileged operations the customer API does not expose.

**JWT Isolation:** Two completely independent JWT issuers exist:
- `onevo-tenant` issuer — accepted only at `/api/v1/*` endpoints
- `onevo-platform-admin` issuer — accepted only at `/admin/v1/*` endpoints

A valid tenant JWT is rejected at admin endpoints. A valid admin JWT is rejected at tenant endpoints. Cross-use is impossible.

**Developer Platform Accounts**
Operators log in with their `@onevo.io` Google account. Their account is stored in `dev_platform_accounts` — a table with no `tenant_id` column (it's a platform-level identity, not a tenant user). Three roles: `super_admin`, `admin`, `viewer`.

### Developer Platform Modules

#### 6.1 Tenant Console

The primary operational tool for managing the OneVo tenant estate.

**Capabilities:**
- **Tenant list:** View all tenants with status, plan, employee count, last activity, agent count
- **Provisioning wizard:** Step-by-step wizard to create a new tenant:
  1. Create tenant record + generate tenant key
  2. Assign subscription plan (which modules are unlocked)
  3. Seed default roles and permissions
  4. Provision desktop agent installer key
  5. Send welcome email to tenant admin
- **Tenant detail:** Drill into any tenant — view settings, active feature flags, billing status, registered agents, recent audit log entries
- **Lifecycle actions:** Suspend a tenant (disable all logins), reactivate a suspended tenant, initiate tenant offboarding (data export + deletion schedule)
- **Impersonation:** Engineering team can generate a time-limited impersonation token that lets them log into the tenant's frontend as a read-only observer — for debugging support tickets. Every impersonation session is audit-logged.

#### 6.2 Feature Flag Manager

Controls which features are enabled across the platform, at global and per-tenant granularity.

**Capabilities:**
- **Global flags:** Toggle a feature on or off for all tenants simultaneously (used for platform-wide releases and rollbacks)
- **Per-tenant overrides:** Give a specific tenant early access to a feature (beta program) or disable a feature for a tenant that hasn't subscribed
- **Module enable/disable:** Turn off entire modules (e.g., disable the Exception Engine for a tenant on the HR-only tier)
- **Audit:** Every flag change is logged with who made the change and when

#### 6.3 Desktop Agent Version Manager

Controls the rollout of desktop agent updates across all tenants.

**Version Catalog**
Every desktop agent release is recorded with:
- Version number (e.g., 1.2.4)
- Release notes
- Minimum OS version requirement
- Status: `stable` / `beta` / `deprecated` / `recalled`

**Deployment Rings**

Releases roll out in three rings:

| Ring | Audience | Purpose |
|:-----|:---------|:--------|
| Ring 0 | OneVo's own internal test tenants | First exposure — catch critical bugs before external release |
| Ring 1 | Opted-in beta customer tenants | Validate across diverse environments and real workloads |
| Ring 2 | All tenants (General Availability) | Full production rollout |

**Ring Promotion Gate**
Before promoting a version from Ring 0 to Ring 1, or Ring 1 to Ring 2, the operator must manually confirm:
- Ring 0 → Ring 1: version ran for at least 24 hours in Ring 0 with no crash reports or forced rollbacks
- Ring 1 → Ring 2: at least 10 beta tenants confirmed agent compatibility

**Force-Update**
If a version is recalled (critical defect or security vulnerability), the operator can push a `force_update` command via Agent Gateway to all agents in a specified ring. Agents receive the command on their next heartbeat and begin updating immediately.

**Rollback**
An operator can pin a specific tenant to a previous stable version, preventing that tenant's agents from auto-updating past the pinned version. Used when a tenant reports a compatibility issue with a new release.

**Tables (3 new):** `agent_version_releases`, `agent_deployment_rings`, `agent_deployment_ring_assignments`

#### 6.4 Audit Console

A cross-tenant read-only audit log viewer for compliance and incident investigations.

**Capabilities:**
- Search audit logs across all tenants (operators can see everything; customers only see their own)
- Filter by: tenant, user, action type (create/update/delete/login/export), date range, IP address, resource type
- View full detail of each audit event: before/after values, request context
- Used when a customer reports "someone deleted our leave records" or "who changed this setting?"

#### 6.5 System Config

Manages global platform configuration defaults and per-tenant overrides that aren't exposed in the customer UI.

**Capabilities:**
- Edit global defaults: session TTL, rate limit thresholds, data retention defaults, max file upload size, heartbeat timeout
- Push per-tenant config overrides: set a specific value for a specific tenant (e.g., increase rate limit for a large enterprise tenant)

#### 6.6 App Catalog Manager

Manages the platform-wide known application catalog — the master list of applications that can appear in activity monitoring data.

**Capabilities:**
- Browse all known applications across the platform (discovered by agents in the field)
- Set `is_public` — whether the app appears in tenant admin's application category lists
- Assign global productivity classification (suggestion to tenants — they can override)
- Bulk-approve uncatalogued apps surfaced from agent data
- Add new applications manually

#### Phase 2 — Platform API Keys (Not in Phase 1)

Customer-facing developer API infrastructure: customers will be able to create API keys for programmatic access to their OneVo data, configure webhooks, and build integrations. This is a separate initiative scoped for Phase 2.

### Developer Platform Database (Phase 1 — 5 tables)

| Table | Purpose |
|:------|:--------|
| `dev_platform_accounts` | Operator identities (Google SSO, `@onevo.io` only, no tenant_id) |
| `dev_platform_sessions` | Operator session tokens |
| `agent_version_releases` | Desktop agent version catalog |
| `agent_deployment_rings` | Ring 0/1/2 definitions |
| `agent_deployment_ring_assignments` | Which tenants are in which ring |

---

## 7. Phase 2 Modules (Defined, Not Built in Phase 1)

These modules are fully designed and their schemas are incorporated into the Phase 1 database structure (so Phase 1 tables can correctly reference Phase 2 foreign keys). They will be built in a subsequent phase.

### 7.1 Payroll (11 tables)

Full payroll processing with external provider integration.
- Payroll provider integration (e.g., Xero, ADP, BambooHR payroll)
- Tax configuration per country
- Allowance types and employee allowances
- Pension schemes and employee enrollments
- Payroll run execution: pull attendance + leave + expense data → calculate gross + deductions → generate payslips
- Payroll adjustments (post-run corrections)
- Full audit trail per payroll run
- Employee payslip view (PDF download)

### 7.2 Performance (7 tables)

Structured performance management.
- Review cycles: admin creates cycles (annual, mid-year, quarterly)
- Self-assessment: employee rates themselves against goals and competencies
- Manager review: manager rates the employee
- Peer feedback: 360-degree feedback from nominated peers
- Goal setting and OKR tracking: set objectives, define key results, track check-ins
- Performance Improvement Plans (PIPs): formal improvement plans with milestones and review dates
- Recognition: peer-to-peer and manager-to-employee recognition with categories
- Succession planning: identify successors for key positions

### 7.3 Skills & Learning — Full (10 additional tables)

Extends the Phase 1 Skills Core with learning delivery:
- Courses: internal content or LMS integration (link to external LMS providers)
- Course enrollments: assign employees to courses, track completion
- Skill assessments: structured questionnaire-based skill evaluation
- Development plans: structured learning paths linking skills gaps to courses
- Employee certifications: upload and track professional certification expiry
- LMS provider integration

### 7.4 Documents (6 tables)

Company document management:
- Upload and organise company documents (policies, handbooks, contracts) into categories
- Employee-specific documents (offer letters, performance reviews, disciplinary notices)
- Document templates: generate employee documents from templates (mail merge)
- Version history: every document edit creates a new version with rollback capability
- Acknowledgement tracking: send policy documents to employees and track who has read and acknowledged
- Access control: document-level permissions, legal hold integration

### 7.5 Grievance (2 tables)

Employee complaint and disciplinary management:
- Grievance filing: employee submits a formal grievance (against a colleague, manager, or policy)
- Investigation workflow: HR assigns an investigator, evidence collection, investigation notes
- Outcome recording: resolution, outcome, any actions taken
- Disciplinary actions: formal disciplinary notices, warnings, and records issued by HR/managers

### 7.6 Expense (3 tables)

Employee expense claim management:
- Expense categories: admin defines categories (Travel, Meals, Equipment, etc.) with spending limits
- Claim submission: employee submits receipts with amount, category, and description
- Approval workflow: manager reviews and approves/rejects
- Payroll integration: approved expenses paid in next payroll run

### 7.7 Reporting Engine (3 tables)

Custom report builder:
- Report builder UI: create custom reports by selecting data fields, filters, and groupings
- Report templates: save and share report configurations
- Scheduled reports: automate report generation and delivery to specified recipients at set intervals
- Export formats: CSV, Excel, PDF

---

## 8. Cross-Module Scenarios

These are the key end-to-end chains — a single business event that triggers a cascade of actions across multiple modules. Understanding these shows how tightly integrated OneVo's modules are.

### 8.1 Employee Full Onboarding

```
HR creates employee profile (Core HR)
    â†“
System creates user account + sends invitation email (Auth)
    â†“
Employee assigned to role with permissions (Auth)
    â†“
Leave entitlements assigned per policy and job level (Leave)
    â†“
Shift assigned per department (Workforce Presence)
    â†“
Onboarding task list created from department template (Core HR)
    â†“
Desktop agent installer downloaded and deployed (Agent Gateway)
    â†“
GDPR consent collected from employee (Auth)
    â†“
Monitoring policy activated for employee (Activity Monitoring)
    â†“
Welcome notification sent (Notifications)
```

### 8.2 Employee Full Offboarding

```
HR initiates offboarding workflow (Core HR)
    â†“
Offboarding checklist created: equipment return, exit interview, final pay (Core HR)
    â†“
On completion: auth sessions revoked (Auth)
    â†“
Desktop agent unregistered / deactivated (Agent Gateway)
    â†“
Leave balances closed — unused balance calculated for payout (Leave)
    â†“
Final payroll calculation triggered (Payroll — Phase 2)
    â†“
Employee status set to terminated (Core HR)
    â†“
Data retention schedule set per tenant policy (Shared Platform)
    â†“
Lifecycle event recorded (Core HR)
```

### 8.3 Leave Request & Approval Chain

```
Employee submits leave request (Leave)
    â†“
System checks: leave balance available? (Leave)
    System checks: calendar conflicts? (Calendar)
    System checks: team coverage? (Workforce Presence — other employees on same shift)
    â†“
Approver notified via in-app + email (Notifications)
    â†“
Approver reviews and approves (Leave)
    â†“
Calendar event created for the leave period (Calendar)
    â†“
Attendance system notified: employee will be absent (Workforce Presence)
    â†“
Payroll system notified: deduct from next pay run if unpaid leave (Payroll — Phase 2)
    â†“
Employee notified of approval (Notifications)
```

### 8.4 Monthly Payroll Run

```
Payroll officer initiates monthly payroll run (Payroll — Phase 2)
    â†“
System pulls: all attendance records for the month (Workforce Presence)
    System pulls: all approved leave with type and pay rules (Leave)
    System pulls: approved expense claims for the month (Expense — Phase 2)
    System pulls: approved overtime records (Workforce Presence)
    â†“
Calculation engine computes: gross pay + allowances + overtime - deductions (Payroll)
    â†“
Payroll officer reviews and approves run (Payroll)
    â†“
Payslips generated per employee and stored (Documents — Phase 2)
    â†“
Employees notified: payslip available (Notifications)
```

### 8.5 Monitoring Alert Escalation Chain

```
Desktop agent detects: employee idle for 50 minutes (Activity Monitoring)
    â†“
Exception Engine evaluates rule: "idle > 45 min = Medium severity alert" (Exception Engine)
    â†“
Alert created: sent to manager's exception dashboard (Exception Engine)
    â†“
Manager notified via in-app + email (Notifications)
    â†“
Alert not acknowledged after 30 minutes → escalate
    â†“
HR Manager notified (Exception Engine — escalation chain Level 2)
    â†“
HR Manager acknowledges: "Employee confirmed in unscheduled off-site meeting" (Exception Engine)
    â†“
Alert resolved + note recorded (Exception Engine)
```

### 8.6 Employee Transfer Chain

```
HR initiates transfer: employee moves from Engineering (London) to Sales (Kuala Lumpur) (Core HR)
    â†“
Org structure updated: new department, new manager, new office location (Org Structure)
    â†“
Workforce Presence: shift reassigned to KL shift schedule (Workforce Presence)
    â†“
Leave policy updated: Malaysian leave entitlements applied (Leave)
    â†“
Monitoring: office location updated for identity verification GPS matching (Configuration)
    â†“
Auth: role permissions updated if job title change requires different access (Auth)
    â†“
Payroll: new legal entity and cost center applied for next pay run (Payroll — Phase 2)
    â†“
Lifecycle event recorded: transfer (Core HR)
    â†“
Employee notified (Notifications)
```

---

## 9. User Flows at a Glance

OneVo has 93+ documented end-to-end user flows. Here is the complete index by module area:

### Platform Setup
Download installer · billing/subscription management · SSO provider setup (Google, Azure AD) · feature flag management · tenant branding

### Auth & Access
User invitation · role creation · permission assignment · login (email + MFA) · MFA setup · password reset · GDPR consent collection

### Org Structure
Legal entity setup · department hierarchy · job family and levels · team creation · cost center setup

### People (Core HR)
Employee onboarding · profile management · compensation setup · employee transfer · employee promotion · employee offboarding · dependent management · qualification tracking

### Leave
Leave type configuration · leave policy setup · leave entitlement assignment · leave request submission · leave approval · leave cancellation · leave balance view

### Workforce Presence
Shift schedule setup · live presence overview · employee activity detail · presence session view · attendance correction · overtime management · break tracking · biometric device setup

### Performance (Phase 2)
Review cycle setup · self-assessment · manager review · peer feedback · goal setting · improvement plans · recognition submission · succession planning

### Payroll (Phase 2)
Payroll provider setup · tax configuration · allowance setup · pension configuration · payroll run execution · payroll adjustment · payslip view

### Skills & Learning
Skill taxonomy setup · employee skill declaration · skill assessment · course enrollment · certification tracking · development plan

### Documents (Phase 2)
Document upload · document access · document acknowledgement · template management · document versioning

### Workforce Intelligence
Monitoring configuration · live dashboard · activity snapshot view · identity verification setup · identity verification review · agent deployment

### Exception Engine
Exception rule setup · alert review · escalation chain setup · exception alerts overview

### Analytics & Reporting
Productivity dashboard · workforce snapshot · report creation · scheduled report setup · data export

### Grievance (Phase 2)
Grievance filing · grievance investigation · disciplinary action

### Expense (Phase 2)
Expense claim submission · expense approval · expense category setup

### Calendar
Calendar event creation · conflict detection

### Notifications
Notification preference setup · notification inbox view

### Work Management (WMS Integration)
Project management · task management · sprint planning · goals and OKRs · time tracking · resource management · chat

### Cross-Module Chains
Employee full onboarding · employee full offboarding · leave request & approval chain · monthly payroll run · attendance dispute chain · performance review cycle chain · employee transfer chain

---

## 10. Technical Highlights

### Security Architecture

**Token-Based, Stateless Auth**
JWTs with short TTLs. Refresh tokens stored server-side (revocable). Sessions tracked in database. All tokens are tenant-scoped — a token from Tenant A cannot access Tenant B.

**Two Completely Separate JWT Issuers**
Customer traffic uses `onevo-tenant` issuer. Operator console traffic uses `onevo-platform-admin` issuer. These are enforced at the policy validation level — there is no code path that accepts both.

**Row-Level Security**
PostgreSQL RLS policies are applied at the database level. Even if application code had a bug that forgot to filter by `tenant_id`, the database would reject the query. This is a defence-in-depth measure.

**RBAC with 90+ Permissions**
No hard-coded roles. Every permission is a named capability (`leave:approve`, `monitoring:configure`, `payroll:run`). Roles are just named collections of permissions. Employees can have permissions beyond their role, or have role permissions revoked — without needing a new role.

**PII Protection**
Sensitive fields (national ID, bank account numbers, biometric reference data) are encrypted at the application layer before storage. Serilog is configured to scrub PII fields from logs. No PII is ever written to application logs.

### Real-Time Infrastructure

**SignalR for Live Updates**
The Presence Live Dashboard, Alert Dashboard, and Agent Health Dashboard all update in real time via SignalR. When an agent goes offline, the manager's dashboard updates within 60 seconds (the heartbeat interval). No polling.

**In-Process Domain Events**
Features publish MediatR domain events for side effects inside the single .NET application. Phase 1 does not use RabbitMQ, MassTransit, or a transactional outbox.

**Idempotent Side Effects**
Handlers should be safe to retry and should record durable state changes in the same ApplicationDbContext transaction where needed.

### Data Architecture

**Single ApplicationDbContext**
All 175 tables belong to one EF Core DbContext. This enables LINQ queries across modules (for reporting and analytics) while still enforcing module boundary rules in application code — no module can call another module's repository directly.

**Clean Architecture per Feature**
Each feature folder is independently testable. Domain logic has zero dependencies on infrastructure. Use cases in the Application layer are independent of which database or API framework is used. This makes the codebase maintainable as it grows.

**PostgreSQL 16 Features Used**
- Row-Level Security (multi-tenancy)
- JSONB columns (agent policies, command payloads, exception rule conditions)
- Partial indexes (e.g., `WHERE is_active = true` for agent sessions — enforces one active session per device at the DB level)
- `timestamptz` everywhere — all timestamps are timezone-aware

### Operational Simplicity

**One Deployable**
Despite 23 modules, the entire backend is one .NET 9 process and one PostgreSQL database. No service mesh, no distributed transactions, no inter-service network calls. Operationally, it behaves like a simple monolith while architecturally enforcing module boundaries.

**Independent Developer Console Deployment**
The operator console (`console.onevo.io`) can be deployed, rolled back, or taken offline without any impact on customer traffic. The `/admin/v1/*` API namespace can be toggled off at the backend level for maintenance without affecting any customer endpoints.

---

## 11. Delivery Timeline

| Week | Focus | Modules Delivered |
|:-----|:------|:-----------------|
| Week 1 (Apr 7–11) | Foundation | Infrastructure, Auth, Org Structure, Shared Platform, Agent Gateway |
| Week 2 (Apr 14–18) | Core HR + Presence | Core HR, Skills Core, Workforce Presence, Identity Verification |
| Week 3 (Apr 21–25) | Intelligence + Leave | Leave, Activity Monitoring, Discrepancy Engine, Exception Engine, Calendar, Notifications |
| Week 4 (Apr 28–May 2) | Analytics + Platform | Productivity Analytics, Configuration, Developer Platform, WMS bridges, Reporting Engine |

---

## 12. Database Scale Summary

| Category | Count |
|:---------|:------|
| Phase 1 modules | 17 |
| Phase 1 tables | 133 |
| Phase 2 modules | 7 |
| Phase 2 tables | 42 |
| Developer Platform tables | 5 (Phase 1) + 1 (Phase 2) |
| **Total tables** | **175 + 6 = 181** |
| Most-referenced table | `tenants` — referenced by 102 other tables |
| Second most-referenced | `employees` — referenced by 71 other tables |
| Largest module by table count | Shared Platform — 33 tables |
| Most complex module | Agent Gateway — 4 data tables + messaging infrastructure (outbox + idempotency) |

### Full Table Count by Module

| Module | Phase | Tables |
|:-------|:------|:-------|
| Infrastructure | 1 | 4 |
| Auth & Security | 1 | 9 |
| Org Structure | 1 | 9 |
| Core HR | 1 | 13 |
| Skills Core | 1 | 5 |
| Leave | 1 | 5 |
| Calendar | 1 | 1 |
| Configuration | 1 | 6 |
| Agent Gateway | 1 | 4 (+messaging) |
| Activity Monitoring | 1 | 9 |
| Discrepancy Engine | 1 | 2 |
| Workforce Presence | 1 | 12 |
| Exception Engine | 1 | 5 |
| Identity Verification | 1 | 6 |
| Productivity Analytics | 1 | 5 |
| Shared Platform | 1 | 33 |
| Notifications | 1 | 0 (uses Shared Platform) |
| **Phase 1 Subtotal** | | **133** |
| Payroll | 2 | 11 |
| Performance | 2 | 7 |
| Skills & Learning (full) | 2 | 10 |
| Documents | 2 | 6 |
| Grievance | 2 | 2 |
| Expense | 2 | 3 |
| Reporting Engine | 2 | 3 |
| **Phase 2 Subtotal** | | **42** |
| Developer Platform | 1+2 | 5 + 1 |
| **Grand Total** | | **181** |

---

*Document prepared from OneVo system knowledge base — April 2026*
