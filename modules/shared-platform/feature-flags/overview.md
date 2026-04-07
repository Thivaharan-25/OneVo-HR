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

- [[shared-platform|Shared Platform Module]]
- [[tenant-management]]
- [[compliance-governance]]
- [[workflow-engine]]
- [[subscriptions-billing]]
- [[multi-tenancy]]
- [[authorization]]
- [[WEEK1-shared-platform]]
