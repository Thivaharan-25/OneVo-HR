# Admin API Contracts

All endpoints are under the `/admin/v1/` prefix and require:

```
Authorization: Bearer <platform-admin-jwt>
```

Platform-admin JWTs are issued with issuer `onevo-platform-admin` and have a 30-minute TTL. Tenant-issued tokens are rejected by all endpoints in this namespace.

---

## Tenant Console

Manages tenant lifecycle: creation, status, subscription, module assignment, provisioning, and impersonation.

| Method | Path | Description |
|---|---|---|
| `GET` | `/admin/v1/tenants` | List all tenants |
| `POST` | `/admin/v1/tenants` | Create tenant (manual provisioning — step 1) |
| `GET` | `/admin/v1/tenants/{id}` | Get tenant detail |
| `PATCH` | `/admin/v1/tenants/{id}/status` | Suspend, unsuspend, or activate a tenant |
| `POST` | `/admin/v1/tenants/{id}/impersonate` | Issue an impersonation token (15 min TTL, `impersonation: true`) |
| `PATCH` | `/admin/v1/tenants/{id}/subscription` | Override subscription tier (exception tool) |
| `PUT` | `/admin/v1/tenants/{id}/modules` | Set active modules for tenant (provisioning step 3) |
| `PATCH` | `/admin/v1/tenants/{id}/provision/confirm` | Finalise provisioning draft → set status active |
| `POST` | `/admin/v1/tenants/{id}/invite-admin` | Create first super-admin and send invite email (provisioning step 5) |

---

## Feature Flag Manager

Controls global feature flag defaults and per-tenant overrides.

| Method | Path | Description |
|---|---|---|
| `GET` | `/admin/v1/feature-flags` | List all flags with their global defaults |
| `GET` | `/admin/v1/feature-flags/{flag}` | Get flag detail including per-tenant overrides |
| `PATCH` | `/admin/v1/feature-flags/{flag}` | Toggle global default for a flag |
| `PUT` | `/admin/v1/tenants/{id}/feature-flags` | Set all feature flag overrides for a tenant (replaces existing) |
| `PATCH` | `/admin/v1/tenants/{id}/feature-flags/{flag}` | Set a single feature flag override for a tenant |

---

## Agent Version Manager

Manages desktop agent versions, release channels, update rings, and force-update commands.

| Method | Path | Description |
|---|---|---|
| `GET` | `/admin/v1/agent-versions` | List version catalog |
| `POST` | `/admin/v1/agent-versions` | Publish a new agent version |
| `PATCH` | `/admin/v1/agent-versions/{id}/channel` | Change version channel (`stable` / `beta` / `recalled`) |
| `POST` | `/admin/v1/agent-versions/{id}/force-update` | Push `UPDATE_AGENT` command to all agents on this version in a ring |
| `GET` | `/admin/v1/agent-rings` | List rings and their tenant assignments |
| `PUT` | `/admin/v1/tenants/{id}/agent-ring` | Assign tenant to an update ring |

---

## Audit Console

Cross-tenant audit log access for platform administrators.

| Method | Path | Description |
|---|---|---|
| `GET` | `/admin/v1/audit-logs` | Query cross-tenant audit log (supports filtering by tenant, date, action type) |

---

## System Config

Manages global tenant setting defaults and per-tenant overrides.

| Method | Path | Description |
|---|---|---|
| `GET` | `/admin/v1/config/defaults` | Get global tenant setting defaults |
| `PATCH` | `/admin/v1/config/defaults` | Update global tenant setting defaults |
| `GET` | `/admin/v1/tenants/{id}/settings` | Get per-tenant settings |
| `PATCH` | `/admin/v1/tenants/{id}/settings` | Override per-tenant settings |

---

## Platform API Keys — Phase 2

> These endpoints are planned for Phase 2 and are not available in Phase 1.

Manages long-lived API keys for programmatic access to the Admin API (CI/CD, external tooling).

| Method | Path | Description |
|---|---|---|
| `GET` | `/admin/v1/api-keys` | List all active platform API keys |
| `POST` | `/admin/v1/api-keys` | Issue a new platform API key |
| `DELETE` | `/admin/v1/api-keys/{id}` | Revoke a platform API key |
