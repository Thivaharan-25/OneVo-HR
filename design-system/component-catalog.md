# Component Catalog

## Base Components (shadcn/ui)

| Component | Usage |
|:----------|:------|
| `Button` | Actions (primary, secondary, destructive, ghost, link) |
| `Input` / `Textarea` | Form inputs |
| `Select` | Dropdowns |
| `Dialog` | Modal dialogs (create/edit forms, confirmations) |
| `Sheet` | Slide-over panels (mobile nav, detail sidepanels) |
| `Tabs` | Content sections within a page |
| `Table` | Data tables (with sorting, pagination) |
| `Badge` | Status indicators, severity labels |
| `Card` | KPI cards, content containers |
| `Tooltip` | Extra information on hover |
| `Toast` | Notifications, success/error feedback |
| `Popover` | Dropdown menus, date pickers |
| `Calendar` | Date selection |
| `Skeleton` | Loading placeholders |
| `Avatar` | Employee photos |
| `Command` | Search/command palette |
| `DropdownMenu` | Action menus |
| `Switch` | Toggle controls (monitoring features) |

## Composed Components

| Component | Location | Usage |
|:----------|:---------|:------|
| `DataTable` | `components/shared/data-table.tsx` | Sortable, filterable, paginated table |
| `PageHeader` | `components/shared/page-header.tsx` | Page title + breadcrumbs + actions |
| `StatCard` | `components/shared/stat-card.tsx` | KPI metric card (value, trend, sparkline) |
| `EmptyState` | `components/shared/empty-state.tsx` | No data / feature disabled states |
| `PermissionGate` | `components/shared/permission-gate.tsx` | RBAC wrapper |
| `StatusBadge` | `components/shared/status-badge.tsx` | Color-coded status (active, idle, offline) |
| `SeverityBadge` | `components/shared/severity-badge.tsx` | Alert severity (info, warning, critical) |
| `DateRangePicker` | `components/shared/date-range-picker.tsx` | Date range filter |
| `SearchInput` | `components/shared/search-input.tsx` | Debounced search with URL state |
| `TimelineBar` | `components/workforce/timeline-bar.tsx` | Full-day activity timeline (active/idle/break/meeting) |
| `ActivityHeatmap` | `components/workforce/activity-heatmap.tsx` | Hourly intensity heatmap |
| `AppUsageChart` | `components/workforce/app-usage-chart.tsx` | Application time breakdown |

## Status Colors

| Status | Color | Tailwind Class |
|:-------|:------|:--------------|
| Active / Online | Green | `text-green-600 bg-green-50` |
| Idle | Yellow | `text-yellow-600 bg-yellow-50` |
| Offline / Absent | Red | `text-red-600 bg-red-50` |
| On Leave | Blue | `text-blue-600 bg-blue-50` |
| Partial | Orange | `text-orange-600 bg-orange-50` |

## Severity Colors

| Severity | Color | Tailwind Class |
|:---------|:------|:--------------|
| Info | Blue | `text-blue-600 bg-blue-50` |
| Warning | Yellow | `text-yellow-600 bg-yellow-50` |
| Critical | Red | `text-red-600 bg-red-50` |

## Related

- [[color-tokens]] — color system
- [[typography]] — type scale
- [[layout-patterns]] — page layouts
- [[frontend-coding-standards]] — component conventions
- [[data-visualization]] — chart components
