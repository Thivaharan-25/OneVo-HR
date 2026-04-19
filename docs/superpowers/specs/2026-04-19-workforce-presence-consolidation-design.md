# Workforce Presence — Consolidated UI Design

**Date:** 2026-04-19
**Branch:** feature/luminous-depth

---

## Summary

Consolidate the WorkforcePage tabs by removing Activity, Work Insights, Online Status, and Identity Verification as separate tabs. Fold status indicators into the Overview card grid. Move per-employee detail to a full-page drill-down. Add hierarchy-adaptive views, escalated exception card treatment, and an Allowed Apps section in Admin.

---

## Userflow Contradictions Resolved

| # | Old Userflow | New Behaviour | Fix |
|---|-------------|---------------|-----|
| 1 | "Online Status" dedicated tab | Status dot (online/break/offline) on each card in Overview grid | Remove Online Status tab; add status dot to card |
| 2 | "Identity Verification" dedicated tab | Shown in employee detail page (remote workers only) | Remove Identity Verification tab; add to detail page |
| 3 | App allowlist buried in Configuration module | Surfaced as "Allowed Apps" section inside Admin page | Add Monitoring Policy tab to Admin page |

---

## Section 1: WorkforcePage Tabs (After Consolidation)

Tabs retained:
- **Overview** (redesigned — see below)
- **Attendance Correction**
- **Overtime**
- **Shifts**

Tabs removed:
- Activity *(content moved to employee detail page)*
- Work Insights *(content moved to employee detail page)*
- Online Status *(status folded into Overview card)*
- Identity Verification *(content moved to employee detail page)*

---

## Section 2: Overview Tab

### Layout (top to bottom)

**1. Summary Bar**
Four stat pills: Online count | On Break count | Offline count | Active Exceptions count.

**2. Charts Row**
Two charts side by side, hierarchy-scoped:
- Bar chart: "Today's Productivity Scores" (employees / teams / departments depending on viewer role)
- Line chart: "7-Day Avg Trend"

**3. Hierarchy-Adaptive Card Grid**

| Viewer | Card represents | Drill behaviour |
|--------|----------------|-----------------|
| CTO / C-level | Department | Click → team cards for that dept |
| Department Head | Team | Click → employee cards for that team |
| Team Lead / Manager | Individual employee | Click → employee detail page |

CTO/C-level sees a tenant filter to switch between tenants.

Each card contains: avatar (or dept/team icon), name, department/team label, status dot, productivity score.

**4. Escalated Cards**

Escalated employee cards float to the top of the grid. Same card design, with:
- Red border
- Exception type badge (e.g. "Excessive Idle")

Escalated cards remain at top until the exception is resolved or dismissed by the manager.

---

## Section 3: Employee Detail Page (Full Page)

Reached by clicking an individual employee card. Back button returns to Overview.

### Header
- Employee avatar, full name, role, department
- Status dot (live)
- "ID Verified ✓" badge (remote workers only)

### Day Filter
Today | Yesterday | Last 7 Days | Last 30 Days | Custom range

### Scrollable Sections

**1. Activity Timeline**
App usage breakdown, active/idle time blocks, screenshots (if enabled by policy), meeting time.

**2. Work Insights**
Productivity score, active %, allowed app violation flags, weekly/monthly trend.

**3. Identity Verification** *(remote workers only)*
Clock-in photo, clock-out photo, verified/unverified status, on-demand capture history.

**4. Exceptions** *(only shown if employee has active exceptions)*
List of active exceptions for this employee, severity, escalation status.
"Request On-Camera Photo" button available here.

> Note: "Request On-Camera Photo" is also available in the **Inbox** screen (exception alert view).

---

## Section 4: Exception Escalation Flow

```
System detects excessive idle
  → Exception Engine fires "Exception: Excessive Idle"
  → Reporting manager / CEO sees alert in Inbox + Overview summary bar

Manager clicks "Request On-Camera Photo" (from Inbox or Employee Detail)
  → Agent Gateway dispatches command to desktop agent via SignalR
  → Desktop agent shows employee notification (GDPR mandatory, 3s delay)

Employee accepts
  → Camera window opens → photo captured → uploaded to blob storage
  → Manager notified: "Capture result available"
  → Viewable in employee detail → Identity Verification section

Employee ignores / declines
  → Exception escalates
  → Employee card moves to top of Overview grid
  → Card shows red border + "Excessive Idle" badge
  → Stays pinned until manager resolves or dismisses the exception
```

Rate limit: max 10 capture requests per agent per hour (existing system constraint).

---

## Section 5: Admin Page — Allowed Apps

New tab added to AdminPage: **Monitoring Policy**

### Allowed Apps section
- Mode selector: **Set per Role** / **Set per Employee**
- Set per Role: pick role → manage allowed/blocked app list
- Set per Employee: pick employee → override their role's app list
- Three-tier resolution: Tenant default → Role → Employee (most specific wins)

This surfaces the existing Configuration module's three-tier app allowlist (tenant → role → employee) in a discoverable location for admins.

---

## Section 6: Admin Sidebar Bug Fix

AdminPage at `/admin` is routing correctly but displaying wrong content in the demo. This is a demo implementation bug to investigate and fix as part of the implementation plan.

Current AdminPage tabs: Users & Roles | Audit Log | Agents | Devices | Compliance
New tab to add: Monitoring Policy

---

## Identity Verification — Remote Worker Rule

Identity verification (photo at clock-in/clock-out) applies **only to remote workers**. The "ID Verified" badge on the employee detail header and the Identity Verification section in the detail page are hidden for on-site employees.

On-demand capture (manager request) applies to any employee with a desktop agent, regardless of remote/on-site status.

---

## Out of Scope

- Backend changes to exception engine escalation logic (already exists in module docs)
- Changes to biometric device flows
- Employee self-service view changes
