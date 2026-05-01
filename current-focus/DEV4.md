# DEV4: Backend Monitoring Agent + Agent Gateway

**Track:** Backend
**Primary ownership:** Windows monitoring agent, Agent Gateway, activity monitoring, identity verification, exception engine, discrepancy engine, productivity analytics, IDE install jobs, agent version rollout
**Current Unfinished Task:** Task 1 - Agent Gateway enrollment
**Blocked By:** DEV1 auth foundation

---

## ADE Instructions

When Dev 4 asks to continue, start with the first unchecked item in **Current Unfinished Task**. Dev 4 owns the monitoring agent end to end. The IDE extension only triggers the consent-based install request flow.

---

## Task 1: Agent Gateway Enrollment

**Goal:** implement login-based Windows agent enrollment and device credential issuance.

### Acceptance Criteria

- [ ] `registered_agents` table exists.
- [ ] `agent_sessions` table exists.
- [ ] `agent_policies` table exists.
- [ ] `agent_health_logs` table exists.
- [ ] `POST /api/v1/agent/enroll/start` creates a short-lived enrollment challenge.
- [ ] `POST /api/v1/agent/enroll/complete` validates challenge and user session, registers device, starts agent session, and returns a device credential.
- [ ] Device credential is separate from user JWT.
- [ ] Agent login/logout APIs start and end employee collection sessions.
- [ ] Tests cover enrollment, challenge expiry, device credential issuance, and tenant isolation.

### References

- [[modules/agent-gateway/overview|Agent Gateway]]
- [[modules/agent-gateway/agent-registration/overview|Agent Registration]]
- [[modules/agent-gateway/agent-server-protocol|Agent Server Protocol]]
- [[modules/agent-gateway/tray-app-ui|Tray App UI]]
- [[modules/agent-gateway/monitoring-lifecycle/overview|Monitoring Lifecycle]]

### Verification

```bash
dotnet test ONEVO.sln --filter AgentGateway
```

---

## Task 2: Monitoring Agent Client

**Goal:** build the Windows monitoring agent, TrayApp login, policy handling, and collector lifecycle.

### Acceptance Criteria

- [ ] Windows installer is produced with correct app identity.
- [ ] TrayApp supports login, logout, status display, and personal break toggle.
- [ ] Agent stores device credential using Windows secure storage.
- [ ] Agent fetches policy after successful enrollment.
- [ ] Collectors start only when policy and presence lifecycle allow collection.
- [ ] Process/window/idle/screenshot collectors obey policy.
- [ ] Local buffer stores events safely when offline.
- [ ] Agent resumes upload when connectivity returns.
- [ ] Tests or harness scripts validate policy fetch, collector start/stop, and offline buffer replay.

### References

- [[backend/agent/windows-agent|Windows Agent]]
- [[modules/agent-gateway/agent-installer|Agent Installer]]
- [[modules/agent-gateway/sqlite-buffer|SQLite Buffer]]
- [[modules/agent-gateway/data-collection|Data Collection]]

### Verification

```bash
dotnet test ONEVO.sln --filter Agent
```

---

## Task 3: Activity Monitoring + Ingestion + Health

**Goal:** receive agent telemetry, heartbeat, health, screenshots, process/window/idle data, and activity events for analytics and admin UI.

### Acceptance Criteria

- [ ] `POST /api/v1/agent/heartbeat` updates last heartbeat and health state.
- [ ] `GET /api/v1/agent/policy` returns merged effective policy.
- [ ] `POST /api/v1/agent/ingest` accepts batch events and returns `202 Accepted`.
- [ ] Ingestion validates device credential and active agent session.
- [ ] Activity Monitoring stores raw activity snapshots, application usage, screenshots, device usage, meeting detection, and daily summaries.
- [ ] Processing checks Configuration toggles before accepting or processing monitored data.
- [ ] Daily aggregation emits events consumed by discrepancy and productivity modules.
- [ ] Rate limiting exists per device.
- [ ] Offline detection job marks missing agents inactive after threshold.
- [ ] Agent health APIs support list and detail views.
- [ ] Tests cover heartbeat, policy fetch, ingest validation, and offline detection.

### References

- [[backend/monitoring-data-flow|Monitoring Data Flow]]
- [[modules/activity-monitoring/overview|Activity Monitoring]]
- [[modules/activity-monitoring/raw-data-processing/overview|Raw Data Processing]]
- [[modules/agent-gateway/heartbeat-monitoring/overview|Heartbeat Monitoring]]

### Verification

```bash
dotnet test ONEVO.sln --filter ActivityMonitoring
dotnet test ONEVO.sln --filter Heartbeat
```

---

## Task 4: Identity Verification + Biometric Backend

**Goal:** build identity verification policies, verification records, biometric device handling, and on-demand capture processing.

### Acceptance Criteria

- [ ] Verification policies exist per tenant.
- [ ] Verification records support photo, fingerprint, login, logout, interval, and on-demand triggers.
- [ ] Biometric devices, enrollments, biometric events, and biometric audit logs exist.
- [ ] Biometric webhook uses HMAC authentication.
- [ ] Photo verification stores photos through file storage and respects retention.
- [ ] Verification policy checks Configuration monitoring overrides.
- [ ] Failed verification publishes events consumed by Exception Engine and Notifications.
- [ ] On-demand capture results from Agent Gateway are processed and linked to originating exception alert.
- [ ] Tests cover policy update, photo verification, failed verification event, biometric device register, biometric enrollment consent, webhook authentication, and on-demand capture processing.

### References

- [[modules/identity-verification/overview|Identity Verification]]
- [[modules/identity-verification/verification-policies/overview|Verification Policies]]
- [[modules/identity-verification/photo-verification/overview|Photo Verification]]
- [[modules/identity-verification/biometric-devices/overview|Biometric Devices]]
- [[Userflow/Workforce-Intelligence/identity-verification-setup|Identity Verification Setup]]
- [[Userflow/Workforce-Intelligence/identity-verification-review|Identity Verification Review]]

### Verification

```bash
dotnet test ONEVO.sln --filter IdentityVerification
dotnet test ONEVO.sln --filter Biometric
```

---

## Task 5: Exception Engine

**Goal:** build configurable anomaly detection, alert generation, escalation chains, and remote capture actions.

### Acceptance Criteria

- [ ] Exception rules, alerts, escalation chains, acknowledgements, and schedules exist.
- [ ] Threshold JSON is schema-validated per rule type.
- [ ] Evaluation job runs only within configured work hours.
- [ ] Rules support low activity, excess idle, unusual pattern, excess meeting, no presence, break exceeded, verification failed, non-allowed app, presence without activity, and heartbeat gap.
- [ ] Active alert deduplication prevents duplicate alerts for the same ongoing condition.
- [ ] Alert evidence is captured in `data_snapshot_json`.
- [ ] Escalation job escalates unacknowledged alerts by severity chain.
- [ ] Remote screenshot/photo capture action publishes command request to Agent Gateway.
- [ ] SignalR event is published for new alerts.
- [ ] Tests cover rule CRUD, threshold validation, evaluation schedule, alert dedup, escalation, acknowledgement, remote capture request, and notification event.

### References

- [[modules/exception-engine/overview|Exception Engine]]
- [[modules/exception-engine/exception-rules/overview|Exception Rules]]
- [[modules/exception-engine/evaluation-engine/overview|Evaluation Engine]]
- [[modules/exception-engine/alert-generation/overview|Alert Generation]]
- [[modules/exception-engine/escalation-chains/overview|Escalation Chains]]

### Verification

```bash
dotnet test ONEVO.sln --filter ExceptionEngine
```

---

## Task 6: Discrepancy Engine + Productivity Analytics

**Goal:** build daily discrepancy detection and aggregated productivity reporting.

### Acceptance Criteria

- [ ] Discrepancy events, WMS daily time logs, and discrepancy baselines exist.
- [ ] Daily discrepancy job compares HR active time, WorkSync logged time, and calendar/meeting time.
- [ ] Severity calculation supports baseline-relative thresholds and absolute fallback thresholds.
- [ ] Employee-facing notifications never reveal discrepancy analysis.
- [ ] Manager/HR discrepancy APIs enforce visibility rules server-side.
- [ ] Productivity daily, weekly, monthly, and workforce snapshot tables exist.
- [ ] Productivity aggregation consumes Activity Monitoring, Workforce Presence, Exception Engine, and WorkSync analytics.
- [ ] Employee self-service analytics only returns own data.
- [ ] CEO summary hides individual drill-down except escalated/critical exception context.
- [ ] Export endpoints support CSV/Excel-ready data.
- [ ] Tests cover discrepancy job, severity calculator, employee visibility denial, manager visibility, daily report generation, workforce snapshot, employee self-service, CEO summary, and export query.

### References

- [[modules/discrepancy-engine/overview|Discrepancy Engine]]
- [[modules/discrepancy-engine/statistical-baselines/overview|Discrepancy Statistical Baselines]]
- [[modules/productivity-analytics/overview|Productivity Analytics]]
- [[modules/productivity-analytics/daily-reports/overview|Daily Reports]]
- [[modules/productivity-analytics/workforce-snapshots/overview|Workforce Snapshots]]
- [[Userflow/Workforce-Intelligence/activity-snapshot-view|Activity Snapshot View]]
- [[Userflow/Analytics-Reporting/productivity-dashboard|Productivity Dashboard]]

### Verification

```bash
dotnet test ONEVO.sln --filter Discrepancy
dotnet test ONEVO.sln --filter ProductivityAnalytics
```

---

## Task 7: IDE Agent Install Jobs

**Goal:** provide server-side entitlement and install job APIs used by the IDE extension.

### Acceptance Criteria

- [ ] `agent_install_entitlements` table exists.
- [ ] `agent_install_jobs` table exists.
- [ ] `GET /api/v1/ide/entitlements` can report monitoring entitlement and installed status.
- [ ] `POST /api/v1/ide/agent-install/request` validates entitlement and creates install job.
- [ ] Response includes job ID, installer download URL, and SHA256 hash.
- [ ] `GET /api/v1/ide/agent-install/status/{jobId}` returns current install status.
- [ ] `PUT /api/v1/ide/agent-install/{jobId}/installed` marks job installed after agent completion.
- [ ] Audit logs are written for entitlement checks and install requests.
- [ ] Tests cover no entitlement, entitled request, hash metadata, status polling, and installed transition.

### References

- [[modules/ide-extension/overview|IDE Extension Spec]]
- [[Userflow/Workforce-Intelligence/agent-deployment|Agent Deployment]]
- [[database/schemas/agent-gateway|Agent Gateway Schema]]

### Verification

```bash
dotnet test ONEVO.sln --filter AgentInstall
```

---

## Task 8: Agent Version Manager Backend for Developer Platform

**Goal:** expose the monitoring-agent version catalog, deployment rings, force-update, and rollback capabilities consumed by the Developer Platform console.

### Backend Module Location

- Agent runtime feature: `Features/AgentGateway`
- Developer Platform release metadata: `Features/DevPlatform`
- Admin host: `ONEVO.Admin.Api`

### Acceptance Criteria

- [ ] `agent_version_releases` entity is mapped under DevPlatform configuration.
- [ ] `agent_deployment_rings` entity is mapped under DevPlatform configuration.
- [ ] `agent_deployment_ring_assignments` entity is mapped under DevPlatform configuration.
- [ ] Ring seed data exists for Ring 0 Internal, Ring 1 Beta, and Ring 2 GA.
- [ ] Every tenant can belong to exactly one ring.
- [ ] `GET /admin/v1/agent-versions` lists version, channel/status, release notes, minimum OS, publisher, published date, and recalled date.
- [ ] `POST /admin/v1/agent-versions` publishes a new signed agent version with semver uniqueness validation.
- [ ] `PATCH /admin/v1/agent-versions/{id}/channel` changes channel/status and writes audit log.
- [ ] Recalled versions are excluded from future normal rollout eligibility.
- [ ] `GET /admin/v1/agent-rings` lists each ring with assigned tenants and aggregate agent counts.
- [ ] `PUT /admin/v1/tenants/{id}/agent-ring` moves a tenant between rings and writes audit log.
- [ ] `POST /admin/v1/agent-versions/{id}/force-update` dispatches `UPDATE_AGENT` commands to all agents in a selected ring through Agent Gateway.
- [ ] Force-update is restricted to `super_admin`.
- [ ] Tenant-level rollback can force-pin a tenant to a previous stable version through the same Agent Gateway command path.
- [ ] Rollout gate metadata supports operator confirmation before promoting a version to GA.
- [ ] Tests cover seed rings, publish version, duplicate semver rejection, channel change, recall exclusion, ring assignment, force-update authorization, command dispatch, and rollback.

### References

- [[modules/dev-platform/overview|Dev Platform Feature]]
- [[developer-platform/modules/agent-version-manager/overview|Agent Version Manager]]
- [[developer-platform/userflow/agent-versions|Agent Version and Ring Management Flows]]
- [[developer-platform/backend/api-contracts|Admin API Contracts]]
- [[modules/agent-gateway/overview|Agent Gateway]]
- [[modules/agent-gateway/remote-commands/overview|Agent Remote Commands]]

### Verification

```bash
dotnet test ONEVO.sln --filter AgentVersion
dotnet test ONEVO.sln --filter AgentRing
dotnet test ONEVO.sln --filter AgentGateway
```

---

## Open Frontend Contracts

- [ ] Confirm install prompt payload with DEV8.
- [ ] Confirm agent health DTO with DEV6.
- [ ] Confirm agent version DTOs with DEV5 Developer Platform console.
