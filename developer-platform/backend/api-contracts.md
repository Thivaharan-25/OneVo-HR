# Admin API Contracts

All endpoints are under the `/admin/v1/` prefix and require:

```http
Authorization: Bearer <platform-admin-jwt>
```

Platform-admin JWTs: issuer `onevo-platform-admin`, 30-minute TTL, signed with a separate key from tenant JWTs. Tenant-issued tokens are rejected at every endpoint in this namespace by the `PlatformAdmin` authorization policy.

Authorization is permission-based. Built-in platform roles are presets only â€” endpoints check explicit `dev_platform_permissions` codes, never role names.

**Convention:**
- `{id}` = UUID unless otherwise stated
- All timestamps in ISO 8601 UTC
- All write endpoints return 200 with updated resource or 201 with created resource
- All errors return `{ "error": "<code>", "message": "...", "details": [...] }`

---

## Authentication

| Method | Path | Description | Permission |
|---|---|---|---|
| `POST` | `/admin/v1/auth/google-callback` | Exchange Google id_token for platform-admin JWT | None |
| `POST` | `/admin/v1/auth/login` | Dev-only email/password login â€” returns 403 in non-Development environments | None |

---

## Dashboard

| Method | Path | Description | Permission |
|---|---|---|---|
| `GET` | `/admin/v1/dashboard/summary` | KPI totals: tenants, users, devices, sessions | `platform.dashboard.view` |
| `GET` | `/admin/v1/dashboard/platform-health` | Per-service health status and uptime | `platform.dashboard.view` |
| `GET` | `/admin/v1/dashboard/alerts` | Alert counts by severity and MTTR | `platform.dashboard.view` |
| `GET` | `/admin/v1/dashboard/recent-events` | Last N platform-significant audit events | `platform.dashboard.view` |
| `GET` | `/admin/v1/dashboard/user-activity-timeseries` | Active user counts over time (resolution adapts to `from`/`to` window) | `platform.dashboard.view` |
| `GET` | `/admin/v1/dashboard/tenant-distribution` | Tenant count broken down by plan tier | `platform.dashboard.view` |
| `GET` | `/admin/v1/dashboard/resource-utilization` | CPU, memory, storage percentage gauges | `platform.dashboard.view` |
| `GET` | `/admin/v1/dashboard/export` | Download dashboard summary as PDF or CSV | `platform.reports.read` |

**Common query params:** `from` (ISO datetime), `to` (ISO datetime), `limit` (integer, recent-events only)

---

## Platform Access

Developer Platform account management. These are not tenant users or tenant roles.

| Method | Path | Description | Permission |
|---|---|---|---|
| `GET` | `/admin/v1/platform-accounts` | List platform accounts | `platform.accounts.read` |
| `POST` | `/admin/v1/platform-accounts/invite` | Invite a new platform manager | `platform.accounts.manage` |
| `GET` | `/admin/v1/platform-accounts/{id}` | Platform account detail | `platform.accounts.read` |
| `PATCH` | `/admin/v1/platform-accounts/{id}` | Update name or role assignment | `platform.accounts.manage` |
| `POST` | `/admin/v1/platform-accounts/{id}/deactivate` | Disable login without deleting | `platform.accounts.manage` |
| `POST` | `/admin/v1/platform-accounts/{id}/reactivate` | Re-enable login | `platform.accounts.manage` |
| `POST` | `/admin/v1/platform-accounts/{id}/sessions/revoke` | Revoke all active sessions for this account | `platform.accounts.manage` |
| `GET` | `/admin/v1/platform-roles` | List platform roles (presets and custom) | `platform.accounts.read` |
| `POST` | `/admin/v1/platform-roles` | Create a custom platform role | `platform.accounts.manage` |
| `GET` | `/admin/v1/platform-roles/{id}` | Platform role detail with permissions | `platform.accounts.read` |
| `PATCH` | `/admin/v1/platform-roles/{id}` | Update role name/description | `platform.accounts.manage` |
| `PUT` | `/admin/v1/platform-roles/{id}/permissions` | Replace permission set for a platform role | `platform.accounts.manage` |
| `GET` | `/admin/v1/platform-permissions/catalog` | All available platform permission codes | `platform.accounts.read` |

---

## Tenant Console

Full tenant lifecycle: 4-step creation wizard, post-activation management, status changes, impersonation.

### Tenant CRUD and Wizard

| Method | Path | Description | Permission |
|---|---|---|---|
| `GET` | `/admin/v1/tenants` | List tenants with filters (status, plan, country, work_mode, search) | `platform.tenants.read` |
| `GET` | `/admin/v1/tenants/validate` | Validate domain/company name uniqueness before Step 1 submit | `platform.tenants.create` |
| `POST` | `/admin/v1/tenants` | Create provisioning draft â€” wizard Step 1 (Organization Info) | `platform.tenants.create` |
| `GET` | `/admin/v1/tenants/{id}` | Full tenant detail including provisioning_state | `platform.tenants.read` |
| `PATCH` | `/admin/v1/tenants/{id}` | Edit tenant profile (company name, phone, website) | `platform.tenants.manage` |
| `PATCH` | `/admin/v1/tenants/{id}/admin-account` | Save admin account â€” wizard Step 2 | `platform.tenants.manage` |
| `PATCH` | `/admin/v1/tenants/{id}/subscription` | Assign/override subscription and commercial terms â€” wizard Step 3 and post-activation override | `platform.subscriptions.manage` |
| `PATCH` | `/admin/v1/tenants/{id}/settings` | Save configuration and setup services â€” wizard Step 4 | `platform.tenants.manage` |
| `PATCH` | `/admin/v1/tenants/{id}/status` | Suspend, unsuspend, or cancel tenant | `platform.tenants.suspend` |
| `PATCH` | `/admin/v1/tenants/{id}/provision/confirm` | Activate provisioning tenant â€” runs activation guard | `platform.tenants.activate` |
| `GET` | `/admin/v1/tenants/{id}/provisioning-summary` | Activation checklist â€” blockers and warnings | `platform.tenants.read` |

### Tenant Actions

| Method | Path | Description | Permission |
|---|---|---|---|
| `POST` | `/admin/v1/tenants/{id}/impersonate` | Issue 15-minute non-renewable impersonation token | `platform.tenants.impersonate` |
| `POST` | `/admin/v1/tenants/{id}/invite-admin` | Send or resend tenant owner invite email | `platform.tenants.manage` |

### Tenant Detail Tabs

| Method | Path | Description | Permission |
|---|---|---|---|
| `GET` | `/admin/v1/tenants/{id}/subscription` | Current subscription detail, module entitlements, invoices | `platform.subscriptions.read` |
| `GET` | `/admin/v1/tenants/{id}/analytics` | Usage analytics (DAU, session duration, feature usage) | `platform.tenants.read` |
| `GET` | `/admin/v1/tenants/{id}/users` | Read-only tenant user list | `platform.tenants.read` |
| `GET` | `/admin/v1/tenants/{id}/device-health-summary` | Aggregate device health counts only; detailed device/version/ring list is Phase 2 | `platform.tenants.read` |
| `GET` | `/admin/v1/tenants/{id}/feature-flags` | Feature flag overrides for this tenant | `platform.feature_flags.read` |
| `GET` | `/admin/v1/tenants/{id}/integrations` | Integration connection status for this tenant | `platform.tenants.read` |
| `POST` | `/admin/v1/tenants/{id}/integrations/{key}/disconnect` | Disconnect a specific integration for this tenant | `platform.tenants.manage` |
| `GET` | `/admin/v1/tenants/{id}/audit` | Audit log filtered to this tenant | `platform.audit.read` |
| `GET` | `/admin/v1/tenants/{id}/settings` | Current tenant settings | `platform.tenants.read` |
| `GET` | `/admin/v1/tenants/{id}/user-activity-timeseries` | Per-tenant user activity chart data | `platform.tenants.read` |
| `GET` | `/admin/v1/tenants/{id}/department-activity` | Top departments by activity | `platform.tenants.read` |

### Tenant AI and Gateway Overrides

| Method | Path | Description | Permission |
|---|---|---|---|
| `GET` | `/admin/v1/tenants/{id}/ai-provider-override` | List AI config overrides for this tenant | `platform.system_config.read` |
| `PUT` | `/admin/v1/tenants/{id}/ai-provider-override/{purpose}` | Set per-tenant AI key for a specific purpose | `platform.system_config.manage` |
| `DELETE` | `/admin/v1/tenants/{id}/ai-provider-override/{purpose}` | Remove AI override â€” falls back to global | `platform.system_config.manage` |
| `POST` | `/admin/v1/tenants/{id}/ai-provider-override/{purpose}/test` | Test tenant's AI config | `platform.system_config.manage` |

### Tenant Settings Overrides

| Method | Path | Description | Permission |
|---|---|---|---|
| `GET` | `/admin/v1/tenants/{id}/settings-override` | List global setting overrides for this tenant | `platform.system_config.read` |
| `PATCH` | `/admin/v1/tenants/{id}/settings-override` | Set a tenant-specific global setting override | `platform.system_config.manage` |
| `DELETE` | `/admin/v1/tenants/{id}/settings-override/{key}` | Clear a setting override â€” falls back to global default | `platform.system_config.manage` |

---

## Subscription Manager

| Method | Path | Description | Permission |
|---|---|---|---|
| `GET` | `/admin/v1/subscription-plans` | List reusable plans with price brackets, module lists, and included feature keys | `platform.subscriptions.read` |
| `POST` | `/admin/v1/subscription-plans` | Create reusable plan from selected Phase 1 modules, included feature keys, and employee-count pricing tiers | `platform.subscriptions.manage` |
| `GET` | `/admin/v1/subscription-plans/{id}` | Plan detail with full price bracket and feature inclusion breakdown | `platform.subscriptions.read` |
| `PATCH` | `/admin/v1/subscription-plans/{id}` | Update plan metadata, modules, included features, or pricing | `platform.subscriptions.manage` |
| `POST` | `/admin/v1/subscription-plans/{id}/clone` | Clone plan with new name | `platform.subscriptions.manage` |
| `DELETE` | `/admin/v1/subscription-plans/{id}` | Deactivate plan â€” blocks new assignments, preserves existing | `platform.subscriptions.manage` |
| `GET` | `/admin/v1/payment-gateways` | List gateway configs â€” no secrets returned | `platform.payment_gateways.read` |
| `POST` | `/admin/v1/payment-gateways` | Create gateway config with encrypted secrets | `platform.payment_gateways.manage` |
| `GET` | `/admin/v1/payment-gateways/{id}` | Gateway detail â€” no secrets | `platform.payment_gateways.read` |
| `PATCH` | `/admin/v1/payment-gateways/{id}` | Update gateway metadata | `platform.payment_gateways.manage` |
| `PATCH` | `/admin/v1/payment-gateways/{id}/rotate-secrets` | Replace all encrypted credentials atomically | `platform.payment_gateways.manage` |
| `DELETE` | `/admin/v1/payment-gateways/{id}` | Deactivate gateway â€” blocked if active tenant assignments exist | `platform.payment_gateways.manage` |
| `POST` | `/admin/v1/system-config/payment-gateways/verify` | Verify gateway credentials against provider â€” does not save | `platform.system_config.manage` |
| `GET` | `/admin/v1/subscription-invoices` | List invoices with filters | `platform.subscriptions.read` |
| `GET` | `/admin/v1/subscription-invoices/{id}` | Invoice detail with line items | `platform.subscriptions.read` |
| `PATCH` | `/admin/v1/subscription-invoices/{id}/mark-paid` | Manually record payment with evidence reference | `platform.subscriptions.manage` |
| `PATCH` | `/admin/v1/subscription-invoices/{id}/void` | Void an open invoice | `platform.subscriptions.manage` |
| `GET` | `/admin/v1/subscription-invoices/{id}/pdf` | Download invoice PDF (PayHere: generated via QuestPDF; Paddle: redirect to paddle_invoice_url) | `platform.subscriptions.read` |
| `PATCH` | `/admin/v1/subscription-invoices/{id}/mark-uncollectible` | Write off invoice as uncollectible â€” requires reason | `platform.subscriptions.manage` |
| `GET` | `/admin/v1/subscription-plans/pricing-history` | All price bracket changes across all plans | `platform.subscriptions.read` |
| `GET` | `/admin/v1/billing-audit-logs` | List billing audit log entries with filters (tenant, action, date range) | `platform.subscriptions.read` |
| `GET` | `/admin/v1/billing-audit-logs/{tenantId}` | Full billing audit trail for a specific tenant | `platform.subscriptions.read` |
| `GET` | `/admin/v1/reports/billing/mrr` | MRR for a given month (`?year=&month=`) | `platform.reports.read` |
| `GET` | `/admin/v1/reports/billing/arr` | ARR at a given date (`?as_of=`) | `platform.reports.read` |
| `GET` | `/admin/v1/reports/billing/churn` | Churn rate for a period (`?from=&to=`) | `platform.reports.read` |
| `GET` | `/admin/v1/reports/billing/revenue-by-plan` | Revenue breakdown per plan for a period | `platform.reports.read` |
| `GET` | `/admin/v1/reports/billing/revenue-by-tenant` | Revenue breakdown per tenant for a period | `platform.reports.read` |
| `GET` | `/admin/v1/reports/billing/failed-payments` | Failed payment count and amount in period | `platform.reports.read` |
| `GET` | `/admin/v1/reports/billing/outstanding` | All open and overdue invoices with totals | `platform.reports.read` |

---

## Tenant Billing Portal (tenant-facing)

Tenant users access their own billing information. All routes require a valid tenant user JWT. Every route is automatically scoped to the authenticated user's tenant â€” no `tenantId` in path.

| Method | Path | Description | Permission |
|---|---|---|---|
| `GET` | `/api/v1/billing/invoices` | List invoices for this tenant (paginated, filterable by status/date) | `billing:read` |
| `GET` | `/api/v1/billing/invoices/{id}` | Invoice detail with line items | `billing:read` |
| `GET` | `/api/v1/billing/invoices/{id}/pdf` | Download invoice PDF â€” PayHere: QuestPDF stream; Paddle: redirect to Paddle-hosted URL | `billing:read` |
| `GET` | `/api/v1/billing/subscription` | Current subscription plan, allowed plans before confirmation, status, billing dates, next renewal amount | `billing:read` |
| `POST` | `/api/v1/billing/subscription/confirm` | Tenant owner selects allowed plan, chooses billing cycle, confirms total employee count, and triggers first invoice/payment flow | `billing:manage` |
| `POST` | `/api/v1/billing/subscription/cancel` | Request subscription cancellation â€” takes effect at end of current billing period | `billing:manage` |
| `POST` | `/api/v1/billing/modules/{moduleId}/add` | Add a module pack (validates payment method on file; charges proration) | `billing:manage` |

**Cancel subscription rules:**
- Sets `tenant_subscriptions.cancellation_requested_at = now()` and `cancel_at_period_end = true`
- For Paddle tenants: calls Paddle API to cancel at period end
- Tenant retains full access until `billing_period_end`
- Creates audit log entry: `subscription.cancel_requested`, actor, reason (optional free-text)
- Platform admin is notified via Info alert: `billing.cancellation_requested`

**Add module pack rules:**
- Validates the module is not already entitled
- Validates a payment method is on file for the configured gateway
- Charges prorated amount for remainder of current billing period
- For Paddle tenants: creates a one-time Paddle transaction for proration, then updates subscription items
- For PayHere tenants: generates proration invoice and initiates PayHere charge
- Updates `tenant_module_entitlements` through module interfaces on payment confirmation

---

## Module Catalog Manager

| Method | Path | Description | Permission |
|---|---|---|---|
| `GET` | `/admin/v1/modules/catalog` | List all product modules | `platform.module_catalog.read` |
| `POST` | `/admin/v1/modules/catalog` | Create a new product module | `platform.module_catalog.manage` |
| `GET` | `/admin/v1/modules/catalog/{moduleKey}` | Module detail â€” pricing, permissions, linked integrations | `platform.module_catalog.read` |
| `PATCH` | `/admin/v1/modules/catalog/{moduleKey}` | Update module metadata and limits | `platform.module_catalog.manage` |
| `GET` | `/admin/v1/modules/catalog/{moduleKey}/permissions` | Permission codes owned by this module | `platform.module_catalog.read` |
| `PUT` | `/admin/v1/modules/catalog/{moduleKey}/permissions` | Replace module permission ownership | `platform.module_catalog.manage` |
| `GET` | `/admin/v1/modules/catalog/{moduleKey}/features` | Commercial feature list for this module | `platform.module_catalog.read` |
| `PUT` | `/admin/v1/modules/catalog/{moduleKey}/features` | Replace commercial feature list for this module | `platform.module_catalog.manage` |
| `GET` | `/admin/v1/modules/catalog/{moduleKey}/pricing` | Pricing brackets and price history | `platform.module_catalog.read` |
| `PATCH` | `/admin/v1/modules/catalog/{moduleKey}/pricing` | Update pricing â€” creates price history entry | `platform.module_catalog.manage` |
| `GET` | `/admin/v1/modules/catalog/{moduleKey}/tenant-impact` | Tenants and plans affected by a pending change | `platform.module_catalog.read` |
| `GET` | `/admin/v1/modules/catalog/{moduleKey}/integrations` | Integrations linked to this module | `platform.module_catalog.read` |
| `POST` | `/admin/v1/modules/catalog/{moduleKey}/integrations` | Link an integration to this module | `platform.module_catalog.manage` |
| `DELETE` | `/admin/v1/modules/catalog/{moduleKey}/integrations/{integrationKey}` | Unlink integration from module | `platform.module_catalog.manage` |

---

## Integration Catalog

| Method | Path | Description | Permission |
|---|---|---|---|
| `GET` | `/admin/v1/integrations/catalog` | List all integration entries | `platform.module_catalog.read` |
| `POST` | `/admin/v1/integrations/catalog` | Create a new integration entry | `platform.module_catalog.manage` |
| `GET` | `/admin/v1/integrations/catalog/{integrationKey}` | Integration entry detail | `platform.module_catalog.read` |
| `PATCH` | `/admin/v1/integrations/catalog/{integrationKey}` | Edit integration entry | `platform.module_catalog.manage` |
| `GET` | `/admin/v1/integrations/catalog/{integrationKey}/tenant-connections` | Tenants with this integration connected | `platform.module_catalog.read` |

---

## Feature Flag Manager

| Method | Path | Description | Permission |
|---|---|---|---|
| `GET` | `/admin/v1/feature-flags` | List all flags with global defaults and override counts | `platform.feature_flags.read` |
| `POST` | `/admin/v1/feature-flags` | Create a new feature flag | `platform.feature_flags.manage` |
| `GET` | `/admin/v1/feature-flags/{flagKey}` | Flag detail with per-tenant override list | `platform.feature_flags.read` |
| `PATCH` | `/admin/v1/feature-flags/{flagKey}` | Update flag default value, rollout %, or description | `platform.feature_flags.manage` |
| `DELETE` | `/admin/v1/feature-flags/{flagKey}` | Deactivate flag | `platform.feature_flags.manage` |
| `GET` | `/admin/v1/feature-flags/tenant-overrides` | All overrides across all flags and all tenants | `platform.feature_flags.read` |
| `GET` | `/admin/v1/tenants/{id}/feature-flags` | Effective flag values for a specific tenant | `platform.feature_flags.read` |
| `PUT` | `/admin/v1/tenants/{id}/feature-flags` | Replace all tenant overrides with an `overrides` value map | `platform.feature_flags.manage` |
| `PATCH` | `/admin/v1/tenants/{id}/feature-flags/{flagKey}` | Set per-tenant override with `value` after module entitlement and commercial feature inclusion validation | `platform.feature_flags.manage` |
| `DELETE` | `/admin/v1/tenants/{id}/feature-flags/{flagKey}` | Remove per-tenant override | `platform.feature_flags.manage` |
| `GET` | `/admin/v1/tenants/{id}/modules/runtime-status` | All module runtime enable/disable statuses for a tenant | `platform.feature_flags.read` |
| `PATCH` | `/admin/v1/tenants/{id}/modules/{moduleKey}/runtime-status` | Toggle module runtime status â€” does not change billing | `platform.feature_flags.manage` |

Tenant-facing product flags must provide both `module_key` and `feature_key`, with `feature_key` owned by the selected module in `module_features`. Only platform operational flags may omit both fields.

---

## Role Template Manager

| Method | Path | Description | Permission |
|---|---|---|---|
| `GET` | `/admin/v1/role-templates` | List all global templates (system and custom) | `platform.role_templates.read` |
| `POST` | `/admin/v1/role-templates` | Create a new global role template | `platform.role_templates.manage` |
| `GET` | `/admin/v1/role-templates/{id}` | Template detail with full permission list | `platform.role_templates.read` |
| `PATCH` | `/admin/v1/role-templates/{id}` | Update template â€” increments version | `platform.role_templates.manage` |
| `POST` | `/admin/v1/role-templates/{id}/clone` | Clone system or custom template into new editable template | `platform.role_templates.manage` |
| `DELETE` | `/admin/v1/role-templates/{id}` | Deactivate template | `platform.role_templates.manage` |
| `GET` | `/admin/v1/tenants/{id}/permissions/catalog` | Module-filtered permission catalog for a specific tenant | `platform.tenants.read` |
| `GET` | `/admin/v1/tenants/{id}/roles` | Materialized tenant roles | `platform.tenants.read` |
| `POST` | `/admin/v1/tenants/{id}/roles` | Create a tenant-specific role (not saved as global template) | `platform.tenants.manage` |
| `PUT` | `/admin/v1/tenants/{id}/roles/{roleId}/permissions` | Replace tenant role permission set | `platform.tenants.manage` |
| `DELETE` | `/admin/v1/tenants/{id}/roles/{roleId}` | Delete tenant role | `platform.tenants.manage` |
| `POST` | `/admin/v1/tenants/{id}/role-templates/{templateId}/apply` | Apply template to tenant â€” with idempotency handling | `platform.tenants.manage` |
| `GET` | `/admin/v1/tenants/{id}/role-template-applications` | History of template applications for this tenant | `platform.tenants.read` |

---

## System Config

| Method | Path | Description | Permission |
|---|---|---|---|
| `GET` | `/admin/v1/system-config/global-defaults` | List all global platform settings with current values | `platform.system_config.read` |
| `PATCH` | `/admin/v1/system-config/global-defaults` | Update one or more global defaults with reason | `platform.system_config.manage` |

### AI Provider Configuration

| Method | Path | Description | Permission |
|---|---|---|---|
| `GET` | `/admin/v1/system-config/ai-providers` | List AI configs â€” no keys returned | `platform.system_config.read` |
| `POST` | `/admin/v1/system-config/ai-providers/fetch-models` | Temporarily use entered key to fetch available models from provider â€” does not save | `platform.system_config.manage` |
| `POST` | `/admin/v1/system-config/ai-providers` | Create AI provider config for a purpose | `platform.system_config.manage` |
| `PUT` | `/admin/v1/system-config/ai-providers/{configId}` | Update AI config â€” key replaced atomically | `platform.system_config.manage` |
| `DELETE` | `/admin/v1/system-config/ai-providers/{configId}` | Deactivate AI config | `platform.system_config.manage` |
| `POST` | `/admin/v1/system-config/ai-providers/{configId}/test` | Test connection using stored key and base URL | `platform.system_config.manage` |

### Platform OAuth Apps

| Method | Path | Description | Permission |
|---|---|---|---|
| `GET` | `/admin/v1/system-config/oauth-apps` | List OAuth app registrations â€” secrets never returned | `platform.system_config.read` |
| `PUT` | `/admin/v1/system-config/oauth-apps/{provider}` | Set OAuth app credentials for a provider | `platform.system_config.manage` |
| `POST` | `/admin/v1/system-config/oauth-apps/{provider}/test` | Validate stored OAuth app with provider | `platform.system_config.manage` |

### Platform Service Keys

| Method | Path | Description | Permission |
|---|---|---|---|
| `GET` | `/admin/v1/system-config/service-keys` | List platform service keys â€” secrets never returned | `platform.system_config.read` |
| `PUT` | `/admin/v1/system-config/service-keys/{serviceKey}` | Set/rotate a platform service key | `platform.system_config.manage` |
| `POST` | `/admin/v1/system-config/service-keys/{serviceKey}/test` | Test service key connection | `platform.system_config.manage` |

---

## Agent Version Manager

> Phase 2 only. These endpoints must be absent from Phase 1 deployments.

| Method | Path | Description | Permission |
|---|---|---|---|
| `GET` | `/admin/v1/agent-versions` | List version catalog with channel and OS info | `platform.agent_versions.read` |
| `POST` | `/admin/v1/agent-versions` | Publish a new agent version | `platform.agent_versions.manage` |
| `PATCH` | `/admin/v1/agent-versions/{id}/channel` | Change version channel: stable / beta / recalled | `platform.agent_versions.manage` |
| `POST` | `/admin/v1/agent-versions/{id}/force-update` | Push force-update command to all devices on this version in a ring | `platform.agent_versions.force_update` |
| `GET` | `/admin/v1/agent-rings` | List deployment rings and current tenant assignments | `platform.agent_versions.read` |
| `PUT` | `/admin/v1/tenants/{id}/agent-ring` | Assign tenant to a deployment ring | `platform.agent_versions.manage` |

---

## Security Center

| Method | Path | Description | Permission |
|---|---|---|---|
| `GET` | `/admin/v1/security/overview` | Security KPI summary â€” alert counts, active sessions, events | `platform.security.read` |
| `GET` | `/admin/v1/security/alerts` | Alert list with filters (severity, status, tenant, alert_code) | `platform.security.read` |
| `GET` | `/admin/v1/security/alerts/{id}` | Alert detail with related audit events | `platform.security.read` |
| `POST` | `/admin/v1/security/alerts/{id}/acknowledge` | Mark alert as acknowledged | `platform.security.manage` |
| `POST` | `/admin/v1/security/alerts/{id}/resolve` | Resolve alert with resolution type and note (Critical requires 20+ char note) | `platform.security.manage` |
| `GET` | `/admin/v1/security/sessions` | Platform admin session list | `platform.security.read` |
| `POST` | `/admin/v1/security/sessions/{sessionId}/revoke` | Revoke a platform admin session | `platform.security.manage` |
| `POST` | `/admin/v1/platform-accounts/{id}/sessions/revoke-all` | Revoke all active sessions for a platform account | `platform.accounts.manage` |
| `GET` | `/admin/v1/security/suspicious-activity` | Below-threshold security events from audit log | `platform.security.read` |

---

## Audit Console

| Method | Path | Description | Permission |
|---|---|---|---|
| `GET` | `/admin/v1/audit-logs` | Query cross-tenant audit log with full filter support | `platform.audit.read` |
| `GET` | `/admin/v1/audit-logs/{id}` | Single audit entry with full previous_state and new_state | `platform.audit.read` |
| `POST` | `/admin/v1/audit-logs/export` | Export filtered log as CSV or JSON â€” async for >10k rows | `platform.audit.export` |
| `GET` | `/admin/v1/audit-logs/export/{jobId}` | Async export job status and download link | `platform.audit.export` |
| `GET` | `/admin/v1/tenants/{id}/audit` | Audit log pre-filtered to a specific tenant | `platform.audit.read` |

**Audit log query params:** `from` (required), `to` (required), `tenant_id`, `actor_type`, `actor_name`, `action_category`, `action_code`, `resource_type`, `result`, `ip_address`, `search`, `page`, `per_page` (max 100), `sort`, `order`

---

## Global Policies

| Method | Path | Description | Permission |
|---|---|---|---|
| `GET` | `/admin/v1/global-policies` | List platform policy defaults | `platform.policies.read` |
| `POST` | `/admin/v1/global-policies` | Create a new platform policy | `platform.policies.manage` |
| `PATCH` | `/admin/v1/global-policies/{id}` | Update policy draft value | `platform.policies.manage` |
| `GET` | `/admin/v1/global-policies/{id}/tenant-impact` | Preview how many tenants would be affected | `platform.policies.read` |
| `POST` | `/admin/v1/global-policies/{id}/publish` | Publish policy â€” propagates to affected tenants | `platform.policies.manage` |

---

## System Operations

Phase 1 exposes Platform Health and Services Monitor only. Device Management, Infrastructure Operations, Background Jobs, and Agent Version Manager endpoints are Phase 2.

| Method | Path | Description | Permission |
|---|---|---|---|
| `GET` | `/admin/v1/operations/platform-health` | Overall platform health + per-service status | `platform.health.read` |
| `GET` | `/admin/v1/operations/platform-health/dependencies` | External dependency health | `platform.health.read` |
| `GET` | `/admin/v1/operations/services` | List all monitored services | `platform.health.read` |
| `GET` | `/admin/v1/operations/services/{serviceKey}` | Service detail â€” metrics, uptime, error rate | `platform.health.read` |
| `POST` | `/admin/v1/operations/services/{serviceKey}/actions/{action}` | Execute an approved safe service action | `platform.health.manage` |

---

## Security & Compliance â€” Extended

| Method | Path | Description | Permission |
|---|---|---|---|
| `GET` | `/admin/v1/compliance/overview` | Compliance status summary | `platform.compliance.read` |
| `GET` | `/admin/v1/compliance/exports` | List compliance export requests and status | `platform.compliance.read` |
| `POST` | `/admin/v1/compliance/exports` | Request a compliance data export | `platform.compliance.manage` |
| `GET` | `/admin/v1/legal-holds` | List active and released legal holds | `platform.compliance.read` |
| `POST` | `/admin/v1/legal-holds` | Create a legal hold on a tenant's data | `platform.compliance.manage` |
| `PATCH` | `/admin/v1/legal-holds/{id}` | Update or release a legal hold | `platform.compliance.manage` |
| `GET` | `/admin/v1/retention-policies` | List data retention policies | `platform.compliance.read` |
| `POST` | `/admin/v1/retention-policies` | Create a retention policy | `platform.compliance.manage` |
| `PATCH` | `/admin/v1/retention-policies/{id}` | Update retention policy | `platform.compliance.manage` |
| `GET` | `/admin/v1/retention-policies/{id}/impact` | Preview which data would be affected | `platform.compliance.read` |

---

## Analytics & Reports

| Method | Path | Description | Permission |
|---|---|---|---|
| `GET` | `/admin/v1/analytics/platform` | Platform-wide operational analytics | `platform.reports.read` |
| `GET` | `/admin/v1/analytics/tenants` | Tenant lifecycle and churn analytics | `platform.reports.read` |
| `GET` | `/admin/v1/analytics/subscriptions` | Commercial and billing analytics | `platform.reports.read` |
| `GET` | `/admin/v1/analytics/modules` | Module adoption and usage analytics | `platform.reports.read` |
| `GET` | `/admin/v1/reports` | Report catalog | `platform.reports.read` |
| `POST` | `/admin/v1/reports/export` | Start a report export | `platform.reports.read` |
| `GET` | `/admin/v1/reports/exports/{id}` | Export status and download link | `platform.reports.read` |

---

## App Catalog Manager

| Method | Path | Description | Permission |
|---|---|---|---|
| `GET` | `/admin/v1/app-catalog` | List global app catalog entries | `platform.app_catalog.read` |
| `POST` | `/admin/v1/app-catalog` | Create a catalog entry | `platform.app_catalog.manage` |
| `PATCH` | `/admin/v1/app-catalog/{id}` | Update metadata or toggle `is_public` | `platform.app_catalog.manage` |
| `GET` | `/admin/v1/app-catalog/uncatalogued` | Uncatalogued app candidates from observed apps | `platform.app_catalog.read` |
| `POST` | `/admin/v1/app-catalog/bulk-approve` | Bulk approve candidates into global catalog | `platform.app_catalog.manage` |

---

## Reference Data

| Method | Path | Description | Permission |
|---|---|---|---|
| `GET` | `/admin/v1/reference/countries/{countryCode}/defaults` | Default timezone, currency, and timezone choices for a country â€” used in Step 1 wizard | None (admin-namespace public) |
| `GET` | `/admin/v1/setup-services` | Global setup service catalog (free and paid) | `platform.tenants.read` |
| `POST` | `/admin/v1/setup-services` | Create a setup service definition | `platform.tenants.manage` |
| `PUT` | `/admin/v1/tenants/{id}/setup-services` | Select and track setup services for a tenant | `platform.tenants.manage` |

---

## Configuration Template Manager

Full CRUD for the global reusable configuration template library. Role templates are managed separately under the Role Template Manager section.

| Method | Path | Description | Permission |
|---|---|---|---|
| `GET` | `/admin/v1/configuration-templates` | List all global configuration templates; filter by `?type=` (position_template, leave_policy, configuration, onboarding, app_allowlist, monitoring_policy, data_import_mapping) and `?active_only=true` | `platform.config_templates.read` |
| `GET` | `/admin/v1/configuration-templates/{id}` | Full template detail including payload JSON and version history | `platform.config_templates.read` |
| `POST` | `/admin/v1/configuration-templates` | Create a new configuration template â€” body: `{ template_key, template_type, name, description, module_keys_json, industry_profile_tag, payload_json, is_system }` | `platform.config_templates.manage` |
| `PATCH` | `/admin/v1/configuration-templates/{id}` | Update template name, description, or payload â€” increments `version`; system templates are read-only (clone instead) | `platform.config_templates.manage` |
| `DELETE` | `/admin/v1/configuration-templates/{id}` | Deactivate template (`is_active = false`) â€” blocked if active tenant positions or assignment rows still reference the template | `platform.config_templates.manage` |
| `POST` | `/admin/v1/configuration-templates/{id}/clone` | Clone a system or custom template into a new editable template | `platform.config_templates.manage` |
| `POST` | `/admin/v1/tenants/{id}/configuration-templates/{templateId}/apply` | Apply template to tenant â€” body: `{ force_update: bool }`. Checks module entitlement, runs type-specific apply handler, writes audit row. Returns `{ application_id, applied_version, warnings[] }` | `platform.config_templates.manage` |
| `GET` | `/admin/v1/tenants/{id}/configuration-template-applications` | History of all template applications for this tenant, ordered by `applied_at desc` | `platform.tenants.read` |

**Query parameters for `GET /admin/v1/configuration-templates`:**

| Param | Type | Description |
|---|---|---|
| `type` | string | Filter by `template_type` enum value |
| `active_only` | bool | Default `true` â€” omit inactive templates |
| `industry_tag` | string | Filter monitoring_policy templates by `industry_profile_tag` |

**Apply response warnings** (non-blocking â€” apply succeeds but caller should surface these):

| Warning | Condition |
|---|---|
| `"Role template '{key}' excluded {count} permissions because the tenant is not entitled to module '{module_key}'."` | Linked position role template contains permissions from modules the tenant has not bought |

**Onboarding template assignment fields:**

| Field | Type | Required | Notes |
|---|---|---|---|
| `assignment_scope` | string | Yes | `tenant`, `department`, or `position` |
| `department_names` | string[] | Required if `assignment_scope = department` | Department assignment targets |
| `position_keys` | string[] | Required if `assignment_scope = position` | Position assignment targets |

Validation error: `assignment_scope_targets_required` when department or position scope is selected without targets.

---

## File Uploads

| Method | Path | Description | Permission |
|---|---|---|---|
| `POST` | `/admin/v1/uploads/integration-logo` | Upload integration catalog logo â€” returns `logo_url` | `platform.module_catalog.manage` |
| `POST` | `/admin/v1/uploads/gateway-logo` | Upload payment gateway logo â€” returns `logo_url` | `platform.payment_gateways.manage` |
| `POST` | `/admin/v1/uploads/oauth-app-logo` | Upload OAuth app provider logo â€” returns `logo_url` | `platform.system_config.manage` |
| `POST` | `/admin/v1/uploads/ai-provider-logo` | Upload AI provider logo â€” returns `logo_url` | `platform.system_config.manage` |

All upload endpoints accept `multipart/form-data` with a single `file` field. Accepted types: PNG, SVG, JPEG. Max 500KB. Response: `{ "logo_url": "https://storage.onevo.io/..." }`.

---

## Webhook Endpoints (inbound â€” not admin-authenticated)

| Method | Path | Description |
|---|---|---|
| `POST` | `/webhooks/paddle` | Inbound Paddle webhook â€” signature verified via `Paddle-Signature` header (HMAC-SHA256) |
| `POST` | `/webhooks/payhere/notify` | Inbound PayHere webhook â€” signature verified via MD5 hash |

Both endpoints return `200` immediately on signature validation and process asynchronously via `webhook_event_queue`.

---

## Platform API Keys â€” Phase 2

> Not available in Phase 1.

| Method | Path | Description | Permission |
|---|---|---|---|
| `GET` | `/admin/v1/api-keys` | List platform API keys | `platform.api_keys.read` |
| `POST` | `/admin/v1/api-keys` | Issue a new platform API key | `platform.api_keys.manage` |
| `DELETE` | `/admin/v1/api-keys/{id}` | Revoke a platform API key | `platform.api_keys.manage` |



