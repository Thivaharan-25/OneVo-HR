# Global Policies End-to-End Logic

## Policy Catalog

The six fixed policy keys and what they map to:

| Policy Key | Type | Default | Table Column Written |
|---|---|---|---|
| `auth.mfa_required_default` | boolean | `false` | `tenant_auth_policies.mfa_required` |
| `auth.google_login_allowed_default` | boolean | `true` | `tenant_auth_policies.google_login_enabled` |
| `auth.password_login_allowed_default` | boolean | `true` | `tenant_auth_policies.password_login_enabled` |
| `auth.google_email_mismatch_allowed_default` | boolean | `false` | `tenant_auth_policies.invite_google_email_mismatch_allowed` |
| `auth.failed_login_lockout_threshold` | integer | `5` | Read by AuthService from `system_settings` at login — no per-tenant column |
| `auth.failed_login_lockout_minutes` | integer | `15` | Read by AuthService from `system_settings` at login — no per-tenant column |

`auth.failed_login_lockout_threshold` and `auth.failed_login_lockout_minutes` are platform-wide runtime values read from `system_settings` directly by AuthService. They do not have per-tenant overrides. Publishing a new value for these takes effect immediately across all tenants — no propagation step applies.

---

## Publish Flow (Future Tenants)

1. Operator opens System Config -> Global Policies.
2. Frontend loads all six policy keys with current published values — `GET /admin/v1/global-policies`.
3. Operator selects a policy and edits the default value — saves as draft. Published value unchanged.
4. Frontend calls `GET /admin/v1/global-policies/{id}/tenant-impact`.
   - Backend counts tenants whose `tenant_auth_policies` value for this field currently matches the published default (i.e. no explicit override set).
   - Returns `{ "affected_tenants": N, "unaffected_tenants": M }`.
5. Operator reviews impact, enters mandatory audit reason, and confirms.
6. Frontend calls `POST /admin/v1/global-policies/{id}/publish { "reason": "..." }`.
7. Backend writes new default value to `system_settings`. Audit log entry written with previous default, new default, reason, affected_tenants count, actor.
8. All future tenant provisioning seeds `tenant_auth_policies` with the new default.

---

## Propagate to Existing Tenants

Propagation is a separate explicit action available after publish. It is never triggered automatically.

1. Operator clicks **Propagate** on the published policy.
2. Backend calculates affected count — tenants whose current `tenant_auth_policies` value for this field does NOT equal the current published default. These are tenants that have not yet received the new value.
3. Frontend shows: affected count, skipped count (explicit overrides), and prompts for mandatory audit reason.
4. Operator confirms.
5. Frontend calls `POST /admin/v1/global-policies/{id}/propagate { "reason": "..." }`.
6. Backend queues a background job.
7. Job iterates affected tenants, updates `tenant_auth_policies` for each, records per-tenant result.
8. Final counts (`applied_count`, `skipped_count`, `failed_count`) written to audit log. Summary visible in Platform Health.

Note: `auth.failed_login_lockout_threshold` and `auth.failed_login_lockout_minutes` have no propagation step — they are read from `system_settings` at runtime and apply immediately on publish.

---

## How Provisioning Uses These Defaults

During tenant provisioning, `CreateTenantCommandHandler` inserts one `tenant_auth_policies` row for the new tenant.

**Current state:** The handler creates `TenantAuthPolicy` using C# entity property defaults (hardcoded). It does not yet read from `system_settings`.

**Required change:** `CreateTenantCommandHandler` must be updated to read the four `tenant_auth_policies`-mapped policy keys from `system_settings` before inserting the row, so that published defaults here take effect for newly provisioned tenants.

**Lockout keys:** `AuthService` currently uses hardcoded values for failed login lockout. It must be updated to read `auth.failed_login_lockout_threshold` and `auth.failed_login_lockout_minutes` from `system_settings` at login time.

After provisioning, platform operators can view and override per-tenant values from Tenant Management → Policies tab.

---

## APIs

| Method | Route | Purpose | Permission |
|---|---|---|---|
| GET | `/admin/v1/global-policies` | List all six policies with published defaults and draft values. Supports `?tenant_id={id}` — returns same data filtered to show this tenant's current value alongside the global default (used by Tenant Management -> Policies tab) | `platform.system_config.read` |
| PATCH | `/admin/v1/global-policies/{id}` | Update draft value for a policy | `platform.system_config.manage` |
| GET | `/admin/v1/global-policies/{id}/tenant-impact` | Count tenants affected by publishing the current draft | `platform.system_config.read` |
| POST | `/admin/v1/global-policies/{id}/publish` | Publish draft as new default | `platform.system_config.manage` |
| POST | `/admin/v1/global-policies/{id}/propagate` | Propagate published value to existing tenants without explicit override | `platform.system_config.manage` |
| GET | `/admin/v1/global-policies/{id}/history` | View publish history for a policy key | `platform.system_config.read` |

There is no `POST /admin/v1/global-policies` (create) and no `DELETE`. The six keys are seeded by ONEVO and are always present.

---

## Failure Handling

- Propagation is idempotent — re-running the background job for the same publish event produces the same result without double-applying values or duplicate audit entries.
- Per-tenant propagation failures are recorded individually in the audit log. A failure on one tenant does not roll back others.
- Propagation result summary (`applied_count`, `skipped_count`, `failed_count`) is visible in Platform Health in Phase 1; standalone Background Jobs drill-down is Phase 2.
