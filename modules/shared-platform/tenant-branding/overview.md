# Tenant Branding

**Module:** Shared Platform  
**Feature:** Tenant Branding

---

## Purpose

Custom branding per tenant and per-user UI preferences. Every tenant gets a default ONEVO-owned URL in the form `https://{tenantSlug}.onevo.com`. Cloudflare DNS manages `onevo.com` and wildcard `*.onevo.com`, while Azure hosts the ONEVO application.

## Database Tables

### `tenant_branding`
Fields: `logo_file_id`, `primary_color`, `accent_color`, `metadata`.

The default `{tenantSlug}.onevo.com` URL comes from `tenants.slug` plus the ONEVO parent domain and does not require a separate branding field.

### `user_preferences`
Per-user: `preference_key` (`theme`, `locale`, `timezone`), `preference_value` (jsonb).

## Related

- [[modules/shared-platform/overview|Shared Platform Module]]
- [[modules/infrastructure/tenant-management/overview|Tenant Management]]
- [[modules/infrastructure/file-management/overview|File Management]]
- [[modules/infrastructure/user-management/overview|User Management]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[frontend/cross-cutting/authorization|Authorization]]
- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4: Shared Platform Agent Gateway]]
