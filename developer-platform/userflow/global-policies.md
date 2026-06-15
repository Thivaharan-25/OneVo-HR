# Global Policies Userflow

## Actor

Platform policy manager (`platform.system_config.read` to view, `platform.system_config.manage` to edit, publish, and propagate).

---

## List Page - System Config -> Global Policies

Shows all six auth/security policy keys in a table. No create button — the keys are fixed.

| Column | Description |
|---|---|
| Policy | Display name (e.g. "MFA Required Default") |
| Key | Machine-readable key (e.g. `auth.mfa_required_default`) |
| Type | `boolean` or `integer` |
| Published Default | Current live default value |
| Draft Value | Pending unpublished value — shown only if an unpublished draft exists |
| Last Published | Timestamp and actor of the most recent publish |

Operator clicks any row to open the detail/edit view.

---

## Detail / Edit View

### Fields shown

| Field | Editable | Notes |
|---|---|---|
| Policy Key | No | Machine-readable identifier |
| Display Name | No | Human label |
| Description | No | Explains what the policy controls and which tenant setting it seeds |
| Current Published Default | No | The live value new tenants are provisioned with |
| New Default Value | Yes | Toggle for boolean; number input for integer. Integer policies show allowed range. |

### Change History

Table below the edit form showing previous publish events:

| Column | Notes |
|---|---|
| Date | Publish timestamp |
| Actor | Platform account that published |
| Previous Value | Value before this publish |
| New Value | Value after this publish |
| Reason | Mandatory audit reason entered by operator |
| Tenants Affected | Count at time of publish |

---

## Step 1 — Edit Draft

Operator changes the **New Default Value** field and saves. This creates a draft — the published default is not changed yet. The list page shows the Draft Value column populated for this policy.

**API:** `PATCH /admin/v1/global-policies/{id}` `{ "draft_value": ... }`

---

## Step 2 — Preview Impact

Operator clicks **Preview Impact**.

**API:** `GET /admin/v1/global-policies/{id}/tenant-impact`

Displays:
- **X tenants will receive this change** — tenants whose current auth policy value matches the existing published default (no explicit override set). These tenants would be updated if the operator propagates after publishing.
- **Y tenants are unaffected** — tenants that have an explicit override and will not be changed regardless.

---

## Step 3 — Publish

Operator clicks **Publish**.

- Mandatory audit reason field (free text, required)
- Confirmation dialog: "Publishing updates the platform default. New tenants will be provisioned with [new value]. [X] existing tenants without an explicit override will not be changed until you propagate."
- On confirm: `POST /admin/v1/global-policies/{id}/publish { "reason": "..." }`
- Success: list page shows updated Published Default. Draft Value cleared.

Publishing alone does not touch any existing tenant's auth policy.

---

## Step 4 — Propagate to Existing Tenants (optional, separate action)

Available after publish via a **Propagate to existing tenants** button on the detail view.

1. Backend recalculates: tenants whose auth policy value still matches the **previous** published default.
2. Operator sees:
   - "**[N] tenants** will be updated to [new value]"
   - "**[M] tenants** have explicit overrides and will not be changed"
3. Operator enters mandatory audit reason.
4. Operator confirms.
5. `POST /admin/v1/global-policies/{id}/propagate { "reason": "..." }`
6. Background job runs. Completion summary (applied, skipped, failed counts) appears in Platform Health.

---

## Error States

| Scenario | What the operator sees |
|---|---|
| Publish without audit reason | Form validation: "Reason is required" |
| Propagate without audit reason | Form validation: "Reason is required" |
| Propagation job partially fails | Platform Health shows: "Global policy propagation completed with [N] failures" — drill down shows per-tenant results |

---

## APIs Used

- `GET /admin/v1/global-policies`
- `PATCH /admin/v1/global-policies/{id}`
- `GET /admin/v1/global-policies/{id}/tenant-impact`
- `GET /admin/v1/global-policies/{id}/history`
- `POST /admin/v1/global-policies/{id}/publish`
- `POST /admin/v1/global-policies/{id}/propagate`

---

## Rules

- Policies cannot be created or deleted — only the six fixed auth keys exist
- Publishing requires a reason — no silent default changes
- Propagation is always a separate explicit action after publishing — publishing never auto-propagates
- Tenant-specific overrides in `tenant_auth_policies` are never overwritten by publish or propagate
- `auth.failed_login_lockout_threshold` and `auth.failed_login_lockout_minutes` have no propagation step — they apply platform-wide immediately on publish
