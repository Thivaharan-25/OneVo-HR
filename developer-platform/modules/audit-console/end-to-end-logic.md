# Audit Console — End-to-End Logic

## Purpose

The Audit Console is the cross-tenant, read-only view of all audit log events across the entire ONEVO platform. It covers actions by tenant users, platform admins, and system processes. All queries are themselves audit-logged. No mutations happen from this screen.

**Route:** `/security/audit-logs`
**Permission:** `platform.audit.read`

---

## Screen Layout

Single main view — no sub-tabs. Full-width audit log table with a comprehensive filter bar at the top and export controls in the header.

---

## Page Header

| Element | Value |
|---|---|
| Title | "Audit Console" |
| Subtitle | "Cross-tenant read-only audit log. All queries are logged." |
| Export button | "Export" dropdown — CSV / JSON |
| Auto-refresh toggle | Toggle to auto-refresh every 30 seconds |
| Time range | Quick selects: Last 1 Hour / Last 24 Hours / Last 7 Days / Last 30 Days / Custom Range (date-time pickers) |

---

## Filter Bar

All filters are applied simultaneously. The filter bar is always visible at the top — it does not collapse.

| Filter | Label | Type | Options / Behavior |
|---|---|---|---|
| Search | (magnifier icon) | Text input | Full-text search across `action_description`, `resource_name`, `actor_name`. Debounced 400ms. |
| Date From | "From" | DateTime picker | ISO datetime; defaults to 24 hours ago |
| Date To | "To" | DateTime picker | ISO datetime; defaults to now |
| Tenant | "Tenant" | Autocomplete | Search by company name or tenant code. Select "Platform-level" for platform admin and system events not scoped to a tenant. |
| Actor Type | "Actor Type" | Dropdown | All / Tenant User / Platform Admin / System |
| Actor | "Actor" | Text input | Filter by actor name or email — partial match |
| Action Category | "Action" | Dropdown | All / Auth / Users / Billing / Settings / Devices / Integrations / Security / Modules / Roles / Data / Templates |
| Resource Type | "Resource" | Dropdown | All / Tenant / User / Role / Invoice / Device / Integration / Feature Flag / Module / Template / Gateway / AI Config / Alert / Session |
| Result | "Result" | Dropdown | All / Success / Failed |
| IP Address | "IP" | Text input | Exact or prefix match on source IP |
| Reset Filters button | — | Button | Clears all filters to defaults |

**Active filter count badge:** Shows how many non-default filters are active (e.g., "4 filters active").

---

## Audit Log Table

**API:** `GET /admin/v1/audit-logs?{filters}&page={n}&per_page={n}&sort=created_at&order=desc`

**Default sort:** `created_at` descending (newest first).
**Rows per page:** 25 (options: 25, 50, 100).
**Max rows returned per request:** 1,000 (for UI display; exports have no row limit).

### Columns

| Column | Label | Description | Width | Sortable |
|---|---|---|---|---|
| Timestamp | "Time" | Full datetime: `2026-05-17 10:24:33 AM` — on hover shows milliseconds and timezone | 175px | Yes, default |
| Actor | "Actor" | Name + email, with type badge below: Tenant User (blue) / Platform Admin (purple) / System (gray). Linked to actor detail where applicable. | 200px | No |
| Action | "Action" | Human-readable action description, e.g. "Tenant suspended", "Invoice marked paid", "Feature flag updated". Below it in smaller text: the machine-readable `action_code`, e.g. `tenant.suspended` | Flexible | No |
| Resource | "Resource" | Entity type + name, e.g. "Tenant: TechNova Solutions", "Invoice: INV-TEN-000001-202505-001". Linked to the resource detail page where it still exists. | 200px | No |
| Tenant | "Tenant" | Company name (linked to tenant detail) or "Platform" for non-tenant events | 160px | Yes |
| IP Address | "IP" | Source IP address. "System" for automated jobs. | 130px | No |
| Result | "Result" | Success (green ✓) / Failed (red ✗) badge | 80px | Yes |

### Row Expand

Clicking any row expands it inline to show the full audit detail:

| Field | Value |
|---|---|
| Action Code | Machine-readable, e.g. `tenant.suspended` |
| Actor ID | UUID of the actor |
| Target Resource ID | UUID of the affected entity |
| Previous State | JSON snapshot of resource state before the action (redacted for sensitive fields) |
| New State | JSON snapshot after the action (redacted) |
| Request ID | Correlation ID linking this audit entry to backend logs |
| User Agent | Browser/client user agent string |
| Session ID | Platform admin session ID (for platform admin actors) |
| Metadata | Any additional context stored at log time (e.g., suspension reason, override reason) |

**Sensitive field redaction:** Fields containing API keys, passwords, tokens, or secrets are replaced with `[REDACTED]` in both Previous State and New State snapshots. Raw values are never stored in the audit log.

---

## Action Code Catalog

Every audit entry has a machine-readable `action_code`. This is the full catalog:

### Auth / Session

| Action Code | Description |
|---|---|
| `auth.login.success` | Platform admin logged in successfully |
| `auth.login.failed` | Login attempt failed (wrong credentials or account inactive) |
| `auth.session.revoked` | Session manually revoked by another admin |
| `auth.session.expired` | Session expired naturally |
| `auth.google_callback.success` | Google OAuth callback succeeded |
| `tenant.user.login.success` | Tenant user logged in |
| `tenant.user.login.failed` | Tenant user login failed |
| `tenant.impersonated` | Platform admin issued impersonation token |

### Tenant Lifecycle

| Action Code | Description |
|---|---|
| `tenant.created` | Provisioning draft created (Step 1 wizard) |
| `tenant.activated` | Provisioning tenant activated |
| `tenant.suspended` | Tenant manually suspended |
| `tenant.unsuspended` | Tenant unsuspended |
| `tenant.cancelled` | Tenant cancelled |
| `tenant.auto_suspended_dunning` | Tenant auto-suspended by dunning job |
| `tenant.invite_sent` | Owner invite email sent |
| `tenant.settings_updated` | Tenant settings changed |

### Billing / Commercial

| Action Code | Description |
|---|---|
| `subscription.assigned` | Subscription plan assigned to tenant |
| `subscription.overridden` | Post-activation subscription override applied |
| `invoice.generated` | Invoice created by billing job |
| `invoice.paid` | Invoice marked paid (gateway or manual) |
| `invoice.manually_marked_paid` | Manual payment recorded by platform admin |
| `invoice.voided` | Invoice voided |
| `payment.failed` | Gateway payment attempt failed |
| `payment.gateway.created` | New gateway configuration saved |
| `payment.gateway.secrets_rotated` | Gateway credentials rotated |

### Module & Feature Flags

| Action Code | Description |
|---|---|
| `module.entitlement.updated` | Module entitlement state changed for tenant |
| `module.runtime_disabled` | Module disabled by operator via Feature Flag Manager |
| `module.runtime_enabled` | Module re-enabled by operator |
| `feature_flag.created` | New feature flag created |
| `feature_flag.default_changed` | Flag global default changed |
| `feature_flag.tenant_override_set` | Per-tenant flag override set |
| `feature_flag.tenant_override_removed` | Per-tenant override removed |

### Roles & Permissions

| Action Code | Description |
|---|---|
| `role_template.created` | New role template created |
| `role_template.updated` | Template edited (new version) |
| `role_template.applied` | Template applied to tenant |
| `tenant.role.created` | Tenant-specific role created |
| `tenant.role.permissions_updated` | Tenant role permission set changed |
| `tenant.role.deleted` | Tenant role deleted |

### Security & Alerts

| Action Code | Description |
|---|---|
| `alert.created` | Platform alert raised by detection pathway |
| `alert.acknowledged` | Alert acknowledged by platform admin |
| `alert.resolved` | Alert resolved by platform admin |
| `alert.auto_resolved` | Alert auto-resolved by background job |
| `audit_log.queried` | Audit Console accessed (every query logged) |
| `audit_log.exported` | Audit log export initiated |

### AI & Integrations

| Action Code | Description |
|---|---|
| `system_config.ai_key_updated` | Global AI provider key set or rotated |
| `tenant.ai_override_set` | Per-tenant AI key override set |
| `tenant.ai_override_removed` | Per-tenant AI override removed |
| `oauth_app.created` | OAuth app registration created |
| `oauth_app.secrets_rotated` | OAuth app secret rotated |
| `integration_catalog.created` | New integration entry created |
| `integration_catalog.updated` | Integration entry edited |
| `module_integration.linked` | Integration linked to module |
| `module_integration.unlinked` | Integration unlinked from module |
| `tenant.integration.connected` | Tenant user connected an integration (OAuth completed) |
| `tenant.integration.disconnected` | Integration disconnected for tenant |

---

## Export — Full Specification

### Export Triggers

- Click "Export" dropdown in the page header → select format
- Current filters are applied to the export — what you see is what you export
- No row limit on exports (unlike the UI display limit of 1,000 rows per request)

### Export Formats

#### CSV Export

**Fields included:**

| CSV Column | Source Field |
|---|---|
| `timestamp` | `created_at` in ISO 8601 format |
| `actor_type` | `Tenant User`, `Platform Admin`, or `System` |
| `actor_name` | Full name or system process name |
| `actor_email` | Email if applicable |
| `actor_id` | UUID |
| `action_code` | Machine-readable action code |
| `action_description` | Human-readable description |
| `resource_type` | Entity type |
| `resource_name` | Entity display name |
| `resource_id` | UUID |
| `tenant_name` | Company name or `Platform` |
| `tenant_id` | UUID |
| `result` | `success` or `failed` |
| `ip_address` | Source IP |
| `metadata` | JSON string of additional context |

**Encoding:** UTF-8 with BOM (for Excel compatibility).
**Line endings:** CRLF.
**Quote character:** `"` (double-quote).

#### JSON Export

Array of objects with the same fields as CSV plus `previous_state` and `new_state` snapshots (with sensitive fields redacted).

### Export Size and Async Behaviour

| Export Size | Behaviour |
|---|---|
| < 10,000 rows | Synchronous — file download starts immediately |
| 10,000 – 100,000 rows | Async — job queued; operator receives a download link via email (Resend) when ready. Download link expires in 24 hours. |
| > 100,000 rows | Blocked in UI — operator must narrow filters. Error: "Export too large — apply more specific filters to reduce below 100,000 rows." |

**API:** `POST /admin/v1/audit-logs/export`

```json
{
  "format": "csv",
  "filters": {
    "tenant_id": "a3f1c...",
    "from": "2026-05-01T00:00:00Z",
    "to": "2026-05-17T23:59:59Z",
    "action_category": "billing"
  }
}
```

**Synchronous response (< 10,000 rows):**
```
HTTP 200
Content-Type: text/csv
Content-Disposition: attachment; filename="audit-export-2026-05-17.csv"
[file content]
```

**Async response (>= 10,000 rows):**
```json
{
  "export_job_id": "job-uuid",
  "estimated_rows": 42000,
  "status": "queued",
  "notification": "Download link will be sent to engineer@onevo.io when ready."
}
```

**Audit log entry for every export:** `action = 'audit_log.exported'`, actor, filters applied, format, row count, export_job_id.

---

## Retention Rules

| Data Category | Retention Period | After Retention |
|---|---|---|
| Standard audit events | 2 years | Archived to cold storage (not queryable via console; available on request) |
| Security-category events (`action_category = 'security'`) | 5 years | Same archival |
| Billing events | 7 years (legal requirement) | Same archival |
| Platform admin session logs | 1 year | Deleted |
| Audit log exports (async download links) | 24 hours | Download link expires; file deleted from storage |

**Query window:** Audit Console only queries events within the retention period that are in hot storage. Events in cold storage are not queryable from the console and require an engineering request.

**Deletion rule:** Audit log entries are never deleted within their retention period. They are append-only. If a tenant is cancelled, their audit events remain for the full retention period.

---

## APIs — Full Catalog

| Method | Route | Purpose | Permission |
|---|---|---|---|
| GET | `/admin/v1/audit-logs` | Query audit logs with filters | `platform.audit.read` |
| GET | `/admin/v1/audit-logs/{id}` | Single audit entry full detail | `platform.audit.read` |
| POST | `/admin/v1/audit-logs/export` | Export filtered log (CSV or JSON) | `platform.audit.export` |
| GET | `/admin/v1/audit-logs/export/{jobId}` | Check async export job status | `platform.audit.export` |
| GET | `/admin/v1/tenants/{id}/audit` | Tenant-scoped audit log (same filters, pre-filtered to tenant) | `platform.audit.read` |

**Query parameters for `GET /admin/v1/audit-logs`:**

| Param | Type | Notes |
|---|---|---|
| `from` | ISO datetime | Required — no unbounded queries |
| `to` | ISO datetime | Required |
| `tenant_id` | UUID | Optional |
| `actor_type` | string | `tenant_user`, `platform_admin`, `system` |
| `actor_name` | string | Partial match |
| `action_category` | string | See Action Code Catalog categories |
| `action_code` | string | Exact match |
| `resource_type` | string | |
| `result` | string | `success` or `failed` |
| `ip_address` | string | Exact or prefix |
| `search` | string | Full-text across description, resource_name, actor_name |
| `page` | int | Default: 1 |
| `per_page` | int | Default: 25, max: 100 |
| `sort` | string | Default: `created_at` |
| `order` | string | `asc` or `desc`, default `desc` |

---

## Error Taxonomy

| HTTP | Code | Condition |
|---|---|---|
| 400 | `missing_date_range` | `from` or `to` not provided |
| 400 | `date_range_too_large` | Date range exceeds 90 days for a single query |
| 403 | `permission_denied` | Missing `platform.audit.read` |
| 422 | `export_too_large` | Export would exceed 100,000 rows |
| 404 | `export_job_not_found` | Async export job ID does not exist |
| 410 | `export_link_expired` | Async download link has expired |
