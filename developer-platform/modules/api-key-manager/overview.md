# Platform API Key Manager

> **Phase 2 — Not available in Phase 1**
>
> This module is planned for Phase 2 of the Developer Platform. It is not built or accessible in the initial Phase 1 release. Do not reference this module in Phase 1 documentation, runbooks, or support guides.

## Purpose

The Platform API Key Manager issues and manages platform-level API keys for external systems and integrations that need to interact with OneVo at the platform level — not scoped to any specific tenant.

## Database Tables / Systems Controlled

| Table / System | Role |
|---|---|
| `platform_api_keys` | Read + write — new table introduced in Phase 2 |

## Capabilities

### Key Issuance
- Create a new platform API key with:
  - A human-readable label (identifies the consuming system)
  - Scope selection (which API resources the key can access)
  - Expiry date (or no-expiry for permanent keys)
  - Rate limit configuration

### Key Revocation
- Revoke any active key immediately
- Revoked keys are rejected at the API gateway with no grace period

### Key Usage Logs
- View per-key usage history: request count, last used timestamp, endpoint breakdown
- Useful for auditing external integrations and detecting anomalous access patterns

## Notes

- Platform API keys are **not tenant-specific**. They are for operator-level integrations (e.g., internal tooling, external partners, data pipelines that span tenants).
- For tenant-scoped API access, use the tenant's own API credentials managed within the OneVo app — this module does not replace that.
- All key creation and revocation events will be audit-logged when this module is live.
