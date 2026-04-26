# App Catalog + Observed Applications — Architecture Plan

**Date:** 2026-04-26
**Status:** Planning
**Relates to:** [[docs/superpowers/plans/2026-04-23-developer-platform-architecture|Developer Platform Plan]]

---

## 1. Problem

The `app_allowlists` table stores `application_name varchar(100)` typed manually by HR admins. The desktop agent sends `application_name` as whatever Windows reports via `GetForegroundWindow` + process introspection. These two strings can differ:

- Admin types `"Chrome"` → Agent reports `"Google Chrome"` → No match → App wrongly flagged as unallowed
- Admin types `"Microsoft Teams"` → Agent reports `"Microsoft Teams (work or personal)"` → No match

Additionally, HR admins have no baseline to work from — they must type app names from memory before seeing what their employees actually use. This makes the initial allowlist configuration error-prone and incomplete.

---

## 2. Solution: Two-Tier App Catalog System

```
Tier 1: Global App Catalog  (OneVo devs manage via developer platform)
         → Pre-seeded: Chrome, Teams, Slack, Zoom, Office suite, VS Code...
         → is_public = true → visible to all HR admins across all tenants
         → process_name is the authoritative matching key — never mismatches

Tier 2: Observed Applications  (per tenant, auto-discovered from agent)
         → Custom ERP, legacy tools, org-specific software
         → Only visible to that tenant, never shared across tenants
         → Populated automatically as employees use their computers
```

HR admins build their allowlist by selecting from both tiers — unified search, no typing required. No name mismatch possible because `process_name` (the Windows exe name) is always used as the matching key.

---

## 3. New Tables

### `global_app_catalog` (shared_platform schema — no tenant_id, global)

Managed exclusively by OneVo devs via the developer platform.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `app_name` | `varchar(200)` | e.g., "Google Chrome" |
| `process_name` | `varchar(100)` | e.g., "chrome.exe" — authoritative matching key |
| `category` | `varchar(50)` | `browser`, `communication`, `development`, `office`, `design`, `productivity`, `other` |
| `publisher` | `varchar(200)` | e.g., "Google LLC" |
| `icon_url` | `varchar(500)` | For UI display |
| `is_public` | `boolean` | True = visible to all HR admins in catalog browser |
| `is_productive_default` | `boolean` | Default productivity classification |
| `created_by_id` | `uuid` | FK → dev_platform_accounts |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

**Index:** `process_name` UNIQUE — no duplicate apps in the catalog.

---

### `observed_applications` (configuration schema, per tenant)

Auto-populated by the ingest processor. Never written to by HR admins directly.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `application_name` | `varchar(200)` | Display name from agent |
| `process_name` | `varchar(100)` | Exe name — deduplication key |
| `global_catalog_id` | `uuid` | Auto-linked FK → global_app_catalog (nullable) |
| `first_seen_at` | `timestamptz` | |
| `last_seen_at` | `timestamptz` | Updated on every ingest that sees this app |
| `employee_count` | `int` | Unique employees who ran this app |
| `total_seconds_observed` | `bigint` | Cumulative usage time across all employees |
| `status` | `varchar(20)` | `pending` \| `added_to_allowlist` \| `dismissed` |

**Unique constraint:** `(tenant_id, process_name)` — one row per app per tenant, always. Ingest uses UPSERT.
**Index:** `(tenant_id, status, employee_count DESC)` — for the HR admin discovered apps list.

---

## 4. Modified Tables

### `app_allowlists` — three new columns

| New Column | Type | Notes |
|:-----------|:-----|:------|
| `process_name` | `varchar(100)` | Nullable — reliable matching key used by ingest processor |
| `source` | `varchar(20)` | `global_catalog` \| `tenant_observed` \| `manual` |
| `global_catalog_id` | `uuid` | Nullable FK → global_app_catalog |

**New unique constraint:** `(tenant_id, scope_type, COALESCE(scope_id, uuid_nil), process_name)` — same app cannot appear twice for the same scope.

All existing rows are backward-compatible — `process_name` nullable means no migration data work required.

---

## 5. Matching Priority (Ingest Processor)

Resolution order when writing `application_usage.is_allowed`:

```
Incoming: { application_name: "Google Chrome", process_name: "chrome.exe" }
  │
  ├─ Step 1: UPSERT observed_applications (tenant_id, process_name)
  │           Increment employee_count, update last_seen_at, total_seconds
  │           Auto-fill global_catalog_id if catalog has matching process_name
  │
  ├─ Step 2: Resolve is_allowed from app_allowlists
  │           Match by process_name (case-insensitive) → scope resolution
  │           Fallback: match by application_name (case-insensitive exact)
  │           No match → is_allowed = null
  │
  └─ Step 3: Write application_usage with resolved is_allowed
              is_allowed = null → PENDING, never triggers non_allowed_app rule
```

**Critical business rule:** `is_allowed = null` means unknown/unreviewed. The `non_allowed_app` exception rule evaluates ONLY on `is_allowed = false`. Unreviewed apps never trigger alerts — this protects against false positives during the discovery period.

---

## 6. Auto-Linking: Catalog ↔ Observed

When a OneVo dev adds an app to `global_app_catalog` with `process_name = "chrome.exe"`:
- A background job runs: `UPDATE observed_applications SET global_catalog_id = X WHERE process_name = 'chrome.exe'` — across all tenants automatically
- Going forward: the ingest processor auto-fills `global_catalog_id` on every upsert

Result: HR admins see catalog metadata (icon, publisher, category) enriched on top of their org's usage data, without any manual linking.

---

## 7. Developer Platform — Module 7: App Catalog Manager

Added to `2026-04-23-developer-platform-architecture.md` as Module 7.

OneVo dev team manages the global app catalog — adds apps, toggles `is_public`, updates `process_name` when Windows updates change exe names.

**Frontend pages:**
```
console.onevo.io/app-catalog/
├── page.tsx              # All catalog apps — sortable, filterable table
├── new/page.tsx          # Add app form (name, process_name, category, publisher, icon)
├── [id]/page.tsx         # Edit app, toggle is_public
└── uncatalogued/page.tsx # Apps seen across many tenants not yet in catalog — bulk approve
```

**Admin API endpoints:**
```
GET    /admin/v1/app-catalog               → List catalog apps (filter: is_public, category)
POST   /admin/v1/app-catalog               → Add new app to catalog
PATCH  /admin/v1/app-catalog/{id}          → Update (name, process_name, is_public, category)
DELETE /admin/v1/app-catalog/{id}          → Remove from catalog
GET    /admin/v1/app-catalog/uncatalogued  → Apps in observed_applications not in catalog, sorted by tenant_count DESC
POST   /admin/v1/app-catalog/bulk-approve  → Add multiple uncatalogued apps to catalog at once
```

---

## 8. HR Admin Frontend — Allowlist Config UI

Located at `/settings/monitoring/allowlist/`.

**Three tabs:**

| Tab | Source | Sorted by |
|:----|:-------|:----------|
| Current Allowlist | `app_allowlists` for this tenant | Status then app name |
| Browse App Catalog | `global_app_catalog` where `is_public = true` | Category then app name |
| Discovered in Your Org | `observed_applications` where `status = pending` | `employee_count DESC` |

**Unified search** — one search box queries catalog + discovered simultaneously, merges by `process_name`. Same app in both sources = one result card.

**Deduplication in UI:**
- Apps already in the allowlist show a status badge on their card — not duplicated
- Same `process_name` in both catalog and discovered → one merged card (catalog provides icon/metadata, observed provides usage stats)
- Dismissed apps hidden from discovered tab, recoverable via "Show dismissed" toggle

**Add to allowlist flow:**
1. Find app in any tab or search
2. Click card → drawer: Allow or Block? Scope: All Employees / Role / Specific Employee
3. Confirm → `POST /api/v1/settings/monitoring/allowlist` (process_name + source auto-filled)
4. `observed_applications.status` flips to `added_to_allowlist`

**API endpoints:**
```
GET    /api/v1/settings/monitoring/allowlist               → Current allowlist
GET    /api/v1/settings/monitoring/allowlist/catalog       → Global catalog (is_public = true)
GET    /api/v1/settings/monitoring/allowlist/discovered    → Tenant observed apps (status = pending)
GET    /api/v1/settings/monitoring/allowlist/search?q=     → Unified search across both sources
POST   /api/v1/settings/monitoring/allowlist               → Add app to allowlist
PUT    /api/v1/settings/monitoring/allowlist/{id}          → Update (is_allowed, scope)
DELETE /api/v1/settings/monitoring/allowlist/{id}          → Remove from allowlist
PATCH  /api/v1/settings/monitoring/allowlist/discovered/{id}/dismiss → Dismiss from discovered
```

---

## 9. Recommended Onboarding Sequence

```
1. Enable application_tracking in Monitoring Toggles
2. Set allowlist_mode = blocklist   ← safe default, no false alerts during discovery
3. Deploy agent to pilot group (20–30% of employees)
4. Wait 5–7 days → observed_applications populates with real org data
5. HR admin reviews "Discovered in Your Org" + Browse App Catalog → builds allowlist
6. Switch allowlist_mode = allowlist
7. Create non_allowed_app exception rule (set violation_threshold_minutes)
8. Full agent rollout to remaining employees
```

Step 4 does not require ALL employees to be onboarded — even 20% will surface 90%+ of the org's app catalog. New apps from late-arriving employees appear in the discovered tab incrementally.

---

## 10. Initial Global Catalog Seed (~40 apps at launch)

OneVo dev team seeds these before any tenant goes live:

| Category | Apps |
|:---------|:-----|
| Browser | Google Chrome (`chrome.exe`), Firefox (`firefox.exe`), Microsoft Edge (`msedge.exe`) |
| Communication | Microsoft Teams (`ms-teams.exe`), Slack (`slack.exe`), Zoom (`Zoom.exe`), Google Meet (browser), Discord (`Discord.exe`), Outlook (`OUTLOOK.EXE`), Skype (`Skype.exe`) |
| Office | Word (`WINWORD.EXE`), Excel (`EXCEL.EXE`), PowerPoint (`POWERPNT.EXE`), OneNote (`ONENOTE.EXE`) |
| Development | VS Code (`Code.exe`), Visual Studio (`devenv.exe`), IntelliJ IDEA (`idea64.exe`), PyCharm (`pycharm64.exe`), Docker Desktop (`Docker Desktop.exe`), Windows Terminal (`WindowsTerminal.exe`) |
| Design | Figma (`Figma.exe`), Adobe Photoshop (`Photoshop.exe`), Adobe Illustrator (`Illustrator.exe`) |
| Productivity | Notion (`Notion.exe`), Trello (browser), Asana (browser), Jira (browser) |

---

## 11. Schema Catalog Impact

| Change | Delta |
|:-------|:------|
| `global_app_catalog` — new table in shared_platform | +1 |
| `observed_applications` — new table in configuration | +1 |
| `app_allowlists` — 3 new columns, no new table | 0 |
| **Total new tables** | **+2** |

Update `database/schema-catalog.md` total count accordingly.

---

## 12. Build Sequence

### Phase 1 — Core matching fix
1. Add `process_name` to agent `app_usage` batch item (protocol + `AppUsageRecord.cs`)
2. Add `process_name`, `source`, `global_catalog_id` columns to `app_allowlists` (EF migration)
3. Add `observed_applications` table (EF migration)
4. Update ingest processor: UPSERT `observed_applications` + auto-link catalog by `process_name`
5. Update exception engine: `is_allowed = null` → skip, never alert

### Phase 2 — Global catalog + UI
1. Add `global_app_catalog` table (EF migration)
2. Seed initial ~40 apps
3. Build App Catalog Manager in developer console (Module 7)
4. Build HR admin allowlist config UI — 3-tab layout + unified search + drawer flow
5. Wire up all `/api/v1/settings/monitoring/allowlist/*` endpoints

### Phase 3 — Auto-linking + enhancements
1. Background job: backfill `observed_applications.global_catalog_id` for existing rows
2. "Uncatalogued apps" view in dev console (bulk approve flow)
3. Historical `application_usage.is_allowed` backfill when new allowlist entries added

---

## Related

- [[database/schemas/configuration|Configuration Schema]] — `app_allowlists` + `observed_applications`
- [[database/schemas/shared-platform|Shared Platform Schema]] — `global_app_catalog`
- [[modules/agent-gateway/agent-server-protocol|Agent Server Protocol]] — `process_name` in `app_usage`
- [[modules/agent-gateway/data-ingestion/end-to-end-logic|Data Ingestion Logic]] — UPSERT observed_applications
- [[modules/exception-engine/evaluation-engine/overview|Evaluation Engine]] — `is_allowed = null` business rule
- [[modules/exception-engine/exception-rules/overview|Exception Rules]] — `non_allowed_app` rule type
- [[docs/superpowers/plans/2026-04-23-developer-platform-architecture|Developer Platform Plan]] — Module 7
- [[Userflow/Configuration/app-allowlist-setup|App Allowlist Setup Userflow]]
