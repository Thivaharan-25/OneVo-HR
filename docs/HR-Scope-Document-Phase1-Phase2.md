# ONEVO-HR Platform - Project Scope Document

**Document Version:** 1.0
**Date:** April 8, 2026
**Prepared by:** ONEVO Product Team
**Classification:** Client Confidential

---

## 1. Platform Overview

ONEVO is a production-grade, multi-tenant platform that unifies **HR Management** and **Workforce Intelligence** into a single ecosystem. Designed for SMBs and mid-market companies, ONEVO provides seamless employee lifecycle management alongside automated, unbiased visibility into workforce productivity.

### Product Configurations

| Configuration | What You Get |
|:---|:---|
| **HR Management** | Complete HR suite for employee lifecycle, leave, org structure |
| **HR + Workforce Intelligence** | HR suite + desktop monitoring, activity tracking, exception alerts |
| **HR + Work Management** | HR suite + integration with WorkManage Pro (project/task management) |
| **Full Suite** | All capabilities including monitoring, task management, and analytics |

Each configuration shares the same secure, multi-tenant foundation. Features activate based on subscription -- no separate deployments required.

---

## 2. Phase 1 Scope

Phase 1 delivers the core platform foundation and the modules required to run day-to-day HR operations alongside real-time workforce monitoring.

### 2.1 Core HR & Employee Management

- **Employee Onboarding & Offboarding** -- guided workflows from hire to exit with document collection and task checklists
- **Profile Management** -- centralised employee records including personal details, employment history, compensation, and dependents
- **Promotions & Transfers** -- structured workflows with approval chains and automatic record updates
- **Compensation Setup** -- salary structures, allowances, and compensation history tracking
- **Qualification Tracking** -- employee certifications, education, and professional qualifications

### 2.2 Organisation Structure

- **Department Hierarchy** -- unlimited nesting of departments and sub-departments
- **Legal Entity Management** -- multiple registered business entities within one account
- **Job Families & Levels** -- career ladder structures with job titles, families, and seniority levels
- **Team Management** -- cross-functional team creation and membership
- **Cost Centres** -- financial grouping for budgeting and reporting

### 2.3 Leave Management

- **Leave Types & Policies** -- configurable leave types (annual, sick, maternity, etc.) with country-specific and job-level-specific rules
- **Entitlement Assignment** -- automatic or manual allocation of leave balances
- **Request & Approval Workflow** -- employee self-service requests with manager approval chains
- **Leave Cancellation** -- cancel or modify approved leave with audit trail
- **Balance Visibility** -- real-time leave balance dashboard for employees and managers

### 2.4 Workforce Intelligence

- **Activity Monitoring** -- real-time tracking of application usage, keyboard/mouse activity, and active/idle time via a lightweight desktop agent
- **Workforce Presence** -- unified daily attendance records combining biometric terminals and desktop agent data, with automatic break detection
- **Identity Verification** -- periodic photo-based verification to confirm employee identity at the workstation
- **Exception Engine** -- automated anomaly detection (excessive idle time, low activity, policy violations) with configurable rules, real-time alerts, and escalation chains
- **Productivity Analytics** -- daily and weekly productivity summaries with trend analysis and team comparisons

### 2.5 Desktop Agent (Windows)

- Lightweight Windows service with system tray application
- Policy-driven -- only monitors what the company has enabled (no hidden tracking)
- Offline buffering with automatic sync when connectivity is restored
- Configurable per tenant and per employee (e.g., disable screenshot capture for specific roles)
- Three transparency modes: **Full** (employees see all their data), **Partial** (employees see summaries), **Covert** (employer only)

### 2.6 Shared Foundation

- **Authentication & Access Control** -- JWT-based auth, MFA, SSO support, hybrid permission model with role-based templates and granular per-employee overrides
- **Notifications** -- in-app, email (via Resend), and webhook notifications across 40+ events
- **Workflow Engine** -- configurable approval workflows for leave, promotions, transfers, and more
- **Tenant Configuration** -- company-level settings, industry profiles, branding, and monitoring toggles
- **Calendar** -- shared company calendar with event creation and conflict detection
- **Billing & Subscriptions** -- Stripe-powered subscription management and feature gating
- **GDPR & Compliance** -- consent management, data retention policies, and audit logging
- **User Management** -- invitations, role creation, permission assignment, and password reset flows

---

## 3. Phase 2 Scope

Phase 2 extends the platform with advanced HR modules and deeper integrations. All Phase 2 modules build on top of the Phase 1 foundation.

### 3.1 Payroll

- Salary computation with allowances, deductions, tax, and pension calculations
- Payroll run execution with line-item breakdown and approval workflow
- Payslip generation and employee self-service viewing
- Provider integration for external payroll processing (e.g., local payroll providers)
- Payroll adjustments and correction workflows

### 3.2 Performance Management

- Configurable review cycles (quarterly, bi-annual, annual)
- Self-assessment, manager review, and 360-degree peer feedback
- Goal setting and tracking with alignment to company objectives
- Performance improvement plans with milestone tracking
- Succession planning and talent pipeline identification
- Employee recognition and kudos system

### 3.3 Skills & Learning

- Organisational skill catalogue with proficiency levels
- Employee skill assessments and gap analysis
- Certification tracking with expiry alerts
- Course assignment and learning path management
- Integration with external LMS providers

### 3.4 Document Management

- Centralised document repository with folder structures and access controls
- Document upload, versioning, and version history
- Template management for offer letters, contracts, and policy documents
- Document acknowledgement tracking (e.g., policy sign-offs)
- Role-based document access with audit trail

### 3.5 Grievance & Disciplinary

- Employee grievance filing with confidential handling
- Investigation workflows with evidence collection and notes
- Disciplinary action tracking with outcome recording
- Escalation paths and resolution timelines

### 3.6 Expense Management

- Expense category configuration by department or company
- Employee expense claim submission with receipt upload
- Multi-level approval workflows
- Integration with payroll for reimbursement processing

### 3.7 Reporting Engine

- Custom report builder with drag-and-drop field selection
- Scheduled reports with email delivery
- Data export (CSV, PDF) across all modules
- Workforce snapshot and productivity dashboards
- Pre-built report templates for common HR metrics

### 3.8 Extended Integrations

- **Google Calendar** -- two-way sync for leave events and company calendar
- **Slack** -- notifications and approval actions directly in Slack
- **Microsoft Teams** -- rich meeting analytics via Graph API
- **Advanced Search** -- upgraded full-text search powered by Meilisearch

---

## 4. What Is Not In Scope

The following items are explicitly excluded from Phase 1 and Phase 2:

- **AI Chatbot (Nexis)** -- planned for a future phase
- **Mobile Application** -- native iOS/Android app planned for a future phase
- **WorkManage Pro Development** -- built by a separate team; ONEVO provides integration bridges only
- **Multi-Region Deployment** -- single-region infrastructure for Phase 1 and Phase 2
- **ADP / Oracle Payroll Sync** -- deep payroll provider integrations planned for Phase 4

---

## 5. Technical Highlights

| Area | Approach |
|:---|:---|
| **Architecture** | Modular monolith (.NET 9) -- clean module boundaries, single deployment |
| **Frontend** | Next.js 14 -- responsive, desktop-first web application |
| **Database** | PostgreSQL 16 with row-level security for tenant isolation |
| **Real-time** | SignalR for live dashboards and alerts |
| **Security** | Multi-tenant isolation at every layer, encrypted data at rest and in transit, GDPR-compliant data handling |
| **Scale** | Designed for 170 database tables (128 Phase 1, 42 Phase 2), 22 modules, 90+ permissions |

---

*This document defines the agreed scope for ONEVO-HR Phase 1 and Phase 2. Any features or modules not listed above are considered out of scope and will be addressed in subsequent phases.*
