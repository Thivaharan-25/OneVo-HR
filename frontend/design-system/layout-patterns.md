# Layout Patterns

## Dashboard Layout

```
┌──────────────────────────────────────────────────────┐
│ Topbar (search, notifications, user menu)            │
├──────────┬───────────────────────────────────────────┤
│          │ Breadcrumbs                                │
│          ├───────────────────────────────────────────┤
│ Sidebar  │                                           │
│          │  Page Content                             │
│ (collap- │                                           │
│  sible)  │  [StatCards row]                          │
│          │  [Main content area]                      │
│          │  [DataTable / Charts / etc]               │
│          │                                           │
│          │                                           │
├──────────┴───────────────────────────────────────────┤
│ (no footer)                                          │
└──────────────────────────────────────────────────────┘
```

## Sidebar Navigation

```
ONEVO
├── Overview
│
├── HR Management                # Permission: employees:read
│   ├── Employees
│   ├── Leave
│   ├── Performance
│   ├── Payroll                  # Permission: payroll:read
│   ├── Skills
│   ├── Documents
│   ├── Grievance                # Permission: grievance:read
│   └── Expense                  # Permission: expense:read
│
├── Workforce Intelligence       # Permission: workforce:view
│   ├── Live Dashboard
│   ├── Reports
│   ├── Exceptions               # Permission: exceptions:view
│   └── Verification             # Permission: verification:view
│
├── Organization
│   ├── Departments
│   ├── Teams
│   └── Job Families
│
└── Settings                     # Permission: settings:read
    ├── General
    ├── Monitoring               # Permission: monitoring:view-settings
    ├── Notifications
    ├── Integrations
    └── Billing                  # Permission: billing:read
```

## Page Layout Patterns

### List Page (Employees, Leave Requests, Alerts)

```
PageHeader (title + "Create" button)
FilterBar (search, status filter, department filter, date range)
DataTable (sortable columns, row actions, pagination)
```

### Detail Page (Employee Detail, Activity Detail)

```
PageHeader (title + back button + actions)
TabGroup
  Tab 1: Overview (stat cards + summary)
  Tab 2: Details (specific data)
  Tab 3: History (timeline / audit log)
```

### Dashboard Page (Overview, Live Workforce)

```
StatCards row (4-6 KPI cards)
Main chart/visualization (full width)
Split section (2 columns: chart + list)
DataTable (if applicable)
```

## Responsive Breakpoints

| Breakpoint | Width | Layout |
|:-----------|:------|:-------|
| Desktop | ≥1280px | Full sidebar + content |
| Small Desktop | ≥1024px | Collapsed sidebar + content |
| Tablet | ≥768px | Hidden sidebar (hamburger) + content |
| Mobile | <768px | Not optimized (Phase 2) |

## Related

- [[component-catalog]] — component library
- [[structure]] — frontend architecture
- [[typography]] — type scale
- [[color-tokens]] — color system
