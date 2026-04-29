# Layout Patterns

## Dashboard Layout

Shell background (light): `#EDEEF2` | (dark): `#0A0A0D`
Shell padding: `8px` all sides. Gap between topbar and bottom row: `6px`. Gap inside bottom row: `6px`.

```
 ┌─────────────────────────────────────────────────────────┐  ← outer shell (#EDEEF2 / #0A0A0D), padding 8px
 │ ┌─────────────────────────────────────────────────────┐ │
 │ │ Topbar (solid) — entity, breadcrumb, search, actions│ │  ← #FFFFFF / #17181F, rounded-[10px], h-10 (40px)
 │ └─────────────────────────────────────────────────────┘ │
 │ ┌──────┐ ┌────────┐ ┌───────────────────────────────┐  │
 │ │      │ │        │ │                               │  │
 │ │ Rail │ │ Panel  │ │  Content area                 │  │
 │ │ 52px │ │ 210px  │ │  (white, rounded-[10px],      │  │
 │ │ dark │ │ #FAF9F6│ │   padding 24px, scrollable)   │  │
 │ │r-[12]│ │ r-[12] │ │                               │  │
 │ └──────┘ └────────┘ └───────────────────────────────┘  │
 └─────────────────────────────────────────────────────────┘
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
| Shell outer padding | 8px | p-2 |
| Shell gap (topbar ↔ bottom row, inner rail/panel/content) | 6px | gap-[6px] |
| Topbar height | 40px | h-10 |
| Topbar border-radius | 10px | rounded-[10px] |
| Sidebar rail width | 52px | w-[52px] |
| Sidebar rail border-radius | 12px | rounded-[12px] |
| Sidebar panel width | 210px | w-[210px] |
| Sidebar panel border-radius | 12px | rounded-[12px] |
| Content area border-radius | 10px | rounded-[10px] |
| Content area padding | 24px | p-6 |
| Card gap | 16px | gap-4 |

## Shell Surface Colors

| Surface | Light | Dark |
|:--------|:------|:-----|
| Outer shell (body bg) | `#EDEEF2` | `#0A0A0D` |
| Topbar | `#FFFFFF` | `#17181F` |
| Rail | `#17181F` (always dark) | `#17181F` |
| Panel | `#FAF9F6` | `#000000` |
| Content area | `#FFFFFF` | `#111118` |

## Related

- [[frontend/design-system/components/component-catalog|Component Catalog]] — component library
- [[frontend/architecture/app-structure|App Structure]] — frontend architecture
- [[frontend/design-system/foundations/typography|Typography]] — type scale
- [[frontend/design-system/foundations/color-tokens|Color Tokens]] — color system
