# SSO Authentication

**Module:** Shared Platform  
**Feature:** SSO Authentication

---

## Purpose

SSO provider management (Google, Microsoft, SAML, OIDC) and refresh token tracking with rotation.

## Database Tables

### `sso_providers`
Key columns: `provider_type` (`google`, `microsoft`, `saml`, `oidc`), `client_id_encrypted`, `client_secret_encrypted`, `metadata_url`, `domain_hint`, `auto_provision_users`.

### `refresh_tokens`
JWT refresh token rotation: `token_hash`, `device_fingerprint`, `expires_at`, `is_revoked`, `replaced_by_id`.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/sso/providers` | `settings:admin` | List SSO providers |
| POST | `/api/v1/sso/providers` | `settings:admin` | Configure SSO |

## Related

- [[modules/shared-platform/overview|Shared Platform Module]]
- [[frontend/cross-cutting/authentication|Authentication]]
- [[frontend/cross-cutting/authorization|Authorization]]
- [[modules/infrastructure/user-management/overview|User Management]]
- [[modules/infrastructure/tenant-management/overview|Tenant Management]]
- [[security/auth-architecture|Auth Architecture]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[backend/messaging/error-handling|Error Handling]]
- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4: Shared Platform Agent Gateway]]
