# Layout Patterns

## Dashboard Layout

Shell background (light): `#EDEEF2` | (dark): `#0A0A0D`
Shell padding: `8px` all sides. Gap between topbar and bottom row: `6px`. Gap inside bottom row: `6px`.

```
 +---------------------------------------------------------+  <- outer shell (#EDEEF2 / #0A0A0D), padding 8px
 | +-----------------------------------------------------+ |
 | | Topbar (solid) - entity, breadcrumb, search, actions| |  <- #FFFFFF / #17181F, rounded-[10px], h-10 (40px)
 | +-----------------------------------------------------+ |
 | +------+ +--------+ +-------------------------------+  |
 | |      | |        | |                               |  |
 | | Rail | | Panel  | |  Content area                 |  |
 | | 52px | | 210px  | |  (white, rounded-[10px],      |  |
 | | dark | | #FAF9F6| |   padding 24px, scrollable)   |  |
 | |r-[12]| | r-[12] | |                               |  |
 | +------+ +--------+ +-------------------------------+  |
 +---------------------------------------------------------+
```

## Sidebar Navigation

```text
ONEVO
+-- Home                    -> employee-style dashboard with permission-shaped content
+-- People                  -> Employees, Onboarding, Offboarding, Checklist Templates
+-- Time Off                -> My Time Off, Team Time Off, Types, Policies, Entitlements
+-- Time & Attendance       -> Attendance, Schedules, Clock-in Policy, Overtime Rules
+-- Work                    -> Projects, Work Items, Documents, Project Members, Worklogs
+-- Calendar                -> Events, holidays, schedules, Time Off, meetings, invitations, reminders, conflicts
+-- Inbox                   -> Approvals, requests, notifications, invitations, assignments, mentions
+-- Monitoring              -> Live status, alerts, device health
+-- Settings                -> General, Branding, Users, Roles & Permissions, Notifications, Billing, Devices, Audit Log
```

## Page Layout Patterns

### List Page (Employees, Time Off Requests, Alerts)

```
PageHeader (title + "Create" button)
FilterBar (search, status filter, department filter, date range)
DataTable (sortable columns, row actions, pagination)
```

### Detail Page (Employee Detail, Activity Detail)

Scrollable sections - no tabs. Deep-link to any section via anchor: `/people/employees/abc123#pay-benefits`

```
Identity Card (glass) - avatar, name, title, dept, status, hire date, reports to
Quick Facts Strip - tenure, Time Off balance, review score, salary band, next milestone
Alerts / Action Items - expiring visa, pending review, probation ending
Employment Details (expanded by default, collapsible)
Pay & Benefits (permission-gated - hidden if unauthorized)
Documents (collapsed by default)
Activity Timeline (collapsed by default)
```

### Dashboard Page (Home)

Action -> awareness -> analysis order:

```
Greeting Bar ("Good morning, Thiva" + quick actions)
Primary KPIs (larger glass cards - actionable: approvals, alerts, expiring docs)
Secondary KPIs (standard glass cards - reference: total employees, attendance, new hires)
Upcoming Events strip + Quick Links (pinned/most-visited pages)
Activity Feed (left) + Active Alerts (right) - flat surfaces
Charts & Graphs (attendance trend, dept headcount) - glass containers
```

## Responsive Breakpoints

Responsive behavior is a Phase 1 requirement. Every layout must adapt smoothly across mobile, tablet, laptop, and desktop viewports.

| Breakpoint | Width | Shell behavior | Page behavior |
|:-----------|:------|:---------------|:--------------|
| Mobile | `<640px` | Topbar with hamburger; rail and panel hidden; navigation opens as a full-height drawer | Single-column content, card/list views for dense data, sticky primary actions where useful |
| Tablet | `640-1023px` | Sidebar hidden by default; hamburger opens drawer; entity/search/actions compact | Content-first layout, filters collapse into sheet/drawer, two-column only for simple sections |
| Laptop | `1024-1279px` | Compact rail visible; expansion panel collapsed or flyout; topbar keeps key actions visible | Dense work surfaces allowed, but tables/forms must still avoid page overflow |
| Desktop | `>=1280px` | Full floating shell with rail, expansion panel, topbar, and content area | Full dashboard, table, chart, and detail layouts |

Rules:

- No page may rely on horizontal page scrolling for primary use.
- Tables must provide a mobile card/list representation or an intentionally constrained scroll region.
- Primary navigation, search, entity context, notifications, and profile access must remain reachable at every breakpoint.
- Page padding should scale with viewport size, typically `p-3 sm:p-4 lg:p-6`.

## Spacing Tokens

| Token | Value | Tailwind class |
|:------|:------|:---------------|
| Shell outer padding | 8px | p-2 |
| Shell gap (topbar <-> bottom row, inner rail/panel/content) | 6px | gap-[6px] |
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

- [[frontend/design-system/components/component-catalog|Component Catalog]] - component library
- [[frontend/architecture/app-structure|App Structure]] - frontend architecture
- [[frontend/design-system/foundations/typography|Typography]] - type scale
- [[frontend/design-system/foundations/color-tokens|Color Tokens]] - color system
