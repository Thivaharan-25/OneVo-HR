# Task: Configuration Module

**Assignee:** Dev 4
**Module:** Configuration
**Priority:** High
**Dependencies:** [[current-focus/DEV1-infrastructure-setup|DEV1 Infrastructure Setup]] (industry profile seeding), [[current-focus/DEV4-shared-platform-agent-gateway|DEV4 Shared Platform Agent Gateway]] (tenant context)

---

## Step 1: Backend

### Acceptance Criteria

- [ ] `tenant_settings` table — timezone, date format, work hours, privacy mode
- [ ] `monitoring_feature_toggles` table — global ON/OFF per monitoring feature
- [ ] Industry profile default seeding (office_it, manufacturing, retail, healthcare, custom)
- [ ] `employee_monitoring_overrides` table — per-employee feature overrides
- [ ] Merge logic: employee override wins over tenant toggle
- [ ] Bulk override API: set by department/team/job family
- [ ] `integration_connections` table — external service connections
- [ ] `retention_policies` table — per data type retention periods
- [ ] `app_allowlist` table — application allowlist by scope (tenant, department, team, employee)
- [ ] Resolved allowlist API: merge tenant → department → team → employee scopes
- [ ] `IConfigurationService` public interface with all methods
- [ ] `GET/PUT /api/v1/config/monitoring-toggles` — feature toggles
- [ ] `GET/PUT /api/v1/config/employee-overrides` — employee overrides
- [ ] `POST /api/v1/config/employee-overrides/bulk` — bulk set overrides
- [ ] `GET/PUT /api/v1/config/retention-policies` — retention policies
- [ ] `GET/PUT /api/v1/config/tenant-settings` — tenant settings
- [ ] Unit tests >= 80% coverage

### Backend References

- [[modules/configuration/overview|Configuration Module]] — module architecture, IConfigurationService
- [[modules/configuration/monitoring-toggles/overview|Monitoring Toggles]] — toggle schema, industry defaults
- [[modules/configuration/employee-overrides/overview|Employee Overrides]] — override merge logic
- [[modules/configuration/tenant-settings/overview|Tenant Settings]] — settings schema
- [[modules/configuration/retention-policies/overview|Retention Policies]] — per-type retention
- [[infrastructure/multi-tenancy|Multi Tenancy]] — tenant context

---

## Step 2: Frontend

### Pages to Build

```
app/(dashboard)/settings/
├── general/page.tsx              # Tenant settings (timezone, work hours, etc.)
├── monitoring/page.tsx           # Monitoring feature toggles + employee overrides
├── integrations/page.tsx         # Integration connections
├── branding/page.tsx             # Logo, colors, domain
├── billing/page.tsx              # Subscription & plan
├── feature-flags/page.tsx        # Feature flag management
├── notifications/page.tsx        # Channel config (org-level)
└── components/                   # Colocated settings components
    ├── SettingsForm.tsx           # Reusable settings form layout
    └── IntegrationCard.tsx        # Integration status card
```

### What to Build

- [ ] Monitoring toggles page: master toggle per feature (screenshots, app tracking, meeting detection, etc.)
- [ ] Employee override management: search employee, toggle individual features
- [ ] Bulk override: select department/team, apply overrides
- [ ] Tenant settings page: timezone, date format, work hours, privacy mode (SettingsForm)
- [ ] Integration connections: IntegrationCard list, add, test connections
- [ ] Colocated components: SettingsForm, IntegrationCard
- [ ] PermissionGate: `monitoring:view-settings`, `monitoring:configure`, `settings:manage`

### Userflows

- [[Userflow/Configuration/monitoring-toggles|Monitoring Toggles]] — toggle monitoring features
- [[Userflow/Configuration/employee-override|Employee Override]] — override monitoring per employee
- [[Userflow/Configuration/retention-policy-setup|Retention Policy Setup]] — configure data retention
- [[Userflow/Configuration/tenant-settings|Tenant Settings]] — manage tenant settings

### API Endpoints (Frontend Consumes)

| Method | Endpoint | Purpose |
|:-------|:---------|:--------|
| GET | `/api/v1/config/monitoring-toggles` | Feature toggles |
| PUT | `/api/v1/config/monitoring-toggles` | Update toggles |
| GET | `/api/v1/config/employee-overrides` | Employee overrides |
| PUT | `/api/v1/config/employee-overrides` | Update overrides |
| POST | `/api/v1/config/employee-overrides/bulk` | Bulk set overrides |
| GET | `/api/v1/config/retention-policies` | Retention policies |
| PUT | `/api/v1/config/retention-policies` | Update policies |
| GET | `/api/v1/config/tenant-settings` | Tenant settings |
| PUT | `/api/v1/config/tenant-settings` | Update settings |

### Frontend References

- [[frontend/design-system/components/component-catalog|Component Catalog]] — Switch, DataTable, Dialog, Select
- [[frontend/design-system/patterns/layout-patterns|Layout Patterns]] — settings page layout
- [[frontend/data-layer/api-integration|API Integration]] — API client pattern

---

## Related Tasks

- [[current-focus/DEV1-infrastructure-setup|DEV1 Infrastructure Setup]] — industry profile seeding
- [[current-focus/DEV3-activity-monitoring|DEV3 Activity Monitoring]] — activity monitoring reads toggles from this module
- [[current-focus/DEV3-workforce-presence-setup|DEV3 Workforce Presence Setup]] — presence features gated by toggles
- [[current-focus/DEV4-identity-verification|DEV4 Identity Verification]] — identity verification toggled here
