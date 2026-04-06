# Module: Shared Platform

**Namespace:** `ONEVO.Modules.SharedPlatform`
**Pillar:** Shared Foundation
**Owner:** Dev 4 (Week 1 + Week 4)
**Tables:** 21

---

## Purpose

Cross-cutting platform services: SSO provider management, subscription/billing (Stripe), feature flags, and the generic workflow/approval engine used by leave, overtime, expense, document approvals, etc.

---

## Dependencies

| Direction | Module | Interface | Purpose |
|:----------|:-------|:----------|:--------|
| **Depends on** | [[infrastructure]] | `ITenantContext` | Multi-tenancy |
| **Consumed by** | [[leave]], [[core-hr]], [[expense]] | Workflow engine | Approval routing |
| **Consumed by** | All modules | Feature flags | Feature toggle checks |

---

## Key Sub-Systems

### 1. SSO Providers

| Table | Purpose |
|:------|:--------|
| `sso_providers` | SSO configuration (Google, Microsoft, SAML) |

**Encrypted fields:** `client_id_encrypted`, `client_secret_encrypted` via `IEncryptionService`.

### 2. Subscriptions & Billing (Stripe)

| Table | Purpose |
|:------|:--------|
| `subscription_plans` | Plan definitions (NOT tenant-scoped — global) |
| `plan_features` | Features per plan |
| `tenant_subscriptions` | Active subscription per tenant |
| `subscription_invoices` | Invoice records |
| `payment_methods` | Stored payment methods |

### 3. Feature Flags

| Table | Purpose |
|:------|:--------|
| `feature_flags` | Feature definitions |
| `tenant_feature_flags` | Per-tenant flag overrides |

### 4. Workflow Engine (Generic)

The workflow engine is **resource-type agnostic** — it works via `resource_type` + `resource_id` polymorphic references. Same engine handles leave, overtime, document, expense approvals.

| Table | Purpose |
|:------|:--------|
| `workflow_definitions` | Workflow templates (e.g., "Leave Approval", "Expense Approval") |
| `workflow_steps` | Steps in a workflow definition |
| `workflow_instances` | Active workflow instance for a specific resource |
| `workflow_step_instances` | Current step state for an instance |
| `approval_actions` | Approval/rejection records |

**How it works:**
1. Module creates a workflow instance: `resource_type = "LeaveRequest"`, `resource_id = {leaveRequestId}`
2. Engine resolves approvers based on step definition (reporting manager, department head, etc.)
3. Approver takes action → engine advances to next step or completes
4. Module receives `WorkflowCompleted` event with outcome

### 5. Additional Platform Tables

| Table | Purpose |
|:------|:--------|
| `system_settings` | Global system configuration |
| `api_keys` | Tenant API keys for integrations |
| `webhook_endpoints` | Registered webhook URLs |
| `webhook_deliveries` | Delivery log |
| `rate_limit_rules` | Per-endpoint rate limit config |
| `scheduled_tasks` | Hangfire job metadata |

---

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/sso/providers` | `settings:admin` | List SSO providers |
| POST | `/api/v1/sso/providers` | `settings:admin` | Configure SSO |
| GET | `/api/v1/subscriptions/current` | `billing:read` | Current subscription |
| POST | `/api/v1/subscriptions/upgrade` | `billing:manage` | Upgrade plan |
| GET | `/api/v1/feature-flags` | Authenticated | Active feature flags |
| GET | `/api/v1/workflows/{resourceType}/{resourceId}` | Authenticated | Workflow status |
| POST | `/api/v1/workflows/{instanceId}/approve` | Authenticated | Approve step |
| POST | `/api/v1/workflows/{instanceId}/reject` | Authenticated | Reject step |

See also: [[module-catalog]], [[infrastructure]], [[auth]], [[external-integrations]]
