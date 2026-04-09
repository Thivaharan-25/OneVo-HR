# Tenant Branding

**Module:** Shared Platform  
**Feature:** Tenant Branding

---

## Purpose

Custom branding per tenant and per-user UI preferences.

## Database Tables

### `tenant_branding`
Fields: `custom_domain`, `logo_file_id`, `primary_color`, `accent_color`, `metadata`.

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
