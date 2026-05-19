# Global Policies Userflow

## Actor

Platform policy manager.

## Journey

1. Operator opens Platform Management -> Global Policies.
2. Console loads current policy defaults.
3. Operator edits policy draft.
4. Operator previews tenant impact.
5. Operator publishes for future tenants or explicitly propagates to selected existing tenants.
6. Backend audits policy changes and background propagation results.

## APIs Used

- `GET /admin/v1/global-policies`
- `POST /admin/v1/global-policies`
- `PATCH /admin/v1/global-policies/{id}`
- `GET /admin/v1/global-policies/{id}/tenant-impact`
- `POST /admin/v1/global-policies/{id}/publish`

## Rules

Existing tenant overrides are not overwritten unless explicitly selected.
