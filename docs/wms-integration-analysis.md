# WMS Integration — Knowledge Brain Analysis

> **Status:** All open questions resolved. Phase 0 knowledge brain fixes complete.
> **Purpose:** Audit of the knowledge brain against the WMS integration spec. Identifies what is wrong, what is missing, and what changes need to happen — in the right order.

---

## Open Questions (Answers needed before full fix)

### Q1 — White Label vs SaaS? ✅ RESOLVED
**Answer:** **White-label SaaS** — cloud-hosted, multi-tenant, Stripe billing, shared infrastructure. Customers brand it under their own name. The model is correct; only the label needed updating.
**Fix applied:** `AI_CONTEXT/project-context.md` updated to "white-label SaaS platform."

### Q2 — Chatbot Scope? ✅ RESOLVED
**Answer:** The chatbot is **not ONEVO's to build**. The WMS team builds it using **Microsoft Semantic Kernel**. ONEVO's only responsibility is to expose its existing REST API with permission checks. The chatbot is NOT limited to leave — it can call any ONEVO endpoint. If a user asks the chatbot to do something they don't have permission for, `[RequirePermission]` returns 403 and the chatbot tells the user they lack access.
**Fix applied:** `modules/shared-platform/chatbot-api-integration.md` created — full architecture, permission enforcement, SK OpenAPI Plugin integration pattern, OAuth scope definitions, Phase 1 (JWT pass-through) and Phase 2 (OAuth 2.0 AS) flows.

### Q3 — Table Count Discrepancy ✅ RESOLVED
**Answer:** 163 was the correct total but both files had wrong Phase 1/2 splits. After manual recount (adding 5 new WMS integration tables, fixing Skills dedup, adding missing Activity Monitoring tables):
- **Correct total: 168 tables (128 Phase 1, 40 Phase 2)**
**Fix applied:** Both `database/schema-catalog.md` and `backend/module-catalog.md` updated to match.

---

## Section A — Errors in the Current Knowledge Brain

### A1. "SaaS" Label Used Everywhere
**Locations:** `AI_CONTEXT/project-context.md` line 5, throughout module docs.
**Problem:** Pending Q1 answer. If white label ≠ SaaS, every occurrence needs updating.
**Fix:** After Q1 answer, do a global search-replace with correct language. If it's *white-label SaaS*, a short clarifying sentence is enough. If it's *self-hosted*, infrastructure docs need larger changes.

---

### A2. Phase 1/2 Table Count Mismatch
**Locations:** `database/schema-catalog.md` vs `backend/module-catalog.md`

| File | Phase 1 | Phase 2 | Total |
|:-----|:--------|:--------|:------|
| `schema-catalog.md` | 121 | 42 | 163 |
| `module-catalog.md` footer | 116 | 47 | 163 |

**Why it differs:** The `schema-catalog.md` likely includes the 5 Phase 1 Skills tables in the Phase 1 count differently from module-catalog.md. Skills is "mixed phase" (5 Phase 1, 10 Phase 2).

**Fix:** Recount manually. Pick one source of truth and sync both files to match.

---

### A3. Two "Performance" Concepts Conflated — This Is a Real Problem

**ONEVO Performance Module** (Phase 2 deferred):
- Tables: `review_cycles`, `reviews`, `goals`, `recognitions`, `succession_plans`, `feedback_requests`, `performance_improvement_plans`
- This is the HR appraisal engine — manager reviews, goals, PIPs, peer feedback

**WMS → HR Performance Bridge** (the bridge named "Performance"):
- `POST /api/v1/bridges/performance/metrics`
- This receives task completion rates, on-time delivery, and productivity scores from WorkManage Pro
- This is **workforce productivity data**, not HR appraisal data

These are completely different. Calling both "Performance" causes confusion. In the knowledge brain, **`modules/productivity-analytics/overview.md`** says its `IProductivityAnalyticsService.GetProductivityScoreAsync()` is consumed by the Performance module — but the Productivity Analytics module only aggregates **agent activity data** (keyboard, app usage, presence). It has **no tables or interfaces for WMS task data**.

**The gap:** WMS task metrics (`on-time delivery rate`, `productivity score from tasks`, `velocity`) have no landing table anywhere in the knowledge brain. They need one.

**Fix required:**
1. Rename the "Performance" bridge → **"Productivity Metrics Bridge"** everywhere
2. Add a `wms_productivity_snapshots` table to the **Productivity Analytics** module (Phase 1, since the Discrepancy Engine already depends on WMS data now)
3. Update `modules/productivity-analytics/overview.md` to show this table and the bridge dependency
4. Update `backend/external-integrations.md` to rename the bridge

---

### A4. Domain Events Missing WMS Bridge as Consumer

`modules/core-hr/overview.md` lists these domain events and their consumers. The WMS People Sync bridge is not listed as a consumer of any of them:

| Event | Current Consumers | Missing Consumer |
|:------|:-----------------|:----------------|
| `EmployeeCreated` | Notifications, Leave | **WMS People Sync** (auto-create WMS account) |
| `EmployeePromoted` | Notifications, Payroll | **WMS People Sync** (permission auto-upgrade) |
| `EmployeeTransferred` | Notifications | **WMS People Sync** (task scope re-map) |
| `EmployeeTerminated` | Leave, Payroll, Agent Gateway | **WMS People Sync** (deactivate WMS access, reassignment alert) |

**Fix:** Update `modules/core-hr/overview.md` domain events table — add WMS People Sync bridge as a consumer for the 4 events above. Document the action it takes for each.

---

### A5. Bridge Payloads Undefined

`backend/external-integrations.md` lists 5 bridge endpoints with routes but **no payload schemas**. The WMS team cannot build against these.

| Bridge | Route | Missing |
|:-------|:------|:--------|
| People Sync | `GET /api/v1/bridges/people-sync/employees` | Response payload: what fields? Role? Permissions? Skill summary? Shift? |
| Availability | `GET /api/v1/bridges/availability/{employeeId}` | Response: leave periods, presence status, public holidays, shift hours — schema undefined |
| Productivity Metrics | `POST /api/v1/bridges/performance/metrics` | Request payload: what fields does WMS send? |
| Skills | `GET/POST /api/v1/bridges/skills/{employeeId}` | Both directions completely undefined |
| Work Activity | `POST /api/v1/bridges/work-activity/time-logs` | Request payload undefined (though Discrepancy Engine implies the fields) |

**Fix:** Create `backend/bridge-api-contracts.md` with full request/response schemas for all 5 bridges.

---

## Section B — Missing from Knowledge Brain

### B1. WMS Inbound — People Sync (Gaps)

The WMS spec requires these inbound flows. Current state:

| WMS Spec Requirement | Knowledge Brain Status |
|:---------------------|:----------------------|
| Auto-create WMS account on onboarding | ❌ Not documented. `EmployeeCreated` event has no WMS consumer |
| Auto-deactivate + reassignment alert on termination | ❌ Not documented. `EmployeeTerminated` has no WMS consumer |
| Permission auto-upgrade on promotion | ❌ Not documented |
| Task scope re-map on team transfer | ❌ Not documented |
| WMS role ↔ ONEVO role mapping when buying both | ❌ No table, no doc |

**Fix needed:**
- Add WMS consumers to domain events (covered in A4)
- Create `backend/bridges/wms-role-mapping.md` documenting how roles map between systems
- Add a `wms_role_mappings` table (in Shared Platform or a new `bridges` module — decision needed)

---

### B2. WMS Inbound — Availability (Gaps)

The current Availability bridge (`GET /api/v1/bridges/availability/{employeeId}`) returns *"leave + presence data."* The WMS spec needs more:

| WMS Spec Requirement | Knowledge Brain Status |
|:---------------------|:----------------------|
| Leave approved (period blocking) | ✓ Leave module has the data |
| Public holidays list | ❌ Missing from bridge. `calendar_events` has this data but no bridge endpoint |
| Daily present/absent status | ✓ Workforce Presence has this |
| Sprint due date adjustment for holidays | ❌ WMS concern, but ONEVO needs to expose the holiday list |
| Shift hours / expected daily hours | ❌ Not in Availability bridge |

**Fix needed:**
- Expand Availability bridge response to include: `leave_periods[]`, `presence_status`, `public_holidays[]`, `shift_start`, `shift_end`, `expected_daily_hours`
- Document this in bridge-api-contracts.md (see A5)

---

### B3. WMS Inbound — Skill & Baseline (Gaps)

| WMS Spec Requirement | Knowledge Brain Status |
|:---------------------|:----------------------|
| Employee skill matrix (skill + proficiency) | ✓ `employee_skills` + `skills` tables exist. Skills bridge (`GET /api/v1/bridges/skills/{employeeId}`) covers this but payload is undefined |
| Shift hours / work policy as baseline | ❌ Not in any bridge |
| Expected daily hours (for idle/overtime detection in WMS) | ❌ Missing |

**Fix needed:** Add shift/hours to the Availability bridge response OR create a separate `GET /api/v1/bridges/baseline/{employeeId}` endpoint. Document which.

---

### B4. WMS Outbound — Performance/Productivity (Gaps)

This is the most significant structural gap. The WMS spec says WMS pushes these back to HR:

| WMS Spec Requirement | Knowledge Brain Status |
|:---------------------|:----------------------|
| Productivity score per task/employee | ❌ No landing table in ONEVO |
| On-time delivery rate | ❌ No landing table |
| Skill gap report (from task performance) | ❌ No table, no mechanism |
| Monthly aggregate for appraisal cycle | ❌ Nothing in Performance module (Phase 2) connects to this |
| Trend analysis (improving/declining) | ❌ No table |

**New table needed:** `wms_productivity_snapshots` in the Productivity Analytics module.

```
wms_productivity_snapshots
- id (uuid)
- tenant_id (uuid)
- employee_id (uuid)
- period_type (varchar) — 'daily', 'weekly', 'monthly'
- period_start (date)
- period_end (date)
- tasks_completed (int)
- tasks_on_time (int)
- on_time_delivery_rate (decimal 5,2)
- productivity_score (decimal 5,2)  — WMS-calculated score
- velocity_story_points (int)  — nullable
- active_projects_count (int)
- submitted_at (timestamptz)
- created_at (timestamptz)
```

This table bridges WMS data into ONEVO without touching the Phase 2 Performance module. When Phase 2 launches, the Performance module reads from both `IProductivityAnalyticsService` (agent-based) and `wms_productivity_snapshots` (task-based).

---

### B5. WMS Outbound — Time & Validation (Gaps)

The Discrepancy Engine (`modules/discrepancy-engine/overview.md`) is well-documented. It reads `wms_logged_minutes` from the Work Activity bridge. This covers the dual-layer validation correctly. ✓

**✅ RESOLVED — Direction is ONEVO-only (no push back to WMS).**

Flow confirmed:
1. WMS pushes task time logs → ONEVO (`POST /api/v1/bridges/work-activity/time-logs`)
2. ONEVO Discrepancy Engine compares WMS logged minutes vs Agent active minutes
3. Discrepancy flag sent to Reporting Manager + Admin inside ONEVO only
4. WMS does NOT receive idle/overtime data back — this is an internal HR compliance record, not a WMS concern

No new endpoint or outbound webhook needed. B5 is closed.

---

### B6. WMS Outbound — Talent & Impact Analysis (Gaps)

| WMS Spec Requirement | Knowledge Brain Status |
|:---------------------|:----------------------|
| Skill gap report from WMS task performance | ✅ Phase 2 — Skills bridge `POST /api/v1/bridges/skills/{employeeId}/gap-report`. `source` column added to `employee_skills` in Phase 1 to distinguish `wms_observed` from `manager_validated` |
| Leave impact risk (project delay risk shown to manager) | ✅ Resolved — Option B chosen: ONEVO exposes `GET /api/v1/bridges/leave-impact/{employeeId}?startDate=&endDate=`, WMS calls it to check open assignments. Manager sees risk before approving leave |
| Sentiment/engagement signals | ✅ Phase 2 — WMS computes from task behavior (assignment response time, collaboration frequency, task avoidance patterns) and pushes signals to ONEVO. HR uses for engagement tracking |
| Burnout detection from work patterns | ✅ Phase 2 — WMS computes from work patterns (consecutive overtime weeks, task overload, declining output per logged hour) and pushes risk flag to ONEVO. HR intervenes early |

**Skills Phase 1:** WMS reads employee validated skills via `GET /api/v1/bridges/skills/{employeeId}`. Returns current `employee_skills` where `status = validated`. Skill management workflow (employee self-declare → manager validates, manager direct-add, employee-only delete) is internal ONEVO — WMS consumes the output only.

**Leave impact — Option B confirmed:** ONEVO pulls from WMS on demand. WMS does not need to know ONEVO's internal leave request lifecycle. Cleaner separation of concerns.

**Sentiment + Burnout direction confirmed:** Both are WMS → ONEVO (outbound from WMS). WMS owns the task behavior data. ONEVO does not generate these signals — it receives and stores them for HR use. Both deferred to Phase 2 pending WMS analytics engine being built.

**Skill gap feedback loop (Phase 2):**
1. `source` column already added to `employee_skills` in Phase 1 (`self_declared` default)
2. Skills bridge `POST /api/v1/bridges/skills/{employeeId}/gap-report` — WMS flags observed gap
3. Written to `employee_skills` with `source = wms_observed` — does not overwrite `manager_validated` entry
4. Surfaces as high-priority gap in ONEVO skills dashboard

---

### B7. Purchasing Model — Not Documented Anywhere

The entire purchase + provisioning flow is missing. The WMS spec and the user's point #4 and #5 need this documented.

**Scenarios to document:**

| Scenario | What must happen |
|:---------|:----------------|
| Buy ONEVO only | Standard ONEVO tenant onboarding |
| Buy WMS only (from other team) | WMS has no ONEVO integration |
| Buy both together | Auto-create ONEVO tenant + WMS tenant linked by shared `tenant_id` or bridge API key. Single onboarding wizard. |
| Buy separately, link later | Admin links accounts post-purchase via API key exchange |

**When buying both:** Role creation happens once — in ONEVO. The WMS team consumes those roles via the People Sync bridge and maps them to WMS permissions. The customer creates one role ("Team Lead") in ONEVO with ONEVO permissions AND selects WMS permissions for that role in the same setup screen.

**Where this needs to be documented:**
- New file: `modules/shared-platform/wms-tenant-provisioning.md`
- Update: `database/schemas/shared-platform.md` — add `wms_tenant_links` table
- Update: `AI_CONTEXT/project-context.md` — purchasing configurations section

---

### B8. Leave Approval in Chatbot ✅ RESOLVED

The WMS team builds the chatbot (Semantic Kernel). ONEVO exposes its existing leave approval API. No special endpoints needed. The existing `POST /api/v1/workflows/{instanceId}/approve` endpoint handles this — the chatbot calls it with the user's JWT. If the user lacks `leave:approve` permission, it returns 403 and the chatbot says "You don't have permission to approve leave requests."

**Documented in:** `modules/shared-platform/chatbot-api-integration.md`

The ONEVO-side notification + workflow panel approval flow (conflict-aware inline approval) is still the primary UX for ONEVO users. The chatbot is a secondary access path for WMS users working inside the WMS tool.

---

## Section C — Phase 1 → Phase 2 Conflict Check

### C1. Salary → Payroll ✓ No Conflict

`employee_salary_history` is in Core HR (Phase 1, 13 tables). When an employee is onboarded, their salary is recorded there. Payroll module (Phase 2) reads `employee_salary_history` as its starting point — it doesn't create a competing structure. **Safe.**

---

### C2. Skills — Needs `source` Column Before Phase 2

The `employee_skills` table (Phase 1) has these columns today:
`id, tenant_id, employee_id, skill_id, proficiency_level, status, validated_by_id, last_assessed_in_review_id, created_at, updated_at`

**Problem:** When WMS syncs skill gap data back (Phase 2 bridge), it will write to `employee_skills`. But there's no way to distinguish:
- `self_declared` — employee added themselves
- `manager_validated` — manager confirmed
- `wms_observed` — WMS flagged an issue with this skill in practice

Without a `source` column, WMS-flagged skill problems will overwrite manager-validated data or appear identical to self-declarations.

**Fix (add in Phase 1, before any WMS sync):**
Add `source varchar(30)` to `employee_skills` with values `self_declared`, `manager_validated`, `wms_observed`, `assessment_result`. Default: `self_declared`.

This is a non-breaking additive migration. Do it in Phase 1 now to avoid a Phase 2 breaking change.

---

### C3. Performance Bridge Needs a Landing Table Before Performance Module Launches

The Performance Bridge (`POST /api/v1/bridges/performance/metrics`) will receive WMS data **before** Phase 2. The Performance module is Phase 2. **There is currently nowhere for this data to go.**

**Solution:** `wms_productivity_snapshots` table in Productivity Analytics module (Phase 1). See B4 for schema.

When the Performance module launches in Phase 2, it reads from:
- `IProductivityAnalyticsService` → agent activity scores
- `wms_productivity_snapshots` → task-based WMS scores
Both feed into a single composite productivity score for the appraisal cycle. No conflict.

---

### C4. WMS Role/Permission Mapping — Missing Table

When a customer buys both ONEVO + WMS, roles are defined in ONEVO. WMS needs to know which ONEVO role maps to which WMS permission level.

**No table exists for this today.** Needed:

```
wms_role_mappings
- id (uuid)
- tenant_id (uuid)
- onevo_role_id (uuid) — FK → roles
- wms_role_identifier (varchar) — the WMS-side role name/ID
- wms_permissions_json (jsonb) — which WMS features are enabled for this ONEVO role
- created_at (timestamptz)
- updated_at (timestamptz)
```

This table lives in Shared Platform. When `EmployeePromoted` fires, the People Sync bridge reads the new role's `wms_role_mappings` entry and pushes the updated permissions to WMS.

---

## Section D — Punch List: Exact Changes Needed

All Phase 0 items are complete. Items marked **[PENDING]** are deferred to dev sprint planning.

| # | File | What Changed | Status |
|:--|:-----|:-------------|:-------|
| 1 | `AI_CONTEXT/project-context.md` | "SaaS" → "white-label SaaS", 163→168 tables | ✅ Done |
| 2 | `database/schema-catalog.md` | Reconciled to 168 (128 P1 / 40 P2), 5 new WMS tables added | ✅ Done |
| 3 | `backend/module-catalog.md` | Footer corrected, Skills row fixed, AM/PA/SP counts updated | ✅ Done |
| 4 | `backend/external-integrations.md` | "Performance" bridge renamed → "Productivity Metrics Bridge" | ✅ Done |
| 5 | `modules/core-hr/overview.md` | WMS People Sync added to 4 domain event consumers | ✅ Done |
| 6 | `modules/productivity-analytics/overview.md` | `wms_productivity_snapshots` table + WMS bridge dependency added | ✅ Done |
| 7 | `database/schemas/activity-monitoring.md` | `wms_daily_time_logs` table added | ✅ Done |
| 7b | `database/schemas/productivity-analytics.md` | `wms_productivity_snapshots` table added | ✅ Done |
| 8 | `modules/skills/overview.md` | `source` column added to `employee_skills` | ✅ Done |
| 9 | Created `backend/bridge-api-contracts.md` | Full request/response schemas for all 5 bridges | ✅ Done |
| 10 | Created `modules/shared-platform/wms-tenant-provisioning.md` | Purchasing model + provisioning flows + key management | ✅ Done |
| 11 | `database/schemas/shared-platform.md` | `bridge_api_keys`, `wms_role_mappings`, `wms_tenant_links` added | ✅ Done |
| 12 | Created `modules/shared-platform/chatbot-api-integration.md` | Semantic Kernel chatbot API design (all features, permission-checked) | ✅ Done |
| 13 | Created `docs/phase-compatibility-guide.md` | All 13 Phase 1→2 transitions verified safe | ✅ Done |
| 14 | `calendar_events` schema | `external_id` + `external_source` columns added for Google Calendar sync | ✅ Done |
| 15 | `backend/messaging/event-catalog.md` | WMS People Sync added as consumer of `EmployeeHired`, `EmployeePromoted`, `EmployeeTransferred`, `EmployeeOffboarded` | ✅ Done |
| 16 | `modules/performance/overview.md` | Dependency + business rule updated: `IProductivityAnalyticsService` composites agent data + `wms_productivity_snapshots`; WMS-optional fallback documented | ✅ Done |

---

## Clarifying Notes

**Re: WorkPulse Agent package quality**
The WorkPulse Agent is a custom-built MSIX package (Windows Service + MAUI tray app). It is **purpose-built for ONEVO**, not a third-party package. There was likely a prior discussion about an external monitoring SDK/package that was evaluated and rejected in favour of building custom. The current knowledge brain docs show the custom build architecture in full detail (`modules/agent-gateway/`). If you're asking whether an external monitoring SDK exists that you could use instead — there are options (Teramind SDK, Hubstaff SDK, etc.) but they don't offer the tight integration, privacy controls, or WMS correlation that the custom agent provides. The decision to build custom appears correct for this system.

**Re: Activity monitoring data for WMS**
The WorkPulse Agent data flows into the Discrepancy Engine which already compares against WMS task logs. This is working as designed. No changes needed here.

**Re: Development not started yet**
Confirmed — no code has been written. The knowledge brain fixes happen first, then the other team can build WMS against the defined bridge contracts.
