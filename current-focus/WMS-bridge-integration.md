# Task: WMS Bridge Integration

**Owner:** Cross-team (Dev 1 + Dev 2 + Dev 3 + Dev 4)
**Pillar:** Connectivity Bridges
**Priority:** High (Phase 1 bridges) / Medium (Phase 2 bridges)
**Depends on:** Knowledge brain fixes completed first (see [[docs/wms-integration-analysis|WMS Integration Analysis]])
**Status:** Phase 0 complete — knowledge brain fixes done. Ready for dev to start Phase 1 bridges.

> [!IMPORTANT]
> Development on these bridges does NOT start until the knowledge brain analysis doc questions are resolved and the fixes in Section D of [[docs/wms-integration-analysis|WMS Integration Analysis]] are applied.
> The WMS team (other team) builds against ONEVO's bridge API contracts — they need the schemas defined first.

---

## Phase 0: Knowledge Brain Fixes (Before Any Code)

These are documentation-only tasks. No code. Assign to the team member who owns each module.

- [x] **Dev 2** — `modules/core-hr/overview.md`: Add WMS People Sync as consumer of `EmployeeCreated`, `EmployeePromoted`, `EmployeeTransferred`, `EmployeeTerminated`
- [x] **Dev 1** — `modules/productivity-analytics/overview.md`: Add `wms_productivity_snapshots` table + bridge dependency
- [x] **Dev 3** — `modules/skills/overview.md`: Add `source` column to `employee_skills` table spec
- [x] **Dev 4** — `database/schemas/shared-platform.md`: Add `wms_role_mappings` + `wms_tenant_links` table specs
- [x] **Dev 4** — `backend/external-integrations.md`: Rename "Performance" bridge → "Productivity Metrics Bridge"
- [x] **Dev 4** — Create `backend/bridge-api-contracts.md`: Full request/response schemas for all 5 bridges
- [x] **Dev 4** — Create `modules/shared-platform/wms-tenant-provisioning.md`: Purchasing model + provisioning flow
- [x] **Product Owner** — `database/schema-catalog.md` + `backend/module-catalog.md`: Reconcile Phase 1/2 table count split
- [x] **Product Owner** — `AI_CONTEXT/project-context.md`: Fix "SaaS" label → "white-label SaaS"
- [x] **Product Owner** — Chatbot scope confirmed: WMS team builds chatbot via Semantic Kernel, ONEVO provides permission-checked REST API (all features, not leave-only). Documented in `modules/shared-platform/chatbot-api-integration.md`

---

## Phase 1 Bridges — Build These During Phase 1

These bridges are needed during Phase 1 because Discrepancy Engine and People Sync depend on them.

### Bridge 1: People Sync (HR → WMS)
**Owner:** Dev 2 (Core HR Lifecycle already handles the events)
**When:** After DEV2-core-hr-lifecycle task is complete
**Endpoint:** `GET /api/v1/bridges/people-sync/employees`

#### Acceptance Criteria
- [ ] Paginated employee list with: `id`, `full_name`, `email`, `role`, `department`, `team`, `job_title`, `status`, `wms_role_identifier` (from `wms_role_mappings`)
- [ ] Authenticated via bridge API key (not user JWT) — `Authorization: Bridge <key>`
- [ ] Tenant-scoped — key maps to a single tenant
- [ ] Query params: `?updatedSince=<ISO8601>` for delta sync, `?page=`, `?pageSize=` (max 100)
- [ ] `EmployeeCreated` domain event → publishes `WmsPeopleSyncPending` → bridge handles async provisioning
- [ ] `EmployeePromoted` event → updates employee's `wms_role_identifier` via new role mapping
- [ ] `EmployeeTransferred` event → updates team/department in sync response
- [ ] `EmployeeTerminated` event → sets `status: "deactivated"` in sync response
- [ ] Response includes `last_modified_at` per employee (WMS uses this for delta detection)

---

### Bridge 2: Availability (HR → WMS)
**Owner:** Dev 1 (Leave + Workforce Presence)
**When:** After DEV1-leave task is complete
**Endpoint:** `GET /api/v1/bridges/availability/{employeeId}`

#### Acceptance Criteria
- [ ] Returns combined availability object:
  - `leave_periods[]` — `start_date`, `end_date`, `leave_type`, `status` (only `approved`)
  - `presence_status` — today's value: `present`, `absent`, `on_leave`, `holiday`, `weekend`
  - `clock_in_at` — ISO8601 timestamp of actual clock-in today, `null` if not yet clocked in
  - `clock_out_at` — ISO8601 timestamp of actual clock-out today, `null` if still clocked in or not yet clocked in
  - `shift_start` — HH:MM (from workforce_presence shift config)
  - `shift_end` — HH:MM
  - `expected_daily_hours` — decimal (e.g., 8.0)
  - `public_holidays[]` — `date`, `name` for the tenant's configured country (next 90 days)
- [ ] Authenticated via bridge API key
- [ ] Query param: `?from=<date>&to=<date>` for leave periods range

---

### Bridge 3: Work Activity (WMS → HR)
**Owner:** Dev 1 (Discrepancy Engine reads this)
**When:** Before Discrepancy Engine goes live
**Endpoint:** `POST /api/v1/bridges/work-activity/time-logs`

#### Acceptance Criteria
- [ ] Accepts batch of time log entries from WMS:
  ```json
  {
    "logs": [
      {
        "employee_id": "uuid",
        "task_id": "string",
        "project_id": "string",
        "date": "2026-04-15",
        "logged_minutes": 120,
        "active_task_at": "2026-04-15T14:30:00Z"
      }
    ]
  }
  ```
- [ ] Aggregates `logged_minutes` by `employee_id` + `date` → writes to `wms_daily_time_logs` table
- [ ] 202 Accepted response (async processing)
- [ ] Idempotent — re-submission for same `employee_id` + `date` overwrites (upsert)
- [ ] Discrepancy Engine reads `wms_daily_time_logs` for `wms_logged_minutes`

**New table needed:** `wms_daily_time_logs`
```
wms_daily_time_logs
- id (uuid)
- tenant_id (uuid)
- employee_id (uuid) — FK → employees
- date (date)
- total_logged_minutes (int)
- active_task_at (timestamptz) — nullable, most recent active task timestamp
- created_at (timestamptz)
- updated_at (timestamptz)
Index: (tenant_id, employee_id, date) UNIQUE
```

---

### Bridge 3a: Skills Profile Read (HR → WMS)
**Owner:** Dev 3 (Skills module)
**When:** Phase 1 — after Skills module `employee_skills` table is built
**Endpoint:** `GET /api/v1/bridges/skills/{employeeId}`

#### Acceptance Criteria
- [ ] Returns all `employee_skills` records where `status = 'validated'` for the given employee
- [ ] Response format: `[{ skill_name, category, proficiency_level, source }]`
- [ ] `source` field included — WMS uses it to distinguish `manager_validated` vs `self_declared`
- [ ] WMS uses this for AI task assignment suggestion (match required skill to available team member)
- [ ] Auth: Bridge API key required (`bridges:read` scope)

---

## Phase 2 Bridges — Build After Phase 1 Complete

### Bridge 4: Productivity Metrics (WMS → HR)
**Owner:** Dev 1 (Productivity Analytics module)
**When:** Phase 2 — after WMS team has task completion data
**Endpoint:** `POST /api/v1/bridges/productivity-metrics/snapshots`
*(formerly named "Performance" bridge — renamed to avoid confusion with ONEVO Performance module)*

#### Acceptance Criteria
- [ ] Accepts monthly/weekly productivity snapshots from WMS:
  ```json
  {
    "employee_id": "uuid",
    "period_type": "monthly",
    "period_start": "2026-04-01",
    "period_end": "2026-04-30",
    "tasks_completed": 24,
    "tasks_on_time": 20,
    "on_time_delivery_rate": 83.3,
    "productivity_score": 78.5,
    "active_projects_count": 3
  }
  ```
- [ ] Writes to `wms_productivity_snapshots` table in Productivity Analytics module
- [ ] Data visible to Admin + Reporting Manager only (not employee)
- [ ] Phase 2 Performance module reads this alongside agent-based scores for composite review

---

### Bridge 5: Skill Gap Report (WMS → HR)
**Owner:** Dev 3 (Skills module)
**When:** Phase 2 — after WMS has task performance data to observe skill gaps
**Note:** Skills GET (WMS reads employee profile) is Bridge 3a in Phase 1. This bridge handles the reverse direction only.
**Endpoint:** `POST /api/v1/bridges/skills/{employeeId}/gap-report`

#### Acceptance Criteria — POST (WMS → ONEVO)
- [ ] Accepts skill gap report from WMS:
  ```json
  {
    "skill_id": "uuid",
    "observed_at": "2026-04-15",
    "task_ids": ["string"],
    "note": "Employee completed 3 tasks tagged React but had repeated issues"
  }
  ```
- [ ] Creates/updates `employee_skills` record with `source: "wms_observed"`, `status: "pending"` (requires HR review)
- [ ] Creates `skill_validation_requests` entry flagging the downgrade for manager review
- [ ] This flag shows as high-priority in ONEVO skills dashboard (surfaced above other pending items)
- [ ] Manager sees: "WMS flagged a skill gap in React — view task context" (with link to task_ids if WMS exposes them)

---

### Bridge 6: Talent & Impact Signals (WMS → HR)
**Owner:** Dev 1 (Productivity Analytics module)
**When:** Phase 2 — after WMS analytics engine is built and has sufficient historical data
**Endpoint:** `POST /api/v1/bridges/talent-signals`

**What WMS sends:**
- **Sentiment / engagement signals** — computed from task behavior: assignment response time, collaboration frequency (comments/updates on tasks), task avoidance patterns (repeated deadline pushes on specific task types)
- **Burnout risk signals** — computed from work patterns: consecutive overtime weeks, simultaneous task overload, declining output per logged hour, no logged breaks within shift

#### Acceptance Criteria
- [ ] Accepts talent signal batch from WMS:
  ```json
  {
    "employee_id": "uuid",
    "period_start": "2026-04-01",
    "period_end": "2026-04-30",
    "sentiment": {
      "score": 62,
      "indicators": ["slow_assignment_response", "declining_task_comments"]
    },
    "burnout_risk": {
      "level": "medium",
      "indicators": ["consecutive_overtime_3wks", "task_overload_active_8"]
    }
  }
  ```
- [ ] Writes to `wms_talent_signals` table (new — Productivity Analytics module)
- [ ] Visible to HR Admin and Reporting Manager only — not exposed to employee
- [ ] HR uses sentiment score for engagement tracking and training triggers
- [ ] HR uses burnout risk level for early intervention before health deteriorates

**New table needed:** `wms_talent_signals`
```
wms_talent_signals
- id (uuid)
- tenant_id (uuid)
- employee_id (uuid) — FK → employees
- period_start (date)
- period_end (date)
- sentiment_score (integer) — nullable, 0–100
- sentiment_indicators (jsonb) — array of indicator strings
- burnout_risk_level (varchar 10) — 'low', 'medium', 'high', nullable
- burnout_indicators (jsonb) — array of indicator strings
- created_at (timestamptz)
Index: (tenant_id, employee_id, period_start)
```

---

## Bridge Authentication

All bridge endpoints use a dedicated **Bridge API Key** (not user JWT).

### How it works
- Tenant admin generates a bridge API key in ONEVO settings (`POST /api/v1/settings/bridge-keys`)
- Key is scoped to `bridges:*` permission only — cannot access any HR data
- Header: `Authorization: Bridge <key>`
- Keys are stored hashed in `bridge_api_keys` table (new table in Shared Platform)
- One key per integration (WMS gets its own key, cannot share with others)
- Keys can be revoked instantly from settings

**New table needed:** `bridge_api_keys`
```
bridge_api_keys
- id (uuid)
- tenant_id (uuid)
- name (varchar 100) — human label e.g. "WorkManage Pro"
- key_hash (varchar) — bcrypt hash of the key
- key_prefix (varchar 8) — first 8 chars for display
- scopes (varchar[]) — e.g. ["bridges:read", "bridges:write"]
- last_used_at (timestamptz)
- expires_at (timestamptz) — nullable
- created_by_id (uuid) — FK → users
- created_at (timestamptz)
- revoked_at (timestamptz) — nullable
```

---

## WMS Tenant Provisioning (When Customer Buys Both)

**Owner:** Dev 4 (Shared Platform)
**Full spec:** [[modules/shared-platform/wms-tenant-provisioning|WMS Tenant Provisioning]]

### Key flows
- **Buy both together:** Onboarding wizard creates ONEVO tenant → generates bridge API key automatically → provides setup guide to configure WMS side
- **Buy separately, link later:** Admin goes to Settings → Integrations → "Connect WorkManage Pro" → generate key → enter into WMS
- **Role mapping:** Admin creates roles in ONEVO → for each role, can assign WMS permission set → stored in `wms_role_mappings`

---

## Cross-Dev Dependencies for WMS Bridges

```
DEV1 Leave complete ──────────────────> Bridge 2 (Availability) can be built
DEV1 Productivity Analytics complete ─> Bridge 4 (Productivity Metrics) table ready
DEV2 Core HR Lifecycle complete ──────> Bridge 1 (People Sync) domain events fire correctly
DEV3 Skills Core complete ────────────> Bridge 5 GET direction ready
DEV4 Shared Platform complete ────────> Bridge API key auth + WMS tenant provisioning ready
All Phase 1 bridges complete ─────────> WMS team can begin integration testing
```

---

## Backend References

- [[docs/wms-integration-analysis|WMS Integration Analysis]] — Full audit of gaps and errors
- [[backend/external-integrations|External Integrations]] — Bridge endpoint registry
- [[backend/bridge-api-contracts|Bridge API Contracts]] — Full request/response schemas (to be created)
- [[modules/discrepancy-engine/overview|Discrepancy Engine]] — Depends on Work Activity bridge
- [[modules/productivity-analytics/overview|Productivity Analytics]] — Landing module for WMS metrics
- [[modules/skills/overview|Skills]] — Bidirectional skills bridge
- [[modules/core-hr/overview|Core HR]] — Domain events that trigger People Sync
- [[modules/shared-platform/wms-tenant-provisioning|WMS Tenant Provisioning]] — Purchasing + role mapping

---

## Related Tasks

- [[current-focus/DEV1-productivity-analytics|DEV1 Productivity Analytics]] — Add `wms_productivity_snapshots` table
- [[current-focus/DEV1-leave|DEV1 Leave]] — Availability bridge reads leave data
- [[current-focus/DEV2-core-hr-lifecycle|DEV2 Core HR Lifecycle]] — Domain events needed for People Sync
- [[current-focus/DEV3-skills-core|DEV3 Skills Core]] — Add `source` column to `employee_skills`
- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4 Shared Platform]] — Bridge API key auth + WMS tenant provisioning
