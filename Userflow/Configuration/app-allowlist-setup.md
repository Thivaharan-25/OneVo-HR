# App Allowlist Setup

**Module:** Configuration
**Feature:** App Allowlist Setup

---

## Overview

HR admins configure which applications employees are permitted to use during work hours. The allowlist is built by selecting from two sources: the global app catalog (pre-seeded by OneVo with common apps) and apps discovered from the organisation's own agent data. No typing required — mismatch between agent-reported names and allowlist entries is prevented by using `process_name` (Windows exe name) as the matching key.

---

## Prerequisites

- `application_tracking` toggle enabled in [[Userflow/Configuration/monitoring-toggles|Monitoring Toggles]]
- Agent deployed to at least a pilot group of employees (20–30%)
- At least 5–7 days of agent data collected for meaningful discovery data

---

## Flow 1: Browse and Approve from App Catalog

**Entry:** Settings → Monitoring → App Allowlist → **Browse App Catalog** tab

```
HR Admin opens App Allowlist page
  → Clicks "Browse App Catalog" tab
  → Sees global catalog: app cards with icon, name, publisher, category
  → Filters by category (browser / communication / development / office / design / productivity)
  → Clicks an app card (e.g., "Microsoft Teams")
  → Drawer opens:
      - App name, publisher, category, icon
      - Toggle: Allow / Block
      - Scope dropdown: All Employees | Role | Specific Employee
  → Clicks "Add to Allowlist"
  → POST /api/v1/settings/monitoring/allowlist
  → App appears in Current Allowlist tab with Allow / Block badge
  → App card in catalog shows checkmark (already configured)
```

---

## Flow 2: Review Apps Discovered in Your Organisation

**Entry:** Settings → Monitoring → App Allowlist → **Discovered in Your Org** tab

```
HR Admin opens Discovered tab
  → Sees app cards from agent data, sorted by employee_count DESC
  → Each card shows:
      - App name + icon (from catalog if matched, else raw name)
      - "X employees · Y avg hours/day"
      - "First seen: [date]"
      - Category badge if matched to global catalog
  → Admin clicks a card
  → Drawer opens:
      - Usage summary (employee count, total hours observed)
      - Toggle: Allow / Block
      - Scope: All Employees | Role | Specific Employee
  → Clicks "Add to Allowlist"
      → Creates app_allowlists row, source = tenant_observed
      → observed_applications.status flips to added_to_allowlist
      → Card moves out of discovered list
  OR clicks "Dismiss"
      → status = dismissed, hidden from tab
      → Recoverable via "Show dismissed" toggle
```

---

## Flow 3: Unified Search

**Entry:** Settings → Monitoring → App Allowlist → search box (any tab)

```
HR Admin types in search box
  → GET /api/v1/settings/monitoring/allowlist/search?q=teams
  → Results merge catalog matches + discovered matches by process_name
  → Each result shows source badge: "From Catalog" | "Seen in Your Org" | both
  → Same app in both sources → ONE result card (catalog metadata + org usage data merged)
  → Admin selects result → same drawer flow as above
```

---

## Flow 4: Edit or Remove an Existing Entry

**Entry:** Settings → Monitoring → App Allowlist → **Current Allowlist** tab

```
HR Admin sees table of current entries (name, scope, allow/block status, added by, date)
  → Toggle Allow ↔ Block inline
  → Change scope (e.g., All Employees → specific Role)
  → Click delete icon → entry removed
      → App returns to "pending" in Discovered tab (if originally from agent data)
```

---

## Business Rules

| Rule | Detail |
|:-----|:-------|
| No duplicates | Same app cannot appear twice for the same scope — enforced by DB unique constraint on `(tenant_id, scope_type, scope_id, process_name)` |
| Null = pending, not a violation | Apps with `is_allowed = null` (not yet reviewed) never trigger exception alerts |
| Scope resolution | Employee override → Role override → Tenant default (most specific wins) |
| Allowlist mode | `blocklist` = only explicitly blocked apps are flagged (use during setup). `allowlist` = only approved apps are allowed. Configure in Monitoring Toggles. |
| Dismissed apps | Hidden from discovered tab but data is preserved — show with "Show dismissed" toggle |

---

## Recommended Setup Order (New Tenant)

```
1. Enable application_tracking in Monitoring Toggles
2. Set allowlist_mode = blocklist   ← prevents false alerts during discovery period
3. Deploy agent to pilot group (20–30% of employees)
4. Wait 5–7 days for observed_applications to populate
5. Open App Allowlist → Discovered tab → review and approve/block apps
6. Browse App Catalog → add standard apps not yet discovered
7. Switch allowlist_mode = allowlist
8. Create non_allowed_app exception rule in Exception Engine
9. Roll out agent to remaining employees
```

---

## Related

- [[Userflow/Configuration/monitoring-toggles|Monitoring Toggles]] — enable application_tracking + set allowlist_mode
- [[Userflow/Configuration/employee-override|Employee Monitoring Override]] — per-employee allowlist exceptions
- [[Userflow/Exception-Engine/exception-rule-setup|Exception Rule Setup]] — configure non_allowed_app rule
- [[modules/configuration/employee-overrides/overview|Configuration Module]]
- [[database/schemas/configuration|Configuration Schema]] — app_allowlists, observed_applications
- [[docs/superpowers/plans/2026-04-26-app-catalog-observed-applications|App Catalog Architecture Plan]]
