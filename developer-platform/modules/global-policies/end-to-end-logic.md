# Global Policies End-to-End Logic

## Publish Policy For Future Tenants

1. Operator opens Platform Management -> Global Policies.
2. Frontend loads policy catalog and current values.
3. Operator edits a policy draft.
4. Frontend calls `GET /admin/v1/global-policies/{id}/tenant-impact`.
5. Operator reviews impact.
6. Frontend calls `POST /admin/v1/global-policies/{id}/publish`.
7. Backend writes `system_settings` or the owning policy store and audits the change.

## Apply Policy To Existing Tenants

1. Operator selects an explicit propagation option.
2. Backend calculates affected tenants and blocked tenants.
3. Operator supplies audit reason.
4. Backend queues a background job for large tenant sets.
5. Job applies policy only to selected fields and records per-tenant results.

## APIs

| Method | Route | Purpose | Permission |
|---|---|---|---|
| GET | `/admin/v1/global-policies` | List policies | `platform.global_policies.read` |
| POST | `/admin/v1/global-policies` | Create policy | `platform.global_policies.manage` |
| PATCH | `/admin/v1/global-policies/{id}` | Update draft/current policy | `platform.global_policies.manage` |
| GET | `/admin/v1/global-policies/{id}/tenant-impact` | Preview impact | `platform.global_policies.read` |
| POST | `/admin/v1/global-policies/{id}/publish` | Publish policy | `platform.global_policies.publish` |

## Failure Handling

- Existing-tenant propagation must be idempotent.
- Partial propagation failures must be visible in the policy publish result and Platform Health summary in Phase 1; standalone Background Jobs visibility is Phase 2.
- Tenant-specific overrides are preserved unless explicitly selected.
