# Layout Patterns

## Dashboard Layout

```
┌──────────────────────────────────────────────────────────┐
│ Topbar (glass) — breadcrumbs, search, bell, avatar       │
├──────┬──────────┬────────────────────────────────────────┤
│      │          │                                        │
│ Rail │  Panel   │  Page Content                          │
│ 64px │  220px   │                                        │
│glass │  glass   │  (scrollable)                          │
│      │ (slides) │                                        │
└──────┴──────────┴────────────────────────────────────────┘
```

## Sidebar Navigation

```
ONEVO (logo mark)
├── 🏠 Home                    → Dashboard (direct nav)
├── 👥 People                  → Employees, Leave
├── 📡 Workforce               → Live Dashboard (tabs: Activity, Work Insights, Online Status)
├── 🏢 Organization            → Org Chart, Departments, Teams
├── 📅 Calendar                → Calendar (direct nav)
├── 📥 Inbox (badge)           → Approvals, tasks, mentions
├── 🔧 Admin                   → Users & Roles, Audit Log, Agents, Devices, Compliance
└── ⚙️ Settings                → General, Monitoring, Notifications, Integrations, Branding, Billing, Alert Rules
```

## Page Layout Patterns

### List Page (Employees, Leave Requests, Alerts)

```
PageHeader (title + "Create" button)
FilterBar (search, status filter, department filter, date range)
DataTable (sortable columns, row actions, pagination)
```

### Detail Page (Employee Detail, Activity Detail)

Scrollable sections — no tabs. Deep-link to any section via anchor: `/people/employees/abc123#pay-benefits`

```
Identity Card (glass) — avatar, name, title, dept, status, hire date, reports to
Quick Facts Strip — tenure, leave balance, review score, salary band, next milestone
Alerts / Action Items — expiring visa, pending review, probation ending
Employment Details (expanded by default, collapsible)
Pay & Benefits (permission-gated — hidden if unauthorized)
Documents (collapsed by default)
Activity Timeline (collapsed by default)
```

### Dashboard Page (Home)

Action → awareness → analysis order:

```
Greeting Bar ("Good morning, Thiva" + quick actions)
Primary KPIs (larger glass cards — actionable: approvals, alerts, expiring docs)
Secondary KPIs (standard glass cards — reference: total employees, attendance, new hires)
Upcoming Events strip + Quick Links (pinned/most-visited pages)
Activity Feed (left) + Active Alerts (right) — flat surfaces
Charts & Graphs (attendance trend, dept headcount) — glass containers
```

## Responsive Breakpoints

| Breakpoint | Width | Layout |
|:-----------|:------|:-------|
| Desktop | ≥1280px | Full sidebar + content |
| Small Desktop | ≥1024px | Collapsed sidebar + content |
| Tablet | ≥768px | Hidden sidebar (hamburger) + content |
| Mobile | <768px | Not optimized (Phase 2) |

## Spacing Tokens

| Token | Value | Tailwind class |
|:------|:------|:---------------|
| Sidebar rail width | 64px | w-16 |
| Sidebar panel width | 220px | w-[220px] |
| Topbar height | 56px | h-14 |
| Page horizontal padding | 32px | px-8 |
| Card gap | 16px | gap-4 |

## Related

- [[frontend/design-system/components/component-catalog|Component Catalog]] — component library
- [[frontend/architecture/app-structure|App Structure]] — frontend architecture
- [[frontend/design-system/foundations/typography|Typography]] — type scale
- [[frontend/design-system/foundations/color-tokens|Color Tokens]] — color system
