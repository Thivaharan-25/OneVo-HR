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

| Component | Location | Usage | Phase |
|:----------|:---------|:------|:------|
| `DataTable` | `components/shared/data-table.tsx` | Sortable, filterable, paginated table | 1 |
| `PageHeader` | `components/shared/page-header.tsx` | Page title + breadcrumbs + actions | 1 |
| `StatCard` | `components/shared/stat-card.tsx` | KPI metric card (value, trend, sparkline) | 1 |
| `EmptyState` | `components/shared/empty-state.tsx` | No data / feature disabled states | 1 |
| `PermissionGate` | `components/shared/permission-gate.tsx` | RBAC wrapper | 1 |
| `StatusBadge` | `components/shared/status-badge.tsx` | Color-coded status (active, idle, offline) | 1 |
| `SeverityBadge` | `components/shared/severity-badge.tsx` | Alert severity (info, warning, critical) | 1 |
| `DateRangePicker` | `components/shared/date-range-picker.tsx` | Date range filter | 1 |
| `SearchInput` | `components/shared/search-input.tsx` | Debounced search with URL state | 1 |
| `TimelineBar` | `components/workforce/timeline-bar.tsx` | Full-day activity timeline (active/idle/break/meeting) | 1 |
| `ActivityHeatmap` | `components/workforce/activity-heatmap.tsx` | Hourly intensity heatmap | 1 |
| `AppUsageChart` | `components/workforce/app-usage-chart.tsx` | Application time breakdown | 1 |

### Glass Components

| Component | Props | Usage |
|:----------|:------|:------|
| `GlassCard` | `glow?: boolean` | Glass surface card. `glow` adds violet border glow for actionable items |
| `GlassSurface` | `variant?: 'default' \| 'light'` | Base glass surface wrapper |
| `IconRail` | `pillars: Pillar[]` | Left nav rail with pillar icons |
| `ExpansionPanel` | `pillar: Pillar, isPinned: boolean` | Slide-out sub-navigation panel |
| `InboxBadge` | — | Inbox count badge with violet glow pulse |

## Status Colors

| Status | Token | Usage |
|:-------|:------|:------|
| Active | `text-status-active` / `bg-status-active` | Online, approved, healthy |
| Warning | `text-status-warning` / `bg-status-warning` | Idle, pending, expiring |
| Critical | `text-status-critical` / `bg-status-critical` | Offline, rejected, critical |
| Info | `text-status-info` / `bg-status-info` | On leave, informational |

## Severity Colors

| Severity | Color | Tailwind Class |
|:---------|:------|:--------------|
| Info | Blue | `text-blue-600 bg-blue-50` |
| Warning | Yellow | `text-yellow-600 bg-yellow-50` |
| Critical | Red | `text-red-600 bg-red-50` |

## Related

- [[frontend/design-system/foundations/color-tokens|Color Tokens]] — color system
- [[frontend/design-system/foundations/typography|Typography]] — type scale
- [[frontend/design-system/patterns/layout-patterns|Layout Patterns]] — page layouts
- [[frontend/coding-standards|Frontend Coding Standards]] — component conventions
- [[frontend/design-system/patterns/data-visualization|Data Visualization]] — chart components
