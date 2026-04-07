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

- [[shared-platform|Shared Platform Module]]
- [[authentication]]
- [[authorization]]
- [[user-management]]
- [[tenant-management]]
- [[auth-architecture]]
- [[multi-tenancy]]
- [[error-handling]]
- [[WEEK1-shared-platform]]
