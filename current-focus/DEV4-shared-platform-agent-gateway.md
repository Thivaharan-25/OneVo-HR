# Task: Shared Platform + Agent Gateway

**Assignee:** Dev 4
**Module:** SharedPlatform + AgentGateway
**Priority:** Critical
**Dependencies:** [[current-focus/DEV1-infrastructure-setup|DEV1 Infrastructure Setup]] (shared kernel), [[current-focus/DEV2-auth-security|DEV2 Auth Security]] (device JWT)

---

## Step 1: Backend

### Acceptance Criteria

#### Shared Platform
- [ ] SSO provider configuration (SAML, OIDC — config only, not full SSO flow)
- [ ] Refresh token table and rotation logic (replaced_by_id chain)
- [ ] Subscription plans seeded (Free, Pro, Enterprise with feature limits)
- [ ] Tenant subscription management (Stripe webhook integration)
- [ ] Feature flag system (4 types: global, org, user, percentage)
- [ ] Feature flag Redis cache with 5-min TTL
- [ ] Tenant branding (custom domain, logo, colors)
- [ ] **Workflow engine:** workflow_definitions, workflow_steps, workflow_instances, approval_actions
- [ ] Workflow supports: conditional routing (JSONB conditions), SLA timeouts, delegation
- [ ] Workflow engine usable by any module via resource_type + resource_id
- [ ] Notification templates (per channel + locale)
- [ ] Notification channels configuration (with encrypted credentials)

#### Agent Gateway
- [ ] `registered_agents` table + CRUD
- [ ] `agent_sessions` table - one active employee session per device; ingest validates employee_id against the active session
- [ ] `agent_policies` table — policy JSON schema validated; includes `document_tracking`, `communication_tracking`, `browser_extension_enabled` flags
- [ ] `agent_health_logs` table
- [ ] **Login-based Windows agent enrollment:** default Phase 1 flow is install app -> user signs in through TrayApp -> backend resolves tenant/user -> backend enrolls device -> device credential issued internally
- [ ] `POST /api/v1/agent/enroll/start` - start authenticated enrollment from TrayApp/system-browser sign-in, return short-lived enrollment challenge
- [ ] `POST /api/v1/agent/enroll/complete` - validate login/enrollment challenge, create or update `registered_agents`, create `agent_sessions`, return internal device credential
- [ ] No employee-facing API key, tenant key, tenant ID, or server URL entry. The employee only signs in.
- [ ] Device credential is issued only after authenticated enrollment and is stored locally with DPAPI / Windows Credential Manager
- [ ] `POST /api/v1/agent/heartbeat` — update last_heartbeat_at, report health
- [ ] `GET /api/v1/agent/policy` — fetch monitoring policy (merged tenant toggles + employee overrides)
- [ ] `POST /api/v1/agent/ingest` — high-throughput data ingestion (202 Accepted, async processing); handles `document_usage` and `communication_usage` batch types in addition to existing types
- [ ] Device JWT authentication (separate from user JWT, `type: "agent"` claim) — see [[modules/auth/authentication/overview|authentication]]
- [ ] Rate limiting per device (30 req/min/device)
- [ ] `POST /api/v1/agent/login` resumes or refreshes an enrolled employee session; `POST /api/v1/agent/logout` ends the active `agent_sessions` row and stops collection
- [ ] Monitoring starts only after successful employee login, policy fetch, consent gate, and Workforce Presence lifecycle permits collection

> **ADE task creation note:** Generate one implementation task named **"Implement login-based Windows agent enrollment"** from this section. Use [[modules/agent-gateway/overview|Agent Gateway]], [[modules/agent-gateway/agent-registration/overview|Agent Registration]], [[modules/agent-gateway/agent-server-protocol|Agent Server Protocol]], [[modules/agent-gateway/tray-app-ui|Tray App UI]], [[modules/agent-gateway/agent-installer|Agent Installer]], [[modules/auth/overview|Auth]], and [[modules/agent-gateway/monitoring-lifecycle/overview|Monitoring Lifecycle]] as the source docs. Do not create a tenant-key installer task for the default flow.
- [ ] `DetectOfflineAgentsJob` Hangfire job — flag agents with no heartbeat for 5+ min
- [ ] Policy merge logic: tenant toggles + employee overrides — see [[modules/configuration/monitoring-toggles/overview|configuration]]

#### WorkPulse Agent — Windows Client
- [ ] `DocumentTracker.cs` — foreground process matching for Word/Excel/PPT/Figma/Photoshop
- [ ] `CommunicationTracker.cs` — Outlook/Slack/Teams active time + UIAutomation send event counts
- [ ] Screenshot trigger: `manual` and `on_demand` only — remove any `scheduled`/`random` trigger logic
- [ ] MSIX package: update `DisplayName` to "WorkPulse Agent" in `Package.appxmanifest`
- [ ] Personal break toggle in TrayApp — pauses all collectors, records period as "Personal Time"

> **macOS Phase 2 — Do NOT build in Phase 1.** Architecture documented in [[modules/agent-gateway/agent-overview|Agent Overview]] macOS section.

### Backend References

- [[backend/module-catalog|Module Catalog]] — SharedPlatform + AgentGateway module details
- [[modules/agent-gateway/overview|agent-gateway]] — Agent Gateway architecture
- [[modules/configuration/monitoring-toggles/overview|configuration]] — monitoring toggles + employee overrides
- [[backend/external-integrations|External Integrations]] — Stripe integration
- [[backend/notification-system|Notification System]] — notification pipeline
- [[backend/messaging/event-catalog|Event Catalog]] — workflow events, agent events
- [[infrastructure/multi-tenancy|Multi Tenancy]] — tenant context for all platform services

---

## Step 2: Frontend

### Pages to Build

```
app/(dashboard)/admin/agents/
├── page.tsx                      # Desktop agent fleet overview
├── [id]/
│   ├── loading.tsx               # Skeleton while loading
│   └── page.tsx                  # Agent detail (status, config, logs)
└── components/                   # Colocated feature components
    ├── AgentStatusCard.tsx        # Agent health + status card
    └── AgentCommandPanel.tsx      # Remote command panel

app/(dashboard)/admin/
├── audit/page.tsx                # Audit log viewer
├── devices/page.tsx              # Hardware terminals
├── compliance/page.tsx           # GDPR, data governance
└── components/                   # Colocated admin components
    └── AuditLogViewer.tsx         # Filterable audit log
```

### What to Build

- [ ] Tenant settings page: timezone, date format, work hours, privacy mode
- [ ] Billing page:
  - Current plan card (plan name, features, limits)
  - Upgrade/downgrade buttons -> Stripe checkout
  - Invoice history
- [ ] SSO configuration page:
  - Provider setup form (SAML/OIDC metadata URL, client ID/secret)
  - Test connection button
- [ ] Feature flag management page (super admin):
  - DataTable: flag name, type, status, scope
  - Toggle on/off, edit targeting rules
- [ ] Notification settings page:
  - Channel configuration: email (Resend API key), in-app, SignalR
  - Template preview per event type
- [ ] Tenant branding page:
  - Logo upload, primary/secondary colors, custom domain
  - Live preview
- [ ] Agent management dashboard:
  - DataTable: device name, employee, status (online/offline), last heartbeat, OS, version
  - StatusBadge: green (online), red (offline > 5 min), yellow (degraded)
  - Agent detail: health log, policy view, registration info
  - Bulk actions: update policy, deregister
- [ ] PermissionGate: `settings:admin`, `agent:view-health`, `agent:manage`

### Userflows

- [[Userflow/Platform-Setup/sso-configuration|Sso Configuration]] — set up SSO provider
- [[Userflow/Platform-Setup/billing-subscription|Billing Subscription]] — manage subscription and billing
- [[Userflow/Platform-Setup/feature-flag-management|Feature Flag Management]] — manage feature flags
- [[frontend/design-system/theming/tenant-branding|Tenant Branding]] — customize tenant branding
- [[Userflow/Workforce-Intelligence/agent-deployment|Agent Deployment]] — deploy and manage desktop agents
- [[Userflow/Notifications/notification-preference-setup|Notification Preference Setup]] — configure notification channels

### API Endpoints (Frontend Consumes)

| Method | Endpoint | Purpose |
|:-------|:---------|:--------|
| GET | `/api/v1/settings/tenant` | Tenant settings |
| PUT | `/api/v1/settings/tenant` | Update tenant settings |
| GET | `/api/v1/settings/branding` | Branding config |
| PUT | `/api/v1/settings/branding` | Update branding |
| GET | `/api/v1/subscriptions/current` | Current subscription |
| POST | `/api/v1/subscriptions/checkout` | Stripe checkout session |
| GET | `/api/v1/subscriptions/invoices` | Invoice history |
| GET | `/api/v1/sso/providers` | SSO provider configs |
| POST | `/api/v1/sso/providers` | Create SSO provider |
| GET | `/api/v1/feature-flags` | List feature flags |
| PUT | `/api/v1/feature-flags/{id}` | Update flag |
| GET | `/api/v1/notifications/channels` | Notification channels |
| PUT | `/api/v1/notifications/channels/{id}` | Update channel config |
| GET | `/api/v1/agents` | List registered agents |
| GET | `/api/v1/agents/{id}` | Agent detail |
| DELETE | `/api/v1/agents/{id}` | Deregister agent |
| GET | `/api/v1/agents/{id}/health` | Agent health log |
| **SignalR** | `/hubs/notifications` | `agent-status` channel |

### Frontend References

- [[frontend/design-system/components/component-catalog|Component Catalog]] — DataTable, StatusBadge, Switch, Card
- [[frontend/design-system/foundations/color-tokens|Color Tokens]] — status colors, brand colors
- [[frontend/data-layer/api-integration|API Integration]] — API client pattern

---

## Related Tasks

- [[current-focus/DEV1-infrastructure-setup|DEV1 Infrastructure Setup]] — shared kernel this depends on
- [[current-focus/DEV2-auth-security|DEV2 Auth Security]] — device JWT issued here, validated by Auth module
- [[current-focus/DEV3-workforce-presence-setup|DEV3 Workforce Presence Setup]] — agent ingest data flows into presence sessions
- [[current-focus/DEV3-activity-monitoring|DEV3 Activity Monitoring]] — agent ingest data flows into activity pipeline
- [[current-focus/DEV4-workforce-presence-biometric|DEV4 Workforce Presence Biometric]] — agent data integration
- [[current-focus/DEV2-notifications|DEV2 Notifications]] — notification module enhanced with monitoring alert event types
