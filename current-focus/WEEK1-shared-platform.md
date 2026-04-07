# WEEK1: Shared Platform + Agent Gateway

**Status:** Planned
**Priority:** Critical
**Assignee:** Dev 4
**Sprint:** Week 1 (Apr 7-11)
**Module:** SharedPlatform + AgentGateway

## Description

Implement cross-cutting platform services: SSO configuration, token rotation, subscription/billing (Stripe), feature flags, tenant branding, the generic workflow/approval engine, AND the Agent Gateway for desktop agent data ingestion.

## Acceptance Criteria

### Shared Platform
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

### Agent Gateway (NEW)
- [ ] `registered_agents` table + CRUD
- [ ] `agent_policies` table — policy JSON schema validated
- [ ] `agent_health_logs` table
- [ ] `POST /api/v1/agent/register` — register device, return device JWT
- [ ] `POST /api/v1/agent/heartbeat` — update last_heartbeat_at, report health
- [ ] `GET /api/v1/agent/policy` — fetch monitoring policy (merged tenant toggles + employee overrides)
- [ ] `POST /api/v1/agent/ingest` — high-throughput data ingestion (202 Accepted, async processing)
- [ ] `POST /api/v1/agent/login` — link employee to device
- [ ] `POST /api/v1/agent/logout` — unlink employee
- [ ] Device JWT authentication (separate from user JWT, `type: "agent"` claim) — see [[auth-architecture]]
- [ ] Rate limiting per device (30 req/min/device)
- [ ] `DetectOfflineAgentsJob` Hangfire job — flag agents with no heartbeat for 5+ min
- [ ] Policy merge logic: tenant toggles + employee overrides — see [[configuration]]

## Related

- [[module-catalog]] — SharedPlatform + AgentGateway module details
- [[shared-platform]] — Shared Platform architecture
- [[agent-gateway]] — Agent Gateway architecture
- [[configuration]] — Monitoring toggles + employee overrides
- [[external-integrations]] — Stripe integration
- [[notification-system]] — notification pipeline
- [[event-catalog]] — workflow events, agent events
- [[auth-architecture]] — SSO, token management, device JWT
- [[multi-tenancy]] — tenant context for all platform services
- [[WEEK1-auth-security]] — device JWT issued here, validated by Auth module (same week)
- [[WEEK1-infrastructure-setup]] — shared kernel and solution structure this depends on
- [[WEEK2-workforce-presence-biometric]] — agent ingest data flows into presence sessions
- [[WEEK3-activity-monitoring]] — agent ingest data flows into activity pipeline
- [[WEEK4-supporting-bridges]] — notification module enhanced with monitoring alert event types
