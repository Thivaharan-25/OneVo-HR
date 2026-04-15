# WMS Tenant Provisioning

**Module:** Shared Platform
**Phase:** 1
**Purpose:** Define how a tenant connects ONEVO to WorkManage Pro — covering purchasing flows, account provisioning, bridge key generation, and role mapping.

---

## Purchasing Model

ONEVO and WorkManage Pro are sold as separate products. A customer can:

1. **Buy ONEVO only** — no WMS connection. Bridges remain unused.
2. **Buy WorkManage Pro only** — no ONEVO connection. Not our concern.
3. **Buy both together** — auto-provisioning flow (see below).
4. **Buy separately, link later** — manual connection flow (see below).

Both ONEVO and WMS are multi-tenant SaaS platforms. Each tenant in ONEVO is linked to at most one WMS tenant via the `wms_tenant_links` table.

---

## Flow A — Buying Both Together (Recommended)

When a customer purchases the **Full Suite** (ONEVO + WorkManage Pro) from the ONEVO sales team or self-serve checkout:

```
1. Customer completes ONEVO onboarding wizard
   └── Selects "Full Suite" or "HR + Work Management" plan

2. ONEVO creates tenant account
   └── tenant_subscriptions record created (includes wms_entitled: true)

3. ONEVO auto-generates a bridge API key
   └── bridge_api_keys row: name = "WorkManage Pro", scopes = ["bridges:read", "bridges:write"]
   └── Key shown ONCE to admin during onboarding — must be copied to WMS

4. Admin sees "Connect WorkManage Pro" step in onboarding wizard
   └── Displays: bridge API key + setup instructions for WMS side
   └── Admin pastes key into WMS Settings → ONEVO Integration

5. WMS (other team) registers the key on their side
   └── WMS calls People Sync bridge (GET /api/v1/bridges/people-sync/employees) to import employees
   └── WMS displays "X employees imported from ONEVO"

6. ONEVO creates wms_tenant_links record
   └── sync_people: true, sync_availability: true, sync_work_activity: true
   └── sync_productivity_metrics: false (Phase 2 — enabled when tenant upgrades)
   └── sync_skills: false (Phase 2)
   └── linked_at = now()
```

**Auto-provisioning completes when:** WMS makes its first successful People Sync call, which triggers `wms_tenant_links.first_sync_at` to be set.

---

## Flow B — Buying Separately, Linking Later

When a customer already has ONEVO and later purchases WorkManage Pro (or vice versa):

```
Admin navigates to: ONEVO Settings → Integrations → WorkManage Pro

Step 1: Generate bridge key
  → POST /api/v1/settings/bridge-keys
  → Body: { "name": "WorkManage Pro", "scopes": ["bridges:read", "bridges:write"] }
  → Response: { "key": "<plaintext — shown once>", "key_prefix": "wmp_k8x2", "id": "uuid" }
  → Admin copies key to WMS

Step 2: ONEVO creates wms_tenant_links record
  → linked_at = now(), sync toggles default OFF (admin enables each bridge individually)

Step 3: Admin enables bridges one by one
  → "Enable People Sync" toggle → sync_people: true
  → "Enable Availability" toggle → sync_availability: true
  → "Enable Work Activity" toggle → sync_work_activity: true
```

---

## Role Mapping

When an employee is promoted or their role changes in ONEVO, the WMS needs to know what permission level to assign them. This is configured via the `wms_role_mappings` table.

### How it works

```
ONEVO Role (e.g. "Team Lead") ──→ wms_role_identifier (e.g. "manager")
```

The `wms_role_identifier` is an opaque string that the WMS team defines — ONEVO just stores and passes it through. The WMS team tells ONEVO admins what strings to use.

### Configuration UI

`Settings → Integrations → WorkManage Pro → Role Mappings`

| ONEVO Role | WMS Permission Set |
|:-----------|:-----------------|
| HR Admin | `admin` |
| Department Manager | `manager` |
| Team Lead | `manager` |
| Standard Employee | `employee` |
| Contractor | `contractor` |
| CEO / Director | `admin` |

Admin can add/edit/delete mappings. Unmapped roles default to `employee` in the bridge response.

### Automatic sync on role change

When `EmployeePromoted` or `EmployeeTransferred` domain event fires:
1. ONEVO looks up new role → `wms_role_mappings` → new `wms_role_identifier`
2. Next People Sync delta call from WMS picks up the updated `wms_role_identifier`
3. WMS updates the employee's permission level accordingly

No push notification to WMS — WMS is expected to poll People Sync at least hourly.

---

## Bridge Key Management

### Generating a key

```
POST /api/v1/settings/bridge-keys
Permission: settings:admin

Body:
{
  "name": "WorkManage Pro",
  "scopes": ["bridges:read", "bridges:write"],
  "expires_at": null
}

Response 201:
{
  "id": "uuid",
  "name": "WorkManage Pro",
  "key": "wmp_k8x2_...<full key shown ONCE>",
  "key_prefix": "wmp_k8x2",
  "scopes": ["bridges:read", "bridges:write"],
  "created_at": "2026-04-15T10:00:00Z"
}
```

> The full key value is only returned on creation. It is stored hashed in `bridge_api_keys`. If lost, the admin must revoke and generate a new key.

### Listing keys

```
GET /api/v1/settings/bridge-keys
Permission: settings:admin

Response:
{
  "keys": [
    {
      "id": "uuid",
      "name": "WorkManage Pro",
      "key_prefix": "wmp_k8x2",
      "scopes": ["bridges:read", "bridges:write"],
      "last_used_at": "2026-04-15T08:30:00Z",
      "expires_at": null,
      "revoked_at": null,
      "created_at": "2026-04-01T10:00:00Z"
    }
  ]
}
```

### Revoking a key

```
DELETE /api/v1/settings/bridge-keys/{id}
Permission: settings:admin

Response 200:
{ "revoked": true, "revoked_at": "2026-04-15T10:05:00Z" }
```

Revocation takes effect immediately. Any subsequent WMS request using this key returns `401 BRIDGE_KEY_INVALID`.

---

## Sync Toggles

Each bridge can be independently enabled/disabled per tenant from `Settings → Integrations → WorkManage Pro`:

| Toggle | Controls | Default (Full Suite) | Default (Manual link) |
|:-------|:---------|:---------------------|:----------------------|
| People Sync | `sync_people` | ON | OFF |
| Availability | `sync_availability` | ON | OFF |
| Work Activity | `sync_work_activity` | ON | OFF |
| Productivity Metrics | `sync_productivity_metrics` | OFF (Phase 2) | OFF |
| Skills | `sync_skills` | OFF (Phase 2) | OFF |

Disabling a toggle does not delete existing data — it stops new data from being accepted on that bridge endpoint (returns `403 BRIDGE_DISABLED`).

---

## Database Tables

### `wms_tenant_links`

Links an ONEVO tenant to a WMS tenant. One row per tenant (max one WMS per ONEVO tenant).

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants (UNIQUE) |
| `wms_tenant_id` | `varchar(100)` | WMS-side tenant ID (opaque) |
| `sync_people` | `bool` | People Sync bridge enabled |
| `sync_availability` | `bool` | Availability bridge enabled |
| `sync_work_activity` | `bool` | Work Activity bridge enabled |
| `sync_productivity_metrics` | `bool` | Productivity Metrics bridge enabled (Phase 2) |
| `sync_skills` | `bool` | Skills bridge enabled (Phase 2) |
| `linked_at` | `timestamptz` | When link was established |
| `first_sync_at` | `timestamptz` | nullable — when WMS made its first successful sync call |
| `last_sync_at` | `timestamptz` | nullable — most recent successful sync call timestamp |
| `created_at` | `timestamptz` | |

### `wms_role_mappings`

Maps ONEVO roles to WMS permission identifiers.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `role_id` | `uuid` | FK → roles |
| `wms_role_identifier` | `varchar(50)` | Opaque string defined by WMS team (e.g. `manager`, `employee`) |
| `created_at` | `timestamptz` | |

**Indexes:** `(tenant_id, role_id)` UNIQUE

### `bridge_api_keys`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `name` | `varchar(100)` | Human label e.g. "WorkManage Pro" |
| `key_hash` | `varchar` | bcrypt hash of the full key |
| `key_prefix` | `varchar(8)` | First 8 chars for display in Settings UI |
| `scopes` | `varchar[]` | `["bridges:read", "bridges:write"]` |
| `last_used_at` | `timestamptz` | nullable |
| `expires_at` | `timestamptz` | nullable |
| `created_by_id` | `uuid` | FK → users |
| `created_at` | `timestamptz` | |
| `revoked_at` | `timestamptz` | nullable — set on DELETE |

---

## Related

- [[backend/bridge-api-contracts|Bridge API Contracts]] — Full request/response schemas for all bridges
- [[backend/external-integrations|External Integrations]] — Bridge endpoint registry
- [[modules/shared-platform/chatbot-api-integration|Chatbot API Integration]] — Semantic Kernel chatbot auth (separate from bridge keys)
- [[current-focus/WMS-bridge-integration|WMS Bridge Integration]] — Implementation task plan
- [[database/schemas/shared-platform|Shared Platform Schema]] — All 3 tables defined here
