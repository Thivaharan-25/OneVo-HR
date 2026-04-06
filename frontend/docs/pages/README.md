# Frontend Page Specifications

Page-by-page specs with wireframes, data sources, permissions, and interactions.

## Shared Pages

| Page | Route | Spec |
|:-----|:------|:-----|
| Overview Dashboard | `/overview` | [[overview-dashboard]] |
| Employee Self-Service | `/my-dashboard` | [[self-service]] |

## Pillar 1: HR Management

| Page | Route | Spec |
|:-----|:------|:-----|
| Employee List | `/hr/employees` | [[employees]] |
| Employee Detail | `/hr/employees/[id]` | [[employee-detail]] |
| Leave Management | `/hr/leave` | [[leave]] |
| Performance Reviews | `/hr/performance` | [[performance]] |
| Payroll Runs | `/hr/payroll` | [[payroll]] |

## Pillar 2: Workforce Intelligence

| Page | Route | Spec |
|:-----|:------|:-----|
| Live Workforce Dashboard | `/workforce/live` | [[live-dashboard]] |
| Employee Activity Detail | `/workforce/activity/[employeeId]` | [[employee-activity]] |
| Workforce Reports | `/workforce/reports` | [[reports]] |
| Exception Management | `/workforce/exceptions` | [[exceptions]] |
| Monitoring Settings | `/settings/monitoring` | [[settings]] |

## Conventions

- Each spec includes: purpose, route, permissions, wireframe (ASCII), data sources, interactions, empty states
- Wireframes are ASCII — use them as layout guides, not pixel-perfect designs
- All pages are permission-gated — check the spec for required permissions
- Data sources reference backend API endpoints from `docs/architecture/modules/`
