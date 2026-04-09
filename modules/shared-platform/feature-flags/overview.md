# Feature Flags

**Module:** Shared Platform  
**Feature:** Feature Flags

---

## Purpose

Feature flag definitions with targeting rules and per-tenant overrides.

## Database Tables

### `feature_flags`
Fields: `flag_key`, `is_enabled`, `conditions` (targeting rules), `toggled_by_id`.

### `tenant_feature_flags`
Per-tenant overrides: `flag_key`, `is_enabled` (override value), `overridden_by_id`.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/feature-flags` | Authenticated | Active flags |

## Related

- [[modules/shared-platform/overview|Shared Platform Module]]
- [[modules/infrastructure/tenant-management/overview|Tenant Management]]
- [[modules/shared-platform/compliance-governance/overview|Compliance Governance]]
- [[modules/shared-platform/workflow-engine/overview|Workflow Engine]]
- [[modules/shared-platform/subscriptions-billing/overview|Subscriptions Billing]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[frontend/cross-cutting/authorization|Authorization]]
- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4: Shared Platform Agent Gateway]]
